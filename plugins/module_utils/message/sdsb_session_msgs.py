from enum import Enum


class SDSBSessionValidationMsg(Enum):
    INVALID_ALIVE_TIME = "The 'alive_time_in_seconds' value must be between 1 and 300."
    ID_MISSING_FOR_DELETE = "You must specify 'id' for the 'delete' operation."
    SESSION_DELETE_SUCCESS = "Session with ID '{}' has been successfully deleted."
    SESSION_DELETE_FAILURE = (
        "Failed to delete session with ID '{}'. Ensure the session ID is valid."
    )
