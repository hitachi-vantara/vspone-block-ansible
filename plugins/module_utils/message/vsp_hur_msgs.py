from enum import Enum


class VSPHurValidateMsg(Enum):
    PRIMARY_VOLUME_ID = "primary_volume_id is a required field, which is missing."
    MIRROR_UNIT_ID = "mirror_unit_id is a required field, which is missing."
    SECONDARY_STORAGE_SN = "secondary_storage_serial_number is a required field, which is missing."
    SECONDARY_POOL_ID = "secondary_pool_id is a required field, which is missing."
    SECONDARY_HOSTGROUPS = "secondary_hostgroup is a required field, which is missing."
    SECONDARY_HOSTGROUPS_ID = "secondary_hostgroup.id is a required field, which is missing."
    SECONDARY_HOSTGROUPS_NAME = "secondary_hostgroup.name is a required field, which is missing."
    SECONDARY_HOSTGROUPS_PORT = "secondary_hostgroup.port is a required field, which is missing."
    PRIMARY_JOURNAL_ID = "primary_volume_journal_id is a required field, which is missing."
    SECONDARY_JOURNAL_ID = "secondary_volume_journal_id is a required field, which is missing."

    INVALID_CG_NEW = "allocate_new_consistency_group cannot be true if consistency_group_id is specified"
    INVALID_CG_ID = "Invalid consistency_group_id provided. Supported values are 0 to 255."
    NO_RESYNC_NEEDED= "HUR pair with primary_volume_id {} on storage system {} and secondary_volume_id {} on storage system {} is already in PAIR status. Resynchronization is not needed."
    ALREADY_SPLIT_PAIR = "HUR pair with primary_volume_id {} on storage system {} and secondary_volume_id {} on storage system {} is already a split pair. Split is not needed."
    PRIMARY_VOLUME_ID_DOES_NOT_EXIST = "HUR pair with primary_volume_id {} is no longer in the system."
    PRIMARY_VOLUME_AND_MU_ID_WRONG = "primary_volume_id {} and mirror_unit_id {} combination is wrong. Provide correct values."
    PRIMARY_VOLUME_ID_NO_PATH = "primary_volume_id {} does not have any path, ensure it is attached to at least one hostgroup."
    