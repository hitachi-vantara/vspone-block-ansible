#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function


__metaclass__ = type

DOCUMENTATION = """
---
module: hv_sds_block_login_message
short_description: Update the login message displayed in the GUI login window and CLI warning banner.
description:
  - Update the message configured to be displayed on the GUI login window and CLI warning banner of the storage system.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/sds_block_login_message.yml)
version_added: "4.6.0"
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
    description: The level of the login message task.
    type: str
    required: false
    choices: ['present']
    default: 'present'
  spec:
    description: Specification for the login message to be updated.
    type: dict
    required: true
    suboptions:
      login_message:
        description: Message body to be displayed in the GUI login window and CLI warning banner. Specify an empty string "" if nothing is to be displayed.
        type: str
        required: true
"""

EXAMPLES = """
- name: Update the current login message
  hitachivantara.vspone_block.sds_block.hv_sds_block_login_message:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    state: present
    spec:
        login_message: "login messagee"
"""

RETURN = r"""
login_message:
  description: The message displayed in the GUI login window and CLI warning banner.
  type: dict
  returned: always
  contains:
    login_message:
      description: Message body to be displayed in the GUI login window and CLI warning banner. Specify an empty string "" if nothing is to be displayed.
      type: str
      sample: "login message"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_login_message_reconciler import (
    SDSBLoginMessageReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBLoginMessageArguments,
    SDSBParametersManager,
)


class SDSBLoginMessageManager:

    def __init__(self):

        self.logger = Log()
        self.argument_spec = SDSBLoginMessageArguments().login_message()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )
        try:
            parameter_manager = SDSBParametersManager(self.module.params)
            self.connection_info = parameter_manager.get_connection_info()
            self.spec = parameter_manager.get_login_message_spec()
            self.state = parameter_manager.get_state()
            self.logger.writeDebug(f"MOD:hv_sds_block_login_message:spec= {self.spec}")
        except Exception as e:
            self.logger.writeError(f"An error occurred during initialization: {str(e)}")
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB Journal Facts ===")
        login_message = None
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_login_reconciler = SDSBLoginMessageReconciler(self.connection_info)
            login_message = sdsb_login_reconciler.update_login_message(
                self.spec, self.state
            )

            self.logger.writeDebug(
                f"MOD:hv_sds_journal_facts:journals= {login_message}"
            )

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB login_message Facts ===")
            self.module.fail_json(msg=str(e))
        data = {
            "changed": self.connection_info.changed,
            "login_message": login_message,
        }

        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo("=== End of SDSB login_message Facts ===")
        self.module.exit_json(**data)


def main():
    obj_store = SDSBLoginMessageManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
