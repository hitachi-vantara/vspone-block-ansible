from dataclasses import dataclass, asdict
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass
    from ..message.vsp_hur_msgs import VspRemoteReplicationMsg, VSPHurValidateMsg
    from ..model.common_base_models import ConnectionInfo
    from ..common.ansible_common import normalize_ldev_id, normalize_copy_pace

except ImportError:
    from .common_base_models import BaseDataClass, SingleBaseClass
    from ..message.vsp_hur_msgs import VspRemoteReplicationMsg, VSPHurValidateMsg
    from model.common_base_models import ConnectionInfo
    from common.ansible_common import normalize_ldev_id, normalize_copy_pace


@dataclass
class TrueCopyFactSpec(SingleBaseClass):
    primary_volume_id: Optional[int] = None
    secondary_volume_id: Optional[int] = None
    copy_group_name: Optional[str] = None
    copy_pair_name: Optional[str] = None
    local_device_group_name: Optional[str] = None
    remote_device_group_name: Optional[str] = None
    secondary_connection_info: Optional[ConnectionInfo] = None

    def __post_init__(self):
        if self.primary_volume_id:
            self.primary_volume_id = normalize_ldev_id(self.primary_volume_id)
        if self.secondary_volume_id:
            self.secondary_volume_id = normalize_ldev_id(self.secondary_volume_id)


@dataclass
class TrueCopyHostGroupSpec:
    # id: Optional[int] = None
    name: Optional[str] = None
    port: Optional[str] = None
    port_id: Optional[str] = None
    lun_id: Optional[int] = None
    # resource_group_id: Optional[int] = None

    def __post_init__(self):
        if self.port_id:
            self.port = str(self.port_id)

    def to_dict(self):
        return asdict(self)


@dataclass
class NVMeSubsystemSpec:
    id: Optional[int] = None
    name: Optional[str] = None
    paths: Optional[List[str]] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class TrueCopySpec:
    data_reduction_share: Optional[bool] = None
    primary_volume_id: Optional[int] = None
    consistency_group_id: Optional[int] = None
    fence_level: Optional[str] = None
    allocate_new_consistency_group: Optional[bool] = None
    secondary_storage_serial_number: Optional[int] = None
    secondary_pool_id: Optional[int] = None
    secondary_hostgroups: Optional[List[TrueCopyHostGroupSpec]] = None
    secondary_iscsi_targets: Optional[List[TrueCopyHostGroupSpec]] = None
    secondary_connection_info: Optional[ConnectionInfo] = None
    secondary_volume_id: Optional[int] = None
    # Making a single hg
    secondary_hostgroup: Optional[TrueCopyHostGroupSpec] = None
    secondary_nvm_subsystem: Optional[NVMeSubsystemSpec] = None

    # These fields are required for the Direcr connection
    copy_group_name: Optional[str] = None
    copy_pair_name: Optional[str] = None
    # replication_type: Optional[str] = None  # we will assign this field to TC
    # remoteStorageDeviceId: Optional[str] = None # from the secondary_storage_serial_number we will find this
    # pvolLdevId : primary_volume_id will be assigned to this field
    # svolLdevId : secondary_volume_id will be assigned to this field
    is_new_group_creation: Optional[bool] = None

    # Optional fields
    path_group_id: Optional[int] = None
    local_device_group_name: Optional[str] = None
    remote_device_group_name: Optional[str] = None
    is_consistency_group: Optional[bool] = False
    copy_pace: Optional[int] = None
    do_initial_copy: Optional[bool] = True
    is_data_reduction_force_copy: Optional[bool] = False
    is_svol_readwriteable: Optional[bool] = False
    new_volume_size: Optional[str] = None
    begin_secondary_volume_id: Optional[int] = None
    end_secondary_volume_id: Optional[int] = None
    should_delete_svol: Optional[bool] = False
    provisioned_secondary_volume_id: Optional[int] = None
    comments: Optional[str] = None

    def __post_init__(self):
        if self.secondary_hostgroup:
            self.secondary_hostgroup = [
                TrueCopyHostGroupSpec(**self.secondary_hostgroup)
            ]
        if self.secondary_hostgroups:
            self.secondary_hostgroups = [
                TrueCopyHostGroupSpec(**x) for x in self.secondary_hostgroups
            ]
        if self.secondary_iscsi_targets:
            self.secondary_iscsi_targets = [
                TrueCopyHostGroupSpec(**x) for x in self.secondary_iscsi_targets
            ]
        if self.secondary_nvm_subsystem:
            self.secondary_nvm_subsystem = NVMeSubsystemSpec(
                **self.secondary_nvm_subsystem
            )
        if self.secondary_connection_info:
            self.secondary_connection_info = ConnectionInfo(
                **self.secondary_connection_info
            )

        if self.primary_volume_id:
            self.primary_volume_id = normalize_ldev_id(self.primary_volume_id)

        if self.secondary_volume_id:
            self.secondary_volume_id = normalize_ldev_id(self.secondary_volume_id)

        if self.begin_secondary_volume_id:
            self.begin_secondary_volume_id = normalize_ldev_id(
                self.begin_secondary_volume_id
            )
        if self.end_secondary_volume_id:
            self.end_secondary_volume_id = normalize_ldev_id(
                self.end_secondary_volume_id
            )
        if self.provisioned_secondary_volume_id:
            self.provisioned_secondary_volume_id = normalize_ldev_id(
                self.provisioned_secondary_volume_id
            )

        if self.copy_pace is not None:
            self.copy_pace = normalize_copy_pace(self.copy_pace)


@dataclass
class VSPReplicationPairInfo:
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
        self.type = kwargs.get("type")
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
            self.secondaryVolumeStorageId = tc_pair_info.get(
                "secondaryVolumeStorageId", -1
            )
            self.status = tc_pair_info.get("status", "")
            self.svolAccessMode = tc_pair_info.get("svolAccessMode", "")

            for field in self.__dataclass_fields__.keys():
                if not getattr(self, field):
                    setattr(self, field, tc_pair_info.get(field, None))


@dataclass
class VSPTrueCopyPairInfoList(BaseDataClass):
    data: List[VSPTrueCopyPairInfo]


@dataclass
class DirectTrueCopyPairInfo(SingleBaseClass):
    replicationType: str
    ldevId: int
    remoteSerialNumber: str
    remoteStorageTypeId: str
    remoteLdevId: int
    primaryOrSecondary: str
    muNumber: int
    status: str
    serialNumber: str
    storageTypeId: str
    isMainframe: bool


@dataclass
class DirectTrueCopyPairInfoList(BaseDataClass):
    data: List[VSPTrueCopyPairInfo]


@dataclass
class TrueCopyBatchSpec(TrueCopySpec):
    number_of_pairs: Optional[int] = None
    begin_primary_volume_id: Optional[int] = None
    end_primary_volume_id: Optional[int] = None
    primary_volume_base_name: Optional[str] = None
    capacity_saving: Optional[str] = None
    primary_volume_base_name_start_number: Optional[int] = None
    primary_volume_base_name_number_of_digits: Optional[int] = None
    volume_size: Optional[str] = None
    primary_pool_id: Optional[int] = None
    is_compression_acceleration_enabled: Optional[bool] = None

    primary_hostgroups: Optional[List[TrueCopyHostGroupSpec]] = None
    primary_iscsi_targets: Optional[List[TrueCopyHostGroupSpec]] = None
    primary_nvm_subsystem: Optional[NVMeSubsystemSpec] = None

    copy_pair_base_name: Optional[str] = None
    comments: Optional[List[str]] = None

    def __post_init__(self, **kwargs):
        super().__post_init__(**kwargs)

        if self.primary_hostgroups:
            self.primary_hostgroups = [
                TrueCopyHostGroupSpec(**x) for x in self.primary_hostgroups
            ]

        if self.primary_iscsi_targets:
            self.primary_iscsi_targets = [
                TrueCopyHostGroupSpec(**x) for x in self.primary_iscsi_targets
            ]
        if self.primary_nvm_subsystem:
            self.primary_nvm_subsystem = NVMeSubsystemSpec(**self.primary_nvm_subsystem)

        if self.capacity_saving:
            if self.capacity_saving.lower() != "disabled":
                self.is_data_reduction_force_copy = True
            else:
                raise ValueError(VspRemoteReplicationMsg.CAPACITY_SAVING_DISABLED.value)
        else:
            self.capacity_saving = "compression"
            self.is_data_reduction_force_copy = True

        if self.begin_primary_volume_id:
            self.begin_primary_volume_id = normalize_ldev_id(
                self.begin_primary_volume_id
            )
        if self.end_primary_volume_id:
            self.end_primary_volume_id = normalize_ldev_id(self.end_primary_volume_id)

        if (
            self.number_of_pairs is None
            or self.number_of_pairs < 1
            or self.number_of_pairs > 32
        ):
            raise ValueError(VSPHurValidateMsg.NUMBER_OF_PAIRS.value)

        if self.volume_size is None:
            raise ValueError(VSPHurValidateMsg.VOLUME_SIZE.value)

        if self.primary_pool_id is None:
            raise ValueError(VSPHurValidateMsg.PRIMARY_POOL_ID.value)

        if self.secondary_pool_id is None:
            raise ValueError(VSPHurValidateMsg.SECONDARY_POOL_ID.value)
        if (
            self.primary_hostgroups is None
            and self.primary_iscsi_targets is None
            and self.primary_nvm_subsystem is None
        ):
            raise ValueError(VSPHurValidateMsg.PRIMARY_HOSTGROUPS_OR_NVME.value)
        if (
            self.secondary_hostgroups is None
            and self.secondary_iscsi_targets is None
            and self.secondary_nvm_subsystem is None
        ):
            raise ValueError(VSPHurValidateMsg.SECONDARY_HOSTGROUPS_OR_NVME.value)
        if (
            self.primary_hostgroups is not None
            and self.primary_iscsi_targets is not None
        ):
            raise ValueError(
                VSPHurValidateMsg.BOTH_PRIMARY_HGS_AND_IST_ARE_SPECIFIED.value
            )
        if (
            self.primary_hostgroups is not None
            and self.primary_nvm_subsystem is not None
        ):
            raise ValueError(
                VSPHurValidateMsg.BOTH_PRIMARY_HGS_AND_NVME_ARE_SPECIFIED.value
            )
        if (
            self.primary_iscsi_targets is not None
            and self.primary_nvm_subsystem is not None
        ):
            raise ValueError(
                VSPHurValidateMsg.BOTH_PRIMARY_IST_AND_NVME_ARE_SPECIFIED.value
            )
        if (
            self.secondary_hostgroups is not None
            and self.secondary_iscsi_targets is not None
        ):
            raise ValueError(
                VSPHurValidateMsg.BOTH_SECONDARY_HGS_AND_IST_ARE_SPECIFIED.value
            )
        if (
            self.secondary_hostgroups is not None
            and self.secondary_nvm_subsystem is not None
        ):
            raise ValueError(
                VSPHurValidateMsg.BOTH_SECONDARY_HGS_AND_NVME_ARE_SPECIFIED.value
            )
        if (
            self.secondary_iscsi_targets is not None
            and self.secondary_nvm_subsystem is not None
        ):
            raise ValueError(
                VSPHurValidateMsg.BOTH_SECONDARY_IST_AND_NVME_ARE_SPECIFIED.value
            )
        if self.primary_hostgroups is not None and self.secondary_hostgroups is None:
            raise ValueError(VSPHurValidateMsg.PRIMARY_HGS_WITHOUT_SECONDARY_HGS.value)

        if self.primary_hostgroups is None and self.secondary_hostgroups is not None:
            raise ValueError(VSPHurValidateMsg.SECONDARY_HGS_WITHOUT_PRIMARY_HGS.value)
        if (
            self.primary_iscsi_targets is not None
            and self.secondary_iscsi_targets is None
        ):
            raise ValueError(VSPHurValidateMsg.PRIMARY_IST_WITHOUT_SECONDARY_IST.value)
        if (
            self.primary_iscsi_targets is None
            and self.secondary_iscsi_targets is not None
        ):
            raise ValueError(VSPHurValidateMsg.SECONDARY_IST_WITHOUT_PRIMARY_IST.value)
        if (
            self.primary_nvm_subsystem is not None
            and self.secondary_nvm_subsystem is None
        ):
            raise ValueError(
                VSPHurValidateMsg.PRIMARY_NVME_WITHOUT_SECONDARY_NVME.value
            )
        if (
            self.primary_nvm_subsystem is None
            and self.secondary_nvm_subsystem is not None
        ):
            raise ValueError(
                VSPHurValidateMsg.SECONDARY_NVME_WITHOUT_PRIMARY_NVME.value
            )
