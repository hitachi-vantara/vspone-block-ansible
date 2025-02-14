try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes
    from ..common.ansible_common import log_entry_exit
    from ..common.hv_log import Log

except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes
    from common.ansible_common import log_entry_exit
    from common.hv_log import Log

logger = Log()


class SubscriberResourceProvisioner:

    def __init__(self, connectionInfo):

        self.gateway = GatewayFactory.get_gateway(
            connectionInfo, GatewayClassTypes.UAIG_SUBSCRIBER_RESOURCE
        )

    @log_entry_exit
    def get_subscriber_resource_facts(self, subscriberId):
        data = self.gateway.get_subscriber_resource_facts(subscriberId)
        data = self.replace_device_id_with_serial(data)
        return data

    @log_entry_exit
    def replace_device_id_with_serial(self, data):
        dev_id_to_serial_map = {}

        for item in data:
            if item["deviceId"] in dev_id_to_serial_map.keys():
                item["deviceId"] = dev_id_to_serial_map["deviceId"]
            else:
                device_id = item["deviceId"]
                device_info = self.gateway.get_device_by_id(device_id)
                dev_id_to_serial_map["deviceId"] = device_info["serialNumber"]
                item["deviceId"] = device_info["serialNumber"]

        return data
