from enum import Enum
from ..common.hv_constants import LdevConstants


class VSPIscsiTargetMessage(Enum):
    PORT_TYPE_INVALID = "The port type is not valid for this operation."
    PORTS_PARAMETER_INVALID = "iSCSI target does not exist; cannot create iSCSI targets without ports parameter."
    ISCSI_TARGET_HAS_BEEN_DELETED = (
        "ISCSI target {} not found on port {}. (Perhaps it has already been deleted.)"
    )
    IQN_IS_NOT_IN_ISCSI_TARGET = "The IQN initiator is not in the iSCSI target."
    LUN_IS_NOT_IN_ISCSI_TARGET = "The LUN is not in the iSCSI target."
    CHAP_USER_IS_NOT_IN_ISCSI_TARGET = "The CHAP user is not in the iSCSI target."
    SPEC_STATE_INVALID = "The spec state '{}' parameter is invalid."
    LDEVS_PRESENT = "The iSCSI target {} on port {} has LDEVs presented. Make sure to unpresent all LDEV prior to deleting the iSCSI target."
    RESOURCE_PRESENT = "The resource is already present."
    CATCH_MSG_ISCSI_TARGET = "The specified target alias cannot be registered because it is already used on the same port"
    RELEASE_HOST_RESERVE = "Release host reservation status is done"
    RELEASE_HOST_RESERVE_LU = (
        "Release host reservation status is done for the logical unit {}"
    )
    ADD_LUN_FAILED = "Failed to add LUN {} error: {}"
    ADD_LUN_PATH_FAILED = "Failed to add LUN path, ldev_id: {} lun_id: {} error: {}"
    PORT_NOT_FOUND = "Port {} is not in the storage system."
    UNSUPPORTED_STATE = "Unsupported state: {}. Supported states are present, absent, added, removed and updated."
    ISCSI_TARGET_NOT_FOUND = "iSCSI target {} is not found."
    NOT_ISCSI_PORTS = "Ports {} are not iSCSI ports."
    ISCSI_TARGET_NOT_FOUND_FOR_UPDATE = (
        "iSCSI target with name {} or id {} not found on port {} for update."
    )
    ISCSI_TARGET_CREATED = "iSCSI target {} is created on port {} successfully."
    ISCSI_OPERATION_SUCCESSFUL = (
        "Operation on iSCSI target {} on port {} is successful."
    )
    ISCSI_DELETE_SUCCESSFUL = (
        "Delete operation on iSCSI target {} on port {} is successful."
    )
    ISCSI_HOST_MODE_UPDATED = "Updated host mode to {} with options {}."
    ADD_LUN_SUCCESS = "Attached LDEVs {} successfully to iSCSI target."
    DELETE_LUN_SUCCESS = "Detached LDEVs {} successfully from iSCSI target."
    ADD_LUN_PATH_SUCCESS = "Added LUN paths successfully, lun_paths: {}."
    DELETE_LUN_PATH_SUCCESS = "Deleted LUN paths successfully, lun_paths: {}."
    ADD_IQN_SUCCESS = "Added IQN initiators successfully, iqns: {}."
    DELETE_IQN_SUCCESS = "Deleted IQN initiators successfully, iqns: {}."
    ADD_CHAP_USER_SUCCESS = "Added CHAP users successfully, chap_users: {}."
    DELETE_CHAP_USER_SUCCESS = "Deleted CHAP users successfully, chap_users: {}."


class VSPIscsiTargetValidationMsg(Enum):
    IQN_OUT_OF_RANGE = (
        "The IQN initiator is out of range. Specify a value in the range of 5 to 223."
    )
    ISCSI_NAME_OUT_OF_RANGE = "The iSCSI target name is out of range. Specify a value in the range of 1 to 32."
    CHAP_USER_NAME_OUT_OF_RANGE = (
        "The CHAP user name is out of range. Specify a value in the range of 1 to 223."
    )
    CHAP_SECRET_OUT_OF_RANGE = (
        "The CHAP secret is out of range. Specify a value in the range of 12 to 32."
    )
    LUN_OUT_OF_RANGE = f"The LUN is out of range. Specify a value in the range of 1 to {LdevConstants.MAX_VALID_LDEV_ID}."
    PORT_OUT_OF_RANGE = (
        "The port is out of range. Specify a value in the range of 1 to 256."
    )
    HOST_MODE_OUT_OF_RANGE = (
        "The host mode is out of range. Specify a value in the range of 1 to 256."
    )
