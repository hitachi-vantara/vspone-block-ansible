from dataclasses import dataclass
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass, base_dict_converter
    from ..common.ansible_common import (
        volume_id_to_hex_format,
        normalize_ldev_id,
    )
    from ..model.common_base_models import ConnectionInfo
    from ..common.ansible_common import normalize_copy_pace
    from ..common.ansible_common_constants import MAX_BULK_PAIRS
    from ..message.vsp_gad_pair_msgs import GADPairValidateMSG, VspOneGadValidationMsg

except ImportError:
    from .common_base_models import BaseDataClass, SingleBaseClass, base_dict_converter
    from common.ansible_common import (
        volume_id_to_hex_format,
        normalize_ldev_id,
    )
    from model.common_base_models import ConnectionInfo
    from message.vsp_gad_pair_msgs import GADPairValidateMSG, VspOneGadValidationMsg


@dataclass
class VspOneGadCtgFactSpec:
    consistency_group_id: Optional[int] = None

    def __post_init__(self, **kwargs):
        if self.consistency_group_id:
            if self.consistency_group_id < 0 or self.consistency_group_id > 1023:
                raise ValueError(
                    VspOneGadValidationMsg.CONSISTENCY_GROUP_ID_RANGE.value.format(
                        self.consistency_group_id
                    )
                )


@dataclass
class GADPairFactSpec:
    primary_volume_id: Optional[int] = None
    secondary_volume_id: Optional[int] = None
    secondary_storage_serial_number: Optional[str] = None
    secondary_connection_info: Optional[ConnectionInfo] = None
    copy_group_name: Optional[str] = None
    copy_pair_name: Optional[str] = None
    local_device_group_name: Optional[str] = None
    remote_device_group_name: Optional[str] = None


@dataclass
class HostgroupSpec:
    id: Optional[int] = None
    name: Optional[str] = None
    lun_id: Optional[int] = None
    enable_preferred_path: Optional[bool] = None
    port: Optional[str] = None
    port_id: Optional[str] = None
    resource_group_id: Optional[int] = None

    def __post_init__(self):
        if self.port_id:
            self.port = str(self.port_id)


@dataclass
class NVMeSubsystemSpec:
    id: Optional[int] = None
    name: Optional[str] = None
    paths: Optional[List[str]] = None


@dataclass
class BaseGadPairSpec:
    """Base class for GAD Pair Specifications containing common fields."""

    data_reduction_share: Optional[bool] = None
    primary_storage_serial_number: Optional[str] = None
    primary_volume_id: Optional[int] = None
    consistency_group_id: Optional[str] = None
    allocate_new_consistency_group: Optional[bool] = None
    primary_hostgroups: Optional[List[HostgroupSpec]] = None
    secondary_storage_serial_number: Optional[str] = None
    secondary_pool_id: Optional[str] = None
    secondary_hostgroups: Optional[List[HostgroupSpec]] = None
    secondary_iscsi_targets: Optional[List[HostgroupSpec]] = None
    secondary_nvm_subsystem: Optional[NVMeSubsystemSpec] = None
    set_alua_mode: Optional[bool] = None
    primary_resource_group_name: Optional[str] = None
    secondary_resource_group_name: Optional[str] = None
    quorum_disk_id: Optional[str] = None
    remote_ucp_system: Optional[str] = None
    path_group_id: Optional[int] = None
    mu_number: Optional[int] = None
    mirror_unit_number: Optional[int] = None
    copy_pace: Optional[int] = None
    copy_pair_name: Optional[str] = None
    copy_group_name: Optional[str] = None
    fence_level: Optional[str] = None
    do_initial_copy: Optional[bool] = None
    is_data_reduction_force_copy: Optional[bool] = None
    is_consistency_group: Optional[bool] = None
    is_new_group_creation: Optional[bool] = None
    secondary_storage_connection_info: Optional[ConnectionInfo] = None
    secondary_connection_info: Optional[ConnectionInfo] = None
    local_device_group_name: Optional[str] = None
    remote_device_group_name: Optional[str] = None
    remote_connection_info: Optional[ConnectionInfo] = None
    new_volume_size: Optional[str] = None
    begin_secondary_volume_id: Optional[int] = None
    end_secondary_volume_id: Optional[int] = None
    is_svol_readwriteable: Optional[bool] = False
    should_delete_svol: Optional[bool] = False
    provisioned_secondary_volume_id: Optional[int] = None
    comments: Optional[str] = None

    def _init_common_fields(self):
        """Initialize common fields shared by child classes."""
        if self.primary_hostgroups:
            self.primary_hostgroups = [
                HostgroupSpec(**x) for x in self.primary_hostgroups
            ]
        if self.secondary_hostgroups:
            self.secondary_hostgroups = [
                HostgroupSpec(**x) for x in self.secondary_hostgroups
            ]
        if self.secondary_iscsi_targets:
            self.secondary_iscsi_targets = [
                HostgroupSpec(**x) for x in self.secondary_iscsi_targets
            ]
        if self.secondary_storage_connection_info:
            self.secondary_storage_connection_info = ConnectionInfo(
                **self.secondary_storage_connection_info
            )
        if self.secondary_connection_info:
            self.secondary_connection_info = ConnectionInfo(
                **self.secondary_connection_info
            )
        if self.remote_connection_info:
            self.remote_connection_info = ConnectionInfo(**self.remote_connection_info)
        if self.secondary_nvm_subsystem:
            self.secondary_nvm_subsystem = NVMeSubsystemSpec(
                **self.secondary_nvm_subsystem
            )
        if self.primary_volume_id:
            self.primary_volume_id = normalize_ldev_id(self.primary_volume_id)
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

        if self.mirror_unit_number is not None:
            self.mu_number = self.mirror_unit_number


@dataclass
class VspGadPairSpec(BaseGadPairSpec):

    def __post_init__(self):
        self._init_common_fields()


@dataclass
class VspBatchGadPairSpec(BaseGadPairSpec):
    primary_iscsi_targets: Optional[List[HostgroupSpec]] = None
    primary_nvm_subsystem: Optional[NVMeSubsystemSpec] = None
    virtual_storage_serial_number: Optional[str] = None
    number_of_pairs: Optional[int] = None
    begin_primary_volume_id: Optional[int] = None
    end_primary_volume_id: Optional[int] = None
    primary_volume_base_name: Optional[str] = None
    primary_volume_base_name_start_number: Optional[int] = None
    primary_pool_id: Optional[str] = None
    volume_size: Optional[str] = None
    capacity_saving: Optional[str] = None
    copy_pair_base_name: Optional[str] = None
    copy_pace: Optional[int] = None
    should_match_volume_ids: Optional[bool] = None
    comments: Optional[List[str]] = None

    def __post_init__(self):
        if self.number_of_pairs is not None and not (
            1 <= self.number_of_pairs <= MAX_BULK_PAIRS
        ):
            raise ValueError(
                GADPairValidateMSG.NUMBER_OF_PAIRS_RANGE.value.format(MAX_BULK_PAIRS)
            )

        if not (
            self.primary_hostgroups
            or self.primary_iscsi_targets
            or self.primary_nvm_subsystem
        ):
            raise ValueError(GADPairValidateMSG.PRIMARY_HG_IST_NVM_REQUIRED.value)

        if self.primary_hostgroups and not self.secondary_hostgroups:
            raise ValueError(GADPairValidateMSG.SECONDARY_HG_REQUIRED.value)
        if self.primary_iscsi_targets and not self.secondary_iscsi_targets:
            raise ValueError(GADPairValidateMSG.SECONDARY_IST_REQUIRED.value)
        if self.primary_nvm_subsystem and not self.secondary_nvm_subsystem:
            raise ValueError(GADPairValidateMSG.SECONDARY_NVM_REQUIRED.value)

        self._init_common_fields()

        if self.primary_iscsi_targets:
            self.primary_iscsi_targets = [
                HostgroupSpec(**x) for x in self.primary_iscsi_targets
            ]

        if self.primary_nvm_subsystem:
            self.primary_nvm_subsystem = NVMeSubsystemSpec(**self.primary_nvm_subsystem)

        if self.begin_primary_volume_id is not None:
            self.begin_primary_volume_id = normalize_ldev_id(
                self.begin_primary_volume_id
            )
        if self.end_primary_volume_id is not None:
            self.end_primary_volume_id = normalize_ldev_id(self.end_primary_volume_id)

        if (
            self.begin_primary_volume_id is not None
            and self.end_primary_volume_id is not None
        ):
            if self.begin_primary_volume_id > self.end_primary_volume_id:
                raise ValueError(
                    GADPairValidateMSG.BEGIN_PRIMARY_GREATER_THAN_END.value
                )
            count = self.end_primary_volume_id - self.begin_primary_volume_id + 1
            if self.number_of_pairs is not None and count < self.number_of_pairs:
                raise ValueError(
                    GADPairValidateMSG.PRIMARY_VOLUME_RANGE_MISMATCH.value.format(
                        self.number_of_pairs, count
                    )
                )
        if (
            self.begin_secondary_volume_id is not None
            and self.end_secondary_volume_id is not None
        ):
            if self.begin_secondary_volume_id > self.end_secondary_volume_id:
                raise ValueError(
                    GADPairValidateMSG.BEGIN_SECONDARY_GREATER_THAN_END.value
                )
            count = self.end_secondary_volume_id - self.begin_secondary_volume_id + 1
            if self.number_of_pairs is not None and count < self.number_of_pairs:
                raise ValueError(
                    GADPairValidateMSG.SECONDARY_VOLUME_RANGE_MISMATCH.value.format(
                        self.number_of_pairs, count
                    )
                )
        if self.number_of_pairs is not None:
            if self.number_of_pairs <= 0:
                raise ValueError(GADPairValidateMSG.NUMBER_OF_PAIRS_POSITIVE.value)


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
    # entitlementStatus: Optional[str] = None
    storageId: Optional[str] = None
    # subscriberId: Optional[str] = None
    # partnerId: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        gadPairInfo = kwargs.get("gadPairInfo")
        if gadPairInfo:
            for key, value in gadPairInfo.items():
                # if not hasattr(self, key):
                setattr(self, key, value)
            if gadPairInfo.get("secondaryVirtualVolumeId"):
                self.secondaryVirtualHexVolumeId = volume_id_to_hex_format(
                    gadPairInfo.get("secondaryVirtualVolumeId")
                ).upper()

    def to_dict(self):

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


#  sng1104
@dataclass
class DirectGadPairInfo(SingleBaseClass):
    replicationType: str
    ldevId: int
    remoteSerialNumber: str
    remoteStorageTypeId: str
    remoteLdevId: int
    primaryOrSecondary: str
    muNumber: int
    status: str
    isSSWS: bool
    createdLocalTime: str
    quorumDiskId: int
    suspendedMode: str


@dataclass
class DirectGadPairInfoList(BaseDataClass):
    data: List[DirectGadPairInfo]


@dataclass
class RemoteConnectionIdInfo(SingleBaseClass):
    pathGroupId: Optional[int] = None
    storageModel: Optional[str] = None
    storageSerialNumber: Optional[str] = None

    def camel_to_snake_dict(self):
        return super().camel_to_snake_dict()


@dataclass
class VspGadCtgInfo(SingleBaseClass):
    id: int
    ioPreference: Optional[str] = None
    localVolumeIoModes: Optional[List[str]] = None
    localVolumePositions: Optional[List[str]] = None
    localVolumeStatuses: Optional[List[str]] = None
    muNumber: Optional[int] = None
    numberOfPairs: Optional[int] = None
    pairOperationModesForBlockedQuorumDisk: Optional[List[str]] = None
    quorumDiskId: Optional[int] = None
    remoteConnectionId: Optional[RemoteConnectionIdInfo] = None

    def __post_init__(self):
        if self.remoteConnectionId:
            self.remoteConnectionId = RemoteConnectionIdInfo(**self.remoteConnectionId)

    def camel_to_snake_dict(self):
        new_dict = super().camel_to_snake_dict()
        new_dict["mirror_unit_number"] = new_dict.pop("mu_number", None)
        return new_dict


@dataclass
class VspGadCtgInfoList(BaseDataClass):
    data: List[VspGadCtgInfo] = None

    def camel_to_snake_dict(self):
        new_data = (
            [item.camel_to_snake_dict() for item in self.data] if self.data else []
        )
        return new_data


@dataclass
class VspOneGadCtgSpec(SingleBaseClass):
    consistency_group_ids: Optional[List[int]] = None
    is_swap_resynced: Optional[bool] = None
    copy_pace: Optional[int] = None
    io_preference_mode: Optional[str] = None
    continue_io_volume: Optional[List[str]] = None
    comments: Optional[str] = None

    def __post_init__(self):
        if self.consistency_group_ids is not None:
            for cg_id in self.consistency_group_ids:
                if cg_id < 0 or cg_id > 1023:
                    raise ValueError(
                        VspOneGadValidationMsg.CONSISTENCY_GROUP_ID_RANGE.value.format(
                            cg_id
                        )
                    )
        if self.copy_pace is not None:
            if self.copy_pace < 1 or self.copy_pace > 15:
                raise ValueError(
                    VspOneGadValidationMsg.COPY_PACE_RANGE.value.format(self.copy_pace)
                )
        else:
            self.copy_pace = 3

        if self.io_preference_mode is not None:
            valid_modes = ["KEEP_CURRENT_SETTING", "DISABLED", "PRIMARY_ENABLED"]
            if self.io_preference_mode.upper() not in valid_modes:
                raise ValueError(
                    VspOneGadValidationMsg.IO_PREFERENCE_MODE_INVALID.value.format(
                        self.io_preference_mode, valid_modes
                    )
                )
            self.io_preference_mode = self.io_preference_mode.upper()
        else:
            self.io_preference_mode = "KEEP_CURRENT_SETTING"

        if self.continue_io_volume is not None:
            if self.continue_io_volume.upper() not in ["PRIMARY", "SECONDARY"]:
                raise ValueError(
                    VspOneGadValidationMsg.CONTINUE_IO_VOLUMES_INVALID.value.format(
                        self.continue_io_volume
                    )
                )
            self.continue_io_volume = self.continue_io_volume.upper()


@dataclass
class VspGadVolumePairInfo(SingleBaseClass):
    id: Optional[str] = None
    localVolumeId: Optional[int] = None
    muNumber: Optional[int] = None
    localVolumeNickname: Optional[str] = None
    localVolumeProvisioningType: Optional[str] = None
    remoteConnectionId: Optional[RemoteConnectionIdInfo] = None
    remoteVolumeId: Optional[int] = None
    localVolumeStatus: Optional[str] = None
    localVolumeProcessingStatus: Optional[str] = None
    failureFactor: Optional[str] = None
    localVolumePosition: Optional[str] = None
    localVolumeIoMode: Optional[str] = None
    copySpeed: Optional[int] = None
    ioPreference: Optional[str] = None
    pairOperationModeForBlockedQuorumDisk: Optional[str] = None
    dataSynchronizationRate: Optional[int] = None
    copyTime: Optional[int] = None
    localVolumeDifferentialDataManagement: Optional[str] = None
    quorumId: Optional[int] = None
    consistencyGroupId: Optional[int] = None
    copyProgressRate: Optional[int] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__post_init__()

    def __post_init__(self):
        if self.remoteConnectionId and isinstance(self.remoteConnectionId, dict):
            self.remoteConnectionId = RemoteConnectionIdInfo(**self.remoteConnectionId)

    def camel_to_snake_dict(self):
        new_dict = super().camel_to_snake_dict()
        new_dict["mirror_unit_number"] = new_dict.pop("mu_number", None)
        return new_dict


@dataclass
class VspGadVolumePairInfoList(BaseDataClass):
    data: List[VspGadVolumePairInfo] = None


@dataclass
class RemoteVolumeActiveActiveMirroringInfo:
    ssid: Optional[str] = None
    port_number: Optional[str] = None
    absolute_lun: Optional[str] = None
    storage_type_number: Optional[str] = None

    def to_dict(self):
        payload = {}
        if self.ssid is not None:
            payload["ssid"] = self.ssid
        if self.port_number is not None:
            payload["portNumber"] = self.port_number
        if self.absolute_lun is not None:
            payload["absoluteLun"] = self.absolute_lun
        if self.storage_type_number is not None:
            payload["storageTypeNumber"] = self.storage_type_number
        return payload


@dataclass
class GadPairConfigInput:
    primary_volume_id: int = None
    provisioned_secondary_volume_id: Optional[int] = None
    mirror_unit_number: int = None

    remote_volume_active_active_mirroring_info: Optional[
        RemoteVolumeActiveActiveMirroringInfo
    ] = None
    already_exists: Optional[bool] = False

    def __post_init__(self):
        if self.primary_volume_id is not None:
            self.primary_volume_id = normalize_ldev_id(self.primary_volume_id)
        if self.provisioned_secondary_volume_id is not None:
            self.provisioned_secondary_volume_id = normalize_ldev_id(
                self.provisioned_secondary_volume_id
            )
        if self.remote_volume_active_active_mirroring_info and isinstance(
            self.remote_volume_active_active_mirroring_info, dict
        ):
            self.remote_volume_active_active_mirroring_info = (
                RemoteVolumeActiveActiveMirroringInfo(
                    **self.remote_volume_active_active_mirroring_info
                )
            )


VSP_ONE_PRIORITY_MODE_VALUES = ["DISABLE", "PRIMARY_ENABLE"]


@dataclass
class VspGadCtgCreateSpec:
    consistency_group_id: int = None
    gad_pairs: List[GadPairConfigInput] = None
    path_group_id: int = None
    quorum_id: int = None
    secondary_servers: Optional[List] = None
    should_replicate_from_primary_to_secondary: Optional[bool] = True
    copy_pace: Optional[int] = None
    io_priority_mode: Optional[str] = None
    secondary_storage_pool_id: Optional[int] = None
    secondary_servers: Optional[List] = None
    comments: Optional[List[str]] = None
    remote_storage_serial_number: Optional[str] = None
    remote_storage_model: Optional[str] = None
    mirror_unit_number: int = None

    def __post_init__(self):
        if self.consistency_group_id is not None and not (
            0 <= self.consistency_group_id <= 1023
        ):
            raise ValueError(
                f"consistency_group_id must be in range 0-1023, got {self.consistency_group_id}"
            )
        if self.path_group_id is not None and not (0 <= self.path_group_id <= 255):
            raise ValueError(
                f"path_group_id must be in range 0-255, got {self.path_group_id}"
            )
        if self.quorum_id is not None and not (0 <= self.quorum_id <= 32):
            raise ValueError(f"quorum_id must be in range 0-32, got {self.quorum_id}")
        if self.copy_pace is not None:
            self.copy_pace = normalize_copy_pace(self.copy_pace)
        if self.io_priority_mode is not None:
            if self.io_priority_mode.upper() not in VSP_ONE_PRIORITY_MODE_VALUES:
                raise ValueError(
                    f"io_priority_mode must be one of {VSP_ONE_PRIORITY_MODE_VALUES}, got {self.io_priority_mode}"
                )
            self.io_priority_mode = self.io_priority_mode.upper()

        if self.gad_pairs:
            self.gad_pairs = [
                GadPairConfigInput(
                    primary_volume_id=p.get("primary_volume_id"),
                    provisioned_secondary_volume_id=p.get(
                        "provisioned_secondary_volume_id"
                    ),
                    mirror_unit_number=self.mirror_unit_number,  # Use mirror_unit_number from the main spec
                )
                for p in self.gad_pairs
            ]

    def create_payload(self):
        payload = {}
        if self.consistency_group_id is not None:
            payload["consistencyGroupId"] = self.consistency_group_id
        if self.gad_pairs is not None:
            pair_list = []
            for pair in self.gad_pairs:
                if pair.already_exists is False:
                    pair_entry = {}
                    if pair.primary_volume_id is not None:
                        pair_entry["localVolumeId"] = pair.primary_volume_id
                    pair_entry["muNumber"] = self.mirror_unit_number
                    if pair.provisioned_secondary_volume_id is not None:
                        pair_entry["remoteVolumeId"] = (
                            pair.provisioned_secondary_volume_id
                        )
                    if pair.remote_volume_active_active_mirroring_info is not None:
                        pair_entry["remoteVolumeActiveActiveMirroringInfo"] = (
                            pair.remote_volume_active_active_mirroring_info.to_dict()
                        )
                    pair_list.append(pair_entry)
            payload["createActiveActiveMirroringPairParamList"] = pair_list
        if self.path_group_id is not None:
            payload["remoteConnectionId"] = {
                "pathGroupId": self.path_group_id,
                "storageModel": self.remote_storage_model,
                "storageSerialNumber": self.remote_storage_serial_number,
            }
        if self.quorum_id is not None:
            payload["quorumId"] = self.quorum_id
        if self.should_replicate_from_primary_to_secondary is not None:
            payload["doCopy"] = self.should_replicate_from_primary_to_secondary
        if self.copy_pace is not None:
            payload["copySpeed"] = self.copy_pace
        if self.io_priority_mode is not None:
            payload["ioPreference"] = self.io_priority_mode

        return (
            payload
            if len(payload["createActiveActiveMirroringPairParamList"]) > 0
            else {}
        )
