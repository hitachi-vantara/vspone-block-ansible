import json
from typing import Optional, List, Dict, Any

try:
    from ..common.uaig_constants import Endpoints
    from ..common.hv_constants import CommonConstants
    from .gateway_manager import UAIGConnectionManager
    from ..common.hv_log import Log
    from ..common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from ..common.uaig_utils import UAIGResourceID
    from ..model.vsp_true_copy_models import VSPReplicationPairInfo, VSPReplicationPairInfoList, VSPTrueCopyPairInfo, VSPTrueCopyPairInfoList
except ImportError:
    from common.uaig_constants import Endpoints
    from common.hv_constants import CommonConstants
    from .gateway_manager import UAIGConnectionManager
    from common.hv_log import Log
    from common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from common.uaig_utils import UAIGResourceID
    from model.vsp_true_copy_models import VSPReplicationPairInfo, VSPReplicationPairInfoList, VSPTrueCopyPairInfo, VSPTrueCopyPairInfoList


logger = Log()
class VSPTrueCopyUAIGateway:

    def __init__(self, connection_info):

        self.connection_manager = UAIGConnectionManager(
            connection_info.address, connection_info.username, connection_info.password, connection_info.api_token)        
        self.end_points = Endpoints
        self.connection_info = connection_info

    @log_entry_exit
    def set_storage_serial_number(self, serial: str):
        self.storage_serial_number = serial

    @log_entry_exit
    def get_ucpsystems(self) -> List[Dict[str, Any]]:
        end_point = self.end_points.GET_UCPSYSTEMS
        ucpsystems = self.connection_manager.get(end_point)
        return ucpsystems["data"]

    @log_entry_exit
    def check_storage_in_ucpsystem(self) -> bool:
        storage_serial_number = self.storage_serial_number
        ucpsystems = self.get_ucpsystems()
        logger.writeDebug("GW:check_storage_in_ucpsystem:ucpsystems={}", ucpsystems)
        for u in ucpsystems:
            # if u.get("name") == CommonConstants.UCP_NAME:
                for s in u.get("storageDevices"):
                    if s.get("serialNumber") == storage_serial_number:
                        return s.get("healthState") != CommonConstants.ONBOARDING
        return False

    @log_entry_exit
    def get_remote_ucp_serial(self, secondary_serial_number):
        logger.writeDebug("GW:get_remote_ucp_serial: type of secondary_serial_number= {}", type(secondary_serial_number))
        ucpsystems = self.get_ucpsystems()
        logger.writeDebug("GW:get_remote_ucp_serial:ucpsystems={}", ucpsystems)
        for  u in ucpsystems:
            storage_devices = u.get("storageDevices")
            logger.writeDebug("GW:get_remote_ucp_serial:storage_devices={}", storage_devices)
            for s in u.get("storageDevices"):
                logger.writeDebug("GW:get_remote_ucp_serial:s={}", s)
                if s.get("serialNumber") == str(secondary_serial_number):
                    return s.get("ucpSystems")[0]

        raise ValueError("Remote secondary storage not found.")
    
    @log_entry_exit
    def get_all_replication_pairs(self, device_id):

        end_point = self.end_points.GET_REPLICATION_PAIRS.format(device_id)
        rp_data = self.connection_manager.get(end_point)
        logger.writeDebug("GW:get_all_replication_pairs:data={}", rp_data)

        return VSPReplicationPairInfoList(
            dicts_to_dataclass_list(rp_data["data"], VSPReplicationPairInfo)
        )
    @log_entry_exit
    def get_all_true_copy_pairs(self, device_id):

        end_point = self.end_points.GET_TRUE_COPY_PAIRS.format(device_id)
        headers = self._populate_headers()  # need this code when use v3
        tc_data = self.connection_manager.get(end_point, headers_input=headers)
        logger.writeDebug("GW:get_all_true_copy_pairs:data={}", tc_data)

        return VSPTrueCopyPairInfoList(
            dicts_to_dataclass_list(tc_data["data"], VSPTrueCopyPairInfo)
        )

    @log_entry_exit
    def get_replication_pair_by_id(self, device_id, pair_id):

        end_point = self.end_points.GET_REPLICATION_PAIR_BY_ID.format(device_id, pair_id)
        data = self.connection_manager.get(end_point)
        rp_data = data["data"]
        logger.writeDebug("GW:get_replication_pair_by_id:data={}", data)
        return VSPReplicationPairInfo(**rp_data)

    @log_entry_exit
    def delete_true_copy_pair(self, id, true_copy_pair_id):
      
        headers = self._populate_headers()
        end_point = self.end_points.DELETE_TRUE_COPY_PAIR.format(id, true_copy_pair_id)
        data = self.connection_manager.delete(end_point, headers_input=headers)
        return data

    @log_entry_exit
    def resync_true_copy_pair(self, id, true_copy_pair_id):
        end_point = self.end_points.RESYNC_TRUE_COPY_PAIR.format(id, true_copy_pair_id)
        data = self.connection_manager.patch(end_point)
        return data

    @log_entry_exit
    def split_true_copy_pair(self, id, true_copy_pair_id):
        end_point = self.end_points.SPLIT_TRUE_COPY_PAIR.format(id, true_copy_pair_id)
        data = self.connection_manager.patch(end_point)
        return data

    @log_entry_exit
    def swap_split_true_copy_pair(self, id, true_copy_pair_id):
        end_point = self.end_points.SWAP_SPLIT_TRUE_COPY_PAIR.format(id, true_copy_pair_id)
        data = self.connection_manager.patch(end_point)
        return data

    @log_entry_exit
    def swap_resync_true_copy_pair(self, id, true_copy_pair_id):
        end_point = self.end_points.SWAP_RESYNC_TRUE_COPY_PAIR.format(id, true_copy_pair_id)
        data = self.connection_manager.patch(end_point)
        return data

    @log_entry_exit
    def create_true_copy(
        self,
        primary_volume_id: int,
        consistency_group_id: int,
        fence_level: str,
        allocate_new_consistency_group: bool,
        secondary_storage_serial_number: int,
        secondary_pool_id: int,
        secondary_hostgroups: list,
        ) -> Dict[str, Any]:

        storage_resourceId = UAIGResourceID().storage_resourceId(
            self.storage_serial_number
        )
        end_point = self.end_points.CREATE_TRUE_COPY_PAIR
        remote_ucp_serial =  self.get_remote_ucp_serial(str(secondary_storage_serial_number))
        logger.writeDebug("GW:create_true_copy:remote_ucp_serial={}", remote_ucp_serial)

        payload = {    
            "consistencyGroupID": consistency_group_id,
            "fenceLevel": fence_level,
            "newConsistencyGroup": allocate_new_consistency_group,
            "primaryLunID": primary_volume_id,
            "primarySerialNumber": str(self.storage_serial_number),
            "secondarySerialNumber": str(secondary_storage_serial_number),
            "secondaryPoolID": secondary_pool_id,
            "secondaryHostGroups": secondary_hostgroups,
            "ucpSystem": CommonConstants.UCP_SERIAL,
            "remoteUcpSystem": remote_ucp_serial,
        }

        headers = self._populate_headers()  # need this code when use v3
        logger.writeDebug(f"Create TrueCopy payload: {payload}")
        return self.connection_manager.post_subtask_ext(end_point, payload, headers_input=headers)

    def _populate_headers(self) -> Dict[str, str]:
        headers = {"partnerId": CommonConstants.PARTNER_ID}
        ##20240814 - hur subscriberId
        # logger.writeDebug("168 self.connection_info.subscriber_id={}", self.connection_info.subscriber_id)
        if self.connection_info.subscriber_id is not None:
            headers["subscriberId"] = self.connection_info.subscriber_id
        return headers