#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


__metaclass__ = type


DOCUMENTATION = """
---
module: hv_cmd_dev
short_description: Manages command devices on Hitachi VSP storage systems.
description:
    - This module allows to enable and to disable a command device on Hitachi VSP storage systems.
    - It also allows to modify the settings of the command device.
    - This module is supported only for direct connection to the storage system.
    - For examples go to URL
      U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/cmd_dev.yml)
version_added: '3.2.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
options:
    state:
        description: The level of the resource group task.
        type: str
        required: false
        choices: ['present', 'absent']
        default: 'present'
    storage_system_info:
        description:
          - Information about the storage system.
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
                description: |
                    IP address or hostname of the storage system.
                type: str
                required: true
            username:
                description: Username for authentication. This field is valid for direct connection type only, and it is a required field.
                type: str
                required: true
            password:
                description: Password for authentication. This field is valid for direct connection type only, and it is a required field.
                type: str
                required: true
            connection_type:
                description: Type of connection to the storage system (Only direct connect available).
                type: str
                required: false
                choices: ['direct']
                default: 'direct'
    spec:
        description:
            - Specification for the command device.
        type: dict
        required: false
        suboptions:
            ldev_id:
                description:
                    - The id of the LDEV.
                type: int
                required: true
            is_security_enabled:
                description:
                    - Specify whether to enable the security settings for the command device.
                type: bool
                required: false
            is_user_authentication_enabled:
                description:
                    - Specify whether to enable the user authentication settings for the command device.
                type: bool
                required: false
            is_device_group_definition_enabled:
                description:
                    - Specify whether to enable the device group definition settings for the command device.
                type: bool
                required: false
"""

EXAMPLES = """
- name: Enable a Command Device
  tasks:
    - hv_cmd_dev:
        connection_info:
          address: storage1.company.com
          username: "admin"
          password: "secret"
        spec:
          ldev_id: 98
          is_security_enabled: false
          is_user_authentication_enabled: false
          is_device_group_definition_enabled: false

- name: Update the settings of a Command Device
  tasks:
    - hv_cmd_dev:
        connection_info:
          address: storage1.company.com
          username: "admin"
          password: "secret"
        spec:
          ldev_id: 98
          is_security_enabled: true
          is_user_authentication_enabled: true
          is_device_group_definition_enabled: true

- name: Disable a Command Device
  tasks:
    - hv_cmd_dev:
        connection_info:
          address: storage1.company.com
          username: "admin"
          password: "secret"
        state: absent
        spec:
          ldev_id: 98
          is_security_enabled: false
          is_user_authentication_enabled: false
          is_device_group_definition_enabled: false
"""

RETURN = """
command_device:
  description: The command device information.
  returned: always except when state is absent
  type: list
  elements: dict
  sample:
    {   canonical_name: "naa.60060e80089c4f0000509c4f00000062",
        dedup_compression_progress: -1,
        dedup_compression_status: "DISABLED",
        deduplication_compression_mode: "disabled",
        emulation_type: "OPEN-V-CVS-CM",
        entitlement_status: "",
        hostgroups: [],
        is_alua: false,
        is_command_device: true,
        is_data_reduction_share_enabled: false,
        is_device_group_definition_enabled: true,
        is_encryption_enabled: false,
        is_security_enabled: true,
        is_user_authentication_enabled: true,
        is_write_protected: false,
        is_write_protected_by_key: false,
        iscsi_targets: [],
        ldev_id: 98,
        logical_unit_id_hex_format: "00:00:62",
        name: "",
        num_of_ports: 0,
        nvm_subsystems: [{   id: 0, name: "NVM-1", ports: ["CL2-H"]}],
        parity_group_id: "",
        partner_id: "",
        path_count: 0,
        pool_id: 0,
        provision_type: "CMD,CVS,HDP",
        qos_settings: {},
        resource_group_id: 0,
        snapshots: [],
        status: "NML",
        storage_serial_number: "40015",
        subscriber_id: "",
        total_capacity: "1.00GB",
        used_capacity: "0.00B",
        virtual_ldev_id: -1,
    }
"""
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_cmd_dev import (
    VSPCmdDevReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPCmdDevArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.message.module_msgs import (
    ModuleMessage,
)


class VSPCmdDevManager:
    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPCmdDevArguments().cmd_dev()
        self.logger.writeDebug(f"MOD:hv_cmd_dev:argument_spec= {self.argument_spec}")
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )
        try:
            self.parameter_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.parameter_manager.get_connection_info()
            self.storage_serial_number = (
                self.parameter_manager.storage_system_info.serial
            )
            self.spec = self.parameter_manager.get_cmd_dev_spec()
            self.state = self.parameter_manager.get_state()
            self.logger.writeDebug(
                f"MOD:hv_cmd_dev:spec= {self.spec} ss = {self.storage_serial_number}"
            )
        except Exception as e:
            self.logger.writeError(f"An error occurred during initialization: {str(e)}")
            self.module.fail_json(msg=str(e))

    def apply(self):

        self.logger.writeInfo("=== Start of Command Device operation. ===")
        registration_message = validate_ansible_product_registration()
        if (
            self.parameter_manager.connection_info.connection_type.lower()
            == ConnectionTypes.GATEWAY
        ):
            err_msg = ModuleMessage.NOT_SUPPORTED_FOR_GW.value
            self.logger.writeError(err_msg)
            self.logger.writeInfo("=== End of Command Device operation. ===")
            self.module.fail_json(msg=err_msg)

        cmd_dev = None
        comment = None
        try:
            reconciler = VSPCmdDevReconciler(
                self.connection_info, self.storage_serial_number, self.state
            )
            cmd_dev = reconciler.reconcile_cmd_dev(self.spec)

        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of Command Device operation. ===")
            self.module.fail_json(msg=str(e))

        if cmd_dev is None and self.state == "absent":
            comment = "Command Device is disabled."
        resp = {
            "changed": self.connection_info.changed,
        }
        if cmd_dev:
            resp["command_device"] = cmd_dev
        if comment:
            resp["comment"] = comment
        if registration_message:
            resp["user_consent_required"] = registration_message

        self.logger.writeInfo(f"{resp}")
        self.logger.writeInfo("=== End of Command Device operation. ===")
        self.module.exit_json(**resp)


def main(module=None):
    obj_store = VSPCmdDevManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
