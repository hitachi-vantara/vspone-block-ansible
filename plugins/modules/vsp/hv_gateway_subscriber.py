#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_gateway_subscriber
short_description: Manages subscribers of a partner on Hitachi VSP storage systems.
description:
  - This module allows for the creation, updating and deletion of subscribers.
  - It supports various subscriber operations based on the specified task level.
  - This module is supported only for gateway connection type.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/subscriber.yml)
version_added: '3.0.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
options:
  state:
    description: The level of the subscriber task. Choices are 'present', 'absent'.
    type: str
    required: false
    choices: ['present', 'absent']
    default: 'present'
  connection_info:
    description: Information required to establish a connection to the storage system.
    required: true
    type: dict
    suboptions:
      address:
        description: IP address or hostname of UAI gateway.
        type: str
        required: true
      username:
        description: Username for authentication.This field is valid for direct connection type only, and it is a required field.
          Not required for this module.
        type: str
        required: false
      password:
        description: Password for authentication.This field is valid for direct connection type only, and it is a required field.
          Not required for this module.
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
    description: Specification for the subscriber task.
    type: dict
    required: true
    suboptions:
      subscriber_id:
        description: The subscriber ID can be 1 to 15 characters long and must include numbers from 0 to 9.
        type: str
        required: true
      name:
        description: Name of the subscriber.
        type: str
        required: false
      soft_limit:
        description: Soft limit in percent for the subscriber. Default is 80.
        type: str
        required: false
      hard_limit:
        description: Hard limit in percent for the subscriber. Default is 90.
        type: str
        required: false
      quota_limit:
        description: Quota limit for the subscriber.
        type: str
        required: false
      description:
        description: Description of the subscriber.
        type: str
        required: false
"""

EXAMPLES = """
- name: Create a subscriber
  hv_gateway_subscriber:
    state: present
    connection_info:
      address: gateway.company.com
      api_token: "eyJhbGciOiJS......"
      connection_type: "gateway"
    spec:
      subscriber_id: "12345"
      name: "Testsub123"
      soft_limit: "70"
      hard_limit: "80"
      quota_limit: "20"

- name: Delete a subscriber
  hv_gateway_subscriber:
    state: absent
    connection_info:
      address: gateway.company.com
      api_token: "eyJhbGciOiJS......"
      connection_type: "gateway"
    spec:
      subscriber_id: "12345"

- name: Update a subscriber
  hv_gateway_subscriber:
    state: present
    connection_info:
      address: gateway.company.com
      api_token: "eyJhbGciOiJS......"
      connection_type: "gateway"
    spec:
      subscriber_id: "12345"
      quota_limit: "30"
"""

RETURN = """
data:
  description: Newly created subscriber object.
  returned: success
  type: dict
  elements: dict
  sample:
    {
        "hard_limit_in_percent": "80",
        "message": "",
        "name": "Test1234",
        "partner_id": "apiadmin",
        "quota_limit_in_gb": "20",
        "soft_limit_in_percent": "70",
        "state": "",
        "subscriber_id": "1234",
        "time": 1716272732,
        "type": "subscriber",
        "used_quota_in_gb": "",
        "used_quota_in_percent": -1
    }
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.uaig_utils import (
    GatewayArguments,
    GatewayParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    StateValue,
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


class SubscriberManager:
    def __init__(self):
        self.logger = Log()
        self.argument_spec = GatewayArguments().gateway_subscriber()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:
            self.params_manager = GatewayParametersManager(self.module.params)
            self.state = self.params_manager.get_state()
            self.connection_info = self.params_manager.get_connection_info()
            self.logger.writeInfo(f"State: {self.state}")

        except Exception as e:
            self.logger.writeError(f"An error occurred during initialization: {str(e)}")
            self.module.fail_json(msg=str(e))

    def apply(self):
        registration_message = validate_ansible_product_registration()
        subscriber_data = None
        reconciler = SubscriberReconciler(self.params_manager.connection_info)
        self.params_manager.set_subscriber_fact_spec()
        try:
            self.logger.writeInfo("=== Start of Gateway Subscriber operation ===")
            if self.state == StateValue.PRESENT:
                if not self.params_manager.spec.subscriber_id:
                    subscriber_data = "Subscriber ID is missing."
                else:

                    existing_subscriber = None
                    try:
                        #  we are getting exception now, hence this try-catch
                        existing_subscriber = reconciler.get_subscriber_facts(
                            self.params_manager.spec
                        )
                    except Exception as e:
                        self.logger.writeError(
                            f"Caught exception implies subscriber not found, go ahead with create: {e}"
                        )

                    if not existing_subscriber or len(existing_subscriber) == 0:
                        self.spec = self.params_manager.set_subscriber_spec("present")
                        subscriber_data = reconciler.create_subscriber(self.spec)
                        if subscriber_data:
                            self.connection_info.changed = True
                    else:
                        self.spec = self.params_manager.set_subscriber_spec("update")
                        subscriber_data = reconciler.update_subscriber(
                            self.spec, existing_subscriber[0]
                        )
                        if subscriber_data:
                            same_data = self.is_both_subscriber_data_same(
                                existing_subscriber[0], subscriber_data
                            )
                            self.connection_info.changed = not same_data
            elif self.state == StateValue.ABSENT:
                self.spec = self.params_manager.set_subscriber_spec("absent")
                subscriber_data = reconciler.delete_subscriber(self.spec)
                if "Subscriber deleted successfully" in subscriber_data:
                    self.connection_info.changed = True
        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of Gateway Subscriber operation ===")
            self.module.fail_json(msg=str(e))

        response = {"changed": self.connection_info.changed, "data": subscriber_data}
        if registration_message:
            response["user_consent_required"] = registration_message
        self.logger.writeInfo(f"{response}")
        self.logger.writeInfo("=== End of Gateway Subscriber operation ===")
        self.module.exit_json(**response)

    def is_both_subscriber_data_same(self, existing, returned):
        if len(existing) != len(returned):
            return False
        else:
            for i in existing:
                if i == "time":
                    continue
                if existing.get(i) != returned.get(i):
                    return False
            return True


def main(module=None):

    obj_store = SubscriberManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
