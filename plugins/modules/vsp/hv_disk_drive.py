#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_disk_drive
short_description: Change disk drive settings from Hitachi VSP storage systems.
description:
    - This module changes disk drive setiings from Hitachi VSP storage systems.
    - This module is supported only for direct connection to the storage system.
    - For examples go to URL
      U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/disk_drive.yml)
version_added: '3.2.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
options:
  state:
    description: The level of the Disk Drives task.
    type: str
    required: false
    choices: ['present']
    default: 'present'
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
        description: Username for authentication.This field is valid for direct connection type only, and it is a required field.
        type: str
        required: false
      password:
        description: Password for authentication.This field is valid for direct connection type only, and it is a required field.
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
        description: Token value to access UAI gateway (required for authentication either 'username,password' or api_token).
        type: str
        required: false
  spec:
    description:
      - Specification for the hard drive facts to be gathered.
    type: dict
    required: false
    suboptions:
      drive_location_id:
        description:
          - The drive location Id of the hard drive to retrieve.
        type: str
        required: false
      is_spared_drive:
        description:
          - Specify whether the disk drive is a spared drive.
        type: bool
        required: false
"""

EXAMPLES = """
- name: Change disk drive settings
  tasks:
    - hv_disk_drive:
        connection_info:
          address: storage1.company.com
          api_token: "api_token"
          connection_type: "direct"
        storage_system_info:
          - serial: "123456"
        state: "present"
        spec:
          drive_location_id: "0-16"
          is_spared_drive: true
"""

RETURN = """
disk_drive:
  description: Disk drive managed by the module.
  returned: success
  type: list
  elements: dict
  sample:
    {
      "copyback_mode": true,
      "drive_type": "SSD",
      "free_capacity": "5.16TB",
      "is_accelerated_compression": false,
      "is_encryption_enabled": true,
      "is_pool_array_group": false,
      "ldev_ids": [],
      "parity_group_id": "1-10",
      "raid_level": "RAID5",
      "resource_group_id": -1,
      "status": "",
      "total_capacity": "5.16TB"
    }
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_disk_drive,
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


class VSPDiskDriveManager:
    def __init__(self):
        self.logger = Log()

        self.argument_spec = VSPParityGroupArguments().drives()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.get_drives_fact_spec()
            self.serial = self.params_manager.get_serial()
            self.state = self.params_manager.get_state()
            self.connection_info = self.params_manager.get_connection_info()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Disk Drive operation. ===")
        registration_message = validate_ansible_product_registration()
        try:
            result = vsp_disk_drive.VSPDiskDriveReconciler(
                self.params_manager.connection_info, self.state
            ).disk_drive_reconcile(self.state, self.spec)

            # if result is not None and result is not str:
            #   snake_case_parity_group_data = camel_dict_to_snake_case(result.to_dict())

            msg = (
                result
                if isinstance(result, str)
                else "Disk drive settings changed successfully."
            )
            result = (
                camel_dict_to_snake_case(result)
                if not isinstance(result, str)
                else None
            )
            response_dict = {
                "changed": self.connection_info.changed,
                "data": result,
                "msg": msg,
            }
            if registration_message:
                response_dict["user_consent_required"] = registration_message

            self.logger.writeInfo(f"{response_dict}")
            self.logger.writeInfo("=== End of Disk Drive operation. ===")
            self.module.exit_json(**response_dict)
        except Exception as ex:
            self.logger.writeException(ex)
            self.logger.writeInfo("=== End of Disk Drive operation. ===")
            self.module.fail_json(msg=str(ex))


def main():
    obj_store = VSPDiskDriveManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
