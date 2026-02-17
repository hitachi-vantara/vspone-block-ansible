import os

try:
    from .gateway_manager import SDSBConnectionManager
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..model.sdsb_dump_log_models import (
        CreateDumpFileSpec,
        DownloadDumpFileSpec,
        DumpLogStatusResponse,
        AllDumpLogStatusResponse,
    )
except ImportError:
    from .gateway_manager import SDSBConnectionManager
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit

CREATE_DUMP_FILE = "v1/objects/dump-file/actions/create-file/invoke"
DOWNLOAD_DUMP_FILE = "v1/objects/dump-file/download"
DOWNLOAD_DUMP_FILE_BY_FILE = "v1/objects/dump-files/{}/download"
DELETE_DUMP_FILE = "v1/objects/dump-files/{}"
DUMP_STATUS = "v1/objects/dump-statuses"
DUMP_STATUS_SINGLE = "v1/objects/dump-status"
ISSUE_AUTH_TICKET = "v1/objects/tickets"
DISCARD_AUTH_TICKET = "v1/objects/tickets/actions/revoke-all/invoke"

logger = Log()


class SDSBDumpLogGateway:

    def __init__(self, connection_info):
        self.connection_manager = SDSBConnectionManager(
            connection_info.address, connection_info.username, connection_info.password
        )

    def generate_file_name(self):
        from datetime import datetime

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"hsds_log_{timestamp}_ansible.tar.gz"

    @log_entry_exit
    def create_dump_file(self, spec: CreateDumpFileSpec):
        end_point = CREATE_DUMP_FILE
        payload = {"label": spec.label, "mode": spec.mode}
        return self.connection_manager.post(end_point, data=payload)

    @log_entry_exit
    def download_dump_file(self, spec: DownloadDumpFileSpec):
        end_point = DOWNLOAD_DUMP_FILE
        file_name = self.generate_file_name()
        file_name_path = os.path.join(spec.file_path, file_name)        # nosec
        resp = self.connection_manager.download_file(end_point)
        with open(file_name_path, "wb") as file:
            file.write(resp)
        return f"Dump file downloaded successfully to {file_name_path}"

    @log_entry_exit
    def download_dump_file_using_filename(self, spec: DownloadDumpFileSpec):

        end_point = DOWNLOAD_DUMP_FILE_BY_FILE.format(spec.file_name)

        file_name_path = os.path.join(spec.file_path, spec.file_name)       # nosec
        try:
            response = self.connection_manager.download_file(end_point)
            with open(file_name_path, "wb") as file:
                file.write(response)
                return f"Dump file downloaded successfully to {file_name_path}"
        except Exception as e:
            raise ValueError(f"File with file name {spec.file_name} not found")

    @log_entry_exit
    def delete_dump_file(self, spec: DownloadDumpFileSpec):
        end_point = DELETE_DUMP_FILE.format(spec.file_name)
        return self.connection_manager.delete(end_point)

    @log_entry_exit
    def get_all_dump_log_status(self):
        end_point = DUMP_STATUS
        response = self.connection_manager.get(end_point)
        return AllDumpLogStatusResponse().dump_to_object(response)

    @log_entry_exit
    def get_dump_log_status(self):
        end_point = DUMP_STATUS_SINGLE
        response = self.connection_manager.get(end_point)
        return DumpLogStatusResponse(**response)
