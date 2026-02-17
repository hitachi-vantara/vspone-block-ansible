try:
    from ..common.hv_api_constants import API
    from .gateway_manager import SDSBConnectionManager
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit, dicts_to_dataclass_list
    from ..model.sdsb_event_log_models import (
        SDSBEventLogSettingInfo,
        SDSBSyslogForwardingSettingInfo,
        SDSBSyslogServerInfo,
        SDSBEmailReportSettingInfo,
        SDSBSmtpSettingInfo,
    )

except ImportError:
    from common.hv_api_constants import API
    from .gateway_manager import SDSBConnectionManager
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit, dicts_to_dataclass_list
    from model.sdsb_event_log_models import (
        SDSBEventLogSettingInfo,
        SDSBSyslogForwardingSettingInfo,
        SDSBSyslogServerInfo,
        SDSBEmailReportSettingInfo,
        SDSBSmtpSettingInfo,
    )

GET_EVENT_LOG_SETTING = "v1/objects/event-log-setting"

logger = Log()


class SDSBEventLogSettingGateway:

    def __init__(self, connection_info):
        self.connection_manager = SDSBConnectionManager(
            connection_info.address, connection_info.username, connection_info.password
        )

    @log_entry_exit
    def get_event_log_setting(self):

        end_point = GET_EVENT_LOG_SETTING
        settings = self.connection_manager.get(end_point)
        logger.writeDebug("GW:get_event_log_setting:data={}", settings)

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

        # Convert smtp_settings list to dataclass objects
        email_report_setting = None
        if "emailReportSetting" in settings:
            smtp_settings_data = settings.get("emailReportSetting", {}).get(
                "smtpSettings", []
            )
            smtp_settings = dicts_to_dataclass_list(
                smtp_settings_data, SDSBSmtpSettingInfo
            )

            # Create the email report setting object
            email_report_setting = SDSBEmailReportSettingInfo(
                smtpSettings=smtp_settings
            )

        # Return the main event log setting info object
        return SDSBEventLogSettingInfo(
            syslogForwardingSetting=syslog_forwarding_setting,
            emailReportSetting=email_report_setting,
        )

    @log_entry_exit
    def modify_event_log_setting_syslog(
        self, syslog_setting: SDSBSyslogForwardingSettingInfo
    ):
        """
        Modify syslog forwarding settings only.
        Note: Either syslogForwardingSetting or emailReportSetting must be specified, but not both.
        """
        logger.writeDebug(
            "GW:modify_event_log_setting_syslog:setting={}", syslog_setting
        )

        end_point = GET_EVENT_LOG_SETTING
        payload = {
            "syslogForwardingSetting": {
                "locationName": syslog_setting.locationName,
                "syslogServers": [
                    {
                        "index": server.index,
                        "isEnabled": server.isEnabled,
                        "serverName": server.serverName,
                        "port": server.port,
                        "transportProtocol": server.transportProtocol,
                    }
                    for server in syslog_setting.syslogServers
                ],
            }
        }

        # Perform the patch operation
        patch_result = self.connection_manager.patch(end_point, payload)
        logger.writeDebug(
            "GW:modify_event_log_setting_syslog:patch_result={}", patch_result
        )

        # Return the updated settings by getting the current state
        return self.get_event_log_setting()

    @log_entry_exit
    def modify_event_log_setting_email(self, email_setting: SDSBEmailReportSettingInfo):
        """
        Modify email report settings only.
        Note: Either syslogForwardingSetting or emailReportSetting must be specified, but not both.
        """
        logger.writeDebug("GW:modify_event_log_setting_email:setting={}", email_setting)

        end_point = GET_EVENT_LOG_SETTING
        smtp_settings_list = []

        for smtp in email_setting.smtpSettings:
            smtp_dict = {
                "index": smtp.index,
                "isEnabled": smtp.isEnabled,
            }

            # Add optional fields only if they have values
            if smtp.smtpServerName is not None:
                smtp_dict["smtpServerName"] = smtp.smtpServerName
            if smtp.smtpAuthAccount:
                smtp_dict["smtpAuthAccount"] = smtp.smtpAuthAccount
            if smtp.smtpAuthPassword is not None:
                smtp_dict["smtpAuthPassword"] = smtp.smtpAuthPassword
            if smtp.fromAddress:
                smtp_dict["fromAddress"] = smtp.fromAddress
            if smtp.toAddress1:
                smtp_dict["toAddress1"] = smtp.toAddress1
            if smtp.toAddress2:
                smtp_dict["toAddress2"] = smtp.toAddress2
            if smtp.toAddress3 is not None:
                smtp_dict["toAddress3"] = smtp.toAddress3

            smtp_settings_list.append(smtp_dict)

        payload = {"emailReportSetting": {"smtpSettings": smtp_settings_list}}

        logger.writeDebug("GW:modify_event_log_setting_email:payload={}", payload)

        # Perform the patch operation
        patch_result = self.connection_manager.patch(end_point, payload)
        logger.writeDebug(
            "GW:modify_event_log_setting_email:patch_result={}", patch_result
        )

        # Return the updated settings by getting the current state
        return self.get_event_log_setting()

    @log_entry_exit
    def modify_event_log_setting(self, setting: SDSBEventLogSettingInfo):
        """
        Modify event log settings. Routes to appropriate method based on what's being modified.
        Note: API requires either syslogForwardingSetting or emailReportSetting, but not both.
        """
        logger.writeDebug("GW:modify_event_log_setting:setting={}", setting)

        # Validate that only one setting type is provided
        has_syslog = setting.syslogForwardingSetting is not None
        has_email = setting.emailReportSetting is not None

        if has_syslog and has_email:
            raise ValueError(
                "Cannot modify both syslogForwardingSetting and emailReportSetting simultaneously. Modify them separately."
            )

        if not has_syslog and not has_email:
            raise ValueError(
                "Either syslogForwardingSetting or emailReportSetting must be specified."
            )

        # Route to appropriate method
        if has_syslog:
            return self.modify_event_log_setting_syslog(setting.syslogForwardingSetting)
        else:
            return self.modify_event_log_setting_email(setting.emailReportSetting)

    @log_entry_exit
    def import_smtp_root_certificate(self, certificate_path, index=1):
        """
        Import SMTP server root certificate.

        Args:
            certificate_path: Path to the certificate file to import
            index: SMTP server index (default: 1)

        Returns:
            Response from the API
        """
        logger.writeDebug(
            "GW:import_smtp_root_certificate:certificate_path={}, index={}",
            certificate_path,
            index,
        )

        end_point = (
            f"v1/objects/smtp-server-root-certificates/{index}/actions/import/invoke"
        )

        # Build multipart form data for the certificate file
        import os

        boundary = self.connection_manager.boundary
        body = bytearray()

        # Read certificate file
        with open(certificate_path, "rb") as cert_file:
            cert_content = cert_file.read()

        # Build multipart body
        filename = os.path.basename(certificate_path)
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(
            f'Content-Disposition: form-data; name="rootCertificate"; filename="{filename}"\r\n'.encode(
                "utf-8"
            )
        )
        body.extend(b"Content-Type: application/octet-stream\r\n\r\n")
        body.extend(cert_content)
        body.extend(b"\r\n")
        body.extend(f"--{boundary}--\r\n".encode("utf-8"))

        # Headers
        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Expect": "",  # Suppress "Expect: 100-continue"
        }

        logger.writeDebug("GW:import_smtp_root_certificate:endpoint={}", end_point)

        try:
            # Make the POST request with multipart data
            resp = self.connection_manager._make_request_for_file(
                method="POST",
                end_point=end_point,
                data=bytes(body),
                headers_input=headers,
            )
            logger.writeDebug(f"resp: {resp}")
            job_id = resp[API.JOB_ID]
            return self.connection_manager._process_job(job_id)
        except Exception as err:
            logger.writeException(err)
            raise err

    @log_entry_exit
    def download_smtp_root_certificate(self, file_name, target_smtp_server=1):
        """
        Download SMTP server root certificate.

        Args:
            file_name: Path where the certificate file will be saved
            target_smtp_server: SMTP server index (default: 1)

        Returns:
            None (writes certificate to file)
        """
        logger.writeDebug(
            "GW:download_smtp_root_certificate:file_name={}, target_smtp_server={}",
            file_name,
            target_smtp_server,
        )

        end_point = (
            f"v1/objects/smtp-server-root-certificates/{target_smtp_server}/download"
        )
        header = 'Content-Disposition: attachment; filename="/tmp/download_smtp_root_certificate"'

        # Download the certificate file
        resp = self.connection_manager.download_file(end_point)
        # resp = self.connection_manager.download_file_header(end_point, header)

        # Write to file
        with open(file_name, mode="wb") as file:
            file.write(resp)

        logger.writeDebug(
            "GW:download_smtp_root_certificate:certificate saved to {}", file_name
        )
        return
