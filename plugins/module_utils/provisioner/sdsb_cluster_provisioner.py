try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit

except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit

logger = Log()


class SDSBClusterProvisioner:

    def __init__(self, connection_info):

        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.SDSB_CLUSTER
        )

    @log_entry_exit
    def download_config_file(self, file_name):
        return self.gateway.download_config_file(file_name)

    @log_entry_exit
    def add_storage_node(self, config_file, setup_user_password):
        return self.gateway.add_storage_node(config_file, setup_user_password)

    @log_entry_exit
    def remove_storage_node(self, id):
        return self.gateway.remove_storage_node(id)
