from dataclasses import dataclass
from typing import Optional


@dataclass
class SDSBBlockDrivesSpec:
    """Block Drives Facts Specification"""

    status_summary: Optional[str] = None
    status: Optional[str] = None
    storage_node_id: Optional[str] = None
    locator_led_status: Optional[str] = None
