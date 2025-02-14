try:
    from .gateway_manager import VSPConnectionManager, UAIGConnectionManager
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
except ImportError:
    from .gateway_manager import VSPConnectionManager, UAIGConnectionManager
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit

GET_CONFIG_PROPERTY = "v2/common/config/property/{}"

logger = Log()


class VSPConfigMapUAIGateway:

    def __init__(self, connection_info):

        self.connection_manager = UAIGConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )
        self.connection_info = connection_info

    @log_entry_exit
    def set_storage_serial_number(self, serial: str):
        self.storage_serial_number = serial

    @log_entry_exit
    def is_out_of_band(self):
        end_point = GET_CONFIG_PROPERTY.format("outofband")
        data = self.connection_manager.get(end_point)
        logger.writeDebug("GW:is_out_of_band:data={} oob = {}", data, data["data"])
        oob = data["data"]
        if oob == "false":
            return False
        else:
            return True


class VSPConfigMapDirectGateway:
    def __init__(self, connection_info):
        self.connection_manager = VSPConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )
        self.connection_info = connection_info
