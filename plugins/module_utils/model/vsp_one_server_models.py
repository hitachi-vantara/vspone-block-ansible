from dataclasses import dataclass
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass
    from ..common.vsp_constants import (
        ServerPayloadConst,
    )
except ImportError:
    from common_base_models import BaseDataClass, SingleBaseClass


@dataclass
class ServerFactsSpec(SingleBaseClass):
    nick_name: Optional[str] = None
    hba_wwn: Optional[str] = None
    iscsi_name: Optional[int] = None
    server_id: Optional[int] = None
    nickname: Optional[str] = None
    include_details: Optional[bool] = None

    def __post_init__(self, **kwargs):
        if self.nickname is not None:
            self.nick_name = self.nickname


@dataclass
class ServerHBAFactsSpec(SingleBaseClass):
    server_id: Optional[int] = None
    nick_name: Optional[str] = None
    hba_wwn: Optional[str] = None
    iscsi_name: Optional[int] = None
    nickname: Optional[str] = None

    def __post_init__(self, **kwargs):
        if self.nickname is not None:
            self.nick_name = self.nickname


@dataclass
class HBASpec(SingleBaseClass):
    hba_wwn: Optional[str] = None
    iscsi_name: Optional[int] = None


@dataclass
class HostGroupSpec(SingleBaseClass):
    host_group_id: Optional[int] = None
    host_group_name: Optional[str] = None
    port_id: Optional[str] = None

    def __post_init__(self):
        if (self.host_group_id is not None and self.host_group_name is not None) or (
            self.host_group_id is None and self.host_group_name is None
        ):
            raise ValueError(
                "Either host_group_id or host_group_name must be provided, but not both"
            )
        if self.port_id is None:
            raise ValueError("port_id must be provided")


@dataclass
class IscsiTargetSpec(SingleBaseClass):
    iscsi_target_id: Optional[int] = None
    iscsi_target_name: Optional[str] = None
    port_id: Optional[str] = None

    def __post_init__(self):
        if (
            self.iscsi_target_id is not None and self.iscsi_target_name is not None
        ) or (self.iscsi_target_id is None and self.iscsi_target_name is None):
            raise ValueError(
                "Either iscsi_target_id or iscsi_target_name must be provided, but not both"
            )
        if self.port_id is None:
            raise ValueError("port_id must be provided")


@dataclass
class VspOneServerPath(SingleBaseClass):
    hbaWwn: Optional[str] = None
    iscsiName: Optional[str] = None
    portIds: Optional[List[str]] = None


@dataclass
class VspOneServerPathSpec(SingleBaseClass):
    hba_wwn: Optional[str] = None
    iscsi_name: Optional[str] = None
    port_ids: Optional[List[str]] = None

    def __post_init__(self):
        if (self.hba_wwn is not None and self.iscsi_name is not None) or (
            self.hba_wwn is None and self.iscsi_name is None
        ):
            raise ValueError(
                "Either hba_wwn or iscsi_name must be provided, but not both"
            )
        if self.port_ids is None or len(self.port_ids) == 0:
            raise ValueError("At least one port_id must be provided")


@dataclass
class IscsiTargetResponse(SingleBaseClass):
    portId: Optional[str] = None
    targetIscsiName: Optional[str] = None


@dataclass
class IscsiTargetList(BaseDataClass):
    data: List[IscsiTargetResponse] = None


@dataclass
class VspOneServerResponse(SingleBaseClass):
    id: Optional[int] = None
    nickname: Optional[str] = None
    protocol: Optional[str] = None
    osType: Optional[str] = None
    totalCapacity: Optional[int] = None
    usedCapacity: Optional[int] = None
    numberOfPaths: Optional[int] = None
    isInconsistent: Optional[bool] = None
    modificationInProgress: Optional[bool] = None
    compatibility: Optional[str] = None
    isReserved: Optional[bool] = None
    hasUnalignedOsTypes: Optional[bool] = None
    osTypeOptions: Optional[List[int]] = None
    numberOfVolumes: Optional[int] = None
    paths: Optional[List[VspOneServerPath]] = None
    hasNonFullmeshLuPaths: Optional[bool] = None
    hasUnalignedOsTypeOptions: Optional[bool] = None
    iscsiTargets: Optional[List[IscsiTargetList]] = None

    def __post_init__(self):
        if self.paths is not None:
            self.paths = [VspOneServerPath(**path) for path in self.paths]

        # if self.iscsiTargets is not None:
        #     self.iscsiTargets = IscsiTargetList(**self.iscsiTargets)


@dataclass
class VspOneServerList(BaseDataClass):
    data: List[VspOneServerResponse] = None


@dataclass
class WwnOfHBA(SingleBaseClass):
    serverId: Optional[int] = None
    hbaWwn: Optional[str] = None
    iscsiName: Optional[str] = None
    portIds: Optional[List[str]] = None


@dataclass
class WwnOfHBAList(BaseDataClass):
    data: List[WwnOfHBA] = None


@dataclass
class ServerPathsResponse(SingleBaseClass):
    id: Optional[str] = None
    serverId: Optional[int] = None
    hbaWwn: Optional[str] = None
    iscsiName: Optional[str] = None
    portId: Optional[str] = None


@dataclass
class ServerPathsList(BaseDataClass):
    data: List[ServerPathsResponse] = None


@dataclass
class ServerIscsiTargetsResponse(SingleBaseClass):
    portId: Optional[int] = None
    targetIscsiName: Optional[bool] = None


@dataclass
class ServerIscsiTargetsList(BaseDataClass):
    data: List[ServerIscsiTargetsResponse] = None


@dataclass
class IscsiTargetNameSpec(SingleBaseClass):
    target_iscsi_name: Optional[str] = None
    port_id: Optional[str] = None


MAX_BULK_SERVER_COUNT = 50


@dataclass
class BulkCreateServerSpec(SingleBaseClass):
    nickname: Optional[str] = None
    protocol: Optional[str] = None
    os_type: Optional[str] = None
    os_type_options: Optional[List[int]] = None
    is_reserved: Optional[bool] = None
    count: Optional[int] = None
    start_index: Optional[int] = None
    end_index: Optional[int] = None
    hbas: Optional[List[HBASpec]] = None
    paths: Optional[List[VspOneServerPathSpec]] = None

    def __post_init__(self):
        # -----------------------------------------------------------------------
        # Resolve the effective [start, end] range from the combination of
        # count / start_index / end_index that the user supplied.
        #
        # Supported combinations:
        #   count only              → [1, count]          (existing behaviour)
        #   start_index + end_index → [start_index, end_index]
        #   start_index + count     → [start_index, start_index + count - 1]
        #   none of the above       → single server, exact nickname
        #
        # Unsupported / ambiguous:
        #   count + end_index (without start_index) → error
        #   start_index + end_index + count         → error
        #   start_index alone                       → error
        #   end_index alone                         → error
        # -----------------------------------------------------------------------
        has_count = self.count is not None
        has_start = self.start_index is not None
        has_end = self.end_index is not None

        # Validate count before anything else so the error message is clear.
        if has_count:
            if self.count < 1:
                raise ValueError(
                    f"'count' must be at least 1, got {self.count}."
                )
            if self.count > MAX_BULK_SERVER_COUNT:
                raise ValueError(
                    f"'count' cannot exceed {MAX_BULK_SERVER_COUNT}, got {self.count}. "
                    "Split the request into multiple tasks to create more servers."
                )

        if has_start and has_end and has_count:
            raise ValueError(
                "Specify either 'start_index'+'end_index', 'start_index'+'count', "
                "or 'count' alone — not all three together."
            )
        if has_end and not has_start:
            raise ValueError(
                "'end_index' requires 'start_index' to be set as well."
            )
        if has_start and not has_end and not has_count:
            raise ValueError(
                "'start_index' must be paired with either 'end_index' or 'count'."
            )
        if has_count and has_end and not has_start:
            raise ValueError(
                "Combining 'count' with 'end_index' (without 'start_index') is ambiguous. "
                "Use 'start_index'+'end_index' or 'start_index'+'count' instead."
            )

        # Compute the resolved (start, end) that expand() will use.
        if has_start and has_end:
            resolved_start, resolved_end = self.start_index, self.end_index
        elif has_start and has_count:
            resolved_start = self.start_index
            resolved_end = self.start_index + self.count - 1
        elif has_count:
            resolved_start, resolved_end = 1, self.count
        else:
            resolved_start, resolved_end = None, None  # single server

        # Validate the resolved range.
        if resolved_start is not None:
            if resolved_start < 1:
                raise ValueError(
                    f"'start_index' must be at least 1, got {resolved_start}."
                )
            if resolved_end < resolved_start:
                raise ValueError(
                    f"'end_index' ({resolved_end}) must be greater than or equal to "
                    f"'start_index' ({resolved_start})."
                )
            effective_count = resolved_end - resolved_start + 1
            if effective_count > MAX_BULK_SERVER_COUNT:
                raise ValueError(
                    f"Range [{resolved_start}, {resolved_end}] produces {effective_count} servers "
                    f"which exceeds the limit of {MAX_BULK_SERVER_COUNT}. "
                    "Split the request into multiple tasks."
                )

            # When creating multiple servers, HBAs and paths cannot be shared.
            if effective_count > 1:
                if self.hbas:
                    raise ValueError(
                        "'hbas' cannot be specified when creating multiple servers. "
                        "HBA WWNs and iSCSI names are unique per physical host. "
                        "Use state=add_hba_bulk after server creation to add HBAs individually."
                    )
                if self.paths:
                    raise ValueError(
                        "'paths' cannot be specified when creating multiple servers. "
                        "Paths are bound to specific HBA WWNs or iSCSI names which are unique per host. "
                        "Use state=add_path_bulk after server creation to add paths individually."
                    )

        # Store resolved values for expand() to consume.
        self._resolved_start = resolved_start
        self._resolved_end = resolved_end

        if self.hbas is not None:
            self.hbas = [HBASpec(**hba) if isinstance(hba, dict) else hba for hba in self.hbas]
        if self.paths is not None:
            self.paths = [
                VspOneServerPathSpec(**path) if isinstance(path, dict) else path
                for path in self.paths
            ]

    def expand(self):
        """
        Expand this entry into a list of resolved server nicknames.

        Single server (no count / range):  returns [nickname]
        Range of servers:                  returns [nickname_01, nickname_02, ...]
          - zero-padding width is based on the largest index in the range
        """
        start = getattr(self, "_resolved_start", None)
        end = getattr(self, "_resolved_end", None)

        if start is None:
            return [self.nickname]

        pad = len(str(end))
        return [f"{self.nickname}_{i:0{pad}d}" for i in range(start, end + 1)]

    def generate_create_payload(self, resolved_nickname=None):
        payload = {}
        name = resolved_nickname if resolved_nickname is not None else self.nickname
        if name is not None:
            payload[ServerPayloadConst.serverNickname] = name
        if self.protocol is not None:
            payload[ServerPayloadConst.protocol] = self.protocol
        if self.os_type is not None:
            payload[ServerPayloadConst.osType] = self.os_type
        if self.os_type_options is not None:
            payload[ServerPayloadConst.osTypeOptions] = self.os_type_options
        if self.is_reserved is not None:
            payload[ServerPayloadConst.isReserved] = self.is_reserved
        return payload

    def has_hbas(self):
        return bool(self.hbas)

    def has_paths(self):
        return bool(self.paths)


@dataclass
class BulkServerHbaSpec(SingleBaseClass):
    server_id: Optional[int] = None
    hbas: Optional[List[HBASpec]] = None

    def __post_init__(self):
        if self.hbas is not None:
            self.hbas = [HBASpec(**hba) for hba in self.hbas]


@dataclass
class BulkServerPathSpec(SingleBaseClass):
    server_id: Optional[int] = None
    paths: Optional[List[VspOneServerPathSpec]] = None

    def __post_init__(self):
        if self.paths is not None:
            self.paths = [VspOneServerPathSpec(**path) for path in self.paths]


@dataclass
class CreateServerSpec(SingleBaseClass):
    server_id: Optional[int] = None
    nick_name: Optional[int] = None
    nickname: Optional[int] = None
    protocol: Optional[int] = None
    os_type: Optional[str] = None
    host_hba_wwn: Optional[str] = None
    host_iscsi_name: Optional[str] = None
    port_ids: Optional[List[str]] = None
    is_reserved: Optional[bool] = None
    os_type_options: Optional[List[int]] = None
    hbas: Optional[List[HBASpec]] = None
    keep_lun_config: Optional[bool] = None
    host_groups: Optional[List[HostGroupSpec]] = None
    iscsi_targets: Optional[List[IscsiTargetSpec]] = None
    comments: Optional[List[str]] = None
    paths: Optional[List[VspOneServerPathSpec]] = None
    iscsi_target_settings: Optional[List[IscsiTargetNameSpec]] = None
    errors: Optional[List[str]] = None
    servers: Optional[List[BulkCreateServerSpec]] = None
    bulk_hbas: Optional[List[BulkServerHbaSpec]] = None
    bulk_paths: Optional[List[BulkServerPathSpec]] = None
    bulk_remove_paths: Optional[List[BulkServerPathSpec]] = None

    def __post_init__(self):
        if self.hbas is not None:
            self.hbas = [HBASpec(**hba) for hba in self.hbas]

        if self.host_groups is not None and self.iscsi_targets is not None:
            raise ValueError(
                "host_groups and iscsi_targets cannot be provided together"
            )

        if self.host_groups is not None:
            self.host_groups = [HostGroupSpec(**hg) for hg in self.host_groups]

        if self.iscsi_targets is not None:
            self.iscsi_targets = [IscsiTargetSpec(**it) for it in self.iscsi_targets]

        if self.paths is not None:
            self.paths = [VspOneServerPathSpec(**path) for path in self.paths]

        if self.iscsi_target_settings is not None:
            self.iscsi_target_settings = [
                IscsiTargetNameSpec(**target) for target in self.iscsi_target_settings
            ]
        if self.nickname is not None:
            self.nick_name = self.nickname

        if self.servers is not None:
            self.servers = [BulkCreateServerSpec(**server) for server in self.servers]
        if self.bulk_hbas is not None:
            self.bulk_hbas = [BulkServerHbaSpec(**entry) for entry in self.bulk_hbas]
        if self.bulk_paths is not None:
            self.bulk_paths = [BulkServerPathSpec(**entry) for entry in self.bulk_paths]
        if self.bulk_remove_paths is not None:
            self.bulk_remove_paths = [
                BulkServerPathSpec(**entry) for entry in self.bulk_remove_paths
            ]

    def generate_create_payload(self):
        payload = {}
        if self.nick_name is not None:
            payload[ServerPayloadConst.serverNickname] = self.nick_name
        if self.protocol is not None:
            payload[ServerPayloadConst.protocol] = self.protocol
        if self.os_type is not None:
            payload[ServerPayloadConst.osType] = self.os_type
        if self.os_type_options is not None:
            payload[ServerPayloadConst.osTypeOptions] = self.os_type_options
        if self.is_reserved is not None:
            payload[ServerPayloadConst.isReserved] = self.is_reserved
        return payload

    def generate_server_settings_payload(self):
        payload = {}
        if self.nick_name is not None:
            payload[ServerPayloadConst.nickname] = self.nick_name
        if self.os_type is not None:
            payload[ServerPayloadConst.osType] = self.os_type
        if self.os_type_options is not None:
            payload[ServerPayloadConst.osTypeOptions] = self.os_type_options
        return payload


@dataclass
class VspOneServerHBAResponse(SingleBaseClass):
    serverId: Optional[int] = None
    hbaWwn: Optional[str] = None
    iscsiName: Optional[str] = None
    portIds: Optional[List[str]] = None


@dataclass
class VspOneServerHBAList(BaseDataClass):
    data: List[VspOneServerHBAResponse] = None
