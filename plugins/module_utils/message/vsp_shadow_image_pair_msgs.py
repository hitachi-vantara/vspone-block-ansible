from enum import Enum


class VSPShadowImagePairValidateMsg(Enum):

    COPY_PACE_TRACK_SIZE_VALUE = (
        "copy_pace_track_size value should be either SLOW, MEDIUM or FAST."
    )
    COPY_PACE_VALUE = "copy_pace value should be either SLOW, MEDIUM or FAST."
    MAX_3_PAIR_EXISTS = "Maximum 3 shadow image pairs are already present."
    AUTO_SPLIT_VALIDATION = "Creating shadow image pair with split or auto_split is true then new_consistency_group should not be true."
    ENABLE_QUICK_MODE_VALIDATION = "Creating shadow image pair with enable_quick_mode is true then auto_split should be true."
    PVOL_NOT_FOUND = "Primary volume not found."
    SVOL_NOT_FOUND = "Secondary volume not found."
    SVOL_POOL_ID_NEEDED = "When secondary_volume_id is not provided or type is UNDEFINED, secondary_pool_id is needed, which is missing."
    PVOL_SVOL_SIZE_MISMATCH = "Primary volume and secondary volume size mismatch."
    PAIR_NOT_FOUND = "Shadow image pair not found with pair id = {}."
    PVOL_NO_HG_PRESENTATION = "Cannot create shadow image pair. Primary volume has no host group presentation."
    NOT_REQD_PARAAMS_PROVIDED = (
        "Either pvol and svol or copy_pair_name and copy_group_name must be provided."
    )
    ANOTHER_PAIR_EXISTS = (
        "Another copy pair might already be using the specified primary volume {} and secondary volume {}. "
        "Please verify and try again with correct copy group name and copy pair name."
    )
    SI_NOT_AVAILABLE = "Shadow image pair is not available."
    PVOL_REQD_FOR_CREATE = (
        "Primary volume ID (pvol) must be provided when creating a shadow image pair."
    )
