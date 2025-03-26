import time
from typing import List, Dict, Any

try:
    from ..common.uaig_constants import Endpoints
    from ..common.hv_constants import CommonConstants
    from .gateway_manager import VSPConnectionManager, UAIGConnectionManager
    from .vsp_replication_pairs_gateway import VSPReplicationPairsDirectGateway
    from ..common.hv_log import Log
    from ..common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from ..common.uaig_utils import UAIGResourceID
    from .vsp_volume import VSPVolumeUAIGateway
    from ..message.vsp_true_copy_msgs import VSPTrueCopyValidateMsg
    from ..model.vsp_true_copy_models import (
        VSPReplicationPairInfo,
        VSPReplicationPairInfoList,
        VSPTrueCopyPairInfo,
        VSPTrueCopyPairInfoList,
        DirectTrueCopyPairInfo,
        DirectTrueCopyPairInfoList,
    )
except ImportError:
    from common.uaig_constants import Endpoints
    from common.hv_constants import CommonConstants
    from .gateway_manager import VSPConnectionManager, UAIGConnectionManager
    from .vsp_replication_pairs_gateway import VSPReplicationPairsDirectGateway
    from common.hv_log import Log
    from common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from common.uaig_utils import UAIGResourceID
    from .vsp_volume import VSPVolumeUAIGateway
    from message.vsp_true_copy_msgs import VSPTrueCopyValidateMsg
    from model.vsp_true_copy_models import (
        VSPReplicationPairInfo,
        VSPReplicationPairInfoList,
        VSPTrueCopyPairInfo,
        VSPTrueCopyPairInfoList,
        DirectTrueCopyPairInfo,
        DirectTrueCopyPairInfoList,
    )

CREATE_TRUE_COPY_PAIR_DIRECT = "v1/objects/storages/{}/remote-mirror-copypairs"
SPLIT_TRUE_COPY_PAIR_DIRECT = (
    "v1/objects/storages/{}/remote-mirror-copypairs/{}/actions/split/invoke"
)
RESYNC_TRUE_COPY_PAIR_DIRECT = (
    "v1/objects/storages/{}/remote-mirror-copypairs/{}/actions/resync/invoke"
)
GET_REMOTE_STORAGES_DIRECT = "v1/objects/remote-storages"
GET_STORAGES_DIRECT = "v1/objects/storages"
GET_TRUE_COPY_PAIRS_DIRECT = "v1/objects/remote-copypairs?replicationType=TC"
# DELETE_TRUE_COPY_PAIR_DIRECT = "v1/objects/storages/{}/remote-mirror-copypairs/{}"

DELETE_TRUE_COPY_PAIR_DIRECT = "v1/objects/remote-mirror-copypairs/{}"


logger = Log()


class VSPTrueCopyDirectGateway(VSPReplicationPairsDirectGateway):

    @log_entry_exit
    def get_all_true_copy_pairs(self, serial=None):
        end_point = GET_TRUE_COPY_PAIRS_DIRECT
        tc_data = self.connection_manager.get(end_point)
        logger.writeDebug("GW-Direct:get_all_true_copy_pairs:data={}", tc_data)

        return DirectTrueCopyPairInfoList(
            dicts_to_dataclass_list(tc_data["data"], DirectTrueCopyPairInfo)
        )

    @log_entry_exit
    def get_secondary_serial(self, spec):
        secondary_storage_info = self.get_secondary_storage_info(
            spec.secondary_connection_info
        )
        return secondary_storage_info.get("serialNumber")

    @log_entry_exit
    def create_true_copy(self, spec) -> Dict[str, Any]:

        secondary_storage_info = self.get_secondary_storage_info(
            spec.secondary_connection_info
        )
        logger.writeDebug(
            "GW:create_true_copy:secondary_storage_info={}",
            secondary_storage_info,
        )
        remote_storage_device_id = secondary_storage_info.get("storageDeviceId")

        payload = {
            "copyGroupName": spec.copy_group_name,
            "copyPairName": spec.copy_pair_name,
            "replicationType": "TC",
            "remoteStorageDeviceId": remote_storage_device_id,
            "pvolLdevId": spec.primary_volume_id,
            "svolLdevId": spec.secondary_volume_id,
            "isNewGroupCreation": (
                spec.is_new_group_creation
                if spec.is_new_group_creation is not None
                else True
            ),
            "fenceLevel": spec.fence_level if spec.fence_level else "NEVER",
        }
        if spec.path_group_id:
            payload["pathGroupId"] = spec.path_group_id
        if spec.local_device_group_name:
            payload["localDeviceGroupName"] = spec.local_device_group_name
        if spec.remote_device_group_name:
            payload["remoteDeviceGroupName"] = spec.remote_device_group_name

        if spec.is_consistency_group is not None:
            payload["isConsistencyGroup"] = spec.is_consistency_group
        else:
            payload["isConsistencyGroup"] = False

        if spec.consistency_group_id:
            if spec.is_new_group_creation:
                pass
            else:
                payload["consistencyGroupId"] = spec.consistency_group_id

        if spec.copy_pace:
            payload["copyPace"] = self.get_copy_pace_value(spec.copy_pace)
        if spec.do_initial_copy is not None:
            payload["doInitialCopy"] = spec.do_initial_copy
        if spec.is_data_reduction_force_copy is not None:
            payload["isDataReductionForceCopy"] = spec.is_data_reduction_force_copy
        else:
            payload["isDataReductionForceCopy"] = True
        storage_deviceId = self.get_storage_device_id(str(self.storage_serial_number))
        logger.writeDebug(
            "GW-Direct:create_true_copy:storage_deviceId={}", storage_deviceId
        )
        headers = self.get_remote_token(spec.secondary_connection_info)
        headers["Remote-Authorization"] = headers.pop("Authorization")
        headers["Job-Mode-Wait-Configuration-Change"] = "NoWait"
        logger.writeDebug("GW-Direct:create_true_copy:remote_header={}", headers)
        end_point = CREATE_TRUE_COPY_PAIR_DIRECT.format(storage_deviceId)
        logger.writeDebug("GW-Direct:create_true_copy:end_point={}", end_point)
        start_time = time.time()
        response = self.connection_manager.post(
            end_point, payload, headers_input=headers
        )
        end_time = time.time()
        logger.writeDebug("PF_REST:create_true_copy:time={:.2f}", end_time - start_time)
        return response

    @log_entry_exit
    def split_true_copy_pair(self, spec):
        return super().split_replication_pair(spec, "TC")

    @log_entry_exit
    def swap_split_true_copy_pair(self, spec, mode=None):
        return super().swap_split_replication_pair(spec, "TC", mode)

    @log_entry_exit
    def resync_true_copy_pair(self, spec):
        return super().resync_replication_pair(spec, "TC")

    @log_entry_exit
    def swap_resync_true_copy_pair(self, spec):
        return super().swap_resync_replication_pair(spec, "TC")

    @log_entry_exit
    def resize_true_copy_pair(self, pair, spec):
        return super().resize_replication_pair(pair, spec)

    @log_entry_exit
    def split_true_copy_pair_by_object_id(
        self, object_id, sec_conn_info, replication_type, is_svol_readwriteable
    ):
        return super().split_replication_pair_by_object_id(
            object_id, sec_conn_info, replication_type, is_svol_readwriteable
        )

    @log_entry_exit
    def swap_split_true_copy_pair_by_object_id(
        self, object_id, sec_conn_info, replication_type
    ):
        return super().swap_split_replication_pair_by_object_id(
            object_id, sec_conn_info, replication_type
        )

    @log_entry_exit
    def resync_true_copy_pair_by_object_id(
        self, object_id, sec_conn_info, replication_type
    ):
        return super().resync_replication_pair_by_object_id(
            object_id, sec_conn_info, replication_type
        )

    @log_entry_exit
    def swap_resync_true_copy_pair_by_object_id(
        self, object_id, sec_conn_info, replication_type
    ):
        return super().swap_resync_replication_pair_by_object_id(
            object_id, sec_conn_info, replication_type
        )

    @log_entry_exit
    def delete_true_copy_pair_by_object_id(self, object_id, sec_conn_info):
        self.connection_manager = VSPConnectionManager(
            self.connection_info.address,
            self.connection_info.username,
            self.connection_info.password,
            self.connection_info.api_token,
        )
        remote_connection_manager = VSPConnectionManager(
            sec_conn_info.address,
            sec_conn_info.username,
            sec_conn_info.password,
            sec_conn_info.api_token,
        )
        headers = remote_connection_manager.getAuthToken()
        headers["Remote-Authorization"] = headers.pop("Authorization")
        end_point = DELETE_TRUE_COPY_PAIR_DIRECT.format(object_id)
        start_time = time.time()
        response = self.connection_manager.delete(
            end_point, None, headers_input=headers
        )
        end_time = time.time()
        logger.writeDebug("PF_REST:delete_true_copy:time={:.2f}", end_time - start_time)
        return response

    @log_entry_exit
    def delete_true_copy_pair_by_pair_id(self, spec):
        return super().delete_replication_pair(spec)

        # secondary_storage_info = self.get_secondary_storage_info(spec.secondary_connection_info)
        # logger.writeDebug("GW:delete_true_copy_pair_by_pair_id:secondary_storage_info={}", secondary_storage_info)
        # remote_storage_deviceId = secondary_storage_info.get("storageDeviceId")
        # # remoteStorageDeviceId,copyGroupName,localDeviceGroupName,remoteDeviceGroupName, copyPairName
        # local_device_group_name = spec.local_device_group_name if spec.local_device_group_name else spec.copy_group_name + "P_"
        # remote_device_group_name = spec.remote_device_group_name if spec.remote_device_group_name else spec.copy_group_name + "S_"
        # object_id = f"{remote_storage_deviceId},{spec.copy_group_name},{local_device_group_name},{remote_device_group_name},{spec.copy_pair_name}"

        # return self.delete_true_copy_pair_by_object_id(object_id, spec.secondary_connection_info)

    @log_entry_exit
    def get_copy_pair_for_primary_volume_id_from_cp_gr(self, cg_gw, spec):
        copy_pairs = cg_gw.get_remote_pairs_for_a_copy_group(spec)
        if copy_pairs is None:
            return None
        for cp in copy_pairs:
            if cp.pvolLdevId == spec.primary_volume_id:
                return cp
        return None

    @log_entry_exit
    def delete_true_copy_pair_by_copy_group_and_pvol_id(self, cg_gw, spec):
        cp = self.get_copy_pair_for_primary_volume_id_from_cp_gr(cg_gw, spec)
        if cp is None:
            return None

        object_id = cp.remoteMirrorCopyPairId
        return self.delete_true_copy_pair_by_object_id(
            object_id, spec.secondary_connection_info
        )

    @log_entry_exit
    def split_true_copy_pair_by_copy_group_and_pvol_id(self, cg_gw, spec):
        cp = self.get_copy_pair_for_primary_volume_id_from_cp_gr(cg_gw, spec)
        if cp is None:
            return None
        object_id = cp.remoteMirrorCopyPairId
        return self.split_true_copy_pair_by_object_id(
            object_id, spec.secondary_connection_info, "TC", spec.is_svol_readwriteable
        )

    @log_entry_exit
    def swap_split_true_copy_pair_by_copy_group_and_pvol_id(self, cg_gw, spec):
        cp = self.get_copy_pair_for_primary_volume_id_from_cp_gr(cg_gw, spec)
        if cp is None:
            return None
        object_id = cp.remoteMirrorCopyPairId
        return self.swap_split_true_copy_pair_by_object_id(
            object_id, spec.secondary_connection_info, "TC"
        )

    @log_entry_exit
    def resync_true_copy_pair_by_copy_group_and_pvol_id(self, cg_gw, spec):
        cp = self.get_copy_pair_for_primary_volume_id_from_cp_gr(cg_gw, spec)
        if cp is None:
            return None
        object_id = cp.remoteMirrorCopyPairId
        return self.resync_true_copy_pair_by_object_id(
            object_id, spec.secondary_connection_info, "TC"
        )

    @log_entry_exit
    def swap_resync_true_copy_pair_by_copy_group_and_pvol_id(self, cg_gw, spec):
        cp = self.get_copy_pair_for_primary_volume_id_from_cp_gr(cg_gw, spec)
        if cp is None:
            return None
        object_id = cp.remoteMirrorCopyPairId
        return self.swap_resync_true_copy_pair_by_object_id(
            object_id, spec.secondary_connection_info, "TC"
        )

    @log_entry_exit
    def delete_true_copy_pair_by_primary_volume_id(self, cg_gw, spec):
        tc_copy_pairs = cg_gw.get_remote_pairs_by_pvol(spec)
        if tc_copy_pairs:
            object_id = tc_copy_pairs[0].remoteMirrorCopyPairId
            return self.delete_true_copy_pair_by_object_id(
                object_id, spec.secondary_connection_info
            )
        return None

    @log_entry_exit
    def split_true_copy_pair_by_primary_volume_id(self, cg_gw, spec):
        tc_copy_pairs = cg_gw.get_remote_pairs_by_pvol(spec)
        if tc_copy_pairs:
            object_id = tc_copy_pairs[0].remoteMirrorCopyPairId
            return self.split_true_copy_pair_by_object_id(
                object_id,
                spec.secondary_connection_info,
                "TC",
                spec.is_svol_readwriteable,
            )
        return None

    @log_entry_exit
    def swap_split_true_copy_pair_by_primary_volume_id(self, cg_gw, spec):
        tc_copy_pairs = cg_gw.get_remote_pairs_by_pvol(spec)
        if tc_copy_pairs:
            object_id = tc_copy_pairs[0].remoteMirrorCopyPairId
            return self.swap_split_true_copy_pair_by_object_id(
                object_id, spec.secondary_connection_info, "TC"
            )
        return None

    @log_entry_exit
    def resync_true_copy_pair_by_primary_volume_id(self, cg_gw, spec):
        tc_copy_pairs = cg_gw.get_remote_pairs_by_pvol(spec)
        if tc_copy_pairs:
            object_id = tc_copy_pairs[0].remoteMirrorCopyPairId
            return self.resync_true_copy_pair_by_object_id(
                object_id, spec.secondary_connection_info, "TC"
            )
        return None

    @log_entry_exit
    def swap_resync_true_copy_pair_by_primary_volume_id(self, cg_gw, spec):
        tc_copy_pairs = cg_gw.get_remote_pairs_by_pvol(spec)
        if tc_copy_pairs:
            object_id = tc_copy_pairs[0].remoteMirrorCopyPairId
            return self.swap_resync_true_copy_pair_by_object_id(
                object_id, spec.secondary_connection_info, "TC"
            )
        return None

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


class VSPTrueCopyUAIGateway:

    def __init__(self, connection_info):

        self.connection_manager = UAIGConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )
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
        logger.writeDebug(
            "GW:get_remote_ucp_serial: type of secondary_serial_number= {}",
            type(secondary_serial_number),
        )
        ucpsystems = self.get_ucpsystems()
        logger.writeDebug("GW:get_remote_ucp_serial:ucpsystems={}", ucpsystems)
        for u in ucpsystems:
            storage_devices = u.get("storageDevices")
            logger.writeDebug(
                "GW:get_remote_ucp_serial:storage_devices={}", storage_devices
            )
            for s in u.get("storageDevices"):
                logger.writeDebug("GW:get_remote_ucp_serial:s={}", s)
                if s.get("serialNumber") == str(secondary_serial_number):
                    return s.get("ucpSystems")[0]

        raise ValueError("Remote secondary storage not found.")

    @log_entry_exit
    def get_all_replication_pairs(self, serial):

        end_point = self.end_points.GET_REPLICATION_PAIRS.format(serial)
        rp_data = self.connection_manager.get(end_point)
        logger.writeDebug("GW:get_all_replication_pairs:data={}", rp_data)

        return VSPReplicationPairInfoList(
            dicts_to_dataclass_list(rp_data["data"], VSPReplicationPairInfo)
        )

    @log_entry_exit
    def get_all_true_copy_pairs(self, serial):
        device_id = UAIGResourceID().storage_resourceId(serial)
        logger.writeDebug("GW:427:serial={}", serial)
        logger.writeDebug("GW:427:device_id={}", device_id)
        end_point = self.end_points.GET_TRUE_COPY_PAIRS.format(device_id)
        headers = self._populate_headers()  # need this code when use v3
        tc_data = self.connection_manager.get(end_point, headers_input=headers)
        logger.writeDebug("GW:get_all_true_copy_pairs:data={}", tc_data)

        return VSPTrueCopyPairInfoList(
            dicts_to_dataclass_list(tc_data["data"], VSPTrueCopyPairInfo)
        )

    @log_entry_exit
    def get_replication_pair_by_id(self, device_id, pair_id):

        end_point = self.end_points.GET_REPLICATION_PAIR_BY_ID.format(
            device_id, pair_id
        )
        data = self.connection_manager.get(end_point)
        rp_data = data["data"]
        logger.writeDebug("GW:get_replication_pair_by_id:data={}", data)
        return VSPReplicationPairInfo(**rp_data)

    @log_entry_exit
    def delete_true_copy_pair(self, id, true_copy_pair_id):

        headers = self._populate_headers()
        delete_lun = False  # need to add this in spec
        end_point = self.end_points.DELETE_TRUE_COPY_PAIR.format(
            id, true_copy_pair_id, delete_lun
        )
        data = self.connection_manager.delete(end_point, headers_input=headers)
        return data

    @log_entry_exit
    def resync_true_copy_pair(self, id, true_copy_pair_id):
        end_point = self.end_points.RESYNC_TRUE_COPY_PAIR.format(id, true_copy_pair_id)
        data = self.connection_manager.patch(end_point)
        return data

    @log_entry_exit
    def split_true_copy_pair(self, id, true_copy_pair_id, enableReadWrite=None):
        end_point = self.end_points.SPLIT_TRUE_COPY_PAIR.format(id, true_copy_pair_id)
        payload = {}
        if enableReadWrite is not None:
            payload["enableReadWrite"] = enableReadWrite
        data = self.connection_manager.patch(end_point, payload)
        return data

    @log_entry_exit
    def swap_split_true_copy_pair(self, id, true_copy_pair_id):
        end_point = self.end_points.SWAP_SPLIT_TRUE_COPY_PAIR.format(
            id, true_copy_pair_id
        )
        data = self.connection_manager.patch(end_point)
        return data

    @log_entry_exit
    def swap_resync_true_copy_pair(self, id, true_copy_pair_id):
        end_point = self.end_points.SWAP_RESYNC_TRUE_COPY_PAIR.format(
            id, true_copy_pair_id
        )
        data = self.connection_manager.patch(end_point)
        return data

    @log_entry_exit
    def create_true_copy(self, spec) -> Dict[str, Any]:

        primary_volume_id = spec.primary_volume_id
        secondary_storage_serial_number = spec.secondary_storage_serial_number
        secondary_pool_id = spec.secondary_pool_id
        secondary_hostgroups = spec.secondary_hostgroups
        consistency_group_id = spec.consistency_group_id or -1
        fence_level = spec.fence_level or "NEVER"
        allocate_new_consistency_group = spec.allocate_new_consistency_group or False

        storage_resourceId = UAIGResourceID().storage_resourceId(
            self.storage_serial_number
        )
        end_point = self.end_points.CREATE_TRUE_COPY_PAIR
        remote_ucp_serial = self.get_remote_ucp_serial(
            str(secondary_storage_serial_number)
        )
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

        if spec.begin_secondary_volume_id is not None:
            payload["beginLdevId"] = spec.begin_secondary_volume_id
        if spec.end_secondary_volume_id is not None:
            payload["endLdevId"] = spec.end_secondary_volume_id

        headers = self._populate_headers()  # need this code when use v3
        logger.writeDebug(f"Create TrueCopy payload: {payload}")
        return self.connection_manager.post_subtask_ext(
            end_point, payload, headers_input=headers
        )

    def _populate_headers(self) -> Dict[str, str]:
        headers = {"partnerId": CommonConstants.PARTNER_ID}
        # 20240814 - hur subscriberId
        # logger.writeDebug("168 self.connection_info.subscriber_id={}", self.connection_info.subscriber_id)
        if self.connection_info.subscriber_id is not None:
            headers["subscriberId"] = self.connection_info.subscriber_id
        return headers

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
    def resize_true_copy_pair(self, pair, spec):
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
            response = self.split_true_copy_pair(storage_resourceId, pair.resourceId)
            logger.writeDebug("GW:resize_replication_pair:split:response={}", response)
        try:
            self.expand_volume(
                self.connection_info,
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
                raise ValueError(VSPTrueCopyValidateMsg.EXPAND_VOLUME_FAILED.value)
            else:
                raise ValueError(
                    VSPTrueCopyValidateMsg.EXPAND_SVOL_FAILED.value.format(svol_id)
                    + str(ex)
                )

        try:
            self.expand_volume(
                self.connection_info, storage_resourceId, ldev_resource_id, spec
            )
            logger.writeDebug("GW:resize_replication_pair:pvol_id={}", pvol_id)
        except Exception as ex:
            logger.writeDebug(
                "GW:resize_replication_pair:exception in expand volume:ex={}", ex
            )
            if "AFA8" in str(ex):
                raise ValueError(VSPTrueCopyValidateMsg.EXPAND_VOLUME_FAILED.value)
            else:
                raise ValueError(
                    VSPTrueCopyValidateMsg.EXPAND_PVOL_FAILED.value.format(pvol_id)
                    + str(ex)
                )

        if split_required:
            response = self.resync_true_copy_pair(storage_resourceId, pair.resourceId)
            logger.writeDebug("GW:resize_replication_pair:resync:response={}", response)
        return response
