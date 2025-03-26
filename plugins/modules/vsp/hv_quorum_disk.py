#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_quorum_disk
short_description: Manages Quorum Disks in the Hitachi VSP storage systems.
description:
  - This module registers and de-registers the Quorum Disks in the Hitachi VSP storage systems.
  - This module is supported for direct connection type only.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/quorum_disk.yml)
version_added: '3.3.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
options:
  state:
    description: The desired state.
    type: str
    required: false
    choices: ['present', 'absent']
    default: 'present'
  storage_system_info:
    description: Information about the Hitachi storage system. This field is required for gateway connection type only.
    type: dict
    required: false
    suboptions:
      serial:
        description: Serial number of the Hitachi storage system.
        type: str
        required: false
  connection_info:
    description: Information required to establish a connection to the storage system.
    type: dict
    required: true
    suboptions:
      address:
        description: IP address or hostname of either the UAI gateway (if connection_type is C(gateway)) or
            the storage system (if connection_type is C(direct)).
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
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['gateway', 'direct']
        default: 'direct'
      subscriber_id:
        description: This field is valid for C(gateway) connection type only. This is an optional field and only needed to support multi-tenancy environment.
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway. This is a required field for C(gateway) connection type.
        type: str
        required: false
  spec:
    description: Specification for the Quorum Disk management.
    type: dict
    required: false
    suboptions:
      id:
        description: Quorum Disk ID, it will be auto-selected if omitted.
        type: int
        required: false
      remote_storage_serial_number:
        description: The remote storage serial number to register.
        type: str
        required: false
      remote_storage_type:
        description: The remote storage type to register.
        type: str
        choices: ['M8', 'R8', 'R9']
        required: false
      ldev_id:
        description: Local LDEV ID for the external volume.
        type: int
        required: false

"""

EXAMPLES = """
- name: Register a Quorum Disk for direct connection type
  hv_quorum_disk_facts:
    connection_info:
      address: gateway.company.com
      username: 'username'
      password: 'password'
      connection_type: "direct"
    spec:
      remote_storage_serial_number: 715036
      remote_storage_type: M8
      ldev_id: 3028
      id: 4
"""

RETURN = """
data:
  description: The Quorum Disk managed by the module.
  returned: success
  type: list
  elements: dict
  sample: {
    "ldev_id": 3028,
    "quorum_disk_id": 4,
    "read_response_guaranteed_time": 40,
    "remote_serial_number": "715036",
    "remote_storage_type_id": "M8",
    "status": "NORMAL"
  }
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_quorum_disk_reconciler import (
    VSPQuorumDiskReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPParametersManager,
    VSPQuorumDiskArguments,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class ModuleManager:
    def __init__(self):
        self.logger = Log()

        self.argument_spec = VSPQuorumDiskArguments().quorum_disk()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.quorum_disk_spec()
            self.serial = self.params_manager.get_serial()
            self.state = self.params_manager.get_state()
            self.connection_info = self.params_manager.get_connection_info()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Quorum Disk operation ===")
        try:
            registration_message = validate_ansible_product_registration()
            result, res_msg = VSPQuorumDiskReconciler(
                self.params_manager.connection_info, self.serial
            ).quorum_disk_reconcile(self.state, self.spec)
            self.logger.writeInfo(f"20250303 result={result}")

            msg = res_msg if res_msg else self.get_message()
            result = result if not isinstance(result, str) else None

            response_dict = {
                "failed": result is None,
                "changed": self.connection_info.changed,
                "data": result,
                "msg": msg,
            }
            if registration_message:
                response_dict["user_consent_required"] = registration_message
            self.logger.writeInfo(f"{response_dict}")
            self.logger.writeInfo("=== End of Quorum Disk operation. ===")
            self.module.exit_json(**response_dict)
        except Exception as ex:
            self.logger.writeException(ex)
            self.logger.writeInfo("=== End of Quorum Disk operation. ===")
            self.module.fail_json(msg=str(ex))

    def get_message(self):

        if self.state == "present":
            return "Quorum Disk registered successfully."
        elif self.state == "absent":
            return "Quorum Disk deregistered successfully."
        else:
            return "Unknown state provided."


def main(module=None):
    obj_store = ModuleManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
