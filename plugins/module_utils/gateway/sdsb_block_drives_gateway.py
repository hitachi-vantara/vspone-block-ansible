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


class SDSBBlockDrivesDirectGateway:

    def __init__(self, connection_info):
        self.connection_manager = SDSBConnectionManager(
            connection_info.address, connection_info.username, connection_info.password
        )

    @log_entry_exit
    def get_drives(self, spec=None):
        end_point = SDSBlockEndpoints.GET_BLOCK_DRIVES

        # Build query based on provided parameters
        params = {}
        if spec.status_summary:
            params["statusSummary"] = spec.status_summary
        if spec.status:
            params["status"] = spec.status
        if spec.storage_node_id:
            params["storageNodeId"] = spec.storage_node_id
        if spec.locator_led_status:
            params["locatorLedStatus"] = spec.locator_led_status

        # Construct query string
        if params:
            query_parts = ["{}={}".format(k, v) for k, v in params.items()]
            end_point = end_point + "?" + "&".join(query_parts)

        logger.writeDebug("GW:get_drives:end_point={}", end_point)
        drives = self.connection_manager.get(end_point)
        logger.writeDebug("GW:get_drives:data={}", drives)

        converted = convert_keys_to_snake_case(drives)
        return converted
