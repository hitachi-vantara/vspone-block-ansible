from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hv_gateway_subscriber_fact
short_description: Retrieves information about subscriber on Hitachi VSP storage systems.
description:
  - This module retrieves information about subscriber.
  - It provides details about a subscriber such as name, ID and other relevant information.
version_added: '3.0.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.0.0
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
      username:
        description: Username for authentication.
        type: str
        required: false
      password:
        description: Password for authentication.
        type: str
        required: false
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
  spec:
    description: Specification for retrieving subscriber information.
    type: dict
    suboptions:
      subscriber_id:
        type: str
        description: ID of the specific subscriber to retrieve information for (Works only for gateway connection type).
        required: false
'''

EXAMPLES = '''
- name: Retrieve information about all subscribers
  hv_gateway_subscriber_fact:         
    connection_info:
      address: gateway.company.com
      api_token: "eyJhbGciOiJS......"
      connection_type: "gateway"
      subscriber_id: ""

    spec:
      subscriber_id: ""

- name: Retrieve information about a specific subscriber
  hv_gateway_subscriber_fact:       
    connection_info:
      address: gateway.company.com
      api_token: "eyJhbGciOiJS......"
      connection_type: "gateway"
      subscriber_id: "sub1234"

    spec:
      subscriber_id: "sub1234"
'''

RETURN = '''
data:
  description: List of subscribers belonging to partner apiadmin.
  returned: success
  type: list
  elements: dict
  sample: [
    {
        "hard_limit_in_percent": "90",
        "message": "",
        "name": "TestSubscriber",
        "partner_id": "apiadmin",
        "quota_limit_in_gb": "90",
        "soft_limit_in_percent": "80",
        "state": "NORMAL",
        "subscriber_id": "12345",
        "time": 1716260209,
        "type": "subscriber",
        "used_quota_in_gb": "0.1953125",
        "used_quota_in_percent": 0.2170139
    }
  ]
'''


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.uaig_utils import (
    GatewayArguments,
    GatewayParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    StateValue,
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    camel_array_to_snake_case,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.uaig_subscriber_reconciler import (
    SubscriberReconciler,
)


try:
    from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_logger import (
        MessageID,
    )

    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_exceptions import (
    HiException,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log


logger = Log()

try:
    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log


class SubscriberFactsManager:
    def __init__(self):

        self.argument_spec = GatewayArguments().get_subscriber_fact()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )

        self.params_manager = GatewayParametersManager(self.module.params)
        self.spec = self.params_manager.set_subscriber_fact_spec()

    def apply(self):

        subscriber_data = None
        logger.writeInfo(
            f"{self.params_manager.connection_info.connection_type} connection type"
        )
        try:

            subscriber_data = SubscriberReconciler(
                self.params_manager.connection_info
            ).get_subscriber_facts(self.params_manager.spec)

        except Exception as e:
            self.module.fail_json(msg=str(e))

        self.module.exit_json(data=subscriber_data)


def main():
    """
    Create AWS FSx class instance and invoke apply
    :return: None
    """
    obj_store = SubscriberFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
