try:
    from ..common.sdsb_constants import SDSBlockEndpoints
    from .gateway_manager import SDSBConnectionManager
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..common.sdsb_utils import convert_keys_to_snake_case

except ImportError:
    from common.sdsb_constants import SDSBlockEndpoints
    from .gateway_manager import SDSBConnectionManager
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from common.sdsb_utils import convert_keys_to_snake_case

logger = Log()


class SDSBBlockClusterInformationDirectGateway:

    def __init__(self, connection_info):
        self.connection_manager = SDSBConnectionManager(
            connection_info.address, connection_info.username, connection_info.password
        )

    @log_entry_exit
    def get_storage_time_settings(self):

        # logger.writeDebug("GW:get_chap_users:spec={}", spec)
        end_point = SDSBlockEndpoints.GET_STORAGE_TIME_SETTINGS

        time = self.connection_manager.get(end_point)
        logger.writeDebug("GW:get_drives:data={}", time)

        converted = convert_keys_to_snake_case(time)
        return converted

    @log_entry_exit
    def get_storage_network_settings(self):

        # logger.writeDebug("GW:get_chap_users:spec={}", spec)
        end_point = SDSBlockEndpoints.GET_STORAGE_NETWORK_SETTING

        settings = self.connection_manager.get(end_point)
        logger.writeDebug("GW:get_drives:data={}", settings)

        converted = convert_keys_to_snake_case(settings)
        return converted

    @log_entry_exit
    def get_protection_domain_settings(self):

        # logger.writeDebug("GW:get_chap_users:spec={}", spec)
        end_point = SDSBlockEndpoints.GET_PROCTECTION_DOMAINS

        settings = self.connection_manager.get(end_point)
        logger.writeDebug("GW:get_drives:data={}", settings)

        converted = convert_keys_to_snake_case(settings)
        return converted
