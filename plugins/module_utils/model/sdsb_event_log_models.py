from dataclasses import dataclass
from typing import List, Optional

try:
    from .common_base_models import SingleBaseClass
except ImportError:
    from common_base_models import SingleBaseClass


@dataclass
class EventLogFactSpec:
    """Event Log Facts Specification"""

    severity: Optional[str] = None
    severity_ge: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    max_events: Optional[int] = None
    id: Optional[str] = None
    start_time: Optional[str] = None
    end_time: Optional[str] = None
    max_events: Optional[int] = None


@dataclass
class SyslogServerSpec:
    index: Optional[int] = None
    is_enabled: Optional[bool] = None
    server_name: Optional[str] = None
    port: Optional[int] = None
    transport_protocol: Optional[str] = None


@dataclass
class SmtpSettingSpec:
    index: Optional[int] = None
    is_enabled: Optional[bool] = None
    smtp_server_name: Optional[str] = None
    port: Optional[int] = None
    connection_encryption_type: Optional[str] = None
    is_smtp_auth_enabled: Optional[bool] = None
    smtp_auth_account: Optional[str] = None
    smtp_auth_password: Optional[str] = None
    from_address: Optional[str] = None
    to_address1: Optional[str] = None
    to_address2: Optional[str] = None
    to_address3: Optional[str] = None


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
class EmailReportSettingSpec(SingleBaseClass):
    smtp_settings: Optional[List[SmtpSettingSpec]] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "smtp_settings" in kwargs and kwargs.get("smtp_settings") is not None:
            self.smtp_settings = [
                SmtpSettingSpec(**smtp) if isinstance(smtp, dict) else smtp
                for smtp in kwargs.get("smtp_settings", [])
            ]


@dataclass
class SmtpRootCertificateSpec(SingleBaseClass):
    """Specification for SMTP root certificate import/download"""

    certificate_path: Optional[str] = None
    target_smtp_server: Optional[int] = None
    download_location: Optional[str] = None  # For download operations


@dataclass
class EventLogSettingsSpec(SingleBaseClass):
    syslog_forwarding_setting: Optional[SyslogForwardingSettingSpec] = None
    email_report_setting: Optional[EmailReportSettingSpec] = None
    smtp_root_certificate: Optional[SmtpRootCertificateSpec] = None

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
        if (
            "email_report_setting" in kwargs
            and kwargs.get("email_report_setting") is not None
        ):
            self.email_report_setting = (
                EmailReportSettingSpec(**kwargs.get("email_report_setting"))
                if isinstance(kwargs.get("email_report_setting"), dict)
                else kwargs.get("email_report_setting")
            )
        if (
            "smtp_root_certificate" in kwargs
            and kwargs.get("smtp_root_certificate") is not None
        ):
            self.smtp_root_certificate = (
                SmtpRootCertificateSpec(**kwargs.get("smtp_root_certificate"))
                if isinstance(kwargs.get("smtp_root_certificate"), dict)
                else kwargs.get("smtp_root_certificate")
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
class SDSBSmtpSettingInfo(SingleBaseClass):
    index: int
    isEnabled: bool
    smtpAuthAccount: str
    fromAddress: str
    toAddress1: str
    toAddress2: str
    toAddress3: str
    port: Optional[int] = None
    connectionEncryptionType: Optional[str] = None
    isSmtpAuthEnabled: Optional[bool] = None
    smtpServerName: Optional[str] = None
    smtpAuthPassword: Optional[str] = None

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict


@dataclass
class SDSBSyslogForwardingSettingInfo(SingleBaseClass):
    locationName: str
    syslogServers: List[SDSBSyslogServerInfo]

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict


@dataclass
class SDSBEmailReportSettingInfo(SingleBaseClass):
    smtpSettings: List[SDSBSmtpSettingInfo]

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict


@dataclass
class SDSBEventLogSettingInfo(SingleBaseClass):
    syslogForwardingSetting: SDSBSyslogForwardingSettingInfo
    emailReportSetting: Optional[SDSBEmailReportSettingInfo] = None

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict
