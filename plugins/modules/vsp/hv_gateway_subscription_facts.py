#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_gateway_subscription_facts
short_description: Retrieves information about resources of a subscriber on Hitachi VSP storage systems.
description:
  - This module retrieves information about resources of a subscriber.
  - It provides details about resources of a subscriber such as type, value and other relevant information.
  - This module is supported only for gateway connection type.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/subscription_facts.yml)
version_added: '3.1.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
options:
  connection_info:
    description: Information required to establish a connection to the storage system.
    required: true
    type: dict
    suboptions:
      address:
        description: IP address or hostname of UAI gateway.
        type: str
        required: true
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        default: 'gateway'
        choices: ['gateway']
      subscriber_id:
        description: This field is valid for gateway connection type only. This is an optional field and only needed to support multi-tenancy environment.
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway.
        type: str
        required: false
      username:
        description: Username for authentication.This field is valid for direct connection type only, and it is a required field.
          Not needed for this module.
        type: str
        required: false
      password:
        description: Password for authentication.This field is valid for direct connection type only, and it is a required field.
          Not needed for this module.
        type: str
        required: false
  storage_system_info:
    description:
      - Information about the Hitachi storage system.
    type: dict
    required: false
    suboptions:
      serial:
        description: Serial number of the Hitachi storage system.
        type: str
        required: true
"""

EXAMPLES = """

- name: Retrieve resource information about a specific subscriber
  hv_gateway_subscription_facts:
    connection_info:
      address: gateway.company.com
      api_token: "eyJhbGciOiJS......"
      connection_type: "gateway"
      subscriber_id: "1234"
    storage_system_info:
      serial: "50015"
"""

RETURN = """
data:
  description: List of subscribers belonging to partner apiadmin.
  returned: success
  type: list
  elements: dict
  sample: [
    {
        "resource_value": "CL1-A",
        "storage_serial": "50015",
        "subscriber_id": "12345",
        "type": "Port"
    },
    {
        "resource_value": "5015",
        "storage_serial": "50015",
        "subscriber_id": "12345",
        "total_capacity": 1073741824,
        "type": "Volume"
    }
  ]
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.uaig_utils import (
    GatewayArguments,
    GatewayParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.uaig_subscriber_resource_reconciler import (
    SubscriberResourceReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class SubscriberResourceFactsManager:
    def __init__(self):
        self.logger = Log()
        self.argument_spec = GatewayArguments().get_subscription_fact()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:
            self.params_manager = GatewayParametersManager(self.module.params)
            self.connection_info = self.params_manager.connection_info
            self.storage_serial_number = self.params_manager.storage_system_info.serial
        except Exception as e:
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Gateway Subscriber Facts ===")
        registration_message = validate_ansible_product_registration()
        subscriber_data = None
        self.logger.writeInfo(
            f"{self.params_manager.connection_info.connection_type} connection type"
        )
        try:
            subscriber_data = SubscriberResourceReconciler(
                self.connection_info, self.storage_serial_number
            ).get_subscriber_resource_facts()

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
    obj_store = SubscriberResourceFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
