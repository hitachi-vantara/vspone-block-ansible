from enum import Enum


class VSPHostGroupMessage(Enum):
    IGNORE_WWNS = "The parameter wwns is ignored."
    IGNORE_LUNS = "The parameter luns is ignored."
    PORT_TYPE_INVALID = "The port type is not valid for this operation."
    PORTS_PARAMETER_INVALID = "Host group does not exist; cannot create host groups without port parameter."
    HG_HAS_BEEN_DELETED = (
        "Host group not found. (Perhaps it has already been deleted)"
    )
    LUN_IS_NOT_IN_HG = "The LUN is not in the host group."
    SPEC_STATE_INVALID = "The spec state parameter is invalid."
    LUNS_PRESENT = "Hostgroup has luns presented. Make sure to unpresent all lun prior deleting hostgroup."
    PORT_NOT_IN_SYSTEM = "Port {} is not in the storage system."
    WWNS_INVALID = "Input wwns is invalid. It must be an array."
    DELETE_SUCCESSFULLY = "Hostgroup {} is deleted successfully."

class VSPHostGroupValidationMsg(Enum):
    HG_NAME_OUT_OF_RANGE = "The host group name is out of range. Specify a value in the range from 1 to 64."
    LUN_OUT_OF_RANGE = "The lun is out of range. Specify a value in the range from 1 to 65535."
    PORT_OUT_OF_RANGE = "The port is out of range. Specify a value in the range from 1 to 256."
    HOST_MODE_OUT_OF_RANGE = "The host mode is out of range. Specify a value in the range from 1 to 256."
    WWN_OUT_OF_RANGE = "The wwn is out of range. Specify a value in the range from 1 to 256."
    INVALID_PARAM_LUNS = "The luns input parameter is incorrect, please correct and try again."
