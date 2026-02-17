from dataclasses import dataclass
from typing import Optional, List
from .common_base_models import BaseDataClass, SingleBaseClass


@dataclass
class SDSBUserSpec:

    id: Optional[str] = None
    name: Optional[str] = None
    user_id: Optional[str] = None
    password: Optional[str] = None
    user_group_ids: list[str] = None
    authentication: Optional[str] = None
    is_enabled_console_login: Optional[bool] = None
    new_password: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None
    comments: Optional[str] = None
    user_group_ids: Optional[List[str]] = None
    is_enabled: Optional[bool] = None
    vps_id: Optional[str] = None
    vps_name: Optional[str] = None


@dataclass
class SDSBUserFactSpec:
    id: Optional[str] = None
    vps_name: Optional[str] = None
    vps_id: Optional[str] = None


@dataclass
class UserGroup(SingleBaseClass):
    userGroupId: Optional[str] = None
    userGroupObjectId: Optional[str] = None


@dataclass
class UserPrivileges(SingleBaseClass):
    scope: Optional[str] = None
    roleNames: Optional[List[str]] = None


@dataclass
class SdsbUserResponse(SingleBaseClass):
    userId: Optional[str] = None
    userObjectId: Optional[str] = None
    passwordExpirationTime: Optional[str] = None
    isEnabled: Optional[bool] = None
    userGroups: Optional[List[UserGroup]] = None
    isBuiltIn: Optional[bool] = None
    authentication: Optional[str] = None
    roleNames: Optional[List[str]] = None
    isEnabledConsoleLogin: Optional[bool] = None
    vpsId: Optional[str] = None
    privileges: Optional[List[UserPrivileges]] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "userGroups" in kwargs:
            self.userGroups = [UserGroup(**user_gp) for user_gp in self.userGroups]
        if "privileges" in kwargs:
            self.privileges = [
                UserPrivileges(**user_priv) for user_priv in self.privileges
            ]

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict


@dataclass
class SdsbUserList(BaseDataClass):
    data: List[SdsbUserResponse] = None


@dataclass
class PasswordComplexitySettingOfUserAuthSetting(SingleBaseClass):
    minLength: Optional[int] = None
    minNumberOfUpperCaseChars: Optional[int] = None
    minNumberOfLowerCaseChars: Optional[int] = None
    minNumberOfNumerals: Optional[int] = None
    minNumberOfSymbols: Optional[int] = None
    numberOfPasswordHistory: Optional[int] = None

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict


@dataclass
class PasswordAgeSettingOfUserAuthSetting(SingleBaseClass):
    requiresInitialPasswordReset: Optional[bool] = None
    minAgeDays: Optional[int] = None
    maxAgeDays: Optional[int] = None

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict


@dataclass
class LockoutSetting(SingleBaseClass):
    maxAttempts: Optional[int] = None
    lockoutSeconds: Optional[int] = None

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict


@dataclass
class SessionSettingOfUserAuthSetting(SingleBaseClass):
    maxLifetimeSeconds: Optional[int] = None
    maxIdleSeconds: Optional[int] = None

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict


@dataclass
class UserAuthSetting(SingleBaseClass):
    passwordComplexitySetting: Optional[PasswordComplexitySettingOfUserAuthSetting] = (
        None
    )
    passwordAgeSetting: Optional[PasswordAgeSettingOfUserAuthSetting] = None
    lockoutSetting: Optional[LockoutSetting] = None
    sessionSetting: Optional[SessionSettingOfUserAuthSetting] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "passwordComplexitySetting" in kwargs:
            self.passwordComplexitySetting = PasswordComplexitySettingOfUserAuthSetting(
                **kwargs["passwordComplexitySetting"]
            )
        if "passwordAgeSetting" in kwargs:
            self.passwordAgeSetting = PasswordAgeSettingOfUserAuthSetting(
                **kwargs["passwordAgeSetting"]
            )
        if "lockoutSetting" in kwargs:
            self.lockoutSetting = LockoutSetting(**kwargs["lockoutSetting"])
        if "sessionSetting" in kwargs:
            self.sessionSetting = SessionSettingOfUserAuthSetting(
                **kwargs["sessionSetting"]
            )

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict


@dataclass
class PasswordAgeSettingSpec:
    requires_initial_password_reset: Optional[bool] = None
    min_age_days: Optional[int] = None
    max_age_days: Optional[int] = None


@dataclass
class PasswordComplexitySettingSpec:
    min_length: Optional[int] = None
    min_number_of_upper_case_chars: Optional[int] = None
    min_number_of_lower_case_chars: Optional[int] = None
    min_number_of_numerals: Optional[int] = None
    min_number_of_symbols: Optional[int] = None
    number_of_password_history: Optional[int] = None


@dataclass
class LockoutSettingSpec:
    max_attempts: Optional[int] = None
    lockout_seconds: Optional[int] = None


@dataclass
class SessionSettingSpec:
    max_lifetime_seconds: Optional[int] = None
    max_idle_seconds: Optional[int] = None


@dataclass
class UserAuthSettingSpec:
    password_age_setting: Optional[PasswordAgeSettingSpec] = None
    password_complexity_setting: Optional[PasswordComplexitySettingSpec] = None
    lockout_setting: Optional[LockoutSettingSpec] = None
    session_setting: Optional[SessionSettingSpec] = None

    def __init__(self, **kwargs):
        if (
            "password_age_setting" in kwargs
            and kwargs["password_age_setting"] is not None
        ):
            self.password_age_setting = PasswordAgeSettingSpec(
                **kwargs["password_age_setting"]
            )
        if (
            "password_complexity_setting" in kwargs
            and kwargs["password_complexity_setting"] is not None
        ):
            self.password_complexity_setting = PasswordComplexitySettingSpec(
                **kwargs["password_complexity_setting"]
            )
        if "lockout_setting" in kwargs and kwargs["lockout_setting"] is not None:
            self.lockout_setting = LockoutSettingSpec(**kwargs["lockout_setting"])
        if "session_setting" in kwargs and kwargs["session_setting"] is not None:
            self.session_setting = SessionSettingSpec(**kwargs["session_setting"])

    def is_empty(self):
        return (
            self.password_age_setting is None
            and self.password_complexity_setting is None
            and self.lockout_setting is None
            and self.session_setting is None
        )
