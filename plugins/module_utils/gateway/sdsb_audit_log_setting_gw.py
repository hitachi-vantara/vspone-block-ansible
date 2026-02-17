try:
    from .gateway_manager import SDSBConnectionManager
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit, dicts_to_dataclass_list
    from ..model.sdsb_audit_log_models import (
        SDSBAuditLogSettingInfo,
        SDSBSyslogForwardingSettingInfo,
        SDSBSyslogServerInfo,
    )

except ImportError:
    from .gateway_manager import SDSBConnectionManager
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit, dicts_to_dataclass_list
    from model.sdsb_audit_log_models import (
        SDSBAuditLogSettingInfo,
        SDSBSyslogForwardingSettingInfo,
        SDSBSyslogServerInfo,
    )

GET_AUDIT_LOG_SETTING = "v1/objects/audit-log-setting"
DOWNLOAD_AUDITLOG_FILE = "v1/objects/audit-logs/download"
COPY_AUDITLOG_FILE = "v1/objects/audit-logs/actions/create-file/invoke"

logger = Log()


class SDSBAuditLogSettingGateway:

    def __init__(self, connection_info):
        self.connection_manager = SDSBConnectionManager(
            connection_info.address, connection_info.username, connection_info.password
        )

    @log_entry_exit
    def get_audit_log_setting(self):

        end_point = GET_AUDIT_LOG_SETTING
        settings = self.connection_manager.get(end_point)
        logger.writeDebug("GW:get_audit_log_setting:data={}", settings)

        # Convert syslog_servers list to dataclass objects
        syslog_servers_data = settings.get("syslogForwardingSetting", {}).get(
            "syslogServers", []
        )
        syslog_servers = dicts_to_dataclass_list(
            syslog_servers_data, SDSBSyslogServerInfo
        )

        # Create the syslog forwarding setting object
        syslog_forwarding_setting = SDSBSyslogForwardingSettingInfo(
            locationName=settings.get("syslogForwardingSetting", {}).get(
                "locationName", ""
            ),
            syslogServers=syslog_servers,
        )

        # Return the main audit log setting info object
        return SDSBAuditLogSettingInfo(
            syslogForwardingSetting=syslog_forwarding_setting
        )

    @log_entry_exit
    def modify_audit_log_setting(self, setting: SDSBAuditLogSettingInfo):
        logger.writeDebug("GW:modify_audit_log_setting:setting={}", setting)

        end_point = GET_AUDIT_LOG_SETTING
        payload = {
            "syslogForwardingSetting": {
                "locationName": setting.syslogForwardingSetting.locationName,
                "syslogServers": [
                    {
                        "index": server.index,
                        "isEnabled": server.isEnabled,
                        "serverName": server.serverName,
                        "port": server.port,
                        "transportProtocol": server.transportProtocol,
                    }
                    for server in setting.syslogForwardingSetting.syslogServers
                ],
            }
        }
        # Perform the patch operation
        patch_result = self.connection_manager.patch(end_point, payload)
        logger.writeDebug("GW:modify_audit_log_setting:patch_result={}", patch_result)

        # Return the updated settings by getting the current state
        return self.get_audit_log_setting()

    @log_entry_exit
    def download_audit_log_file(self, file_name):
        end_point = DOWNLOAD_AUDITLOG_FILE
        resp = self.connection_manager.download_file(end_point)
        # logger.writeDebug(f"GW:resp={resp}")
        with open(file_name, mode="wb") as file:
            file.write(resp)
        return

    @log_entry_exit
    def create_audit_log_file(self, spec):
        end_point = COPY_AUDITLOG_FILE
        payload = None
        return self.connection_manager.post(end_point, payload)
