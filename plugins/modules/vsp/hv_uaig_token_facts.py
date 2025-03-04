#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_uaig_token_facts
short_description: Retrieves an API token for the Hitachi gateway service host.
description:
  - This module retrieves an API token for the gateway.
  - The API token is valid for 10 hours.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/uai_gateway_token.yml)
version_added: '3.0.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.8
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: full
options:
  connection_info:
    description: Information required to establish a connection to the UAI gateway.
    required: true
    type: dict
    suboptions:
      address:
        description: IP address or hostname of the UAI gateway.
        type: str
        required: true
      username:
        description: Username for authentication. This is a required field for token generation.
        type: str
        required: true
      password:
        description: Password for authentication. This is a required field for token generation.
        type: str
        required: true
"""

EXAMPLES = """
- name: Retrieve information about all subscribers
  hv_uaig_token_facts:
    connection_info:
      address: gateway.company.com
      username: "admin"
      password: "password"
"""

RETURN = """
ansible_facts:
  description: >
    Dictionary containing the discovered properties of the API token.
  returned: always
  type: dict
  contains:
    api_token:
      description: API token for the gateway.
      type: dict
      contains:
        token:
          description: The retrieved API token.
          type: str
          sample: "eyJhbGci..."
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.uaig_auth_token import (
    UAIGAuthTokenReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    UAIGTokenArguments,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class UAIGTokenFactManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = UAIGTokenArguments.get_arguments()
        self.logger.writeDebug(
            f"MOD:hv_uai_token_fact:argument_spec= {self.argument_spec}"
        )
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        self.params = SDSBParametersManager(self.module.params)

        parameterManager = SDSBParametersManager(self.module.params)
        self.connection_info = parameterManager.get_connection_info()

    def apply(self):
        self.logger.writeInfo("=== Start of UAI Token Facts ===")
        token = None
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_reconciler = UAIGAuthTokenReconciler(self.connection_info)
            token = sdsb_reconciler.get_auth_token()

            output = {
                "token": str(token),
            }

        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of UAI Token Facts ===")
            self.module.fail_json(msg=str(e))
        comments = None
        if registration_message:
            comments = registration_message

        self.logger.writeInfo("=== End of UAI Token Facts ===")
        self.module.exit_json(api_token=output, comments=comments)


def main(module=None):
    obj_store = UAIGTokenFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
