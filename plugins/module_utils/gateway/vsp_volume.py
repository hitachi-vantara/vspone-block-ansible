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
    from ..common.ansible_common import log_entry_exit
except ImportError:
    from common.ansible_common import log_entry_exit
    from common.vsp_constants import Endpoints, VolumePayloadConst, AutomationConstants
    from common.ansible_common import dicts_to_dataclass_list
    from model.vsp_volume_models import VSPVolumesInfo, VSPVolumeInfo, CreateVolumeSpec


class VSPVolumeDirectGateway:
    """
    VSPVolumeDirectGateway
    """

    def __init__(self, connection_info):

        self.rest_api = VSPConnectionManager(
            connection_info.address, connection_info.username, connection_info.password
        )
        self.end_points = Endpoints

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
        return VSPVolumeInfo(**vol_data)

    @log_entry_exit
    def create_volume(self, spec: CreateVolumeSpec):
        payload = {}
        payload[VolumePayloadConst.BYTE_CAPACITY] = spec.size
        if isinstance(spec.pool_id, int):
            payload[VolumePayloadConst.POOL_ID] = spec.pool_id
        if spec.lun:
            payload[VolumePayloadConst.LDEV] = spec.lun
        if spec.capacity_saving:
            payload[VolumePayloadConst.ADR_SETTING] = spec.capacity_saving
        if spec.parity_group:
            payload[VolumePayloadConst.PARITY_GROUP] = spec.parity_group

        end_point = self.end_points.POST_LDEVS
        url = self.rest_api.post(end_point, payload)

        # Split the ldevid from url
        return url.split("/")[-1]

    @log_entry_exit
    def delete_volume(self, ldev_id):

        end_point = self.end_points.DELETE_LDEVS.format(ldev_id)
        return self.rest_api.delete(end_point)

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
    def expand_volume(self, ldev_id, additional_capacity):

        payload = {
            VolumePayloadConst.PARAMS: {
                VolumePayloadConst.ADDITIONAL_BLOCK_CAPACITY: round(additional_capacity)
            }
        }
        end_point = self.end_points.POST_EXPAND_LDEV.format(ldev_id)
        return self.rest_api.post(end_point, payload)


class VSPVolumeUAIGateway:
    pass
