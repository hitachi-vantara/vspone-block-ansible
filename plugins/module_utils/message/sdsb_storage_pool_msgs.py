from enum import Enum


class SDSBStoragePoolValidationMsg(Enum):

    BOTH_ID_AND_NAME_NONE = (
        "Both id and name fields are null, you must specify one of them."
    )
    DRIVE_IDS_REQD_FOR_EXPAND = (
        "For expand operation drive_ids is a required field, which is missing."
    )
    STORAGE_POOL_NOT_FOUND = "Did not find storage pool named {}."
    NAMES_STR_OR_LIST = (
        "Eirther prvode a string for name field for getting information of a single storage pool,"
        "or provide a list of strings for getting information about multiple storage pools."
    )
    WRONG_POOL_ID = "Wrong pool id given, did not find storage pool with that ID."
