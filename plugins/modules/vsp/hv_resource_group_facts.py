#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_resource_group_facts
short_description: Retrieves resource group information from Hitachi VSP storage systems.
description:
    - This module retrieves information about resource groups from Hitachi VSP storage systems.
    - This module is supported for both C(direct) and C(gateway) connection types.
    - For C(direct) connection type examples, go to URL
      U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/resource_group_facts.yml)
    - For C(gateway) connection type examples, go to URL
      U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/resource_group_facts.yml)
version_added: '3.2.0'
author:
    - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.8
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: full
options:
    storage_system_info:
        description:
          - Information about the storage system. This field is required for gateway connection type only.
        type: dict
        required: false
        suboptions:
            serial:
                description: The serial number of the storage system.
                type: str
                required: false
    connection_info:
        description: Information required to establish a connection to the storage system.
        type: dict
        required: true
        suboptions:
            address:
                description: IP address or hostname of either the UAI gateway (if connection_type is C(gateway))
                  or the storage system (if connection_type is C(direct)).
                type: str
                required: true
            username:
                description: Username for authentication. This field is valid for C(direct) connection type only, and it is a required field.
                type: str
                required: false
            password:
                description: Password for authentication. This field is valid for C(direct) connection type only, and it is a required field.
                type: str
                required: false
            connection_type:
                description: Type of connection to the storage system. Two types of connection are supported, C(direct) and C(gateway).
                type: str
                required: false
                choices: ['gateway', 'direct']
                default: 'direct'
            api_token:
                description: API token for the C(gateway) connection or value of the lock token to operate on locked resources for C(direct) connection.
                type: str
                required: false
    spec:
        description: Specification for the resource group facts to be gathered.
        type: dict
        required: false
        suboptions:
            name:
                description: The name of the specific resource group to retrieve.
                type: str
                required: false
            id:
                description: The id of the specific resource group to retrieve.
                type: int
                required: false
            is_locked:
                description: >
                    If this field is not present, all resource groups will be retrieved.
                    If this field is true, only the locked resource groups will be retrieved.
                    If this field is false, only the unlocked resource groups will be retrieved.
                type: bool
                required: false
            query:
                description: >
                    The field allows to query resource groups for different types of resources.
                    Types of resources are: ldevs, parity_groups, ports, host_groups, iscsi_targets, nvm_subsystem_ids, and storage_pool_ids.
                    If this field is not present, all resources information of the resource group will be retrieved except storage_pool_ids.
                    When storage_pool_ids is present, all the ldevs that constitute the storage pool will be included in the response under the ldevs field.
                type: list
                required: false
                elements: str
"""

EXAMPLES = """
- name: Get all Resource Groups for direct connection type
  hitachivantara.vspone_block.vsp.hv_resource_group_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"

- name: Get all Resource Groups for gateway connection types
  hitachivantara.vspone_block.vsp.hv_resource_group_facts:
    storage_system_info:
      serial: "811150"
    connection_info:
      address: gateway.company.com
      api_token: "api token value"
      connection_type: "gateway"

- name: Get Resource Group by name for direct connection type
  hitachivantara.vspone_block.vsp.hv_resource_group_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    spec:
      name: "my_resource_group"

- name: Get Resource Group by name for gateway connection type
  hitachivantara.vspone_block.vsp.hv_resource_group_facts:
    storage_system_info:
      serial: "811150"
    connection_info:
      address: gateway.company.com
      api_token: "api token value"
      connection_type: "gateway"
    spec:
      name: "my_resource_group"

- name: Get information about the Resource Groups specified in the query for direct connection type
  hitachivantara.vspone_block.vsp.hv_resource_group_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    spec:
      query:
        - ldevs
        - parity_groups
        - ports
        - host_groups
        - iscsi_targets
        - nvm_subsystem_ids
"""

RETURN = """
ansible_facts:
    description: The resource group information.
    returned: always
    type: dict
    contains:
        resource_groups:
            description: The resource group information.
            returned: always
            type: list
            elements: dict
            contains:
                id:
                    description: The ID of the resource group.
                    type: int
                    sample: 4
                name:
                    description: The name of the resource group.
                    type: str
                    sample: "my_resource_group"
                lock_status:
                    description: The lock status of the resource group.
                    type: str
                    sample: "Unlocked"
                host_groups:
                    description: List of host groups in the resource group.
                    type: list
                    elements: dict
                    contains:
                        id:
                            description: The ID of the host group.
                            type: int
                            sample: 1
                        name:
                            description: The name of the host group.
                            type: str
                            sample: "my_host_group_1"
                        port:
                            description: The port of the host group.
                            type: str
                            sample: "CL1-A"
                iscsi_targets:
                    description: List of iSCSI targets in the resource group.
                    type: list
                    elements: dict
                    contains:
                        id:
                            description: The ID of the iSCSI target.
                            type: int
                            sample: 1
                        name:
                            description: The name of the iSCSI target.
                            type: str
                            sample: "my_iscsi_target_1"
                        port:
                            description: The port of the iSCSI target.
                            type: str
                            sample: "CL1-C"
                ldevs:
                    description: List of LDEVs in the resource group.
                    type: list
                    elements: int
                    sample: [1, 2, 3]
                parity_groups:
                    description: List of parity groups in the resource group.
                    type: list
                    elements: str
                    sample: ["PG1", "PG2"]
                ports:
                    description: List of ports in the resource group.
                    type: list
                    elements: str
                    sample: ["CL1-A", "CL1-C"]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_resource_group import (
    VSPResourceGroupReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPResourceGroupArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.message.module_msgs import (
    ModuleMessage,
)


class VSPResourceGroupFactsManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = VSPResourceGroupArguments().resource_group_facts()

        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:
            self.parameter_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.parameter_manager.get_connection_info()
            self.storage_serial_number = self.parameter_manager.get_serial()
            self.logger.writeDebug(
                f"MOD:hv_resource_group_facts:serial= {self.storage_serial_number}"
            )
            self.spec = self.parameter_manager.get_resource_group_fact_spec()
            self.state = self.parameter_manager.get_state()

        except Exception as e:
            self.logger.writeError(f"An error occurred during initialization: {str(e)}")
            self.module.fail_json(msg=str(e))

    def apply(self):

        self.logger.writeInfo("=== Start of Resource Group Facts ===")
        registration_message = validate_ansible_product_registration()

        try:
            reconciler = VSPResourceGroupReconciler(
                self.connection_info, self.storage_serial_number, self.state
            )

            if self.connection_info.connection_type.lower() == ConnectionTypes.GATEWAY:
                oob = reconciler.is_out_of_band()
                if oob is True:
                    err_msg = ModuleMessage.OOB_NOT_SUPPORTED.value
                    self.logger.writeError(err_msg)
                    self.logger.writeInfo(
                        "=== End of Resource Group Lock operation ==="
                    )
                    self.module.fail_json(msg=err_msg)

            resource_groups = reconciler.get_resource_group_facts(self.spec)

        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of Resource Group Facts ===")
            self.module.fail_json(msg=str(e))

        data = {
            "resource_groups": resource_groups,
        }
        if registration_message:
            data["user_consent_required"] = registration_message

        self.logger.writeInfo(f"{data}")
        self.logger.writeInfo("=== End of Resource Group Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)


def main():
    obj_store = VSPResourceGroupFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
