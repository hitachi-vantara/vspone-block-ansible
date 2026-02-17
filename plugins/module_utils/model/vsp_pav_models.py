from dataclasses import dataclass
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass
except ImportError:
    from common_base_models import BaseDataClass, SingleBaseClass


@dataclass
class VSPPavLdevResponse(SingleBaseClass):
    cuNumber: Optional[int] = None
    ldevId: Optional[int] = None
    pavAttribute: Optional[str] = None
    cBaseVolumeId: Optional[int] = None
    sBaseVolumeId: Optional[int] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@dataclass
class VSPPavLdevResponseList(BaseDataClass):
    data: List[VSPPavLdevResponse] = None


@dataclass
class VSPPavLdevRequestSpec(SingleBaseClass):
    alias_ldev_ids: List[int]
    base_ldev_id: int
    comment: Optional[str] = None


@dataclass
class VSPPavLdevFactsSpec(SingleBaseClass):
    cu_number: Optional[int] = None
    base_ldev_id: Optional[int] = None
    alias_ldev_id: Optional[int] = None

    def __post_init__(self):
        if (
            self.cu_number is not None
            and self.base_ldev_id is not None
            and self.alias_ldev_id is not None
        ):
            raise ValueError(
                "Only one of 'cu_number', 'base_ldev_id', or 'alias_ldev_id' should be provided."
            )
