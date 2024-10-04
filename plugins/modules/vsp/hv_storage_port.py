#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


__metaclass__ = type


DOCUMENTATION = """
---
module: hv_storage_port
short_description: Change the storage port settings in the Hitachi VSP storage systems.
description:
     - This module change the storage port settings information in the Hitachi VSP storage systems.
version_added: '3.1.0'
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
  spec:
    description:
      - Specification for the storage port facts to be gathered.
    type: dict
    required: false
    suboptions:
      port:
        description:
          - The port id of the specific port to retrieve.
        type: int
        required: true
      port_mode:
        description:
          - Specify the operating mode of the port between 'FC-NVMe' and 'FCP-SCSI' for the port.
        type: str
        required: false
      enable_port_security:
        description:
          - Specify whether to enable the lun security setting for the port.This attribute cannot be specified at the same time as the port_mode attribute.
        type: bool
        required: false
"""

EXAMPLES = """

- name: Change the port settings of a port
  tasks:
    - hv_storage_port:
        connection_info:
          address: storage1.company.com
          username: "admin"
          password: "secret"
          connection_type: "direct"
        spec:
          port: "CL1-A"
          enable_port_security: true


"""

RETURN = """
storagePort:
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
    StateValue,
    ConnectionTypes,
    CommonConstants,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_storage_port import (
    VSPStoragePortReconciler,
)

try:
    from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_logger import (
        MessageID,
    )

    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log


from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log_decorator import (
    LogDecorator,
)


@LogDecorator.debug_methods
class VSPStoragePortManager:

    def __init__(self):
        self.logger = Log()
        try:
            self.argument_spec = VSPStoragePortArguments().storage_port()
            self.module = AnsibleModule(
                argument_spec=self.argument_spec,
                supports_check_mode=True,
                # can be added mandotary , optional mandatory arguments
            )

            self.params_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.params_manager.connection_info
            self.storage_serial_number = self.params_manager.storage_system_info.serial
            self.spec = self.params_manager.port_module_spec()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        port_data = None
        self.logger.writeInfo(
            f"{self.params_manager.connection_info.connection_type} connection type"
        )
        try:

            port_data = self.storage_port_module()

        except Exception as e:
            self.module.fail_json(msg=str(e))

        resp = {
                "changed": self.connection_info.changed,
                "port_info": port_data,
                "msg": f"Storage port reconciled successfully",
            }
        self.module.exit_json(**resp)

    def storage_port_module(self):
        reconciler = VSPStoragePortReconciler(
            self.connection_info,
            self.storage_serial_number,
        )
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            found = reconciler.check_storage_in_ucpsystem()
            if not found:
                self.module.fail_json(
                    "The storage system is still onboarding or refreshing, Please try after sometime"
                )

        result = reconciler.vsp_storage_port_reconcile(self.spec)
        return result


def main():
    """
    :return: None
    """
    obj_store = VSPStoragePortManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
