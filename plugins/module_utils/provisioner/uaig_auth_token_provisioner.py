try:
    from ..gateway.gateway_manager import UAIGConnectionManager
    from ..common.ansible_common import log_entry_exit

except ImportError:
    from gateway.gateway_manager import UAIGConnectionManager
    from common.ansible_common import log_entry_exit


class UAIGAuthTokenProvisioner:

    def __init__(self, connection_info):
        self.gateway = UAIGConnectionManager(
            connection_info.address, connection_info.username, connection_info.password
        )

    @log_entry_exit
    def get_auth_token(self):
        token = self.gateway.get_auth_token()
        return token
