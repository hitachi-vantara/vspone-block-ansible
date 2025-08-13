from dataclasses import dataclass, asdict
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass
except ImportError:
    from common_base_models import BaseDataClass, SingleBaseClass


@dataclass
class StorageNodeSpec:
    id: Optional[str] = None
    name: Optional[str] = None


@dataclass
class StorageNodeFactSpec:
    fault_domain_id: Optional[str] = None
    name: Optional[str] = None
    cluster_role: Optional[str] = None
    protection_domain_id: Optional[str] = None


@dataclass
class StorageNodeSpec:
    id: Optional[str] = None
    name: Optional[str] = None
    os_type: Optional[str] = None
    state: Optional[str] = None
    iscsi_initiators: Optional[List[str]] = None
    volumes: Optional[List[str]] = None
    host_nqns: Optional[List[str]] = None
    should_delete_all_volumes: Optional[bool] = False


@dataclass
class InsufficientResourcesForRebuildCapacity:
    capacityOfDrive: int = 0
    numberOfDrives: int = 0


@dataclass
class RebuildableResources:
    numberOfDrives: int = 0


@dataclass
class SDSBStorageNodeInfo(SingleBaseClass):
    id: str = None
    biosUuid: str = None
    protectionDomainId: str = None
    faultDomainId: str = None
    faultDomainName: str = None
    name: str = None
    clusterRole: str = None
    storageNodeAttributes: Optional[List[str]] = None
    statusSummary: str = None
    status: str = None
    driveDataRelocationStatus: str = None
    controlPortIpv4Address: str = None
    internodePortIpv4Address: str = None
    softwareVersion: str = None
    modelName: str = None
    serialNumber: str = None
    memory: int = 0
    insufficientResourcesForRebuildCapacity: InsufficientResourcesForRebuildCapacity = (
        None
    )
    rebuildableResources: RebuildableResources = None
    availabilityZoneId: str = None
    physicalZone: str = None
    logicalZone: str = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        super().__init__(**kwargs)

    # def __init__(self, **kwargs):
    #     self.id = kwargs.get("id")
    #     self.nickname = kwargs.get("nickname")
    #     self.osType = kwargs.get("osType")
    #     self.totalCapacity = kwargs.get("totalCapacity")
    #     self.usedCapacity = kwargs.get("usedCapacity")
    #     self.vpsId = kwargs.get("vpsId")
    #     self.vpsName = kwargs.get("vpsName")
    #     if "numberOfVolumes" in kwargs:
    #         self.numberOfVolumes = kwargs.get("numberOfVolumes")
    #     if "numberOfPaths" in kwargs:
    #         self.numberOfPaths = kwargs.get("numberOfPaths")
    #     # if "lun" in kwargs:
    #     #     self.lun = kwargs.get("lun")
    #     if "paths" in kwargs:
    #         self.paths = [Path(**path) for path in kwargs.get("paths")]

    def to_dict(self):
        return asdict(self)


@dataclass
class SDSBStorageNodeInfoList(BaseDataClass):
    data: List[SDSBStorageNodeInfo]
