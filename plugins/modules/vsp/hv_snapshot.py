#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_snapshot
short_description: Manages snapshots on Hitachi VSP storage systems.
description:
  - This module allows for the creation, deletion, splitting, syncing, and restoring of snapshots on Hitachi VSP storage systems.
  - It supports various snapshot operations based on the specified task level.
  - This module is supported for both C(direct) and C(gateway) connection types.
  - For C(direct) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/snapshot.yml)
  - For C(gateway) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/snapshot.yml)
version_added: '3.0.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.8
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: none
options:
  state:
    description: The level of the snapshot task. Choices are C(present), C(absent), C(split), C(sync), C(restore), C(clone).
    type: str
    required: false
    choices: ['present', 'absent', 'split', 'sync', 'restore', 'clone']
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
        description: IP address or hostname of either the UAI gateway (if connection_type is C(gateway) ) or
          the storage system (if connection_type is C(direct) .)
        type: str
        required: true
      username:
        description: Username for authentication.This field is valid for C(direct) connection type only, and it is a required field.
        type: str
        required: false
      password:
        description: Password for authentication.This field is valid for C(direct) connection type only, and it is a required field.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['gateway', 'direct']
        default: 'direct'
      api_token:
        description: API token for authentication. This is a required field for C(gateway) connection type.
        type: str
        required: false
      subscriber_id:
        description: This field is valid for C(gateway) connection type only. This is an optional field and only needed to support multi-tenancy environment.
        type: str
        required: false
  spec:
    description: Specification for the snapshot task.
    type: dict
    required: true
    suboptions:
      primary_volume_id:
        description: ID of the primary volume.
        type: int
        required: true
      pool_id:
        description: ID of the pool where the snapshot will be allocated.
        type: int
        required: false
      snapshot_group_name:
        description: Name of the snapshot group (required for C(direct) connection type and thin image advance).
        type: str
        required: false
      is_data_reduction_force_copy:
        description: Specify whether to forcibly create a pair for a volume for which the capacity saving function is enabled
          (Required for C(direct) connection type and thin image advance, Default is True when capacity savings is not C(disabled).
        required: false
        type: bool
      is_clone:
        description: Specify true to create a thin image advance clone pair
        required: false
        type: bool
      can_cascade:
        description: Specify whether the pair can be cascaded. (Required for C(direct) connection type and thin image advance,
          Default is True when capacity savings is not C(disabled), Lun may not required to add to any host group when is it true.
        required: false
        type: bool
      allocate_new_consistency_group:
        description: Specify whether to allocate a consistency group.
        required: false
        type: bool
      mirror_unit_id:
        description: ID of the mirror unit.
        required: false
        type: int
      auto_split:
        description: Specify whether to automatically split the pair.
        required: false
        type: bool
      consistency_group_id:
        description: ID of the consistency group.
        required: false
        type: int
      enable_quick_mode:
        description: Specify whether to enable quick mode.
        required: false
        type: bool
"""

EXAMPLES = """
- name: Create a snapshot for direct connection type
  hitachivantara.vspone_block.vsp.hv_snapshot:
    state: present
    connection_info:
      address: storage1.company.com
      username: "username"
      password: "password"
      connection_type: "direct"
    spec:
      primary_volume_id: 123
      pool_id: 1
      snapshot_group_name: "snap_group"

- name: Create a thin image advance cascade pair for direct connection type
  hitachivantara.vspone_block.vsp.hv_snapshot:
    state: present
    connection_info:
      address: storage1.company.com
      username: "username"
      password: "password"
      connection_type: "direct"
    spec:
      primary_volume_id: 123
      pool_id: 1
      snapshot_group_name: "snap_group"
      can_cascade: true
      is_data_reduction_force_copy: true

- name: Create a thin image advance clone pair for direct connection type
  hitachivantara.vspone_block.vsp.hv_snapshot:
    state: present
    connection_info:
      address: storage1.company.com
      username: "username"
      password: "password"
      connection_type: "direct"
    spec:
      primary_volume_id: 123
      pool_id: 1
      snapshot_group_name: "snap_group"
      is_clone: true
      is_data_reduction_force_copy: true

- name: Clone a thin image advance clone pair for direct connection type
  hitachivantara.vspone_block.vsp.hv_snapshot:
    state: clone
    connection_info:
      address: storage1.company.com
      username: "username"
      password: "password"
      connection_type: "direct"
    spec:
      primary_volume_id: 123
      mirror_unit: 3

- name: Delete a snapshot for direct connection type
  hitachivantara.vspone_block.vsp.hv_snapshot:
    state: absent
    connection_info:
      address: gateway.company.com
      username: "username"
      password: "password"
      connection_type: "direct"
    spec:
      primary_volume_id: 123
      mirror_unit: 10

- name: Split a snapshot for direct connection type
  hitachivantara.vspone_block.vsp.hv_snapshot:
    state: split
    connection_info:
      address: storage1.company.com
      username: "username"
      password: "password"
      connection_type: "direct"
    spec:
      primary_volume_id: 123
      mirror_unit: 10

- name: Split a snapshot for gateway connection type
  hitachivantara.vspone_block.vsp.hv_snapshot:
    state: split
    storage_system_info:
      serial: "811150"
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
    spec:
      primary_volume_id: 123
      mirror_unit: 10

- name: Resync a snapshot for direct connection type
  hitachivantara.vspone_block.vsp.hv_snapshot:
    state: resync
    connection_info:
      address: gateway.company.com
      username: "username"
      password: "password"
      connection_type: "direct"
    spec:
      primary_volume_id: 123
      mirror_unit: 10

- name: Restore a snapshot for direct connection type
  hitachivantara.vspone_block.vsp.hv_snapshot:
    state: restore
    connection_info:
      address: gateway.company.com
      username: "username"
      password: "password"
      connection_type: "direct"
    spec:
      primary_volume_id: 123
      mirror_unit: 3
"""

RETURN = """
snapshots:
  description: A list of snapshots gathered from the storage system.
  returned: always
  type: list
  elements: dict
  contains:
    storage_serial_number:
      description: Serial number of the storage system.
      type: int
      sample: 810050
    primary_volume_id:
      description: ID of the primary volume.
      type: int
      sample: 1030
    primary_hex_volume_id:
      description: Hexadecimal ID of the primary volume.
      type: str
      sample: "00:04:06"
    secondary_volume_id:
      description: ID of the secondary volume.
      type: int
      sample: 1031
    secondary_hex_volume_id:
      description: Hexadecimal ID of the secondary volume.
      type: str
      sample: "00:04:07"
    svol_access_mode:
      description: Access mode of the secondary volume.
      type: str
      sample: ""
    pool_id:
      description: ID of the pool where the snapshot is allocated.
      type: int
      sample: 12
    consistency_group_id:
      description: ID of the consistency group.
      type: int
      sample: -1
    mirror_unit_id:
      description: ID of the mirror unit.
      type: int
      sample: 3
    copy_rate:
      description: Copy rate of the snapshot.
      type: int
      sample: -1
    copy_pace_track_size:
      description: Copy pace track size.
      type: str
      sample: ""
    status:
      description: Status of the snapshot.
      type: str
      sample: "PAIR"
    type:
      description: Type of the snapshot.
      type: str
      sample: ""
    snapshot_id:
      description: ID of the snapshot.
      type: str
      sample: "1030,3"
    is_consistency_group:
      description: Indicates if the snapshot is part of a consistency group.
      type: bool
      sample: true
    primary_or_secondary:
      description: Indicates if the volume is primary or secondary.
      type: str
      sample: "P-VOL"
    snapshot_group_name:
      description: Name of the snapshot group.
      type: str
      sample: "NewNameSPG"
    can_cascade:
      description: Indicates if the snapshot can be cascaded.
      type: bool
      sample: true
"""


from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    operation_constants,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPSnapshotArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
    CommonConstants,
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
class VSPHtiSnapshotManager:

    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPSnapshotArguments().get_snapshot_reconcile_args()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )
        try:

            self.params_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.params_manager.connection_info
            self.storage_serial_number = self.params_manager.storage_system_info.serial
            self.spec = self.params_manager.get_snapshot_reconcile_spec()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Snapshot operation ===")
        snapshot_data = None
        registration_message = validate_ansible_product_registration()

        try:

            snapshot_data = self.reconcile_snapshot()
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
            self.logger.writeInfo("=== End of Snapshot operation ===")
            self.module.fail_json(msg=str(e))

        if registration_message:
            resp["user_consent_required"] = registration_message

        self.logger.writeInfo(f"{resp}")
        self.logger.writeInfo("=== End of Snapshot operation ===")
        self.module.exit_json(**resp)

    def reconcile_snapshot(self):
        reconciler = VSPHtiSnapshotReconciler(
            self.connection_info,
            self.storage_serial_number,
        )
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            found = reconciler.check_storage_in_ucpsystem()
            if not found:
                raise ValueError(ModuleMessage.STORAGE_SYSTEM_ONBOARDING.value)

        result = reconciler.reconcile_snapshot(self.spec)

        #  20240826 TIA post processing
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            # result can be just a string on negative test cases
            snapshot = result
            if snapshot and isinstance(snapshot, dict):
                snapshot["can_cascade"] = False
                snapshot["is_cloned"] = ""
                snapshot["is_data_reduction_force_copy"] = False

                ttype = snapshot.get("type")
                if ttype == "CASCADE":
                    snapshot["is_data_reduction_force_copy"] = True
                    snapshot["can_cascade"] = True
                    snapshot["is_cloned"] = False
                elif ttype == "CLONE":
                    snapshot["is_data_reduction_force_copy"] = True
                    snapshot["can_cascade"] = True
                    snapshot["is_cloned"] = True

                #  20240826 inject the subscriber info
                snapshot["entitlement_status"] = "unassigned"
                subscriberId = self.connection_info.subscriber_id
                if subscriberId and subscriberId != "":
                    snapshot["entitlement_status"] = "assigned"
                    snapshot["partner_id"] = CommonConstants.PARTNER_ID
                    snapshot["subscriber_id"] = subscriberId

                result = snapshot

        return result


def main(module=None):
    obj_store = VSPHtiSnapshotManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
