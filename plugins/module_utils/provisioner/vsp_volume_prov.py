try:
    from ..common.ansible_common import log_entry_exit
    from ..common.hv_constants import GatewayClassTypes
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.vsp_constants import  VolumePayloadConst
except ImportError:
    from common.ansible_common import log_entry_exit
    from common.hv_constants import GatewayClassTypes
    from gateway.gateway_factory import GatewayFactory
    from common.vsp_constants import  VolumePayloadConst



class VSPVolumeProvisioner:

    def __init__(self, connection_info):
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_VOLUME
        )

    @log_entry_exit
    def get_volumes(self, start_ldev=None, count=None):

        count = 0 if not count else int(count)
        start_ldev = 0 if not start_ldev else int(start_ldev)
        return self.gateway.get_volumes(start_ldev=start_ldev, count=count)

    @log_entry_exit
    def get_volume_by_ldev(self, ldev):

        return self.gateway.get_volume_by_id(ldev)

    @log_entry_exit
    def delete_volume(self, ldev, force_execute):

        return self.gateway.delete_volume(ldev, force_execute)

    @log_entry_exit
    def create_volume(self, spec):
        vol_id =  self.gateway.create_volume(spec)

        vol_info = self.get_volume_by_ldev(vol_id)
        if vol_info.status == VolumePayloadConst.BLOCK:
            force_format = True if vol_info.dataReductionMode and vol_info.dataReductionMode.lower() != VolumePayloadConst.DISABLED else  False
            self.gateway.format_volume(vol_id , force_format)
        return vol_id

    @log_entry_exit
    def expand_volume_capacity(self, ldev_id, payload, enhanced_expansion):

        return self.gateway.expand_volume(ldev_id, payload, enhanced_expansion)
    
    @log_entry_exit
    def format_volume(self, ldev_id, payload):

        return self.gateway.format_volume(ldev_id, payload)

    @log_entry_exit
    def change_volume_settings(self, ldev_id, name=None, adr_setting=None):

        return self.gateway.update_volume(ldev_id, name, adr_setting)
