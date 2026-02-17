from dataclasses import dataclass
from typing import Optional

try:
    from .common_base_models import SingleBaseClass
    from ..common.ansible_common import normalize_ldev_id

except ImportError:
    from .common_base_models import SingleBaseClass
    from common.ansible_common import normalize_ldev_id


@dataclass
class VSPVcloneParentVolumeFactSpec(SingleBaseClass):
    vclone_volume_id: Optional[int] = None

    def __post_init__(self):
        if self.vclone_volume_id:
            self.vclone_volume_id = normalize_ldev_id(self.vclone_volume_id)
