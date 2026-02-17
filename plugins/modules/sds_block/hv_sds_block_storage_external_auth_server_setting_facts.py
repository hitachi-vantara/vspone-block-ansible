#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_sds_block_storage_external_auth_server_setting_facts
short_description: Get external authentication server settings from the storage system.
description:
  - Get external authentication server settings from the storage system.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/external_auth_server_setting_facts.yml)
version_added: "4.6.0"
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.9
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: full
extends_documentation_fragment:
  - hitachivantara.vspone_block.common.sdsb_connection_info
"""

EXAMPLES = """
- name: Retrieve information about external authentication server settings.
  hitachivantara.vspone_block.sds_block.hv_sds_block_storage_external_auth_server_setting_facts:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
"""

RETURN = r"""
---
ansible_facts:
  description: Facts containing details of external authentication server settings configured in the system.
  returned: always
  type: dict
  contains:
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

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBExternalAuthServerArguments,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_external_auth_server import (
    SDSBExternalAuthServerReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class SDSBExternalAuthServerSettingFactsManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = (
            SDSBExternalAuthServerArguments().external_auth_server_facts()
        )
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()
        # self.spec = parameter_manager.get_user_group_facts_spec()
        # self.logger.writeDebug(f"MOD:hv_sds_users_group_facts:spec= {self.spec}")

    def apply(self):
        self.logger.writeInfo(
            "=== Start of SDSB External Auth Server Setting Facts ==="
        )
        external_auth_server_settings = None
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_reconciler = SDSBExternalAuthServerReconciler(self.connection_info)
            external_auth_server_settings = (
                sdsb_reconciler.get_external_auth_server_settings()
            )

            self.logger.writeDebug(
                f"MOD:hv_sds_block_storage_external_auth_server_setting_facts:external_auth_server_settings= {external_auth_server_settings}"
            )

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo(
                "=== End of SDSB External Auth Server Setting Facts ==="
            )
            self.module.fail_json(msg=str(e))

        data = {"external_auth_server_settings": external_auth_server_settings}
        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo("=== End of SDSB External Auth Server Setting Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)


def main():
    obj_store = SDSBExternalAuthServerSettingFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
