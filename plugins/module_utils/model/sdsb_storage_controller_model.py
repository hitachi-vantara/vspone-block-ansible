from dataclasses import dataclass
from typing import Optional


@dataclass
class SDSBStorageControllerSpec:
    """Block Drives Facts Specification"""

    primary_fault_domain_id: Optional[str] = None
    primary_fault_domain_name: Optional[str] = None
    id: Optional[str] = None
