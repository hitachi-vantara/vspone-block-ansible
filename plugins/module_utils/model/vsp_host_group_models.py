from dataclasses import dataclass
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass
    from ..common.ansible_common import (
        dicts_to_dataclass_list,
        normalize_ldev_id,
        volume_id_to_hex_format,
    )
    from ..common.ansible_common_constants import MAX_BULK_PAIRS
    from ..message.vsp_host_group_msgs import VSPHostGroupValidationMsg
except ImportError:
    from .common_base_models import BaseDataClass, SingleBaseClass
    from common.ansible_common import (
        dicts_to_dataclass_list,
        normalize_ldev_id,
        volume_id_to_hex_format,
    )
    from message.vsp_host_group_msgs import VSPHostGroupValidationMsg


@dataclass
class GetHostGroupSpec:
    name: Optional[str] = None
    ports: Optional[List[str]] = None
    port_ids: Optional[List[str]] = None
    lun: Optional[int] = None
    query: Optional[List[str]] = None
    host_group_number: Optional[int] = None

    def __post_init__(self):
        if self.port_ids and not self.ports:
            self.ports = self.port_ids


@dataclass
class HostWWN:
    wwn: str = None
    nick_name: str = None
    nickname: str = None

    def __post_init__(self, **kwargs):
        if self.nickname is not None:
            self.nick_name = self.nickname


@dataclass
class HostGroupPaths(SingleBaseClass):
    ldev: int = None
    lun: int = None

    def __post_init__(self):
        if self.ldev is not None:
            self.ldev = normalize_ldev_id(self.ldev)


@dataclass
class HostGroupSpec(SingleBaseClass):
    state: Optional[str] = None
    name: Optional[str] = None
    port: Optional[str] = None
    port_id: Optional[str] = None
    host_mode: Optional[str] = None
    host_mode_options: Optional[List[int]] = None
    ldevs: Optional[List[int]] = None
    wwns: Optional[List[HostWWN]] = None
    delete_all_luns: Optional[bool] = None
    asymmetric_access_priority: Optional[str] = None
    host_group_number: Optional[int] = None
    should_release_host_reserve: Optional[bool] = None
    lun: Optional[int] = None
    lun_paths: Optional[List[HostGroupPaths]] = None
    ports: Optional[List[str]] = None
    port_ids: Optional[List[str]] = None
    should_delete_all_volumes: Optional[bool] = None
    comments: Optional[List[str]] = None
    errors: Optional[List[str]] = None

    def __init__(self, **kwargs):
        for field in self.__dataclass_fields__.keys():
            setattr(self, field, kwargs.get(field, None))
        self.delete_all_luns = kwargs.get("should_delete_all_ldevs", None)

        if kwargs.get("should_delete_all_volumes", None) is not None:
            self.delete_all_luns = kwargs.get("should_delete_all_volumes", None)

        self.__post_init__()

    def __post_init__(self):
        if self.wwns:
            self.wwns = [HostWWN(**wwn) for wwn in self.wwns]

        if self.ldevs is not None and self.lun_paths is not None:
            raise ValueError(
                VSPHostGroupValidationMsg.LDEVS_OR_LUN_PATHS_NOT_BOTH.value
            )

        if self.ldevs:
            self.ldevs = [normalize_ldev_id(ldev_id) for ldev_id in self.ldevs]
        if self.lun_paths:
            self.lun_paths = [HostGroupPaths(**path) for path in self.lun_paths]

        if self.port is not None and self.ports is not None:
            raise ValueError("Specify either 'port' or 'ports', not both.")

        if self.port_id is not None and self.port_ids is not None:
            raise ValueError(
                VSPHostGroupValidationMsg.PORT_ID_OR_PORT_IDS_NOT_BOTH.value
            )

        if self.port_ids is not None and not (
            1 <= len(self.port_ids) <= MAX_BULK_PAIRS
        ):
            raise ValueError(VSPHostGroupValidationMsg.PORT_IDS_LIST_RANGE.value)
        if (
            self.port is None
            and self.ports is None
            and self.port_id is None
            and self.port_ids is None
        ):
            raise ValueError(VSPHostGroupValidationMsg.PORT_OR_PORT_ID_REQUIRED.value)

        if self.ports is not None and len(self.ports) > 6:
            raise ValueError(VSPHostGroupValidationMsg.PORTS_LIST_MAX_EXCEEDED.value)

        if self.port_ids is not None and len(self.port_ids) > 6:
            raise ValueError(VSPHostGroupValidationMsg.PORT_IDS_LIST_MAX_EXCEEDED.value)

        if self.port_id:
            self.port = self.port_id
        if self.port_ids:
            self.ports = self.port_ids


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
class LuHostReserve(SingleBaseClass):
    openSystem: bool = None
    persistent: bool = None
    pgrKey: bool = None
    mainframe: bool = None
    acaReserve: bool = None


@dataclass
class VSPLunResponse(SingleBaseClass):
    portId: Optional[str] = None
    lun: Optional[int] = None
    ldevId: Optional[int] = None
    hostGroupNumber: Optional[int] = None
    hostMode: Optional[str] = None
    lunId: Optional[str] = None
    isCommandDevice: Optional[bool] = None
    luHostReserve: Optional[LuHostReserve] = None
    asymmetricAccessState: Optional[str] = None
    isAluaEnabled: Optional[bool] = None
    hostModeOptions: Optional[List[str]] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.luHostReserve = (
            LuHostReserve(**kwargs.get("luHostReserve"))
            if kwargs.get("luHostReserve")
            else None
        )


@dataclass
class VSPLunResponses(BaseDataClass):
    data: List[VSPLunResponse] = None


@dataclass
class VSPHostModeOption(SingleBaseClass):
    hostModeOption: str = None
    hostModeOptionNumber: int = None


@dataclass
class VSPLunPathDetails(SingleBaseClass):
    ldevId: int = None
    ldevIdHex: str = None
    portId: str = None
    hostGroupNumber: int = None
    hostMode: str = None
    isCommandDevice: bool = None
    luHostReserve: Optional[LuHostReserve] = None
    lunId: str = None
    lun: int = None
    asymmetricAccessState: Optional[str] = None
    isAluaEnabled: Optional[bool] = None
    hostModeOptions: Optional[List[str]] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if kwargs.get("luHostReserve"):
            self.luHostReserve = LuHostReserve(**kwargs.get("luHostReserve"))
        self.__post_init__()

    def __post_init__(self):
        if self.ldevId:
            self.ldevIdHex = volume_id_to_hex_format(self.ldevId)


@dataclass
class VSPLunPath(SingleBaseClass):
    # lunId: int = None
    ldevId: int = None
    # portId: str = None
    lun: int = None
    # hostGroupNumber: int = None
    # hostMode: str = None

    # isCommandDevice: bool = None
    # luHostReserve: Optional[LuHostReserve] = None
    # hostModeOptions: List = None

    # def __init__(self, **kwargs):
    # if kwargs.get("luHostReserve"):
    #     self.luHostReserve = LuHostReserve(**kwargs.get("luHostReserve"))


@dataclass
class VSPWwn(SingleBaseClass):
    id: int = None
    nick_name: str = None
    nickname: str = None

    def __post_init__(self):
        if self.nickname is None:
            self.nickname = self.nick_name


@dataclass
class VSPHostGroupInfo(SingleBaseClass):
    hostGroupId: int = None
    hostGroupName: str = None
    hostMode: str = None
    hostModeOptions: List[VSPHostModeOption] = None
    lunPaths: List[VSPLunPathDetails] = None
    wwns: List[VSPWwn] = None
    port: str = None
    resourceGroupId: int = None
    portId: str = None
    hostGroupNumber: int = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.hostGroupId = (
            kwargs.get("hostGroupNumber")
            if kwargs.get("hostGroupNumber") is not None
            else kwargs.get("hostGroupId")
        )
        self.hostGroupName = kwargs.get("hostGroupName")
        self.hostMode = kwargs.get("hostMode")
        if "hostModeOptions" in kwargs:
            self.hostModeOptions = dicts_to_dataclass_list(
                kwargs.get("hostModeOptions"), VSPHostModeOption
            )
        if "lunPaths" in kwargs:
            if (
                kwargs.get("lunPaths")
                and "luHostReserve" in kwargs.get("lunPaths")[0].keys()
            ):
                self.lunPaths = [
                    VSPLunPathDetails(**lunPath) for lunPath in kwargs.get("lunPaths")
                ]
            else:
                self.lunPaths = [
                    VSPLunPath(**lunPath) for lunPath in kwargs.get("lunPaths")
                ]
        if "wwns" in kwargs:
            self.wwns = [VSPWwn(**wwn) for wwn in kwargs.get("wwns")]
        self.port = kwargs.get("port")
        self.portId = kwargs.get("portId")
        if self.port is not None and self.portId is None:
            self.portId = self.port
        self.resourceGroupId = kwargs.get("resourceGroupId")
        self.__post__init__()

    def __post__init__(self):
        self.hostGroupNumber = self.hostGroupId

    def camel_to_snake_dict(self) -> dict:
        data = super().camel_to_snake_dict()
        data["port_id"] = data.pop("port")
        data.pop("host_group_number", None)
        return data


@dataclass
class VSPHostGroupsInfo(BaseDataClass):
    data: List[VSPHostGroupInfo]


@dataclass
class VSPOneHostGroupInfo(BaseDataClass):
    data: VSPHostGroupInfo


@dataclass
class VSPModifyHostGroupProvResponse(SingleBaseClass):
    changed: bool = None
    host_group: VSPHostGroupInfo = None
    comments: List[str] = None
    comment: str = None
    errors: List[str] = None

    def camel_to_snake_dict(self):
        data = super().camel_to_snake_dict()
        if not data.get("comment"):
            data.pop("comment")
        if not data.get("comments"):
            data.pop("comments")
        if not data.get("errors"):
            data.pop("errors")
        return data


@dataclass
class HostModesRes(SingleBaseClass):
    hostModeId: int = None
    hostModeName: str = None
    hostModeDisplay: str = None


@dataclass
class hostModeOptionsRes(SingleBaseClass):
    hostModeOptionId: int = None
    hostModeOptionDescription: str = None
    scope: str = None
    requiredHostModes: List[int] = None


@dataclass
class HostModeOptionsResponse(SingleBaseClass):
    hostModes: List[HostModesRes] = None
    hostModeOptions: List[hostModeOptionsRes] = None

    def __post_init__(self):
        if self.hostModes:
            self.hostModes = [HostModesRes(**mode) for mode in self.hostModes]
        if self.hostModeOptions:
            self.hostModeOptions = [
                hostModeOptionsRes(**option) for option in self.hostModeOptions
            ]
