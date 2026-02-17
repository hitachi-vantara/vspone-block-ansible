try:
    from ..common.ansible_common import (
        log_entry_exit,
    )
    from ..common.hv_log import Log
    from ..provisioner.vsp_snapshot_family_provisioner import (
        VSPSnapshotFamilyProvisioner,
    )
    from ..message.vsp_vclone_msgs import VSPVcloneValidateMsg
except ImportError:
    from common.ansible_common import (
        log_entry_exit,
    )
    from common.hv_log import Log
    from provisioner.vsp_snapshot_family_provisioner import VSPSnapshotFamilyProvisioner
    from message.vsp_vclone_msgs import VSPVcloneValidateMsg

logger = Log()


class VSPSnapshotFamilyReconciler:
    def __init__(self, connection_info, serial=None):

        self.connection_info = connection_info
        self.provisioner = VSPSnapshotFamilyProvisioner(connection_info, serial)
        self.storage_serial_number = serial

    @log_entry_exit
    def get_snapshot_family_facts(self, spec=None):
        is_vclone_supported = self.provisioner.is_vclone_supported()
        if not is_vclone_supported:
            raise ValueError(VSPVcloneValidateMsg.NOT_SUPPORTED_ON_THIS_STORAGE.value)

        snapshots = self.provisioner.get_snapshot_family(spec.ldev_id)
        logger.writeDebug("RC:get_snapshot_family_facts:snapshots={}", snapshots)
        return snapshots
