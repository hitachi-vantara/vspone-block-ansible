from __future__ import absolute_import, division, print_function
__metaclass__ = type

from dataclasses import dataclass
from typing import Optional


@dataclass
class SDSBControlPortSpec:

    storage_node_id: Optional[str] = None
    storage_node_name: Optional[str] = None
    id: Optional[str] = None
