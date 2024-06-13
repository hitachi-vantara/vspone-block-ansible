from dataclasses import dataclass, asdict
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass
except ImportError:
    from common_base_models import BaseDataClass, SingleBaseClass


@dataclass
class SnapshotFactSpec:
    pvol: Optional[int] = None
    mirror_unit_id: Optional[int] = None


@dataclass
class SnapshotReqData:
    pass


@dataclass
class SnapshotReconcileSpec:
    pvol: int
    pool_id: Optional[int] = None
    allocate_consistency_group: Optional[bool] = False
    enable_quick_mode: Optional[bool] = False
    consistency_group_id: Optional[int] = -1
    mirror_unit_id: Optional[int] = None
    state: Optional[str] = "present"
    snapshot_group_name: Optional[str] = None
    auto_split: Optional[bool] = None
    is_data_reduction_force_copy: Optional[bool] = None
    can_cascade: Optional[bool] = None


@dataclass
class DirectSnapshotInfo(SingleBaseClass):
    snapshotGroupName: Optional[str] = None
    primaryOrSecondary: Optional[str] = None
    status: Optional[str] = None
    pvolLdevId: Optional[int] = None
    muNumber: Optional[int] = None
    svolLdevId: Optional[int] = None
    snapshotPoolId: Optional[int] = None
    concordanceRate: Optional[int] = None
    isConsistencyGroup: Optional[bool] = None
    isWrittenInSvol: Optional[bool] = None
    isClone: Optional[bool] = None
    canCascade: Optional[bool] = None
    isRedirectOnWrite: Optional[bool] = None
    splitTime: Optional[str] = None
    snapshotId: Optional[str] = None
    pvolProcessingStatus: Optional[str] = None
    snapshotDataReadOnly: Optional[bool] = None
    resourceId: Optional[str] = None
    snapshotReplicationId: Optional[str] = None
    consistencyGroupId: Optional[int] = None


@dataclass
class DirectSnapshotsInfo(BaseDataClass):
    data: List[DirectSnapshotInfo]


@dataclass
class UAIGSnapshotInfo(SingleBaseClass):
    resourceId: Optional[str] = None
    storageSerialNumber: Optional[int] = None
    primaryVolumeId: Optional[int] = None
    primaryHexVolumeId: Optional[str] = None
    secondaryVolumeId: Optional[int] = None
    secondaryHexVolumeId: Optional[str] = None
    svolAccessMode: Optional[str] = None
    poolId: Optional[int] = None
    consistencyGroupId: Optional[int] = None
    mirrorUnitId: Optional[int] = None
    copyRate: Optional[int] = None
    copyPaceTrackSize: Optional[str] = None
    status: Optional[str] = None
    type: Optional[str] = None
    storageId: Optional[str] = None
    entitlementStatus: Optional[str] = None
    partnerId: Optional[str] = None
    subscriberId: Optional[str] = None
    # snapshotPairInfo: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        snapshot_pair_info = kwargs.get("snapshotPairInfo")
        if snapshot_pair_info:
            for field in self.__dataclass_fields__.keys():
                if not getattr(self, field):
                    setattr(self, field, snapshot_pair_info.get(field, None))

    def to_dict(self):
        return asdict(self)


@dataclass
class UAIGSnapshotsInfo(BaseDataClass):
    data: List[UAIGSnapshotInfo]
