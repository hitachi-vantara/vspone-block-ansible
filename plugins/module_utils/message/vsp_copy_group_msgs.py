from enum import Enum


class CopyGroupFailedMsg(Enum):
    NOT_SUPPORTED_FOR_UAI_GATEWAY = (
        "Copy group {} operation is not supported by UAI Gateway."
    )


class VSPCopyGroupsValidateMsg(Enum):
    SECONDARY_CONNECTION_INFO = "secondary_connection_info is a required field for direct connect, which is missing."
    COPY_GROUP_NOT_FOUND = "Could not find remote copy group by name {}."
