from enum import Enum


class SDSBDumpFileMsg(Enum):

    DUMP_FILE_CREATED = "Dump file with label {} created successfully."
    FILE_PATH_REQD = "File path is required."
    FILE_NAME_REQD = "File name is required."
    DUMP_FILE_DELETED = "Dump file {} deleted successfully."
    DUMP_FILE_NOT_FOUND = "Dump file {} not found or already deleted."
