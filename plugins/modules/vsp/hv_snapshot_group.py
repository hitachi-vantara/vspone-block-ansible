#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_snapshot_group
short_description: Manages snapshots in units of snapshot groups on Hitachi VSP storage systems.
description:
  - This module allows for the deletion, splitting, syncing, and restoring of snapshots on Hitachi VSP storage systems.
  - It supports various snapshot operations based on the specified task level.
  - This module is supported only for direct connection type.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/snapshot_group.yml)
version_added: '3.2.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
options:
  state:
    description: The level of the snapshot task. Choices are 'absent', 'split', 'sync', 'restore', 'clone'.
    type: str
    required: true
    choices: ['absent', 'split', 'sync', 'restore', 'clone']
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
        description: Username for authentication.This field is valid for direct connection type only, and it is a required field.
        type: str
        required: false
      password:
        description: Password for authentication.This field is valid for direct connection type only, and it is a required field.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system (direct only).
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
      - Specification for the snapshot facts to be gathered.
    type: dict
    required: true
    suboptions:
      snapshot_group_name:
        description:
          - The name of the snapshot group.
        type: str
        required: true
      auto_split:
        description:
          - Automatically split the snapshot group.
        type: bool
        required: false
"""

EXAMPLES = """
- name: Split snapshots using snapshot group name
  hv_snapshot_group:
    storage_system_info:
      serial: '811150'
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
      connection_type: "direct"
    state: split
    spec:
      snapshot_group_name: 'NewNameSPG'

- name: Restore snapshots using snapshot group name
  hv_snapshot_group:
    storage_system_info:
      serial: '811150'
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
      connection_type: "direct"
    state: restore
    spec:
      snapshot_group_name: 'NewNameSPG'

- name: Resync snapshots using snapshot group name
  hv_snapshot_group:
    storage_system_info:
      serial: '811150'
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
      connection_type: "direct"
    state: sync
    spec:
      snapshot_group_name: 'NewNameSPG'

- name: Delete snapshots using snapshot group name
  hv_snapshot_group:
    storage_system_info:
      serial: '811150'
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
      connection_type: "direct"
    state: absent
    spec:
      snapshot_group_name: 'NewNameSPG'
"""

RETURN = """
snapshots:
  description: A list of snapshots gathered from the storage system.
  returned: always
  type: list
  elements: dict
  sample:
    - snapshot_group_id: "SampleNameSPG"
      snapshot_group_name: "SampleNameSPG"
      snapshots:
        - storage_serial_number: 810050
          primary_volume_id: 1030
          primary_hex_volume_id: "00:04:06"
          secondary_volume_id: 1031
          secondary_hex_volume_id: "00:04:07"
          svol_access_mode: ""
          pool_id: 12
          consistency_group_id: -1
          mirror_unit_id: 3
          copy_rate: -1
          copy_pace_track_size: ""
          status: "PAIR"
          type: ""
          snapshot_id: "1030,3"
          is_consistency_group: true
          primary_or_secondary: "P-VOL"
          can_cascade: true
"""


from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPSnapshotArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    operation_constants,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_snapshot_reconciler import (
    VSPHtiSnapshotReconciler,
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
class VSPHtiSnapshotGrpFactManager:

    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPSnapshotArguments().snapshot_grp_args()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:

            self.params_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.params_manager.connection_info
            self.storage_serial_number = self.params_manager.storage_system_info.serial
            self.spec = self.params_manager.snapshot_grp_spec()
            self.state = self.params_manager.get_state()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Snapshot Group operation ===")
        snapshot_data = None
        registration_message = validate_ansible_product_registration()

        try:
            if (
                self.params_manager.connection_info.connection_type
                == ConnectionTypes.GATEWAY
            ):
                err_msg = ModuleMessage.NOT_SUPPORTED_FOR_GW.value
                self.logger.writeError(f"{err_msg}")
                self.logger.writeInfo("=== End of Snapshot Group operation ===")
                self.module.fail_json(msg=err_msg)
            snapshot_data = VSPHtiSnapshotReconciler(
                self.connection_info, self.storage_serial_number
            ).snapshot_group_id_reconcile(self.spec, self.state)

            operation = operation_constants(self.module.params["state"])
            msg = (
                f"Snapshot {operation} successfully"
                if not isinstance(snapshot_data, str)
                else snapshot_data
            )
            resp = {
                "changed": self.connection_info.changed,
                "snapshot_data": (
                    snapshot_data if isinstance(snapshot_data, dict) else None
                ),
                "msg": msg,
            }

        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of Snapshot Group operation ===")
            self.module.fail_json(msg=str(e))

        if registration_message:
            resp["user_consent_required"] = registration_message

        self.logger.writeInfo(f"{resp}")
        self.logger.writeInfo("=== End of Snapshot Group operation ===")
        self.module.exit_json(**resp)


def main(module=None):
    """Main function to execute the module."""
    obj_store = VSPHtiSnapshotGrpFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
