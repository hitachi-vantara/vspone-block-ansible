from dataclasses import dataclass
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass
    from ..common.ansible_common import (
        normalize_ldev_id,
        volume_id_to_hex_format,
    )
    from ..message.vsp_gad_pair_msgs import VspOneGadValidationMsg
    from ..common.vsp_constants import AutomationConstants
except ImportError:
    from .common_base_models import BaseDataClass, SingleBaseClass
    from common.ansible_common import normalize_ldev_id, volume_id_to_hex_format
    from message.vsp_gad_pair_msgs import VspOneGadValidationMsg
    from common.vsp_constants import AutomationConstants


@dataclass
class VspOneGadFactSpec:
    """Spec for filtering GAD pair facts via hv_vsp_one_gad_facts.
    Note: Not a Base class, so no __init__ override needed here."""

    consistency_group_id: Optional[int] = None
    primary_volume_id: Optional[int] = None
    mirror_unit_number: Optional[int] = None
    count: Optional[int] = 500
    start_id: Optional[str] = None
    comments: Optional[str] = None

    def __post_init__(self):
        if self.primary_volume_id is not None:
            self.primary_volume_id = normalize_ldev_id(self.primary_volume_id)
        if self.mirror_unit_number is None:
            self.mirror_unit_number = 0  # default
        if self.primary_volume_id is not None and self.mirror_unit_number is not None:
            self.start_id = f"{self.primary_volume_id},{self.mirror_unit_number}"
        if self.count < 1 or self.count > 500:
            raise ValueError(VspOneGadValidationMsg.COUNT_INVALID.value.format(self.count))

    def is_empty(self):
        return (
            all(
                v is None
                for v in [
                    self.consistency_group_id,
                    self.primary_volume_id,
                    self.mirror_unit_number,
                    self.start_id,
                ]
            )
            and self.count == 500
        )


@dataclass
class RemoteVolumeMirroringInfo(SingleBaseClass):
    ssid: Optional[int] = None
    portNumber: Optional[int] = None
    absoluteLun: Optional[int] = None
    storageTypeNumber: Optional[int] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@dataclass
class VspOneCreateGadVolumeEntry(SingleBaseClass):
    local_volume_id: Optional[int] = None
    mu_number: Optional[int] = 0
    remote_volume_id: Optional[int] = None
    remote_volume_active_active_mirroring_info: Optional[RemoteVolumeMirroringInfo] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__post_init__()

    def __post_init__(self):
        if self.local_volume_id is not None:
            self.local_volume_id = normalize_ldev_id(self.local_volume_id)
        if self.remote_volume_id is not None:
            self.remote_volume_id = normalize_ldev_id(self.remote_volume_id)
        if isinstance(self.remote_volume_active_active_mirroring_info, dict):
            self.remote_volume_active_active_mirroring_info = RemoteVolumeMirroringInfo(**self.remote_volume_active_active_mirroring_info)


@dataclass
class RemoteConnectionSpec(SingleBaseClass):
    storageModel: Optional[str] = None
    storageSerialNumber: Optional[str] = None
    pathGroupId: Optional[int] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@dataclass
class VspOneCreateGadSpec(SingleBaseClass):
    consistency_group_id: Optional[int] = None
    remote_connection_id: Optional[RemoteConnectionSpec] = None
    quorum_id: Optional[int] = None
    create_active_active_mirroring_pair_param_list: Optional[List[VspOneCreateGadVolumeEntry]] = None
    do_copy: Optional[bool] = True
    copy_speed: Optional[int] = 3
    io_preference: Optional[str] = "DISABLE"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__post_init__()

    def __post_init__(self):
        if isinstance(self.remote_connection_id, dict):
            self.remote_connection_id = RemoteConnectionSpec(**self.remote_connection_id)
        if self.create_active_active_mirroring_pair_param_list:
            self.create_active_active_mirroring_pair_param_list = [
                VspOneCreateGadVolumeEntry(**item) if isinstance(item, dict) else item for item in self.create_active_active_mirroring_pair_param_list
            ]


@dataclass
class VspOneDeleteGadSpec:
    # Matches Playbook: primary_volume_mirrors
    primary_volume_mirrors: List[dict]
    delete_mode: Optional[str] = "NORMAL"
    allow_volume_access_after_force_delete: Optional[bool] = None

    # Internal attribute for the Backend API format ["ldev,mu"]
    ids: List[str] = None

    def __post_init__(self):
        self.ids = _convert_mirrors_to_ids(self.primary_volume_mirrors)
        if self.delete_mode is not None:
            if self.delete_mode.upper() not in ["NORMAL", "FORCE"]:
                raise ValueError(VspOneGadValidationMsg.DELETE_MODE_INVALID.value.format(self.delete_mode))
            self.delete_mode = self.delete_mode.upper()
        else:
            self.delete_mode = "NORMAL"
        if self.delete_mode == "FORCE":
            if self.allow_volume_access_after_force_delete is None:
                raise ValueError(VspOneGadValidationMsg.ALLOW_VOLUME_ACCESS_REQUIRED.value.format())


@dataclass
class VspOneSuspendGadSpec:
    primary_volume_mirrors: List[dict]
    continue_io_volume: Optional[str] = "PRIMARY"
    ids: List[str] = None

    def __post_init__(self):
        self.ids = _convert_mirrors_to_ids(self.primary_volume_mirrors)
        if self.continue_io_volume is not None:
            if self.continue_io_volume.upper() not in ["PRIMARY", "SECONDARY"]:
                raise ValueError(VspOneGadValidationMsg.CONTINUE_IO_VOLUMES_INVALID.value.format(self.continue_io_volume))
            self.continue_io_volume = self.continue_io_volume.upper()
        else:
            self.continue_io_volume = "PRIMARY"


@dataclass
class VspOneResyncGadSpec:
    primary_volume_mirrors: List[dict]
    is_swap_resynced: Optional[bool] = False
    copy_pace: Optional[int] = None
    io_preference: Optional[str] = "KEEP_CURRENT_SETTING"
    ids: List[str] = None

    def __post_init__(self):
        self.ids = _convert_mirrors_to_ids(self.primary_volume_mirrors)
        if self.copy_pace is not None:
            if self.copy_pace < AutomationConstants.COPY_PACE_MIN or self.copy_pace > AutomationConstants.COPY_PACE_MAX:
                raise ValueError(VspOneGadValidationMsg.COPY_PACE_RANGE.value.format(self.copy_pace))
        else:
            self.copy_pace = AutomationConstants.COPY_PACE_DEFAULT

        if self.io_preference is not None:
            valid_modes = ["KEEP_CURRENT_SETTING", "DISABLE", "PRIMARY_ENABLE"]
            if self.io_preference.upper() not in valid_modes:
                raise ValueError(VspOneGadValidationMsg.IO_PREFERENCE_MODE_INVALID.value.format(self.io_preference, valid_modes))
            self.io_preference = self.io_preference.upper()
        else:
            self.io_preference = "KEEP_CURRENT_SETTING"


def _convert_mirrors_to_ids(mirrors: List[dict]) -> List[str]:
    """
    Converts Playbook format to internal Backend string format.
    Input: [{'primary_volume_id': 100, 'mirror_unit_number': 1}]
    Output: ["00:00:64,1"]
    """
    if not mirrors:
        return []

    normalized_list = []
    for m in mirrors:
        p_id = m.get("primary_volume_id")
        mu = m.get("mirror_unit_number")
        if p_id is not None and mu is not None:
            # normalize_ldev_id handles the conversion to 00:00:XX format
            clean_ldev = normalize_ldev_id(str(p_id).strip())
            normalized_list.append(f"{clean_ldev},{str(mu).strip()}")
    return normalized_list


@dataclass
class RemoteConnectionIdInfo(SingleBaseClass):
    storageModel: Optional[str] = None
    storageSerialNumber: Optional[str] = None
    pathGroupId: Optional[int] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@dataclass
class VspOneGadResponse(SingleBaseClass):
    id: Optional[str] = None
    localVolumeId: Optional[int] = None
    muNumber: Optional[int] = None
    localVolumeNickname: Optional[str] = None  # Maps to primary_volume_name
    localVolumeProvisioningType: Optional[str] = None
    remoteConnectionId: Optional[RemoteConnectionIdInfo] = None
    remoteVolumeId: Optional[int] = None
    localVolumeStatus: Optional[str] = None
    localVolumeProcessingStatus: Optional[str] = None
    failureFactor: Optional[str] = None
    localVolumePosition: Optional[str] = None
    localVolumeIoMode: Optional[str] = None
    copySpeed: Optional[int] = None  # Maps to copy_pace
    ioPreference: Optional[str] = None
    pairOperationModeForBlockedQuorumDisk: Optional[str] = None
    copyProgressRate: Optional[int] = None
    dataSynchronizationRate: Optional[int] = None
    copyTime: Optional[int] = None
    createdTime: Optional[str] = None
    localLastUpdatedTime: Optional[str] = None
    localVolumeDifferentialDataManagement: Optional[str] = None
    quorumId: Optional[int] = None  # Maps to quorum_disk_id
    consistencyGroupId: Optional[int] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__post_init__()

    def __post_init__(self):
        if isinstance(self.remoteConnectionId, dict):
            self.remoteConnectionId = RemoteConnectionIdInfo(**self.remoteConnectionId)

    def camel_to_snake_dict(self):
        # 1. Get the standard snake_case conversion
        snake_dict = super().camel_to_snake_dict()

        # 2. Remove the API-specific ID as requested
        snake_dict.pop("id", None)

        # 3. Define the explicit renames based on the target JSON structure
        renames = {
            "mu_number": "mirror_unit_number",
            "local_volume_id": "primary_volume_id",
            "local_volume_nickname": "primary_volume_name",
            "local_volume_provisioning_type": "primary_volume_provisioning_type",
            "local_volume_status": "primary_volume_status",
            "local_volume_processing_status": "primary_volume_processing_status",
            "local_volume_position": "primary_volume_position",
            "local_volume_io_mode": "primary_volume_io_mode",
            "local_volume_differential_data_management": "primary_volume_differential_data_management",
            "remote_volume_id": "secondary_volume_id",
            "copy_speed": "copy_pace",
            "quorum_id": "quorum_disk_id",
        }

        # 4. Apply renames
        for old_key, new_key in renames.items():
            if old_key in snake_dict:
                snake_dict[new_key] = snake_dict.pop(old_key)

        # 5. Add Hex calculations
        if self.localVolumeId is not None:
            snake_dict["primary_volume_id_hex"] = volume_id_to_hex_format(self.localVolumeId)
        if self.remoteVolumeId is not None:
            snake_dict["secondary_volume_id_hex"] = volume_id_to_hex_format(self.remoteVolumeId)

        return snake_dict


@dataclass
class VspOneGadList(BaseDataClass):
    """Matches the outer shell of the sample output, simplified like Snapshots."""

    data: List[VspOneGadResponse] = None

    def __init__(self, *args, **kwargs):
        # We pass only 'data' to super if it exists in kwargs,
        # or just call super() to be safe.
        super().__init__(*args, **kwargs)
        self.__post_init__()

    def __post_init__(self):
        if self.data:
            self.data = [VspOneGadResponse(**item) if isinstance(item, dict) else item for item in self.data]

    def camel_to_snake_dict(self):
        new_data = [item.camel_to_snake_dict() for item in self.data] if self.data else []
        return new_data
