from dataclasses import dataclass, asdict
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass, base_dict_converter
except ImportError:
    from common_base_models import BaseDataClass, SingleBaseClass, base_dict_converter


@dataclass
class GADPairFactSpec:
    primary_volume_id: Optional[str] = None


@dataclass
class HostgroupSpec:
    id: Optional[int] = None
    name: Optional[str] = None
    enable_preferred_path: Optional[bool] = None
    port: Optional[str] = None
    resource_group_id: Optional[int] = None

@dataclass
class VspGadPairSpec:
    primary_storage_serial_number: Optional[str] = None
    primary_volume_id: Optional[str] = None
    consistency_group_id: Optional[str] = None
    allocate_new_consistency_group: Optional[bool] = None
    primary_hostgroups: Optional[List[HostgroupSpec]] = None
    secondary_storage_serial_number: Optional[str] = None
    secondary_pool_id: Optional[str] = None
    secondary_hostgroups: Optional[List[HostgroupSpec]] = None
    set_alua_mode: Optional[bool] = None
    primary_resource_group_name: Optional[str] = None
    secondary_resource_group_name: Optional[str] = None
    quorum_disk_id: Optional[str] = None
    remote_ucp_system: Optional[str] = None

    def __post_init__(self, **kwargs):
        if self.primary_hostgroups:
            self.primary_hostgroups = [HostgroupSpec(**x) for x in self.primary_hostgroups]
        if self.secondary_hostgroups:
            self.secondary_hostgroups = [HostgroupSpec(**x) for x in self.secondary_hostgroups]
        

@dataclass
class VspGadPairInfo(SingleBaseClass):
    resourceId: Optional[str] = None
    consistencyGroupId: Optional[int] = None
    copyPaceTrackSize: Optional[int] = None
    copyRate: Optional[int] = None
    mirrorUnitId: Optional[int] = None
    pairName: Optional[str] = None
    primaryHexVolumeId: Optional[str] = None
    primaryVSMResourceGroupName: Optional[str] = None
    primaryVirtualHexVolumeId: Optional[str] = None
    primaryVirtualStorageId: Optional[str] = None
    primaryVirtualVolumeId: Optional[int] = None
    primaryVolumeId: Optional[int] = None
    primaryVolumeStorageId: Optional[int] = None
    secondaryHexVolumeId: Optional[str] = None
    secondaryVSMResourceGroupName: Optional[str] = None
    secondaryVirtualHexVolumeId: Optional[str] = None
    secondaryVirtualStorageId: Optional[str] = None
    secondaryVirtualVolumeId: Optional[int] = None
    secondaryVolumeId: Optional[int] = None
    secondaryVolumeStorageId: Optional[int] = None
    status: Optional[str] = None
    svolAccessMode: Optional[str] = None
    type: Optional[str] = None
    entitlementStatus : Optional[str] = None
    storageId : Optional[str] = None
    subscriberId : Optional[str] = None
    partnerId : Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        gadPairInfo = kwargs.get("gadPairInfo")
        if gadPairInfo:
            for key, value in gadPairInfo.items():
                # if not hasattr(self, key):
                setattr(self, key, value)
                
    def to_dict(self) :

        data = base_dict_converter(self)
        if data.get("storage_id"):
            data.pop("storage_id", None)
        if data.get("resourceId"):
            data.pop("resourceId", None)
        # data["primary_vsm_resource_group_name"] = data.pop("primary_vsmresource_group_name", None)
        return data
    
@dataclass
class VspGadPairsInfo(BaseDataClass):
    data: List[VspGadPairInfo] = None