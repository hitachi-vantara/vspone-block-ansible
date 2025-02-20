#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_nvm_subsystems_facts
short_description: Retrieves information about NVM subsystems from Hitachi VSP storage systems.
description:
  - This module gathers facts about NVM subsystems from Hitachi VSP storage systems.
  - This module is supported only for direct connection to the storage system.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/nvm_subsystem_facts.yml)
version_added: '3.1.0'
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
        description: IP address or hostname of the storage system.
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
        description: Type of connection to the storage system. Only direct connection is supported.
        type: str
        required: false
        choices: ['direct', 'gateway']
        default: 'direct'
      subscriber_id:
        description:
          - This field is valid for gateway connection type only. This is an optional field and only needed to support multi-tenancy environment.
        type: str
        required: false
      api_token:
        description: Value of the lock token to operate on locked resources for direct connection.
        type: str
        required: false
  spec:
    description: Specification for the NVM subsystems facts to be gathered.
    type: dict
    required: false
    suboptions:
      name:
        description: The name of the NVM subsystem to retrieve.
        type: str
        required: false
      id:
        description: The ID of the NVM subsystem to retrieve.
        type: int
        required: false
"""

EXAMPLES = """
- name: Get all NVM subsystems
  tasks:
    - hv_nvm_subsystems_facts:
        connection_info:
          address: storage1.company.com
          username: "admin"
          password: "secret"
          connection_type: "direct"

- name: Get a specific NVM subsystem
  tasks:
    - hv_nvm_subsystems_facts:
        connection_info:
          address: storage1.company.com
          username: "admin"
          password: "secret"
          connection_type: "direct"
        spec:
          name: "Nvm_subsystem_01"
"""

RETURN = """
nvm_subsystems:
  description: The NVM subsystem information.
  returned: always
  type: list
  elements: dict
  sample:
    storage_serial_number: "810005"
    host_nqn_info:
        - host_nqn: "nqn.2014-08.org.example:uuid:4b73e622-ddc1-449a-99f7-412c0d3baa40"
          host_nqn_nickname: "my_host_nqn_40"
    namespace_paths_info:
        - host_nqn: "nqn.2014-08.org.example:uuid:4b73e622-ddc1-449a-99f7-412c0d3baa40"
          ldev_id: 11101
          ldev_hex_id: "00:2b:5c"
          namespace_id: 3
    namespaces_info:
        - block_capacity: 23068672
          capacity_in_unit: "11.00 G"
          ldev_id: 11101
          ldev_hex_id: "00:2b:5c"
          namespace_id: 3
          namespace_nickname: "nickname"
    nvm_subsystem_info:
        host_mode: "VMWARE_EX"
        namespace_security_setting: "Enable"
        nvm_subsystem_id: 1000
        nvm_subsystem_name: "nvm_tcp_01"
        resource_group_id: 0
        t10pi_mode: "Disable"
    port:
        - port_id: "CL1-D"
          port_type: "NVME_TCP"
"""
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_nvme import (
    VSPNvmeReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPNvmeSubsystemArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.message.module_msgs import (
    ModuleMessage,
)


class VSPNvmSubsystemFactsManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = VSPNvmeSubsystemArguments().nvme_subsystem_facts()

        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        try:
            self.parameter_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.parameter_manager.get_connection_info()
            self.storage_serial_number = (
                self.parameter_manager.storage_system_info.serial
            )
            self.spec = self.parameter_manager.get_nvme_subsystem_fact_spec()
            self.state = self.parameter_manager.get_state()
            self.logger.writeDebug(f"MOD:hv_nvm_subsystem_facts:spec= {self.spec}")
        except Exception as e:
            self.logger.writeError(f"An error occurred during initialization: {str(e)}")
            self.module.fail_json(msg=str(e))

    def apply(self):

        self.logger.writeInfo("=== Start of NVM Subsystem Facts ===")
        registration_message = validate_ansible_product_registration()
        if (
            self.parameter_manager.connection_info.connection_type.lower()
            == ConnectionTypes.GATEWAY
        ):
            err_msg = ModuleMessage.NOT_SUPPORTED_FOR_GW.value
            self.logger.writeError(f"{err_msg}")
            self.logger.writeInfo("=== End of NVM Subsystem operation ===")
            self.module.fail_json(msg=err_msg)

        try:
            reconciler = VSPNvmeReconciler(
                self.connection_info, self.storage_serial_number, self.state
            )
            nvme_subsystems = reconciler.get_nvme_subsystem_facts(self.spec)

            self.logger.writeDebug(
                f"MOD:hv_nvm_subsystem_facts:nvme_subsystems= {nvme_subsystems}"
            )

        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of NVM Subsystem Facts ===")
            self.module.fail_json(msg=str(e))
        data = {
            "nvm_subsystems": nvme_subsystems,
        }
        if registration_message:
            data["user_consent_required"] = registration_message

        self.logger.writeInfo(f"{data}")
        self.logger.writeInfo("=== End of NVM Subsystem Facts ===")
        self.module.exit_json(**data)


def main(module=None):
    obj_store = VSPNvmSubsystemFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
