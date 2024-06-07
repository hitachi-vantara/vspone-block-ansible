from enum import Enum


class VSPSnapShotValidateMsg(Enum):
    PVOL_VALID_RANGE = (
        "Specify a decimal (base 10) number equal to or greater than 0 for pvol"
    )
    MU_VALID_RANGE = "Specify a value in the range from 0 to 1023 for mirror_unit_id "
    MU_VALID_PVOL_VALUE = "pvol is required to filter mirror_unit_id"
    SNAPSHOT_GRP_NAME = "snapshot_group_name is required for the direct connection new snapshot creation"
    SNAPSHOT_GRP_NAME_SPLIT = "snapshot_group_name is required for the direct connection auto-split mode"
    MU_PVOL_REQUIRED = "pvol and mirror_unit_id is required for the 'absent', 'sync', 'restore','split' "
    PVOL_REQUIRED = "pvol is required for the 'split' mode "
    POOL_ID_REQUIRED = "pool_id or mirror_unit_id is required when the state is 'split'"