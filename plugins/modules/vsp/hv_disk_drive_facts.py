#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_disk_drive_facts
short_description: Retrieves information about hard drives from Hitachi VSP storage systems.
description:
    - This module gathers facts about hard drives from Hitachi VSP storage systems.
    - This module is supported only for direct connection to the storage system.
    - For examples go to URL
      U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/disk_drive_facts.yml)
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
        description: IP address of the hostname of the storage system.
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
          This field is not required for this module.
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway. This is a required field for gateway connection type. Not required for this module.
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
"""

EXAMPLES = """
- name: Get a specific hard drive
  tasks:
    - hv_hard_drive_facts:
        connection_info:
          address: storage1.company.com
          username: "admin"
          password: "secret"
          connection_type: "direct"
        spec:
          drive_location_id: 0-16

- name: Get all hard drives
  tasks:
    - hv_hard_drive_facts:
        connection_info:
          address: storage1.company.com
          username: "admin"
          password: "secret"
          connection_type: "direct"
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
      "total_capacity": "5.16TB",
    }

"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPParityGroupArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_parity_group,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    camel_dict_to_snake_case,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class VspDiskDriveFactManager:
    def __init__(self):
        # VSPStoragePoolArguments
        self.logger = Log()
        self.argument_spec = VSPParityGroupArguments().drives_fact()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.get_drives_fact_spec()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        registration_message = validate_ansible_product_registration()

        try:
            self.logger.writeInfo("=== Start of Disk Drive Facts ===")
            result = vsp_parity_group.VSPParityGroupReconciler(
                self.params_manager.connection_info
            ).get_all_drives(self.spec)

            # if result is not None and result is not str:
            #   snake_case_parity_group_data = camel_dict_to_snake_case(result.to_dict())

            msg = (
                result
                if isinstance(result, str)
                else "Disk drives retrieved successfully."
            )
            result = (
                camel_dict_to_snake_case(result)
                if not isinstance(result, str)
                else None
            )
            response_dict = {
                "disk_drives": result,
                "msg": msg,
            }
            if registration_message:
                response_dict["user_consent_required"] = registration_message

            self.logger.writeInfo(f"{response_dict}")
            self.logger.writeInfo("=== End of Disk Drive Facts ===")
            self.module.exit_json(**response_dict)
        except Exception as ex:
            self.logger.writeException(ex)
            self.logger.writeInfo("=== End of Disk Drive Facts ===")
            self.module.fail_json(msg=str(ex))


def main(module=None):
    obj_store = VspDiskDriveFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
