from enum import Enum


class SDSBBmcConnectionValidationMsg(Enum):
    NOT_SUPPORTED_ON_CLOUD = "This operation is only supported for bare metal."
