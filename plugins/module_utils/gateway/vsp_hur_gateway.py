import time
from typing import List, Dict, Any

try:
    from ..common.uaig_constants import Endpoints
    from ..common.hv_constants import CommonConstants
    from .gateway_manager import UAIGConnectionManager
    from .vsp_replication_pairs_gateway import VSPReplicationPairsDirectGateway
    from ..common.hv_log import Log
    from ..common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from ..common.uaig_utils import UAIGResourceID
    from .vsp_volume import VSPVolumeUAIGateway
    from ..message.vsp_hur_msgs import VSPHurValidateMsg
    from ..model.vsp_hur_models import (
        VSPHurPairInfoList,
        VSPHurPairInfo,
        DirectHurPairInfoList,
        DirectHurPairInfo,
    )
except ImportError:
    from common.uaig_constants import Endpoints
    from common.hv_constants import CommonConstants
    from .gateway_manager import UAIGConnectionManager
    from .vsp_replication_pairs_gateway import VSPReplicationPairsDirectGateway
    from common.hv_log import Log
    from common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from common.uaig_utils import UAIGResourceID
    from .vsp_volume import VSPVolumeUAIGateway
    from message.vsp_hur_msgs import VSPHurValidateMsg
    from model.vsp_hur_models import (
        VSPHurPairInfoList,
        VSPHurPairInfo,
        DirectHurPairInfoList,
        DirectHurPairInfo,
    )

CREATE_REMOTE_COPY_PAIR_DIRECT = "v1/objects/remote-mirror-copypairs"
CREATE_HUR_PAIR_DIRECT = "v1/objects/remote-mirror-copypairs"
GET_REMOTE_STORAGES_DIRECT = "v1/objects/remote-storages"
GET_HUR_PAIRS_DIRECT = "v1/objects/remote-copypairs?replicationType=UR"

logger = Log()


class VSPHurDirectGateway(VSPReplicationPairsDirectGateway):
    # def __init__(self, connection_info):

    #     self.connection_manager = VSPConnectionManager(
    #         connection_info.address, connection_info.username, connection_info.password)
    #     self.end_points = Endpoints
    #     self.connection_info = connection_info

    # @log_entry_exit
    # def set_storage_serial_number(self, serial: str):
    #     self.storage_serial_number = serial

    # @log_entry_exit
    # def get_storage_device_id(self, serial_number):
    #     end_point = GET_REMOTE_STORAGES_DIRECT
    #     storage_devices = self.connection_manager.get(end_point)
    #     logger.writeDebug("GW:get_local_storage_device_id:storage_devices={}", storage_devices)
    #     for s in storage_devices["data"]:
    #         if s.get("serialNumber") == serial_number:
    #             return s.get("storageDeviceId")
    #     raise ValueError("Storage device not found.")

    @log_entry_exit
    def get_all_replication_pairs(self, serial=None):
        end_point = GET_HUR_PAIRS_DIRECT
        tc_data = self.connection_manager.get(end_point)
        logger.writeDebug("GW-Direct:get_all_hur_pairs:data={}", tc_data)

        return DirectHurPairInfoList(
            dicts_to_dataclass_list(tc_data["data"], DirectHurPairInfo)
        )

    @log_entry_exit
    def get_secondary_serial(self, spec):
        # logger.writeDebug("sng20241115 65 secondary_connection_info ={}", spec.secondary_connection_info)
        secondary_storage_info = self.get_secondary_storage_info(
            spec.secondary_connection_info
        )
        return secondary_storage_info.get("serialNumber")

    @log_entry_exit
    def create_hur_pair(self, spec) -> Dict[str, Any]:

        # secondary_storage_serial_number = self.get_secondary_serial(spec)
        secondary_storage_info = self.get_secondary_storage_info(
            spec.secondary_connection_info
        )
        remote_storage_deviceId = secondary_storage_info.get("storageDeviceId")

        payload = {
            "copyGroupName": spec.copy_group_name,
            "copyPairName": spec.copy_pair_name,
            "replicationType": "UR",
            "remoteStorageDeviceId": remote_storage_deviceId,
            "pvolLdevId": spec.primary_volume_id,
            "isNewGroupCreation": spec.is_new_group_creation,
            "svolLdevId": int(spec.secondary_volume_id),
            "fenceLevel": spec.fence_level if spec.fence_level else "ASYNC",
        }
        if spec.is_new_group_creation is True:
            payload["muNumber"] = (
                spec.mirror_unit_id if spec.mirror_unit_id is not None else 1
            )
            payload["pvolJournalId"] = spec.primary_volume_journal_id
            payload["svolJournalId"] = spec.secondary_volume_journal_id

        if spec.local_device_group_name:
            payload["localDeviceGroupName"] = spec.local_device_group_name
        if spec.remote_device_group_name:
            payload["remoteDeviceGroupName"] = spec.remote_device_group_name
        if spec.consistency_group_id:
            payload["consistencyGroupId"] = spec.consistency_group_id
        if spec.do_initial_copy is not None:
            payload["doInitialCopy"] = spec.do_initial_copy
        if spec.is_data_reduction_force_copy is not None:
            payload["isDataReductionForceCopy"] = spec.is_data_reduction_force_copy
        else:
            payload["isDataReductionForceCopy"] = True
        if spec.do_delta_resync_suspend is not None:
            payload["doDeltaResyncSuspend"] = spec.do_delta_resync_suspend

        # storage_deviceId = self.get_storage_device_id(str(self.storage_serial_number))
        # logger.writeDebug("GW-Direct:create_hur_copy:storage_deviceId={}", storage_deviceId)
        headers = self.get_remote_token(spec.remote_connection_info)
        headers["Remote-Authorization"] = headers.pop("Authorization")
        headers["Job-Mode-Wait-Configuration-Change"] = "NoWait"
        logger.writeDebug("GW-Direct:create_hur_copy:remote_header={}", headers)
        end_point = CREATE_REMOTE_COPY_PAIR_DIRECT  # .format(storage_deviceId)
        logger.writeDebug("GW-Direct:create_hur_copy:end_point={}", end_point)
        start_time = time.time()
        response = self.connection_manager.post(
            end_point, payload, headers_input=headers
        )
        end_time = time.time()
        logger.writeDebug("PF_REST:create_hur_copy:time={:.2f}", end_time - start_time)
        return response

    @log_entry_exit
    def split_hur_pair(self, spec):
        return super().split_replication_pair(spec, "UR")

    @log_entry_exit
    def swap_split_hur_pair(self, spec):
        return super().swap_split_replication_pair(spec, "UR")

    @log_entry_exit
    def resync_hur_pair(self, spec):
        return super().resync_replication_pair(spec, "UR")

    @log_entry_exit
    def swap_resync_hur_pair(self, spec):
        return super().swap_resync_replication_pair(spec, "UR")

    @log_entry_exit
    def delete_hur_pair_by_pair_id(self, spec):
        return super().delete_replication_pair(spec)

    @log_entry_exit
    def get_hur_pair(self, spec):
        return super().get_replication_pair(spec)

    @log_entry_exit
    def resize_hur_pair(self, pair, spec):
        return super().resize_replication_pair(pair, spec)


class VSPHurUAIGateway:

    def __init__(self, connection_info):
        self.logger = Log()
        self.connection_manager = UAIGConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )
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
    def get_all_replication_pairs(self, serial):
        device_id = UAIGResourceID().storage_resourceId(serial)
        end_point = self.end_points.GET_HUR_PAIRS.format(device_id)
        headers = self._populate_headers()
        headers["fetchAllHurPairs"] = True
        rp_data = self.connection_manager.get(end_point, headers)
        self.logger.writeDebug("GW:get_all_replication_pairs:data={}", rp_data)

        #  20240805
        return VSPHurPairInfoList(
            dicts_to_dataclass_list(rp_data["data"], VSPHurPairInfo)
        )

    @log_entry_exit
    def get_replication_pair_by_id(self, device_id, pair_id):

        end_point = self.end_points.GET_HUR_PAIR_BY_ID.format(device_id, pair_id)
        rp_data = self.connection_manager.get(end_point)
        rp_data = rp_data["data"]
        self.logger.writeDebug("GW:get_replication_pair_by_id:data={}", rp_data)
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
        self.connection_manager.patch(end_point)
        return hur_pair_id

    @log_entry_exit
    def split_hur_pair(self, id, hur_pair_id, is_svol_readwriteable=None):
        end_point = self.end_points.SPLIT_HUR_PAIR.format(id, hur_pair_id)
        payload = {}
        if is_svol_readwriteable is not None:
            payload["enableReadWrite"] = is_svol_readwriteable
        data = self.connection_manager.patch(end_point, payload)
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
    def get_remote_ucp_serial(self, secondary_serial_number):
        ucpsystems = self.get_ucpsystems()
        for u in ucpsystems:
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
        mirror_unit_id: int,
        begin_secondary_volume_id: int,
        end_secondary_volume_id: int,
    ):

        storage_resourceId = UAIGResourceID().storage_resourceId(
            self.storage_serial_number
        )
        end_point = self.end_points.CREATE_HUR_PAIR
        remote_ucp_serial = self.get_remote_ucp_serial(
            str(secondary_storage_serial_number)
        )
        self.logger.writeDebug(
            "secondary_storage_serial_number={}", secondary_storage_serial_number
        )
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

        # 20240821 - hur consistency_group_id
        if consistency_group_id:
            payload["consistencyGroupID"] = consistency_group_id

        if mirror_unit_id is not None:
            payload["mirrorUnitId"] = mirror_unit_id

        if begin_secondary_volume_id is not None:
            payload["beginLdevId"] = begin_secondary_volume_id
        if end_secondary_volume_id is not None:
            payload["endLdevId"] = end_secondary_volume_id

        headers = self._populate_headers()
        self.logger.writeDebug(f"Create Hur payload: {payload}")
        if self.connectionInfo.subscriber_id is None:
            return (
                self.connection_manager.post_ext(
                    end_point, payload, headers_input=headers
                ),
                None,
            )
        else:
            return self.connection_manager.post_ext_hur_v3(
                end_point, payload, headers_input=headers
            )

    def _populate_headers(self) -> Dict[str, str]:
        headers = {"partnerId": CommonConstants.PARTNER_ID}
        # 20240814 - hur subscriberId
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
            "secondaryHostGroups": self._get_secondary_hgs_payload(
                secondary_hostgroups
            ),
            "ucpSystem": CommonConstants.UCP_SERIAL,
            "remoteUcpSystem": "UCP-CI-558018",
        }

        headers = self._populate_headers()
        self.logger.writeDebug(f"Create Hur payload: {payload}")
        return self.connection_manager.post(end_point, payload, headers_input=headers)

    def _get_secondary_hgs_payload_mock(self, secondary_hgs):
        ret_list = []
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

    @log_entry_exit
    def expand_volume(self, connection, storage_resourceId, ldev_resourceId, spec):
        vol_gateway = VSPVolumeUAIGateway(connection)
        volume_data = vol_gateway.get_volume_by_id_v2(
            storage_resourceId, ldev_resourceId
        )
        response = vol_gateway.update_volume(
            storage_resourceId,
            ldev_resourceId,
            spec.new_volume_size,
            volume_data.deduplicationCompressionMode,
            volume_data.name,
        )
        return response

    @log_entry_exit
    def resize_hur_pair(self, pair, spec):
        response = ""
        split_required = True
        if pair.status == "PSUS":
            split_required = False
        pvol_id = pair.primaryVolumeId
        svol_id = pair.secondaryVolumeId

        svol_storage_resourceId = UAIGResourceID().storage_resourceId(
            spec.secondary_storage_serial_number
        )
        ldev_resource_id = UAIGResourceID().ldev_resourceId(
            self.storage_serial_number, pvol_id
        )
        svol_ldev_resource_id = UAIGResourceID().ldev_resourceId(
            spec.secondary_storage_serial_number, svol_id
        )
        storage_resourceId = UAIGResourceID().storage_resourceId(
            self.storage_serial_number
        )
        # secondary_storage_resourceId = UAIGResourceID().storage_resourceId(
        #     spec.secondary_storage_serial_number
        # )
        if split_required:
            response = self.split_hur_pair(storage_resourceId, pair.resourceId)
            logger.writeDebug("GW:resize_replication_pair:split:response={}", response)
        try:
            self.expand_volume(
                self.connectionInfo,
                svol_storage_resourceId,
                svol_ldev_resource_id,
                spec,
            )
            logger.writeDebug("GW:resize_replication_pair:svol_id={}", svol_id)
        except Exception as ex:
            logger.writeDebug(
                "GW:resize_replication_pair:exception in expand volume:ex={}", ex
            )
            if "AFA8" in str(ex):
                raise ValueError(VSPHurValidateMsg.EXPAND_VOLUME_FAILED.value)
            else:
                raise ValueError(
                    VSPHurValidateMsg.EXPAND_SVOL_FAILED.value.format(svol_id) + str(ex)
                )

        try:
            self.expand_volume(
                self.connectionInfo, storage_resourceId, ldev_resource_id, spec
            )
            logger.writeDebug("GW:resize_replication_pair:pvol_id={}", pvol_id)
        except Exception as ex:
            logger.writeDebug(
                "GW:resize_replication_pair:exception in expand volume:ex={}", ex
            )
            if "AFA8" in str(ex):
                raise ValueError(VSPHurValidateMsg.EXPAND_VOLUME_FAILED.value)
            else:
                raise ValueError(
                    VSPHurValidateMsg.EXPAND_PVOL_FAILED.value.format(pvol_id) + str(ex)
                )

        if split_required:
            response = self.resync_hur_pair(storage_resourceId, pair.resourceId)
            logger.writeDebug("GW:resize_replication_pair:resync:response={}", response)
        return response
