from enum import Enum


class VSPStoragePoolValidateMsg(Enum):
    EMPTY_POOL_ID = "pool_id is empty. Specify a value for pool_id or remove the parameter from the playbook."
    BOTH_POOL_ID_AND_NAME = "Both id and name are specified. Specify only one of them."
    PG_ID_CAPACITY = "missing both capacity and parity_group_id in pool_volumes. Specify both values or pool_volumes parameter"
    MISSING_CAPACITY = "capacity is missing in pool_volumes. Specify the capacity value for {} parity_group_id."
    MISSING_PG_ID = "parity_group_id is missing in pool_volumes. Specify the parity_group_id where capacity is {}."
    POOL_SIZE_MIN = "The capacity must be at least 8GB."
    POOL_DOES_NOT_EXIST = "The specified pool does not exist."
    POOL_NAME_REQUIRED = "The name of the pool is required for new pool creation."
    POOL_TYPE_REQUIRED = "The type of the pool is required for new pool creation."
    POOL_VOLUME_REQUIRED = "Pool volumes are required for new pool creation."
