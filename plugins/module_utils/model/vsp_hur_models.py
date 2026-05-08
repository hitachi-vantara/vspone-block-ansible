from dataclasses import dataclass, asdict
from typing import Optional, List

from .common_base_models import BaseDataClass, SingleBaseClass

try:
    from ..common.ansible_common import normalize_ldev_id
    from ..message.vsp_hur_msgs import VspRemoteReplicationMsg, VSPHurValidateMsg
    from .vsp_true_copy_models import DirectTrueCopyPairInfo, DirectTrueCopyPairInfoList
    from ..model.common_base_models import ConnectionInfo
except ImportError:
    from common.ansible_common import normalize_ldev_id
    from .vsp_true_copy_models import DirectTrueCopyPairInfo, DirectTrueCopyPairInfoList
    from model.common_base_models import ConnectionInfo


@dataclass
class HurHostGroupSpec:
    # id: int = None
    name: str = None
    port: str = None
    port_id: str = None
    lun_id: Optional[int] = None
    # resource_group_id: Optional[int] = None

    def __post_init__(self, **kwargs):
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


#  20240812 tag.HUR
@dataclass
class HurFactSpec(SingleBaseClass):
    primary_volume_id: Optional[int] = None
    secondary_volume_id: Optional[int] = None
    pvol: Optional[int] = None
    mirror_unit_id: Optional[int] = None
    mirror_unit_number: Optional[int] = None

    secondary_storage_serial_number: Optional[str] = None
    secondary_connection_info: Optional[ConnectionInfo] = None
    copy_group_name: Optional[str] = None
    copy_pair_name: Optional[str] = None
    local_device_group_name: Optional[str] = None
    remote_device_group_name: Optional[str] = None

    def __post_init__(self, **kwargs):
        if self.secondary_connection_info:
            self.secondary_connection_info = ConnectionInfo(
                **self.secondary_connection_info
            )
        if self.primary_volume_id:
            self.primary_volume_id = normalize_ldev_id(self.primary_volume_id)
        if self.secondary_volume_id:
            self.secondary_volume_id = normalize_ldev_id(self.secondary_volume_id)
        if self.mirror_unit_number is not None:
            self.mirror_unit_id = self.mirror_unit_number


@dataclass
class HurSpec:
    data_reduction_share: Optional[bool] = None
    primary_volume_id: Optional[int] = None
    secondary_volume_id: Optional[int] = None
    copy_group_name: Optional[str] = None
    copy_pair_name: Optional[str] = None
    fence_level: Optional[str] = None
    local_device_group_name: Optional[str] = None
    remote_device_group_name: Optional[str] = None
    do_initial_copy: Optional[bool] = None
    is_data_reduction_force_copy: Optional[bool] = None
    consistency_group_id: Optional[int] = None
    enable_delta_resync: Optional[bool] = None
    allocate_new_consistency_group: Optional[bool] = None
    secondary_storage_serial_number: Optional[int] = None
    secondary_pool_id: Optional[int] = None
    secondary_hostgroups: Optional[List[HurHostGroupSpec]] = None
    secondary_iscsi_targets: Optional[List[HurHostGroupSpec]] = None
    secondary_nvm_subsystem: Optional[NVMeSubsystemSpec] = None
    primary_volume_journal_id: Optional[int] = None
    secondary_volume_journal_id: Optional[int] = None
    mirror_unit_id: Optional[int] = None
    mirror_unit_number: Optional[int] = None
    do_delta_resync_suspend: Optional[bool] = None
    is_new_group_creation: Optional[bool] = None
    secondary_connection_info: Optional[ConnectionInfo] = None
    # remote_connection_info: Optional[ConnectionInfo] = None
    # secondary_storage_connection_info: Optional[ConnectionInfo] = None
    is_svol_readwriteable: Optional[bool] = False
    svolOperationMode: Optional[str] = None
    doSwapSvol: Optional[bool] = None
    new_volume_size: Optional[str] = None
    begin_secondary_volume_id: Optional[int] = None
    end_secondary_volume_id: Optional[int] = None
    path_group_id: Optional[int] = None
    should_delete_svol: Optional[bool] = False
    provisioned_secondary_volume_id: Optional[int] = None

    # Making a single hg
    secondary_hostgroup: Optional[HurHostGroupSpec] = None
    comments: Optional[str] = None
    primary_journal_id: Optional[int] = None
    secondary_journal_id: Optional[int] = None
    mirror_unit_number: Optional[int] = None

    is_consistency_group: Optional[bool] = None

    def __post_init__(self, **kwargs):
        if self.secondary_hostgroup:
            self.secondary_hostgroup = [HurHostGroupSpec(**self.secondary_hostgroup)]
        if self.secondary_hostgroups:
            self.secondary_hostgroups = [
                HurHostGroupSpec(**x) for x in self.secondary_hostgroups
            ]
        if self.secondary_iscsi_targets:
            self.secondary_iscsi_targets = [
                HurHostGroupSpec(**x) for x in self.secondary_iscsi_targets
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
        if self.mirror_unit_number is not None:
            self.mirror_unit_id = self.mirror_unit_number


@dataclass
class VSPHurPairInfo(SingleBaseClass):
    resourceId: str
    consistencyGroupId: int
    copyRate: int
    fenceLevel: str
    mirrorUnitId: int
    mirrorUnitNumber: int
    pairName: str
    primaryVolumeId: int

    primaryVolumeStorageId: int
    secondaryVolumeId: int

    secondaryVolumeStorageId: int
    status: str
    svolAccessMode: str
    type: str

    # primaryHexVolumeId: Optional[str] = None
    # secondaryHexVolumeId: Optional[str] = None
    entitlementStatus: Optional[str] = None
    partnerId: Optional[str] = None
    subscriberId: Optional[str] = None
    primaryJournalPoolId: Optional[int] = None
    secondaryJournalPoolId: Optional[int] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        #  20240814 Porcelain DTO: VSPHurPairInfo
        #  hur_pair_info is from v3 response
        hur_pair_info = kwargs.get("hurPairInfo")

        #  flattern the struct from v3
        if hur_pair_info:
            for field in self.__dataclass_fields__.keys():
                if not getattr(self, field):
                    setattr(self, field, hur_pair_info.get(field, None))

    def to_dict(self):
        return asdict(self)


@dataclass
class VSPHurPairInfoList(BaseDataClass):
    data: List[VSPHurPairInfo]


DirectHurPairInfo = DirectTrueCopyPairInfo
DirectHurPairInfoList = DirectTrueCopyPairInfoList


@dataclass
class HurBatchSpec(HurSpec):
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
    should_match_volume_ids: Optional[bool] = None

    primary_hostgroups: Optional[List[HurHostGroupSpec]] = None
    primary_iscsi_targets: Optional[List[HurHostGroupSpec]] = None
    primary_nvm_subsystem: Optional[NVMeSubsystemSpec] = None

    copy_pair_base_name: Optional[str] = None
    comments: Optional[List[str]] = None

    def __post_init__(self, **kwargs):
        super().__post_init__(**kwargs)

        if self.primary_hostgroups:
            self.primary_hostgroups = [
                HurHostGroupSpec(**x) for x in self.primary_hostgroups
            ]

        if self.primary_iscsi_targets:
            self.primary_iscsi_targets = [
                HurHostGroupSpec(**x) for x in self.primary_iscsi_targets
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
