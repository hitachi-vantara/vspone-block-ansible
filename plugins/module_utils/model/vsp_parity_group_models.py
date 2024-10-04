from dataclasses import dataclass, asdict, fields
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass
except ImportError:
    from common_base_models import BaseDataClass, SingleBaseClass


@dataclass
class ParityGroupFactSpec:
    parity_group_id: Optional[str] = None


@dataclass
class VSPPfrestParityGroup(SingleBaseClass):
    parityGroupId: str = None
    availableVolumeCapacity: int = None
    raidLevel: str = None
    driveTypeName: str = None
    isCopyBackModeEnabled: bool = None
    isEncryptionEnabled: bool = None
    totalCapacity: int = None
    isAcceleratedCompressionEnabled: bool = None
    physicalCapacity: int = None
    # Not used fields
    # numOfLdevs: int = None
    # usedCapacityRate: int = None
    # availableVolumeCapacityInKB: int = None
    # raidType: str = None
    # clprId: int = None
    # driveType: str = None
    # availablePhysicalCapacity: int = None
    # spaces: List[] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@dataclass
class VSPPfrestParityGroupList(BaseDataClass):
    data: List[VSPPfrestParityGroup] = None


@dataclass
class VSPPfrestParityGroupSpace(SingleBaseClass):
    lbaSize: str = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@dataclass
class VSPPfrestExternalParityGroup(SingleBaseClass):
    externalParityGroupId: str = None
    availableVolumeCapacity: int = None
    usedCapacityRate: int = None
    spaces: List[VSPPfrestParityGroupSpace] = None
    # Not used fields
    # numOfLdevs: int = None
    # emulationType: str = None
    # clprId: int = None
    # externalProductId: str = None
    # availableVolumeCapacityInKB: int = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@dataclass
class VSPPfrestExternalParityGroupList(BaseDataClass):
    data: List[VSPPfrestExternalParityGroup] = None


@dataclass
class VSPPfrestLdev(SingleBaseClass):
    ldevId: int = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)


@dataclass
class VSPPfrestLdevList(BaseDataClass):
    data: List[VSPPfrestLdev] = None


@dataclass
class VSPParityGroup(SingleBaseClass):
    resourceId: str = None
    parityGroupId: str = None
    freeCapacity: str = None
    resourceGroupId: int = None
    totalCapacity: str = None
    ldevIds: List[int] = None
    raidLevel: str = None
    driveType: str = None
    copybackMode: bool = None
    status: str = None
    isPoolArrayGroup: bool = None
    isAcceleratedCompression: bool = None
    isEncryptionEnabled: bool = None


@dataclass
class VSPParityGroups(BaseDataClass):
    data: List[VSPParityGroup] = None

@dataclass
class VSPParityGroupUAIG(SingleBaseClass):
    resourceId: str = None
    parityGroupId: str = None
    freeCapacity: int = 0
    resourceGroupId: int = 0
    totalCapacity: int = 0
    ldevIds: List[int] = None
    raidLevel: str = None
    driveType: str = None
    copybackMode: bool = False
    status: str = None
    isPoolArrayGroup: bool = False
    isAcceleratedCompression: bool = False
    isEncryptionEnabled: bool = False

@dataclass
class VSPParityGroupsUAIG(BaseDataClass):
    data: List[VSPParityGroupUAIG] = None