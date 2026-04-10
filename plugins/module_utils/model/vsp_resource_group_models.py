from dataclasses import dataclass, asdict
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass
    from ..common.ansible_common import normalize_ldev_id
except ImportError:
    from .common_base_models import BaseDataClass, SingleBaseClass
    from common.ansible_common import normalize_ldev_id


@dataclass
class VSPResourceGroupFactSpec(SingleBaseClass):
    name: Optional[str] = None
    id: Optional[int] = None
    is_locked: Optional[bool] = None
    is_simple: Optional[bool] = False
    query: Optional[List[str]] = None

    def is_empty(self):
        if (
            self.name is None
            and self.id is None
            and self.is_locked is None
            and self.is_simple is None
            and self.query is None
        ):
            return True
        return False


@dataclass
class HostGroupInfo:
    id: Optional[int] = None
    port: str = None
    port_id: str = None
    name: str = None

    def __post_init__(self):
        if self.port_id is None:
            self.port_id = self.port


@dataclass
class HostGroupSpec:
    id: Optional[int] = None
    port: str = None
    port_id: str = None
    name: str = None
    ids: Optional[List[int]] = None
    begin_id: Optional[int] = None
    end_id: Optional[int] = None

    def __post_init__(self):
        if self.port_id is not None:
            self.port = self.port_id

        if self.id is not None and self.id > 254:
            raise ValueError(f"'id' must be 254 or less, got {self.id}")

        if self.ids is not None:
            invalid = [i for i in self.ids if i > 254]
            if invalid:
                raise ValueError(
                    f"All values in 'ids' must be 254 or less, got invalid values: {invalid}"
                )

        if self.begin_id is not None and self.begin_id > 254:
            raise ValueError(f"'begin_id' must be 254 or less, got {self.begin_id}")

        if self.end_id is not None and self.end_id > 254:
            raise ValueError(f"'end_id' must be 254 or less, got {self.end_id}")

        # Check which identifier fields are provided
        has_name = self.name is not None
        has_ids = self.ids is not None
        has_range = self.begin_id is not None or self.end_id is not None

        provided = [
            label
            for label, flag in [
                ("name", has_name),
                ("ids", has_ids),
                ("begin_id/end_id", has_range),
            ]
            if flag
        ]

        if len(provided) == 0:
            raise ValueError(
                "One of 'name', 'ids', or 'begin_id/end_id' must be provided."
            )

        if len(provided) > 1:
            raise ValueError(
                f"Only one of 'name', 'ids', or 'begin_id/end_id' can be provided, "
                f"but got: {', '.join(provided)}"
            )

        # If either begin_id or end_id is given, both must be present
        if (self.begin_id is None) != (self.end_id is None):
            raise ValueError(
                "'begin_id' and 'end_id' must both be provided together, "
                f"got begin_id={self.begin_id}, end_id={self.end_id}"
            )

        # begin_id must be less than end_id
        if self.begin_id is not None and self.end_id is not None:
            if self.begin_id >= self.end_id:
                raise ValueError(
                    f"'begin_id' ({self.begin_id}) must be less than 'end_id' ({self.end_id})"
                )


@dataclass
class VSPResourceGroupSpec(SingleBaseClass):
    id: Optional[int] = None
    name: Optional[str] = None
    virtual_storage_serial: Optional[str] = None
    virtual_storage_model: Optional[str] = None
    virtual_storage_type: Optional[str] = None
    ldevs: Optional[List[int]] = None
    ports: Optional[List[str]] = None
    port_ids: Optional[List[str]] = None
    parity_groups: Optional[List[str]] = None
    storage_pool_ids: Optional[List[int]] = None
    host_groups_simple: Optional[List[str]] = None
    host_groups: Optional[List[HostGroupSpec]] = None
    iscsi_targets: Optional[List[HostGroupSpec]] = None
    iscsi_targets_simple: Optional[List[str]] = None
    nvm_subsystem_ids: Optional[List[int]] = None
    state: Optional[str] = None
    force: Optional[bool] = False
    add_resource_time_out_in_sec: Optional[int] = None
    parity_group_ids: Optional[List[str]] = None

    external_parity_groups: Optional[List[str]] = None
    start_ldev: Optional[int] = None
    end_ldev: Optional[int] = None
    begin_ldev_id: Optional[int] = None
    end_ldev_id: Optional[int] = None

    def __post_init__(self):
        if self.host_groups is not None:
            self.host_groups = [HostGroupSpec(**x) for x in self.host_groups]
        if self.iscsi_targets is not None:
            self.iscsi_targets = [HostGroupSpec(**x) for x in self.iscsi_targets]
        if self.begin_ldev_id is not None:
            self.start_ldev = self.begin_ldev_id
        if self.end_ldev_id is not None:
            self.end_ldev = self.end_ldev_id
        if self.start_ldev:
            self.start_ldev = normalize_ldev_id(self.start_ldev)
        if self.end_ldev:
            self.end_ldev = normalize_ldev_id(self.end_ldev)
        if self.ldevs:
            self.ldevs = [normalize_ldev_id(ldev) for ldev in self.ldevs]
        if self.parity_group_ids is not None:
            self.parity_groups = [str(pg_id) for pg_id in self.parity_group_ids]
        if self.port_ids is not None:
            self.ports = [str(port_id) for port_id in self.port_ids]
        if self.virtual_storage_model and self.virtual_storage_serial:
            self.virtual_storage_serial = self.virtual_storage_serial[-5:]


@dataclass
class VirtualStorageMachineInfo(SingleBaseClass):
    virtualStorageDeviceId: str
    virtualSerialNumber: str
    virtualModel: str
    resourceGroupIds: List[int]
    virtualStorageTypeId: str
    virtualModelDetail: Optional[str] = None

    def to_dict(self):
        return asdict(self)


@dataclass
class VirtualStorageMachineInfoList(BaseDataClass):
    data: List[VirtualStorageMachineInfo]


@dataclass
class VspResourceGroupInfo(SingleBaseClass):
    resourceGroupName: str
    resourceGroupId: int
    lockStatus: str
    virtualStorageId: int
    ldevIds: List[int]
    parityGroupIds: List[str]
    externalParityGroupIds: List[str]
    portIds: List[str]
    hostGroupIds: List[HostGroupInfo]
    nvmSubsystemIds: List[int] = None
    selfLock: bool = None
    lockOwner: str = None
    lockHost: str = None
    lockSessionId: int = None
    virtualStorageDeviceId: str = None
    virtualSerialNumber: str = None
    virtualModel: str = None

    def __init__(self, **kwargs):
        self.resourceGroupName = kwargs.get("resourceGroupName")
        self.resourceGroupId = kwargs.get("resourceGroupId")
        self.lockStatus = kwargs.get("lockStatus")
        if "selfLock" in kwargs:
            self.selfLock = kwargs.get("selfLock")
        if "lockOwner" in kwargs:
            self.selfLock = kwargs.get("lockOwner")
        if "lockHost" in kwargs:
            self.lockHost = kwargs.get("lockHost")
        if "lockSessionId" in kwargs:
            self.lockSessionId = kwargs.get("lockSessionId")
        self.virtualStorageId = kwargs.get("virtualStorageId")
        self.ldevIds = kwargs.get("ldevIds")
        self.parityGroupIds = kwargs.get("parityGroupIds")
        self.externalParityGroupIds = kwargs.get("externalParityGroupIds")
        self.portIds = kwargs.get("portIds")
        self.hostGroupIds = kwargs.get("hostGroupIds")
        if "nvmSubsystemIds" in kwargs:
            self.nvmSubsystemIds = kwargs.get("nvmSubsystemIds")

    def to_dict(self):
        return asdict(self)


@dataclass
class VspResourceGroupInfoList(BaseDataClass):
    data: List[VspResourceGroupInfo]


@dataclass
class DisplayResourceGroup:
    name: str
    id: int
    lockStatus: str
    virtualStorageId: int
    ldevs: List[int]
    parityGroups: List[str]
    externalParityGroups: List[str]
    ports: List[str]
    hostGroups: List[HostGroupInfo]
    nvmSubsystemIds: List[int]
    storagePoolIds: List[int]
    iscsiTargets: List[HostGroupInfo]
    selfLock: bool
    lockOwner: str
    lockHost: str
    lockSessionId: int
    virtualStorageDeviceId: str
    virtualSerialNumber: str
    virtualModel: str
    virtualDeviceType: str

    def __init__(self):
        self.name = None
        self.id = None
        self.lockStatus = None
        self.virtualStorageId = None
        self.ldevs = None
        self.parityGroups = None
        self.externalParityGroups = None
        self.ports = None
        self.hostGroups = None
        self.nvmSubsystemIds = None
        self.storagePoolIds = None
        self.iscsiTargets = None
        self.selfLock = None
        self.lockOwner = None
        self.lockHost = None
        self.lockSessionId = None
        self.virtualStorageDeviceId = None
        self.virtualSerialNumber = None
        self.virtualModel = None
        self.virtualDeviceType = None

    def to_dict(self):
        return asdict(self)


@dataclass
class DisplayResourceGroupList(BaseDataClass):
    data: List[DisplayResourceGroup]
