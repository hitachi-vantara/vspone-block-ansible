from enum import Enum


class GADFailedMsg(Enum):
    PAIR_CREATION_FAILED = "Failed to create the GAD pair."
    PAIR_RESIZE_FAILED = "Failed to resize the GAD pair."
    PAIR_SPLIT_FAILED = "Failed to split the GAD pair."
    PAIR_SWAP_SPLIT_FAILED = "Failed to swap split the GAD pair."
    PAIR_SWAP_RESYNC_FAILED = "Failed to swap resync the GAD pair."
    PAIR_RESYNC_FAILED = "Failed to resync the GAD pair."

    SEC_VOLUME_DELETE_FAILED = "Failed to delete the secondary volume."
    SEC_VOLUME_OPERATION_FAILED = "Failed to perform operation on the secondary volume."


class GADPairValidateMSG(Enum):
    """
    Enum class for GAD pair validation messages
    """

    GAD_PAIR_NOT_FOUND = "GAD pair with id {} not found."
    GAD_PAIR_NOT_FOUND_SIMPLE = "GAD pair is not found."
    DELETE_GAD_PAIR_SUCCESS = "GAD pair deleted successfully."
    DELETE_GAD_FAIL_SPLIT_DIRECT = (
        "To delete the GAD pair, it must be in the split state."
    )
    DELETE_GAD_FAIL_SPLIT_GW = "To delete the GAD pair, it must be in the PAIR state."
    PRIMARY_STORAGE_SN = "Primary storage serial number is required."
    SECONDARY_STORAGE_SN = "Secondary storage serial number is required."
    PRIMARY_VOLUME_ID = "Primary volume id is required."
    SECONDARY_POOL_ID = "Secondary pool id is required."
    REMOTE_UCP_SYSTEM = "Remote UCP system is required."
    SECONDARY_HOSTGROUPS = "Secondary hostgroups id is missing."
    SECONDARY_HOSTGROUPS_OR_NVME = (
        "Either specify Secondary hostgroups, NVM subsystem or Iscsi target details."
    )
    HOSTGROUPS_ID = "{} Hostgroups id is missing."
    HOSTGROUPS_NAME = "{} Hostgroups name is missing."
    HOSTGROUPS_PORT = "{} Hostgroups port is missing."
    HG_RES_GRP_ID = "{} Hostgroups resource_group_id is missing."
    SECONDARY_SYSTEM_NT_FOUND = "Secondary storage system not found or not on boarded."
    SECONDARy_SYSTEM_CANNOT_BE_SAME = (
        "Secondary storage system cannot be same as primary storage system."
    )
    INCONSISTENCY_GROUP = "consistency_group_id and allocate_new_consistency_group can't be present at the same time. provide only one."
    NO_PRIMARY_VOLUME_FOUND = "Primary volume {} not found."
    PRIMARY_HG_NOT_FOUND = "Primary hostgroup with names {} not found."
    SEC_HG_NOT_FOUND = "Secondary hostgroup with names {} not found."
    NO_REMOTE_HG_FOUND = "Remote hostgroup is not found."
    NO_PAIR_FOR_PRIMARY_VOLUME_ID = (
        "Could not find the GAD pair associated with primary_volume_id {}."
    )
    NO_SWAP_SPLIT_WITH_CTG = "The swap_split operation is not supported for GAD pairs that are part of a consistency group."
    NEW_VOLUME_SIZE = (
        "new_volume_size is a required field for resize operation, which is missing."
    )
    EXPAND_VOLUME_FAILED = "Failed to expand the volume. Ensure System Option Mode (SOM) 1198 is enabled and 1199 is disabled."
    EXPAND_PVOL_FAILED = "Failed to perform operation for primary volume {}."
    EXPAND_SVOL_FAILED = "Failed to perform operation for secondary volume {}."
    NO_GAD_PAIR_FOUND_FOR_INPUTS = (
        "Could not find GAD pair for the input parameters supplied."
    )
    NO_REMOTE_HGS_FOUND = "Specified host groups not found on secondary storage."
    NO_REMOTE_ISCSI_FOUND = "Specified iSCSI targets not found on secondary storage."
    RG_DID_NOT_MATCH = (
        "Resource Group ID for secondary volume and the hostgroups did not match."
    )
    QUORUM_DISK_ID = "quorum_disk_id is a required field, which is missing."
    VLDEV_ID_NOT_SET_FOR_DRS_PVOL = "Virtual LDEV ID is not set for the data reduction share primary volume {}, which is required for GAD pair creation."
    CREATE_GAD_PAIR_FAILED = "Failed to create the GAD pair for primary_volume_id {}."
    BATCH_CREATE_PRIMARY_VOLUME_FAILED = (
        "Failed to create primary volumes for batch GAD pair creation. "
        "Please check the error details for more information."
    )
    SEC_HGS_IN_META_RG = (
        "Secondary host groups cannot be part of a meta resource group for GAD pair creation. "
        "Secondary host group '{}' is part of meta resource group."
    )
    SEC_IST_IN_META_RG = (
        "Secondary iSCSI target groups cannot be part of a meta resource group for GAD pair creation. "
        "Secondary iSCSI target group '{}' is part of meta resource group."
    )
    SEC_NVM_SUBSYSTEM_IN_META_RG = (
        "Secondary NVM subsystems cannot be part of a meta resource group for GAD pair creation. "
        "Secondary NVM subsystem '{}' is part of meta resource group."
    )
    NUMBER_OF_PAIRS_RANGE = (
        "number_of_pairs must be a positive integer between 1 and {}."
    )
    NUMBER_OF_PAIRS_POSITIVE = "number_of_pairs must be a positive integer."
    PRIMARY_HG_IST_NVM_REQUIRED = (
        "At least one of primary_hostgroups, primary_iscsi_targets, "
        "or primary_nvm_subsystems must be provided."
    )
    SECONDARY_HG_REQUIRED = (
        "secondary_hostgroups must be provided if primary_hostgroups is present."
    )
    SECONDARY_IST_REQUIRED = (
        "secondary_iscsi_targets must be provided if primary_iscsi_targets is present."
    )
    SECONDARY_NVM_REQUIRED = (
        "secondary_nvm_subsystem must be provided if primary_nvm_subsystem is present."
    )
    BEGIN_PRIMARY_GREATER_THAN_END = (
        "begin_primary_volume_id cannot be greater than end_primary_volume_id."
    )
    BEGIN_SECONDARY_GREATER_THAN_END = (
        "begin_secondary_volume_id cannot be greater than end_secondary_volume_id."
    )
    PRIMARY_VOLUME_RANGE_MISMATCH = (
        "The range defined by begin_primary_volume_id and end_primary_volume_id "
        "must match or be greater than number_of_pairs. Expected {} but got {}."
    )
    SECONDARY_VOLUME_RANGE_MISMATCH = (
        "The range defined by begin_secondary_volume_id and end_secondary_volume_id "
        "must match or be greater than number_of_pairs. Expected {} but got {}."
    )
    GAD_PAIR_DOES_NOT_EXIST = (
        "GAD pair with copy group name '{}' and copy pair name '{}' does not exist."
    )


class VspOneGadValidationMsg(Enum):
    """
    Enum class for VSP One GAD validation messages
    """

    CONSISTENCY_GROUP_ID_REQUIRED = (
        "consistency_group_id is required in the spec to create GAD pairs"
    )
    GAD_PAIR_DEFINITION_REQUIRED = (
        "At least one gad pair definition is required in the spec to create GAD pairs"
    )
    SECONDARY_STORAGE_POOL_ID_REQUIRED = ("secondary_storage_pool_id is required in the spec to create GAD pairs or "
                                          "few secondary volumes in gad_pairs are not provisioned")

    PATH_GROUP_ID_REQUIRED = "path_group_id is required in the spec to create GAD pairs"
    QUORUM_ID_REQUIRED = "quorum_id is required in the spec to create GAD pairs"
    SECONDARY_SERVER_REQUIRED = (
        "At least one secondary server is required in the spec to create GAD pairs or few secondary volumes in gad_pairs are not provisioned"
    )
    SECONDARY_STORAGE_NOT_FOUND = (
        "Secondary storage with IP {} not found in remote storages"
    )
    PATH_GROUP_NOT_FOUND = "Path group not found in secondary storage with IP {}"
    PRIMARY_VOLUME_NOT_FOUND = "Primary volume with ID {} not found"
    PRIMARY_VOLUME_NOT_MAPPED = (
        "Primary volume with ID {} is not mapped to any server, "
        "it needs to be mapped to at least one server to be used in GAD"
    )
    FAILED_TO_CREATE_GAD_CTG = "Failed to create GAD CTG with ID {}: {}"
    FAILED_TO_CREATE_SECONDARY_VOLUMES = "Failed to create secondary volumes: {}"
    FAILED_TO_ATTACH_SERVERS_TO_VOLUMES = "Failed to add primary volumes to server: {}"
    FAILED_TO_DETACH_SECONDARY_VOLUME = (
        "Failed to detach secondary volume with ID {} from server {} during cleanup: {}"
    )
    FAILED_TO_DELETE_SECONDARY_VOLUMES = (
        "Failed to delete secondary volumes during cleanup: {}"
    )
    CONSISTENCY_GROUP_ID_RANGE = (
        "consistency_group_id must be between 0 and 1023. Provided value is {}."
    )
    COPY_PACE_RANGE = "copy_pace must be between 1 and 15. Provided value is {}."
    CONTINUE_IO_VOLUMES_INVALID = "Invalid continue_io_volume value '{}'. It must be one of 'PRIMARY', or 'SECONDARY'."
    IO_PREFERENCE_MODE_INVALID = (
        "Invalid io_preference_mode value '{}'. It must be one of {}."
    )
    MIRROR_UNIT_NUMBER_MISMATCH = "mirror_unit_number {} for for consistency group {} must be the same across all GAD pairs. Existing ID is: {}"
    SECONDARY_VOLUME_NOT_FOUND = "Secondary volume with ID {} not found."
    DELETE_MODE_INVALID = "Invalid delete_mode value '{}'. It must be one of 'NORMAL', or 'FORCE'."
    ALLOW_VOLUME_ACCESS_REQUIRED = "allow_volume_access_after_force_delete is required when delete_mode is FORCE."
    COUNT_INVALID = "count must be a positive integer between 1 and 500. Provided value is {}."
