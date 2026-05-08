#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_vsp_one_gad
short_description: Manages GAD pairs on VSP One block storage systems.
description:
  - This module allows for the creation, deletion, splitting, and resynchronization of GAD pairs on VSP One block storage systems.
  - It supports various GAD pairs operations based on the specified task level.
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
- hitachivantara.vspone_block.common.connection_info
options:
  state:
    description: Desired state of the GAD resource.
    type: str
    required: true
    choices: [present, absent, splitted, resynced]
  secondary_connection_info:
    description: Information required to establish a connection to the secondary storage system.
    required: false
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
        description: Password for authentication. This field is required for secondary storage connection api_token is not provided.
        type: str
        required: false
      api_token:
        description: Value of the lock token to operate on locked resources. Provide this only when operation is on locked resources.
        type: str
        required: false
  spec:
    description: Specification for the GAD pair operation.
    type: dict
    required: true
    suboptions:
      # --- Creation Parameters (state=present) ---
      consistency_group_id:
        description: The consistency group ID. Required for state present (create).
        type: int
        # required: true
      gad_pairs:
        description: List of GAD pair definitions. Required for state present (create).
        type: list
        elements: dict
        # required: true
        suboptions:
          primary_volume_id:
            description: The primary volume ID.
            type: int
            required: true
          provisioned_secondary_volume_id:
            description: The provisioned secondary volume ID.
            type: int
            required: false
      path_group_id:
        description: The path group ID. Required for state present (create).
        type: int
        # required: true
      quorum_id:
        description: The quorum ID. Required for state present (create).
        type: int
        # required: true
      secondary_storage_pool_id:
        description: The secondary storage pool ID. Required for state present (create).
        type: int
        # required: true
      secondary_servers:
        description: List of secondary servers.
        type: list
        elements: int
        required: false
      should_replicate_from_primary_to_secondary:
        description: Whether to replicate from primary to secondary.
        type: bool
        required: false
      copy_pace:
        description: The copy pace.
        type: int
        required: false
      mirror_unit_number:
        description: The mirror unit number.
        type: int
        required: false
        choices: [0, 1, 2, 3]
      io_priority_mode:
        description: The IO priority mode, values are 'DISABLE' or 'PRIMARY_ENABLE' and case insensitive.
        type: str
        required: false

      # --- Action Parameters (splitted/resynced/delete) ---
      primary_volume_mirrors:
        description: List of pairs for volume-level actions. Required for state splitted/resynced/delete.
        type: list
        elements: dict
        suboptions:
          primary_volume_id:
            description: The primary volume ID.
            type: int
            required: true
          mirror_unit_number:
            description: The mirror unit ID.
            type: int
            required: true
            choices: [0, 1, 2, 3]

      # --- Split Parameters (state=splitted) ---
      continue_io_volume:
        description: Which volume stays R/W during a split (PRIMARY or SECONDARY). Default is PRIMARY.
        type: str
        required: false

      # --- Resync Parameters (state=resynced) ---
      is_swap_resynced:
        description: Whether to perform a swap-resync (Secondary becomes new Primary).
        type: bool
        required: false
        default: false
      # copy_pace:
      #   description: Pace of synchronization (1-15). Default is 3.
      #   type: int
      #   required: false
      io_preference:
        description: I/O priority mode during path failure. Values are 'KEEP_CURRENT_SETTING', 'DISABLE', or 'PRIMARY_ENABLE'. Default is KEEP_CURRENT_SETTING.
        type: str
        required: false

      # --- Delete Parameters (state=absent) ---
      delete_mode:
        description: NORMAL or FORCE deletion. Default is NORMAL.
        type: str
        required: false
      allow_volume_access_after_force_delete:
        description: Required if delete_mode is FORCE. Whether to allow access to volumes after force deletion.
        type: bool
        required: false
"""

EXAMPLES = """
- name: Create GAD pairs with automatic provisioning
  hitachivantara.vspone_block.vsp.hv_vsp_one_gad:
    connection_info: "{{ connection_info }}"
    secondary_connection_info: "{{ secondary_connection_info }}"
    state: present
    spec:
      consistency_group_id: 1
      path_group_id: 0
      quorum_id: 22
      secondary_storage_pool_id: 2
      gad_pairs:
        - primary_volume_id: 385
          provisioned_secondary_volume_id: 85 # Optional
      should_replicate_from_primary_to_secondary: true
      copy_pace: 3
      mirror_unit_number: 1 # Optional

- name: Suspend (Split) GAD pairs
  hitachivantara.vspone_block.vsp.hv_vsp_one_gad:
    connection_info: "{{ connection_info }}"
    state: splitted
    spec:
      primary_volume_mirrors:
        - primary_volume_id: 100
          mirror_unit_number: 1
        - primary_volume_id: 200
          mirror_unit_number: 1
      continue_io_volume: primary

- name: Resync GAD pairs
  hitachivantara.vspone_block.vsp.hv_vsp_one_gad:
    connection_info: "{{ connection_info }}"
    state: sync
    spec:
      primary_volume_mirrors:
        - primary_volume_id: 100
          mirror_unit_number: 1
      is_swap_resynced: false
      copy_pace: 3
      io_preference: KEEP_CURRENT_SETTING

- name: Delete GAD pairs (Force Mode)
  hitachivantara.vspone_block.vsp.hv_vsp_one_gad:
    connection_info: "{{ connection_info }}"
    state: absent
    spec:
      primary_volume_mirrors:
        - primary_volume_id: 100
          mirror_unit_number: 1
      delete_mode: force
      allow_volume_access_after_force_delete: true
"""

RETURN = """
gad_pairs:
  description: List of GAD pairs returned from the operation.
  returned: always
  type: list
  elements: dict
  contains:
    consistency_group_id:
      description: The consistency group ID of the GAD pair.
      type: int
      sample: 6
    copy_progress_rate:
      description: The copy progress rate. -1 indicates copy is complete.
      type: int
      sample: -1
    copy_speed:
      description: The copy speed setting.
      type: int
      sample: 3
    copy_time:
      description: The copy time in seconds.
      type: int
      sample: 0
    data_synchronization_rate:
      description: The data synchronization rate percentage.
      type: int
      sample: 100
    failure_factor:
      description: The failure factor if any.
      type: str
      sample: "NONE"
    id:
      description: The GAD pair ID in format 'volume_id,mirror_unit_number'.
      type: str
      sample: "385,1"
    io_preference:
      description: The IO preference setting.
      type: str
      sample: "DISABLED"
    local_volume_differential_data_management:
      description: The differential data management type for the local volume.
      type: str
      sample: "HIERARCHICAL"
    local_volume_id:
      description: The local (primary) volume ID.
      type: int
      sample: 385
    local_volume_io_mode:
      description: The IO mode of the local volume.
      type: str
      sample: "MIRROR"
    local_volume_nickname:
      description: The nickname of the local volume.
      type: str
      sample: "NewGadTest"
    local_volume_position:
      description: The position of the local volume in the pair.
      type: str
      sample: "PRIMARY"
    local_volume_processing_status:
      description: The processing status of the local volume.
      type: str
      sample: "IDLE"
    local_volume_provisioning_type:
      description: The provisioning type of the local volume.
      type: str
      sample: "VIRTUAL"
    local_volume_status:
      description: The status of the local volume in the GAD pair.
      type: str
      sample: "PAIR"
    mirror_unit_number:
      description: The mirror unit number.
      type: int
      sample: 1
    pair_operation_mode_for_blocked_quorum_disk:
      description: The pair operation mode when quorum disk is blocked.
      type: str
      sample: "QUORUMLESS"
    quorum_id:
      description: The quorum ID used by the GAD pair.
      type: int
      sample: 22
    remote_connection_id:
      description: Remote connection information for the GAD pair.
      type: dict
      contains:
        path_group_id:
          description: The path group ID for the remote connection.
          type: int
          sample: 0
        storage_model:
          description: The model of the remote storage system.
          type: str
          sample: "RH20ETP"
        storage_serial_number:
          description: The serial number of the remote storage system.
          type: str
          sample: "70041"
    remote_volume_id:
      description: The remote (secondary) volume ID.
      type: int
      sample: 85
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)

# Utilities
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPOneGadArguments,
    VSPOneGadCtgArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_one_gad_ctg_reconciler import (
    VSPOneGadCtgReconciler,
)

# Reconcilers
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_one_gad_reconciler import (
    VspOneGadReconciler,
)


class VSPOneGadUnifiedManager:
    def __init__(self):
        self.logger = Log()

        # 1. Spec Merging Logic (Same as before)
        unified_spec = VSPOneGadArguments().get_vsp_one_gad_action_args()
        # ctg_action_spec = VSPOneGadCtgArguments().vsp_one_gad_ctg()
        creation_spec = VSPOneGadCtgArguments.get_vsp_one_gad_ctg_args()

        # unified_spec["spec"]["options"].update(ctg_action_spec["spec"]["options"])
        unified_spec["spec"]["options"].update(creation_spec["spec"]["options"])

        # 2. Add top-level secondary connection
        unified_spec["secondary_connection_info"] = {
            "required": False,
            "type": "dict",
            "options": {
                "address": {"type": "str", "required": True},
                "username": {"type": "str", "required": False},
                "password": {"type": "str", "required": False, "no_log": True},
                "api_token": {"type": "str", "required": False, "no_log": True},
            },
        }

        # 3. Programmatic strip of 'required' flags
        for option in unified_spec["spec"]["options"].values():
            if isinstance(option, dict):
                option["required"] = False

        self.module = AnsibleModule(argument_spec=unified_spec, supports_check_mode=False)

        try:
            spec_params = self.module.params.get("spec")
            if not spec_params:
                self.module.fail_json(msg="The 'spec' parameter is required.")

            # --- START OF WHITELIST FILTERING & ROUTING ---
            self.state = self.module.params.get("state")

            # MODE 1: Individual Volume Pairs
            if "primary_volume_mirrors" in spec_params and spec_params["primary_volume_mirrors"]:
                pair_keys = [
                    "primary_volume_mirrors",
                    "continue_io_volume",
                    "is_swap_resynced",
                    "copy_pace",
                    "io_preference",
                    "delete_mode",
                    "allow_volume_access_after_force_delete",
                ]
                # Filter the dictionary to only pair-specific keys
                self.module.params["spec"] = {k: v for k, v in spec_params.items() if k in pair_keys}

                # Initialize standard manager and spec
                self.params_manager = VSPParametersManager(self.module.params)
                self.spec = self.params_manager.get_vsp_one_gad_spec(self.state)
                self.use_ctg_reconciler = False

            # MODE 2: GAD Pair Creation (present)
            elif self.state == "present":
                create_keys = [
                    "consistency_group_id",
                    "gad_pairs",
                    "path_group_id",
                    "quorum_id",
                    "secondary_storage_pool_id",
                    "secondary_servers",
                    "should_replicate_from_primary_to_secondary",
                    "copy_pace",
                    "io_priority_mode",
                    "mirror_unit_number",
                ]
                self.module.params["spec"] = {k: v for k, v in spec_params.items() if k in create_keys}

                self.params_manager = VSPParametersManager(self.module.params)
                self.spec = self.params_manager.get_vsp_one_gad_ctg_create_spec()
                self.use_ctg_reconciler = True

            else:
                self.module.fail_json(msg="Could not determine GAD mode. Provide 'primary_volume_mirrors'.")

            # Common Connection Info
            self.connection_info = self.params_manager.get_connection_info()
            self.secondary_connection_info = self.params_manager.get_secondary_connection_info()

        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=f"Initialization failed: {str(e)}")

    def apply(self):
        self.logger.writeInfo(f"=== Start of Unified GAD Operation: {self.state} ===")
        registration_message = validate_ansible_product_registration()

        try:
            if self.use_ctg_reconciler:
                reconciler = VSPOneGadCtgReconciler(self.connection_info, self.secondary_connection_info)

                if self.state == "present":
                    reconcile_output = reconciler.vsp_one_gad_pair_reconcile(self.spec, self.state)
                else:
                    reconcile_output = reconciler.reconcile(self.state, self.spec)
            else:
                reconciler = VspOneGadReconciler(self.connection_info, self.secondary_connection_info)
                reconcile_output = reconciler.gad_pair_reconcile(self.state, self.spec)

            response_dict = {
                "changed": self.connection_info.changed,
                "gad_pairs": reconcile_output if isinstance(reconcile_output, list) else [],
                "count": len(reconcile_output) if isinstance(reconcile_output, list) else 0,
            }

            if hasattr(self.spec, "comments") and self.spec.comments:
                response_dict["msg"] = self.spec.comments

            if registration_message:
                response_dict["user_consent_required"] = registration_message

            self.module.exit_json(**response_dict)

        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=f"Operation failed: {str(e)}")


def main():
    module_instance = VSPOneGadUnifiedManager()
    module_instance.apply()


if __name__ == "__main__":
    main()
