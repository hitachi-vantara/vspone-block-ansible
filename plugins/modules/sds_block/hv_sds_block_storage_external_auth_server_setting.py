#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_sds_block_storage_external_auth_server_setting
short_description: Manages external authentication server settings on VSP One SDS Block and Cloud systems.
description:
  - This module allows to configure external authentication server settings.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/external_auth_server_setting.yml)
version_added: '4.6.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.9
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: none
extends_documentation_fragment:
  - hitachivantara.vspone_block.common.sdsb_connection_info
options:
  state:
    description: State of the external authentication server settings.
    required: false
    type: str
    choices: ['present', 'download_root_certificate', 'import_root_certificate']
    default: 'present'
  spec:
    description: Specification for External Auth Server Settings.
    required: false
    type: dict
    suboptions:
      is_enabled:
        description: Whether external authentication is enabled.
        type: bool
        required: false
      auth_protocol:
        description: Authentication protocol used for external authentication.
        type: str
        choices: ['LDAP']
        default: LDAP
        required: false
      download_location:
        description: Local filesystem path where the root certificate will be downloaded.
        required: false
        type: str
      target_server:
        description:
          - Hostname or IP address of the external authentication server.
        required: false
        type: str
      root_certificate_file_path:
        description: Absolute path of the root certificate file to be imported.
        required: false
        type: str
      ldap_setting:
        description: LDAP-specific configuration settings.
        type: dict
        required: false
        suboptions:
          mapping_mode:
            description: Specifies how LDAP entries are mapped.
            type: str
            choices: ['User', 'Group']
            required: false
          primary_ldap_server_url:
            description: URL of the primary LDAP server.
            type: str
            required: false
          secondary_ldap_server_url:
            description: URL of the secondary LDAP server.
            type: str
            required: false
          is_start_tls_enabled:
            description: Whether STARTTLS is enabled for LDAP communication.
            type: bool
            required: false
          base_dn:
            description: Base distinguished name (DN) for LDAP searches.
            type: str
            required: false
          bind_dn:
            description: Distinguished name (DN) used to bind to the LDAP server.
            type: str
            required: false
          bind_dn_password:
            description: Password for the bind DN.
            type: str
            required: false
          user_id_attribute:
            description: LDAP attribute used as the user ID.
            type: str
            required: false
          user_tree_dn:
            description: Base DN under which user entries are searched.
            type: str
            required: false
          user_object_class:
            description: LDAP object class used for user entries.
            type: str
            required: false
          external_group_name_attribute:
            description: LDAP attribute used as the external group name.
            type: str
            required: false
          user_group_tree_dn:
            description: Base DN under which group entries are searched.
            type: str
            required: false
          user_group_object_class:
            description: LDAP object class used for group entries.
            type: str
            required: false
          timeout_seconds:
            description: Timeout value in seconds for LDAP operations.
            type: int
            required: false
          retry_interval_milliseconds:
            description: Interval in milliseconds between retry attempts.
            type: int
            required: false
          max_retries:
            description: Maximum number of retry attempts for LDAP operations.
            type: int
            required: false
"""

EXAMPLES = """
- name: Update external auth server settings
  hitachivantara.vspone_block.sds_block.hv_sds_block_storage_external_auth_server_setting:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      auth_protocol: "LDAP"
      is_enabled: true
      ldap_setting:
        base_dn: "dc=esd-dc1,dc=sie,dc=hds,dc=com"
        bind_dn: "cn=ldap1,cn=Users,dc=esd-dc1,dc=sie,dc=hds,dc=com"
        bind_password: "CHANGEME_123"
        external_group_name_attribute: "sAMAccountName"
        is_start_tls_enabled: false
        mapping_mode: "Group"
        max_retries: 1
        primary_ldap_server_url: "ldap://esd-dc1.sie.hds.com"
        retry_interval_milliseconds: 100
        secondary_ldap_server_url: ""
        timeout_seconds: 7
        user_group_object_class: "Group"
        user_group_tree_dn: "ou=StorageGroups,dc=esd-dc1,dc=sie,dc=hds,dc=com"
        user_id_attribute: "sAMAccountName"
        user_object_class: "User"
        user_tree_dn: "ou=StorageUsers,dc=esd-dc1,dc=sie,dc=hds,dc=com"

- name: Verify external auth server settings
  hitachivantara.vspone_block.sds_block.hv_sds_block_storage_external_auth_server_setting:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
"""

RETURN = """
external_auth_server_settings:
  description:
    - External authentication server configuration settings.
  returned: success
  type: dict
  contains:
    auth_protocol:
      description:
        - Authentication protocol used by the external authentication server.
      type: str
      sample: LDAP
    is_enabled:
      description:
        - Indicates whether external authentication is enabled.
      type: bool
      sample: false
    ldap_setting:
      description:
        - LDAP-specific configuration settings.
      type: dict
      contains:
        base_dn:
          description:
            - Base distinguished name used for LDAP searches.
          type: str
          sample: dc=example,dc=com
        bind_dn:
          description:
            - Distinguished name used to bind to the LDAP server.
          type: str
          sample: cn=admin,dc=example,dc=com
        external_group_name_attribute:
          description:
            - LDAP attribute used as the external group name.
          type: str
          sample: cn
        is_start_tls_enabled:
          description:
            - Indicates whether STARTTLS is enabled for LDAP connections.
          type: bool
          sample: false
        mapping_mode:
          description:
            - Mapping mode used for LDAP user and group mapping.
          type: str
          sample: User
        max_retries:
          description:
            - Maximum number of retry attempts for LDAP connections.
          type: int
          sample: 1
        primary_ldap_server_url:
          description:
            - URL of the primary LDAP server.
          type: str
          sample: ldap://ldap-primary.example.com
        retry_interval_milliseconds:
          description:
            - Interval between retry attempts in milliseconds.
          type: int
          sample: 100
        secondary_ldap_server_url:
          description:
            - URL of the secondary LDAP server.
          type: str
          sample: ldap://ldap-secondary.example.com
        timeout_seconds:
          description:
            - LDAP connection timeout in seconds.
          type: int
          sample: 7
        user_group_object_class:
          description:
            - LDAP object class used for user groups.
          type: str
          sample: group
        user_group_tree_dn:
          description:
            - Distinguished name for the LDAP user group search tree.
          type: str
          sample: ou=groups,dc=example,dc=com
        user_id_attribute:
          description:
            - LDAP attribute used as the user identifier.
          type: str
          sample: cn
        user_object_class:
          description:
            - LDAP object class used for user entries.
          type: str
          sample: person
        user_tree_dn:
          description:
            - Distinguished name for the LDAP user search tree.
          type: str
          sample: ou=users,dc=example,dc=com
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_external_auth_server import (
    SDSBExternalAuthServerReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBExternalAuthServerArguments,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)


class SDSBExternalAuthServerSettingManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = (
            SDSBExternalAuthServerArguments().external_auth_server_setting()
        )
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )

        parameter_manager = SDSBParametersManager(self.module.params)
        self.state = parameter_manager.get_state()
        self.connection_info = parameter_manager.get_connection_info()
        self.spec = parameter_manager.get_external_auth_server_setting_spec()

    def apply(self):
        self.logger.writeInfo(
            "=== Start of SDSB External Auth Server Setting Operation ==="
        )
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_reconciler = SDSBExternalAuthServerReconciler(self.connection_info)
            ext_auth_server_settings = (
                sdsb_reconciler.reconcile_external_auth_server_settings(
                    self.spec, self.state
                )
            )

            self.logger.writeDebug(
                f"MOD:hv_sds_block_storage_external_auth_server_setting:external_auth_server_settings= {ext_auth_server_settings}"
            )

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo(
                "=== End of SDSB External Auth Server Setting Operation ==="
            )
            self.module.fail_json(msg=str(e))

        response = {
            "changed": self.connection_info.changed,
        }
        if (
            self.state == "import_root_certificate"
            or self.state == "download_root_certificate"
        ):
            response["message"] = ext_auth_server_settings
        else:
            response["external_auth_server_settings"] = ext_auth_server_settings

        if registration_message:
            response["user_consent_required"] = registration_message
        self.logger.writeInfo(
            "=== End of SDSB External Auth Server Setting Operation ==="
        )
        self.module.exit_json(**response)


def main(module=None):
    obj_store = SDSBExternalAuthServerSettingManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
