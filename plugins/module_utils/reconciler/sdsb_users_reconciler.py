try:
    from ..provisioner.sdsb_users_provisioner import SDSBUsersProvisioner
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..common.hv_constants import StateValue
except ImportError:
    from ..provisioner.sdsb_users_provisioner import SDSBUsersProvisioner
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from common.hv_constants import StateValue

logger = Log()


class SDSBUsersReconciler:

    def __init__(self, connection_info):
        self.connection_info = connection_info
        self.provisioner = SDSBUsersProvisioner(self.connection_info)

    @log_entry_exit
    def get_users(self, spec=None):
        return self.provisioner.get_users(spec)

    @log_entry_exit
    def reconcile_user(self, spec, state=None):

        if state == StateValue.PRESENT:
            user = self.get_users(spec)
            if user is not None:
                return user
            else:
                logger.writeDebug("User not found, creating new user: {}", spec.user_id)
                self.connection_info.changed = True
                return self.provisioner.create_user(spec)
        elif state == StateValue.UPDATE:
            user = self.get_users(spec)
            if user is not None:
                logger.writeDebug("User found, updating user: {}", spec.user_id)
                self.connection_info.changed = True
                return self.provisioner.update_user(spec)
            else:
                logger.writeDebug("User not found, cannot update: {}", spec.user_id)
                # After deploying the cluster first time, admin user is not returned
                # by the get users, but update password rest api call works
                if spec.user_id == "admin":
                    return self.provisioner.update_user(spec)
                else:
                    raise ValueError(
                        f"User {spec.user_id} not found for updating password."
                    )
