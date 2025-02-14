#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_remote_copy_group_facts
short_description: Retrieves Copy Groups information from Hitachi VSP storage systems.
description:
  - This module retrieves information about Copy Groups from Hitachi VSP storage systems.
  - This module is supported only for direct connection type.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/remote_copy_group_facts.yml)
version_added: '3.2.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
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
  connection_info:
    description: Information required to establish a connection to the storage system.
    type: dict
    required: true
    suboptions:
      address:
        description: IP address or hostname of storage system.
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
      api_token:
        description: Value of the lock token to operate on locked resources.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system. Only direct connection is supported.
        type: str
        required: false
        choices: ['direct', 'gateway']
        default: 'direct'
      subscriber_id:
        description: >
          Subscriber ID is required for gateway connection type to support multi-tenancy. Not needed for direct connection or
          for gateway connection with single tenant. Not needed for this operation.
        type: str
        required: false
  secondary_connection_info:
    description: Information required to establish a connection to the secondary storage system.
    required: true
    type: dict
    suboptions:
      address:
        description: IP address or hostname of storage system.
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
      api_token:
        description: Value of the lock token to operate on locked resources.
        type: str
        required: false
  spec:
    description:
      - Specification for the Copy Group facts to be gathered.
    type: dict
    required: false
    suboptions:
      name:
        description:
          - The copy group name. If not provided, list of all copy groups will be returned.
        type: str
        required: false
      should_include_remote_replication_pairs:
        description:
          - Whether we want to get all replication pairs from a specific copy group. Should be specified along with the 'name' parameter in spec
        type: bool
        required: false
"""

EXAMPLES = """
- name: Get all Copy Groups for direct connection
  hv_copy_group_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"

- name: Get one Copy Group for direct connection
  hv_copy_group_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    spec:
      name: "copygroup1"

- name: Get one Copy Group detail for direct connection
  hv_copy_group_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    spec:
      name: "copygroup1"
      should_include_remote_replication_pairs: true
"""

RETURN = """
copygroups:
  description: A list of copy groups gathered from the storage system.
  returned: always
  type: list
  elements: dict
  sample:
    {
        "copy_group_name": "copygroup1",
        "local_device_group_name": "copygroup1P_",
        "mirror_unit_id": 0,
        "remote_device_group_name": "copygroup1S_",
        "remote_mirror_copy_group_id": "A34000811112,copygroup1,copygroup1P_,copygroup1S_",
        "remote_storage_device_id": "A34000811112",
        "storage_serial_number": "8101111"
    }
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_copy_groups import (
    VSPCopyGroupsReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPCopyGroupsArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class VSPCopyGroupsFactsManager:
    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPCopyGroupsArguments().copy_groups_facts()

        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        self.parameter_manager = VSPParametersManager(self.module.params)
        self.connection_info = self.parameter_manager.get_connection_info()
        self.storage_serial_number = self.parameter_manager.get_serial()
        self.spec = self.parameter_manager.get_copy_groups_fact_spec()
        self.spec.copy_group_name = self.spec.name
        self.state = self.parameter_manager.get_state()
        self.secondary_connection_info = (
            self.parameter_manager.get_secondary_connection_info()
        )

    def apply(self):
        self.logger.writeInfo("=== Start of Remote Copy Group Facts ===")

        registration_message = validate_ansible_product_registration()
        try:
            reconciler = VSPCopyGroupsReconciler(
                self.connection_info,
                self.storage_serial_number,
                self.state,
                self.secondary_connection_info,
            )

            copy_groups = reconciler.get_remote_copy_groups_facts(self.spec)
            msg = ""

            if (
                self.spec.copy_group_name is not None
                and self.spec.should_include_remote_replication_pairs is True
            ):
                if "copy_pairs" not in copy_groups:
                    msg = "Copy pair information not available for copy group {} as operations cannot be performed for this copy group".format(
                        self.spec.copy_group_name
                    )
                elif copy_groups is not None:
                    msg = "Remote copy group information along with copy pairs retrieved successfully"
            elif self.spec.copy_group_name is not None and copy_groups is not None:
                msg = "Remote copy group information retrieved successfully"
            elif copy_groups is not None:
                msg = "Remote copy groups retrieved successfully"
            self.logger.writeDebug(
                f"MOD:hv_copy_group_facts:copy_groups= {copy_groups}"
            )

        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of Remote Copy Group Facts ===")
            self.module.fail_json(msg=str(e))
        data = {"remote_copy_groups": copy_groups, "msg": msg}
        if registration_message:
            data["user_consent_required"] = registration_message

        self.logger.writeInfo(f"{data}")
        self.logger.writeInfo("=== End of Remote Copy Group Facts ===")
        self.module.exit_json(**data)


def main(module=None):
    obj_store = VSPCopyGroupsFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
