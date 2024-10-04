from dataclasses import dataclass, field, asdict
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass
    from ..common.ansible_common import dicts_to_dataclass_list

except ImportError:
    from .common_base_models import BaseDataClass, SingleBaseClass
    from common.ansible_common import dicts_to_dataclass_list

@dataclass
class TrueCopyFactSpec(SingleBaseClass):
    primary_volume_id: Optional[int] = None
    secondary_volume_id: Optional[int] = None

@dataclass
class TrueCopyHostGroupSpec:
    # id: int = None
    name: str = None
    port: str = None
    # resource_group_id: Optional[int] = None

    def to_dict(self):
        return asdict(self)

@dataclass
class TrueCopySpec(SingleBaseClass):
    primary_volume_id: Optional[int] = None
    consistency_group_id: Optional[int] = None
    fence_level: Optional[str] = None
    allocate_new_consistency_group: Optional[bool] = None
    secondary_storage_serial_number: Optional[int] = None
    secondary_pool_id: Optional[int] = None
    secondary_hostgroups: Optional[List[TrueCopyHostGroupSpec]] = None

    #Making a single hg
    secondary_hostgroup: Optional[TrueCopyHostGroupSpec] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "secondary_hostgroup" in kwargs and kwargs.get("secondary_hostgroup") is not None:
            self.secondary_hostgroups = [TrueCopyHostGroupSpec(**kwargs.get("secondary_hostgroup"))]

@dataclass
class VSPReplicationPairInfo():
    resourceId: str
    consistencyGroupId: int
    copyPaceTrackSize: int
    copyRate: int
    mirrorUnitId: int
    pairName: str
    primaryHexVolumeId: str
    primaryVSMResourceGroupName: str
    primaryVirtualHexVolumeId: str
    primaryVirtualStorageId: str
    primaryVirtualVolumeId: int
    primaryVolumeId: int
    primaryVolumeStorageId: int
    secondaryHexVolumeId: str
    secondaryVSMResourceGroupName: str  
    secondaryVirtualStorageId: str
    secondaryVirtualVolumeId: int
    secondaryVolumeId: int
    secondaryVolumeStorageId: int
    status: str
    svolAccessMode: str
    type: str
    secondaryVirtualHexVolumeId: int = None

    def __init__(self, **kwargs):
        self.resourceId = kwargs.get("resourceId")
        self.consistencyGroupId = kwargs.get("consistencyGroupId")
        self.copyPaceTrackSize = kwargs.get("copyPaceTrackSize")
        self.copyRate = kwargs.get("copyRate")
        self.mirrorUnitId = kwargs.get("mirrorUnitId")
        self.pairName = kwargs.get("pairName")
        self.primaryHexVolumeId = kwargs.get("primaryHexVolumeId")
        self.primaryVSMResourceGroupName = kwargs.get("primaryVSMResourceGroupName")
        self.primaryVirtualHexVolumeId = kwargs.get("primaryVirtualHexVolumeId")
        self.primaryVirtualStorageId = kwargs.get("primaryVirtualStorageId")
        self.primaryVirtualVolumeId = kwargs.get("primaryVirtualVolumeId")
        self.primaryVolumeId = kwargs.get("primaryVolumeId")
        self.primaryVolumeStorageId = kwargs.get("primaryVolumeStorageId")
        self.secondaryHexVolumeId = kwargs.get("secondaryHexVolumeId")
        self.secondaryVSMResourceGroupName = kwargs.get("secondaryVSMResourceGroupName")
        self.secondaryVirtualStorageId = kwargs.get("secondaryVirtualStorageId")
        self.secondaryVirtualVolumeId = kwargs.get("secondaryVirtualVolumeId")
        self.secondaryVolumeId = kwargs.get("secondaryVolumeId")
        self.secondaryVolumeStorageId = kwargs.get("secondaryVolumeStorageId")
        self.status = kwargs.get("status")
        self.svolAccessMode = kwargs.get("svolAccessMode")
        self.type =  kwargs.get("type")  
        if "secondaryVirtualHexVolumeId" in kwargs:
            self.secondaryVirtualHexVolumeId = kwargs.get("secondaryVirtualHexVolumeId")

    def to_dict(self):
        return asdict(self)
    
@dataclass
class VSPReplicationPairInfoList(BaseDataClass):
    data: List[VSPReplicationPairInfo]

@dataclass
class VSPTrueCopyPairInfo(SingleBaseClass):
    resourceId: str
    type: str
    resourceId: str
    storageId: str
    entitlementStatus: str
    consistencyGroupId: int
    copyRate: int
    mirrorUnitId: int
    pairName: str
    primaryVolumeId: int
    primaryVolumeStorageId: int
    secondaryVolumeId: int
    secondaryVolumeStorageId: int
    status: str
    svolAccessMode: str
    type: str
    partnerId: str
    subscriberId: str

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        tc_pair_info = kwargs.get("trueCopyPairInfo")
        if tc_pair_info:
            self.consistencyGroupId = tc_pair_info.get("consistencyGroupId", -1)
            self.copyRate = tc_pair_info.get("copyRate", -1)
            self.mirrorUnitId = tc_pair_info.get("mirrorUnitId", 0)
            self.pairName = tc_pair_info.get("pairName", "")
            self.primaryVolumeId = tc_pair_info.get("primaryVolumeId", -1)
            self.primaryVolumeStorageId = tc_pair_info.get("primaryVolumeStorageId", -1)
            self.secondaryVolumeId = tc_pair_info.get("secondaryVolumeId", -1)
            self.secondaryVolumeStorageId = tc_pair_info.get("secondaryVolumeStorageId", -1)
            self.status = tc_pair_info.get("status", "")
            self.svolAccessMode = tc_pair_info.get("svolAccessMode", "")

            for field in self.__dataclass_fields__.keys():
                if not getattr(self, field):
                    setattr(self, field, tc_pair_info.get(field, None))

@dataclass
class VSPTrueCopyPairInfoList(BaseDataClass):
    data: List[VSPTrueCopyPairInfo]
