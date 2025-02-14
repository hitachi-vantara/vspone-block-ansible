try:
    from ..common.uaig_constants import Endpoints
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from .gateway_manager import UAIGConnectionManager
    from ..common.hv_constants import GatewayConstant
except ImportError:
    from common.uaig_constants import Endpoints
    from common.hv_constants import GatewayConstant
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from .gateway_manager import UAIGConnectionManager


class PasswordUAIGateway:

    def __init__(self, connection_info):
        funcName = "PasswordUAIGateway: init"
        self.logger = Log()
        self.logger.writeEnterSDK(funcName)

        self.connectionManager = UAIGConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )

    @log_entry_exit
    def gateway_password(self, password, user):
        funcName = "PasswordUAIGateway: gateway_password"
        self.logger.writeEnterSDK(funcName)
        request = {}

        request["username"] = user["username"]
        request["password"] = password
        request["firstName"] = user.get("firstName", "")
        request["lastName"] = user.get("lastName", "")

        body = request
        end_point = Endpoints.UPDATE_PASSWORD.format(id=user["id"])
        try:
            data = self.connectionManager.update(end_point, body)
            self.logger.writeDebug("{} Response={}", funcName, data)
            self.logger.writeExitSDK(funcName)
            return data
        except (ValueError, TypeError):
            return "Failed to update admin password"

    @log_entry_exit
    def get_admin_user(self):
        end_point = Endpoints.GET_USERS
        try:
            user_data = self.connectionManager.get(end_point)
            self.logger.writeDebug("Response={}", user_data)
            self.logger.writeDebug("GW:get_admin_user:user_data={}", user_data)
            users = user_data["data"].get("users")
            for user in users:
                if user["username"] == GatewayConstant.ADMIN_USER_NAME:
                    return user
        except (ValueError, TypeError):
            return "Failed to get admin user"
        return {}
