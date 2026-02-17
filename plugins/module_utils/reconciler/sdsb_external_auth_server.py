import os
import time
from pathlib import Path

try:
    from ..provisioner.sdsb_external_auth_server_provisioner import (
        SDSBExternalAuthServerProvisioner,
    )
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..common.hv_constants import StateValue
    from ..message.sdsb_external_auth_server_msgs import (
        SDSBExternalAuthServerValidationMsg,
    )
except ImportError:
    from provisioner.sdsb_external_auth_server_provisioner import (
        SDSBExternalAuthServerProvisioner,
    )
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from common.hv_constants import StateValue
    from message.sdsb_external_auth_server_msgs import (
        SDSBExternalAuthServerValidationMsg,
    )

logger = Log()


class SDSBExternalAuthServerReconciler:

    def __init__(self, connection_info):
        self.connection_info = connection_info
        self.provisioner = SDSBExternalAuthServerProvisioner(self.connection_info)

    @log_entry_exit
    def get_user_auth_setting(self):
        return self.provisioner.get_user_auth_setting()

    @log_entry_exit
    def get_external_auth_server_settings(self):
        return self.provisioner.get_external_auth_server_settings()

    @log_entry_exit
    def reconcile_external_auth_server_settings(self, spec=None, state=None):
        logger.writeDebug(
            f"RECONCILER:reconcile_external_auth_server_settings:spec= {spec}, state= {state}"
        )

        if state == StateValue.PRESENT:
            if spec is None:
                return self.verify_external_auth_server_settings()
            else:
                return self.update_external_auth_server_settings(spec)
        elif state == StateValue.DOWNLOAD_ROOT_CERTIFICATE:
            return self.download_root_certificate(spec)
        elif state == StateValue.IMPORT_ROOT_CERTIFICATE:
            return self.import_root_certificate(spec)
        else:
            raise ValueError(
                SDSBExternalAuthServerValidationMsg.INVALID_STATE_PROVIDED.format(state)
            )

    @log_entry_exit
    def validate_import_root_certificate_spec(self, spec):
        if (
            spec is None
            or spec.root_certificate_file_path is None
            or spec.target_server is None
        ):
            raise ValueError(
                SDSBExternalAuthServerValidationMsg.IMPORT_ROOT_CERTIFICATE_SPEC_INVALID.value
            )
        certificate_path = spec.root_certificate_file_path
        # Validate certificate file exists
        if not os.path.exists(certificate_path):
            raise ValueError(f"Certificate file not found: {certificate_path}")

        spec.target_server = self.validate_target_server(spec.target_server)

    @log_entry_exit
    def import_root_certificate(self, spec):
        self.validate_import_root_certificate_spec(spec)
        logger.writeDebug(
            f"RC:=== Importing External Auth Server root certificate from {spec.root_certificate_file_path} for server index {spec.target_server} ==="
        )
        self.provisioner.import_external_auth_server_root_certificate(
            spec.root_certificate_file_path, spec.target_server
        )
        # Mark as changed since we're importing a new certificate
        self.connection_info.changed = True
        logger.writeDebug(
            "RC:=== External Auth Server root certificate imported successfully ==="
        )
        return "Root certificate for External Auth Server is imported successfully."

    @log_entry_exit
    def validate_target_server(self, target_server):
        valid_server_map = {
            "primary": "primary1",
            "secondary": "secondary1",
        }
        if target_server.lower() not in valid_server_map.keys():
            raise ValueError(
                SDSBExternalAuthServerValidationMsg.INVALID_TARGET_SERVER_PROVIDED.value
            )
        return valid_server_map[target_server.lower()]

    @log_entry_exit
    def validate_download_root_certificate_spec(self, spec):
        spec.target_server = self.validate_target_server(spec.target_server)
        if spec.download_location is None:
            spec.download_location = Path.home()

        # Create directory if it doesn't exist
        if not os.path.exists(spec.download_location):
            os.makedirs(spec.download_location)

    @log_entry_exit
    def download_root_certificate(self, spec):
        self.validate_download_root_certificate_spec(spec)

        # Generate filename with timestamp
        timestamp = int(time.time() * 1000)
        file_name = os.path.join(                                                               # nosec
            spec.download_location,                                                             # nosec
            f"external_auth_server_{spec.target_server}_root_certificate_{timestamp}.crt",      # nosec
        )                                                                                       # nosec
        logger.writeDebug(
            f"RC:=== Downloading External Auth Server root certificate for server {spec.target_server} to {file_name} ==="
        )
        try:
            # Download the certificate
            self.provisioner.download_external_auth_server_root_certificate(
                file_name, spec.target_server
            )
            # Mark as not changed since we're just downloading
            self.connection_info.changed = False

            logger.writeDebug(
                "RC:=== External Auth Server root certificate downloaded successfully ==="
            )
            return f"Successfully downloaded External Auth Server root certificate to {file_name}"
        except Exception as e:
            logger.writeError("GW:download_root_certificate:error={}", e)
            return str(e)

    @log_entry_exit
    def update_external_auth_server_settings(self, spec):
        current_auth_server_settings = self.get_external_auth_server_settings()
        if current_auth_server_settings is not None:
            if self.is_auth_server_update_reuired(current_auth_server_settings, spec):
                return self.provisioner.update_external_auth_server_settings(spec)
            else:
                return current_auth_server_settings
        else:
            raise ValueError(
                "No existing external authentication server settings found to update."
            )

    @log_entry_exit
    def is_auth_server_update_reuired(self, current_auth_server_settings, spec):
        logger.writeDebug(
            f"RECONCILER:is_auth_server_update_reuired:current_auth_server_settings= {current_auth_server_settings}, spec= {spec}"
        )
        if (
            spec.ldap_setting is not None
            and spec.ldap_setting.bind_dn_password is not None
        ):
            return True
        changed = False
        if (
            spec.is_enabled is not None
            and spec.is_enabled != current_auth_server_settings["is_enabled"]
        ):
            changed = True
        if (
            spec.auth_protocol is not None
            and spec.auth_protocol != current_auth_server_settings["auth_protocol"]
        ):
            changed = True
        if spec.ldap_setting is not None:
            current_ldap_setting = current_auth_server_settings.get("ldap_setting", {})
            if (
                spec.ldap_setting.mapping_mode is not None
                and spec.ldap_setting.mapping_mode
                != current_ldap_setting.get("mapping_mode")
            ):
                changed = True
            if (
                spec.ldap_setting.primary_ldap_server_url is not None
                and spec.ldap_setting.primary_ldap_server_url
                != current_ldap_setting.get("primary_ldap_server_url")
            ):
                changed = True
            if (
                spec.ldap_setting.secondary_ldap_server_url is not None
                and spec.ldap_setting.secondary_ldap_server_url
                != current_ldap_setting.get("secondary_ldap_server_url")
            ):
                changed = True
            if (
                spec.ldap_setting.is_start_tls_enabled is not None
                and spec.ldap_setting.is_start_tls_enabled
                != current_ldap_setting.get("is_start_tls_enabled")
            ):
                changed = True
            if (
                spec.ldap_setting.base_dn is not None
                and spec.ldap_setting.base_dn != current_ldap_setting.get("base_dn")
            ):
                changed = True
            if (
                spec.ldap_setting.bind_dn is not None
                and spec.ldap_setting.bind_dn != current_ldap_setting.get("bind_dn")
            ):
                changed = True
            if (
                spec.ldap_setting.user_id_attribute is not None
                and spec.ldap_setting.user_id_attribute
                != current_ldap_setting.get("user_id_attribute")
            ):
                changed = True
            if (
                spec.ldap_setting.user_tree_dn is not None
                and spec.ldap_setting.user_tree_dn
                != current_ldap_setting.get("user_tree_dn")
            ):
                changed = True
            if (
                spec.ldap_setting.user_object_class is not None
                and spec.ldap_setting.user_object_class
                != current_ldap_setting.get("user_object_class")
            ):
                changed = True
            if (
                spec.ldap_setting.external_group_name_attribute is not None
                and spec.ldap_setting.external_group_name_attribute
                != current_ldap_setting.get("external_group_name_attribute")
            ):
                changed = True
            if (
                spec.ldap_setting.user_group_tree_dn is not None
                and spec.ldap_setting.user_group_tree_dn
                != current_ldap_setting.get("user_group_tree_dn")
            ):
                changed = True
            if (
                spec.ldap_setting.user_group_object_class is not None
                and spec.ldap_setting.user_group_object_class
                != current_ldap_setting.get("user_group_object_class")
            ):
                changed = True
            if (
                spec.ldap_setting.timeout_seconds is not None
                and spec.ldap_setting.timeout_seconds
                != current_ldap_setting.get("timeout_seconds")
            ):
                changed = True
            if (
                spec.ldap_setting.retry_interval_milliseconds is not None
                and spec.ldap_setting.retry_interval_milliseconds
                != current_ldap_setting.get("retry_interval_milliseconds")
            ):
                changed = True
            if (
                spec.ldap_setting.max_retries is not None
                and spec.ldap_setting.max_retries
                != current_ldap_setting.get("max_retries")
            ):
                changed = True
        return changed

    @log_entry_exit
    def verify_external_auth_server_settings(self):
        response = self.provisioner.verify_external_auth_server_settings()
        if response:
            self.connection_info.changed = True
        return response
