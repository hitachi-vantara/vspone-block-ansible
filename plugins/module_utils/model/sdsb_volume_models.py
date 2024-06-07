from dataclasses import dataclass, asdict
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass
except ImportError:
    from common_base_models import BaseDataClass, SingleBaseClass


@dataclass
class VolumeFactSpec:
    count: Optional[int] = None
    names: Optional[List[str]] = None
    nicknames: Optional[List[str]] = None
    saving_setting: Optional[str] = None

@dataclass
class VolumeSpec:
    id: Optional[str] = None
    name: Optional[str] = None
    nickname: Optional[str] = None
    capacity: Optional[str] = None
    state: Optional[str] = None
    saving_setting: Optional[str] = None  
    pool_name: Optional[str] = None
    compute_nodes: Optional[List[str]] = None

@dataclass
class QosParam(SingleBaseClass):
    upperLimitForIops: int
    upperLimitForTransferRate: int
    upperAlertAllowableTime: int
    upperAlertTime: str = ""


@dataclass
class DataReductionEffects:
    dataReductionRate: int
    dataReductionCapacity: int
    compressedCapacity: int
    reclaimedCapacity: int
    systemDataCapacity: int
    preCapacityDataReductionWithoutSystemData: int
    postCapacityDataReduction: int


@dataclass
class Lun:
    lun: int
    serverId: str


@dataclass
class SDSBVolumeInfo(SingleBaseClass):

    dataReductionEffects: DataReductionEffects
    id: str
    name: str
    nickname: str
    volumeNumber: int
    poolId: str
    poolName: str
    totalCapacity: int
    usedCapacity: int
    numberOfConnectingServers: int
    numberOfSnapshots: int
    protectionDomainId: str
    fullAllocated: bool
    volumeType: str
    statusSummary: str
    status: str
    storageControllerId: str
    snapshotAttribute: str
    snapshotStatus: str
    savingSetting: str
    savingMode: str
    dataReductionStatus: str
    dataReductionProgressRate: str
    vpsId: str
    vpsName: str
    naaId: str
    qosParam: QosParam

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def to_dict(self):
        return asdict(self)


@dataclass
class SDSBVolumesInfo(BaseDataClass):
    data: List[SDSBVolumeInfo]

@dataclass
class ComputeNodeSummaryInfo:
    id: str
    name: str

@dataclass
class SDSBVolumeAndComputeNodeInfo(SingleBaseClass):
    volumeInfo:SDSBVolumeInfo
    computeNodeInfo: List[ComputeNodeSummaryInfo]

    def to_dict(self):
        return asdict(self)
    
@dataclass
class SDSBVolumeAndComputeNodeList(BaseDataClass):
    data: List[SDSBVolumeAndComputeNodeInfo]