#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
  module: hv_truecopy_facts
  short_description: Retrieves TrueCopy pairs information from Hitachi VSP storage systems.
  description:
    - This module retrieves the TrueCopy pairs information from Hitachi VSP storage systems.
    - This module is supported for both direct and gateway connection types.
    - For direct connection type examples, go to URL
      U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/truecopy_facts.yml)
    - For gateway connection type examples, go to URL
      U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/truecopy_facts.yml)
  version_added: '3.1.0'
  author:
    - Hitachi Vantara LTD (@hitachi-vantara)
  options:
    storage_system_info:
      description:
        - Information about the Hitachi storage system.
      type: dict
      required: false
      suboptions:
        serial:
          description:
            - Serial number of the Hitachi storage system.
          type: str
          required: false
    secondary_connection_info:
      description: >
        Information required to establish a connection to the secondary storage system. Required for direct connection only.
        Not needed for gateway connection.
      required: false
      type: dict
      suboptions:
        address:
          description:
            - IP address or hostname of either the UAI gateway or Hitachi storage system.
          type: str
          required: true
        username:
          description:
            - Username for authentication. This field is valid for direct connection type only, and it is a required field.
          type: str
          required: false
        password:
          description:
            - Password for authentication. This field is valid for direct connection type only, and it is a required field.
          type: str
          required: false
        api_token:
          description:
            - This fieild is used to pass the value of the lock token of the secondary storage to operate on locked resources.
          type: str
          required: false
    connection_info:
      description:
        - Information required to establish a connection to the storage system.
      type: dict
      required: true
      suboptions:
        address:
          description:
            - IP address or hostname of either the UAI gateway or Hitachi storage system.
          type: str
          required: true
        username:
          description:
            - Username for authentication. Required for direct connection. Not needed for gateway connection as it uses API token.
          type: str
          required: false
        password:
          description:
            - Password for authentication. Required for direct connection. Not needed for gateway connection as it uses API token.
          type: str
          required: false
        connection_type:
          description:
            - Type of connection to the storage system. Two types of connections are supported, 'direct' and 'gateway'.
          type: str
          required: false
          choices:
            - direct
            - gateway
          default: direct
        api_token:
          description:
            - Token value to access UAI gateway for gateway connection..
          type: str
          required: false
        subscriber_id:
          description: >
            Subscriber ID is required for gateway connection type to support multi-tenancy. Not needed for direct connection or
            for gateway connection with single tenant.
          type: str
          required: false
    spec:
      description:
        - Specification for retrieving TrueCopy pair information.
      type: dict
      required: false
      suboptions:
        primary_volume_id:
          description:
            - ID of the primary volume to retrieve TrueCopy pair information for.
          type: int
          required: false
        secondary_volume_id:
          description:
            - ID of the secondary volume to retrieve TrueCopy pair information for.
          type: int
          required: false
        copy_group_name:
          description:
            - Name of the copy group to retrieve TrueCopy pair information for. Used only for direct connection.
          type: str
          required: false
        copy_pair_name:
          description:
            - Name of the copy pair to retrieve TrueCopy pair information for. Used only for direct connection.
          type: str
          required: false
        local_device_group_name:
          description:
            - Name of the local device group to retrieve TrueCopy pair information for. Used only for direct connection.
          type: str
          required: false
        remote_device_group_name:
          description:
            - Name of the remote device group to retrieve TrueCopy pair information for. Used only for direct connection.
          type: str
          required: false
"""

EXAMPLES = """
- name: Get all TrueCopy pairs for direct connection
  hv_truecopy_facts:
    storage_system_info:
      serial: "811150"
    connection_info:
      address: gateway.company.com
      username: "admin"
      password: "password"

- name: Get all TrueCopy pairs for gateway connection for a specific subscriber
  hv_truecopy_facts:
    storage_system_info:
      serial: "811150"
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: 12345

- name: Retrieve TrueCopy pair information for a specific volume for direct connection
  hv_truecopy_facts:
    storage_system_info:
      serial: "811150"
    connection_info:
      address: gateway.company.com
      username: "admin"
      password: "password"
    spec:
      primary_volume_id: 123

- name: Retrieve TrueCopy pair information for a specific volume for gateway connection
  hv_truecopy_facts:
    storage_system_info:
      serial: "811150"
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: 12345
    spec:
      primary_volume_id: 123
"""

RETURN = """
truecopy_pairs:
  description: a list of TrueCopy pairs information for gateway connection.
  returned: always
  type: list
  elements: dict
  sample: [
    {
      "consistency_group_id": -1,
      "copy_rate": 100,
      "entitlement_status": "unassigned",
      "mirror_unit_id": 0,
      "pair_name": "",
      "partner_id": "apiadmin",
      "primary_hex_volume_id": "00:05:01",
      "primary_volume_id": 1281,
      "primary_volume_storage_id": 810050,
      "resource_id": "replpair-037f68f4f56351b2de6a68ff5dc0cdeb",
      "secondary_hex_volume_id": "00:00:82",
      "secondary_volume_id": 130,
      "secondary_volume_storage_id": 810045,
      "status": "PSUS",
      "storage_id": "storage-b2c93d5e8fadb70b208341b0e19c6527",
      "storage_serial_number": "810050",
      "svol_access_mode": "READWRITE",
      "type": "truecopypair"
    }
  ]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_true_copy import (
    VSPTrueCopyReconciler,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPTrueCopyArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.message.module_msgs import (
    ModuleMessage,
)


class VSPTrueCopyFactsManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = VSPTrueCopyArguments().true_copy_facts()
        self.logger.writeDebug(
            f"MOD:hv_truecopy_facts:argument_spec= {self.argument_spec}"
        )
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        self.parameter_manager = VSPParametersManager(self.module.params)
        self.connection_info = self.parameter_manager.get_connection_info()
        self.storage_serial_number = self.parameter_manager.storage_system_info.serial
        self.spec = self.parameter_manager.get_true_copy_fact_spec()
        self.state = self.parameter_manager.get_state()
        self.secondary_connection_info = (
            self.parameter_manager.get_secondary_connection_info()
        )

        self.spec.secondary_connection_info = self.secondary_connection_info
        # self.logger.writeDebug(f"MOD:hv_truecopy_facts:spec= {self.spec}")

    def apply(self):

        self.logger.writeInfo("=== Start of TrueCopy Facts ===")
        registration_message = validate_ansible_product_registration()
        try:
            reconciler = VSPTrueCopyReconciler(
                self.connection_info, self.storage_serial_number, self.state
            )
            if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
                oob = reconciler.is_out_of_band()
                self.logger.writeDebug(f"oob = {oob}")
                if oob is True:
                    raise ValueError(ModuleMessage.OOB_NOT_SUPPORTED.value)

            tc_pairs = reconciler.get_true_copy_facts(self.spec)
            self.logger.writeDebug(f"MOD:hv_truecopy_facts:tc_pairs= {tc_pairs}")

        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of TrueCopy Facts ===")
            self.module.fail_json(msg=str(e))

        data = {
            "truecopy_pairs": tc_pairs,
        }
        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo(f"{data}")
        self.logger.writeInfo("=== End of TrueCopy Facts ===")
        self.module.exit_json(**data)


def main(module=None):
    obj_store = VSPTrueCopyFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
