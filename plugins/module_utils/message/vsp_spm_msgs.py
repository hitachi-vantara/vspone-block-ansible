from enum import Enum


class VSPSpmValidateMsg(Enum):
    BOTH_NOT_ALLOWED = (
        "Either specify host_wwn attribute or specify iscsi_name attribute, not both."
    )
    ONE_HBA_RQRD = (
        "You must specify either the host_wwn attribute or the iscsi_name attribute."
    )
    BOTH_LIMIT_NOT_ALLOWED = "Either specify upper_limit_for_iops attribute or specify upper_limit_for_transfer_rate_in_MBps attribute, not both."
    ONE_LIMIT_RQRD = "You must specify either the upper_limit_for_iops attribute or the upper_limit_for_transfer_rate_in_MBps attribute."
    IOPS_OUT_OF_RANGE = (
        "For upper_limit_for_iops specify a value in the range from 1 to 65535."
    )
    TR_OUT_OF_RANGE = "For upper_limit_for_transfer_rate_in_MBps specify a value in the range from 1 to 31."
    HBA_WWN_16_CHARS = (
        "For host_wwn specify a hexadecimal number consisting of 16 characters."
    )
    SPM_INFO_SET_SUCCESS = "Server Priority Manager information set successfully."
    SPM_INFO_CHANGE_SUCCESS = (
        "Server Priority Manager information changed successfully."
    )
    SPM_INFO_CHANGE_NOT_NEEDED = (
        "Server Priority Manager information change not needed."
    )
    SPM_INFO_DELETE_SUCCESS = (
        "Server Priority Manager information deleted successfully."
    )
