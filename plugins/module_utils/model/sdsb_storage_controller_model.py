from dataclasses import dataclass
from typing import Optional


@dataclass
class SDSBStorageControllerFactSpec:

    primary_fault_domain_id: Optional[str] = None
    primary_fault_domain_name: Optional[str] = None
    id: Optional[str] = None


@dataclass
class SDSBStorageControllerSpec:
    id: Optional[str] = None
    is_detailed_logging_mode: Optional[bool] = None

    def is_empty(self):
        if self.id is None and self.is_detailed_logging_mode is None:
            return True
        else:
            return False
