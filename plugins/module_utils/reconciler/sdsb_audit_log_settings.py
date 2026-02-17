try:
    from ..provisioner.sdsb_audit_log_setting_provisioner import (
        SDSBAuditLogSettingProvisioner,
    )
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
except ImportError:
    from provisioner.sdsb_audit_log_setting_provisioner import (
        SDSBAuditLogSettingProvisioner,
    )
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit

logger = Log()


class SDSBAuditLogSettingsReconciler:

    def __init__(self, connection_info):
        self.connection_info = connection_info
        self.provisioner = SDSBAuditLogSettingProvisioner(self.connection_info)

    @log_entry_exit
    def get_audit_log_settings(self):
        return self.provisioner.get_audit_log_setting().camel_to_snake_dict()

    @log_entry_exit
    def modify_audit_log_settings(self, setting):
        # First get the current settings
        current_settings = self.provisioner.get_audit_log_setting()

        if current_settings and self._settings_match(current_settings, setting):
            logger.writeDebug("RC:=== Settings already match, no changes needed ===")
            self.connection_info.changed = False
            return current_settings.camel_to_snake_dict()

        # See If we need to make a change or not
        return self.provisioner.modify_audit_log_setting(setting).camel_to_snake_dict()

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

        logger.writeDebug("RC:=== All settings match ===")
        return True

    @log_entry_exit
    def reconcile_audit_log_settings(self, state, spec):
        logger.writeDebug("RC:=== reconcile audit log settings ===")

        if state.lower() == "download_audit_log":
            logger.writeDebug("RC:=== Downloading audit log file ===")
            return self.download_audit_log(spec)

        if spec is None:
            logger.writeDebug("RC:=== No spec provided, getting current settings ===")
            return self.get_audit_log_settings()

        if state.lower() == "present":
            logger.writeDebug("RC:=== Modifying audit log settings ===")
            # Convert spec to SDSBAuditLogSettingInfo object
            from ..model.sdsb_audit_log_models import (
                SDSBAuditLogSettingInfo,
                SDSBSyslogForwardingSettingInfo,
                SDSBSyslogServerInfo,
            )

            # Build syslog servers list
            syslog_servers = []
            if (
                spec.syslog_forwarding_setting
                and spec.syslog_forwarding_setting.syslog_servers
            ):
                for server_spec in spec.syslog_forwarding_setting.syslog_servers:
                    syslog_server = SDSBSyslogServerInfo(
                        index=server_spec.index,
                        isEnabled=server_spec.is_enabled,
                        serverName=server_spec.server_name,
                        port=server_spec.port,
                        transportProtocol=server_spec.transport_protocol or "UDP",
                    )
                    syslog_servers.append(syslog_server)

            # Build syslog forwarding setting
            syslog_forwarding = SDSBSyslogForwardingSettingInfo(
                locationName=(
                    spec.syslog_forwarding_setting.location_name or ""
                    if spec.syslog_forwarding_setting
                    else ""
                ),
                syslogServers=syslog_servers,
            )

            # Build audit log setting
            audit_log_setting = SDSBAuditLogSettingInfo(
                syslogForwardingSetting=syslog_forwarding
            )

            self.connection_info.changed = True
            return self.modify_audit_log_settings(audit_log_setting)
        else:
            raise ValueError(f"Unsupported state: {state}")

    @log_entry_exit
    def download_audit_log_file(self, file_name):
        return self.provisioner.download_audit_log_file(file_name)

    @log_entry_exit
    def create_audit_log_file(self, spec):
        return self.provisioner.create_audit_log_file(spec)

    @log_entry_exit
    def download_audit_log(self, spec):
        """Download audit log file to specified location"""
        import os
        import time

        if not spec or not spec.audit_log_file_location:
            raise ValueError(
                "audit_log_file_location is required for download_audit_log state"
            )

        file_location = spec.audit_log_file_location

        # Create directory if it doesn't exist
        if not os.path.exists(file_location):
            os.makedirs(file_location)

        ret_msg = ""
        # If refresh is True, create the audit log file on the storage system first
        if spec.refresh and spec.refresh is True:
            logger.writeDebug("RC:=== Creating audit log file on storage system ===")
            try:
                self.provisioner.create_audit_log_file(None)
                self.connection_info.changed = True
                ret_msg += "Audit log file created successfully. "
                logger.writeDebug("RC:=== Audit log file created successfully ===")
            except Exception as e:
                logger.writeError(f"RC:=== Failed to create audit log file: {e} ===")
                raise Exception(
                    f"Failed to create audit log file on storage system: {e}"
                )

        # Generate filename with timestamp
        timestamp = int(time.time() * 1000)
        file_name = os.path.join(file_location, f"audit_log_{timestamp}.zip")  # nosec

        logger.writeDebug(f"RC:=== Downloading audit log to {file_name} ===")

        try:
            # Download the file
            self.provisioner.download_audit_log_file(file_name)

            if not spec.refresh:
                self.connection_info.changed = False

            ret_msg += f"Successfully downloaded audit log file to {file_name}."
            return ret_msg
        except Exception as e:
            logger.writeError("GW:download_audit_log_file:error={}", e)
            ret_msg += "The file could not be downloaded. The target file does not exist. Please create the audit log file first."
            return ret_msg
