from enum import Enum


class VSPParityGroupValidateMsg(Enum):
    EMPTY_PARITY_GROUP_ID = "parity_group_id is empty. Specify a value for parity_group_id or remove the parameter from the playbook."
