from enum import Enum


class SDSBVolumeMessage(Enum):
    pass


class SDSBVolValidationMsg(Enum):

    SAVING_SETTING = "This module only accepts Disabled or Compression for saving_setting field."
    CAPACITY = "capacity must be provided while creating a volume."
    CAPACITY_UNITS = "This module only accepts MB, GB, or TB for capacity field."
    POOL_NAME_EMPTY = "pool_name must be provided while creating a volume."
    POOL_NAME_NOT_FOUND = "Pool name {0} not found."
    NO_NAME_ID = "Either volume ID or volume name must be provided."
    VOL_ID_ABSENT = "Could not find volume with ID {0}."
    NO_SPEC = "Specifications for the volume are not provided."
    COMPUTE_NODES_EXIST = "Ensure all compute node names provided in the spec are present in the system."
    INVALID_CAPACITY = "Volume capacity specified is less than the actual volume capacity. Provide a capacity greater than the actual capacity."
    CONTRADICT_INFO = "Contradicting information provided in the spec. Volume name does not exist in the system, and spec.state is set to remove_compute_node."

