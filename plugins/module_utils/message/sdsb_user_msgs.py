from enum import Enum


class SDSBUserValidationMsg(Enum):

    ID_USER_GROUP_IDS_REQD = "Id and user_groups_ids are required for {} operation."
    FIELD_MISSING_FOR_EDIT_USER = (
        "To edit user information, you must specify password, is_enabled, or both."
    )
    UNSUPPORTED_STATE = "Unsupported state: {}. Supported states are present, absent, update. add_user_group and remove_user_group."
    USER_INFO_UPDATED_SUCCESS = "User information updated successfully."
    USER_INFO_UPDATE_NOT_NEEDED = "User information update not needed."
    USER_CREATED_SUCCESS = "User created successfully."
    USER_PASSWORD_UPDATED_SUCCESS = "User password updated successfully."
    USER_NOT_FOUND_FOR_PASSWORD_UPDATE = "User {} not found for updating password."
    BOTH_CURRENT_AND_NEW_PASSWORD_REQD = (
        "Both current_password and new_password are required for changing password."
    )
    NEW_PASSWORD_DOES_NOT_MEET_COMPLEXITY = (
        "New password does not meet complexity requirements."
    )
    NEW_PASSWORD_SAME_AS_CURRENT = (
        "New password must be different from the current password."
    )
    NEW_PASSWORD_TOO_SHORT = "New password must be at least 8 characters long."
    NEW_PASSWORD_TOO_LONG = "New password must not exceed 256 characters."
