try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes
    from ..common.ansible_common import log_entry_exit

except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes
    from common.ansible_common import log_entry_exit


class SDSBUsersProvisioner:

    def __init__(self, connection_info):

        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.SDSB_USER
        )

    @log_entry_exit
    def get_users(self, spec=None):
        users = self.gateway.get_users(spec)
        return users

    @log_entry_exit
    def create_user(self, spec=None):
        user = self.gateway.create_user(spec)
        return user

    @log_entry_exit
    def update_user(self, spec=None):
        user = self.gateway.update_user(spec)
        return user
