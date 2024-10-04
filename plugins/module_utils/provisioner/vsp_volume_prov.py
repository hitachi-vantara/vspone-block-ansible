try:
    from ..common.ansible_common import log_entry_exit
    from ..common.hv_constants import GatewayClassTypes
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.vsp_constants import  VolumePayloadConst
    from ..message.vsp_lun_msgs import VSPVolValidationMsg
    from .vsp_storage_port_provisioner import VSPStoragePortProvisioner
    from .vsp_storage_system_provisioner import VSPStorageSystemProvisioner
except ImportError:
    from common.ansible_common import log_entry_exit
    from common.hv_constants import GatewayClassTypes
    from gateway.gateway_factory import GatewayFactory
    from common.vsp_constants import  VolumePayloadConst
    from message.vsp_lun_msgs import VSPVolValidationMsg
    from .vsp_storage_port_provisioner import VSPStoragePortProvisioner
    from .vsp_storage_system_provisioner import VSPStorageSystemProvisioner


class VSPVolumeProvisioner:

    def __init__(self, connection_info):
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_VOLUME
        )
        VSPStorageSystemProvisioner(connection_info).populate_basic_storage_info()

    @log_entry_exit
    def get_volumes(self, start_ldev=None, count=None):

        count = 0 if not count else int(count)
        start_ldev = 0 if not start_ldev else int(start_ldev)
        volumes =  self.gateway.get_volumes(start_ldev=start_ldev, count=count)
        return volumes

    @log_entry_exit
    def get_volume_by_ldev(self, ldev):

        return self.gateway.get_volume_by_id(ldev)

    @log_entry_exit
    def get_volumes_by_pool_id(self, pool_id):

        return self.gateway.get_volumes_by_pool_id(pool_id)

    @log_entry_exit
    def delete_volume(self, ldev, force_execute):

        return self.gateway.delete_volume(ldev, force_execute)

    @log_entry_exit
    def delete_lun_path(self, port):

        return self.gateway.delete_lun_path(port)
    
    @log_entry_exit
    def create_volume(self, spec):
        if not spec.ldev_id:
            spec.ldev_id = self.get_free_ldev_from_meta()
        vol_id =  self.gateway.create_volume(spec)

        vol_info = self.get_volume_by_ldev(vol_id)
        if vol_info.status == VolumePayloadConst.BLOCK:
            force_format = True if vol_info.dataReductionMode and vol_info.dataReductionMode.lower() != VolumePayloadConst.DISABLED else  False
            self.gateway.format_volume(vol_id , force_format)
        return vol_id

    @log_entry_exit
    def get_free_ldev_from_meta(self):
        ldevs = self.gateway.get_free_ldev_from_meta()
        if not ldevs.data:
            raise Exception(VSPVolValidationMsg.NO_FREE_LDEV.value)
        return ldevs.data[0].ldevId
    
    @log_entry_exit
    def expand_volume_capacity(self, ldev_id, payload, enhanced_expansion):

        return self.gateway.expand_volume(ldev_id, payload, enhanced_expansion)
    
    @log_entry_exit
    def format_volume(self, ldev_id, payload):

        return self.gateway.format_volume(ldev_id, payload)

    @log_entry_exit
    def change_volume_settings(self, ldev_id, name=None, adr_setting=None):

        return self.gateway.update_volume(ldev_id, name, adr_setting)
    

    @log_entry_exit
    def get_volume_by_name(self, name):
        volumes =  self.gateway.get_simple_volumes(start_ldev=0, count=0)
        for v in volumes.data:
            if v.label  == name:
                return v
        
        return None
