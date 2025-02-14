try:
    from ..common.uaig_constants import Endpoints
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..common.hv_constants import CommonConstants
    from .gateway_manager import UAIGConnectionManager
except ImportError:
    from common.uaig_constants import Endpoints
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from common.hv_constants import CommonConstants
    from .gateway_manager import UAIGConnectionManager

logger = Log()


class SubscriberResourceUAIGateway:

    def __init__(self, connection_info):

        self.connectionManager = UAIGConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )

    @log_entry_exit
    def get_subscriber_resource_facts(self, subscriber_id):

        end_point = Endpoints.GET_SUBSCRIBER_RESOURCES.format(
            CommonConstants.PARTNER_ID, subscriber_id
        )
        data = self.connectionManager.get(end_point)

        logger.writeDebug("Response={}", data)
        return data

    @log_entry_exit
    def get_device_by_id(self, device_id):

        end_point = Endpoints.GET_STORAGE_DEVICE_BY_ID.format(device_id)
        data = self.connectionManager.get(end_point)

        logger.writeDebug("Response={}", data)
        return data["data"]
