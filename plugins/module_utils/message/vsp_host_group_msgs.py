from enum import Enum


class VSPHostGroupMessage(Enum):
    IGNORE_WWNS = "The parameter wwns is ignored."
    IGNORE_LUNS = "The parameter ldevs is ignored."
    PORT_TYPE_INVALID = "The port type is not valid for this operation."
    PORTS_PARAMETER_INVALID = (
        "Host group does not exist; cannot create host groups without port parameter."
    )
    HG_HAS_BEEN_DELETED = "Host group not found. (Perhaps it has already been deleted)"
    LUN_IS_NOT_IN_HG = "The LDEV is not in the host group."
    SPEC_STATE_INVALID = "The spec state parameter is invalid."
    LDEVS_PRESENT = "Hostgroup has ldevs presented. Make sure to unpresent all ldev prior deleting hostgroup."
    PORT_NOT_IN_SYSTEM = "Port {} is not in the storage system."
    WWNS_INVALID = "Input wwns is invalid. It must be an array."
    DELETE_SUCCESSFULLY = "Hostgroup {} is deleted successfully."
    HG_NAME_EMPTY = "The host group name parameter cannot be empty."
    HG_CREATE_FAILED = "Host group create failed. "
    HG_IN_META_NOT_AVAILABLE = "Host group in meta resource not available."


class VSPHostGroupValidationMsg(Enum):
    HG_NAME_OUT_OF_RANGE = "The host group name is out of range. Specify a value in the range from 1 to 64."
    LUN_OUT_OF_RANGE = (
        "The lun is out of range. Specify a value in the range from 1 to 65535."
    )
    PORT_OUT_OF_RANGE = (
        "The port is out of range. Specify a value in the range from 1 to 256."
    )
    HOST_MODE_OUT_OF_RANGE = (
        "The host mode is out of range. Specify a value in the range from 1 to 256."
    )
    HOST_MODE_OPTION_OUT_OF_RANGE = "The host mode option is out of range. Specify a value in the range from 0 to 999."
    WWN_OUT_OF_RANGE = (
        "The wwn is out of range. Specify a value in the range from 1 to 256."
    )
    INVALID_PARAM_LDEVS = (
        "The ldevs input parameter is incorrect, please correct and try again."
    )
