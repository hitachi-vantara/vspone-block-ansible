try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..gateway.sdsb_platform_info_gateway import SDSBPlatformInfoGateway
    from ..common.hv_constants import GatewayClassTypes
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit

except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from gateway.sdsb_platform_info_gateway import SDSBPlatformInfoGateway
    from common.hv_constants import GatewayClassTypes
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit

logger = Log()


class SDSBClusterProvisioner:

    def __init__(self, connection_info):

        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.SDSB_CLUSTER
        )
        self.connection_info = connection_info

    @log_entry_exit
    def create_config_file(self, export_file_type):
        return self.gateway.create_config_file(export_file_type)

    @log_entry_exit
    def download_config_file(self, file_name):
        return self.gateway.download_config_file(file_name)

    @log_entry_exit
    def add_storage_node(self, config_file, setup_user_password):
        return self.gateway.add_storage_node(config_file, setup_user_password)

    @log_entry_exit
    def remove_storage_node(self, id):
        return self.gateway.remove_storage_node(id)

    @log_entry_exit
    def get_storage_time_settings(self):
        return self.gateway.get_storage_time_settings()

    @log_entry_exit
    def get_platform(self):
        platform_gw = SDSBPlatformInfoGateway(self.connection_info)
        return platform_gw.get_platform()
