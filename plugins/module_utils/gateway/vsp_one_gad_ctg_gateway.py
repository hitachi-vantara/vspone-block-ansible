import ast
from .gateway_manager import AdministratorConnectionManager
from ..model.vsp_gad_pairs_models import (
    VspGadCtgInfo,
    VspGadCtgInfoList,
    VspGadCtgCreateSpec,
    VspGadVolumePairInfo,
    VspGadVolumePairInfoList,
)
from ..common.hv_log import Log

from ..common.ansible_common import log_entry_exit
from .vsp_storage_system_gateway import VSPStorageSystemDirectGateway
from ..model.vsp_quorum_disk_models import VspOneQuorumDiskInfoList


VSP_ONE_GET_GAD_CTGS = "v1/objects/active-active-mirroring-consistency-groups"
VSP_ONE_GET_GAD_CTG_BY_ID = "v1/objects/active-active-mirroring-consistency-groups/{}"
VSP_ONE_SUSPEND_GAD_PAIRS = (
    "v1/objects/active-active-mirroring-consistency-groups/actions/suspend/invoke"
)
VSP_ONE_RESYNC_GAD_PAIRS = (
    "v1/objects/active-active-mirroring-consistency-groups/actions/resync/invoke"
)
CREATE_GAD_PAIR = "v1/objects/active-active-mirroring-pairs"
GET_ALL_GAD_PAIRS = "v1/objects/active-active-mirroring-pairs"
GET_GAD_PAIRS_BY_CTG_ID = (
    "v1/objects/active-active-mirroring-pairs?startId={}&consistencyGroupId={}"
)
GAD_PAIR_BY_ID = "v1/objects/active-active-mirroring-pairs/{}"
QUORUM_DISK_GET = "v1/objects/quorum-disks"
logger = Log()


class VspOneGadCtgGateway:

    def __init__(self, connection_info, secondary_connection_info):
        self.rest_api = AdministratorConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )
        self.storage_gw = VSPStorageSystemDirectGateway(connection_info)
        self.secondary_rest_api = AdministratorConnectionManager(
            secondary_connection_info.address,
            secondary_connection_info.username,
            secondary_connection_info.password,
            secondary_connection_info.api_token,
        )
        self.connection_info = connection_info
        self.is_block_high_end = self.storage_gw.is_block_high_end()

    @log_entry_exit
    def get_remote_token(self):
        secondary_headers = self.secondary_rest_api.getAuthToken()
        value = secondary_headers.get("Authorization")
        if value:
            token = value.split(" ")[1]  # Extract the token part
            return token
        return None

    @log_entry_exit
    def get_gad_ctgs(self):
        end_point = VSP_ONE_GET_GAD_CTGS
        headers = {}
        headers["X-Agent-Request-Id"] = self.get_remote_token()
        headers["X-Agent-Type"] = "SEA"
        has_next_page = True
        all_ctgs = []
        while has_next_page:
            response = self.rest_api.get(end_point, headers_input=headers)
            ctgs = response.get("data", [])
            all_ctgs.extend(ctgs)
            has_next_page = response.get("hasNext")
            if has_next_page:
                end_point = f"{VSP_ONE_GET_GAD_CTGS}?startId={response.get('count')}"
            else:
                has_next_page = False
        return VspGadCtgInfoList().dump_to_object({"data": all_ctgs})

    @log_entry_exit
    def get_gad_ctg_by_id(self, ctg_id):
        """
        Get GAD consistency group information by ID
        :param ctg_id: GAD consistency group ID
        :return: GAD consistency group information
        """
        endpoint = VSP_ONE_GET_GAD_CTG_BY_ID.format(ctg_id)
        try:
            headers = {}
            headers["X-Agent-Type"] = "SEA"
            headers["X-Agent-Request-Id"] = self.get_remote_token()
            response = self.rest_api.get(endpoint, headers_input=headers)
            return VspGadCtgInfo(**response)
        except Exception as e:
            logger.writeError(
                f"Error getting GAD consistency group by ID {ctg_id}: {e}"
            )
            return None

    @log_entry_exit
    def suspend_gad_pairs(self, ctg_ids, continue_io_volume):
        """
        Suspend GAD pairs in a consistency group
        :param ctg_ids: List of GAD consistency group IDs
        :param continue_io_volume: Whether to continue I/O volume
        :return: Result of the suspend operation
        """
        endpoint = VSP_ONE_SUSPEND_GAD_PAIRS
        try:
            headers = {}
            headers["X-Agent-Type"] = "SEA"
            headers["X-Agent-Request-Id"] = self.get_remote_token()
            payload = {
                "ids": ctg_ids,
                "continueIoVolume": continue_io_volume,
            }
            response = self.rest_api.post_without_job(
                endpoint, data=payload, headers_input=headers
            )
            data = response.get("data", [])
            ids = [item["id"] for item in data]
            return ids
        except Exception as e:
            logger.writeError(
                f"Error suspending GAD pairs in consistency groups {ctg_ids}: {e}"
            )
            if "cannot be suspended" in str(e):
                logger.writeError(
                    "Suspension failed because one or more GAD pairs are currently resyncing. Please wait for the resync to complete and try again."
                )
                raise ValueError(str(e))
            else:
                data = ast.literal_eval(str(e))
                error_msg = []
                for item in data["data"]:
                    if "errorCode" in item:
                        error_msg.append(
                            f"ID {item['id']}: Error Code: {item['errorCode']} Message: {item.get('errorMessage', 'No message provided')}"
                        )
                logger.writeError(f"Resync GAD pairs error details: {error_msg}")
                raise ValueError(", ".join(error_msg))

    @log_entry_exit
    def resync_gad_pairs(
        self,
        ctg_ids,
        is_swap_resynced=False,
        io_preference_mode="KEEP_CURRENT_SETTING",
        copy_pace=3,
    ):
        """
        Resync GAD pairs in a consistency group
        :param ctg_ids: List of GAD consistency group IDs
        :param is_swap_resynced: Whether to perform swap resync
        :param io_preference_mode: I/O preference mode
        :param copy_pace: Copy pace
        :return: Result of the resync operation
        """
        endpoint = VSP_ONE_RESYNC_GAD_PAIRS

        try:
            headers = {}
            headers["X-Agent-Type"] = "SEA"
            headers["X-Agent-Request-Id"] = self.get_remote_token()
            payload = {
                "ids": ctg_ids,
                "copySpeed": copy_pace,
                "ioPreference": io_preference_mode,
            }
            if is_swap_resynced:
                payload["swapResync"] = "ENABLE"
            else:
                payload["swapResync"] = "DISABLE"
            response = self.rest_api.post_without_job(
                endpoint, data=payload, headers_input=headers
            )
            logger.writeDebug(f"Resync GAD pairs response: {response}")
            data = response.get("data", [])
            ids = [item["id"] for item in data]
            return ids
        except Exception as e:
            logger.writeError(
                f"Error resyncing GAD pairs in consistency groups {ctg_ids}: {e}"
            )
            if "cannot be resynchronized" in str(e) or "are not found" in str(e):
                logger.writeError(
                    "Resync failed because one or more GAD pairs are currently resyncing. Please wait for the resync to complete and try again."
                )
                raise ValueError(str(e))
            else:
                data = ast.literal_eval(str(e))
                error_msg = []
                for item in data["data"]:
                    if "errorCode" in item:
                        error_msg.append(
                            f"ID {item['id']}: Error Code: {item['errorCode']} Message: {item.get('errorMessage', 'No message provided')}"
                        )
                logger.writeError(f"Resync GAD pairs error details: {error_msg}")
                raise ValueError(", ".join(error_msg))

    @log_entry_exit
    def create_gad_pairs(self, spec: VspGadCtgCreateSpec):
        payload = spec.create_payload()
        if not payload:
            logger.writeInfo(
                "No new GAD pairs to create based on the provided specification."
            )
            return []
        headers = {}
        headers["X-Agent-Type"] = "SEA"
        respone = self.rest_api.pegasus_post_without_job(
            CREATE_GAD_PAIR, payload, headers_input=headers
        )
        self.connection_info.changed = True
        return respone

    @log_entry_exit
    def get_all_gad_pairs(self):
        end_point = GET_ALL_GAD_PAIRS
        headers = {}
        headers["X-Agent-Type"] = "SEA"
        has_next_page = True
        all_pairs = []
        # TODO: Fix it by testing this method with more number of GAD pairs to ensure pagination is working as expected
        while has_next_page:
            response = self.rest_api.get(end_point, headers_input=headers)
            all_pairs.extend(response.get("data", []))
            has_next_page = response.get("hasNext")
            if has_next_page:
                end_point = f"{GET_ALL_GAD_PAIRS}?startId={response.get('count')}"
            else:
                has_next_page = False
        return VspGadVolumePairInfoList().dump_to_object({"data": all_pairs})

    @log_entry_exit
    def get_all_gad_pairs_by_ctg_id(self, ctg_id):
        start_id = "0,0"
        end_point = GET_GAD_PAIRS_BY_CTG_ID.format(start_id, ctg_id)
        headers = {}
        headers["X-Agent-Type"] = "SEA"
        has_next_page = True
        all_pairs = []
        while has_next_page:
            response = self.rest_api.get(end_point, headers_input=headers)
            all_pairs.extend(response.get("data", []))
            has_next_page = response.get("hasNext")
            if has_next_page:
                start_id = f"{response.get('count')},0"
                end_point = GET_GAD_PAIRS_BY_CTG_ID.format(start_id, ctg_id)
            else:
                has_next_page = False
        return VspGadVolumePairInfoList().dump_to_object({"data": all_pairs})

    @log_entry_exit
    def get_gad_pair_by_id(self, pair_id):
        endpoint = GAD_PAIR_BY_ID.format(pair_id)
        headers = {}
        headers["X-Agent-Type"] = "SEA"
        try:
            response = self.rest_api.get(endpoint, headers_input=headers)
            return VspGadVolumePairInfo(**response)
        except Exception as e:
            logger.writeError(f"Error getting GAD pair by ID {pair_id}: {e}")
            return None

    @log_entry_exit
    def get_primary_vsp_one_quorum_disk(self):
        endpoint = QUORUM_DISK_GET
        headers = {}
        headers["X-Agent-Type"] = "SEA"
        response = self.rest_api.get(endpoint, headers_input=headers)
        return VspOneQuorumDiskInfoList().dump_to_object(response)

    @log_entry_exit
    def get_secondary_vsp_one_quorum_disk(self):
        endpoint = QUORUM_DISK_GET
        headers = {}
        headers["X-Agent-Type"] = "SEA"
        response = self.secondary_rest_api.get(endpoint, headers_input=headers)
        return VspOneQuorumDiskInfoList().dump_to_object(response)
