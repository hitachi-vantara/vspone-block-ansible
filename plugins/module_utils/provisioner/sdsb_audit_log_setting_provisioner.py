try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes
    from ..common.ansible_common import log_entry_exit
    from ..common.hv_log import Log

except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes
    from common.ansible_common import log_entry_exit
    from common.hv_log import Log

logger = Log()


class SDSBAuditLogSettingProvisioner:

    def __init__(self, connection_info):

        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.SDSB_AUDIT_LOG_SETTING
        )

    @log_entry_exit
    def get_audit_log_setting(self):
        audit_log_settings = self.gateway.get_audit_log_setting()
        result = audit_log_settings
        return result

    @log_entry_exit
    def modify_audit_log_setting(self, setting):
        result = self.gateway.modify_audit_log_setting(setting)
        return result

    @log_entry_exit
    def download_audit_log_file(self, file_name):
        result = self.gateway.download_audit_log_file(file_name)
        return result

    @log_entry_exit
    def create_audit_log_file(self, spec):
        result = self.gateway.create_audit_log_file(spec)
        return result
