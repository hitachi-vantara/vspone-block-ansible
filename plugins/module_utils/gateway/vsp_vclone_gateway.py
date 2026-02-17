try:
    from .gateway_manager import VSPConnectionManager
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit, convert_keys_to_snake_case
    from .vsp_storage_system_gateway import VSPStorageSystemDirectGateway
except ImportError:
    from .gateway_manager import VSPConnectionManager
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit, convert_keys_to_snake_case
    from .vsp_storage_system_gateway import VSPStorageSystemDirectGateway

GET_VCLONE_PARENT_VOLUMES = "v1/objects/virtual-clone-parent-volumes"
logger = Log()


class VSPVcloneGateway:

    def __init__(self, connection_info):
        self.connection_manager = VSPConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )
        self.connection_info = connection_info
        self.serial = None
        self.pegasus_model = None

    @log_entry_exit
    def set_serial(self, serial):
        self.serial = serial

    @log_entry_exit
    def is_vclone_supported(self):
        storage_gw = VSPStorageSystemDirectGateway(self.connection_info)
        return storage_gw.is_vclone_supported()

    @log_entry_exit
    def get_vclone_parent_volumes(self):
        """Get Vclone Parent Volumes"""
        end_point = GET_VCLONE_PARENT_VOLUMES
        response = self.connection_manager.get(end_point)
        vclone_parent_volumes = response.get("data", [])
        logger.writeDebug(
            f"GATEWAY:get_vclone_parent_volumes:vclone_parent_volumes: {vclone_parent_volumes}"
        )
        converted = convert_keys_to_snake_case(vclone_parent_volumes)
        return converted
