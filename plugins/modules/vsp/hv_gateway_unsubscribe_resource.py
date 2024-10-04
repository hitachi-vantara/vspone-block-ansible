from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hv_gateway_unsubscribe_resource
short_description: Manages un-subscription of resources for a subscriber on Hitachi VSP storage systems.
description:
  - This module unsubscribes different resources for a subscriber.
version_added: '3.1.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.1.0
requirements:
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
        required: true
        choices: ['gateway']
      subscriber_id:
        description: Subscriber ID for multi-tenancy (required for "gateway" connection type).
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway (required for authentication either 'username,password' or api_token).
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
  spec:
    description: Specification for the un-subscription task.
    type: dict
    required: true
    suboptions:
      resources:
        description: Resources information that to be unsubscribed.
        type: list
        required: true 
'''

EXAMPLES = '''

- name: Try to unsubscribe listed resources
  hv_gateway_subscription_facts:
    connection_info:
      address: gateway.company.com
      api_token: "eyJhbGciOiJS......"
      connection_type: "gateway"
      subscriber_id: "1234"

    spec:
      resources:
        - type: "hostgroup"
          values: ["test-001", "test-005"]
        - type : "volume"
            values : ["5015", "5016"]
        - type : "port"
            values : ["CL5-A", "CL1-A"]
'''

RETURN = '''
data:
  description: List of failure and success tasks for the un-subscription try.
  returned: success
  type: list
  elements: dict
  sample: [
        "error": [
            "Did not find Host Group test-001.",
            "Unable to untag Host Group test-005 from subscriber 12345 since it is already attached to volumes.",
            "Failed to untag storage volume 5015 from subscriber 12345 as it is tagged to a host group or iSCSI target",
            "Failed to untag storage volume 5016 from subscriber 12345 as it is tagged to a host group or iSCSI target",
            "Host group is present in Port CL5-A that tagged to the subscriber 12345",
            "Did not find Port with ID CL1-A.",
            "Storage is not registered",
            "Resource not found",
            "Unable to find the resource. localpair-6764f2c78f8f53a1766ad716a65206f8."
        ],
        "info": [
            "Found 1 Host Group(s) called test-005. ",
            "Found Volume with LDEV ID 5015. ",
            "Found Volume with LDEV ID 5016. ",
            "Found Port with ID CL5-A. ",
            "Found shadowimage with ID localpair-6764f2c78f8f53a1766ad716a65206f7. "
        ]
  ]
'''
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPUnsubscriberArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_unsubscriber import (
    VSPUnsubscriberReconciler,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log


from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log_decorator import (
    LogDecorator,
)

logger = Log()
@LogDecorator.debug_methods
class UnsubscriberManager:

    def __init__(self):
        try:
            self.argument_spec = VSPUnsubscriberArguments().unsubscribe()

            self.module = AnsibleModule(
                argument_spec=self.argument_spec,
                supports_check_mode=True,
                # can be added mandotary , optional mandatory arguments
            )

            self.params_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.params_manager.connection_info
            self.storage_serial_number = self.params_manager.storage_system_info.serial
            self.spec = self.params_manager.unsubscribe_spec()
            self.state = self.params_manager.get_state()

        except Exception as e:
            logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        data = None
        logger.writeDebug(
            f"Spec = {self.spec}"
        )
        logger.writeDebug("state = {}", self.state)
        try:

            err, data = self.unsubscribe_module()

        except Exception as e:
            self.module.fail_json(msg=str(e))

        resp = {
                "changed": self.connection_info.changed,
                "info": data, 
                "error" : err,
                "msg": "Un-subscription tasks completed.",
            }
        self.module.exit_json(**resp)

    def unsubscribe_module(self):
 
        reconciler = VSPUnsubscriberReconciler(
            self.connection_info,
            self.storage_serial_number,
            self.state
        )
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            found = reconciler.check_storage_in_ucpsystem()
            if not found:
                self.module.fail_json(
                    "The storage system is still onboarding or refreshing, Please try after sometime"
                )

        result = reconciler.unsubscribe(self.spec)
        return result


def main():
    obj_store = UnsubscriberManager()
    obj_store.apply()


if __name__ == "__main__":
    main()