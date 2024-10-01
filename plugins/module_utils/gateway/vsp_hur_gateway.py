import json
from typing import Optional, List, Dict, Any

try:
    from ..common.uaig_constants import Endpoints
    from ..common.hv_constants import CommonConstants
    from .gateway_manager import UAIGConnectionManager
    from ..common.hv_log import Log
    from ..common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from ..common.uaig_utils import UAIGResourceID
    from ..model.vsp_hur_models import VSPHurPairInfoList, VSPHurPairInfo
except ImportError:
    from common.uaig_constants import Endpoints
    from common.hv_constants import CommonConstants
    from .gateway_manager import UAIGConnectionManager
    from common.hv_log import Log
    from common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from common.uaig_utils import UAIGResourceID
    from model.vsp_hur_models import VSPHurPairInfoList, VSPHurPairInfo



class VSPHurUAIGateway:

    def __init__(self, connection_info):
        self.logger = Log()
        self.connection_manager = UAIGConnectionManager(
            connection_info.address, connection_info.username, connection_info.password, connection_info.api_token)        
        self.end_points = Endpoints
        self.connectionInfo = connection_info

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

        for u in ucpsystems:
            # if u.get("name") == CommonConstants.UCP_NAME:
                for s in u.get("storageDevices"):
                    if str(s.get("serialNumber")) == str(storage_serial_number):
                        return s.get("healthState") != CommonConstants.ONBOARDING
        return False

    @log_entry_exit
    def get_all_replication_pairs(self, device_id):

        end_point = self.end_points.GET_HUR_PAIRS.format(device_id)
        headers = self._populate_headers()
        headers['fetchAllHurPairs'] = True
        rp_data = self.connection_manager.get(end_point, headers)
        self.logger.writeDebug("GW:get_all_replication_pairs:data={}", rp_data)

        ## 20240805
        return VSPHurPairInfoList(
            dicts_to_dataclass_list(rp_data["data"], VSPHurPairInfo)
        )

    @log_entry_exit
    def get_replication_pair_by_id(self, device_id, pair_id):

        end_point = self.end_points.GET_HUR_PAIR_BY_ID.format(device_id, pair_id)
        rp_data = self.connection_manager.get(end_point)
        rp_data = rp_data["data"]
        self.logger.writeDebug("GW:get_all_replication_pairs:data={}", rp_data)
        return VSPHurPairInfo(**rp_data)
    
    @log_entry_exit
    def delete_hur_pair(self, id, hur_pair_id):
        end_point = self.end_points.DELETE_HUR_PAIR.format(id, hur_pair_id)
        headers = self._populate_headers()
        data = self.connection_manager.delete(end_point, headers_input=headers)
        return data
    
    @log_entry_exit
    def resync_hur_pair(self, id, hur_pair_id):
        end_point = self.end_points.RESYNC_HUR_PAIR.format(id, hur_pair_id)
        data = self.connection_manager.patch(end_point)
        return hur_pair_id

    @log_entry_exit
    def split_hur_pair(self, id, hur_pair_id):
        end_point = self.end_points.SPLIT_HUR_PAIR.format(id, hur_pair_id)
        body = {}
        data = self.connection_manager.patch(end_point, body)
        return hur_pair_id

    @log_entry_exit
    def swap_split_hur_pair(self, id, hur_pair_id):
        end_point = self.end_points.SWAP_SPLIT_HUR_PAIR.format(id, hur_pair_id)
        data = self.connection_manager.patch(end_point)
        return data

    @log_entry_exit
    def swap_resync_hur_pair(self, id, hur_pair_id):
        end_point = self.end_points.SWAP_RESYNC_HUR_PAIR.format(id, hur_pair_id)
        data = self.connection_manager.patch(end_point)
        return data

    @log_entry_exit
    def get_ucpsystems(self) -> List[Dict[str, Any]]:
        end_point = self.end_points.GET_UCPSYSTEMS
        ucpsystems = self.connection_manager.get(end_point)
        return ucpsystems["data"]
    
    @log_entry_exit
    def get_remote_ucp_serial(self, secondary_serial_number):
        ucpsystems = self.get_ucpsystems()
        for  u in ucpsystems:
            for s in u.get("storageDevices"):
                if s.get("serialNumber") == secondary_serial_number:
                    return s.get("ucpSystems")[0]

        raise ValueError("Remote secondary storage not found.")
    
    @log_entry_exit
    def create_hur(
        self,
        primary_volume_id: int,
        consistency_group_id: int,
        enable_delta_resync: str,
        allocate_new_consistency_group: bool,
        secondary_storage_serial_number: int,
        secondary_pool_id: int,
        secondary_hostgroups: list,
        primary_volume_journal_id: int,
        secondary_volume_journal_id: int,
        ) -> Dict[str, Any]:

        storage_resourceId = UAIGResourceID().storage_resourceId(
            self.storage_serial_number
        )
        end_point = self.end_points.CREATE_HUR_PAIR
        remote_ucp_serial =  self.get_remote_ucp_serial(str(secondary_storage_serial_number))
        self.logger.writeDebug("secondary_storage_serial_number={}", secondary_storage_serial_number)
        self.logger.writeDebug("remote_ucp_serial={}", remote_ucp_serial)
        payload = {
            # "consistencyGroupID": consistency_group_id,
            "primaryVolumeId": primary_volume_id,
            "primaryVolumeJournalId": primary_volume_journal_id,
            "primarySerialNumber": str(self.storage_serial_number),
            "ucpSystem": CommonConstants.UCP_SERIAL,
            "remoteUcpSystem": remote_ucp_serial,
            "secondaryHostGroups": secondary_hostgroups,
            "secondaryVolumeJournalId": secondary_volume_journal_id,
            "secondaryPoolID": secondary_pool_id,
            "enableDeltaResync": enable_delta_resync,
            "newConsistencyGroup": allocate_new_consistency_group,
            "secondarySerialNumber": str(secondary_storage_serial_number),
            }
        
        ##20240821 - hur consistency_group_id
        if consistency_group_id:
            payload['consistencyGroupID'] = consistency_group_id
        
        headers = self._populate_headers()
        self.logger.writeDebug(f"Create Hur payload: {payload}")
        if self.connectionInfo.subscriber_id is None:
            return self.connection_manager.post_ext(end_point, payload, headers_input=headers), None
        else:
            return self.connection_manager.post_ext_hur_v3(end_point, payload, headers_input=headers)

    def _populate_headers(self) -> Dict[str, str]:
        headers = {"partnerId": CommonConstants.PARTNER_ID}
        ##20240814 - hur subscriberId
        # self.logger.writeDebug("168 self.connectionInfo.subscriber_id={}", self.connectionInfo.subscriber_id)
        if self.connectionInfo.subscriber_id is not None:
            headers["subscriberId"] = self.connectionInfo.subscriber_id
        return headers

    @log_entry_exit
    def create_hur_true_copy_test(
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
        end_point = self.end_points.CREATE_HUR_PAIR
        end_point = self.end_points.CREATE_TRUE_COPY_PAIR
        payload = {    
            "consistencyGroupID": consistency_group_id,
            "fenceLevel": fence_level,
            "newConsistencyGroup": allocate_new_consistency_group,
            "primaryLunID": primary_volume_id,
            "primarySerialNumber": str(self.storage_serial_number),
            "secondarySerialNumber": str(secondary_storage_serial_number),
            "secondaryPoolID": secondary_pool_id,
            "secondaryHostGroups": self._get_secondary_hgs_payload(secondary_hostgroups),
            "ucpSystem": CommonConstants.UCP_SERIAL,
            "remoteUcpSystem": "UCP-CI-558018",
        }
        
            
        headers = self._populate_headers()
        self.logger.writeDebug(f"Create Hur payload: {payload}")
        return self.connection_manager.post(end_point, payload, headers_input=headers)

    def _get_secondary_hgs_payload_mock(self, secondary_hgs):
        ret_list = []
        if True:
            item = {}
            item["hostGroupID"] = 40
            item["name"] = "Frank-Test-Group"
            item["port"] = "CL1-A"
            item["resourceGroupID"] = 0
            ret_list.append(item)

        return ret_list
    
    
    def _get_secondary_hgs_payload(self, secondary_hgs):
        ret_list = []
        for hg in secondary_hgs:
            item = {}
            # item["id"] = hg.id
            item["name"] = hg.name
            item["port"] = hg.port
            # item["resourceGroupID"] = hg.resource_group_id or 0
            ret_list.append(item)

        return ret_list    