try:
    from ..provisioner.sdsb_block_drives_provisioner import SDSBBlockDrivesProvisioner
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
except ImportError:
    from ..provisioner.sdsb_block_drives_provisioner import SDSBBlockDrivesProvisioner
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit

logger = Log()


class SDSBBlockDrivesReconciler:

    def __init__(self, connection_info):
        self.connection_info = connection_info
        self.provisioner = SDSBBlockDrivesProvisioner(self.connection_info)

    @log_entry_exit
    def get_drives(self, spec=None):
        return self.provisioner.get_drives(spec)
