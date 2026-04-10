from enum import Enum


class SDSBUserGroupValidationMsg(Enum):
    UNSUPPORTED_STATE = (
        "Unsupported state: {}. Supported states are present, and absent."
    )
    USER_GROUP_DELETED = "User group {} deleted successfully."
    USER_GROUP_DELETE_FAILED = "Failed to delete user group {}."
