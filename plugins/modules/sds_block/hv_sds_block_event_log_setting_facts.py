#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_sds_block_event_log_setting_facts
short_description: Get event log setting from SDS Block storage system
description:
  - Get event log setting from SDS Block storage system.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/event_log_setting_facts.yml)
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
options:
  spec:
    description: Specification for the event log settings facts retrieval.
    type: dict
    required: false
    suboptions: {}
"""

EXAMPLES = """
- name: Retrieve event log setting information
  hitachivantara.vspone_block.sds_block.hv_sds_block_event_log_setting_facts:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
"""

RETURN = r"""
ansible_facts:
  description: >
    Dictionary containing the discovered event log setting.
  returned: always
  type: dict
  contains:
    event_log_setting:
      description: Event log setting information.
      type: dict
      contains:
        syslogForwardingSetting:
          description: Syslog forwarding settings.
          type: dict
          contains:
            locationName:
              description: Location name for syslog.
              type: str
              sample: "datacenter-01"
            syslogServers:
              description: List of syslog servers.
              type: list
              elements: dict
        emailReportSetting:
          description: Email report settings.
          type: dict
          contains:
            smtpSettings:
              description: List of SMTP server settings.
              type: list
              elements: dict
"""


from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBEventLogSettingArguments,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_event_log_settings import (
    SDSBEventLogSettingsReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class SDSBEventLogSettingFactsManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = SDSBEventLogSettingArguments().event_log_setting_facts()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()
        self.logger.writeDebug(
            f"MOD:event_log_settings:connection_info= {self.connection_info}"
        )

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB Event Log Setting Facts ===")
        event_log_settings = None
        event_log_settings_data_extracted = None
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_reconciler = SDSBEventLogSettingsReconciler(self.connection_info)
            event_log_settings = sdsb_reconciler.get_event_log_settings()

            self.logger.writeDebug(
                f"MOD:hv_sds_block_event_log_setting_facts:event_log_settings= {event_log_settings}"
            )
            output_dict = event_log_settings.camel_to_snake_dict()
        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB Event Log Setting Facts ===")
            self.module.fail_json(msg=str(e))

        data = {"event_log_settings": output_dict}
        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo("=== End of SDSB Event Log Setting Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)


def main():
    obj_store = SDSBEventLogSettingFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
