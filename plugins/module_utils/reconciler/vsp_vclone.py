try:
    from ..common.ansible_common import (
        log_entry_exit,
    )
    from ..common.hv_log import Log
    from ..provisioner.vsp_vclone_provisioner import VSPVcloneProvisioner
    from ..provisioner.vsp_volume_prov import VSPVolumeProvisioner
    from ..message.vsp_vclone_msgs import VSPVcloneValidateMsg
except ImportError:
    from common.ansible_common import (
        log_entry_exit,
    )
    from common.hv_log import Log
    from provisioner.vsp_vclone_provisioner import VSPVcloneProvisioner
    from message.vsp_vclone_msgs import VSPVcloneValidateMsg

logger = Log()


class VSPVcloneReconciler:
    def __init__(self, connection_info, serial=None):

        self.connection_info = connection_info
        self.provisioner = VSPVcloneProvisioner(connection_info, serial)
        self.storage_serial_number = serial
        self.vol_prov = VSPVolumeProvisioner(
            self.connection_info, self.storage_serial_number
        )

    @log_entry_exit
    def get_vclone_parent_volume_facts(self, spec=None):
        is_vclone_supported = self.provisioner.is_vclone_supported()
        if not is_vclone_supported:
            raise ValueError(VSPVcloneValidateMsg.NOT_SUPPORTED_ON_THIS_STORAGE.value)
        if spec is None:
            vclone_parent_volumes = self.provisioner.get_vclone_parent_volumes()
            return vclone_parent_volumes
        else:
            if spec.vclone_volume_id:
                volume = self.vol_prov.get_volume_by_ldev(spec.vclone_volume_id)
                logger.writeDebug("RC:get_vclone_parent_volume_facts:volume={}", volume)
                if volume.parentLdevId:
                    return [{"ldev_id": volume.parentLdevId}]
            return []

    @log_entry_exit
    def reconcile_vclone(self, spec):
        pass
