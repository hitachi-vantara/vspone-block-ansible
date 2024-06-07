import time

try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes

except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes


class SubscriberProvisioner:

    def __init__(self, connectionInfo):

        self.gateway = GatewayFactory.get_gateway(
            connectionInfo, GatewayClassTypes.UAIG_SUBSCRIBER
        )

    def get_subscriber_facts(self, subscriberId):

        return self.gateway.get_subscriber_facts(subscriberId)

    def create_subscriber(self, request):

        self.gateway.create_subscriber(request)
        time.sleep(5)
        subscriber_data = self.gateway.get_subscriber_facts(request["subscriberId"])
        return subscriber_data

    def update_subscriber(self, request):

        self.gateway.update_subscriber(request)
        time.sleep(5)
        subscriber_data = self.gateway.get_subscriber_facts(request["subscriberId"])
        return subscriber_data

    def delete_subscriber(self, subscriberId):

        return self.gateway.delete_subscriber(subscriberId)
