from enum import Enum


class VspRemoteReplicationMsg(Enum):
    STORAGE_INFO = "This message is for {} storage system."
    HGS_DOES_NOT_EXIST = "Hostgroup '{}' does not exist on port {}."
    INSUFFICIENT_FREE_LDEVS = "Requested {} free LDEVs, but only {} are available for the specified condition."
    FAILED_TO_CREATE_LDEVS = (
        "Failed to create LDEVs on {} storage system for the HUR batch creation."
    )
    ISCSI_TARGET_DOES_NOT_EXIST = "iSCSI target '{}' does not exist on port {}."
    NVM_SUBSYSTEM_DOES_NOT_EXIST = "NVMe subsystem '{}' does not exist."
    NO_HG_PROVIDED = "No host group provided for remote replication."
    NO_VALID_HG_PROVIDED = "No valid host group provided for remote replication."
    NO_ISCSI_TARGET_PROVIDED = "No iSCSI target provided for remote replication."
    NO_VALID_ISCSI_TARGET_PROVIDED = (
        "No valid iSCSI target provided for remote replication."
    )
    NO_NVM_SUBSYSTEM_PROVIDED = "No NVMe subsystem provided for remote replication."
    HOST_GROUPS_OR_IST_OR_NVME_MISSING = "One of host groups, iSCSI targets, or NVMe subsystem must be specified for remote batch replication."
    JOURNAL_ID_DOES_NOT_EXIST = (
        "Journal with ID '{}' does not exist on storage system '{}'."
    )
    NVM_OPERATION_FAILED = (
        "Operation '{}' failed for NVMe subsystem '{}' on storage system '{}'."
    )
    CAPACITY_SAVING_DISABLED = (
        "Capacity saving is disabled, this operation cannot be performed."
    )


class HurFailedMsg(Enum):
    PAIR_CREATION_FAILED = "Failed to create the HUR pair."
    PAIR_RESIZE_FAILED = "Failed to resize the HUR pair."
    PAIR_SPLIT_FAILED = "Failed to split the HUR pair."
    PAIR_SWAP_SPLIT_FAILED = "Failed to swap split the HUR pair."
    PAIR_SWAP_RESYNC_FAILED = "Failed to swap resync the HUR pair."
    PAIR_RESYNC_FAILED = "Failed to resync the HUR pair."
    PAIR_DELETION_FAILED = "Failed to delete the HUR pair."
    SECONDARY_TAKEOVER_FAILED = "Failed to take over the secondary volume."

    SEC_VOLUME_DELETE_FAILED = "Failed to delete the secondary volume."
    SEC_VOLUME_OPERATION_FAILED = "Failed to perform operation on the secondary volume."


class VSPHurValidateMsg(Enum):
    PRIMARY_VOLUME_ID = "primary_volume_id is a required field, which is missing."
    MIRROR_UNIT_ID = "mirror_unit_id is a required field, which is missing."
    SECONDARY_STORAGE_SN = (
        "secondary_storage_serial_number is a required field, which is missing."
    )
    PRIMARY_POOL_ID = "primary_pool_id is a required field, which is missing."
    SECONDARY_POOL_ID = "secondary_pool_id is a required field, which is missing."
    SECONDARY_HOSTGROUPS = "secondary_hostgroup is a required field, which is missing."
    SECONDARY_HOSTGROUPS_ID = (
        "secondary_hostgroup.id is a required field, which is missing."
    )
    SECONDARY_HOSTGROUPS_NAME = (
        "secondary_hostgroup.name is a required field, which is missing."
    )
    SECONDARY_HOSTGROUPS_PORT = (
        "secondary_hostgroup.port is a required field, which is missing."
    )
    PRIMARY_JOURNAL_ID = (
        "primary_volume_journal_id is a required field, which is missing."
    )
    SECONDARY_JOURNAL_ID = (
        "secondary_volume_journal_id is a required field, which is missing."
    )

    INVALID_CTG_BOTH_NONE = "Either consistency_group_id or allocate_new_consistency_group must be specified"
    INVALID_CTG_NONE = "consistency_group_id must be specified if allocate_new_consistency_group is false"
    INVALID_CG_NEW = "allocate_new_consistency_group cannot be true if consistency_group_id is specified"
    INVALID_CG_ID = (
        "Invalid consistency_group_id provided. Supported values are 0 to 255."
    )
    NO_PRIMARY_VOLUME_FOUND = "Could not find primary_volume_id {}."
    NO_RESYNC_NEEDED = (
        "HUR pair with primary_volume_id {} on storage system {} and "
        "secondary_volume_id {} on storage system {} is already in PAIR status. "
        "Resynchronization is not needed."
    )
    ALREADY_SPLIT_PAIR = (
        "HUR pair with primary_volume_id {} on storage system {} and "
        "secondary_volume_id {} on storage system {} is already a split pair. "
        "Split is not needed."
    )
    PRIMARY_VOLUME_ID_DOES_NOT_EXIST = (
        "HUR pair with primary_volume_id {} is no longer in the system."
    )
    HUR_PAIR_ALREADY_EXIST = (
        "HUR pair with primary_volume_id {} and mirror_unit_id {} already exist."
    )
    PRIMARY_VOLUME_AND_MU_ID_WRONG = "primary_volume_id {} and mirror_unit_id {} combination is wrong, pair not found. Provide correct values."
    PRIMARY_VOLUME_ID_NO_PATH = "primary_volume_id {} does not have any path, ensure it is attached to at least one hostgroup."
    NO_HUR_PAIR_FOUND = "Could not find the HUR pair associated with copy_pair_name {}."
    HUR_PAIR_NOT_FOUND_SIMPLE = "HUR pair is not found."
    NO_LOCAL_DEVICE_NAME_FOUND = "Incorrect local_device_group_name for existing copy_group {}. Provide correct existing value {}."
    NO_REMOTE_DEVICE_NAME_FOUND = "Incorrect remote_device_group_name for existing copy_group {}. Provide correct existing value {}."
    NEW_VOLUME_SIZE = (
        "new_volume_size is a required field for resize operation, which is missing."
    )
    EXPAND_VOLUME_FAILED = "Failed to expand the volume. Ensure System Option Mode ( SOM ) 1198 is enabled and 1199 is disabled."
    REDUCE_VOLUME_SIZE_NOT_SUPPORTED = "Shrink/reduce volume size is not supported."
    SECONDARY_RANGE_ID_INVALID = "Please specify both begin_secondary_volume_id and end_secondary_volume_id. Specifying either one is not supported."
    EXPAND_PVOL_FAILED = "Failed to perform operation for primary volume {}."
    EXPAND_SVOL_FAILED = "Failed to perform operation for secondary volume {}."
    PAIR_NOT_IN_SSWS_STATE = (
        "HUR pair {} is not in SSWS state. Operation is not allowed."
    )
    SECONDARY_VOLUME_ID_OUT_OF_RANGE = "provisioned_secondary_volume_id does not lie between begin_secondary_volume_id and end_secondary_volume_id."
    HUR_OPERATION_FAILED = "HUR operation failed with response: {}"
    NUMBER_OF_PAIRS = "number_of_pairs is a required field and should be greater than 0 and less than or equal to 32 for HUR batch creation."
    VOLUME_SIZE = (
        "volume_size is a required field for HUR batch creation, which is missing."
    )
    PRIMARY_HOSTGROUPS_OR_NVME = "One of primary_hostgroups, primary_iscsi_targets, or primary_nvm_subsystem must be specified for HUR batch creation."
    SECONDARY_HOSTGROUPS_OR_NVME = "One of secondary_hostgroups, secondary_iscsi_targets, or secondary_nvm_subsystem must be specified for HUR batch creation."
    BOTH_PRIMARY_HGS_AND_IST_ARE_SPECIFIED = "primary_hostgroups and primary_iscsi_targets cannot both be specified. Please specify only one of them."
    BOTH_PRIMARY_HGS_AND_NVME_ARE_SPECIFIED = "primary_hostgroups and primary_nvm_subsystem cannot both be specified. Please specify only one of them."
    BOTH_PRIMARY_IST_AND_NVME_ARE_SPECIFIED = "primary_iscsi_targets and primary_nvm_subsystem cannot both be specified. Please specify only one of them."
    BOTH_SECONDARY_HGS_AND_IST_ARE_SPECIFIED = "secondary_hostgroups and secondary_iscsi_targets cannot both be specified. Please specify only one of them."
    BOTH_SECONDARY_HGS_AND_NVME_ARE_SPECIFIED = "secondary_hostgroups and secondary_nvm_subsystem cannot both be specified. Please specify only one of them."
    BOTH_SECONDARY_IST_AND_NVME_ARE_SPECIFIED = "secondary_iscsi_targets and secondary_nvm_subsystem cannot both be specified. Please specify only one of them."
    PRIMARY_HGS_WITHOUT_SECONDARY_HGS = "primary_hostgroups cannot be specified without secondary_hostgroups for HUR batch creation."
    SECONDARY_HGS_WITHOUT_PRIMARY_HGS = "secondary_hostgroups cannot be specified without primary_hostgroups for HUR batch creation."
    PRIMARY_IST_WITHOUT_SECONDARY_IST = "primary_iscsi_targets cannot be specified without secondary_iscsi_targets for HUR batch creation."
    SECONDARY_IST_WITHOUT_PRIMARY_IST = "secondary_iscsi_targets cannot be specified without primary_iscsi_targets for HUR batch creation."
    PRIMARY_NVME_WITHOUT_SECONDARY_NVME = "primary_nvm_subsystem cannot be specified without secondary_nvm_subsystem for HUR batch creation."
    SECONDARY_NVME_WITHOUT_PRIMARY_NVME = "secondary_nvm_subsystem cannot be specified without primary_nvm_subsystem for HUR batch creation."

    NOT_ENOUGH_FREE_LDEVS = "Not enough free LDEVs available to create {0} HUR pairs requested for the specification on {1} storage. Available free LDEVs: {2}."
    PRIMARY_HGS_DOES_NOT_EXIST = (
        "Hostgroup '{}' does not exist on port '{}' on primary storage."
    )
    SECONDARY_HGS_DOES_NOT_EXIST = (
        "Hostgroup '{}' does not exist on port '{}' on secondary storage."
    )
    HUR_PAIR_AND_SVOL_DELETED = (
        "HUR pair '{}' and secondary volume '{}' deleted successfully."
    )
    HUR_PAIR_DELETED = "HUR pair '{}' deleted successfully."
    PAIR_ALREADY_IN_SYNC = "HUR pair '{}' is already in sync."
    PAIR_RESYNCED = "HUR pair '{}' resynced successfully."
    PAIR_SWAP_RESYNCED = "HUR pair '{}' swap resynced successfully."
    SECONDARY_TAKEOVER_COMPLETED = (
        "Secondary takeover for HUR pair '{}' completed successfully."
    )
    PAIR_RESIZED = "HUR pair '{}' resized successfully."
    HUR_PAIR_ALREADY_EXISTS = "HUR pair '{}' already exists."
    HUR_PAIR_CREATED = "HUR pair '{}' created successfully."
    PAIR_ALREADY_SPLIT = "HUR pair '{}' is already split."
    PAIR_SPLIT = "HUR pair '{}' split successfully."
    PAIR_SWAP_SPLIT = "HUR pair '{}' swap split successfully."
    PAIR_ALREADY_SPLIT_AND_SWAPPED = "HUR pair '{}' is already split and swapped."
    NO_FREE_JOURNAL_POOL = "No free journal pool available on storage system '{}'."
