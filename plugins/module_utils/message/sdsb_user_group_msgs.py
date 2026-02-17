from enum import Enum


class SDSBUserGroupValidationMsg(Enum):
    UNSUPPORTED_STATE = (
        "Unsupported state: {}. Supported states are present, and absent."
    )
