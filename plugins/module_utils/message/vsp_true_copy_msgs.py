from enum import Enum


class VSPTrueCopyValidateMsg(Enum):
    PRIMARY_VOLUME_ID = "primary_volume_id is a required field, which is missing."
    SECONDARY_STORAGE_SN = "secondary_storage_serial_number is a required field, which is missing."
    SECONDARY_POOL_ID = "secondary_pool_id is a required field, which is missing."
    SECONDARY_HOSTGROUPS = "secondary_hostgroup is a required field, which is missing."
    SECONDARY_HOSTGROUPS_ID = "secondary_hostgroup.id is a required field, which is missing."
    SECONDARY_HOSTGROUPS_NAME = "secondary_hostgroup.name is a required field, which is missing."
    SECONDARY_HOSTGROUPS_PORT = "secondary_hostgroup.port is a required field, which is missing."

    INVALID_CG_ID = "Invalid consistency_group_id provided. Supported values are 0 to 255."
    NO_RESYNC_NEEDED= "TrueCopy pair with primary_volume_id {} on storage system {} and secondary_volume_id {} on storage system {} is already in PAIR status. Resynchronization is not needed."
    ALREADY_SPLIT_PAIR = "TrueCopy pair with primary_volume_id {} on storage system {} and secondary_volume_id {} on storage system {} is already a split pair. Split is not needed."
    PRIMARY_VOLUME_ID_DOES_NOT_EXIST = "Could not find primary_volume_id {}."
    REMOTE_REP_DID_NOT_FIND_PORT = "Could not find the port {}."
    REMOTE_REP_NO_MORE_PORTS_AVAILABLE = "No more ports available to create default hostgroup for remote replication pairs."
    PRIMARY_VOLUME_ID_NO_PATH = "primary_volume_id {} does not have any path, ensure it is attached to at least one hostgroup."
    NO_TC_PAIR_FOR_PRIMARY_VOLUME_ID = "Could not find the truecopy pair associated with primary_volume_id {}."

    NO_REMOTE_HG_FOUND = "Could not find hostgroup {} on port {}."
    HG_SUBSCRIBER_ID_MISMATCH = "Provided subscriber_id {} and hostgroup subscriber Id did not match."
    NO_SUB_PROVIDED_HG_HAS_SUB = "No subscriber_id provided, but the hostgroup belongs to a subscriber."
    PORT_SUBSCRIBER_ID_MISMATCH = "Provided subscriber_id {} and port subscriber Id did not match."
    NO_SUB_PROVIDED_PORT_HAS_SUB = "No subscriber_id provided, but the port belongs to a subscriber."
    WRONG_PORT_PROVIDED = "{}'s port type is {} and port mode is {}. Ensure provided port's port type is FIBRE and port mode is SCSI."

    