from enum import Enum


class VSPVcloneValidateMsg(Enum):
    NOT_SUPPORTED_ON_THIS_STORAGE = (
        "This operation is supported only for the B20 and B85 storage families."
    )
