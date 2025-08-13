try:
    from ..provisioner.sdsb_storage_controller_provisioner import (
        SDSBStorageControllerProvisioner,
    )
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
except ImportError:
    from ..provisioner.sdsb_storage_controller_provisioner import (
        SDSBStorageControllerProvisioner,
    )
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit

logger = Log()


class SDSBStorageControllerReconciler:

    def __init__(self, connection_info):
        self.connection_info = connection_info
        self.provisioner = SDSBStorageControllerProvisioner(self.connection_info)

    @log_entry_exit
    def get_storage_controllers(self, spec=None):
        return self.provisioner.get_storage_controllers(spec)
