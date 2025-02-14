try:
    from ..provisioner.uaig_password_provisioner import GatewayPasswordProvisioner
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
except ImportError:
    from provisioner.uaig_password_provisioner import GatewayPasswordProvisioner
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit

logger = Log()


class GatewayPasswordReconciler:

    def __init__(self, connection_info):
        self.connection_info = connection_info
        self.provisioner = GatewayPasswordProvisioner(self.connection_info)

    @log_entry_exit
    def gateway_password(self, spec):
        user = self.get_admin_user()

        logger.writeDebug("RC:gateway_password:user={}", user)
        if not user.get("id"):
            return "Missing admin user"
        else:
            logger.writeDebug(
                "RC:gateway_password:connection_info.changed={}",
                self.connection_info.changed,
            )
            ret_val = self.provisioner.gateway_password(spec.password, user)
            self.connection_info.changed = True
            logger.writeDebug(
                "RC:gateway_password:connection_info.changed={}",
                self.connection_info.changed,
            )
            return ret_val

    @log_entry_exit
    def get_admin_user(self):
        return self.provisioner.get_admin_user()
