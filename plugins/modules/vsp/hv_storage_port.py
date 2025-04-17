#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_storage_port
short_description: Change the storage port settings in the Hitachi VSP storage systems.
description:
  - This module change the storage port settings information in the Hitachi VSP storage systems.
  - This module is supported only for C(direct) connection type.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/storage_port.yml)
version_added: '3.1.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.8
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: none
options:
  storage_system_info:
    description: Information about the storage system.
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
        description: IP address or hostname of the storage system.
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
        description: Type of connection to the storage system. Only C(direct) connection type is supported.
        type: str
        required: false
        choices: ['direct']
        default: 'direct'
      api_token:
        description: Value of the lock token to operate on locked resources for C(direct) connection type.
        type: str
        required: false
  spec:
    description: Specification for the storage port facts to be gathered.
    type: dict
    required: false
    suboptions:
      port:
        description: The port id of the specific port to retrieve.
        type: str
        required: true
      port_mode:
        description: Specify the operating mode of the port between 'FC-NVMe' and 'FCP-SCSI' for the port.
        type: str
        required: false
      enable_port_security:
        description: Specify whether to enable the lun security setting for the port.This attribute cannot
          be specified at the same time as the port_mode attribute.
        type: bool
        required: false
"""

EXAMPLES = """
- name: Change the port settings of a port for direct connection type
  hitachivantara.vspone_block.vsp.hv_storage_port:
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
  contains:
    fabric_mode:
      description: Indicates if the port is in fabric mode.
      type: bool
      sample: true
    ipv4_address:
      description: IPv4 address of the port.
      type: str
      sample: ""
    ipv4_gateway_address:
      description: IPv4 gateway address of the port.
      type: str
      sample: ""
    ipv4_subnetmask:
      description: IPv4 subnet mask of the port.
      type: str
      sample: ""
    iscsi_window_size:
      description: iSCSI window size.
      type: str
      sample: ""
    keep_alive_timer:
      description: Keep alive timer value.
      type: int
      sample: -1
    loop_id:
      description: Loop ID of the port.
      type: str
      sample: "CE"
    lun_security_setting:
      description: Indicates if LUN security setting is enabled.
      type: bool
      sample: false
    mac_address:
      description: MAC address of the port.
      type: str
      sample: ""
    port_attributes:
      description: List of port attributes.
      type: list
      elements: str
      sample: ["TAR", "MCU", "RCU", "ELUN"]
    port_connection:
      description: Type of port connection.
      type: str
      sample: "PtoP"
    port_id:
      description: Port ID.
      type: str
      sample: "CL8-B"
    port_mode:
      description: Operating mode of the port.
      type: str
      sample: "FCP-SCSI"
    port_speed:
      description: Speed of the port.
      type: str
      sample: "AUT"
    port_type:
      description: Type of the port.
      type: str
      sample: "FIBRE"
    storage_serial_number:
      description: Serial number of the storage system.
      type: str
      sample: "715035"
    tcp_port:
      description: TCP port number.
      type: str
      sample: ""
    wwn:
      description: World Wide Name of the port.
      type: str
      sample: "50060e8028274271"
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
class VSPStoragePortManager:

    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPStoragePortArguments().storage_port()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )
        try:

            self.params_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.params_manager.connection_info
            self.storage_serial_number = self.params_manager.storage_system_info.serial
            self.spec = self.params_manager.port_module_spec()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Storage Port operation. ===")
        port_data = None
        registration_message = validate_ansible_product_registration()
        try:

            port_data = self.storage_port_module()

        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of Storage Port operation. ===")
            self.module.fail_json(msg=str(e))

        resp = {
            "changed": self.connection_info.changed,
            "port_info": port_data,
            "msg": "Storage port updated successfully",
        }
        if registration_message:
            resp["user_consent_required"] = registration_message
        self.logger.writeInfo(f"{resp}")
        self.logger.writeInfo("=== End of Storage Port operation. ===")
        self.module.exit_json(**resp)

    def storage_port_module(self):
        reconciler = VSPStoragePortReconciler(
            self.connection_info,
            self.storage_serial_number,
        )
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            oob = reconciler.is_out_of_band()
            if oob is True:
                raise ValueError(ModuleMessage.OOB_NOT_SUPPORTED.value)

        result = reconciler.vsp_storage_port_reconcile(self.spec)
        return result


def main(module=None):
    """
    :return: None
    """
    obj_store = VSPStoragePortManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
