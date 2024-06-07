from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hv_gateway_admin_password
short_description: Update password of gateway admin on Hitachi VSP storage systems.
description:
  - This module updates the password of gateway admin.
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
      uai_gateway_address:
        description: IP address or hostname of UAI gateway.
        type: str
        required: true
      api_token:
        description: Token value to access UAI gateway (required for authentication either 'username,password' or api_token).
        type: str
        required: true
  spec:
    description: Specification for updating admin password.
    type: dict
    required: false
    suboptions:
      password:
        type: str
        description: The new password value to be updated.
        required: true
'''

EXAMPLES = '''
- name: Update password of UAI gateway admin
  hv_gateway_admin_password:      
    connection_info:
      uai_gateway_address: gateway.company.com
      api_token: "eyJhbGciOiJS......"

    spec:
      password: "changeMe!"
'''

RETURN = '''
data:
  description: Indicates whether gateway admin password task completed successfully or not.
  returned: success
  type: str
  sample:
    - "Sucessfully updated apiadmin password"
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

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.uaig_password_reconciler import (
    GatewayPasswordReconciler,
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


logger = Log()

try:
    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log


class GatewayPasswordManager:
    def __init__(self):

        self.argument_spec = GatewayArguments().gateway_password()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )
        c_info = self.module.params.get("connection_info")
        logger.writeInfo(
            f"{c_info} module_params_connection_info"
        )
        field = c_info.pop("uai_gateway_address")
        c_info["address"] = field
        c_info["connection_type"] = "gateway"
        self.params_manager = GatewayParametersManager(self.module.params)
        self.connection_info = self.params_manager.get_connection_info()
        self.state = self.params_manager.get_state()
        logger.writeInfo(f"State: {self.state}")
        self.spec = self.params_manager.set_admin_password_spec()

    def apply(self):

        logger.writeInfo(
            f"{self.params_manager.connection_info.connection_type} connection type"
        )
        try:

            if not self.state:
                data = GatewayPasswordReconciler(
                    self.params_manager.connection_info
                ).gateway_password(self.spec)
            elif self.state == StateValue.PRESENT:
                data = GatewayPasswordReconciler(
                    self.params_manager.connection_info
                ).gateway_password(self.spec)
            else:
                data = "Absent operation is not supported"
            if "Sucessfully updated apiadmin password" in data:
                self.connection_info.changed = True

        except Exception as e:
            self.module.fail_json(msg=str(e))

        response = {"changed": self.connection_info.changed, "data": data}

        self.module.exit_json(**response)


def main():
    """
    Create AWS FSx class instance and invoke apply
    :return: None
    """
    obj_store = GatewayPasswordManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
