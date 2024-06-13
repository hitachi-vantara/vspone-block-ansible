from enum import Enum


class VSPVolumeMessage(Enum):
    pass


class VSPVolValidationMsg(Enum):
    NOT_POOL_ID_OR_PARITY_ID = "either pool_id or parity_group should be provided."
    LUN_REQUIRED = "lun is required for absent state to delete."
    COUNT_VALUE = "The parameter 'count' must be a whole number greater than zero."
    END_LDEV_AND_COUNT = "Ambiguous parameters, count and end_ldev_id cannot co-exist."
    POOL_ID_OR_PARITY_ID = "pool_id or parity_group is mandatory for new lun creation."
    SIZE_REQUIRED = "size is mandatory for new lun creation."
    SIZE_INT_REQUIRED = "provide integer value for the size with unit. e.g. 5GB, 2TB, etc."
    VALID_SIZE = "size is less than actual volume size of the lun , Please provide with more than the actual size."
    LDEV_ID_OUT_OF_RANGE = "lun id is out of range to create, Please specify within the range of 1 to 65535."
    MAX_LDEV_ID_OUT_OF_RANGE = (
        "ldev id is out of range, Please specify within the range of 1 to 65535."
    )
    START_LDEV_LESS_END = "end_ldev_id can't be less then start_ldev_id."
    BOTH_API_TOKEN_USER_DETAILS = "either api_token or user details (username, key) is required, both can't be provided"
    NOT_API_TOKEN_USER_DETAILS = "either api_token or user details (username, key) is required"
    DIRECT_API_TOKEN_ERROR = "api_token should not be present when connection type is 'direct'"
    VOLUME_NOT_FOUND = "Volume not found for the given lun id {}"
    VOLUME_NOT_FOUND_BY_NAME = "Volume not found for the given lun name {}"
    POOL_ID_PARITY_GROUP = "Either pool id or parity group is required for volume creation. Please provide one of them not both"
    POOL_ID_OR_PARITY_GROUP = "Either pool id or parity group is required for volume creation."
