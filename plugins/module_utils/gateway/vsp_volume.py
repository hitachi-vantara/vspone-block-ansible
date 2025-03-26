try:
    from .gateway_manager import VSPConnectionManager, UAIGConnectionManager
    from ..common.vsp_constants import (
        Endpoints,
        VolumePayloadConst,
        AutomationConstants,
    )
    from ..common.hv_constants import CommonConstants
    from ..common.ansible_common import dicts_to_dataclass_list
    from ..model.vsp_volume_models import (
        VSPVolumesInfo,
        VSPVolumeInfo,
        CreateVolumeSpec,
        VSPStorageVolumesUAIG,
        VSPStorageVolumeUAIG,
        VSPVolume_V2,
        VolumeQosParamsOutput,
        VSPUndefinedVolumeInfo,
        VSPUndefinedVolumeInfoList,
    )
    from ..common.hv_log import Log

    from ..common.ansible_common import log_entry_exit
    from ..model.common_base_models import VSPStorageDevice
    from ..common.vsp_constants import PEGASUS_MODELS
    from ..common.uaig_constants import Endpoints as UAIGEndpoints
    from ..common.uaig_utils import UAIGResourceID

except ImportError:
    from common.ansible_common import log_entry_exit
    from common.vsp_constants import Endpoints, VolumePayloadConst, AutomationConstants
    from common.hv_constants import CommonConstants
    from common.ansible_common import dicts_to_dataclass_list
    from model.vsp_volume_models import (
        VSPVolumesInfo,
        VSPVolumeInfo,
        CreateVolumeSpec,
        VSPStorageVolumesUAIG,
        VSPStorageVolumeUAIG,
        VSPVolume_V2,
        VolumeQosParamsOutput,
        VSPUndefinedVolumeInfo,
        VSPUndefinedVolumeInfoList,
    )
    from model.common_base_models import VSPStorageDevice
    from common.hv_log import Log
    from common.vsp_constants import PEGASUS_MODELS
    from common.uaig_constants import Endpoints as UAIGEndpoints
    from common.uaig_utils import UAIGResourceID


logger = Log()


class VSPVolumeDirectGateway:
    """
    VSPVolumeDirectGateway
    """

    def __init__(self, connection_info):
        self.rest_api = VSPConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )
        self.end_points = Endpoints
        self.is_pegasus = self.get_storage_details()
        self.serial = None

    @log_entry_exit
    def set_serial(self, serial):
        self.serial = serial

    @log_entry_exit
    def get_simple_volumes(
        self, start_ldev=0, ldev_option="defined", count=0
    ) -> VSPVolumesInfo:

        path = VolumePayloadConst.HEAD_LDEV_ID.format(start_ldev)
        path += VolumePayloadConst.LDEV_OPTION.format(ldev_option)
        path += VolumePayloadConst.COUNT.format(
            count if count > 0 else AutomationConstants.LDEV_MAX_NUMBER
        )

        end_point = self.end_points.GET_LDEVS.format(path)
        vol_data = self.rest_api.get(end_point)
        volumes = VSPVolumesInfo(
            dicts_to_dataclass_list(vol_data["data"], VSPVolumeInfo)
        )
        return volumes

    @log_entry_exit
    def get_volumes(
        self, start_ldev=0, ldev_option="defined", count=0
    ) -> VSPVolumesInfo:

        path = VolumePayloadConst.HEAD_LDEV_ID.format(start_ldev)
        path += VolumePayloadConst.LDEV_OPTION.format(ldev_option)
        path += VolumePayloadConst.COUNT.format(
            count if count > 0 else AutomationConstants.LDEV_MAX_NUMBER
        )

        end_point = self.end_points.GET_LDEVS.format(path)
        vol_data = self.rest_api.get(end_point)
        volumes = VSPVolumesInfo(
            dicts_to_dataclass_list(vol_data["data"], VSPVolumeInfo)
        )

        if self.is_pegasus:
            for volume in volumes.data:
                try:
                    pega_end_point = self.end_points.PEGA_LDEVS_ONE.format(
                        volume.ldevId
                    )
                    add_vol_data = self.rest_api.pegasus_get(pega_end_point)
                    drs_enabled = add_vol_data.get(
                        VolumePayloadConst.IS_DATA_REDUCTION_SHARE_ENABLED, False
                    )
                    volume.isDataReductionShareEnabled = drs_enabled
                except Exception as ex:
                    logger.writeDebug(f"GW: exception in get_volumes {ex}")
        return volumes

    @log_entry_exit
    def get_volumes_by_pool_id(self, pool_id) -> VSPVolumesInfo:

        end_point = self.end_points.GET_LDEVS_BY_POOL_ID.format(pool_id)
        vol_data = self.rest_api.get(end_point)
        return VSPVolumesInfo(dicts_to_dataclass_list(vol_data["data"], VSPVolumeInfo))

    @log_entry_exit
    def get_volume_by_id(self, ldev_id) -> VSPVolumeInfo:

        end_point = self.end_points.LDEVS_ONE.format(ldev_id)
        try:
            vol_data = self.rest_api.get(end_point)
        except Exception:
            # try once more
            vol_data = self.rest_api.get(end_point)

        volume_info = VSPVolumeInfo(**vol_data)
        if self.is_pegasus and volume_info.poolId is not None:
            try:
                pega_end_point = self.end_points.PEGA_LDEVS_ONE.format(ldev_id)
                add_vol_data = self.rest_api.pegasus_get(pega_end_point)
                drs_enabled = add_vol_data.get(
                    VolumePayloadConst.IS_DATA_REDUCTION_SHARE_ENABLED, False
                )
                volume_info.isDataReductionShareEnabled = drs_enabled
            except Exception as ex:
                logger.writeDebug(f"GW: exception in get_volume_by_id {ex}")
        return volume_info

    @log_entry_exit
    def get_volume_by_id_external_volume(self, ldev_id) -> VSPVolumeInfo:

        end_point = self.end_points.GET_LDEV_EXT_VOL.format(ldev_id)
        try:
            vol_data = self.rest_api.get(end_point)
        except Exception:
            # try once more
            vol_data = self.rest_api.get(end_point)

        volume_info = VSPVolumeInfo(**vol_data)
        if self.is_pegasus and volume_info.poolId is not None:
            try:
                pega_end_point = self.end_points.PEGA_LDEVS_ONE.format(ldev_id)
                add_vol_data = self.rest_api.pegasus_get(pega_end_point)
                drs_enabled = add_vol_data.get(
                    VolumePayloadConst.IS_DATA_REDUCTION_SHARE_ENABLED, False
                )
                volume_info.isDataReductionShareEnabled = drs_enabled
            except Exception as ex:
                logger.writeDebug(f"GW: exception in get_volume_by_id {ex}")
        return volume_info

    @log_entry_exit
    def map_ext_volume(
        self, ldevId: int, externalParityGroupId: str, externalVolumeCapacity: int
    ):
        payload = {
            "ldevId": ldevId,
            "externalParityGroupId": externalParityGroupId,
            "blockCapacity": externalVolumeCapacity,
        }

        end_point = self.end_points.POST_LDEVS
        logger.writeDebug(f"Payload for map volume: {payload}")

        url = self.rest_api.post(end_point, payload)

        # Split the ldevid from url
        return url.split("/")[-1]

    @log_entry_exit
    def create_volume(self, spec: CreateVolumeSpec):
        payload = {}
        logger.writeDebug(f"spec for creating volume: {spec}")

        # the block_size is added to support decimal values like 1.5 GB etc.
        if spec.block_size:
            payload[VolumePayloadConst.BLOCK_CAPACITY] = spec.block_size
        else:
            payload[VolumePayloadConst.BYTE_CAPACITY] = spec.size
        if isinstance(spec.pool_id, int):
            payload[VolumePayloadConst.POOL_ID] = spec.pool_id
        if spec.ldev_id:
            payload[VolumePayloadConst.LDEV] = spec.ldev_id
        if spec.capacity_saving:
            payload[VolumePayloadConst.ADR_SETTING] = spec.capacity_saving
            if self.is_pegasus:
                if (
                    spec.capacity_saving.lower() != VolumePayloadConst.DISABLED
                    and spec.pool_id is not None
                ):
                    logger.writeDebug(
                        f"is spec.data_reduction_share : {spec.data_reduction_share}"
                    )
                    is_true = (
                        True
                        if spec.data_reduction_share is None
                        else spec.data_reduction_share
                    )
                    logger.writeDebug(f"is true: {is_true}")

                    if spec.pool_id != -1:
                        payload[
                            VolumePayloadConst.IS_DATA_REDUCTION_SHARED_VOLUME_ENABLED
                        ] = is_true
            else:
                payload[VolumePayloadConst.IS_DATA_REDUCTION_SHARED_VOLUME_ENABLED] = (
                    spec.data_reduction_share
                )
        if spec.parity_group:
            payload[VolumePayloadConst.PARITY_GROUP] = spec.parity_group

        end_point = self.end_points.POST_LDEVS
        logger.writeDebug(f"Payload for creating volume: {payload}")

        url = self.rest_api.post(end_point, payload)
        # url = self.rest_api.post(end_point, payload, token=spec.lock_token)

        # Split the ldevid from url
        return url.split("/")[-1]

    @log_entry_exit
    def delete_volume(self, ldev_id, force_execute):
        payload = None
        if force_execute is not None:
            payload = {
                VolumePayloadConst.IS_DATA_REDUCTION_DELETE_FORCE_EXECUTE: force_execute
            }
        end_point = self.end_points.DELETE_LDEVS.format(ldev_id)
        return self.rest_api.delete(end_point, data=payload)

    @log_entry_exit
    def delete_lun_path(self, port):
        end_point = self.end_points.DELETE_LUNS.format(
            port["portId"], port["hostGroupNumber"], port["lun"]
        )
        return self.rest_api.delete(end_point)

    @log_entry_exit
    def get_free_ldev_from_meta(self):
        end_point = self.end_points.GET_FREE_LDEV_FROM_META
        vol_data = self.rest_api.get(end_point)
        return VSPVolumesInfo(dicts_to_dataclass_list(vol_data["data"], VSPVolumeInfo))

    @log_entry_exit
    def get_free_ldev_matching_pvol(self, pvol_id):

        found = False
        vol_data = None

        # while not found:
        end_point = self.end_points.GET_FREE_LDEV_MATCHING_PVOL.format(pvol_id)
        vol_data = self.rest_api.get(end_point)
        if vol_data["data"]:
            resource_group_id = vol_data["data"][0]["resourceGroupId"]
            if resource_group_id != 0:
                #     # if resource_group_id is 0, then it is a free ldev in meta
                #     found = True
                # else:
                end_point = self.end_points.GET_FREE_LDEV_FROM_META.format(pvol_id)
                vol_data = self.rest_api.get(end_point)

        return VSPUndefinedVolumeInfoList(
            dicts_to_dataclass_list(vol_data["data"], VSPUndefinedVolumeInfo)
        )

    @log_entry_exit
    def update_volume(self, ldev_id, name=None, adr_setting=None):

        payload = {}

        if adr_setting:
            payload[VolumePayloadConst.ADR_SETTING] = adr_setting
        if name:
            payload[VolumePayloadConst.LABEL] = name

        end_point = self.end_points.LDEVS_ONE.format(ldev_id)
        return self.rest_api.patch(end_point, payload)

    @log_entry_exit
    def expand_volume(self, ldev_id, additional_capacity, enhanced_expansion):

        payload = {
            VolumePayloadConst.PARAMS: {
                VolumePayloadConst.ADDITIONAL_BLOCK_CAPACITY: round(additional_capacity)
            }
        }
        if enhanced_expansion:
            payload[VolumePayloadConst.PARAMS][
                VolumePayloadConst.ENHANCED_EXPANSION
            ] = True
        end_point = self.end_points.POST_EXPAND_LDEV.format(ldev_id)
        return self.rest_api.post(end_point, payload)

    # sng20241205 unassign_vldev
    @log_entry_exit
    def unassign_vldev(self, ldev_id, vldev_id):
        payload = {
            VolumePayloadConst.PARAMS: {
                VolumePayloadConst.VIRTUAL_LDEVID: vldev_id,
            }
        }
        end_point = self.end_points.POST_UNASSIGN_VLDEV.format(ldev_id)
        return self.rest_api.post(end_point, payload)

    @log_entry_exit
    def assign_vldev(self, ldev_id, vldev_id):
        payload = {
            VolumePayloadConst.PARAMS: {
                VolumePayloadConst.VIRTUAL_LDEVID: vldev_id,
            }
        }
        end_point = self.end_points.POST_ASSIGN_VLDEV.format(ldev_id)
        return self.rest_api.post(end_point, payload)

    @log_entry_exit
    def format_volume(self, ldev_id, force_format: bool):
        operation_type = (
            VolumePayloadConst.FMT if force_format else VolumePayloadConst.QFMT
        )
        payload = {
            VolumePayloadConst.PARAMS: {
                VolumePayloadConst.OPERATION_TYPE: operation_type,
                VolumePayloadConst.FORCE_FORMAT: force_format,
            }
        }
        end_point = self.end_points.POST_FORMAT_LDEV.format(ldev_id)
        return self.rest_api.post(end_point, payload)

    @log_entry_exit
    def shredding_volume(self, ldev_id, start=True):

        operation_type = VolumePayloadConst.START if start else VolumePayloadConst.STOP
        payload = {
            VolumePayloadConst.PARAMS: {
                VolumePayloadConst.OPERATION_TYPE: operation_type,
            }
        }
        end_point = self.end_points.POST_SHRED_LDEV.format(ldev_id)
        return self.rest_api.post(end_point, payload)

    @log_entry_exit
    def change_qos_settings(self, ldev_id, qos_spec):
        # Define the data
        nested_data = {
            VolumePayloadConst.UPPER_IOPS: qos_spec.upper_iops,
            VolumePayloadConst.LOWER_IOPS: qos_spec.lower_iops,
            VolumePayloadConst.UPPER_TRANSFER_RATE: qos_spec.upper_transfer_rate,
            VolumePayloadConst.LOWER_TRANSFER_RATE: qos_spec.lower_transfer_rate,
            VolumePayloadConst.UPPER_ALERT_ALLOWABLE_TIME: qos_spec.upper_alert_allowable_time,
            VolumePayloadConst.LOWER_ALERT_ALLOWABLE_TIME: qos_spec.lower_alert_allowable_time,
            VolumePayloadConst.RESPONSE_PRIORITY: qos_spec.response_priority,
            VolumePayloadConst.RESPONSE_ALERT_ALLOWABLE_TIME: qos_spec.response_alert_allowable_time,
        }

        # Iterate over each item and send individual requests for non-None values
        for key, value in nested_data.items():
            if value is not None:
                payload = {VolumePayloadConst.PARAMS: {key: value}}
                end_point = self.end_points.POST_QOS_UPDATE.format(ldev_id)
                self.rest_api.post(end_point, payload)

        return "All QoS updates sent successfully."

    @log_entry_exit
    def get_qos_settings(self, ldev_id):
        end_point = self.end_points.GET_QOS_SETTINGS.format(ldev_id)

        qos_data = self.rest_api.get(end_point)
        if len(qos_data.get("data")) > 0 and qos_data.get("data")[0].get("qos"):
            return VolumeQosParamsOutput(**qos_data.get("data")[0].get("qos"))
        return None

    @log_entry_exit
    def change_volume_status(self, ldev_id, is_block=False):

        operation_type = "blk" if is_block else "nml"
        payload = {
            VolumePayloadConst.PARAMS: {
                VolumePayloadConst.STATUS: operation_type,
            }
        }
        end_point = self.end_points.POST_CHANGE_STATUS_LDEV.format(ldev_id)
        return self.rest_api.post(end_point, payload)

    @log_entry_exit
    def fill_cmd_device_info(self, volume):
        logger.writeDebug(f"fill_cmd_device_info: is_pegasus= {self.is_pegasus}")
        volume.isCommandDevice = True
        if self.is_pegasus:
            # VSP One does not support detailInfoType=class
            return volume

        end_point = self.end_points.GET_CMD_DEVICE.format(volume.ldevId)
        vol_data = self.rest_api.get(end_point)
        if vol_data and vol_data.get("data"):
            vol_data = vol_data.get("data")
            command_device = vol_data[0].get("commandDevice")
            if command_device:
                volume.isSecurityEnabled = command_device.get("isSecurityEnabled")
                volume.isUserAuthenticationEnabled = command_device.get(
                    "isUserAuthenticationEnabled"
                )
                volume.isDeviceGroupDefinitionEnabled = command_device.get(
                    "isDeviceGroupDefinitionEnabled"
                )
        logger.writeDebug(f"fill_cmd_device_info: vol_data= {vol_data}")
        return volume

    @log_entry_exit
    def change_volume_settings(self, ldev_id, label=None, isAluaEnabled=None):

        doPatch = False
        payload = {}
        if isAluaEnabled is not None:
            payload["isAluaEnabled"] = isAluaEnabled
            doPatch = True
        if label is not None:
            payload["label"] = label
            doPatch = True

        if not doPatch:
            return

        end_point = self.end_points.LDEVS_ONE.format(ldev_id)
        return self.rest_api.patch(end_point, payload)

    @log_entry_exit
    def change_volume_settings_tier_reloc(self, ldev_id, spec=None):

        doPatch = False
        payload = {}
        tier_level_for_new_page_allocation = spec.tier_level_for_new_page_allocation
        if tier_level_for_new_page_allocation:
            tierLevelForNewPageAlloc = "M"
            if tier_level_for_new_page_allocation.lower() == "high":
                tierLevelForNewPageAlloc = "H"
            if tier_level_for_new_page_allocation.lower() == "low":
                tierLevelForNewPageAlloc = "L"
            payload["tierLevelForNewPageAllocation"] = tierLevelForNewPageAlloc
            doPatch = True
        isRelocationEnabled = spec.is_relocation_enabled
        if isRelocationEnabled is not None:
            payload["isRelocationEnabled"] = isRelocationEnabled
            doPatch = True

        if not doPatch:
            return

        end_point = self.end_points.LDEVS_ONE.format(ldev_id)
        return self.rest_api.patch(end_point, payload)

    # sng20241202 change_volume_settings_tier_policy
    @log_entry_exit
    def change_volume_settings_tier_policy(self, ldev_id, spec=None):

        if not spec.is_relocation_enabled:
            return

        tiering_policy = spec.tiering_policy
        if tiering_policy is None:
            return

        tieringPolicy = {
            "tierLevel": tiering_policy.get("tier_level", None),
            "tier1AllocationRateMin": tiering_policy.get(
                "tier1_allocation_rate_min", None
            ),
            "tier1AllocationRateMax": tiering_policy.get(
                "tier1_allocation_rate_max", None
            ),
            "tier3AllocationRateMin": tiering_policy.get(
                "tier3_allocation_rate_min", None
            ),
            "tier3AllocationRateMax": tiering_policy.get(
                "tier3_allocation_rate_max", None
            ),
        }

        payload = {"tieringPolicy": tieringPolicy}
        end_point = self.end_points.LDEVS_ONE.format(ldev_id)
        return self.rest_api.patch(end_point, payload)

    @log_entry_exit
    def get_storage_details(self):
        end_point = self.end_points.GET_STORAGE_INFO
        storage_info = self.rest_api.get(end_point)
        logger.writeDebug(f"Found storage details{storage_info}")
        storage_info = VSPStorageDevice(**storage_info)

        pegasus_model = any(sub in storage_info.model for sub in PEGASUS_MODELS)
        logger.writeDebug(f"Storage Model: {storage_info.model}")
        return pegasus_model


class VSPVolumeUAIGateway:
    def __init__(self, connection_info):
        self.connection_manager = UAIGConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )
        self.connection_info = connection_info
        self.serial = None
        self.resource_id = None

    @log_entry_exit
    def set_serial(self, serial):
        self.serial = serial
        self.set_resource_id()

    @log_entry_exit
    def set_resource_id(self):
        self.resource_id = UAIGResourceID().storage_resourceId(self.serial)
        logger.writeDebug(
            "GW:set_resource_id:serial = {}  resourceId = {}",
            self.serial,
            self.resource_id,
        )

    @log_entry_exit
    def get_volumes(self, device_id):
        end_point = UAIGEndpoints.UAIG_GET_VOLUMES.format(device_id)
        headers = self.populate_headers()
        vol_data = self.connection_manager.get(end_point, headers_input=headers)
        volumes = VSPStorageVolumesUAIG(
            dicts_to_dataclass_list(vol_data["data"], VSPStorageVolumeUAIG)
        )

        logger.writeDebug("GW:get_volumes:data = {}", volumes)
        return volumes

    @log_entry_exit
    def get_volume_by_id(self, volume_id):
        # sng20241220 - this function is for gateway and it is not work
        # code was added and never tested
        end_point = UAIGEndpoints.GET_VOLUME_BY_ID.format(self.resource_id, volume_id)
        headers = self.populate_headers()
        vol_data = self.connection_manager.get(end_point, headers_input=headers)
        logger.writeDebug("GW:get_volume_by_id:data = {}", vol_data)

        volume_info = VSPVolume_V2(**vol_data.get("data"))
        # for v in volume_info.data:
        #     logger.writeDebug(
        #         f"PROV:get_volume_by_id:volumes: {v.storageVolumeInfo['ldevId']} "
        #     )
        #     if str(v.storageVolumeInfo["ldevId"]) == str(volume_id):
        #         return v
        return volume_info

    @log_entry_exit
    def populate_headers(self):
        headers = {"partnerId": CommonConstants.PARTNER_ID}
        if self.connection_info.subscriber_id is not None:
            headers["subscriberId"] = self.connection_info.subscriber_id
        return headers

    @log_entry_exit
    def get_volume_by_id_v2(self, storage_id, volume_id):
        end_point = UAIGEndpoints.GET_VOLUME_BY_ID.format(storage_id, volume_id)

        vol_data = self.connection_manager.get(end_point, headers_input=None)
        logger.writeDebug("GW:get_volume_by_id_v2:data = {}", vol_data)

        volume_info = VSPVolume_V2(**vol_data.get("data"))
        return volume_info

    @log_entry_exit
    def update_volume(
        self, storage_id, volume_id, capacity=None, de_dup_comp_mode=None, lu_name=None
    ):
        end_point = UAIGEndpoints.GET_VOLUME_BY_ID.format(storage_id, volume_id)
        headers = self.populate_headers()

        payload = {}
        if capacity:
            payload["capacity"] = capacity
        if de_dup_comp_mode:
            payload["deduplicationCompressionMode"] = de_dup_comp_mode
        if lu_name:
            payload["luName"] = lu_name
        response = self.connection_manager.patch(end_point, payload, headers)
        return response
