from dataclasses import dataclass
from typing import Optional
from .common_base_models import SingleBaseClass


@dataclass
class LdapSettingSpec:
    mapping_mode: Optional[str] = None
    primary_ldap_server_url: Optional[str] = None
    secondary_ldap_server_url: Optional[str] = None
    is_start_tls_enabled: Optional[bool] = None
    base_dn: Optional[str] = None
    bind_dn: Optional[str] = None
    bind_dn_password: Optional[str] = None
    user_id_attribute: Optional[str] = None
    user_tree_dn: Optional[str] = None
    user_object_class: Optional[str] = None
    external_group_name_attribute: Optional[str] = None
    user_group_tree_dn: Optional[str] = None
    user_group_object_class: Optional[str] = None
    timeout_seconds: Optional[int] = None
    retry_interval_milliseconds: Optional[int] = None
    max_retries: Optional[int] = None


@dataclass
class SDSBExternalAuthServerSettingSpec(SingleBaseClass):
    is_enabled: Optional[bool] = None
    auth_protocol: Optional[str] = None
    ldap_setting: Optional[dict] = None
    download_location: Optional[str] = None
    target_server: Optional[str] = None
    root_certificate_file_path: Optional[str] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "ldap_setting" in kwargs and kwargs["ldap_setting"] is not None:
            self.ldap_setting = LdapSettingSpec(**kwargs["ldap_setting"])


@dataclass
class LdapSettingOfExternalAuthServerSetting(SingleBaseClass):
    mappingMode: Optional[str] = None
    primaryLdapServerUrl: Optional[str] = None
    secondaryLdapServerUrl: Optional[str] = None
    isStartTlsEnabled: Optional[bool] = None
    baseDn: Optional[str] = None
    bindDn: Optional[str] = None
    userIdAttribute: Optional[str] = None
    userTreeDn: Optional[str] = None
    userObjectClass: Optional[str] = None
    externalGroupNameAttribute: Optional[str] = None
    userGroupTreeDn: Optional[str] = None
    userGroupObjectClass: Optional[str] = None
    timeoutSeconds: Optional[int] = None
    retryIntervalMilliseconds: Optional[int] = None
    maxRetries: Optional[int] = None

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict


@dataclass
class ExternalAuthServerSetting(SingleBaseClass):
    isEnabled: Optional[bool] = None
    authProtocol: Optional[str] = None
    ldapSetting: Optional[LdapSettingOfExternalAuthServerSetting] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "ldapSetting" in kwargs:
            self.ldapSetting = LdapSettingOfExternalAuthServerSetting(
                **kwargs["ldapSetting"]
            )

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict


@dataclass
class LdapServerConnectionVerificationResult(SingleBaseClass):
    numberOfExternalUsers: Optional[int] = None
    numberOfExternalUserGroups: Optional[int] = None

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict


@dataclass
class LdapServerConnectionVerificationError(SingleBaseClass):
    code: Optional[int] = None
    message: Optional[str] = None

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict


@dataclass
class ResultOfLdapServerConnectionVerification(SingleBaseClass):
    primaryServer: Optional[LdapServerConnectionVerificationResult] = None
    secondaryServer: Optional[LdapServerConnectionVerificationResult] = None

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict


@dataclass
class ErrorInformationOfLdapServerConnectionVerification(SingleBaseClass):
    primaryServer: Optional[LdapServerConnectionVerificationError] = None
    secondaryServer: Optional[LdapServerConnectionVerificationError] = None

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict


@dataclass
class LdapServerConnectionVerification(SingleBaseClass):
    result: Optional[ResultOfLdapServerConnectionVerification] = None
    error: Optional[ErrorInformationOfLdapServerConnectionVerification] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "result" in kwargs:
            self.result = ResultOfLdapServerConnectionVerification(**kwargs["result"])
        if "error" in kwargs:
            self.error = ErrorInformationOfLdapServerConnectionVerification(
                **kwargs["error"]
            )

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict


@dataclass
class ExternalAuthServerConnectionVerification(SingleBaseClass):
    authProtocol: Optional[str] = None
    ldap: Optional[LdapServerConnectionVerification] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "ldap" in kwargs:
            self.ldap = LdapServerConnectionVerification(**kwargs["ldap"])

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict
