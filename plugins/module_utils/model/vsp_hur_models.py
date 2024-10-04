from dataclasses import dataclass, field, asdict
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass
    from ..common.ansible_common import dicts_to_dataclass_list

except ImportError:
    from .common_base_models import BaseDataClass, SingleBaseClass
    from common.ansible_common import dicts_to_dataclass_list


@dataclass
class HurHostGroupSpec:
    # id: int = None
    name: str = None
    port: str = None
    # resource_group_id: Optional[int] = None

    def to_dict(self):
        return asdict(self)

## 20240812 tag.HUR
@dataclass
class HurFactSpec(SingleBaseClass):
    primary_volume_id: Optional[int] = None
    secondary_volume_id: Optional[int] = None
    pvol: Optional[int] = None
    mirror_unit_id: Optional[int] = None

@dataclass
class HurSpec(SingleBaseClass):
    primary_volume_id: Optional[int] = None
    consistency_group_id: Optional[int] = None
    enable_delta_resync: Optional[bool] = None
    allocate_new_consistency_group: Optional[bool] = None
    secondary_storage_serial_number: Optional[int] = None
    secondary_pool_id: Optional[int] = None
    secondary_hostgroups: Optional[List[HurHostGroupSpec]] = None
    primary_volume_journal_id: Optional[int] = None
    secondary_volume_journal_id: Optional[int] = None
    mirror_unit_id: Optional[int] = None

    #Making a single hg
    secondary_hostgroup: Optional[HurHostGroupSpec] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "secondary_hostgroup" in kwargs and kwargs.get("secondary_hostgroup") is not None:
            self.secondary_hostgroups = [HurHostGroupSpec(**kwargs.get("secondary_hostgroup"))]


@dataclass
class VSPHurPairInfo(SingleBaseClass):
    resourceId: str
    consistencyGroupId: int
    copyRate: int
    fenceLevel: str
    mirrorUnitId: int
    pairName: str
    primaryVolumeId: int
    
    primaryVolumeStorageId: int
    secondaryVolumeId: int
    
    secondaryVolumeStorageId: int
    status: str
    svolAccessMode: str
    type: str
    
    # primaryHexVolumeId: Optional[str] = None
    # secondaryHexVolumeId: Optional[str] = None
    entitlementStatus: Optional[str] = None
    partnerId: Optional[str] = None
    subscriberId: Optional[str] = None
    

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        ## 20240814 Porcelain DTO: VSPHurPairInfo
        ## hur_pair_info is from v3 response
        hur_pair_info = kwargs.get("hurPairInfo")
        
        ## flattern the struct from v3
        if hur_pair_info:
            for field in self.__dataclass_fields__.keys():
                if not getattr(self, field):
                    setattr(self, field, hur_pair_info.get(field, None))
                    

    def to_dict(self):
        return asdict(self)
    
@dataclass
class VSPHurPairInfoList(BaseDataClass):
    data: List[VSPHurPairInfo]
