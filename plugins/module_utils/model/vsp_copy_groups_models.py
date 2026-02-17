from dataclasses import dataclass, asdict
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass
    from ..model.common_base_models import ConnectionInfo

except ImportError:
    from .common_base_models import BaseDataClass, SingleBaseClass
    from model.common_base_models import ConnectionInfo


@dataclass
class CopyGroupSpec(SingleBaseClass):
    secondary_connection_info: Optional[ConnectionInfo] = None
    secondary_storage_serial_number: Optional[int] = None
    copy_group_name: Optional[str] = None
    copy_pair_name: Optional[str] = None
    local_device_group_name: Optional[str] = None
    remote_device_group_name: Optional[str] = None
    replication_type: Optional[str] = None
    svol_operation_mode: Optional[str] = None
    is_svol_writable: Optional[bool] = False
    do_pvol_write_protect: Optional[bool] = False
    do_data_suspend: Optional[bool] = False
    do_failback: Optional[bool] = False
    failback_mirror_unit_number: Optional[int] = None
    is_consistency_group: Optional[bool] = False
    consistency_group_id: Optional[int] = None
    fence_level: Optional[str] = None
    copy_pace: Optional[int] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@dataclass
class CopyGroupsFactSpec(SingleBaseClass):
    secondary_connection_info: Optional[ConnectionInfo] = None
    secondary_storage_serial_number: Optional[int] = None
    copy_group_name: Optional[str] = None
    name: Optional[str] = None
    should_include_remote_replication_pairs: Optional[bool] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@dataclass
class CopyGroupInfo(SingleBaseClass):
    remoteMirrorCopyGroupId: str
    copyGroupName: str
    remoteStorageDeviceId: str
    localDeviceGroupName: str
    remoteDeviceGroupName: str
    muNumber: Optional[int] = None


@dataclass
class CopyGroupInfoList(BaseDataClass):
    data: List[CopyGroupInfo]


@dataclass
class DirectCopyPairInfo(SingleBaseClass):
    copyGroupName: str
    copyPairName: str
    remoteMirrorCopyPairId: str
    pvolLdevId: int
    svolLdevId: int
    pvolStatus: str
    svolStatus: str
    pvolStorageDeviceId: str
    svolStorageDeviceId: str

    consistencyGroupId: Optional[int] = None
    svolDifferenceDataManagement: Optional[str] = None
    svolProcessingStatus: Optional[str] = None
    quorumDiskId: Optional[int] = None
    pvolIOMode: Optional[str] = None
    svolIOMode: Optional[str] = None
    replicationType: Optional[str] = None
    fenceLevel: Optional[str] = None
    pvolDifferenceDataManagement: Optional[str] = None
    pvolProcessingStatus: Optional[str] = None
    pvolJournalId: Optional[int] = None
    svolJournalId: Optional[int] = None
    isAluaEnabled: Optional[bool] = None
    copyProgressRate: Optional[int] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class DirectCopyPairInfoList(BaseDataClass):
    data: List[DirectCopyPairInfo]


@dataclass
class DirectSpecificCopyGroupInfo(SingleBaseClass):
    remoteMirrorCopyGroupId: str
    copyGroupName: str
    remoteStorageDeviceId: str
    localDeviceGroupName: str
    remoteDeviceGroupName: str
    copyPairs: List[DirectCopyPairInfo]
    muNumber: Optional[int] = None

    def __init__(self, **kwargs):
        self.remoteMirrorCopyGroupId = kwargs.get("remoteMirrorCopyGroupId")
        self.copyGroupName = kwargs.get("copyGroupName")
        self.remoteStorageDeviceId = kwargs.get("remoteStorageDeviceId")
        self.localDeviceGroupName = kwargs.get("localDeviceGroupName")
        self.remoteDeviceGroupName = kwargs.get("remoteDeviceGroupName")
        if "copyPairs" in kwargs and kwargs.get("copyPairs") is not None:
            self.copyPairs = [
                DirectCopyPairInfo(**copyPair) for copyPair in kwargs.get("copyPairs")
            ]

    def to_dict(self):
        return asdict(self)


@dataclass
class DirectSpecificCopyGroupInfoList(BaseDataClass):
    data: List[DirectSpecificCopyGroupInfo]
