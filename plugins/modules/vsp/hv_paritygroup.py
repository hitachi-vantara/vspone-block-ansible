#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_paritygroup
short_description: Create, delete parity group from Hitachi VSP storage systems.
description:
  - This module creates, delete parity group from Hitachi VSP storage systems. This is only supported for direct connection.
  - This module is supported only for direct connection to the storage system.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/paritygroup.yml)
version_added: '3.2.0'
author:
  - Hitachi Vantara, LTD. (@hitachi-vantara)
options:
  storage_system_info:
    description:
      - Information about the storage system.
    type: dict
    required: false
    suboptions:
      serial:
        description:
          - The serial number of the storage system.
        type: str
        required: false
  state:
    description: The level of the HUR pairs task. Choices are 'present', 'absent', 'update'.
    type: str
    required: false
    choices: ['present', 'absent', 'update']
    default: 'present'
  connection_info:
    description: Information required to establish a connection to the storage system.
    type: dict
    required: true
    suboptions:
      address:
        description: IP address or hostname of either the UAI gateway (if connection_type is gateway) or the storage system (if connection_type is direct).
        type: str
        required: true
      username:
        description: Username for authentication. This field is valid for direct connection type only, and it is a required field.
        type: str
        required: false
      password:
        description: Password for authentication. This field is valid for direct connection type only, and it is a required field.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['gateway', 'direct']
        default: 'direct'
      subscriber_id:
        description: This field is valid for gateway connection type only. This is an optional field and only needed to support multi-tenancy environment.
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway. This is a required field for gateway connection type.
        type: str
        required: false
  spec:
    description:
      - Specification for the parity group facts to be gathered.
    type: dict
    required: false
    suboptions:
      parity_group_id:
        description:
          - The parity group number of the parity group to retrieve.
        type: str
        required: false
      drive_location_ids:
        description:
          - Specify the locations of the drives to be used to create to the parity group.
        type: list
        elements: str
        required: false
      raid_type:
        description:
          - RAID type.
        type: str
        required: false
      is_encryption_enabled:
        description:
          - Specify whether to enable the encryption function for the parity group.
        type: bool
        required: false
      is_copy_back_mode_enabled:
        description:
          - Specify whether to enable the encryption function for the parity group.
        type: bool
        required: false
      is_accelerated_compression_enabled:
        description:
          - Specify whether to enable accelerated compression for the parity group.
        type: bool
        required: false
      clpr_id:
        description:
          - Specify a CLPR number in the range from 0 to 31.
        type: int
        required: false
"""

EXAMPLES = """
- name: Create parity group
  tasks:
    - hv_paritygroup:
        connection_info:
          address: storage1.company.com
          username: "admin"
          password: "secret"
        storage_system_info:
          - serial: "811150"
        state: "present"
        spec:
          parity_group_id: 1-10
          drive_location_ids: ["0-16", "0-17", "0-18", "0-19"]
          raid_type: 3D+1P
          is_encryption_enabled: true
          is_copy_back_mode_enabled: false
          is_accelerated_compression_enabled: true
          clpr_id: 1

- name: Delete parity group
  tasks:
    - hv_paritygroup:
        connection_info:
          address: storage1.company.com
          username: "admin"
          password: "secret"

        storage_system_info:
          - serial: "811150"

        state: "absent"
        spec:
          parity_group_id: 1-10

- name: Update parity group
  tasks:
    - hv_paritygroup:
        connection_info:
          address: storage1.company.com
          username: "admin"
          password: "secret"

        storage_system_info:
          - serial: "811150"

        state: "update"
        spec:
          parity_group_id: 1-10
          is_accelerated_compression_enabled: true
"""

RETURN = """
parity_group:
  description: Parity group managed by the module.
  returned: success
  type: list
  elements: dict
  sample: [
  {
    "clpr_id": 0,
    "copyback_mode": false,
    "drive_type": "SSD",
    "free_capacity": "5.16TB",
    "is_accelerated_compression": false,
    "is_encryption_enabled": true,
    "is_pool_array_group": null,
    "ldev_ids": [],
    "parity_group_id": "1-10",
    "raid_level": "RAID5",
    "resource_group_id": null,
    "resource_id": null,
    "status": null,
    "total_capacity": "5.16TB"
  }
  ]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_parity_group,
)

try:

    HAS_MESSAGE_ID = True
except ImportError:
    HAS_MESSAGE_ID = False

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPParametersManager,
    VSPParityGroupArguments,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    camel_dict_to_snake_case,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class VSPParityGroupManager:
    def __init__(self):
        self.logger = Log()

        self.argument_spec = VSPParityGroupArguments().parity_group()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.get_parity_group_spec()
            self.serial = self.params_manager.get_serial()
            self.state = self.params_manager.get_state()
            self.connection_info = self.params_manager.get_connection_info()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Parity Group operation ===")
        registration_message = validate_ansible_product_registration()
        try:
            result = vsp_parity_group.VSPParityGroupReconciler(
                self.params_manager.connection_info, self.state
            ).parity_group_reconcile(self.state, self.spec)

            # if result is not None and result is not str:
            #   snake_case_parity_group_data = camel_dict_to_snake_case(result.to_dict())
            msg_state = ""
            if self.state == "present":
                msg_state = "Parity group created successfully."
            elif self.state == "update":
                msg_state = "Parity group updated successfully."
            msg = result if isinstance(result, str) else msg_state

            snake_case_parity_group_data = {}
            if not isinstance(result, str):
                parity_group_dict = result.to_dict()
                parity_group_data_extracted = vsp_parity_group.VSPParityGroupCommonPropertiesExtractor().extract_parity_group(
                    parity_group_dict
                )
                snake_case_parity_group_data = camel_dict_to_snake_case(
                    parity_group_data_extracted
                )

            response_dict = {
                "changed": self.connection_info.changed,
                "data": snake_case_parity_group_data,
                "msg": msg,
            }
            if registration_message:
                response_dict["user_consent_required"] = registration_message

            self.logger.writeInfo(f"{response_dict}")
            self.logger.writeInfo("=== End of Parity Group operation ===")
            self.module.exit_json(**response_dict)
        except Exception as ex:
            self.logger.writeException(ex)
            self.logger.writeInfo("=== End of Parity Group operation ===")
            self.module.fail_json(msg=str(ex))


def main():
    obj_store = VSPParityGroupManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
