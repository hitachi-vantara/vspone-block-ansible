try:
    from ..provisioner.uaig_auth_token_provisioner import UAIGAuthTokenProvisioner
    from ..common.hv_constants import StateValue
    from ..common.hv_log import Log
    from ..model.sdsb_chap_user_models import *
except ImportError:
    from provisioner.uaig_auth_token_provisioner import UAIGAuthTokenProvisioner
    from common.hv_constants import StateValue
    from common.hv_log import Log
    from model.sdsb_chap_user_models import *

logger = Log()


class UAIGAuthTokenReconciler:

    def __init__(self, connectionInfo):
        self.connectionInfo = connectionInfo
        self.provisioner = UAIGAuthTokenProvisioner(self.connectionInfo)

    def get_auth_token(self):
        return self.provisioner.get_auth_token()

