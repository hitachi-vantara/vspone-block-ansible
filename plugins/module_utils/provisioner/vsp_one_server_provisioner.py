from ..common.ansible_common import log_entry_exit
from ..common.hv_log import (
    Log,
)
from ..common.vsp_errors import VspFeatureNotSupportedError
from ..gateway.vsp_one_server_gateway import VspServerSimpleApiGateway
from ..message.vsp_lun_msgs import VSPVolumeMSG
from ..message.vsp_one_server_msgs import VSPOneServerMSG
import re
from ..model.vsp_one_server_models import (
    CreateServerSpec,
    ServerFactsSpec,
    VspOneServerResponse,
)

logger = Log()


FC = "FC"
ISCSI = "ISCSI"


def check_server_exists(func):
    """
    Decorator to check if server exists before executing the method
    """

    def wrapper(self, *args, **kwargs):
        # Extract server_id from arguments
        server_id = None
        if len(args) == 1:
            # Check if first argument is server_id (int)
            if args and isinstance(args[0], int):
                server_id = args[0]
            # Check if spec object has server_id attribute
            elif (
                args and hasattr(args[0], "server_id") and args[0].server_id is not None
            ):
                server_id = args[0].server_id
            # Check in kwargs
            elif "server_id" in kwargs and kwargs["server_id"] is not None:
                server_id = kwargs["server_id"]
            # Check if spec object has nick_name and get server_id by nick_name
            elif args and hasattr(args[0], "nick_name") and args[0].nick_name:

                existing_server = self.get_server_by_nick_name(args[0].nick_name)
                if existing_server:
                    server_id = existing_server.id

            # Validate that either server_id or nick_name was provided and resolved
            if server_id is None:
                # Check if nick_name was provided but server not found
                if args and hasattr(args[0], "nick_name") and args[0].nick_name:
                    raise ValueError(
                        VSPOneServerMSG.SERVER_WITH_NICKNAME_NOT_FOUND.value.format(
                            nickname=args[0].nick_name
                        )
                    )
                else:
                    raise ValueError(
                        VSPOneServerMSG.SERVER_ID_OR_NICKNAME_REQUIRED.value
                    )

            # Check if server exists
            try:
                existing_server = self.get_server_by_id(server_id)
                if not existing_server:
                    raise ValueError(
                        VSPOneServerMSG.SERVER_WITH_ID_NOT_EXIST.value.format(
                            server_id=server_id
                        )
                    )
                # Ensure spec has server_id set
                args[0].server_id = server_id
                args = list(args)
                if len(args) < 2:
                    # Pass server object to method
                    args.append(existing_server)
                else:
                    # Pass server object to method
                    args[1] = existing_server
                args = tuple(args)
            except Exception as e:
                raise ValueError(
                    VSPOneServerMSG.ERROR_CHECKING_SERVER_EXISTENCE.value.format(
                        error=str(e)
                    )
                )

        func(self, *args, **kwargs)
        server = self.get_server_by_id_with_details(server_id)
        return server.camel_to_snake_dict() if server else None

    return wrapper


class VSPServerSimpleApiProvisioner:
    """
    VSPServerSimpleApiProvisioner
    """

    def __init__(self, connection_info):
        self.gateway = VspServerSimpleApiGateway(connection_info)
        self.connection_info = connection_info
        if not self.gateway.is_pegasus:
            raise VspFeatureNotSupportedError(
                VSPVolumeMSG.ONLY_SUPPORTED_ON_PEGASUS.value
            )

    @log_entry_exit
    def create_update_server(self, spec: CreateServerSpec):
        """
        Create server
        """
        existing_server = None
        if spec.server_id is not None:
            existing_server = (
                self.get_server_by_id(spec.server_id) if spec.server_id else None
            )
        elif spec.nick_name is not None:
            existing_server = self.get_server_by_nick_name(spec.nick_name)

        if existing_server:
            spec.server_id = existing_server.id
            self.update_server_settings(spec, existing_server)
        else:
            try:
                response = self.register_server(spec)
                spec.server_id = response
                self.connection_info.changed = True

            except Exception as e:
                logger.writeError(
                    VSPOneServerMSG.ERROR_CREATING_SERVER.value.format(str(e))
                )

                spec.errors.append(
                    VSPOneServerMSG.ERROR_CREATING_SERVER.value.format(str(e))
                )
                return None

            if spec.hbas and len(spec.hbas) > 0:
                self.add_wwn_of_hba(spec, spec.server_id)

            if spec.paths is not None:
                self.add_path_to_server(spec, spec.server_id)

            if spec.host_groups is not None:
                self.add_hg_to_server(spec, spec.server_id)

            if spec.iscsi_targets is not None:
                self.add_hg_to_server(spec, spec.server_id)

        existing_server = self.get_server_by_id_with_details(spec.server_id)

        return existing_server.camel_to_snake_dict()

    @log_entry_exit
    def create_servers_bulk(self, spec: CreateServerSpec):
        """
        Create multiple servers, then optionally add HBAs and paths.
        The API accepts at most 100 server entries per request; larger sets
        are automatically split into batches of 100.

        Idempotent: servers that already exist are skipped. If all requested
        servers already exist the operation returns changed=False.
        """
        MAX_SERVERS_PER_REQUEST = 100

        if not spec.servers:
            raise ValueError(VSPOneServerMSG.BULK_SERVERS_REQUIRED.value)

        # Expand entries that carry a count > 1 into individual (nickname, template) pairs.
        expanded = []  # list of (resolved_nickname, BulkCreateServerSpec)
        for entry in spec.servers:
            if entry.nickname is None:
                raise ValueError("nickname is required for each entry in servers.")
            for resolved_name in entry.expand():
                expanded.append((resolved_name, entry))

        # ------------------------------------------------------------------
        # Idempotency check — skip servers that already exist on the storage.
        # ------------------------------------------------------------------
        new_entries = []
        skipped_names = []
        for name, entry in expanded:
            existing = self.get_server_by_nick_name(name)
            if existing is not None:
                logger.writeDebug(
                    f"create_servers_bulk: server '{name}' already exists "
                    f"(id={existing.id}), skipping creation."
                )
                skipped_names.append(name)
            else:
                new_entries.append((name, entry))

        if skipped_names:
            spec.comments.append(
                f"Skipped {len(skipped_names)} already-existing server(s): "
                + ", ".join(skipped_names)
            )

        if not new_entries:
            # All servers already exist — nothing to do.
            logger.writeDebug("create_servers_bulk: all servers already exist, no changes.")
            spec.comments.append(
                VSPOneServerMSG.BULK_SERVER_OPERATION_SUCCESS.value.format(
                    operation="create_servers"
                )
            )
            return self._get_servers_details_by_nicknames(
                [name for name, entry in expanded], spec
            )

        # Build payload only for servers that don't yet exist, then send in
        # batches of MAX_SERVERS_PER_REQUEST to stay within the API limit.
        payload = [
            entry.generate_create_payload(resolved_nickname=name)
            for name, entry in new_entries
        ]

        total = len(payload)
        batch_count = (total + MAX_SERVERS_PER_REQUEST - 1) // MAX_SERVERS_PER_REQUEST
        logger.writeDebug(
            f"create_servers_bulk: creating {total} new server(s) "
            f"in {batch_count} batch(es) of up to {MAX_SERVERS_PER_REQUEST}."
        )

        for i in range(0, total, MAX_SERVERS_PER_REQUEST):
            batch = payload[i: i + MAX_SERVERS_PER_REQUEST]
            logger.writeDebug(
                f"create_servers_bulk: batch {i // MAX_SERVERS_PER_REQUEST + 1}/{batch_count} "
                f"— {len(batch)} server(s): "
                + str([p.get("serverNickname") for p in batch])
            )
            self.gateway.create_servers_bulk(batch)

        self.connection_info.changed = True

        # Determine which new entries need HBAs or paths added.
        needs_hba = [(name, entry) for name, entry in new_entries if entry.has_hbas()]
        needs_path = [(name, entry) for name, entry in new_entries if entry.has_paths()]

        if needs_hba or needs_path:
            nicknames_needed = set(name for name, entry in needs_hba + needs_path)
            nickname_to_id = {}
            for nickname in nicknames_needed:
                server = self.get_server_by_nick_name(nickname)
                if server is None:
                    logger.writeError(
                        f"Could not find newly created server '{nickname}'; "
                        "skipping HBA/path registration for this server."
                    )
                    continue
                nickname_to_id[nickname] = server.id

            if needs_hba:
                hba_payload = []
                for name, entry in needs_hba:
                    server_id = nickname_to_id.get(name)
                    if server_id is None:
                        continue
                    hbas = []
                    for hba in entry.hbas:
                        hba_item = {}
                        if hba.hba_wwn is not None:
                            hba_item["hbaWwn"] = hba.hba_wwn
                        if hba.iscsi_name is not None:
                            hba_item["iscsiName"] = hba.iscsi_name
                        if hba_item:
                            hbas.append(hba_item)
                    if hbas:
                        hba_payload.append({"serverId": server_id, "hbas": hbas})
                if hba_payload:
                    self.gateway.add_wwn_of_hba_bulk(hba_payload)

            if needs_path:
                path_payload = []
                for name, entry in needs_path:
                    server_id = nickname_to_id.get(name)
                    if server_id is None:
                        continue
                    for path in entry.paths:
                        path_item = {"serverId": server_id, "portIds": path.port_ids}
                        if path.hba_wwn is not None:
                            path_item["hbaWwn"] = path.hba_wwn
                        if path.iscsi_name is not None:
                            path_item["iscsiName"] = path.iscsi_name
                        path_payload.append(path_item)
                if path_payload:
                    self.gateway.add_path_to_server_bulk(path_payload)

        spec.comments.append(
            VSPOneServerMSG.BULK_SERVER_OPERATION_SUCCESS.value.format(
                operation="create_servers"
            )
        )
        # Return enriched server objects for all expanded nicknames.
        return self._get_servers_details_by_nicknames(
            [name for name, entry in expanded], spec
        )

    def _get_servers_details_by_nicknames(self, nicknames, spec):
        """
        Look up each server by nickname and return a list of enriched server
        dicts. Servers that cannot be found are skipped with a warning.
        """
        results = []
        for nickname in nicknames:
            server = self.get_server_by_nick_name(nickname)
            if server is None:
                logger.writeError(
                    f"Could not retrieve details for server '{nickname}'."
                )
                continue
            details = self.get_server_by_id_with_details(server.id)
            if details is not None:
                results.append(details.camel_to_snake_dict())
        return results

    @log_entry_exit
    def add_hba_bulk(self, spec: CreateServerSpec):
        """
        Add HBAs/iSCSI names to multiple servers.
        """
        if not spec.bulk_hbas:
            raise ValueError(VSPOneServerMSG.BULK_HBAS_REQUIRED.value)

        payload = []
        for entry in spec.bulk_hbas:
            if entry.server_id is None:
                raise ValueError("server_id is required for each entry in bulk_hbas.")
            if not entry.hbas:
                raise ValueError("hbas list is required for each entry in bulk_hbas.")

            # Idempotency: collect HBAs already present on the server so we
            # only add new ones.
            existing_server = self.get_server_by_id_with_details(entry.server_id)
            existing_hbas = set()
            if existing_server is not None and existing_server.paths:
                for path in existing_server.paths:
                    if path.hbaWwn is not None:
                        existing_hbas.add(path.hbaWwn)
                    if path.iscsiName is not None:
                        existing_hbas.add(path.iscsiName)

            hbas = []
            for hba in entry.hbas:
                if hba.hba_wwn in existing_hbas or hba.iscsi_name in existing_hbas:
                    spec.comments.append(
                        f"HBA '{hba.hba_wwn or hba.iscsi_name}' already exists on "
                        f"server {entry.server_id}. Skipping."
                    )
                    continue

                hba_payload = {}
                if hba.hba_wwn is not None:
                    hba_payload["hbaWwn"] = hba.hba_wwn
                if hba.iscsi_name is not None:
                    hba_payload["iscsiName"] = hba.iscsi_name
                if not hba_payload:
                    raise ValueError(
                        "Either hba_wwn or iscsi_name must be provided in bulk_hbas."
                    )
                hbas.append(hba_payload)

            if hbas:
                payload.append({"serverId": entry.server_id, "hbas": hbas})

        if payload:
            # API limit: max 32 server entries per add-HBA request.
            MAX_HBA_PER_REQUEST = 32
            for i in range(0, len(payload), MAX_HBA_PER_REQUEST):
                batch = payload[i: i + MAX_HBA_PER_REQUEST]
                logger.writeDebug(
                    f"add_hba_bulk: batch {i // MAX_HBA_PER_REQUEST + 1} "
                    f"— {len(batch)} server(s)."
                )
                self.gateway.add_wwn_of_hba_bulk(batch)
            self.connection_info.changed = True
            spec.comments.append(
                VSPOneServerMSG.BULK_SERVER_OPERATION_SUCCESS.value.format(
                    operation="add_hba_bulk"
                )
            )
        return self._get_servers_details_by_ids(
            [entry.server_id for entry in spec.bulk_hbas], spec
        )

    @log_entry_exit
    def add_path_bulk(self, spec: CreateServerSpec):
        """
        Add paths to multiple servers.
        """
        if not spec.bulk_paths:
            raise ValueError(VSPOneServerMSG.BULK_PATHS_REQUIRED.value)

        payload = []
        for entry in spec.bulk_paths:
            if entry.server_id is None:
                raise ValueError("server_id is required for each entry in bulk_paths.")
            if not entry.paths:
                raise ValueError("paths list is required for each entry in bulk_paths.")

            # Idempotency: collect (hba/iscsi, portId) pairs already present on
            # the server so we only add new paths.
            existing_server = self.get_server_by_id_with_details(entry.server_id)
            existing_paths = set()
            if existing_server is not None and existing_server.paths:
                for existing_path in existing_server.paths:
                    identifier = existing_path.hbaWwn or existing_path.iscsiName
                    for port_id in existing_path.portIds or []:
                        existing_paths.add((identifier, port_id))

            for path in entry.paths:
                identifier = path.hba_wwn or path.iscsi_name
                new_port_ids = [
                    port_id
                    for port_id in path.port_ids
                    if (identifier, port_id) not in existing_paths
                ]
                if not new_port_ids:
                    spec.comments.append(
                        f"Path for '{identifier}' on server {entry.server_id} "
                        f"already exists. Skipping."
                    )
                    continue

                path_payload = {
                    "serverId": entry.server_id,
                    "portIds": new_port_ids,
                }
                if path.hba_wwn is not None:
                    path_payload["hbaWwn"] = path.hba_wwn
                if path.iscsi_name is not None:
                    path_payload["iscsiName"] = path.iscsi_name
                payload.append(path_payload)

        if payload:
            # API limit: max 64 path entries per add-path request.
            MAX_PATHS_PER_REQUEST = 64
            for i in range(0, len(payload), MAX_PATHS_PER_REQUEST):
                batch = payload[i: i + MAX_PATHS_PER_REQUEST]
                logger.writeDebug(
                    f"add_path_bulk: batch {i // MAX_PATHS_PER_REQUEST + 1} "
                    f"— {len(batch)} path entry(ies)."
                )
                self.gateway.add_path_to_server_bulk(batch)
            self.connection_info.changed = True
            spec.comments.append(
                VSPOneServerMSG.BULK_SERVER_OPERATION_SUCCESS.value.format(
                    operation="add_path_bulk"
                )
            )
        return self._get_servers_details_by_ids(
            [entry.server_id for entry in spec.bulk_paths], spec
        )

    @log_entry_exit
    def remove_path_bulk(self, spec: CreateServerSpec):
        """
        Remove paths from multiple servers.
        """
        if not spec.bulk_remove_paths:
            raise ValueError(VSPOneServerMSG.BULK_REMOVE_PATHS_REQUIRED.value)

        payload = []
        for entry in spec.bulk_remove_paths:
            if entry.server_id is None:
                raise ValueError(
                    "server_id is required for each entry in bulk_remove_paths."
                )
            if not entry.paths:
                raise ValueError(
                    "paths list is required for each entry in bulk_remove_paths."
                )

            # Idempotency: collect (hba/iscsi, portId) pairs currently present on
            # the server so we only remove paths that actually exist.
            existing_server = self.get_server_by_id_with_details(entry.server_id)
            existing_paths = set()
            if existing_server is not None and existing_server.paths:
                for existing_path in existing_server.paths:
                    identifier = existing_path.hbaWwn or existing_path.iscsiName
                    for port_id in existing_path.portIds or []:
                        existing_paths.add((identifier, port_id))

            for path in entry.paths:
                identifier = path.hba_wwn or path.iscsi_name
                port_ids_to_remove = [
                    port_id
                    for port_id in path.port_ids
                    if (identifier, port_id) in existing_paths
                ]
                if not port_ids_to_remove:
                    spec.comments.append(
                        f"Path for '{identifier}' on server {entry.server_id} "
                        f"does not exist. Skipping."
                    )
                    continue

                path_payload = {
                    "serverId": entry.server_id,
                    "portIds": port_ids_to_remove,
                }
                if path.hba_wwn is not None:
                    path_payload["hbaWwn"] = path.hba_wwn
                if path.iscsi_name is not None:
                    path_payload["iscsiName"] = path.iscsi_name
                payload.append(path_payload)

        if payload:
            # API limit: max 64 path entries per remove-path request.
            MAX_PATHS_PER_REQUEST = 64
            for i in range(0, len(payload), MAX_PATHS_PER_REQUEST):
                batch = payload[i: i + MAX_PATHS_PER_REQUEST]
                logger.writeDebug(
                    f"remove_path_bulk: batch {i // MAX_PATHS_PER_REQUEST + 1} "
                    f"— {len(batch)} path entry(ies)."
                )
                self.gateway.remove_path_from_server_bulk(batch)
            self.connection_info.changed = True
            spec.comments.append(
                VSPOneServerMSG.BULK_SERVER_OPERATION_SUCCESS.value.format(
                    operation="remove_path_bulk"
                )
            )
        return self._get_servers_details_by_ids(
            [entry.server_id for entry in spec.bulk_remove_paths], spec
        )

    @log_entry_exit
    def register_server(self, spec: CreateServerSpec):
        """
        Register server
        """
        if spec.protocol == ISCSI and spec.hbas and spec.hbas[0].iscsi_name is None:
            raise ValueError(VSPOneServerMSG.ISCSI_NAME_REQUIRED_FOR_ISCSI.value)
        elif spec.protocol == FC and spec.hbas and spec.hbas[0].hba_wwn is None:
            raise ValueError(VSPOneServerMSG.HBA_WWN_REQUIRED_FOR_FC.value)

        return self.gateway.register_server(spec)

    @log_entry_exit
    def delete_server(self, spec: CreateServerSpec, server_object=None):
        """
        Delete server

        """
        if spec.server_id is not None:
            existing_server = (
                self.get_server_by_id(spec.server_id) if spec.server_id else None
            )
        elif spec.nick_name is not None:
            existing_server = self.get_server_by_nick_name(spec.nick_name)

        if not existing_server:
            spec.comments.append(VSPOneServerMSG.SERVER_NOT_FOUND_OR_DELETED.value)
            return
        spec.server_id = existing_server.id
        try:
            self.gateway.delete_server(spec.server_id, spec)
            self.connection_info.changed = True
            spec.comments.append(VSPOneServerMSG.SERVER_DELETED_SUCCESS.value)
        except Exception as e:
            logger.writeError(
                VSPOneServerMSG.ERROR_DELETING_SERVER.value.format(error=e)
            )
            spec.errors.append(
                VSPOneServerMSG.ERROR_DELETING_SERVER.value.format(error=e)
            )
        return

    @log_entry_exit
    def update_server_settings(self, spec: CreateServerSpec, server):
        """
        Handle existing server
        """
        if spec.os_type is not None and spec.os_type == server.osType:
            spec.os_type = None  # No change needed
        if spec.nick_name is not None and spec.nick_name == server.nickname:
            spec.nick_name = None  # No change needed

        try:
            response = self.gateway.change_server_settings(spec.server_id, spec)
            if response:
                self.connection_info.changed = True
                spec.comments.append(VSPOneServerMSG.SERVER_UPDATED_SUCCESS.value)
        except Exception as e:
            logger.writeError(
                VSPOneServerMSG.ERROR_UPDATING_SERVER.value.format(error=e)
            )
            spec.errors.append(
                VSPOneServerMSG.ERROR_UPDATING_SERVER.value.format(error=e)
            )

    @check_server_exists
    @log_entry_exit
    def add_hg_to_server(self, spec: CreateServerSpec, server_object=None):
        """
        Add host group to server
        """
        try:
            self.gateway.add_hg_to_server(spec.server_id, spec)
            self.connection_info.changed = True
            spec.comments.append(VSPOneServerMSG.HOST_GROUP_ADDED_SUCCESS.value)
        except Exception as e:
            logger.writeError(
                VSPOneServerMSG.ERROR_ADDING_HOST_GROUP.value.format(error=e)
            )
            spec.errors.append(
                VSPOneServerMSG.ERROR_ADDING_HOST_GROUP.value.format(error=e)
            )

    @log_entry_exit
    @check_server_exists
    def add_path_to_server(self, spec, server_object=None):
        """
        Add path to server
        """
        if not self._validate_hba_for_protocol(spec, server_object):
            return

        if spec.paths is None or len(spec.paths) == 0:
            raise ValueError(VSPOneServerMSG.PATHS_LIST_REQUIRED.value)
        for path in spec.paths:
            try:
                response = self.gateway.add_path_to_server(spec.server_id, path)
                self.connection_info.changed = True
                spec.comments.append(
                    VSPOneServerMSG.PATH_ADDED_SUCCESS.value.format(
                        port_ids=path.port_ids
                    )
                )
            except Exception as e:
                logger.writeError(
                    VSPOneServerMSG.ERROR_VALIDATING_EXISTING_PATHS.value.format(
                        error=e
                    )
                )
                spec.errors.append(
                    VSPOneServerMSG.ERROR_VALIDATING_EXISTING_PATHS.value.format(
                        error=e
                    )
                )
                return None

        return response

    @log_entry_exit
    @check_server_exists
    def remove_path_from_server(self, spec: ServerFactsSpec, server_object=None):
        """
        Remove path from server
        """
        if not self._validate_hba_for_protocol(spec, server_object):
            return

        if spec.paths is None or len(spec.paths) == 0:
            raise ValueError(VSPOneServerMSG.PATHS_LIST_REQUIRED.value)
        for path in spec.paths:
            try:
                for port_id in path.port_ids:
                    self.gateway.remove_path_from_server(
                        spec.server_id, port_id, path.iscsi_name, path.hba_wwn
                    )
                    spec.comments.append(
                        VSPOneServerMSG.PATH_REMOVED_SUCCESS.value.format(
                            port_id=port_id
                        )
                    )
                    self.connection_info.changed = True
            except Exception as e:
                logger.writeError(
                    VSPOneServerMSG.ERROR_REMOVING_PATH.value.format(error=e)
                )
                spec.errors.append(
                    VSPOneServerMSG.ERROR_REMOVING_PATH.value.format(error=e)
                )
        return

    @log_entry_exit
    def change_server_settings(self, server_id, spec):
        """
        Change server settings
        """
        response = self.gateway.change_server_settings(server_id, spec)
        return response

    def _get_servers_details_by_ids(self, server_ids, spec):
        """
        Fetch enriched details for each server ID and return a list of dicts.
        Servers that cannot be retrieved are skipped with a warning.
        """
        results = []
        for server_id in server_ids:
            details = self.get_server_by_id_with_details(server_id)
            if details is not None:
                results.append(details.camel_to_snake_dict())
            else:
                logger.writeError(
                    f"Could not retrieve details for server id {server_id}."
                )
        return results

    @log_entry_exit
    def get_server_by_id(self, server_id: int):
        """
        Get server
        """
        response = self.gateway.get_server_by_id(server_id)
        return response

    @log_entry_exit
    def get_server_by_id_with_details(self, server_id: int):
        """
        Get server
        """
        response = self.gateway.get_server_by_id_with_details(server_id)
        return response

    @log_entry_exit
    def get_server_by_nick_name(self, nick_name: str):
        """
        Get server by nick name
        """
        pattern = r"^[\w,./:@\\]([\w,\-./:@\\ ]*[\w,\-./:@\\])?$"

        if not re.match(pattern, nick_name):
            raise ValueError(VSPOneServerMSG.NAME_ERROR.value)

        try:
            response = self.gateway.get_all_servers_with_filter(nick_name=nick_name)
            if len(response.data) > 0:
                return response.data[0]
        except Exception as ex:
            logger.writeError(f"Error getting server with nick name {nick_name}: {ex}")
            return None
        return None

    @log_entry_exit
    @check_server_exists
    def sync_server_nick_name(self, spec: ServerFactsSpec, server_object=None):
        """
        Sync server nick name
        """
        response = self.gateway.sync_server_nick_name(spec.server_id)
        self.connection_info.changed = True
        spec.comments.append(VSPOneServerMSG.SERVER_NICKNAME_SYNCED_SUCCESS.value)
        return response

    @log_entry_exit
    @check_server_exists
    def add_wwn_of_hba(self, spec: CreateServerSpec, server_object=None):
        """
        Add wwn of hba to server spec
        """
        if not spec.hbas or len(spec.hbas) == 0:
            raise ValueError(VSPOneServerMSG.HBA_LIST_REQUIRED.value)

        if not self._validate_hba_for_protocol(spec, server_object):
            return

        if isinstance(server_object, VspOneServerResponse):

            hba_wwns = [
                hba.hbaWwn for hba in server_object.paths if hba.hbaWwn is not None
            ]
            if not hba_wwns:
                hba_wwns = [
                    hba.iscsiName
                    for hba in server_object.paths
                    if hba.iscsiName is not None
                ]
            for hba in spec.hbas:
                if (hba.hba_wwn in hba_wwns) or (hba.iscsi_name in hba_wwns):
                    spec.hbas.remove(hba)

            if len(spec.hbas) == 0:
                logger.writeInfo("No new HBAs to add after filtering.")
                spec.comments.append(VSPOneServerMSG.NO_NEW_HBAS_TO_ADD.value)
                return None
        response = self.gateway.add_wwn_of_hba(spec)
        self.connection_info.changed = True
        spec.comments.append(VSPOneServerMSG.WWN_HBA_ADDED_SUCCESS.value)
        return response

    @log_entry_exit
    @check_server_exists
    def remove_wwn_of_hba(self, spec: CreateServerSpec, server_object=None):
        """
        Remove wwn of hba from server spec
        """
        if not spec.hbas or len(spec.hbas) == 0:
            raise ValueError(VSPOneServerMSG.HBA_LIST_REQUIRED.value)

        if not self._validate_hba_for_protocol(spec, server_object):
            return

        try:
            hbas = [hba.hbaWwn or hba.iscsiName for hba in server_object.paths]
            if not hbas:
                return None
            for hba in spec.hbas:
                if (hba.hba_wwn or hba.iscsi_name) in hbas:
                    wwn_or_iscsi = hba.hba_wwn if hba.hba_wwn else hba.iscsi_name
                    self.gateway.remove_wwn_of_hba(spec.server_id, wwn_or_iscsi)

                    spec.comments.append(
                        VSPOneServerMSG.WWN_HBA_REMOVED_SUCCESS.value.format(
                            wwn_or_iscsi=wwn_or_iscsi
                        )
                    )
                    self.connection_info.changed = True
        except Exception as e:
            logger.writeError(
                VSPOneServerMSG.ERROR_REMOVING_WWN_HBA.value.format(error=e)
            )
            spec.errors.append(
                VSPOneServerMSG.ERROR_REMOVING_WWN_HBA.value.format(error=e)
            )
        return

    @log_entry_exit
    @check_server_exists
    def change_iscsi_target_settings(self, spec: CreateServerSpec, server_object=None):
        """
        Change iscsi target settings
        """
        if spec.iscsi_target_settings is None:
            raise ValueError(VSPOneServerMSG.ISCSI_TARGET_PORT_ID_REQUIRED.value)

        for target in spec.iscsi_target_settings:
            if target.port_id is None or target.target_iscsi_name is None:
                raise ValueError(VSPOneServerMSG.ISCSI_TARGET_BOTH_REQUIRED.value)
            try:
                unused = self.gateway.change_iscsi_target_settings(
                    spec.server_id, target.port_id, target.target_iscsi_name
                )
                self.connection_info.changed = True
                spec.comments.append(
                    VSPOneServerMSG.ISCSI_TARGET_CHANGED_SUCCESS.value.format(
                        port_id=target.port_id
                    )
                )
            except Exception as e:
                logger.writeError(
                    VSPOneServerMSG.ERROR_CHANGING_ISCSI_TARGET.value.format(
                        port_id=target.port_id, error=e
                    )
                )
                spec.errors.append(
                    VSPOneServerMSG.ERROR_CHANGING_ISCSI_TARGET.value.format(
                        port_id=target.port_id, error=e
                    )
                )
        return

    @log_entry_exit
    def get_server_hbas(self, spec):
        """
        Get HBAs for a server
        """
        if spec.server_id is None and spec.nick_name is None:
            raise ValueError(VSPOneServerMSG.SERVER_ID_NAME_REQUIRED.value)

        if spec.server_id is None and spec.nick_name is not None:
            existing_server = self.get_server_by_nick_name(spec.nick_name)
            if existing_server:
                spec.server_id = existing_server.id
            else:
                raise ValueError(
                    VSPOneServerMSG.SERVER_WITH_NICKNAME_NOT_FOUND.value.format(
                        nickname=spec.nick_name
                    )
                )
        if spec.hba_wwn is not None or spec.iscsi_name is not None:
            existing_hba = self.gateway.get_hba_by_wwn(
                spec.server_id,
                spec.hba_wwn if spec.hba_wwn is not None else spec.iscsi_name,
            )
            if existing_hba:
                return existing_hba.camel_to_snake_dict()
            else:
                return "HBA not found."
        else:
            hbas = self.gateway.get_hbas_by_server_id(spec.server_id)
            return hbas.data_to_snake_case_list() if hbas else []

    def _validate_hba_for_protocol(self, spec: CreateServerSpec, server_object=None):
        """
        Validate HBA based on server protocol
        """

        if isinstance(server_object, VspOneServerResponse):
            if server_object.protocol.upper() == ISCSI:
                # Check if all HBAs have iscsi_name when HBAs are provided
                if spec.hbas and all(hba.iscsi_name is None for hba in spec.hbas):
                    spec.errors.append(
                        VSPOneServerMSG.ISCSI_NAME_REQUIRED_FOR_ISCSI.value
                    )
                    return False
                # Check if all paths have iscsi_name when paths are provided
                if spec.paths and any(path.iscsi_name is None for path in spec.paths):
                    spec.errors.append(
                        VSPOneServerMSG.ISCSI_NAME_REQUIRED_FOR_ISCSI.value
                    )
                    return False
            elif server_object.protocol.upper() == FC:
                # Check if all HBAs have hba_wwn when HBAs are provided
                if spec.hbas and any(hba.hba_wwn is None for hba in spec.hbas):
                    spec.errors.append(VSPOneServerMSG.HBA_WWN_REQUIRED_FOR_FC.value)
                    return False
                if spec.paths and all(path.hba_wwn is None for path in spec.paths):
                    spec.errors.append(VSPOneServerMSG.HBA_WWN_REQUIRED_FOR_FC.value)
                    return False
        return True
