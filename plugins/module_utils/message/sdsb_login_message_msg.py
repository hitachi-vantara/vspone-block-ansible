from enum import Enum


class SDSBLoginMessageValidationMsg(Enum):
    NO_SPEC = "Message field is required for updating login message."
    INVALID_CHAR = "Message contains invalid characters: '{}'."
    MESSAGE_LIMIT = "Message exceeds 6144 characters limit."
    MESSAGE_STR = "Message must be a string."
    UNSUPPORTED_STATE = "The requested state '{}' is not supported for login message. Supported state is 'present'."
