from enum import Enum


class GADPairValidateMSG(Enum):
    """
    Enum class for GAD pair validation messages
    """
    GAD_PAIR_NOT_FOUND = "GAD pair with id {} not found."
    DELETE_GAD_PAIR_SUCCESS = "GAD pair deleted successfully."
    PRIMARY_STORAGE_SN = "Primary storage serial number is required."
    SECONDARY_STORAGE_SN = "Secondary storage serial number is required."
    PRIMARY_VOLUME_ID = "Primary volume id is required."
    SECONDARY_POOL_ID = "Secondary pool id is required."
    REMOTE_UCP_SYSTEM = "Remote UCP system is required."
    SECONDARY_HOSTGROUPS = "Secondary hostgroups id is missing."
    HOSTGROUPS_ID = "{} Hostgroups id is missing."
    HOSTGROUPS_NAME = "{} Hostgroups name is missing."
    HOSTGROUPS_PORT = "{} Hostgroups port is missing."
    HG_RES_GRP_ID = "{} Hostgroups resource_group_id is missing."
    SECONDARY_SYSTEM_NT_FOUND = "Secondary storage system not found or not on boarded."
    SECONDARy_SYSTEM_CANNOT_BE_SAME = "Secondary storage system cannot be same as primary storage system."
    INCONSISTENCY_GROUP = "consistency_group_id and allocate_new_consistency_group can't be present at the same time. provide only one."
    PRIMARY_HG_NOT_FOUND = "Primary hostgroup with names {} not found."
    SEC_HG_NOT_FOUND =  "Secondary hostgroup with names {} not found."
    