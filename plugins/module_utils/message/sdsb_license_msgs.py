from enum import Enum


class SDSBLicenseMsg(Enum):
    INVALID_STATUS = "Invalid status value: '{}'. Valid values are: '{}'."
    OVERCAPACITY_NOT_SUPPORTED = (
        "The 'allow_over_capacity' setting is only supported on AWS. Got: '{}'."
    )
    INVALID_TOTAL_POOL_CAPACITY_RATE = (
        "The 'total_pool_capacity_rate' value must be -1 or between 0 and 100. Got: {}."
    )
    INVALID_REMAINING_DAYS = (
        "The 'remaining_days' value must be between -1 and 60. Got: {}."
    )
    KEY_CODE_REQD_FOR_CREATE = "Key code is required for creating a license."
    ID_REQD_FOR_DELETE = "License id is required for deleting a license."
    INVALID_KEY_CODE = (
        "key_code must be between 1 and 75 characters. Got: {} characters."
    )
    INVALID_CHARS_IN_KEY_CODE = (
        "key_code must contain only uppercase alphanumeric characters (A-Z, 0-9)."
    )
    LICENSE_CREATE_SUCCESS = "License created successfully."
    LICENSE_DELETE_SUCCESS = "License deleted successfully."
    LICENSE_NOT_FOUND = "License not found - no action taken."
    INVALID_STATE = "Invalid state value: '{}'. Valid values are: 'present', 'absent'."
