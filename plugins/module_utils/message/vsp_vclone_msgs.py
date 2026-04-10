from enum import Enum


class VSPVcloneValidateMsg(Enum):
    NOT_SUPPORTED_ON_THIS_STORAGE = (
        "This operation is supported only for the B20 and B85 storage families."
    )
    NOT_CORRECT_STATE_FOR_VCLONE = "Snapshot with primary volume ID '{}' and mirror unit ID '{}' is not in a valid state to create a VClone."
    VCLONE_REQD_PARAMS_MISSING = (
        "primary_volume_id and mirror_unit_id are required for 'vclone' operation_type."
    )
    # INVALID_OPERATION_TYPE = "Invalid operation_type: {}. Supported operation_types are 'vclone', and 'restore'."
    # INVALID_OPERATION_TYPE_2 = "Invalid operation_type: {}. Supported operations are: '{}'"
