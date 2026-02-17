from ..gateway.sdsb_dump_log_gateway import SDSBDumpLogGateway

from ..common.ansible_common import log_entry_exit


class SDSBDumpLogProvisioner:

    def __init__(self, connection_info):
        self.gateway = SDSBDumpLogGateway(connection_info)
        self.connection_info = connection_info

    @log_entry_exit
    def create_dump_file(self, spec):
        unused = self.gateway.create_dump_file(spec)
        msg = f"Dump file with label {spec.label} created successfully"
        self.connection_info.changed = True
        return msg

    @log_entry_exit
    def download_dump_file(self, spec):
        if spec.file_path is None:
            raise ValueError("File path is required")
        if spec.file_name is not None:
            return self.gateway.download_dump_file_using_filename(spec)
        return self.gateway.download_dump_file(spec)

    @log_entry_exit
    def download_dump_file_using_filename(self, spec):
        return self.gateway.download_dump_file_using_filename(spec)

    @log_entry_exit
    def delete_dump_file(self, spec):

        if spec.file_name is None:
            raise ValueError("File name is required")

        try:
            self.gateway.delete_dump_file(spec)
            msg = f"Dump file {spec.file_name} deleted successfully"
            self.connection_info.changed = True
            return msg
        except Exception as e:
            msg = f"Dump file {spec.file_name} not found or already deleted"
            return msg

    @log_entry_exit
    def get_all_dump_log_status(self):
        return self.gateway.get_all_dump_log_status()

    @log_entry_exit
    def get_dump_log_status(self):
        return self.gateway.get_dump_log_status()
