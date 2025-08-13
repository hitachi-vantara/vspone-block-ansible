try:
    from .gateway_manager import SDSBConnectionManager
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit

except ImportError:
    from .gateway_manager import SDSBConnectionManager
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit

DOWNLOAD_CONFIG_FILE = "v1/objects/configuration-file/download"
CREATE_CONFIG_FILE = "v1/objects/configuration-file/actions/create/invoke"
ADD_STORAGE_NODE = "v1/objects/storage-nodes"
DELETE_STORAGE_NODE = "v1/objects/storage-nodes/{}"

logger = Log()

export_file_type_map = {
    "normal": "Normal",
    "add_storage_nodes": "AddStorageNodes",
    "replace_storage_nodes": "ReplaceStorageNode",
    "add_drives": "AddDrives",
    "replace_drives": "ReplaceDrive",
}


class SDSBClusterGateway:

    def __init__(self, connection_info):
        self.connection_manager = SDSBConnectionManager(
            connection_info.address, connection_info.username, connection_info.password
        )

    def create_config_file(self, export_file_type):
        end_point = CREATE_CONFIG_FILE
        payload = {"exportFileType": export_file_type_map[export_file_type]}
        resp = self.connection_manager.post(end_point, data=payload)
        logger.writeDebug(f"GW:create_config_file:resp={resp}")
        return

    @log_entry_exit
    def download_config_file(self, file_name):
        end_point = DOWNLOAD_CONFIG_FILE
        resp = self.connection_manager.download_file(end_point)
        # logger.writeDebug(f"GW:download_config_file:resp={resp}")
        with open(file_name, mode="wb") as file:
            file.write(resp)
        return

    @log_entry_exit
    def add_storage_node(self, config_file, setup_user_password):
        logger.writeDebug(
            f"GW:add_storage_node:config_file={config_file}, setup_user_password={setup_user_password}"
        )
        end_point = ADD_STORAGE_NODE
        resp = self.connection_manager.add_storage_node(
            end_point, config_file, setup_user_password
        )

        return resp

    @log_entry_exit
    def remove_storage_node(self, id):
        end_point = DELETE_STORAGE_NODE.format(id)
        resp = self.connection_manager.remove_storage_node(end_point)

        return resp
