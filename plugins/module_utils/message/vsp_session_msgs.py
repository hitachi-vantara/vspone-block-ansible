from enum import Enum


class VSPSessionValidationMsg(Enum):
    INVALID_ALIVE_TIME = "The 'alive_time_in_seconds' value must be between 1 and 300."
    INVALID_AUTHENTICATION_TIMEOUT = (
        "The 'authentication_timeout' value must be between 1 and 900."
    )
    ID_MISSING_FOR_DELETE = "You must specify 'id' for the 'delete' operation."
    TOKEN_MISSING_FOR_GET_BY_ID = (
        "You must specify 'token' for the 'get by id' operation."
    )
    TOKEN_MISSING_FOR_DELETE = "You must specify 'token' for the 'delete' operation."
    SESSION_DELETE_SUCCESS = "Session with ID '{}' has been successfully deleted."
    SESSION_DELETE_FAILURE = (
        "Could not delete session, ensure session ID '{}' is valid. Cause: '{}'"
    )
    FAILED_TO_GENERATE_TOKEN = "Failed to generate session token. Please check the error message for details: {}"
