#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_sds_block_login_message_facts
short_description: Get the login message displayed in the GUI login window and CLI warning banner.
description:
  - Retrieves the message configured to be displayed on the GUI login window and CLI warning banner of the storage system.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/sds_block_login_message_facts.yml)
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
- name: Get the current login message
  hitachivantara.vspone_block.sds_block.hv_sds_block_login_message_facts:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
"""

RETURN = r"""
ansible_facts:
  description: >
    Dictionary containing the login message retrieved from the system.
  returned: always
  type: dict
  contains:
    login_message:
      description: The message displayed in the GUI login window and CLI warning banner.
      type: dict
      returned: always
      contains:
        message:
          description: Message body to be displayed in the GUI login window and CLI warning banner. Specify an empty string "" if nothing is to be displayed.
          type: str
          sample: "login message"
"""

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBLoginMessageArguments,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_login_message_reconciler import (
    SDSBLoginMessageReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)
from ansible.module_utils.basic import AnsibleModule


class SDSBLoginMessageFactsManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = SDSBLoginMessageArguments().login_message_facts()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:
            parameter_manager = SDSBParametersManager(self.module.params)
            self.connection_info = parameter_manager.get_connection_info()
            self.logger.writeDebug(
                f"MOD:hv_sds_block_login_message_facts:connection_info= {self.connection_info}"
            )
        except Exception as e:
            self.logger.writeError(f"An error occurred during initialization: {str(e)}")
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB Login Message Facts ===")
        login_message = None
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_login_reconciler = SDSBLoginMessageReconciler(self.connection_info)
            login_message = sdsb_login_reconciler.get_login_message()
            self.logger.writeDebug(
                f"MOD:hv_sds_block_login_message_facts:login_message= {login_message}"
            )

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB Login Message Facts ===")
            self.module.fail_json(msg=str(e))

        data = {"login_message": login_message}
        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo("=== End of SDSB Login Message Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)


def main():
    obj_store = SDSBLoginMessageFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
