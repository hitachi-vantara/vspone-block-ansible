#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_sds_block_audit_log_setting_facts
short_description: Get audit log setting from SDS Block storage system
description:
  - Get audit log setting from SDS Block storage system.
version_added: '4.6.0'
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
- name: Retrieve audit log setting information
  hitachivantara.vspone_block.sds_block.hv_sds_block_audit_log_setting_facts:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
"""

RETURN = r"""
ansible_facts:
  description: >
    Dictionary containing the discovered audit log setting.
  returned: always
  type: dict
  contains:
    audit_log_setting:
      description: Audit log setting information.
      type: dict
      contains:
        enabled:
          description: Whether audit logging is enabled.
          type: bool
          sample: true
        destination:
          description: Audit log destination settings.
          type: str
          sample: "syslog"
"""


from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBAuditLogSettingArguments,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_audit_log_settings import (
    SDSBAuditLogSettingsReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class SDSBAuditLogSettingFactsManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = SDSBAuditLogSettingArguments().audit_log_setting_facts()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()
        self.logger.writeDebug(
            f"MOD:audit_log_settings:connection_info= {self.connection_info}"
        )

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB Audit Log Setting Facts ===")
        audit_log_settings = None
        audit_log_settings_data_extracted = None
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_reconciler = SDSBAuditLogSettingsReconciler(self.connection_info)
            audit_log_settings = sdsb_reconciler.get_audit_log_settings()

            self.logger.writeDebug(
                f"MOD:hv_sds_block_audit_log_setting_facts:audit_log_settings= {audit_log_settings}"
            )
            output_dict = audit_log_settings

            # we may not need this
            # audit_log_settings_data_extracted = AuditLogSettingPropertiesExtractor().extract_dict(
            #     output_dict
            # )

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB Audit Log Setting Facts ===")
            self.module.fail_json(msg=str(e))

        # data = {"audit_log_settings": audit_log_settings_data_extracted}
        data = {"audit_log_settings": output_dict}
        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo("=== End of SDSB Audit Log Setting Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)


def main():
    obj_store = SDSBAuditLogSettingFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
