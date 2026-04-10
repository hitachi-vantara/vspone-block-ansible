from enum import Enum


class VSPStorageSystemMonitorValidateMsg(Enum):
    ALERT_TYPE_NEEDED = "alert_type is required when query field is alerts."
    OPERATION_NOT_SUPPORTED = (
        "This operation is not supported for the specified storage system."
    )
