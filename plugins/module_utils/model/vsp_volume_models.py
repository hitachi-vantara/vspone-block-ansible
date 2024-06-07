from dataclasses import dataclass, asdict
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass
except ImportError:
    from common_base_models import BaseDataClass, SingleBaseClass


@dataclass
class VolumeFactSpec:
    lun: Optional[str] = None
    name: Optional[str] = None
    count: Optional[int] = None
    end_ldev_id: Optional[int] = None
    start_ldev_id: Optional[str] = None


@dataclass
class CreateVolumeSpec:
    name: Optional[str] = None
    size: Optional[str] = None
    lun: Optional[str] = None
    pool_id: Optional[int] = None
    capacity_saving: Optional[str] = None
    parity_group: Optional[str] = None


@dataclass
class VSPVolumeInfo(SingleBaseClass):
    ldevId: int
    clprId: int
    emulationType: str
    byteFormatCapacity: Optional[str] = None
    blockCapacity: Optional[int] = None
    composingPoolId: Optional[int] = None
    attributes: Optional[List[str]] = None
    raidLevel: Optional[str] = None
    raidType: Optional[str] = None
    numOfParityGroups: Optional[int] = None
    parityGroupIds: Optional[List[str]] = None
    driveType: Optional[str] = None
    driveByteFormatCapacity: Optional[str] = None
    driveBlockCapacity: Optional[int] = None
    label: Optional[str] = None
    status: Optional[str] = None
    mpBladeId: Optional[int] = None
    ssid: Optional[str] = None
    resourceGroupId: Optional[int] = None
    isAluaEnabled: Optional[bool] = None
    numOfPorts: Optional[int] = None
    ports: Optional[List[str]] = None
    virtualLdevId: Optional[int] = None
    poolId: Optional[int] = None
    numOfUsedBlock: Optional[int] = None
    dataReductionMode: Optional[str] = None
    dataReductionStatus: Optional[str] = None
    dataReductionProcessMode: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@dataclass
class VSPVolumesInfo(BaseDataClass):
    data: List[VSPVolumeInfo]
