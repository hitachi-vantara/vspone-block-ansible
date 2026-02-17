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


class SDSBEventLogSettingProvisioner:

    def __init__(self, connection_info):

        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.SDSB_EVENT_LOG_SETTING
        )

    @log_entry_exit
    def get_event_log_setting(self):
        event_log_settings = self.gateway.get_event_log_setting()
        result = event_log_settings
        return result

    @log_entry_exit
    def modify_event_log_setting(self, setting):
        result = self.gateway.modify_event_log_setting(setting)
        return result

    @log_entry_exit
    def modify_event_log_setting_syslog(self, syslog_setting):
        result = self.gateway.modify_event_log_setting_syslog(syslog_setting)
        return result

    @log_entry_exit
    def modify_event_log_setting_email(self, email_setting):
        result = self.gateway.modify_event_log_setting_email(email_setting)
        return result

    @log_entry_exit
    def import_smtp_root_certificate(self, certificate_path, target_smtp_server=1):
        """
        Import SMTP server root certificate.

        Args:
            certificate_path: Path to the certificate file
            target_smtp_server: SMTP server index (default: 1)

        Returns:
            Response from the API
        """
        result = self.gateway.import_smtp_root_certificate(
            certificate_path, target_smtp_server
        )
        return result

    @log_entry_exit
    def download_smtp_root_certificate(self, file_name, target_smtp_server=1):
        """
        Download SMTP server root certificate.

        Args:
            file_name: Path where the certificate will be saved
            target_smtp_server: SMTP server index (default: 1)

        Returns:
            None (writes to file)
        """
        result = self.gateway.download_smtp_root_certificate(
            file_name, target_smtp_server
        )
        return result
