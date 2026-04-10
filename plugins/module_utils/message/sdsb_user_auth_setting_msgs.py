from enum import Enum


class SDSBUserAuthSettingMsg(Enum):
    UNSUPPORTED_STATE = "The requested state '{}' is not supported for user authentication settings. Supported state is 'present'."
    NO_USER_AUTH_SETTINGS = "No user authentication settings provided for update."
    USER_AUTH_SETTING_NOT_FOUND = (
        "No existing user authentication settings found to update."
    )
