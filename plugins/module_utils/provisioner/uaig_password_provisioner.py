try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes

except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes


class GatewayPasswordProvisioner:

    def __init__(self, connectionInfo):

        self.gateway = GatewayFactory.get_gateway(
            connectionInfo, GatewayClassTypes.UAIG_PASSWORD
        )

    def gateway_password(self, password, user):

        self.gateway.gateway_password(password, user)
        return "Sucessfully updated admin password"

    def get_admin_user(self):
        return self.gateway.get_admin_user()
