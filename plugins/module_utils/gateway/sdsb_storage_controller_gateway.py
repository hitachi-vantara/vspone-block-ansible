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


class SDSBStorageControllerDirectGateway:

    def __init__(self, connection_info):
        self.connection_manager = SDSBConnectionManager(
            connection_info.address, connection_info.username, connection_info.password
        )

    @log_entry_exit
    def get_storage_controllers(self, spec=None):

        # logger.writeDebug("GW:get_chap_users:spec={}", spec)
        end_point = SDSBlockEndpoints.GET_STORAGE_CONTROLLERS

        if spec is not None:
            if spec.id:
                end_point = SDSBlockEndpoints.GET_STORAGE_CONTROLLERS_ID.format(spec.id)
                logger.writeDebug("GW:get_storage_controllers:end_point={}", end_point)

        storage_controller = self.connection_manager.get(end_point)
        logger.writeDebug("GW:get_storage_controllers:data={}", storage_controller)

        converted = convert_keys_to_snake_case(storage_controller)
        logger.writeDebug("GW:get_storage_controllers:converted={}", storage_controller)
        return converted
