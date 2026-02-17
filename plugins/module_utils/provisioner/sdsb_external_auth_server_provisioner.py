try:
    from ..gateway.sdsb_external_auth_server_gateway import (
        SDSBExternalAuthServerGateway,
    )
    from ..gateway.sdsb_storage_node_gateway import (
        SDSBStorageNodeDirectGateway,
    )
    from ..common.ansible_common import log_entry_exit
    from ..common.hv_log import Log
except ImportError:
    from gateway.sdsb_external_auth_server_gateway import SDSBExternalAuthServerGateway
    from common.ansible_common import log_entry_exit
    from common.hv_log import Log

logger = Log()


class SDSBExternalAuthServerProvisioner:

    def __init__(self, connection_info):
        self.connection_info = connection_info
        self.gateway = SDSBExternalAuthServerGateway(connection_info)

    @log_entry_exit
    def get_external_auth_server_settings(self):
        response = self.gateway.get_external_auth_server_settings()
        return response.camel_to_snake_dict()

    @log_entry_exit
    def verify_external_auth_server_settings(self):
        response = self.gateway.verify_external_auth_server_settings()
        logger.writeDebug(
            f"PROVISIONER:verify_external_auth_server_settings:response= {response}"
        )
        ret_value = response.camel_to_snake_dict()
        logger.writeDebug(
            f"PROVISIONER:verify_external_auth_server_settings:ret_value= {ret_value}"
        )
        return ret_value

    @log_entry_exit
    def update_external_auth_server_settings(self, spec):
        patch_param = {}
        if spec.is_enabled is not None:
            patch_param["isEnabled"] = spec.is_enabled
        if spec.auth_protocol is not None:
            patch_param["authProtocol"] = spec.auth_protocol
        if spec.ldap_setting is not None:
            ldap_setting = {}
            if spec.ldap_setting.mapping_mode is not None:
                ldap_setting["mappingMode"] = spec.ldap_setting.mapping_mode
            if spec.ldap_setting.primary_ldap_server_url is not None:
                ldap_setting["primaryLdapServerUrl"] = (
                    spec.ldap_setting.primary_ldap_server_url
                )
            if spec.ldap_setting.secondary_ldap_server_url is not None:
                ldap_setting["secondaryLdapServerUrl"] = (
                    spec.ldap_setting.secondary_ldap_server_url
                )
            if spec.ldap_setting.is_start_tls_enabled is not None:
                ldap_setting["isStartTlsEnabled"] = (
                    spec.ldap_setting.is_start_tls_enabled
                )
            if spec.ldap_setting.base_dn is not None:
                ldap_setting["baseDn"] = spec.ldap_setting.base_dn
            if spec.ldap_setting.bind_dn is not None:
                ldap_setting["bindDn"] = spec.ldap_setting.bind_dn
            if spec.ldap_setting.bind_dn_password is not None:
                ldap_setting["bindDnPassword"] = spec.ldap_setting.bind_dn_password
            if spec.ldap_setting.user_id_attribute is not None:
                ldap_setting["userIdAttribute"] = spec.ldap_setting.user_id_attribute
            if spec.ldap_setting.user_tree_dn is not None:
                ldap_setting["userTreeDn"] = spec.ldap_setting.user_tree_dn
            if spec.ldap_setting.user_object_class is not None:
                ldap_setting["userObjectClass"] = spec.ldap_setting.user_object_class
            if spec.ldap_setting.external_group_name_attribute is not None:
                ldap_setting["externalGroupNameAttribute"] = (
                    spec.ldap_setting.external_group_name_attribute
                )
            if spec.ldap_setting.user_group_tree_dn is not None:
                ldap_setting["userGroupTreeDn"] = spec.ldap_setting.user_group_tree_dn
            if spec.ldap_setting.user_group_object_class is not None:
                ldap_setting["userGroupObjectClass"] = (
                    spec.ldap_setting.user_group_object_class
                )
            if spec.ldap_setting.timeout_seconds is not None:
                ldap_setting["timeoutSeconds"] = spec.ldap_setting.timeout_seconds
            if spec.ldap_setting.retry_interval_milliseconds is not None:
                ldap_setting["retryIntervalMilliseconds"] = (
                    spec.ldap_setting.retry_interval_milliseconds
                )
            if spec.ldap_setting.max_retries is not None:
                ldap_setting["maxRetries"] = spec.ldap_setting.max_retries
            patch_param["ldapSetting"] = ldap_setting

        response = self.gateway.update_external_auth_server_settings(patch_param)
        logger.writeDebug(
            f"PROVISIONER:update_external_auth_server_settings:response= {response}"
        )
        ret_value = response.camel_to_snake_dict()
        self.connection_info.changed = True
        logger.writeDebug(
            f"PROVISIONER:update_external_auth_server_settings:ret_value= {ret_value}"
        )
        return ret_value

    @log_entry_exit
    def import_external_auth_server_root_certificate(self, file_name, target_server):
        host_ip = self.get_primary_master_node_ip()
        response = self.gateway.import_external_auth_server_root_certificate(
            host_ip, file_name, target_server
        )
        logger.writeDebug(
            f"PROVISIONER:import_external_auth_server_root_certificate:response= {response}"
        )

        return response

    @log_entry_exit
    def download_external_auth_server_root_certificate(self, file_name, target_server):
        host_ip = self.get_primary_master_node_ip()
        response = self.gateway.download_external_auth_server_root_certificate(
            host_ip, file_name, target_server
        )
        logger.writeDebug(
            f"PROVISIONER:download_external_auth_server_root_certificate:response= {response}"
        )

        return response

    @log_entry_exit
    def get_primary_master_node_ip(self):
        storage_node_gateway = SDSBStorageNodeDirectGateway(self.connection_info)
        storage_nodes = storage_node_gateway.get_storage_nodes()
        logger.writeDebug(
            f"PROVISIONER:get_primary_master_node_ip:storage_nodes= {storage_nodes}"
        )
        primary_master_node = None
        for node in storage_nodes.data:
            if node.isStorageMasterNodePrimary:
                primary_master_node = node
                break

        logger.writeDebug(
            f"PROVISIONER:get_primary_master_node_ip:primary_master_node= {primary_master_node}"
        )
        return primary_master_node.controlPortIpv4Address
