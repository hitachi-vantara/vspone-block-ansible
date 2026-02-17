from dataclasses import dataclass
from typing import Optional

try:
    from .common_base_models import SingleBaseClass
    from ..common.ansible_common import normalize_ldev_id

except ImportError:
    from .common_base_models import SingleBaseClass
    from common.ansible_common import normalize_ldev_id


@dataclass
class VSPSnapshotFamilyFactSpec(SingleBaseClass):
    ldev_id: Optional[int] = None

    def __post_init__(self):
        if self.ldev_id:
            self.ldev_id = normalize_ldev_id(self.ldev_id)
