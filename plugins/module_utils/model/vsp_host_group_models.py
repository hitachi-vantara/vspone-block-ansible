from dataclasses import dataclass, asdict
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass
    from ..common.ansible_common import dicts_to_dataclass_list
except ImportError:
    from .common_base_models import BaseDataClass, SingleBaseClass
    from common.ansible_common import dicts_to_dataclass_list


@dataclass
class GetHostGroupSpec:
    name: Optional[str] = None
    ports: Optional[List[str]] = None
    lun: Optional[int] = None
    query: Optional[List[str]] = None


@dataclass
class HostGroupSpec(SingleBaseClass):
    state: Optional[str] = None
    name: Optional[str] = None
    port: Optional[str] = None
    host_mode: Optional[str] = None
    host_mode_options: Optional[List[int]] = None
    luns: Optional[List[int]] = None
    wwns: Optional[List[str]] = None
    delete_all_luns: Optional[bool] = None

    def __init__(self, **kwargs):
        for field in self.__dataclass_fields__.keys():
            setattr(self, field, kwargs.get(field, None))
        self.delete_all_luns = kwargs.get("should_delete_all_luns", None)

@dataclass
class VSPPortResponse:
    portId: str = None
    portType: str = None

    def __init__(self, **kwargs):
        self.portId = kwargs.get("portId")
        self.portType = kwargs.get("portType")


@dataclass
class VSPWwnResponse:
    portId: str = None
    hostWwn: str = None
    wwnNickname: str = None

    def __init__(self, **kwargs):
        self.portId = kwargs.get("portId")
        self.hostWwn = kwargs.get("hostWwn")
        self.wwnNickname = kwargs.get("wwnNickname")


@dataclass
class VSPLunResponse:
    portId: str = None
    lun: int = None
    ldevId: int = None

    def __init__(self, **kwargs):
        self.portId = kwargs.get("portId")
        self.lun = kwargs.get("lun")
        self.ldevId = kwargs.get("ldevId")


@dataclass
class VSPHostModeOptionProvResponse:
    hostModeOption: str = None
    hostModeOptionNumber: int = None


@dataclass
class VSPLunPathProvResponse:
    ldevId: int = None
    lunId: int = None


@dataclass
class VSPWwnProvResponse:
    id: int = None
    name: str = None


@dataclass
class VSPHostGroupInfo(SingleBaseClass):
    hostGroupId: int = None
    hostGroupName: str = None
    hostMode: str = None
    hostModeOptions: List[VSPHostModeOptionProvResponse] = None
    lunPaths: List[VSPLunPathProvResponse] = None
    wwns: List[VSPWwnProvResponse] = None
    port: str = None
    resourceGroupId: int = None

    def __init__(self, **kwargs):
        self.hostGroupId = kwargs.get("hostGroupId")
        self.hostGroupName = kwargs.get("hostGroupName")
        self.hostMode = kwargs.get("hostMode")
        if "hostModeOptions" in kwargs:
            self.hostModeOptions = dicts_to_dataclass_list(
                kwargs.get("hostModeOptions"), VSPHostModeOptionProvResponse
            )
        if "lunPaths" in kwargs:
            self.lunPaths = [
                VSPLunPathProvResponse(**lunPath) for lunPath in kwargs.get("lunPaths")
            ]
        if "wwns" in kwargs:
            self.wwns = [VSPWwnProvResponse(**wwn) for wwn in kwargs.get("wwns")]
        self.port = kwargs.get("port")
        self.resourceGroupId = kwargs.get("resourceGroupId")


@dataclass
class VSPHostGroupsInfo(BaseDataClass):
    data: List[VSPHostGroupInfo]


@dataclass
class VSPOneHostGroupInfo(BaseDataClass):
    data: VSPHostGroupInfo


@dataclass
class VSPModifyHostGroupProvResponse:
    changed: bool = None
    hostGroup: VSPHostGroupInfo = None
    comments: List[str] = None
    comment: str = None
