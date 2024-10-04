from typing import Optional, List, Dict, Any
try:
    from ..common.ansible_common import (
        log_entry_exit,
        camel_to_snake_case,
        get_response_key,
        volume_id_to_hex_format,
    )
    from ..common.hv_log import Log
    from ..common.hv_constants import *
    from ..provisioner.vsp_unsubscribe_provisioner import VSPUnsubscribeProvisioner
    from ..message.vsp_true_copy_msgs import VSPTrueCopyValidateMsg
    from ..model.vsp_true_copy_models import TrueCopySpec


except ImportError:
    from common.ansible_common import (
        log_entry_exit,
        camel_to_snake_case,
        get_response_key,
        volume_id_to_hex_format,
    )
    from common.hv_log import Log
    from common.hv_constants import *
    from provisioner.vsp_unsubscribe_provisioner import VSPUnsubscribeProvisioner
    from message.vsp_true_copy_msgs import VSPTrueCopyValidateMsg
    from model.vsp_true_copy_models import TrueCopySpec


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