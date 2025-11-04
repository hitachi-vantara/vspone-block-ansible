import re

try:
    from ..common.sdsb_constants import SDSBlockEndpoints
    from .gateway_manager import SDSBConnectionManager
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..common.sdsb_utils import convert_keys_to_snake_case

except ImportError:
    from common.sdsb_constants import SDSBlockEndpoints
    from .gateway_manager import SDSBConnectionManager
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from common.sdsb_utils import convert_keys_to_snake_case

logger = Log()

PASSWORD_REGEX = re.compile(
    r"^[-A-Za-z0-9!#\$%&\"'\(\)\*\+,\.\/:;<>=\?@\[\]\\\^_`\{\}\|~]{1,256}$"
)


class SDSBBlockUsersDirectGateway:

    def __init__(self, connection_info):
        self.connection_manager = SDSBConnectionManager(
            connection_info.address, connection_info.username, connection_info.password
        )

    @log_entry_exit
    def get_users(self, spec=None):

        end_point = SDSBlockEndpoints.GET_USERS

        if spec is not None:
            if spec.id:
                end_point = SDSBlockEndpoints.GET_USERS_BY_ID.format(spec.id)
                logger.writeDebug("GW:get_users:end_point={}", end_point)
            elif spec.user_id:
                end_point = SDSBlockEndpoints.GET_USERS_BY_ID.format(spec.user_id)
                logger.writeDebug("GW:get_users:end_point={}", end_point)

        try:
            users = self.connection_manager.get(end_point)
            logger.writeDebug("GW:get_users:data={}", users)
        except Exception as e:
            logger.writeError("GW:get_users:Exception={}", str(e))
            return None

        converted = convert_keys_to_snake_case(users)
        return converted

    @log_entry_exit
    def create_user(self, spec=None):

        end_point = SDSBlockEndpoints.GET_USERS
        payload = {}

        # Validate user ID length
        if len(spec.user_id) < 6 or len(spec.user_id) > 28:
            raise ValueError("User ID must be between 6 and 28 characters long.")

        payload["userId"] = spec.user_id
        if not PASSWORD_REGEX.fullmatch(spec.password):
            raise ValueError("Password does not meet complexity requirements.")
        payload["password"] = spec.password
        if spec.authentication:
            payload["authentication"] = spec.authentication
        else:
            payload["authentication"] = "local"
        if spec.user_group_ids:
            payload["userGroupIds"] = spec.user_group_ids
        if spec.is_enabled_console_login is not None:
            payload["isEnabledConsoleLogin"] = spec.is_enabled_console_login

        response = self.connection_manager.post(end_point, payload)
        logger.writeDebug("GW:create_user:response={}", response)
        user = self.get_users(spec)
        logger.writeDebug("GW:create_user:user={}", user)
        return user

    @log_entry_exit
    def update_user(self, spec=None):

        end_point = SDSBlockEndpoints.GET_USERS_BY_ID.format(spec.user_id) + "/password"
        payload = {}
        payload["currentPassword"] = spec.current_password
        if not PASSWORD_REGEX.fullmatch(spec.new_password):
            raise ValueError("New password does not meet complexity requirements.")
        if spec.new_password == spec.current_password:
            raise ValueError(
                "New password must be different from the current password."
            )
        if len(spec.new_password) < 8:
            raise ValueError("New password must be at least 8 characters long.")
        if len(spec.new_password) > 256:
            raise ValueError("New password must not exceed 256 characters.")
        payload["newPassword"] = spec.new_password

        response = self.connection_manager.patch(end_point, payload)
        logger.writeDebug("GW:update_user:response={}", response)

        # Update connection manager password
        self.connection_manager.password = spec.new_password

        user = self.get_users(spec)
        logger.writeDebug("GW:update_user:user={}", user)
        return user
