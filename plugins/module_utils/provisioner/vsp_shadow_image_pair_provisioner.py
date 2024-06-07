import time

try:
    from ..common.ansible_common import log_entry_exit
    from ..gateway.gateway_factory import GatewayFactory
    from ..gateway.vsp_shadow_image_pair_gateway import VSPShadowImagePairUAIGateway
    from ..common.hv_constants import GatewayClassTypes
    from ..model.vsp_shadow_image_pair_models import *
    from ..common.ansible_common import dicts_to_dataclass_list
except ImportError:
    from common.ansible_common import log_entry_exit
    from gateway.vsp_shadow_image_pair_gateway import VSPShadowImagePairUAIGateway
    from common.hv_constants import GatewayClassTypes
    from gateway.gateway_factory import GatewayFactory
    from model.vsp_shadow_image_pair_models import *
    from common.ansible_common import dicts_to_dataclass_list


class VSPShadowImagePairProvisioner:

    def __init__(self, connection_info):
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_SHADOW_IMAGE_PAIR
        )

    @log_entry_exit
    def get_all_shadow_image_pairs(self, serial, pvol):
        if pvol is not None:
            shadow_image_pairs = self.get_shadow_image_pair_by_pvol_and_svol(
                serial, pvol
            )
        else:
            shadow_image_pairs = self.gateway.get_all_shadow_image_pairs(serial)
        

        return shadow_image_pairs.data_to_list()

    @log_entry_exit
    def create_shadow_image_pair(self, serial, createShadowImagePairSpec):
        pairId = self.gateway.create_shadow_image_pair(
            serial, createShadowImagePairSpec
        )
        time.sleep(20)
        shadow_image_pair = self.gateway.get_shadow_image_pair_by_id(serial, pairId)
        if isinstance(shadow_image_pair,dict):
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
            shadow_image_pairs = self.gateway.get_shadow_image_pair_by_pvol(serial,pvol)
        shadow_image_list = []        
        shadow_image_pair = None
        for sip in shadow_image_pairs.data_to_list():
            print("pvol = "+str(pvol))
            if sip.get("primaryVolumeId") == pvol:
                shadow_image_list.append(sip)
            if svol is not None:
                if sip.get("secondaryVolumeId") == svol:
                    shadow_image_pair = sip
                    return shadow_image_pair
        
        return VSPShadowImagePairsInfo(dicts_to_dataclass_list(shadow_image_list, VSPShadowImagePairInfo))
        

    @log_entry_exit
    def split_shadow_image_pair(self, serial, updateShadowImagePairSpec):
        response = self.gateway.split_shadow_image_pair(
            serial, updateShadowImagePairSpec
        )
        time.sleep(20)
        shadow_image_pair = self.gateway.get_shadow_image_pair_by_id(
            serial, updateShadowImagePairSpec.pair_id
        )
        if isinstance(shadow_image_pair,dict):
            return shadow_image_pair
        return shadow_image_pair.to_dict()

    @log_entry_exit
    def resync_shadow_image_pair(self, serial, updateShadowImagePairSpec):
        response = self.gateway.resync_shadow_image_pair(
            serial, updateShadowImagePairSpec
        )
        time.sleep(20)
        shadow_image_pair = self.gateway.get_shadow_image_pair_by_id(
            serial, updateShadowImagePairSpec.pair_id
        )
        if isinstance(shadow_image_pair,dict):
            return shadow_image_pair
        return shadow_image_pair.to_dict()

    @log_entry_exit
    def restore_shadow_image_pair(self, serial, updateShadowImagePairSpec):
        response = self.gateway.restore_shadow_image_pair(
            serial, updateShadowImagePairSpec
        )
        time.sleep(20)
        shadow_image_pair = self.gateway.get_shadow_image_pair_by_id(
            serial, updateShadowImagePairSpec.pair_id
        )
        if isinstance(shadow_image_pair,dict):
            return shadow_image_pair
        return shadow_image_pair.to_dict()

    @log_entry_exit
    def delete_shadow_image_pair(self, serial, deleteShadowImagePairSpec):
        response = self.gateway.delete_shadow_image_pair(
            serial, deleteShadowImagePairSpec
        )
        return "Shadow image pair is deleted."
