from enum import Enum


class VSPSnapShotValidateMsg(Enum):
    PVOL_VALID_RANGE = (
        "Specify a decimal (base 10) number equal to or greater than 0 for pvol"
    )
    MU_VALID_RANGE = "Specify a value in the range from 0 to 1023 for mirror_unit_id "
    MU_VALID_PVOL_VALUE = "pvol is required to filter mirror_unit_id"
    SNAPSHOT_GRP_NAME = "snapshot_group_name is required for the direct connection new snapshot creation"
    SNAPSHOT_GRP_NAME_SPLIT = (
        "snapshot_group_name is required for the direct connection auto-split mode"
    )
    MU_PVOL_REQUIRED = "pvol and mirror_unit_id is required for the 'absent', 'sync', 'restore','split' "
    PVOL_REQUIRED = "pvol is required for the 'split' mode "
    POOL_ID_REQUIRED = "pool_id or mirror_unit_id is required when the state is 'split'"
    DATA_REDUCTION_SHARE = "Data reduction share is not enabled on the volume to create advanced snapshot pair"
    PROVIDE_SAME_POOL_ID = "When creating a Thin Image Advanced pair,specify the pool ID of the HDP pool to which the P-VOL belongs."
    DATA_REDUCTION_FORCE_COPY = "Data reduction force copy is not enabled on the volume to create snapshot pair when data reduction mode is enabled"
