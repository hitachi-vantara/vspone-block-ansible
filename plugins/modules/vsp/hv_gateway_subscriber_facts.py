#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_gateway_subscriber_facts
short_description: Retrieves information about subscriber on Hitachi VSP storage systems.
description:
  - This module retrieves information about subscriber.
  - It provides details about a subscriber such as name, ID and other relevant information.
  - This module is supported only for gateway connection type.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/subscriber_facts.yml)
version_added: '3.0.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
options:
  connection_info:
    description: Information required to establish a connection to the storage system.
    required: true
    type: dict
    suboptions:
      address:
        description: IP address or hostname of the UAI gateway.
        type: str
        required: true
      username:
        description: Username for authentication. Not needed for this module.
        type: str
        required: false
      password:
        description: Password for authentication. Not needed for this module.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['gateway']
        default: 'gateway'
      api_token:
        description: Token value to access UAI gateway.
        type: str
        required: false
  spec:
    description: Specification for retrieving subscriber information.
    type: dict
    suboptions:
      subscriber_id:
        type: str
        description: ID of the specific subscriber to retrieve information for (Works only for gateway connection type).
        required: false
"""

EXAMPLES = """
- name: Retrieve information about all subscribers
  hv_gateway_subscriber_facts:
    connection_info:
      address: gateway.company.com
      api_token: "eyJhbGciOiJS......"
      connection_type: "gateway"
    spec:
      subscriber_id: "811150"

- name: Retrieve information about a specific subscriber
  hv_gateway_subscriber_facts:
    connection_info:
      address: gateway.company.com
      api_token: "eyJhbGciOiJS......"
      connection_type: "gateway"
    spec:
      subscriber_id: "1234"
"""

RETURN = """
data:
  description: List of subscribers belonging to partner apiadmin.
  returned: success
  type: list
  elements: dict
  sample:
    {
        "hard_limit_in_percent": "90",
        "message": "",
        "name": "TestSubscriber",
        "partner_id": "apiadmin",
        "quota_limit_in_gb": "90",
        "soft_limit_in_percent": "80",
        "state": "NORMAL",
        "subscriber_id": "811150",
        "time": 1716260209,
        "type": "subscriber",
        "used_quota_in_gb": "0.1953125",
        "used_quota_in_percent": 0.2170139
    }
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.uaig_utils import (
    GatewayArguments,
    GatewayParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.uaig_subscriber_reconciler import (
    SubscriberReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class SubscriberFactsManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = GatewayArguments().get_subscriber_fact()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:
            self.params_manager = GatewayParametersManager(self.module.params)
            self.spec = self.params_manager.set_subscriber_fact_spec()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Gateway Subscriber Facts ===")
        registration_message = validate_ansible_product_registration()
        subscriber_data = None

        try:

            subscriber_data = SubscriberReconciler(
                self.params_manager.connection_info
            ).get_subscriber_facts(self.params_manager.spec)

        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of Gateway Subscriber Facts ===")
            self.module.fail_json(msg=str(e))

        data = {
            "subscriber_data": subscriber_data,
        }

        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo(f"{data}")
        self.logger.writeInfo("=== End of Gateway Subscriber Facts ===")
        self.module.exit_json(**data)


def main(module=None):
    obj_store = SubscriberFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
