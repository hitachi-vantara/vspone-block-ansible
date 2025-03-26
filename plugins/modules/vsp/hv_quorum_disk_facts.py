#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_quorum_disk_facts
short_description: Retrieves information about Quorum Disks from Hitachi VSP storage systems.
description:
  - This module retrieves information about Quorum Disks from Hitachi VSP storage systems.
  - This module is supported for direct connection type only.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/quorum_disk_facts.yml)
version_added: '3.3.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
options:
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
    description: Specification for retrieving Quorum Disk information.
    type: dict
    required: false
    suboptions:
      id:
        description: Quorum Disk ID, it will be auto-selected if omitted.
        type: int
        required: false

"""

EXAMPLES = """
- name: Retrieve information about all Quorum Disks for direct connection type
  hv_quorum_disk_facts:
    connection_info:
      address: gateway.company.com
      username: 'username'
      password: 'password'
      connection_type: "direct"
"""

RETURN = """
ansible_facts:
  description: >
    Dictionary containing the discovered properties of the Quorum Disks.
  returned: success
  type: dict
  contains:
    quorum_disk:
      description: List of Quorum Disks with their attributes.
      type: list
      elements: dict
      contains:
        id:
          description: Quorum Disk ID.
          type: int
          sample: 1
        ldev_id:
          description: Local volume LDEV ID.
          type: int
          sample: 123
        read_response_guaranteed_time:
          description: Copy pace track size.
          type: int
          sample: 40
        remote_serial_number:
          description: Copy pace track size.
          type: str
          sample: "712345"
        remote_storage_type_id:
          description: Copy pace track size.
          type: str
          sample: "M8"
        status:
          description: Quorum Disk status.
          type: str
          sample: "NORMAL"
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


class VSPQuorumDiskFactManager:
    def __init__(self):
        self.logger = Log()

        self.argument_spec = VSPQuorumDiskArguments().quorum_disk_fact()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.get_quorum_disk_fact_spec()
            self.serial = self.params_manager.get_serial()
            self.logger.writeDebug("20250228 serial={}", self.serial)
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Quorum Disk Facts ===")
        registration_message = validate_ansible_product_registration()
        try:
            result = []
            result = VSPQuorumDiskReconciler(
                self.params_manager.connection_info, self.serial
            ).quorum_disk_facts(self.spec)

        except Exception as ex:

            self.logger.writeException(ex)
            self.logger.writeInfo("=== End of Quorum Disk Facts ===")
            self.module.fail_json(msg=str(ex))
        data = {
            "quorum_disk": result,
        }
        if registration_message:
            data["user_consent_required"] = registration_message
        # self.logger.writeInfo(f"{data}")
        self.logger.writeInfo("=== End of Quorum Disk Facts ===")
        self.module.exit_json(**data)


def main(module=None):
    obj_store = VSPQuorumDiskFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
