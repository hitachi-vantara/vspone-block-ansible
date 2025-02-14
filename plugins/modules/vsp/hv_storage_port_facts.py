#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_storage_port_facts
short_description: Retrieves storage port information from Hitachi VSP storage systems.
description:
  - This module retrieves information about storage ports from Hitachi VSP storage systems.
  - This module is supported only for direct connection type.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/storage_port_facts.yml)
version_added: '3.0.0'
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
        description: IP address or hostname of either the UAI gateway (if connection_type is gateway) or the storage system (if connection_type is direct).
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
        description: Type of connection to the storage system (Only direct connect available).
        type: str
        required: false
        choices: ['direct']
        default: 'direct'
      api_token:
        description: Value of the lock token to operate on locked resources.
        type: str
        required: false
  spec:
    description:
      - Specification for the storage port facts to be gathered.
    type: dict
    required: false
    suboptions:
      ports:
        description:
          - The id of the specific ports to retrieve.
        type: list
        required: false
        elements: str
"""

EXAMPLES = """
- name: Get all ports
  tasks:
    - hv_storage_port_facts:
        connection_info:
          address: storage1.company.com
          username: "admin"
          password: "secret"
          connection_type: "direct"

- name: Get a specific port
  tasks:
    - hv_storage_port_facts:
        connection_info:
          address: storage1.company.com
          username: "admin"
          password: "secret"
          connection_type: "direct"
        spec:
          ports: ["CLA-1", "CLA-2"]
"""

RETURN = """
storageport:
  description: The storage port information.
  returned: always
  type: list
  elements: dict
  sample:
    - fabric_mode: true
      ipv4_address: ""
      ipv4_gateway_address: ""
      ipv4_subnetmask: ""
      iscsi_window_size: ""
      keep_alive_timer: -1
      loop_id: "CE"
      lun_security_setting: false
      mac_address: ""
      port_attributes:
        - "TAR"
        - "MCU"
        - "RCU"
        - "ELUN"
      port_connection: "PtoP"
      port_id: "CL8-B"
      port_mode: "FCP-SCSI"
      port_speed: "AUT"
      port_type: "FIBRE"
      storage_serial_number: "715035"
      tcp_port: ""
      wwn: "50060e8028274271"
"""


from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPStoragePortArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_storage_port import (
    VSPStoragePortReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log_decorator import (
    LogDecorator,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.message.module_msgs import (
    ModuleMessage,
)


@LogDecorator.debug_methods
class VSPStoragePortFactManager:

    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPStoragePortArguments().storage_port_fact()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:

            self.params_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.params_manager.connection_info
            self.storage_serial_number = self.params_manager.storage_system_info.serial
            self.spec = self.params_manager.get_port_fact_spec()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Storage Port Facts ===")
        port_data = None
        registration_message = validate_ansible_product_registration()

        try:

            port_data = self.get_storage_port_facts()

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of Storage Port Facts ===")
            self.module.fail_json(msg=str(e))
        data = {
            "port_data": port_data,
        }
        if registration_message:
            data["user_consent_required"] = registration_message

        self.logger.writeInfo(f"{data}")
        self.logger.writeInfo("=== End of Storage Port Facts ===")
        self.module.exit_json(**data)

    def get_storage_port_facts(self):
        reconciler = VSPStoragePortReconciler(
            self.connection_info,
            self.storage_serial_number,
        )
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            found = reconciler.check_storage_in_ucpsystem()
            if not found:
                raise ValueError(ModuleMessage.STORAGE_SYSTEM_ONBOARDING.value)
            oob = reconciler.is_out_of_band()
            if oob is True:
                raise ValueError(ModuleMessage.OOB_NOT_SUPPORTED.value)

        result = reconciler.vsp_storage_port_facts(self.spec)
        return result


def main(module=None):
    """
    :return: None
    """
    obj_store = VSPStoragePortFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
