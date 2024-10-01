#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


__metaclass__ = type


DOCUMENTATION = """
---
module: hv_nvm_subsystems_facts
short_description: Retrieves information about NVM subsystems from Hitachi VSP storage systems.
description:
     - This module gathers facts about NVM subsystems from Hitachi VSP storage systems.
version_added: '3.1.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.1.0
requirements:
options:
  storage_system_info:
    description:
      - Information about the storage system.
    type: dict
    required: true
    suboptions:
      serial:
        description:
          - The serial number of the storage system.
        type: str
        required: true
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
        description: Username for authentication.
        type: str
        required: true
      password:
        description: Password for authentication.
        type: str
        required: true
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['direct']
        default: 'direct'
  spec:
    description:
      - Specification for the NVM subsystems facts to be gathered.
    type: dict
    required: false
    suboptions:
      name:
        description:
          - The name of the NVM subsystem to retrieve.
        type: str
        required: false
      id:
        description:
          - The ID of the NVM subsystem to retrieve.
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
          name: "Nvm_subsystem_01
"""

RETURN = """
nvm_subsystems:
  description: The NVM subsystem information.
  returned: always
  type: list
  elements: dict/list
  sample:
    storage_serial_number: "810005"
    host_nqn_info:
        - host_nqn: "nqn.2014-08.org.example:uuid:4b73e622-ddc1-449a-99f7-412c0d3baa40"
          host_nqn_nickname: ""
    namespace_paths_info:
        - host_nqn: "nqn.2014-08.org.example:uuid:4b73e622-ddc1-449a-99f7-412c0d3baa40"
          ldev_id: 5555
          namespace_id: 3
    namespaces_info:
        - block_capacity: 23068672
          byte_format_capacity: "11.00 G"
          ldev_id: 5555
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
    
"""
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_nvme import (
    VSPNvmeReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPNvmeSubsystemArguments,
    VSPParametersManager,
)

logger = Log()


class VSPNvmSubsystemFactsManager:
    def __init__(self):

        self.argument_spec = VSPNvmeSubsystemArguments().nvme_subsystem_facts()
        logger.writeDebug(
            f"MOD:hv_nvm_subsystem_facts:argument_spec= {self.argument_spec}"
        )
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )

        self.parameter_manager = VSPParametersManager(self.module.params)
        self.connection_info = self.parameter_manager.get_connection_info()
        self.storage_serial_number = self.parameter_manager.storage_system_info.serial
        self.spec = self.parameter_manager.get_nvme_subsystem_fact_spec()
        self.state = self.parameter_manager.get_state()
        logger.writeDebug(f"MOD:hv_nvm_subsystem_facts:spec= {self.spec}")

    def apply(self):

        logger.writeInfo(f"{self.connection_info.connection_type} connection type")
        if (
                self.parameter_manager.connection_info.connection_type.lower()
                == ConnectionTypes.GATEWAY
            ):
            self.module.fail_json(msg="This feature is not supported for Gateway Connection.")

        try:
            reconciler = VSPNvmeReconciler(
                self.connection_info,
                self.storage_serial_number,
                self.state
            )
            nvme_subsystems = reconciler.get_nvme_subsystem_facts(self.spec)

            logger.writeDebug(
                f"MOD:hv_nvm_subsystem_facts:nvme_subsystems= {nvme_subsystems}"
            )

        except Exception as e:
            self.module.fail_json(msg=str(e))

        self.module.exit_json(nvm_subsystems=nvme_subsystems)


def main(module=None):
    obj_store = VSPNvmSubsystemFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()