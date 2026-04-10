from enum import Enum


class SDSBEventLogValidationMsg(Enum):

    BOTH_SEVERITY_SPECIFIED = "Specify either severity or severity_ge — not both."
    BOTH_SETTING_SPECIFIED = (
        "Cannot modify both syslogForwardingSetting and emailReportSetting simultaneously. "
        "Modify them separately."
    )
    NO_SETTING_SPECIFIED = (
        "Either syslog_forwarding_setting or email_report_setting must be provided."
    )
    UNSUPPORTED_STATE = (
        "The requested state '{}' is not supported for event log settings. "
        "Supported states are 'present', 'download_smtp_certificate' and 'import_smtp_certificate'."
    )
    CERT_PATH_REQDUIRED = (
        "The certificate_path must be provided for importing SMTP root certificate."
    )
    CERT_FILE_NOT_FOUND = "The specified certificate file '{}' was not found."
    CERT_IMPORT_SUCCESS = (
        "Root certificate for SMTP server communication is imported successfully."
    )
    CERT_DOWNLOAD_SUCCESS = "Successfully downloaded SMTP root certificate to {}."
