from enum import Enum


class SDSBRemotePathGroupValidationMsg(Enum):

    ID_REQD = "Id is required for this operation."
    REQD_INPUT_MISSING = (
        "One or more required input parameters are missing for create operation. The required input parameters for this operation are: "
        "'local_port', 'remote_port', 'remote_serial', 'remote_storage_system_type', 'path_group_id'."
    )
    REQD_INPUT_MISSING_FOR_UPDATE = "Required input parameter 'remote_io_timeout_in_sec' is missing for update operation."
    REQD_INPUT_MISSING_FOR_PATH_OPERATION = (
        "One or more required input parameters are missing. The required input parameters for this operation are: "
        "'local_port', 'remote_port'."
    )
    INVALID_REMOTE_SERIAL = "Invalid value for 'remote_serial'. It must be a 6-digit numeric string (e.g., '810045')."
    INVALID_PORT = "Invalid value for '{}'. It must be in CLx-y format."
    INVALID_PATH_GROUP_ID = "The 'path_group_id' value must be between 1 and 255."
    INVALID_TIMEOUT_VALUE = (
        "The 'remote_io_timeout_in_sec' value must be between 10 and 80."
    )
    UNSUPPORTED_STATE = "Unsupported state: {}. Supported states are present, absent, update, add_remote_path and remove_remote_path."
    REMOTE_PATH_GROUP_NOT_FOUND = "Did not find remote path group with id = '{}'."
    REMOTE_PATH_EXISTS = (
        "The remote path already exists in the remote path group with id = '{}'."
    )
    REMOTE_PATH_DOES_NOT_EXIST = (
        "The remote path does not exist in the remote path group with id = '{}'."
    )
    DELETE_REMOTE_PATH_SUCCESS = (
        "Remote path group with ID '{}' has been successfully deleted."
    )
    REMOTE_PATH_GROUP_NOT_FOUND_OR_DELETED = (
        "Remote path group with ID '{}' not found or already deleted."
    )
