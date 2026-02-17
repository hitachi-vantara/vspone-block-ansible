from enum import Enum


class SDSBExternalAuthServerValidationMsg(Enum):

    DOWNLOAD_ROOT_CERTIFICATE_SPEC_INVALID = "Download root certificate specification is invalid. target_server must be provided."
    IMPORT_ROOT_CERTIFICATE_SPEC_INVALID = "Import root certificate specification is invalid. root_certificate_file_path and target_server must be provided."
    INVALID_STATE_PROVIDED = (
        "SDSB External Auth Server Setting reconciliation supports only the 'present', 'download_root_certificate', "
        "and 'import_root_certificate' states. Got {} instead."
    )
    INVALID_TARGET_SERVER_PROVIDED = (
        "Invalid target server provided. Valid values are 'primary' and 'secondary'."
    )
