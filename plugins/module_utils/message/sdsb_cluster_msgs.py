from enum import Enum


class SDSBClusterValidationMsg(Enum):
    NO_NAME_OR_ID_FOR_STORAGE_NODE = "Either node_name or node_id of the storage node must be specified to do this operation."
    STORAGE_NODE_NOT_FOUND = "Did not find storage node named {}."
    STORAGE_NODE_SETUP_PASSWD_REQD = (
        "Storage node setup_user_password is a required field, which is missing."
    )
    CONFIG_FILE_DOES_NOT_EXIST = (
        "File path ({}) provided for the configuration_file does not exist."
    )
