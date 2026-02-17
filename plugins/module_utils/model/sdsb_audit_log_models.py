from dataclasses import dataclass
from typing import List, Optional

try:
    from .common_base_models import SingleBaseClass
except ImportError:
    from common_base_models import SingleBaseClass


@dataclass
class SyslogServerSpec:
    index: Optional[int] = None
    is_enabled: Optional[bool] = None
    server_name: Optional[str] = None
    port: Optional[int] = None
    transport_protocol: Optional[str] = None


@dataclass
class SyslogForwardingSettingSpec(SingleBaseClass):
    location_name: Optional[str] = None
    syslog_servers: Optional[List[SyslogServerSpec]] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "syslog_servers" in kwargs and kwargs.get("syslog_servers") is not None:
            self.syslog_servers = [
                SyslogServerSpec(**server) if isinstance(server, dict) else server
                for server in kwargs.get("syslog_servers", [])
            ]


@dataclass
class AuditLogSettingsSpec(SingleBaseClass):
    audit_log_file_location: Optional[str] = None
    refresh: Optional[bool] = None
    syslog_forwarding_setting: Optional[SyslogForwardingSettingSpec] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if (
            "syslog_forwarding_setting" in kwargs
            and kwargs.get("syslog_forwarding_setting") is not None
        ):
            self.syslog_forwarding_setting = (
                SyslogForwardingSettingSpec(**kwargs.get("syslog_forwarding_setting"))
                if isinstance(kwargs.get("syslog_forwarding_setting"), dict)
                else kwargs.get("syslog_forwarding_setting")
            )


@dataclass
class SDSBSyslogServerInfo(SingleBaseClass):
    index: int
    isEnabled: bool
    serverName: str
    port: int
    transportProtocol: str

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict


@dataclass
class SDSBSyslogForwardingSettingInfo(SingleBaseClass):
    locationName: str
    syslogServers: List[SDSBSyslogServerInfo]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict


@dataclass
class SDSBAuditLogSettingInfo(SingleBaseClass):
    syslogForwardingSetting: SDSBSyslogForwardingSettingInfo

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict
