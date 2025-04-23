from enum import Enum


class CopyGroupFailedMsg(Enum):
    NOT_SUPPORTED_FOR_UAI_GATEWAY = (
        "Copy group {} operation is not supported by UAI Gateway."
    )


class VSPCopyGroupsValidateMsg(Enum):
    SECONDARY_CONNECTION_INFO = "secondary_connection_info is a required field for direct connect, which is missing."
    COPY_GROUP_NOT_FOUND = "Could not find remote copy group by name {}."
    LOCAL_COPY_GROUP_NOT_FOUND = "Could not find local copy group by name {}."
    GROUP_SPLIT_FAILED = "Failed to split the copy group."
    GROUP_RESYNC_FAILED = "Failed to resync the copy group."
    GROUP_RESTORE_FAILED = "Failed to restore the copy group."
    GROUP_DELETE_FAILED = "Failed to delete the copy group."
    NO_PVOL_DEVICE_NAME_FOUND = "Incorrect pvol_device_group_name for existing copy_group {}. Provide correct existing value {}."
    NO_SVOL_DEVICE_NAME_FOUND = "Incorrect svol_device_group_name for existing copy_group {}. Provide correct existing value {}."
