try:
    from ..provisioner.uaig_auth_token_provisioner import UAIGAuthTokenProvisioner
    from ..common.hv_log import Log
except ImportError:
    from provisioner.uaig_auth_token_provisioner import UAIGAuthTokenProvisioner
    from common.hv_log import Log

logger = Log()


class UAIGAuthTokenReconciler:

    def __init__(self, connectionInfo):
        self.connectionInfo = connectionInfo
        self.provisioner = UAIGAuthTokenProvisioner(self.connectionInfo)

    def get_auth_token(self):
        return self.provisioner.get_auth_token()
