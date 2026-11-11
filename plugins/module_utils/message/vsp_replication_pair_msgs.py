from __future__ import absolute_import, division, print_function
__metaclass__ = type

from enum import Enum


class VSPReplicationPairValidateMsg(Enum):
    REPLICATION_PAIR_NOT_FOUND = (
        "Replication pair with copy_group_name {0} and copy_pair_name {1} not found."
    )
