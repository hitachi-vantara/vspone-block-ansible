from enum import Enum


class VSPSExternalParityGroupValidateMsg(Enum):
    CLPR_ID_REQD = "clpr_id is a required field, which is missing."
    MP_BLADE_ID_REQD = "mp_blade_id is a required field, which is missing."
    EXTERNAL_PARITY_GROUP_REQUIRED_FOR_DISCONNECT = "For disconnect operation, external_parity_group_id parameter is mandatory, which is not provided."
    PRESENT_STATE_FIELD_MISSING = (
        "For 'present' state, external_path_group_id, port_id, external_wwn, "
        "and lun_id are mandatory fields. One or more mandatory fields are missing."
    )
    EXTERNAL_PARITY_GROUP_CREATE_SUCCESS = (
        "External Parity Group has been successfully created."
    )
    ASSIGN_EXTERNAL_PARITY_GROUP_SUCCESS = (
        "External Parity Group has been successfully assigned to a CLPR."
    )
    EXTERNAL_PARITY_GROUP_ALREADY_ASSIGNED = (
        "External Parity Group is already assigned to the specified CLPR."
    )
    CHANGE_MP_BLADE_SUCCESS = (
        "Changed the MP blade assigned to an external parity group."
    )
    DISCONNECT_SUCCESS = "Volume disconnected from the external parity group."
    EXTERNAL_PARITY_GROUP_DELETE_SUCCESS = (
        "External Parity Group has been successfully deleted."
    )
