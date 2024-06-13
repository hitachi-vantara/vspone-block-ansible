from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hv_uaig_token_fact
short_description: Retrieves an API token for the Histachi gateway service host.
description:
  - This module retrieves an API token for the gateway.
  - The API token is valid for 10 hours.
version_added: '3.0.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.0.0
requirements: []
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
        description: Username for authentication.
        type: str
        required: true
      password:
        description: Password for authentication.
        type: str
        required: true
'''

EXAMPLES = '''
- name: Retrieve information about all subscribers
  hv_gateway_subscriber_fact:         
    connection_info:
      address: gateway.company.com
      username: "admin"
      password: "password"
'''

RETURN = '''
data:
  description: List of subscribers belonging to partner apiadmin.
  returned: always
  type: dict
  elements: dict
  sample: 
    api_token:
      token: "eyJhbGci..."
      changed: false
      failed: false
'''

import json

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.uaig_auth_token import (
    UAIGAuthTokenReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    UAIGTokenArguments,
    SDSBParametersManager,
)

logger = Log()


class UAIGTokenFactManager:
    def __init__(self):

        self.argument_spec = UAIGTokenArguments.get_arguments()
        logger.writeDebug(f"MOD:hv_uai_token_fact:argument_spec= {self.argument_spec}")
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )

        self.params = SDSBParametersManager(self.module.params)

        parameterManager = SDSBParametersManager(self.module.params)
        self.connection_info = parameterManager.get_connection_info()
        logger.writeDebug(
            f"MOD:hv_uai_token_fact:connection_info= {self.connection_info}"
        )

    def apply(self):
        token = None

        logger.writeInfo(
            f"{self.params.connection_info.connection_type} connection type"
        )
        try:
            sdsb_reconciler = UAIGAuthTokenReconciler(self.connection_info)
            token = sdsb_reconciler.get_auth_token()

            logger.writeDebug(f"MOD:hv_uai_token_fact:compute_nodes= {token}")
            output = {
                "token": str(token),
            }
            # output_dict = chap_users.data_to_list()
            # chap_users_data_extracted = ChapUserPropertiesExtractor().extract(output_dict)

        except Exception as e:
            self.module.fail_json(msg=str(e))

        self.module.exit_json(api_token=output)


def main(module=None):
    obj_store = UAIGTokenFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
