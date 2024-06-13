try:
    from .gateway_manager import VSPConnectionManager
    from ..common.vsp_constants import (
        Endpoints,
        VolumePayloadConst,
        AutomationConstants,
    )
    from ..common.ansible_common import dicts_to_dataclass_list
    from ..model.vsp_volume_models import (
        VSPVolumesInfo,
        VSPVolumeInfo,
        CreateVolumeSpec,
    )
    from ..common.hv_log import Log

    from ..common.ansible_common import log_entry_exit
    from ..model.common_base_models import VSPStorageDevice
    from ..common.vsp_constants import PEGASUS_MODELS

except ImportError:
    from common.ansible_common import log_entry_exit
    from common.vsp_constants import Endpoints, VolumePayloadConst, AutomationConstants
    from common.ansible_common import dicts_to_dataclass_list
    from model.vsp_volume_models import VSPVolumesInfo, VSPVolumeInfo, CreateVolumeSpec
    from model.common_base_models import VSPStorageDevice
    from common.hv_log import Log
    from common.vsp_constants import PEGASUS_MODELS




class VSPVolumeDirectGateway:
    """
    VSPVolumeDirectGateway
    """

    def __init__(self, connection_info):
        self.logger = Log()
        self.rest_api = VSPConnectionManager(
            connection_info.address, connection_info.username, connection_info.password
        )
        self.end_points = Endpoints
        self.is_pegasus = self.get_storage_details()
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
        return VSPVolumesInfo(dicts_to_dataclass_list(vol_data["data"], VSPVolumeInfo))

    @log_entry_exit
    def get_volume_by_id(self, ldev_id) -> VSPVolumeInfo:

        end_point = self.end_points.LDEVS_ONE.format(ldev_id)
        vol_data = self.rest_api.get(end_point)
        volume_info = VSPVolumeInfo(**vol_data)
        if self.is_pegasus and volume_info.poolId is not None:
            pega_end_point = self.end_points.PEGA_LDEVS_ONE.format(ldev_id)
            add_vol_data = self.rest_api.pegasus_get(pega_end_point)
            volume_info.isDataReductionShareEnabled = add_vol_data.get(VolumePayloadConst.IS_DATA_REDUCTION_SHARE_ENABLED)
        return volume_info

    @log_entry_exit
    def create_volume(self, spec: CreateVolumeSpec):
        payload = {}
        self.logger.writeDebug(f"spec for creating volume: {spec}")

        payload[VolumePayloadConst.BYTE_CAPACITY] = spec.size
        if isinstance(spec.pool_id, int):
            payload[VolumePayloadConst.POOL_ID] = spec.pool_id
        if spec.lun:
            payload[VolumePayloadConst.LDEV] = spec.lun
        if spec.capacity_saving:
            payload[VolumePayloadConst.ADR_SETTING] = spec.capacity_saving
            if self.is_pegasus:
                if spec.capacity_saving.lower() != VolumePayloadConst.DISABLED and spec.pool_id is not None:
                    self.logger.writeDebug(f"is spec.data_reduction_share : {spec.data_reduction_share}")
                    is_true = True if spec.data_reduction_share is None else spec.data_reduction_share
                    self.logger.writeDebug(f"is true: {is_true}")

                    payload[VolumePayloadConst.IS_DATA_REDUCTION_SHARED_VOLUME_ENABLED] = is_true
            else:
                payload[VolumePayloadConst.IS_DATA_REDUCTION_SHARED_VOLUME_ENABLED] = spec.data_reduction_share
        if spec.parity_group:
            payload[VolumePayloadConst.PARITY_GROUP] = spec.parity_group

        end_point = self.end_points.POST_LDEVS
        self.logger.writeDebug(f"Payload for creating volume: {payload}")
        url = self.rest_api.post(end_point, payload)

        # Split the ldevid from url
        return url.split("/")[-1]

    @log_entry_exit
    def delete_volume(self, ldev_id, force_execute):
        payload = None
        if force_execute is not None:
            payload =  {
                    VolumePayloadConst.IS_DATA_REDUCTION_DELETE_FORCE_EXECUTE: force_execute
                    }
        end_point = self.end_points.DELETE_LDEVS.format(ldev_id)
        return self.rest_api.delete(end_point,data=payload)

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
            payload[VolumePayloadConst.PARAMS][VolumePayloadConst.ENHANCED_EXPANSION] = True
        end_point = self.end_points.POST_EXPAND_LDEV.format(ldev_id)
        return self.rest_api.post(end_point, payload)
    
    @log_entry_exit
    def format_volume(self, ldev_id, force_format:bool):

        payload = {
            VolumePayloadConst.PARAMS: {
                VolumePayloadConst.OPERATION_TYPE: VolumePayloadConst.FMT,
                VolumePayloadConst.FORCE_FORMAT: force_format,

            }
        }
        end_point = self.end_points.POST_FORMAT_LDEV.format(ldev_id)
        return self.rest_api.post(end_point, payload)
    
    @log_entry_exit
    def get_storage_details(self) -> VSPStorageDevice:
        end_point = self.end_points.GET_STORAGE_INFO
        storage_info = self.rest_api.get(end_point)
        self.logger.writeDebug(f"Found storage details{storage_info}")
        storage_info =  VSPStorageDevice(**storage_info)

        pegasus_model = any(sub in storage_info.model for sub in PEGASUS_MODELS)
        self.logger.writeDebug(f"Storage Model: {storage_info.model}")
        return pegasus_model

class VSPVolumeUAIGateway:
    pass
