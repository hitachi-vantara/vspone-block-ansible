try:
    from .gateway_manager import SDSBConnectionManager
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..model.sdsb_user_models import UserAuthSetting
except ImportError:
    from .gateway_manager import SDSBConnectionManager
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from model.sdsb_user_models import UserAuthSetting


GET_USER_AUTH_SETTING = "v1/objects/user-auth-setting"
UPDATE_USER_AUTH_SETTING = "v1/objects/user-auth-setting"

logger = Log()


class SDSBUserAuthSettingGateway:

    def __init__(self, connection_info):
        self.connection_manager = SDSBConnectionManager(
            connection_info.address, connection_info.username, connection_info.password
        )

    @log_entry_exit
    def get_user_auth_setting(self):
        end_point = GET_USER_AUTH_SETTING
        user_auth_setting = self.connection_manager.get(end_point)
        logger.writeDebug("GW:get_user_auth_setting:data={}", user_auth_setting)

        return UserAuthSetting(**user_auth_setting)

    @log_entry_exit
    def update_user_auth_settings(self, patch_user_auth_setting_param):
        end_point = UPDATE_USER_AUTH_SETTING
        update_response = self.connection_manager.patch(
            end_point, data=patch_user_auth_setting_param
        )
        logger.writeDebug("GW:update_user_auth_settings:data={}", update_response)

        return UserAuthSetting(**update_response)
