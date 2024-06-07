from dataclasses import dataclass, asdict, fields
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass
except ImportError:
    from common_base_models import BaseDataClass, SingleBaseClass


@dataclass
class PoolFactSpec:
    pool_id: Optional[int] = None


@dataclass
class VSPPfrestStoragePool(SingleBaseClass):
    poolId: int = None
    poolName: str = None
    poolType: str = None
    poolStatus: str = None
    usedCapacityRate: int = None
    availableVolumeCapacity: int = None
    totalPoolCapacity: int = None
    totalLocatedCapacity: int = None
    warningThreshold: int = None
    depletionThreshold: int = None
    virtualVolumeCapacityRate: int = None
    locatedVolumeCount: int = None
    snapshotCount: int = None
    isShrinking: bool = None

    # Not used info
    # usedPhysicalCapacityRate: int = None
    # availablePhysicalVolumeCapacity: int = None
    # totalPhysicalCapacity: int = None
    # numOfLdevs: int = None
    # firstLdevId: int = None
    # suspendSnapshot: bool = None
    # snapshotUsedCapacity: int = None
    # blockingMode: str = None
    # totalReservedCapacity: int = None
    # reservedVolumeCount: int = None
    # poolActionMode: str = None
    # monitoringMode: str = None
    # tierOperationStatus: str = None
    # dat: str = None
    # tiers: List[tier_object] = None
    # duplicationLdevIds: List[int] = None
    # duplicationNumber: int = None
    # dataReductionAccelerateCompCapacity: int = None
    # dataReductionCapacity: int = None
    # dataReductionBeforeCapacity: int = None
    # dataReductionAccelerateCompRate: int = None
    # dataReductionRate: int = None
    # dataReductionAccelerateCompIncludingSystemData: dataReductionAccelerateCompIncludingSystemData_object = None
    # dataReductionIncludingSystemData: dataReductionIncludingSystemData_object = None
    # capacitiesExcludingSystemData: capacitiesExcludingSystemData_object = None
    # compressionRate: int = None
    # duplicationRate: int = None
    # isMainframe: bool = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@dataclass
class VSPPfrestStoragePoolList(BaseDataClass):
    data: List[VSPPfrestStoragePool] = None


@dataclass
class VSPPfrestLdev(SingleBaseClass):
    ldevId: int = None
    blockCapacity: int = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@dataclass
class VSPPfrestLdevList(BaseDataClass):
    data: List[VSPPfrestLdev] = None


@dataclass
class VSPDpVolume(SingleBaseClass):
    logicalUnitId: int = None
    size: int = None


@dataclass
class VSPStoragePool(SingleBaseClass):
    poolId: int = None
    poolName: str = None
    poolType: str = None
    status: str = None
    utilizationRate: int = None
    freeCapacity: int = None
    freeCapacityInUnits: str = None
    totalCapacity: int = None
    totalCapacityInUnit: str = None
    warningThresholdRate: int = None
    depletionThresholdRate: int = None
    subscriptionLimitRate: int = None
    virtualVolumeCount: int = None
    subscriptionRate: int = None
    ldevIds: List[int] = None
    dpVolumes: List[VSPDpVolume] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@dataclass
class VSPStoragePools(BaseDataClass):
    data: List[VSPStoragePool] = None
