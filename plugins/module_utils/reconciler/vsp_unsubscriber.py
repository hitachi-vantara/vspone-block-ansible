try:
    from ..common.ansible_common import (
        log_entry_exit,
    )
    from ..common.hv_log import Log
    from ..provisioner.vsp_unsubscribe_provisioner import VSPUnsubscribeProvisioner

except ImportError:
    from common.ansible_common import (
        log_entry_exit,
    )
    from common.hv_log import Log
    from provisioner.vsp_unsubscribe_provisioner import VSPUnsubscribeProvisioner


logger = Log()


class VSPUnsubscriberReconciler:
    def __init__(self, connection_info, serial, state=None):

        self.connection_info = connection_info
        self.storage_serial_number = serial
        self.provisioner = VSPUnsubscribeProvisioner(connection_info, serial)
        if state:
            self.state = state

    @log_entry_exit
    def check_storage_in_ucpsystem(self) -> bool:
        """
        Check if the storage is in the UCP system.
        """
        return self.provisioner.check_storage_in_ucpsystem()

    @log_entry_exit
    def unsubscribe(self, spec):
        return self.provisioner.unsubscribe(spec)
        # self.provisioner.
