from dataclasses import dataclass, asdict
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass
except ImportError:
    from common_base_models import BaseDataClass, SingleBaseClass


@dataclass
class GetShadowImageSpec:
    pvol: Optional[int] = None
    #svol: Optional[int] = None


@dataclass
class VSPShadowImagePairInfo(SingleBaseClass):
    resourceId: Optional[str] = None
    consistencyGroupId: Optional[int] = None
    copyPaceTrackSize: Optional[str] = None
    copyRate: Optional[int] = None
    mirrorUnitId: Optional[int] = None
    primaryHexVolumeId: Optional[str] = None
    primaryVolumeId: Optional[int] = None
    storageSerialNumber: Optional[str] = None
    secondaryHexVolumeId: Optional[str] = None
    secondaryVolumeId: Optional[int] = None
    status: Optional[int] = None
    svolAccessMode: Optional[str] = None
    type: Optional[str] = None
    entitlementStatus: Optional[str] = None
    partnerId: Optional[str] = None
    subscriberId: Optional[str] = None
    __pvolMuNumber: Optional[int] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        shadow_image_info = kwargs.get("shadowImageInfo")
        if shadow_image_info:
            for field in self.__dataclass_fields__.keys():
                if not getattr(self, field):
                    setattr(self, field, shadow_image_info.get(field, None))

            self.type = shadow_image_info.get("type", None)

    def to_dict(self):
        return asdict(self)


@dataclass
class VSPShadowImagePairsInfo(BaseDataClass):
    data: List[VSPShadowImagePairInfo]


@dataclass
class ShadowImagePairSpec:
    pvol: Optional[int] = None
    svol: Optional[int] = None
    auto_split: Optional[bool] = None
    new_consistency_group: Optional[bool] = None
    consistency_group_id: Optional[int] = None
    copy_pace_track_size: Optional[str] = None
    enable_quick_mode: Optional[bool] = None
    enable_read_write: Optional[bool] = None
    copy_pace: Optional[str] = None
    is_data_reduction_force_copy: Optional[bool] = None
    pair_id: Optional[str] = None


@dataclass
class UaigResourceMappingInfo:
    deviceId: Optional[str] = None
    resourceId: Optional[str] = None
    partnerId: Optional[str] = None
    subscriberId: Optional[str] = None
    type: Optional[str] = None
    resourceValue: Optional[str] = None
    time: Optional[float] = None
    totalCapacity: Optional[str] = None

    def to_dict(self):
        return asdict(self)
