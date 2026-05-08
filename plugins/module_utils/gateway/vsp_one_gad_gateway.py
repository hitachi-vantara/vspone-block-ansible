try:
    from .gateway_manager import VSPConnectionManager
    from ..model.vsp_one_gad_models import (
        VspOneGadResponse,
        VspOneGadList,
    )
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from .vsp_storage_system_gateway import VSPStorageSystemDirectGateway

except ImportError:
    from .gateway_manager import VSPConnectionManager
    from model.vsp_one_gad_models import (
        VspOneGadResponse,
        VspOneGadList,
    )
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from .vsp_storage_system_gateway import VSPStorageSystemDirectGateway

# VspOne GAD Endpoints
GET_GAD_PAIRS_SIMPLE = "simple/v1/objects/active-active-mirroring-pairs"
GET_GAD_PAIR_BY_ID_SIMPLE = "simple/v1/objects/active-active-mirroring-pairs/{}"
DELETE_GAD_PAIRS_SIMPLE = (
    "simple/v1/objects/active-active-mirroring-pairs/actions/delete/invoke"
)
SUSPEND_GAD_PAIRS_SIMPLE = (
    "simple/v1/objects/active-active-mirroring-pairs/actions/suspend/invoke"
)
RESYNC_GAD_PAIRS_SIMPLE = (
    "simple/v1/objects/active-active-mirroring-pairs/actions/resync/invoke"
)

logger = Log()


class VspOneGadGateway:
    def __init__(self, connection_info):
        self.connection_info = connection_info
        self.rest_api = VSPConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )
        self.storage_gw = VSPStorageSystemDirectGateway(connection_info)
        self.is_block_high_end = self.storage_gw.is_block_high_end()
        # Standard header required for Pegasus GAD APIs
        self.gad_headers = {"X-Agent-Type": "SEA"}

    @log_entry_exit
    def get_gad_pairs_facts(self, spec):
        all_data = []
        has_next = True
        page_count = 0

        # Determine the user's desired limit (default to a high number if not set)
        requested_limit = spec.count if (spec and spec.count) else float("inf")

        current_spec = spec

        while has_next:
            page_count += 1

            # 1. Build endpoint
            endpoint = GET_GAD_PAIRS_SIMPLE
            if current_spec and not current_spec.is_empty():
                endpoint += self.get_query_parameters_for_gad_facts(current_spec)

            # 2. API Call
            response = self.rest_api.pegasus_get(
                endpoint, headers_input=self.gad_headers
            )

            # 3. Collect Data
            batch = response.get("data", [])
            all_data.extend(batch)

            logger.writeInfo(
                f"GW:GAD_FACT: Page {page_count} fetched {len(batch)} items. Total: {len(all_data)}/{requested_limit}"
            )

            # 4. Check if we have met or exceeded the user's requested count
            if len(all_data) >= requested_limit:
                logger.writeInfo(
                    "GW:GAD_FACT: Requested count reached. Stopping retrieval."
                )
                # Optional: Trim if batch put us over the limit
                all_data = all_data[:requested_limit]
                break

            # 5. Check API Pagination
            has_next = response.get("hasNext", False)

            if has_next and batch:
                last_item = batch[-1]
                current_spec.primary_volume_id = last_item.get("localVolumeId")
                current_spec.mirror_unit_number = last_item.get("muNumber")

                # Adjust 'count' for the next call to only get what's remaining
                # This prevents the final page from being unnecessarily large
                remaining = requested_limit - len(all_data)
                if remaining < current_spec.count:
                    current_spec.count = remaining
            else:
                has_next = False

        return VspOneGadList(data=all_data)

    @log_entry_exit
    def get_gad_pair_by_id(self, local_volume_id, mu_number):
        pair_id = f"{local_volume_id},{mu_number}"
        endpoint = GET_GAD_PAIR_BY_ID_SIMPLE.format(pair_id)
        try:
            response = self.rest_api.pegasus_get(
                endpoint, headers_input=self.gad_headers
            )
            return VspOneGadResponse(**response)
        except Exception as e:
            logger.writeError(f"GW:get_gad_pair_by_id: Error retrieving {pair_id}: {e}")
            raise ValueError(f"GAD pair with {pair_id} does not exist on the storage system.")

    @log_entry_exit
    def delete_gad_pairs(self, spec):
        final_payload = self.get_body_for_delete_gad(spec)
        response = self.rest_api.pegasus_post(
            DELETE_GAD_PAIRS_SIMPLE,
            data=final_payload,
            headers_input=self.gad_headers,
        )
        if response:
            self.connection_info.changed = True
        return response

    @log_entry_exit
    def suspend_gad_pairs(self, spec):
        final_payload = self.get_body_for_suspend_gad(spec)
        response = self.rest_api.pegasus_post(
            SUSPEND_GAD_PAIRS_SIMPLE,
            data=final_payload,
            headers_input=self.gad_headers,
        )
        if response:
            self.connection_info.changed = True
        return response

    @log_entry_exit
    def resync_gad_pairs(self, spec):
        final_payload = self.get_body_for_resync_gad(spec)
        response = self.rest_api.pegasus_post(
            RESYNC_GAD_PAIRS_SIMPLE,
            data=final_payload,
            headers_input=self.gad_headers,
        )
        if response:
            self.connection_info.changed = True
        return response

    @log_entry_exit
    def get_query_parameters_for_gad_facts(self, spec):
        params = {}
        if spec.consistency_group_id is not None:
            params["consistencyGroupId"] = spec.consistency_group_id

        # Mapping primary_volume_id + mu_number to the API startId
        # If mu_number is not provided (None), it defaults to 0
        if spec.primary_volume_id is not None:
            mu = spec.mirror_unit_number if spec.mirror_unit_number is not None else 0
            params["startId"] = f"{spec.primary_volume_id},{mu}"

        if spec.count is not None:
            params["count"] = spec.count

        query = ""
        if params:
            query_parts = [f"{k}={v}" for k, v in params.items()]
            query = "?" + "&".join(query_parts)
        return query

    @log_entry_exit
    def get_body_for_suspend_gad(self, spec):
        continue_io = getattr(spec, "continue_io_volume", "PRIMARY")
        if not continue_io:
            continue_io = "PRIMARY"
        body = {
            "ids": self._format_ids_for_api(spec.ids),
            "continueIoVolume": continue_io.upper(),
        }
        return body

    @log_entry_exit
    def get_body_for_delete_gad(self, spec):
        delete_mode = getattr(spec, "delete_mode", "NORMAL").upper()
        body = {
            "ids": self._format_ids_for_api(spec.ids),
            "deleteMode": delete_mode
        }
        if delete_mode == "FORCE":
            # Map boolean to API ENUM: ALLOW or DENY
            allow_access = getattr(spec, "allow_volume_access_after_force_delete", False)
            body["forceVolumeAccess"] = "ALLOW" if allow_access else "DENY"
        return body

    @log_entry_exit
    def get_body_for_resync_gad(self, spec):
        body = {
            "ids": self._format_ids_for_api(spec.ids),
            "swapResync": "ENABLE" if getattr(spec, "is_swap_resynced", False) else "DISABLE",
        }
        if getattr(spec, "copy_pace", None) is not None:
            body["copySpeed"] = spec.copy_pace

        io_pref = getattr(spec, "io_preference", "KEEP_CURRENT_SETTING")
        body["ioPreference"] = io_pref.upper()
        return body

    @log_entry_exit
    def _format_ids_for_api(self, ids):
        """
        Converts internal list ['100,1', '200,1']
        to API structure [{'localVolumeId': '100', 'muNumber': '1'}, ...]
        """
        formatted = []
        for id_str in ids:
            parts = id_str.split(",")
            formatted.append({"localVolumeId": parts[0], "muNumber": parts[1]})
        return formatted
