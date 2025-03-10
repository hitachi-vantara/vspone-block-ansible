import time

try:
    from ..common.ansible_common import log_entry_exit
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes, ConnectionTypes
    from ..common.hv_log import Log
    from ..model.vsp_shadow_image_pair_models import (
        VSPShadowImagePairsInfo,
        VSPShadowImagePairInfo,
    )
    from ..common.ansible_common import dicts_to_dataclass_list
    from ..common.vsp_constants import VolumePayloadConst, PairStatus
    from .vsp_volume_prov import VSPVolumeProvisioner
    from ..message.vsp_shadow_image_pair_msgs import VSPShadowImagePairValidateMsg

except ImportError:
    from common.ansible_common import log_entry_exit
    from common.hv_constants import GatewayClassTypes, ConnectionTypes
    from common.hv_log import Log
    from gateway.gateway_factory import GatewayFactory
    from model.vsp_shadow_image_pair_models import (
        VSPShadowImagePairsInfo,
        VSPShadowImagePairInfo,
    )
    from common.ansible_common import dicts_to_dataclass_list
    from .vsp_volume_prov import VSPVolumeProvisioner
    from common.vsp_constants import VolumePayloadConst, PairStatus
    from message.vsp_shadow_image_pair_msgs import VSPShadowImagePairValidateMsg

logger = Log()


class VSPShadowImagePairProvisioner:

    def __init__(self, connection_info):
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_SHADOW_IMAGE_PAIR
        )
        self.connection_info = connection_info
        self.config_gw = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_CONFIG_MAP
        )
        if self.connection_info.connection_type == ConnectionTypes.DIRECT:
            #  20240820 for direct only
            self.vol_provisioner = VSPVolumeProvisioner(connection_info)

    @log_entry_exit
    def get_all_shadow_image_pairs(self, serial, pvol):
        if pvol is not None:
            shadow_image_pairs = self.get_shadow_image_pair_by_pvol_and_svol(
                serial, pvol
            )
        else:
            shadow_image_pairs = self.gateway.get_all_shadow_image_pairs(serial)
            shadow_image_pairs = shadow_image_pairs.data_to_list()

        return shadow_image_pairs

    @log_entry_exit
    def create_shadow_image_pair(self, serial, createShadowImagePairSpec):

        if self.connection_info.connection_type == ConnectionTypes.DIRECT:
            #  20240820 for direct only
            pvol = self.vol_provisioner.get_volume_by_ldev(
                createShadowImagePairSpec.pvol
            )
            if pvol.emulationType == VolumePayloadConst.NOT_DEFINED:
                err_msg = VSPShadowImagePairValidateMsg.PVOL_NOT_FOUND.value
                logger.writeError(err_msg)
                raise ValueError(err_msg)

            createShadowImagePairSpec.is_data_reduction_force_copy = (
                True
                if pvol.dataReductionMode
                and pvol.dataReductionMode != VolumePayloadConst.DISABLED
                else False
            )

        pairId = self.gateway.create_shadow_image_pair(
            serial, createShadowImagePairSpec
        )
        time.sleep(20)
        shadow_image_pair = self.gateway.get_shadow_image_pair_by_id(serial, pairId)
        if isinstance(shadow_image_pair, dict):
            return shadow_image_pair
        return shadow_image_pair.to_dict()

    @log_entry_exit
    def get_shadow_image_pair_by_id(self, serial, pairId):

        return self.gateway.get_shadow_image_pair_by_id(serial, pairId)

    @log_entry_exit
    def get_shadow_image_pair_by_pvol_and_svol(self, serial, pvol, svol=None):
        shadow_image_pairs = None
        if pvol is None:
            shadow_image_pairs = self.gateway.get_all_shadow_image_pairs(serial)
        else:
            shadow_image_pairs = self.gateway.get_shadow_image_pair_by_pvol(
                serial, pvol
            )
        shadow_image_list = []
        shadow_image_pair = None
        for sip in shadow_image_pairs.data_to_list():
            if sip.get("primaryVolumeId") == pvol:
                shadow_image_list.append(sip)
            if svol is not None:
                if sip.get("secondaryVolumeId") == svol:
                    shadow_image_pair = sip
                    return shadow_image_pair

        if svol is not None:
            return None

        data = VSPShadowImagePairsInfo(
            dicts_to_dataclass_list(shadow_image_list, VSPShadowImagePairInfo)
        )
        return data.data_to_list()

    @log_entry_exit
    def is_out_of_band(self):
        return self.config_gw.is_out_of_band()

    @log_entry_exit
    def split_shadow_image_pair(self, serial, updateShadowImagePairSpec):
        unused = self.gateway.split_shadow_image_pair(serial, updateShadowImagePairSpec)
        return self.get_si_pair_with_latest_data(
            serial, updateShadowImagePairSpec.pair_id, PairStatus.PSUS
        )

    @log_entry_exit
    def resync_shadow_image_pair(self, serial, updateShadowImagePairSpec):
        unused = self.gateway.resync_shadow_image_pair(
            serial, updateShadowImagePairSpec
        )
        return self.get_si_pair_with_latest_data(
            serial, updateShadowImagePairSpec.pair_id, PairStatus.PAIR
        )

    @log_entry_exit
    def restore_shadow_image_pair(self, serial, updateShadowImagePairSpec):
        unused = self.gateway.restore_shadow_image_pair(
            serial, updateShadowImagePairSpec
        )

        return self.get_si_pair_with_latest_data(
            serial, updateShadowImagePairSpec.pair_id, PairStatus.PAIR
        )

    @log_entry_exit
    def get_si_pair_with_latest_data(self, serial, pair_id, type):
        pair = None
        count = 0

        while count < 10:
            pair = self.gateway.get_shadow_image_pair_by_id(serial, pair_id)

            if (
                isinstance(pair, dict)
                and pair.get("status") == type
                or pair.status == type
            ):
                return pair.to_dict()
            time.sleep(10)
            count += 1
        return pair

    @log_entry_exit
    def delete_shadow_image_pair(self, serial, deleteShadowImagePairSpec):
        unused = self.gateway.delete_shadow_image_pair(
            serial, deleteShadowImagePairSpec
        )
        return "Shadow image pair is deleted."
