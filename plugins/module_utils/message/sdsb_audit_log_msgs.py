from enum import Enum


class SDSBAuditLogMsg(Enum):

    UNSUPPORTED_STATE = "Unsupported state: {}. Supported states is present."
    AUDIT_LOG_FILE_LOCATION_REQD = (
        "audit_log_file_location is required for downloading the audit log."
    )
    AUDIT_LOG_FILE_CREATED = "Audit log file has been created successfully. "
    AUDIT_LOG_FILE_CREATE_FAILED = (
        "Failed to create audit log file on the storage system: {}."
    )
    AUDIT_LOG_FILE_DOWNLODED = "Audit log file has been downloaded successfully to {}. "
    AUDIT_LOG_FILE_DOWNLOAD_FAILED = "The file could not be downloaded. The target file does not exist. Please create the audit log file first."
