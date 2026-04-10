try:
    from ..provisioner.sdsb_user_auth_setting_provisioner import (
        SDSBUserAuthSettingProvisioner,
    )
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..common.hv_constants import StateValue
    from ..message.sdsb_user_auth_setting_msgs import SDSBUserAuthSettingMsg
except ImportError:
    from provisioner.sdsb_user_auth_setting_provisioner import (
        SDSBUserAuthSettingProvisioner,
    )
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from common.hv_constants import StateValue
    from message.sdsb_user_auth_setting_msgs import SDSBUserAuthSettingMsg


logger = Log()


class SDSBUserAuthSettingReconciler:

    def __init__(self, connection_info):
        self.connection_info = connection_info
        self.provisioner = SDSBUserAuthSettingProvisioner(self.connection_info)

    @log_entry_exit
    def get_user_auth_setting(self):
        return self.provisioner.get_user_auth_setting()

    @log_entry_exit
    def reconcile_user_auth_settings(self, spec=None, state=None):
        logger.writeDebug(
            f"RECONCILER:reconcile_user_auth_settings:spec= {spec}, state= {state}"
        )
        if state == StateValue.PRESENT:
            return self.update_user_auth_settings(spec)
        else:
            raise ValueError(SDSBUserAuthSettingMsg.UNSUPPORTED_STATE.value).format(
                state
            )

    @log_entry_exit
    def update_user_auth_settings(self, spec):
        if spec.is_empty():
            raise ValueError(SDSBUserAuthSettingMsg.NO_USER_AUTH_SETTINGS.value)
        current_user_auth_settings = self.get_user_auth_setting()
        if current_user_auth_settings is not None:
            if self.is_user_auth_setting_update_reuired(
                current_user_auth_settings, spec
            ):
                return self.provisioner.update_user_auth_settings(spec)
            else:
                return current_user_auth_settings
        else:
            raise ValueError(SDSBUserAuthSettingMsg.USER_AUTH_SETTING_NOT_FOUND.value)

    @log_entry_exit
    def is_user_auth_setting_update_reuired(self, current_user_auth_settings, spec):
        logger.writeDebug(
            f"RECONCILER:is_user_auth_setting_update_reuired:current_user_auth_settings= {current_user_auth_settings}, spec= {spec}"
        )

        changed = False

        if spec.password_age_setting is not None:
            current_password_age_setting = current_user_auth_settings.get(
                "password_age_setting", {}
            )
            if (
                spec.password_age_setting.requires_initial_password_reset is not None
                and spec.password_age_setting.requires_initial_password_reset
                != current_password_age_setting.get("requires_initial_password_reset")
            ):
                changed = True
            if (
                spec.password_age_setting.min_age_days is not None
                and spec.password_age_setting.min_age_days
                != current_password_age_setting.get("min_age_days")
            ):
                changed = True
            if (
                spec.password_age_setting.max_age_days is not None
                and spec.password_age_setting.max_age_days
                != current_password_age_setting.get("max_age_days")
            ):
                changed = True

        if spec.password_complexity_setting is not None:
            current_password_complexity_setting = current_user_auth_settings.get(
                "password_complexity_setting", {}
            )
            if (
                spec.password_complexity_setting.min_length is not None
                and spec.password_complexity_setting.min_length
                != current_password_complexity_setting.get("min_length")
            ):
                changed = True
            if (
                spec.password_complexity_setting.min_number_of_upper_case_chars
                is not None
                and spec.password_complexity_setting.min_number_of_upper_case_chars
                != current_password_complexity_setting.get(
                    "min_number_of_upper_case_chars"
                )
            ):
                changed = True
            if (
                spec.password_complexity_setting.min_number_of_lower_case_chars
                is not None
                and spec.password_complexity_setting.min_number_of_lower_case_chars
                != current_password_complexity_setting.get(
                    "min_number_of_lower_case_chars"
                )
            ):
                changed = True
            if (
                spec.password_complexity_setting.min_number_of_numerals is not None
                and spec.password_complexity_setting.min_number_of_numerals
                != current_password_complexity_setting.get("min_number_of_numerals")
            ):
                changed = True
            if (
                spec.password_complexity_setting.min_number_of_symbols is not None
                and spec.password_complexity_setting.min_number_of_symbols
                != current_password_complexity_setting.get("min_number_of_symbols")
            ):
                changed = True
            if (
                spec.password_complexity_setting.number_of_password_history is not None
                and spec.password_complexity_setting.number_of_password_history
                != current_password_complexity_setting.get("number_of_password_history")
            ):
                changed = True

        if spec.lockout_setting is not None:
            current_lockout_setting = current_user_auth_settings.get(
                "lockout_setting", {}
            )
            if (
                spec.lockout_setting.max_attempts is not None
                and spec.lockout_setting.max_attempts
                != current_lockout_setting.get("max_attempts")
            ):
                changed = True
            if (
                spec.lockout_setting.lockout_seconds is not None
                and spec.lockout_setting.lockout_seconds
                != current_lockout_setting.get("lockout_seconds")
            ):
                changed = True

        if spec.session_setting is not None:
            current_session_setting = current_user_auth_settings.get(
                "session_setting", {}
            )
            if (
                spec.session_setting.max_lifetime_seconds is not None
                and spec.session_setting.max_lifetime_seconds
                != current_session_setting.get("max_lifetime_seconds")
            ):
                changed = True
            if (
                spec.session_setting.max_idle_seconds is not None
                and spec.session_setting.max_idle_seconds
                != current_session_setting.get("max_idle_seconds")
            ):
                changed = True
        return changed
