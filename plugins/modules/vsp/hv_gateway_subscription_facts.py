from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hv_gateway_subscription_facts
short_description: Retrieves information about subscriber on Hitachi VSP storage systems.
description:
  - This module retrieves information about subscriber.
  - It provides details about a subscriber such as name, ID and other relevant information.
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
'''

EXAMPLES = '''

- name: Retrieve resource information about a specific subscriber
  hv_gateway_subscription_facts:       
    connection_info:
      address: gateway.company.com
      api_token: "eyJhbGciOiJS......"
      connection_type: "gateway"
      subscriber_id: "1234"

    storage_system_info:
      serial: "50015"
'''

RETURN = '''
data:
  description: List of subscribers belonging to partner apiadmin.
  returned: success
  type: list
  elements: dict
  sample: [
    {
        "resource_value": "CL1-A",
        "storage_serial": "810045",
        "subscriber_id": "12345",
        "type": "Port"
    },
    {
        "resource_value": "5015",
        "storage_serial": "810050",
        "subscriber_id": "12345",
        "total_capacity": 1073741824,
        "type": "Volume"
    }
  ]
'''


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.uaig_utils import (
    GatewayArguments,
    GatewayParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.uaig_subscriber_resource_reconciler import (
    SubscriberResourceReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log

logger = Log()

class SubscriberResourceFactsManager:
    def __init__(self):

        self.argument_spec = GatewayArguments().get_subscription_fact()
        logger.writeInfo(
            f"Argument spec : {self.argument_spec}"
        )
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )

        self.params_manager = GatewayParametersManager(self.module.params)
        self.connection_info = self.params_manager.connection_info
        self.storage_serial_number = self.params_manager.storage_system_info.serial

    def apply(self):

        subscriber_data = None
        logger.writeInfo(
            f"{self.params_manager.connection_info.connection_type} connection type"
        )
        try:
            subscriber_data = SubscriberResourceReconciler(
                self.connection_info, self.storage_serial_number
            ).get_subscriber_resource_facts()

        except Exception as e:
            self.module.fail_json(msg=str(e))

        self.module.exit_json(data=subscriber_data)


def main():
    """
    Create AWS FSx class instance and invoke apply
    :return: None
    """
    obj_store = SubscriberResourceFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()