from enum import Enum


class VSPCmdDevValidateMsg(Enum):
    LDEV_NOT_FOUND = "LDEV with id {} not found."
    LDEV_NOT_DEFINED = "LDEV with id {} is not defined."
    CMD_DEV_ENABLE_SUCCESS = "Command Device has been enabled successfully."
    CMD_DEV_DISABLE_SUCCESS = "Command Device has been disabled successfully."
    NO_CMD_DEV_INFO = (
        " No Command Device information is available for VSP One storage system."
    )
