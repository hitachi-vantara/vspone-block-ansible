#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function


__metaclass__ = type


DOCUMENTATION = """
---
module: hv_sds_block_snapshot
short_description: Manages snapshots on Hitachi SDS Block storage systems.
description:
  - This module allows you to create, prepare, and finalize snapshots on Hitachi SDS Block storage systems.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/snapshot.yml)
version_added: "4.1.0"
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.9
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: none
extends_documentation_fragment:
  - hitachivantara.vspone_block.common.sdsb_connection_info
options:
  state:
    description: The desired state of the snapshot.
    type: str
    required: false
    choices: ["present", "absent", "restore"]
    default: 'present'
  spec:
    description: Specification for the snapshot operation.
    type: dict
    required: true
    suboptions:
      name:
        description: The name of the snapshot.
        type: str
        required: false
      master_volume_name:
        description: The name of the master volume.
        type: str
        required: false
      master_volume_id:
        description: The ID of the master volume.
        type: str
        required: false
      snapshot_volume_name:
        description: The name of the snapshot volume.
        type: str
        required: false
      snapshot_volume_id:
        description: The ID of the snapshot volume.
        type: str
        required: false
      operation_type:
        description: The type of snapshot operation.
        type: str
        required: false
        choices: ["prepare_and_finalize", "prepare", "finalize"]
      vps_id:
        description: The ID of the VPS.
        type: str
        required: false
      vps_name:
        description: The name of the VPS.
        type: str
        required: false
      qos:
        description: QoS settings for the snapshot.
        type: dict
        required: false
        suboptions:
          upper_limit_for_iops:
            description: Upper limit for IOPS.
            type: int
            required: false
          upper_limit_for_transfer_rate:
            description: Upper limit for transfer rate.
            type: int
            required: false
          upper_alert_allowable_time:
            description: Upper alert allowable time.
            type: int
            required: false
"""

EXAMPLES = """
- name: Create a snapshot (present)
  hitachivantara.vspone_block.sds_block.hv_sds_block_snapshot:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    state: "present"
    spec:
      name: "snapshot1"
      master_volume_name: "volume1"
      operation_type: "prepare_and_finalize"

- name: Delete a snapshot (absent)
  hitachivantara.vspone_block.sds_block.hv_sds_block_snapshot:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    state: "absent"
    spec:
      snapshot_volume_name: "snapshot1"

- name: Restore a snapshot (restore)
  hitachivantara.vspone_block.sds_block.hv_sds_block_snapshot:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    state: "restore"
    spec:
      snapshot_volume_name: "snapshot1"
"""

RETURN = """

"""
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_snapshot_reconciler import (
    SDSBSnapshotReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBSnapshotArguments,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class SDSBSnapShotManager:
    def __init__(self):
        self.logger = Log()
        self.argument_spec = SDSBSnapshotArguments().snapshot_args()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )
        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()
        self.spec = parameter_manager.get_sdsb_snapshot_spec()
        self.state = parameter_manager.get_state()

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB Snapshot Operation ===")
        storage_nodes = None
        registration_message = validate_ansible_product_registration()
        try:
            sdsb_reconciler = SDSBSnapshotReconciler(self.connection_info)
            storage_nodes, msg = sdsb_reconciler.snapshot_reconcile(
                self.state, self.spec
            )
        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB Snapshot Operation ===")
            self.module.fail_json(msg=str(e))
        data = {
            "snapshot_info": storage_nodes,
            "changed": self.connection_info.changed,
            "message": msg,
        }
        if registration_message:
            data["user_consent_required"] = registration_message

        self.logger.writeInfo("=== End of SDSB Snapshot Operation ===")
        self.module.exit_json(**data)


def main():
    obj_store = SDSBSnapShotManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
