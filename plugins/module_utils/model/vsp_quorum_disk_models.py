from dataclasses import dataclass
from typing import Optional, List, Any

try:
    from .common_base_models import BaseDataClass, SingleBaseClass

except ImportError:
    from .common_base_models import BaseDataClass, SingleBaseClass


@dataclass
class HostgroupSpec:
    id: Optional[int] = None
    name: Optional[str] = None
    enable_preferred_path: Optional[bool] = None
    port: Optional[str] = None
    resource_group_id: Optional[int] = None


@dataclass
class ExtVolumeInfo(SingleBaseClass):
    externalLun: Optional[int] = None
    portId: Optional[str] = None
    externalWwn: Optional[str] = None
    externalVolumeCapacity: Optional[int] = None
    externalVolumeInfo: Optional[str] = None
    externalPathGroupId: int = None
    externalSerialNumber: str = None
    externalProductId: str = None
    externalVolumeCapacityInMb: Optional[int] = None
    externalLdevId: Optional[int] = None
    ldevIds: Optional[list[int]] = None


@dataclass
class ExtVolumeInfoList(BaseDataClass):
    data: List[ExtVolumeInfo]


@dataclass
class ExternalPathInfo(SingleBaseClass):
    portId: str
    externalWwn: str
    qDepth: str
    ioTimeOut: int
    blockedPathMonitoring: int


@dataclass
class ExternalPathInfoList(BaseDataClass):
    data: List[ExternalPathInfo]


@dataclass
class ExternalPathGroupInfo(SingleBaseClass):
    externalPathGroupId: int
    externalSerialNumber: str
    externalProductId: str
    externalParityGroups: List[Any]
    externalPaths: List[ExternalPathInfo]
    nextPageHeadPathGroupId: int


@dataclass
class ExternalPathGroupInfoList(BaseDataClass):
    data: List[ExternalPathGroupInfo]


@dataclass
class QuorumDiskInfo(SingleBaseClass):
    quorumDiskId: int
    remoteSerialNumber: str
    remoteStorageTypeId: str
    readResponseGuaranteedTime: int
    ldevId: Optional[int] = -1
    status: Optional[str] = ""


@dataclass
class QuorumDiskInfoList(BaseDataClass):
    data: List[QuorumDiskInfo]


@dataclass
class QuorumDiskSpec:

    secondary_storage_serial_number: Optional[str] = None
    remote_storage_serial_number: Optional[str] = None
    remote_storage_type: Optional[str] = None
    # local map of external volume
    ldev_id: Optional[int] = None
    # qrd id
    id: Optional[int] = None


@dataclass
class QuorumDiskFactSpec:
    id: Optional[int] = None
