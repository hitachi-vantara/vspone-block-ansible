from enum import Enum


class VSPStoragePoolValidateMsg(Enum):
    EMPTY_POOL_ID = "pool_id is empty. Specify a value for pool_id or remove the parameter from the playbook."
