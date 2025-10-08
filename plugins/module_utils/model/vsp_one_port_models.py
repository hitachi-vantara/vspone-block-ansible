from dataclasses import dataclass
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass
except ImportError:
    from common_base_models import BaseDataClass, SingleBaseClass

PROTOCOL_LIST = ["fc", "iscsi", "nvme_tcp", "nvme"]

PROTOCOL_MAP = {
    "fc": "FC",
    "iscsi": "iSCSI",
    "nvme_tcp": "NVME_TCP",
    "nvme": "NVME_TCP",
}

# VSP one Port Response Models


@dataclass
class IpInformation(SingleBaseClass):
    address: Optional[str] = None
    subnetMask: Optional[str] = None
    defaultGateway: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@dataclass
class Ipv6Information(SingleBaseClass):
    linklocal: Optional[str] = None
    linklocalAddress: Optional[str] = None
    linklocalAddressStatus: Optional[str] = None
    global_: Optional[str] = None
    globalAddress: Optional[str] = None
    globalAddressStatus: Optional[str] = None
    defaultGateway: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if "global" in kwargs:
            self.global_ = kwargs["global"]

    def camel_to_snake_dict(self):
        data = super().camel_to_snake_dict()
        if "global_" in data:
            data["global"] = data.pop("global_")
        return data


@dataclass
class IscsiInformation(SingleBaseClass):
    vlanUse: Optional[bool] = None
    vlanId: Optional[int] = None
    ipMode: Optional[str] = None
    ipv4Information: Optional[IpInformation] = None
    ipv6Information: Optional[Ipv6Information] = None
    isIpv6Updating: Optional[bool] = None
    tcpPort: Optional[int] = None
    discoveryTcpPort: Optional[int] = None
    selectiveAck: Optional[bool] = None
    delayedAck: Optional[bool] = None
    windowSize: Optional[str] = None
    mtuSize: Optional[str] = None
    linkMtuSize: Optional[str] = None
    keepAliveTimer: Optional[int] = None
    isnsServerMode: Optional[bool] = None
    isnsServerIpAddress: Optional[str] = None
    isnsServerPort: Optional[int] = None
    virtualPortEnabled: Optional[bool] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__post_init__()

    def __post_init__(self):
        if self.ipv4Information is not None:
            self.ipv4Information = IpInformation(**self.ipv4Information)
        if self.ipv6Information is not None:
            self.ipv6Information = Ipv6Information(**self.ipv6Information)


@dataclass
class NvmeTcpInformation(SingleBaseClass):
    vlanUse: Optional[bool] = None
    vlanId: Optional[int] = None
    ipMode: Optional[str] = None
    ipv4Information: Optional[IpInformation] = None
    ipv6Information: Optional[Ipv6Information] = None
    isIpv6Updating: Optional[bool] = None
    tcpPort: Optional[int] = None
    discoveryTcpPort: Optional[int] = None
    selectiveAck: Optional[bool] = None
    delayedAck: Optional[bool] = None
    windowSize: Optional[str] = None
    mtuSize: Optional[str] = None
    linkMtuSize: Optional[str] = None
    virtualPortEnabled: Optional[bool] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__post_init__()

    def __post_init__(self):
        if self.ipv4Information is not None:
            self.ipv4Information = IpInformation(**self.ipv4Information)
        if self.ipv6Information is not None:
            self.ipv6Information = Ipv6Information(**self.ipv6Information)


@dataclass
class FCInformationRes(SingleBaseClass):
    alPa: Optional[str] = None
    fabricSwitchSetting: Optional[bool] = None
    connectionType: Optional[str] = None
    sfpDataTransferRate: Optional[str] = None
    portMode: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@dataclass
class VspOnePortResponse(SingleBaseClass):
    id: Optional[str] = None
    protocol: Optional[str] = None
    portIscsiName: Optional[str] = None
    portSpeed: Optional[str] = None
    actualPortSpeed: Optional[str] = None
    portSecurity: Optional[bool] = None
    iscsiInformation: Optional[IscsiInformation] = None
    nvmeTcpInformation: Optional[IscsiInformation] = None
    fcInformation: Optional[FCInformationRes] = None
    portWwn: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__post_init__()

    def __post_init__(self):
        if self.iscsiInformation is not None:
            self.iscsiInformation = IscsiInformation(**self.iscsiInformation)

        if self.nvmeTcpInformation is not None:
            self.nvmeTcpInformation = NvmeTcpInformation(**self.nvmeTcpInformation)
        if self.fcInformation is not None:
            self.fcInformation = FCInformationRes(**self.fcInformation)

    def camel_to_snake_dict(self):
        data = super().camel_to_snake_dict()
        if data.get("nvme_tcp_information") is None:
            data.pop("nvme_tcp_information")
        if data.get("fc_information") is None:
            data.pop("fc_information")
        if data.get("iscsi_information") is None:
            data.pop("iscsi_information")
        return data


@dataclass
class VspOnePortList(BaseDataClass):
    data: List[VspOnePortResponse] = None


# VSP one Port Spec Models
@dataclass
class Ipv4Settings(SingleBaseClass):
    address: Optional[str] = None
    subnet_mask: Optional[str] = None
    default_gateway: Optional[str] = None


@dataclass
class Ipv6Settings(SingleBaseClass):
    linklocal: Optional[str] = None
    linklocal_address: Optional[str] = None
    linklocal_address_status: Optional[str] = None
    global_: Optional[str] = None
    global_address: Optional[str] = None
    global_address_status: Optional[str] = None
    default_gateway: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if "global" in kwargs:
            self.global_ = kwargs["global"]


@dataclass
class FcSettings(SingleBaseClass):
    al_pa: Optional[str] = None
    should_enable_fabric_switch_setting: Optional[bool] = None
    connection_type: Optional[str] = None


@dataclass
class IscsiSettings(SingleBaseClass):
    enable_vlan_use: Optional[bool] = None
    add_vlan_id: Optional[int] = None
    delete_vlan_id: Optional[int] = None
    ip_mode: Optional[str] = None
    ipv4_configuration: Optional[Ipv4Settings] = None
    ipv6_configuration: Optional[Ipv6Settings] = None
    tcp_port: Optional[int] = None
    enable_selective_ack: Optional[bool] = None
    enable_delayed_ack: Optional[bool] = None
    window_size: Optional[str] = None
    mtu_size: Optional[str] = None
    keep_alive_timer: Optional[int] = None
    enable_isns_server_mode: Optional[bool] = None
    isns_server_ip_address: Optional[str] = None
    isns_server_port: Optional[int] = None
    enable_virtual_port: Optional[bool] = None

    def __post_init__(self):
        if self.ipv4_configuration and not isinstance(
            self.ipv4_configuration, Ipv4Settings
        ):
            self.ipv4_configuration = Ipv4Settings(**self.ipv4_configuration)
        if self.ipv6_configuration and not isinstance(
            self.ipv6_configuration, Ipv6Settings
        ):
            self.ipv6_configuration = Ipv6Settings(**self.ipv6_configuration)


@dataclass
class NvmeTcpSettings(SingleBaseClass):
    enable_vlan_use: Optional[bool] = None
    add_vlan_id: Optional[int] = None
    delete_vlan_id: Optional[int] = None
    ip_mode: Optional[str] = None
    ipv4_configuration: Optional[Ipv4Settings] = None
    ipv6_configuration: Optional[Ipv6Settings] = None
    tcp_port: Optional[int] = None
    discovery_tcp_port: Optional[int] = None
    enable_selective_ack: Optional[bool] = None
    enable_delayed_ack: Optional[bool] = None
    window_size: Optional[str] = None
    mtu_size: Optional[str] = None

    def __post_init__(self):
        if self.ipv4_configuration and not isinstance(
            self.ipv4_configuration, Ipv4Settings
        ):
            self.ipv4_configuration = Ipv4Settings(**self.ipv4_configuration)
        if self.ipv6_configuration and not isinstance(
            self.ipv6_configuration, Ipv6Settings
        ):
            self.ipv6_configuration = Ipv6Settings(**self.ipv6_configuration)


@dataclass
class VspOnePortSpec(SingleBaseClass):
    port_id: str
    port_speed_in_gbps: Optional[int] = None
    enable_port_security: Optional[bool] = None
    fc_settings: Optional[FcSettings] = None
    iscsi_settings: Optional[IscsiSettings] = None
    nvme_tcp_settings: Optional[NvmeTcpSettings] = None
    comment: Optional[str] = None

    def __post_init__(self):
        if self.fc_settings and not isinstance(self.fc_settings, FcSettings):
            self.fc_settings = FcSettings(**self.fc_settings)
        if self.iscsi_settings and not isinstance(self.iscsi_settings, IscsiSettings):
            self.iscsi_settings = IscsiSettings(**self.iscsi_settings)
        if self.nvme_tcp_settings and not isinstance(
            self.nvme_tcp_settings, NvmeTcpSettings
        ):
            self.nvme_tcp_settings = NvmeTcpSettings(**self.nvme_tcp_settings)

    def create_port_setting_payload(self) -> dict:
        """Create a payload dictionary for port settings API call."""
        payload = {}

        # Port speed mapping
        speed_mapping = {
            0: "NUMBER_0",  # Auto
            1: "NUMBER_1",  # 1 Gbps
            4: "NUMBER_4",  # 4 Gbps
            8: "NUMBER_8",  # 8 Gbps
            10: "NUMBER_10",  # 10 Gbps
            16: "NUMBER_16",  # 16 Gbps
            25: "NUMBER_25",  # 25 Gbps
            32: "NUMBER_32",  # 32 Gbps
            64: "NUMBER_64",  # 64 Gbps
            100: "NUMBER_100",  # 100 Gbps
        }

        if self.port_speed_in_gbps is not None:
            payload["portSpeed"] = speed_mapping.get(self.port_speed_in_gbps)

        if self.enable_port_security is not None:
            payload["portSecurity"] = self.enable_port_security

        # FC settings
        if self.fc_settings:
            fc_info = {}
            if self.fc_settings.al_pa is not None:
                fc_info["alPa"] = self.fc_settings.al_pa
            if self.fc_settings.should_enable_fabric_switch_setting is not None:
                fc_info["fabricSwitchSetting"] = (
                    self.fc_settings.should_enable_fabric_switch_setting
                )
            if self.fc_settings.connection_type is not None:
                fc_info["connectionType"] = self.fc_settings.connection_type
            if fc_info:
                payload["fcInformation"] = fc_info

        # iSCSI settings
        if self.iscsi_settings:
            iscsi_info = {}
            if self.iscsi_settings.enable_vlan_use is not None:
                iscsi_info["vlanUse"] = self.iscsi_settings.enable_vlan_use
            if self.iscsi_settings.add_vlan_id is not None:
                iscsi_info["addVlanId"] = self.iscsi_settings.add_vlan_id
            if self.iscsi_settings.delete_vlan_id is not None:
                iscsi_info["deleteVlanId"] = self.iscsi_settings.delete_vlan_id
            if self.iscsi_settings.ip_mode is not None:
                iscsi_info["ipMode"] = self.iscsi_settings.ip_mode
            if self.iscsi_settings.ipv4_configuration:
                ipv4_info = {}
                if self.iscsi_settings.ipv4_configuration.address is not None:
                    ipv4_info["address"] = (
                        self.iscsi_settings.ipv4_configuration.address
                    )
                if self.iscsi_settings.ipv4_configuration.subnet_mask is not None:
                    ipv4_info["subnetMask"] = (
                        self.iscsi_settings.ipv4_configuration.subnet_mask
                    )
                if self.iscsi_settings.ipv4_configuration.default_gateway is not None:
                    ipv4_info["defaultGateway"] = (
                        self.iscsi_settings.ipv4_configuration.default_gateway
                    )
                if ipv4_info:
                    iscsi_info["ipv4Information"] = ipv4_info
            if self.iscsi_settings.ipv6_configuration:
                ipv6_info = {}
                if self.iscsi_settings.ipv6_configuration.linklocal is not None:
                    ipv6_info["linklocal"] = (
                        self.iscsi_settings.ipv6_configuration.linklocal
                    )
                if self.iscsi_settings.ipv6_configuration.global_ is not None:
                    ipv6_info["global"] = self.iscsi_settings.ipv6_configuration.global_
                if self.iscsi_settings.ipv6_configuration.default_gateway is not None:
                    ipv6_info["defaultGateway"] = (
                        self.iscsi_settings.ipv6_configuration.default_gateway
                    )
                if ipv6_info:
                    iscsi_info["ipv6Information"] = ipv6_info
            if self.iscsi_settings.tcp_port is not None:
                iscsi_info["tcpPort"] = self.iscsi_settings.tcp_port
            if self.iscsi_settings.enable_selective_ack is not None:
                iscsi_info["selectiveAck"] = self.iscsi_settings.enable_selective_ack
            if self.iscsi_settings.enable_delayed_ack is not None:
                iscsi_info["delayedAck"] = self.iscsi_settings.enable_delayed_ack
            if self.iscsi_settings.window_size is not None:
                iscsi_info["windowSize"] = self.iscsi_settings.window_size
            if self.iscsi_settings.mtu_size is not None:
                iscsi_info["mtuSize"] = self.iscsi_settings.mtu_size
            if self.iscsi_settings.keep_alive_timer is not None:
                iscsi_info["keepAliveTimer"] = self.iscsi_settings.keep_alive_timer
            if self.iscsi_settings.enable_isns_server_mode is not None:
                iscsi_info["isnsServerMode"] = (
                    self.iscsi_settings.enable_isns_server_mode
                )
            if self.iscsi_settings.isns_server_ip_address is not None:
                iscsi_info["isnsServerIpAddress"] = (
                    self.iscsi_settings.isns_server_ip_address
                )
            if self.iscsi_settings.isns_server_port is not None:
                iscsi_info["isnsServerPort"] = self.iscsi_settings.isns_server_port
            if self.iscsi_settings.enable_virtual_port is not None:
                iscsi_info["virtualPortEnabled"] = (
                    self.iscsi_settings.enable_virtual_port
                )
            if iscsi_info:
                payload["iscsiInformation"] = iscsi_info

        # NVMe/TCP settings
        if self.nvme_tcp_settings:
            nvme_info = {}
            if self.nvme_tcp_settings.enable_vlan_use is not None:
                nvme_info["vlanUse"] = self.nvme_tcp_settings.enable_vlan_use
            if self.nvme_tcp_settings.add_vlan_id is not None:
                nvme_info["addVlanId"] = self.nvme_tcp_settings.add_vlan_id
            if self.nvme_tcp_settings.delete_vlan_id is not None:
                nvme_info["deleteVlanId"] = self.nvme_tcp_settings.delete_vlan_id
            if self.nvme_tcp_settings.ip_mode is not None:
                nvme_info["ipMode"] = self.nvme_tcp_settings.ip_mode
            if self.nvme_tcp_settings.ipv4_configuration:
                ipv4_info = {}
                if self.nvme_tcp_settings.ipv4_configuration.address is not None:
                    ipv4_info["address"] = (
                        self.nvme_tcp_settings.ipv4_configuration.address
                    )
                if self.nvme_tcp_settings.ipv4_configuration.subnet_mask is not None:
                    ipv4_info["subnetMask"] = (
                        self.nvme_tcp_settings.ipv4_configuration.subnet_mask
                    )
                if (
                    self.nvme_tcp_settings.ipv4_configuration.default_gateway
                    is not None
                ):
                    ipv4_info["defaultGateway"] = (
                        self.nvme_tcp_settings.ipv4_configuration.default_gateway
                    )
                if ipv4_info:
                    nvme_info["ipv4Information"] = ipv4_info
            if self.nvme_tcp_settings.ipv6_configuration:
                ipv6_info = {}
                if self.nvme_tcp_settings.ipv6_configuration.linklocal is not None:
                    ipv6_info["linklocal"] = (
                        self.nvme_tcp_settings.ipv6_configuration.linklocal
                    )
                if self.nvme_tcp_settings.ipv6_configuration.global_ is not None:
                    ipv6_info["global"] = (
                        self.nvme_tcp_settings.ipv6_configuration.global_
                    )
                if (
                    self.nvme_tcp_settings.ipv6_configuration.default_gateway
                    is not None
                ):
                    ipv6_info["defaultGateway"] = (
                        self.nvme_tcp_settings.ipv6_configuration.default_gateway
                    )
                if ipv6_info:
                    nvme_info["ipv6Information"] = ipv6_info
            if self.nvme_tcp_settings.tcp_port is not None:
                nvme_info["tcpPort"] = self.nvme_tcp_settings.tcp_port
            if self.nvme_tcp_settings.discovery_tcp_port is not None:
                nvme_info["discoveryTcpPort"] = (
                    self.nvme_tcp_settings.discovery_tcp_port
                )
            if self.nvme_tcp_settings.enable_selective_ack is not None:
                nvme_info["selectiveAck"] = self.nvme_tcp_settings.enable_selective_ack
            if self.nvme_tcp_settings.enable_delayed_ack is not None:
                nvme_info["delayedAck"] = self.nvme_tcp_settings.enable_delayed_ack
            if self.nvme_tcp_settings.window_size is not None:
                nvme_info["windowSize"] = self.nvme_tcp_settings.window_size
            if self.nvme_tcp_settings.mtu_size is not None:
                nvme_info["mtuSize"] = self.nvme_tcp_settings.mtu_size
            if nvme_info:
                payload["nvmeTcpInformation"] = nvme_info

        return payload


def vsp_one_port_args():
    port_args = {
        "port_id": {"type": "str", "required": True},
        "port_speed_in_gbps": {
            "type": "int",
            "choices": [0, 1, 4, 8, 10, 16, 25, 32, 64, 100],
            "required": False,
        },
        "enable_port_security": {"type": "bool", "required": False},
        "fc_settings": {
            "type": "dict",
            "required": False,
            "options": {
                "al_pa": {"type": "str", "required": False},
                "should_enable_fabric_switch_setting": {
                    "type": "bool",
                    "required": False,
                },
                "connection_type": {
                    "type": "str",
                    "choices": ["Point_To_Point", "FC_AL"],
                    "required": False,
                },
            },
        },
        "iscsi_settings": {
            "type": "dict",
            "required": False,
            "options": {
                "enable_vlan_use": {"type": "bool", "required": False},
                "add_vlan_id": {"type": "int", "required": False},
                "delete_vlan_id": {"type": "int", "required": False},
                "ip_mode": {
                    "type": "str",
                    "choices": ["ipv4", "ipv4v6"],
                    "required": False,
                },
                "ipv4_configuration": {
                    "type": "dict",
                    "required": False,
                    "options": {
                        "address": {"type": "str", "required": False},
                        "subnet_mask": {"type": "str", "required": False},
                        "default_gateway": {"type": "str", "required": False},
                    },
                },
                "ipv6_configuration": {
                    "type": "dict",
                    "required": False,
                    "options": {
                        "linklocal": {"type": "str", "required": False},
                        "global": {"type": "str", "required": False},
                        "default_gateway": {"type": "str", "required": False},
                    },
                },
                "tcp_port": {"type": "int", "required": False},
                "enable_selective_ack": {"type": "bool", "required": False},
                "enable_delayed_ack": {"type": "bool", "required": False},
                "window_size": {
                    "type": "str",
                    "choices": [
                        "NUMBER_16K",
                        "NUMBER_32K",
                        "NUMBER_64K",
                        "NUMBER_128K",
                        "NUMBER_256K",
                        "NUMBER_512K",
                        "NUMBER_1024K",
                    ],
                    "required": False,
                },
                "mtu_size": {
                    "type": "str",
                    "choices": ["NUMBER_1500", "NUMBER_4500", "NUMBER_9000"],
                    "required": False,
                },
                "keep_alive_timer": {"type": "int", "required": False},
                "enable_isns_server_mode": {"type": "bool", "required": False},
                "isns_server_ip_address": {"type": "str", "required": False},
                "isns_server_port": {"type": "int", "required": False},
                "enable_virtual_port": {"type": "bool", "required": False},
            },
        },
        "nvme_tcp_settings": {
            "type": "dict",
            "required": False,
            "options": {
                "enable_vlan_use": {"type": "bool", "required": False},
                "add_vlan_id": {"type": "int", "required": False},
                "delete_vlan_id": {"type": "int", "required": False},
                "ip_mode": {
                    "type": "str",
                    "choices": ["ipv4", "ipv4v6"],
                    "required": False,
                },
                "ipv4_configuration": {
                    "type": "dict",
                    "required": False,
                    "options": {
                        "address": {"type": "str", "required": False},
                        "subnet_mask": {"type": "str", "required": False},
                        "default_gateway": {"type": "str", "required": False},
                    },
                },
                "ipv6_configuration": {
                    "type": "dict",
                    "required": False,
                    "options": {
                        "linklocal": {"type": "str", "required": False},
                        "global_": {"type": "str", "required": False},
                        "default_gateway": {"type": "str", "required": False},
                    },
                },
                "tcp_port": {"type": "int", "required": False},
                "discovery_tcp_port": {"type": "int", "required": False},
                "enable_selective_ack": {"type": "bool", "required": False},
                "enable_delayed_ack": {"type": "bool", "required": False},
                "window_size": {
                    "type": "str",
                    "choices": [
                        "NUMBER_64K",
                        "NUMBER_128K",
                        "NUMBER_256K",
                        "NUMBER_512K",
                        "NUMBER_1024K",
                    ],
                    "required": False,
                },
                "mtu_size": {
                    "type": "str",
                    "choices": ["NUMBER_1500", "NUMBER_4500", "NUMBER_9000"],
                    "required": False,
                },
            },
        },
    }
    return port_args


@dataclass
class VspOnePortFactsSpec(SingleBaseClass):
    """
    This class represents the VSP One port facts specification.
    """

    port_id: str = None
    protocol: str = None

    def __post_init__(self):

        if self.port_id is not None and self.protocol is not None:
            raise ValueError(
                "Only one of 'port_id' or 'protocol' should be provided, not both."
            )

        if self.protocol is not None and self.protocol.lower() not in PROTOCOL_LIST:
            raise ValueError(
                f"Invalid protocol '{self.protocol}'. Valid options are: {PROTOCOL_LIST}"
            )
        self.protocol = PROTOCOL_MAP[self.protocol.lower()] if self.protocol else None


class VspOnePortConst:
    FC = "FC"
    ISCSI = "iSCSI"
    NVME_TCP = "NVME_TCP"
