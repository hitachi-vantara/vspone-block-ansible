from ..gateway.sdsb_dump_log_gateway import SDSBDumpLogGateway
from ..message.sdsb_dump_file_msgs import SDSBDumpFileMsg
from ..common.ansible_common import log_entry_exit


class SDSBDumpLogProvisioner:

    def __init__(self, connection_info):
        self.gateway = SDSBDumpLogGateway(connection_info)
        self.connection_info = connection_info

    @log_entry_exit
    def create_dump_file(self, spec):
        unused = self.gateway.create_dump_file(spec)
        msg = SDSBDumpFileMsg.DUMP_FILE_CREATED.value.format(spec.label)
        self.connection_info.changed = True
        return msg

    @log_entry_exit
    def download_dump_file(self, spec):
        if spec.file_path is None:
            raise ValueError(SDSBDumpFileMsg.FILE_PATH_REQD.value)
        if spec.file_name is not None:
            return self.gateway.download_dump_file_using_filename(spec)
        return self.gateway.download_dump_file(spec)

    @log_entry_exit
    def download_dump_file_using_filename(self, spec):
        return self.gateway.download_dump_file_using_filename(spec)

    @log_entry_exit
    def delete_dump_file(self, spec):

        if spec.file_name is None:
            raise ValueError(SDSBDumpFileMsg.FILE_NAME_REQD.value)

        try:
            self.gateway.delete_dump_file(spec)
            msg = SDSBDumpFileMsg.DUMP_FILE_DELETED.value.format(spec.file_name)
            self.connection_info.changed = True
            return msg
        except Exception as e:
            msg = SDSBDumpFileMsg.DUMP_FILE_NOT_FOUND.value.format(spec.file_name)
            return msg

    @log_entry_exit
    def get_all_dump_log_status(self):
        return self.gateway.get_all_dump_log_status()

    @log_entry_exit
    def get_dump_log_status(self):
        return self.gateway.get_dump_log_status()
