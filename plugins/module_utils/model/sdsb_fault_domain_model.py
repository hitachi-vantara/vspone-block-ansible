from __future__ import absolute_import, division, print_function
__metaclass__ = type

from dataclasses import dataclass
from typing import Optional


@dataclass
class SDSBFaultDomainSpec:
    """Block Drives Facts Specification"""

    id: Optional[str] = None
    name: Optional[str] = None
