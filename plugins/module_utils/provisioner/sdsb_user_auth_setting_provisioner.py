try:
    from ..gateway.sdsb_user_auth_setting_gateway import (
        SDSBUserAuthSettingGateway,
    )
    from ..common.ansible_common import log_entry_exit
    from ..common.hv_log import Log
except ImportError:
    from gateway.sdsb_user_auth_setting_gateway import SDSBUserAuthSettingGateway
    from common.ansible_common import log_entry_exit
    from common.hv_log import Log

logger = Log()


class SDSBUserAuthSettingProvisioner:

    def __init__(self, connection_info):
        self.connection_info = connection_info
        self.gateway = SDSBUserAuthSettingGateway(connection_info)

    @log_entry_exit
    def get_user_auth_setting(self):
        response = self.gateway.get_user_auth_setting()
        return response.camel_to_snake_dict()

    @log_entry_exit
    def update_user_auth_settings(self, spec):
        patch_param = {}

        if spec.password_complexity_setting is not None:
            password_complexity_setting = {}
            if spec.password_complexity_setting.min_length is not None:
                password_complexity_setting["minLength"] = (
                    spec.password_complexity_setting.min_length
                )
            if (
                spec.password_complexity_setting.min_number_of_upper_case_chars
                is not None
            ):
                password_complexity_setting["minNumberOfUpperCaseChars"] = (
                    spec.password_complexity_setting.min_number_of_upper_case_chars
                )
            if (
                spec.password_complexity_setting.min_number_of_lower_case_chars
                is not None
            ):
                password_complexity_setting["minNumberOfLowerCaseChars"] = (
                    spec.password_complexity_setting.min_number_of_lower_case_chars
                )
            if spec.password_complexity_setting.min_number_of_numerals is not None:
                password_complexity_setting["minNumberOfNumerals"] = (
                    spec.password_complexity_setting.min_number_of_numerals
                )
            if spec.password_complexity_setting.min_number_of_symbols is not None:
                password_complexity_setting["minNumberOfSymbols"] = (
                    spec.password_complexity_setting.min_number_of_symbols
                )
            if spec.password_complexity_setting.number_of_password_history is not None:
                password_complexity_setting["numberOfPasswordHistory"] = (
                    spec.password_complexity_setting.number_of_password_history
                )
            patch_param["passwordComplexitySetting"] = password_complexity_setting

        if spec.password_age_setting is not None:
            password_age_setting = {}
            if spec.password_age_setting.requires_initial_password_reset is not None:
                password_age_setting["requiresInitialPasswordReset"] = (
                    spec.password_age_setting.requires_initial_password_reset
                )
            if spec.password_age_setting.min_age_days is not None:
                password_age_setting["minAgeDays"] = (
                    spec.password_age_setting.min_age_days
                )
            if spec.password_age_setting.max_age_days is not None:
                password_age_setting["maxAgeDays"] = (
                    spec.password_age_setting.max_age_days
                )
            patch_param["passwordAgeSetting"] = password_age_setting

        if spec.lockout_setting is not None:
            lockout_setting = {}
            if spec.lockout_setting.max_attempts is not None:
                lockout_setting["maxAttempts"] = spec.lockout_setting.max_attempts
            if spec.lockout_setting.lockout_seconds is not None:
                lockout_setting["lockoutSeconds"] = spec.lockout_setting.lockout_seconds
            patch_param["lockoutSetting"] = lockout_setting

        if spec.session_setting is not None:
            session_setting = {}
            if spec.session_setting.max_lifetime_seconds is not None:
                session_setting["maxLifetimeSeconds"] = (
                    spec.session_setting.max_lifetime_seconds
                )
            if spec.session_setting.max_idle_seconds is not None:
                session_setting["maxIdleSeconds"] = (
                    spec.session_setting.max_idle_seconds
                )
            patch_param["sessionSetting"] = session_setting

        response = self.gateway.update_user_auth_settings(patch_param)
        logger.writeDebug(f"PROVISIONER:update_user_auth_settings:response= {response}")
        ret_value = response.camel_to_snake_dict()
        self.connection_info.changed = True
        logger.writeDebug(
            f"PROVISIONER:update_user_auth_settings:ret_value= {ret_value}"
        )
        return ret_value
