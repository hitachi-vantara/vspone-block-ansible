#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = """
---
module: hv_vsp_one_gad_consistency_group
short_description: Manages GAD pairs in a consistency group on VSP One block storage systems.
description:
  - This module allows for the splitting, and resynchronization of GAD pairs in a consistency group on VSP One block storage systems.
  - It supports various GAD pairs operations based on the specified task level.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/vsp_one_gad_consistency_group.yml)
version_added: '4.8.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.9
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: none
extends_documentation_fragment:
- hitachivantara.vspone_block.common.gateway_note
- hitachivantara.vspone_block.common.connection_with_type
- hitachivantara.vspone_block.common.gad_note
options:
  state:
    description: The level of the GAD consistency group task.
    type: str
    required: false
    choices: [ 'present', 'absent', 'suspended', 'resynced' ]
    default: 'present'
  secondary_connection_info:
    description: Information required to establish a connection to the secondary storage system.
    required: true
    type: dict
    suboptions:
      address:
        description: IP address or hostname of the secondary storage.
        type: str
        required: true
      username:
        description: Username for authentication. This field is required for secondary storage connection if api_token is not provided.
        type: str
        required: false
      password:
        description: Password for authentication. This field is required for secondary storage connection if api_token is not provided.
        type: str
        required: false
      api_token:
        description: Value of the lock token to operate on locked resources.
        type: str
        required: false
  spec:
    description: Specification for the GAD consistency group task.
    type: dict
    required: true
    suboptions:
      consistency_group_ids:
        description:
          - List of consistency group IDs.
          - Each consistency group ID must be an integer in the range 0 to 1023 (inclusive).
        required: true
        type: list
        elements: int
      copy_pace:
        description:
          - The copy pace for the resync operation.
          - Higher values indicate faster copy speed.
          - Valid values are integers from 1 to 15.
        required: false
        type: int
        default: 3
      io_preference_mode:
        description:
          - The I/O preference mode for the resync operation.
          - Determines how I/O is handled during the resync process.
          - Valid values are KEEP_CURRENT_SETTING, DISABLED, or PRIMARY_ENABLED. Case insensitive.
        required: false
        type: str
      continue_io_volume:
        description:
          - The volume to continue I/O on during the suspend operation.
          - Specifies which volume should remain active for I/O while suspending.
          - Valid values are PRIMARY or SECONDARY. Case insensitive.
        required: false
        type: str
"""

EXAMPLES = """
- name: Suspend GAD pairs using consistency group Ids
  hitachivantara.vspone_block.vsp.hv_gad:
    state: "suspended"
    connection_info:
      address: storage1.company.com
      username: "username"
      password: "password"
    secondary_connection_info:
      address: storage2.company.com
      username: "admin"
      password: "secret"
    spec:
      consistency_group_ids: [0, 1]
      continue_io_volume: "PRIMARY"

- name: Resync GAD pairs using consistency group Ids
  hitachivantara.vspone_block.vsp.hv_gad:
    state: "swap_resync"
    connection_info:
      address: storage2.company.com
      username: "username"
      password: "password"
    secondary_connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    spec:
      consistency_group_ids: [0, 1]
      copy_pace: 10
      io_preference_mode: "KEEP_CURRENT_SETTING"
"""

RETURN = """
gad_pairs:
  description: List of dictionaries containing detailed GAD pair properties.
  returned: always
  type: list
  elements: dict
  contains:
    primary_volume_id:
      description: LDEV ID of the local (primary) volume.
      type: int
      sample: 244
    primary_volume_id_hex:
      description: Hexadecimal representation of the primary volume ID.
      type: str
      sample: "00:00:F4"
    mirror_unit_number:
      description: Mirror Unit (MU) number.
      type: int
      sample: 0
    primary_volume_name:
      description: Nickname or name assigned to the primary volume.
      type: str
      sample: "GadTest"
    primary_volume_provisioning_type:
      description: Provisioning type (INTERNAL, VIRTUAL, or EXTERNAL).
      type: str
      sample: "VIRTUAL"
    remote_connection_id:
      description: Information about the remote storage system connection.
      type: dict
      contains:
        storage_model:
          description: Model of the remote storage (e.g., RH20ETP).
          type: str
          sample: "RH20ETP"
        storage_serial_number:
          description: Serial number of the remote storage.
          type: str
          sample: "70041"
        path_group_id:
          description: ID of the path group used for the connection.
          type: int
          sample: 0
    secondary_volume_id:
      description: LDEV ID of the volume on the remote storage system.
      type: int
      sample: 55
    secondary_volume_id_hex:
      description: Hexadecimal representation of the secondary volume ID.
      type: str
      sample: "00:00:37"
    primary_volume_status:
      description: Current pair status (PAIR, COPY, PSUS, etc.).
      type: str
      sample: "PAIR"
    primary_volume_processing_status:
      description: Capacity expansion status (IDLE, EXPANDING).
      type: str
      sample: "IDLE"
    failure_factor:
      description: Reason for GAD pair failure, if any.
      type: str
      sample: "NONE"
    primary_volume_position:
      description: Role of the local volume (PRIMARY or SECONDARY).
      type: str
      sample: "PRIMARY"
    primary_volume_io_mode:
      description: Host I/O behavior (MIRROR, LOCAL, BLOCK).
      type: str
      sample: "MIRROR"
    copy_pace:
      description: Speed of the copy operation (1-15).
      type: int
      sample: 3
    io_preference:
      description: I/O preference settings.
      type: str
      sample: "DISABLED"
    pair_operation_mode_for_blocked_quorum_disk:
      description: Behavior when the quorum disk is blocked.
      type: str
      sample: "QUORUMLESS"
    copy_progress_rate:
      description: Percentage of initial copy completion.
      type: int
      sample: -1
    data_synchronization_rate:
      description: Synchronization percentage between volumes.
      type: int
      sample: 100
    copy_time:
      description: Total seconds taken to reach PAIR status.
      type: int
      sample: 0
    created_time:
      description: Timestamp of pair creation.
      type: str
      sample: "2024-10-01T10:00:00Z"
    local_last_updated_time:
      description: Timestamp of the last local update.
      type: str
      sample: "2024-10-01T10:05:00Z"
    primary_volume_differential_data_management:
      description: Method used for differential data management.
      type: str
      sample: "HIERARCHICAL"
    quorum_disk_id:
      description: ID of the quorum disk used for the GAD pair.
      type: int
      sample: 22
    consistency_group_id:
      description: ID of the consistency group the pair belongs to.
      type: int
      sample: 2
count:
  description: The number of GAD pairs retrieved and stored in ansible_facts.
  type: int
  returned: success
  sample: 2
"""


from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_one_gad_ctg_reconciler import (
    VSPOneGadCtgReconciler,
)
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPOneGadCtgArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class VspOneGadCtgManager:

    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPOneGadCtgArguments().vsp_one_gad_ctg()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )
        try:
            params_manager = VSPParametersManager(self.module.params)
            self.spec = params_manager.get_vsp_one_gad_ctg_spec()
            self.connection_info = params_manager.get_connection_info()
            self.state = params_manager.get_state()
            self.secondary_connection_info = params_manager.get_secondary_connection_info()
            self.logger.writeDebug(f"GAD pairs after reconciliation: {self.spec}")
        except Exception as e:
            self.logger.writeError(f"An error occurred during initialization: {str(e)}")
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of VSP One GAD consistency group Operation ===")
        gad_pairs = None
        registration_message = validate_ansible_product_registration()
        response = None

        try:
            gad_reconciler = VSPOneGadCtgReconciler(self.connection_info, self.secondary_connection_info)
            gad_pairs = gad_reconciler.reconcile(self.state, self.spec)

            self.logger.writeDebug(f"GAD pairs after reconciliation: {gad_pairs}")
            count = 0
            if gad_pairs is not None:
                if isinstance(gad_pairs, list):
                    count = len(gad_pairs)
                elif isinstance(gad_pairs, dict):
                    count = 1
            response = {
                "changed": self.connection_info.changed,
                "gad_pairs": gad_pairs if gad_pairs is not None else [],
                "count": count,
                # "comments": self.spec.comments if self.spec.comments else [],
                # "errors": self.spec.errors if self.spec.errors else [],
            }
            if self.spec.comments:
                response["comments"] = self.spec.comments

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of VSP One GAD consistency group Operation ===")
            self.module.fail_json(msg=str(e))

        if registration_message:
            response["user_consent_required"] = registration_message
        self.logger.writeInfo("=== End of VSP One GAD consistency group Operation ===")
        self.module.exit_json(**response)


def main():
    obj_store = VspOneGadCtgManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
