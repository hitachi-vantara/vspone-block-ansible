from dataclasses import dataclass, field, asdict
from typing import Optional, List


@dataclass
class ConnectionInfo:
    """_summary_"""

    address: str
    username: Optional[str] = None
    password: Optional[str] = None
    api_token: Optional[str] = None
    subscriber_id: Optional[str] = None
    connection_type: str = field(
        default="direct", metadata={"field": "connection_type"}
    )
    changed: bool = field(default=False, metadata={"field": "changed"})


@dataclass
class StorageSystemInfo:
    serial: int


@dataclass
class TaskLevel:
    state: str


@dataclass
class TenantInfo:
    partnerId: Optional[str] = None
    subscriberId: Optional[str] = None


# Define a parent class with the common functionality
class BaseDataClass:

    def __init__(self, data=None):
        self.data = data if data is not None else []

    def data_to_list(self):
        return [item.to_dict() for item in self.data]

    def __setattr__(self, name, value):
        if name == "data":
            super().__setattr__(name, value)
        else:
            raise AttributeError("Cannot set attribute directly")


class SingleBaseClass:

    def __init__(self, **kwargs):
        for field in self.__dataclass_fields__.keys():
            setattr(self, field, kwargs.get(field, None))

    def to_dict(self):
        return asdict(self)


@dataclass
class VSPStorageDevice:
    storageDeviceId: str
    model: str
    ip: str
    serialNumber: int
    ctl1Ip: str
    ctl2Ip: str
    dkcMicroVersion: str
    isSecure: bool

    def __init__(self, **kwargs):
        for key in self.__annotations__.keys():
            setattr(self, key, kwargs.get(key, None))