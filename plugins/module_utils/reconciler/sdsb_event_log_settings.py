import os
import time
from pathlib import Path

try:
    from ..provisioner.sdsb_event_log_setting_provisioner import (
        SDSBEventLogSettingProvisioner,
    )
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
except ImportError:
    from provisioner.sdsb_event_log_setting_provisioner import (
        SDSBEventLogSettingProvisioner,
    )
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit

logger = Log()


class SDSBEventLogSettingsReconciler:

    def __init__(self, connection_info):
        self.connection_info = connection_info
        self.provisioner = SDSBEventLogSettingProvisioner(self.connection_info)

    @log_entry_exit
    def get_event_log_settings(self):
        return self.provisioner.get_event_log_setting()

    @log_entry_exit
    def modify_event_log_settings(self, setting):
        """
        Modify event log settings with idempotency check.
        Routes to appropriate method based on what's being modified.
        """
        # First get the current settings
        current_settings = self.provisioner.get_event_log_setting()

        if current_settings and self._settings_match(current_settings, setting):
            logger.writeDebug("RC:=== Settings already match, no changes needed ===")
            self.connection_info.changed = False
            return current_settings

        # See If we need to make a change or not
        return self.provisioner.modify_event_log_setting(setting)

    @log_entry_exit
    def modify_event_log_settings_syslog(self, syslog_setting):
        """
        Modify syslog forwarding settings only with idempotency check.
        """
        # First get the current settings
        current_settings = self.provisioner.get_event_log_setting()

        # Check if syslog settings match
        if current_settings and current_settings.syslogForwardingSetting:
            if self._syslog_settings_match(
                current_settings.syslogForwardingSetting, syslog_setting
            ):
                logger.writeDebug(
                    "RC:=== Syslog settings already match, no changes needed ==="
                )
                self.connection_info.changed = False
                return current_settings

        # Make the change
        self.connection_info.changed = True
        return self.provisioner.modify_event_log_setting_syslog(syslog_setting)

    @log_entry_exit
    def modify_event_log_settings_email(self, email_setting):
        """
        Modify email report settings only with idempotency check.
        """
        # First get the current settings
        current_settings = self.provisioner.get_event_log_setting()

        # Check if email settings match
        if current_settings and current_settings.emailReportSetting:
            if self._email_settings_match(
                current_settings.emailReportSetting, email_setting
            ):
                logger.writeDebug(
                    "RC:=== Email settings already match, no changes needed ==="
                )
                self.connection_info.changed = False
                return current_settings

        # Make the change
        self.connection_info.changed = True
        return self.provisioner.modify_event_log_setting_email(email_setting)

    def _settings_match(self, current_settings, desired_setting):
        """Compare current settings with desired settings by index"""
        logger.writeDebug("RC:=== Comparing current and desired settings ===")

        # Check if both have syslog forwarding settings
        if not (
            current_settings.syslogForwardingSetting
            and desired_setting.syslogForwardingSetting
        ):
            return False

        current_forwarding = current_settings.syslogForwardingSetting
        desired_forwarding = desired_setting.syslogForwardingSetting

        # Compare location names
        if current_forwarding.locationName != desired_forwarding.locationName:
            logger.writeDebug(
                f"RC:=== Location name mismatch: current='{current_forwarding.locationName}', desired='{desired_forwarding.locationName}' ==="
            )
            return False

        # Compare syslog servers by index
        if not (current_forwarding.syslogServers and desired_forwarding.syslogServers):
            return False

        # Create dictionaries for easy comparison by index
        current_servers = {
            server.index: server for server in current_forwarding.syslogServers
        }
        desired_servers = {
            server.index: server for server in desired_forwarding.syslogServers
        }

        # Check each desired server against current server with same index
        for index, desired_server in desired_servers.items():
            if index not in current_servers:
                logger.writeDebug(
                    f"RC:=== Server with index {index} not found in current settings ==="
                )
                return False

            current_server = current_servers[index]

            # Compare all server properties
            if (
                current_server.isEnabled != desired_server.isEnabled
                or current_server.serverName != desired_server.serverName
                or current_server.port != desired_server.port
                or current_server.transportProtocol != desired_server.transportProtocol
            ):
                logger.writeDebug(f"RC:=== Server {index} properties mismatch ===")
                logger.writeDebug(
                    f"RC:=== Current: enabled={current_server.isEnabled}, "
                    f"name='{current_server.serverName}', port={current_server.port}, "
                    f"protocol='{current_server.transportProtocol}' ==="
                )
                logger.writeDebug(
                    f"RC:=== Desired: enabled={desired_server.isEnabled}, "
                    f"name='{desired_server.serverName}', port={desired_server.port}, "
                    f"protocol='{desired_server.transportProtocol}' ==="
                )
                return False

        # Compare email report settings if present in desired settings
        if desired_setting.emailReportSetting:
            if not current_settings.emailReportSetting:
                logger.writeDebug(
                    "RC:=== Email report setting missing in current settings ==="
                )
                return False

            current_email = current_settings.emailReportSetting
            desired_email = desired_setting.emailReportSetting

            # Compare SMTP settings by index
            if not (current_email.smtpSettings and desired_email.smtpSettings):
                return False

            # Create dictionaries for easy comparison by index
            current_smtp = {smtp.index: smtp for smtp in current_email.smtpSettings}
            desired_smtp = {smtp.index: smtp for smtp in desired_email.smtpSettings}

            # Check each desired SMTP setting against current SMTP setting with same index
            for index, desired_smtp_server in desired_smtp.items():
                if index not in current_smtp:
                    logger.writeDebug(
                        f"RC:=== SMTP server with index {index} not found in current settings ==="
                    )
                    return False

                current_smtp_server = current_smtp[index]

                # Compare all SMTP server properties
                # Note: Password is not compared as it may not be returned by the API
                if (
                    current_smtp_server.isEnabled != desired_smtp_server.isEnabled
                    or current_smtp_server.smtpServerName
                    != desired_smtp_server.smtpServerName
                    or current_smtp_server.port != desired_smtp_server.port
                    or current_smtp_server.connectionEncryptionType
                    != desired_smtp_server.connectionEncryptionType
                    or current_smtp_server.isSmtpAuthEnabled
                    != desired_smtp_server.isSmtpAuthEnabled
                    or current_smtp_server.smtpAuthAccount
                    != desired_smtp_server.smtpAuthAccount
                    or current_smtp_server.fromAddress
                    != desired_smtp_server.fromAddress
                    or current_smtp_server.toAddress1 != desired_smtp_server.toAddress1
                    or current_smtp_server.toAddress2 != desired_smtp_server.toAddress2
                    or current_smtp_server.toAddress3 != desired_smtp_server.toAddress3
                ):
                    logger.writeDebug(
                        f"RC:=== SMTP server {index} properties mismatch ==="
                    )
                    return False

                # If password is provided in desired settings, always consider it changed
                # (API doesn't return passwords for security, so we can't compare)
                if desired_smtp_server.smtpAuthPassword is not None:
                    logger.writeDebug(
                        f"RC:=== SMTP server {index} has password update ==="
                    )
                    return False

        logger.writeDebug("RC:=== All settings match ===")
        return True

    def _syslog_settings_match(self, current_forwarding, desired_forwarding):
        """Compare syslog forwarding settings by index"""
        logger.writeDebug("RC:=== Comparing syslog settings ===")

        # Compare location names
        if current_forwarding.locationName != desired_forwarding.locationName:
            logger.writeDebug(
                f"RC:=== Location name mismatch: current='{current_forwarding.locationName}', desired='{desired_forwarding.locationName}' ==="
            )
            return False

        # Compare syslog servers by index
        if not (current_forwarding.syslogServers and desired_forwarding.syslogServers):
            return False

        # Create dictionaries for easy comparison by index
        current_servers = {
            server.index: server for server in current_forwarding.syslogServers
        }
        desired_servers = {
            server.index: server for server in desired_forwarding.syslogServers
        }

        # Check each desired server against current server with same index
        for index, desired_server in desired_servers.items():
            if index not in current_servers:
                logger.writeDebug(
                    f"RC:=== Syslog server with index {index} not found in current settings ==="
                )
                return False

            current_server = current_servers[index]

            # Compare all server properties
            if (
                current_server.isEnabled != desired_server.isEnabled
                or current_server.serverName != desired_server.serverName
                or current_server.port != desired_server.port
                or current_server.transportProtocol != desired_server.transportProtocol
            ):
                logger.writeDebug(
                    f"RC:=== Syslog server {index} properties mismatch ==="
                )
                return False

        logger.writeDebug("RC:=== All syslog settings match ===")
        return True

    def _email_settings_match(self, current_email, desired_email):
        """Compare email report settings by index"""
        logger.writeDebug("RC:=== Comparing email settings ===")

        # Compare SMTP settings by index
        if not (current_email.smtpSettings and desired_email.smtpSettings):
            return False

        # Create dictionaries for easy comparison by index
        current_smtp = {smtp.index: smtp for smtp in current_email.smtpSettings}
        desired_smtp = {smtp.index: smtp for smtp in desired_email.smtpSettings}

        # Check each desired SMTP setting against current SMTP setting with same index
        for index, desired_smtp_server in desired_smtp.items():
            if index not in current_smtp:
                logger.writeDebug(
                    f"RC:=== SMTP server with index {index} not found in current settings ==="
                )
                return False

            current_smtp_server = current_smtp[index]

            # Compare all SMTP server properties (except password)
            if (
                current_smtp_server.isEnabled != desired_smtp_server.isEnabled
                or current_smtp_server.smtpServerName
                != desired_smtp_server.smtpServerName
                or current_smtp_server.smtpAuthAccount
                != desired_smtp_server.smtpAuthAccount
                or current_smtp_server.fromAddress != desired_smtp_server.fromAddress
                or current_smtp_server.toAddress1 != desired_smtp_server.toAddress1
                or current_smtp_server.toAddress2 != desired_smtp_server.toAddress2
                or current_smtp_server.toAddress3 != desired_smtp_server.toAddress3
            ):
                logger.writeDebug(f"RC:=== SMTP server {index} properties mismatch ===")
                return False

        logger.writeDebug("RC:=== All email settings match ===")
        return True

    @log_entry_exit
    def reconcile_event_log_settings(self, state, spec):
        logger.writeDebug("RC:=== reconcile event log settings ===")

        if state.lower() == "import_smtp_certificate":
            logger.writeDebug("RC:=== Importing SMTP root certificate ===")
            if not spec or not spec.smtp_root_certificate:
                raise ValueError(
                    "smtp_root_certificate spec is required for import_smtp_certificate state"
                )
            return self.import_smtp_root_certificate(spec.smtp_root_certificate)

        if state.lower() == "download_smtp_certificate":
            logger.writeDebug("RC:=== Downloading SMTP root certificate ===")
            return self.download_smtp_root_certificate(spec.smtp_root_certificate)

        if spec is None:
            logger.writeDebug("RC:=== No spec provided, getting current settings ===")
            return self.get_event_log_settings()

        if state.lower() == "present":
            logger.writeDebug("RC:=== Modifying event log settings ===")
            # Convert spec to SDSBEventLogSettingInfo object
            try:
                from ..model.sdsb_event_log_models import (
                    SDSBSyslogForwardingSettingInfo,
                    SDSBSyslogServerInfo,
                    SDSBEmailReportSettingInfo,
                    SDSBSmtpSettingInfo,
                )
            except ImportError:
                from model.sdsb_event_log_models import (
                    SDSBSyslogForwardingSettingInfo,
                    SDSBSyslogServerInfo,
                    SDSBEmailReportSettingInfo,
                    SDSBSmtpSettingInfo,
                )

            # Check which settings are being modified
            has_syslog = (
                spec.syslog_forwarding_setting is not None
                and spec.syslog_forwarding_setting.syslog_servers
            )
            has_email = (
                spec.email_report_setting and spec.email_report_setting.smtp_settings
            )

            # Validate that only one type is being modified
            if has_syslog and has_email:
                raise ValueError(
                    "Cannot modify both syslogForwardingSetting and emailReportSetting simultaneously. "
                    "Modify them separately."
                )

            # Modify syslog settings only
            if has_syslog:
                logger.writeDebug("RC:=== Modifying syslog settings only ===")
                syslog_servers = []
                for server_spec in spec.syslog_forwarding_setting.syslog_servers:
                    syslog_server = SDSBSyslogServerInfo(
                        index=server_spec.index,
                        isEnabled=server_spec.is_enabled,
                        serverName=server_spec.server_name,
                        port=server_spec.port,
                        transportProtocol=server_spec.transport_protocol or "UDP",
                    )
                    syslog_servers.append(syslog_server)

                syslog_forwarding = SDSBSyslogForwardingSettingInfo(
                    locationName=spec.syslog_forwarding_setting.location_name,
                    syslogServers=syslog_servers,
                )

                return self.modify_event_log_settings_syslog(syslog_forwarding)

            # Modify email settings only
            elif has_email:
                logger.writeDebug("RC:=== Modifying email settings only ===")
                smtp_settings = []
                for smtp_spec in spec.email_report_setting.smtp_settings:
                    smtp_setting = SDSBSmtpSettingInfo(
                        index=smtp_spec.index,
                        isEnabled=smtp_spec.is_enabled,
                        smtpServerName=smtp_spec.smtp_server_name,
                        port=smtp_spec.port,
                        connectionEncryptionType=smtp_spec.connection_encryption_type
                        or "STARTTLS",
                        isSmtpAuthEnabled=smtp_spec.is_smtp_auth_enabled,
                        smtpAuthAccount=smtp_spec.smtp_auth_account,
                        smtpAuthPassword=smtp_spec.smtp_auth_password,
                        fromAddress=smtp_spec.from_address,
                        toAddress1=smtp_spec.to_address1,
                        toAddress2=smtp_spec.to_address2 or "",
                        toAddress3=smtp_spec.to_address3 or "",
                    )
                    smtp_settings.append(smtp_setting)

                email_report_setting = SDSBEmailReportSettingInfo(
                    smtpSettings=smtp_settings
                )

                return self.modify_event_log_settings_email(email_report_setting)

            else:
                raise ValueError(
                    "Either syslog_forwarding_setting or email_report_setting must be provided"
                )
        else:
            raise ValueError(f"Unsupported state: {state}")

    @log_entry_exit
    def import_smtp_root_certificate(self, certificate_spec):
        """
        Import SMTP server root certificate.

        Args:
            certificate_spec: SmtpRootCertificateSpec containing certificate_path and target_smtp_server

        Returns:
            Result from the API call
        """

        if not certificate_spec or not certificate_spec.certificate_path:
            raise ValueError(
                "certificate_path is required for importing SMTP root certificate"
            )

        certificate_path = certificate_spec.certificate_path
        target_smtp_server = certificate_spec.target_smtp_server or 1

        # Validate certificate file exists
        if not os.path.exists(certificate_path):
            raise ValueError(f"Certificate file not found: {certificate_path}")

        logger.writeDebug(
            f"RC:=== Importing SMTP root certificate from {certificate_path} for server index {target_smtp_server} ==="
        )

        # Import the certificate
        result = self.provisioner.import_smtp_root_certificate(
            certificate_path, target_smtp_server
        )

        # Mark as changed since we're uploading a certificate
        self.connection_info.changed = True

        logger.writeDebug("RC:=== SMTP root certificate imported successfully ===")
        return (
            "Root certificate for SMTP server communication is imported successfully."
        )

    @log_entry_exit
    def download_smtp_root_certificate(self, certificate_spec=None):
        """
        Download SMTP server root certificate.

        Args:
            certificate_spec: SmtpRootCertificateSpec containing download_location and target_smtp_server

        Returns:
            Success message with file path
        """

        download_location = ""
        if not certificate_spec or not certificate_spec.download_location:
            download_location = Path.home()
        else:
            download_location = certificate_spec.download_location

        target_smtp_server = 1
        if certificate_spec and certificate_spec.target_smtp_server is not None:
            target_smtp_server = certificate_spec.target_smtp_server

        # Create directory if it doesn't exist
        if not os.path.exists(download_location):
            os.makedirs(download_location)

        # Generate filename with timestamp
        timestamp = int(time.time() * 1000)  # nosec
        file_name = os.path.join(  # nosec
            download_location,  # nosec
            f"smtp_server_{target_smtp_server}_root_certificate_{timestamp}.crt",  # nosec
        )  # nosec

        logger.writeDebug(
            f"RC:=== Downloading SMTP root certificate from server {target_smtp_server} to {file_name} ==="
        )

        # Download the certificate
        self.provisioner.download_smtp_root_certificate(file_name, target_smtp_server)
        # Mark as not changed since we're just downloading
        self.connection_info.changed = False

        logger.writeDebug("RC:=== SMTP root certificate downloaded successfully ===")
        return f"Successfully downloaded SMTP root certificate to {file_name}"
