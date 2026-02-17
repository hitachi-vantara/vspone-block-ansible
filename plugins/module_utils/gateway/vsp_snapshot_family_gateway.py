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

GET_SNAPSHOT_FAMILY = "v1/objects/snapshot-family?ldevId={}"
logger = Log()


class VSPSnapshotFamilyGateway:

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
    def get_snapshot_family(self, ldev_id):
        """Get Snapshot Family"""
        try:
            end_point = GET_SNAPSHOT_FAMILY.format(ldev_id)
            response = self.connection_manager.get(end_point)
            snapshot_family = response.get("data", [])
            logger.writeDebug(
                f"GATEWAY:get_snapshot_family:snapshot_family: {snapshot_family}"
            )
            converted = convert_keys_to_snake_case(snapshot_family)
            return converted
        except Exception as e:
            logger.writeException(e)
            return []
