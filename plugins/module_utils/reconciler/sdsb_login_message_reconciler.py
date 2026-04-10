try:
    from ..provisioner.sdsb_login_message_provisioner import SDSBLoginMessageProvisioner
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..message.sdsb_login_message_msg import SDSBLoginMessageValidationMsg
except ImportError:
    from provisioner.sdsb_login_message_provisioner import SDSBLoginMessageProvisioner
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from message.sdsb_login_message_msg import SDSBLoginMessageValidationMsg

logger = Log()


class SDSBLoginMessageReconciler:

    def __init__(self, connection_info):
        self.connection_info = connection_info
        self.provisioner = SDSBLoginMessageProvisioner(self.connection_info)

    @log_entry_exit
    def get_login_message(self):
        return self.provisioner.get_login_message()

    @log_entry_exit
    def update_login_message(self, spec, state=None):
        if state == "present":
            return self.provisioner.update_login_message(spec)
        else:
            raise ValueError(
                SDSBLoginMessageValidationMsg.UNSUPPORTED_STATE.value.format(state)
            )
