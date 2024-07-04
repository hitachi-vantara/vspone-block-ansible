from enum import Enum

class VSPShadowImagePairValidateMsg(Enum):

    COPY_PACE_TRACK_SIZE_VALUE = "copy_pace_track_size value should be either SLOW, MEDIUM or FAST"
    COPY_PACE_VALUE = "copy_pace value should be either SLOW, MEDIUM or FAST"
    MAX_3_PAIR_EXISTS = "Maximum 3 shadow image pairs are already present"
    AUTO_SPLIT_VALIDATION = "Creating shadow image pair with split or auto_split is true then new_consistency_group should not be true"
    ENABLE_QUICK_MODE_VALIDATION = "Creating shadow image pair with enable_quick_mode is true then auto_split should be true"
    PVOL_NOT_FOUND = "Primary volume not found"