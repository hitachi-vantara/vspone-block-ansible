from typing import List, Dict, Any

try:
    from .gateway_manager import VSPConnectionManager, UAIGConnectionManager
    from ..common.hv_constants import CommonConstants, HEADER_NAME_CONSTANT
    from ..common.uaig_constants import Endpoints as UAIGEndpoints
    from ..model.vsp_gad_pairs_models import (
        VspGadPairSpec,
        VspGadPairsInfo,
        DirectGadPairInfoList,
        DirectGadPairInfo,
    )
    from ..common.uaig_constants import GADPairConst
    from ..common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from ..common.hv_log import Log
    from .vsp_replication_pairs_gateway import VSPReplicationPairsDirectGateway
    from .vsp_volume import VSPVolumeUAIGateway
    from ..message.vsp_gad_pair_msgs import GADPairValidateMSG
    from ..common.uaig_utils import UAIGResourceID

except ImportError:
    from .gateway_manager import VSPConnectionManager, UAIGConnectionManager
    from common.hv_constants import CommonConstants, HEADER_NAME_CONSTANT
    from common.uaig_constants import Endpoints as UAIGEndpoints
    from model.vsp_gad_pairs_models import (
        VspGadPairSpec,
        VspGadPairsInfo,
        DirectGadPairInfoList,
        DirectGadPairInfo,
    )
    from common.uaig_constants import GADPairConst
    from common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from common.hv_log import Log
    from .vsp_replication_pairs_gateway import VSPReplicationPairsDirectGateway
    from .vsp_volume import VSPVolumeUAIGateway
    from message.vsp_gad_pair_msgs import GADPairValidateMSG
    from common.uaig_utils import UAIGResourceID

DELETE_GAD_PAIR_DIRECT = "v1/objects/remote-mirror-copypairs/{}"
CREATE_GAD_PAIR_DIRECT = "v1/objects/remote-mirror-copypairs"
SPLIT_GAD_PAIR_DIRECT = "v1/objects/remote-mirror-copypairs/{}/actions/split/invoke"
RESYNC_GAD_PAIR_DIRECT = "v1/objects/remote-mirror-copypairs/{}/actions/resync/invoke"
GET_REMOTE_STORAGES_DIRECT = "v1/objects/remote-storages"
GET_GAD_PAIRS_DIRECT = "v1/objects/remote-copypairs?replicationType=GAD"

logger = Log()


class VSPGadPairDirectGateway(VSPReplicationPairsDirectGateway):
    # def __init__(self, connection_info):

    #     self.connection_manager = VSPConnectionManager(
    #         connection_info.address, connection_info.username, connection_info.password)
    #     # self.end_points = Endpoints
    #     self.connection_info = connection_info
    #     self.rest_api = VSPConnectionManager(
    #         connection_info.address,
    #         connection_info.username,
    #         connection_info.password
    #     )

    #     # sng20241115 VSPReplicationPairsDirectGateway needs this data member
    #     self.remote_connection_manager = None
    #     self.copy_group_gateway = None

    @log_entry_exit
    def swap_split_gad_pair(self, spec, mode=None):
        return super().swap_split_replication_pair(spec, "GAD", mode)

    @log_entry_exit
    def swap_resync_gad_pair(self, spec):
        return super().swap_resync_replication_pair(spec, "GAD")

    @log_entry_exit
    def get_secondary_serial(self, spec):
        # logger.writeDebug("sng20241115 secondary_connection_info ={}", spec.secondary_connection_info)
        secondary_storage_info = self.get_secondary_storage_info(
            spec.secondary_connection_info
        )
        return secondary_storage_info.get("serialNumber")

    # @log_entry_exit
    # def set_storage_serial_number(self, serial: str):
    #     self.storage_serial_number = serial

    # @log_entry_exit
    # def get_storage_device_id(self, serial_number):
    #     end_point = GET_REMOTE_STORAGES_DIRECT
    #     storage_devices = self.connection_manager.get(end_point)
    #     logger.writeDebug("GW:get_local_storage_device_id:storage_devices={}", storage_devices)
    #     for s in storage_devices["data"]:
    #         if str(s.get("serialNumber")) == str(serial_number):
    #             return s.get("storageDeviceId")
    #     raise ValueError("Storage device not found.")

    @log_entry_exit
    def get_all_gad_pairs(self, serial=None):
        # sng1104 - have to use the CG version
        logger.writeDebug("SHOULD USE THE COPY GROUP GET!!")
        end_point = GET_GAD_PAIRS_DIRECT
        tc_data = self.connection_manager.get(end_point)
        logger.writeDebug("GW-Direct:get_all_gad_pairs:data={}", tc_data)

        return DirectGadPairInfoList(
            dicts_to_dataclass_list(tc_data["data"], DirectGadPairInfo)
        )

    @log_entry_exit
    def get_remote_token(self, remote_connection_info):
        remote_connection_manager = VSPConnectionManager(
            remote_connection_info.address,
            remote_connection_info.username,
            remote_connection_info.password,
            remote_connection_info.api_token,
        )
        return remote_connection_manager.getAuthToken()

    # sng20241105 sng1104 create_gad_pair
    @log_entry_exit
    def create_gad_pair(self, spec) -> Dict[str, Any]:

        # secondary_storage_serial_number = spec.secondary_storage_serial_number
        # remote_storage_deviceId = self.get_storage_device_id(
        #     str(secondary_storage_serial_number)
        # )
        secondary_storage_info = self.get_secondary_storage_info(
            spec.secondary_connection_info
        )
        remote_storage_deviceId = secondary_storage_info.get("storageDeviceId")
        logger.writeDebug(
            f"115 spec.is_new_group_creation : {spec.is_new_group_creation}"
        )
        logger.writeDebug(f"115 spec.mu_number : {spec.mu_number}")

        payload = {
            "copyGroupName": spec.copy_group_name,
            "copyPairName": spec.copy_pair_name,
            "replicationType": "GAD",
            "remoteStorageDeviceId": remote_storage_deviceId,
            "pvolLdevId": spec.primary_volume_id,
            "svolLdevId": spec.secondary_volume_id,
            "isNewGroupCreation": (
                spec.is_new_group_creation
                if spec.is_new_group_creation is not None
                else True
            ),
            "fenceLevel": spec.fence_level if spec.fence_level else "NEVER",
            "copyPace": 3,
            "doInitialCopy": True,
            "isDataReductionForceCopy": True,
        }

        isConsistencyGroup = None
        if spec.is_consistency_group is not None:
            payload["isConsistencyGroup"] = spec.is_consistency_group
            isConsistencyGroup = spec.is_consistency_group
        if spec.allocate_new_consistency_group is not None:
            payload["isConsistencyGroup"] = spec.allocate_new_consistency_group
            isConsistencyGroup = spec.allocate_new_consistency_group

        if isConsistencyGroup and spec.consistency_group_id:
            payload["consistencyGroupId"] = spec.consistency_group_id

        is_new_group_creation = None
        if spec.is_new_group_creation is not None:
            is_new_group_creation = spec.is_new_group_creation

        # adding GAD to existing copy group,
        # payload cannot include the mu number
        #
        # for new copy group, it is either 0 or user input
        mu_number = 0
        if spec.mu_number:
            mu_number = spec.mu_number
        if is_new_group_creation:
            payload["muNumber"] = mu_number

        if spec.quorum_disk_id is not None:
            payload["quorumDiskId"] = spec.quorum_disk_id
        if spec.path_group_id is not None:
            payload["pathGroupId"] = spec.path_group_id
        if spec.local_device_group_name:
            payload["localDeviceGroupName"] = spec.local_device_group_name
        if spec.remote_device_group_name:
            payload["remoteDeviceGroupName"] = spec.remote_device_group_name
        if spec.is_consistency_group is not None:
            payload["isConsistencyGroup"] = spec.is_consistency_group
        if spec.is_consistency_group and spec.consistency_group_id:
            payload["consistencyGroupId"] = spec.consistency_group_id
        if spec.copy_pace:
            payload["copyPace"] = self.get_copy_pace_value(spec.copy_pace)
        if spec.do_initial_copy is not None:
            payload["doInitialCopy"] = spec.do_initial_copy
        if spec.is_data_reduction_force_copy is not None:
            payload["isDataReductionForceCopy"] = spec.is_data_reduction_force_copy

        storage_deviceId = self.get_storage_device_id(str(self.storage_serial_number))
        logger.writeDebug("GW-Direct:create_gad:storage_deviceId={}", storage_deviceId)
        headers = self.get_remote_token(spec.secondary_storage_connection_info)
        headers["Remote-Authorization"] = headers.pop("Authorization")
        # headers["Remote-Authorization"] = "Session cf68b8ce47fd47e5ad9195466c915d7e"
        # end_point = CREATE_GAD_PAIR_DIRECT.format(storage_deviceId)
        end_point = CREATE_GAD_PAIR_DIRECT
        logger.writeDebug("GW-Direct:create_gad:end_point={}", end_point)
        return self.connection_manager.post(end_point, payload, headers_input=headers)

    def get_copy_pace_value(self, copy_pace=None):
        copy_pace_value = 1
        if copy_pace:
            copy_pace = copy_pace.strip().upper()
        if copy_pace == "SLOW":
            copy_pace_value = 1
        elif copy_pace == "FAST":
            copy_pace_value = 10
        else:
            copy_pace_value = 3
        return copy_pace_value

    @log_entry_exit
    def split_gad_pair(self, spec):
        return super().split_replication_pair(spec, "GAD")

    @log_entry_exit
    def resync_gad_pair(self, spec):
        return super().resync_replication_pair(spec, "GAD")

    @log_entry_exit
    def resize_gad_pair(self, pair, spec):
        return super().resize_replication_pair(pair, spec)

    @log_entry_exit
    def split_gad_pair_old(self, spec, object_id):
        parameters = {
            "replicationType": "GAD",
        }
        payload = {"parameters": parameters}
        headers = self.get_remote_token(spec.secondary_storage_connection_info)
        headers["Remote-Authorization"] = headers.pop("Authorization")
        headers["Job-Mode-Wait-Configuration-Change"] = "NoWait"
        end_point = SPLIT_GAD_PAIR_DIRECT.format(object_id)
        return self.connection_manager.update(end_point, payload, headers_input=headers)

    @log_entry_exit
    def resync_gad_pair_old(self, spec, object_id):
        parameters = {
            "replicationType": "GAD",
        }
        payload = {"parameters": parameters}
        headers = self.get_remote_token(spec.secondary_storage_connection_info)
        headers["Remote-Authorization"] = headers.pop("Authorization")
        headers["Job-Mode-Wait-Configuration-Change"] = "NoWait"
        end_point = RESYNC_GAD_PAIR_DIRECT.format(object_id)
        return self.connection_manager.update(end_point, payload, headers_input=headers)

    @log_entry_exit
    def resync_gad_pair_by_spec(self, spec):
        secondary_storage_serial_number = spec.secondary_storage_serial_number
        remote_storage_deviceId = self.get_storage_device_id(
            str(secondary_storage_serial_number)
        )

        self.get_storage_device_id(str(self.storage_serial_number))
        # remoteStorageDeviceId,copyGroupName,localDeviceGroupName,remoteDeviceGroupName, copyPairName
        parameters = {
            "replicationType": "GAD",
        }
        local_device_group_name = (
            spec.local_device_group_name
            if spec.local_device_group_name
            else spec.copy_group_name + "P_"
        )
        remote_device_group_name = (
            spec.remote_device_group_name
            if spec.remote_device_group_name
            else spec.copy_group_name + "S_"
        )
        object_id = f"{remote_storage_deviceId},{spec.copy_group_name},{local_device_group_name},{remote_device_group_name},{spec.copy_pair_name}"
        payload = {"parameters": parameters}
        headers = self.get_remote_token(spec.secondary_storage_connection_info)
        headers["Remote-Authorization"] = headers.pop("Authorization")
        headers["Job-Mode-Wait-Configuration-Change"] = "NoWait"
        end_point = RESYNC_GAD_PAIR_DIRECT.format(object_id)
        return self.connection_manager.update(end_point, payload, headers_input=headers)

    @log_entry_exit
    def delete_gad_pair(self, spec, object_id):
        logger.writeDebug("GW:delete_gad_pair:object_id={}", object_id)
        end_point = DELETE_GAD_PAIR_DIRECT.format(object_id)
        headers = self.get_remote_token(spec.secondary_storage_connection_info)
        headers["Remote-Authorization"] = headers.pop("Authorization")
        # headers["Job-Mode-Wait-Configuration-Change"] = "NoWait"
        return self.connection_manager.delete_with_headers(end_point, headers=headers)


class GADPairUAIGateway:

    def __init__(self, connection_info):
        self.connectionManager = UAIGConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )

        #  Set the resource id
        self.serial_number = None
        self.resource_id = None
        self.connectionInfo = connection_info

        #  Set the headers
        self.headers = {HEADER_NAME_CONSTANT.PARTNER_ID: CommonConstants.PARTNER_ID}
        if connection_info.subscriber_id is not None:
            self.headers[HEADER_NAME_CONSTANT.SUBSCRIBER_ID] = (
                connection_info.subscriber_id
            )
        self.UCP_SYSTEM = CommonConstants.UCP_SERIAL
        self.new_pair = False

    @log_entry_exit
    def set_storage_serial_number(self, serial: str):
        self.storage_serial_number = serial

    @log_entry_exit
    def swap_split_gad_pair(self, true_copy_pair_id):
        end_point = UAIGEndpoints.SWAP_SPLIT_GAD_PAIR.format(
            self.resource_id, true_copy_pair_id
        )
        data = self.connectionManager.patch(end_point, headers_input=self.headers)
        return data

    @log_entry_exit
    def swap_resync_gad_pair(self, true_copy_pair_id):
        end_point = UAIGEndpoints.SWAP_RESYNC_GAD_PAIR.format(
            self.resource_id, true_copy_pair_id
        )
        data = self.connectionManager.patch(end_point, headers_input=self.headers)
        return data

    @log_entry_exit
    def get_all_gad_pairs_v2(self):
        #  Get the storage pools
        endPoint = UAIGEndpoints.GET_REPLICATION_PAIRS.format(self.resource_id)
        gadPairsDict = self.connectionManager.get(endPoint)
        return VspGadPairsInfo().dump_to_object(gadPairsDict)

    @log_entry_exit
    def get_all_gad_pairs(self, spec):
        # Get the storage pools
        if self.new_pair:
            # call refresh api
            endPoint = UAIGEndpoints.GET_REPLICATION_PAIRS_REFRESH.format(
                self.resource_id
            )
            self.connectionManager.get(endPoint, headers_input=self.headers)
            self.new_pair = False
        endPoint = UAIGEndpoints.GET_GAD_PAIRS_V3.format(self.resource_id)
        gadPairsDict = self.connectionManager.get(endPoint, headers_input=self.headers)
        return VspGadPairsInfo().dump_to_object(gadPairsDict)

    @log_entry_exit
    def delete_gad_pair(self, spec, gad_pair_id):
        # sng20250106 - need to implement deleteLun in the playbook
        #  delete_gad_pair
        endPoint = (
            UAIGEndpoints.GAD_SINGLE_PAIR_V3.format(self.resource_id, gad_pair_id)
            + "?isDelete=true&deleteLun=false"
        )
        return self.connectionManager.delete(endPoint, headers_input=self.headers)

    @log_entry_exit
    def split_gad_pair(self, gad_pair_id):
        #  split_gad_pair
        endPoint = UAIGEndpoints.SPLIT_GAD_PAIR_V3.format(self.resource_id, gad_pair_id)
        return self.connectionManager.patch(endPoint, headers_input=self.headers)

    @log_entry_exit
    def resync_gad_pair(self, gad_pair_id):
        #  resync_gad_pair
        endPoint = UAIGEndpoints.RESYNC_GAD_PAIR_V3.format(
            self.resource_id, gad_pair_id
        )
        return self.connectionManager.patch(endPoint, headers_input=self.headers)

    @log_entry_exit
    def create_gad_pair(self, spec: VspGadPairSpec):
        payload = {
            GADPairConst.PRIMARY_SERIAL_NUMBER: spec.primary_storage_serial_number,
            GADPairConst.PRIMARY_LUN_ID: spec.primary_volume_id,
            GADPairConst.SECONDARY_SERIAL_NUMBER: spec.secondary_storage_serial_number,
            GADPairConst.SECONDARY_POOL_ID: spec.secondary_pool_id,
            GADPairConst.UCP_SYSTEM: self.UCP_SYSTEM,
        }
        if spec.remote_ucp_system:
            payload[GADPairConst.REMOTE_UCP_SYSTEM] = spec.remote_ucp_system

        if spec.consistency_group_id:
            payload[GADPairConst.CONSISTENCY_GROUP_ID] = spec.consistency_group_id
        else:
            payload[GADPairConst.CONSISTENCY_GROUP_ID] = -1
        if spec.primary_hostgroups:
            payload[GADPairConst.PRIMARY_HOSTGROUP_PAYLOADS] = self._append_hg_payload(
                spec.primary_hostgroups
            )

        if spec.secondary_hostgroups:
            payload[GADPairConst.SECONDARY_HOSTGROUP_PAYLOADS] = (
                self._append_hg_payload(spec.secondary_hostgroups)
            )

        if spec.allocate_new_consistency_group:
            payload[GADPairConst.NEW_CONSISTENCY_GROUP] = (
                spec.allocate_new_consistency_group
            )

        if spec.set_alua_mode:
            payload[GADPairConst.SET_ALUA_MODE] = spec.set_alua_mode
        if spec.primary_resource_group_name:
            payload[GADPairConst.PRIMARY_RESOURCE_GROUP_PAYLOAD] = {
                GADPairConst.NAME: spec.primary_resource_group_name
            }
        if spec.secondary_resource_group_name:
            payload[GADPairConst.VIRTUAL_RESOURCE_GROUP_PAYLOAD] = {
                GADPairConst.NAME: spec.secondary_resource_group_name
            }
        if spec.quorum_disk_id is not None:
            payload[GADPairConst.QUORUM_DISK_ID] = spec.quorum_disk_id

        endPoint = UAIGEndpoints.POST_GAD_PAIR
        result = self.connectionManager.post_subtask_ext(
            endPoint, data=payload, headers_input=self.headers
        )
        self.new_pair = True
        return result

    def _append_hg_payload(self, input_data):
        list_hgs = []
        for hg in input_data:
            dict_hg = {}
            dict_hg[GADPairConst.HOST_GROUP_ID] = hg.id
            dict_hg[GADPairConst.NAME] = hg.name
            dict_hg[GADPairConst.PORT] = hg.port
            dict_hg[GADPairConst.RESOURCE_GROUP_ID] = hg.resource_group_id
            if hg.enable_preferred_path:
                dict_hg[GADPairConst.ENABLE_PREFERRED_PATH] = hg.enable_preferred_path
            list_hgs.append(dict_hg)
        return list_hgs

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
    def resize_gad_pair(self, pair, spec):
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
            response = self.split_gad_pair(pair.resourceId)
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
            # if we split the pair, then we need to resync it before returning

            if "AFA8" in str(ex):
                raise ValueError(GADPairValidateMSG.EXPAND_VOLUME_FAILED.value)
            else:
                raise ValueError(
                    GADPairValidateMSG.EXPAND_SVOL_FAILED.value.format(svol_id)
                    + str(ex)
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
                raise ValueError(GADPairValidateMSG.EXPAND_VOLUME_FAILED.value)
            else:
                raise ValueError(
                    GADPairValidateMSG.EXPAND_PVOL_FAILED.value.format(pvol_id)
                    + str(ex)
                )

        if split_required:
            response = self.resync_gad_pair(pair.resourceId)
            logger.writeDebug("GW:resize_replication_pair:resync:response={}", response)
        return response

    @log_entry_exit
    def check_storage_in_ucpsystem(self) -> bool:
        storage_serial_number = self.serial_number
        logger.writeDebug(
            "GW:check_storage_in_ucpsystem:storage_serial_number={}",
            storage_serial_number,
        )
        ucpsystems = self.get_ucpsystems()
        logger.writeDebug("GW:check_storage_in_ucpsystem:ucpsystems={}", ucpsystems)
        for u in ucpsystems:
            # if u.get("name") == CommonConstants.UCP_NAME:
            for s in u.get("storageDevices"):
                if str(s.get("serialNumber")) == str(storage_serial_number):
                    return str(s.get("healthState")) != str(CommonConstants.ONBOARDING)
        return False

    @log_entry_exit
    def get_ucpsystems(self) -> List[Dict[str, Any]]:
        end_point = UAIGEndpoints.GET_UCPSYSTEMS
        ucpsystems = self.connectionManager.get(end_point)
        return ucpsystems["data"]
