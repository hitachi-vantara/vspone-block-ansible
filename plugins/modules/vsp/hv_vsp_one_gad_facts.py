#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_vsp_one_gad_facts
short_description: Retrieves GAD (Global-Active Device) information from VSP One storage systems.
description:
  - This module retrieves GAD pair information from VSP One Block 20/80 series and VSP E series storage systems.
version_added: '4.8.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
options:
  spec:
    description: Query parameters for filtering and paginating GAD pair information.
    type: dict
    required: false
    suboptions:
      consistency_group_id:
        description:
          - Filter results by a specific Consistency Group ID.
          - If omitted, GAD pairs from all consistency groups are retrieved.
        type: int
        required: false
      primary_volume_id:
        description:
          - Specifies the starting LDEV ID for cursor-based pagination.
          - When provided, retrieval begins at this volume ID. If the exact LDEV ID is not present, the operation falls back to the next available pair.
          - If I(count) is set to C(1), this parameter functions as a specific lookup for the designated LDEV.
          - This parameter acts as a starting offset for sequential retrieval and includes all subsequent LDEVs up to the specified I(count).
        type: int
        required: false
      mirror_unit_number:
        description:
          - The Mirror Unit (MU) number associated with the I(primary_volume_id) to start retrieval from.
          - If I(primary_volume_id) is specified but this is omitted, it defaults to 0.
          - All subsequent pairs, regardless of their Mirror Unit number, will be included in the results.
        type: int
        required: false
      count:
        description:
          - The maximum number of GAD pair entries to retrieve in a single operation.
          - Supports values from 1 to 500.
          - If set to C(1) alongside I(primary_volume_id), the module targets a specific GAD pair matching that LDEV ID and Mirror Unit.
          - If set to a value greater than C(1), it initiates a sequential retrieval. This begins at the specified cursor (or the next numerically
            available pair if the exact ID is missing) and includes all subsequent entries across all Mirror Units.
          - If omitted, this defaults to C(500), retrieving up to 500 pairs starting from the beginning of the list or the specified I(primary_volume_id).
        type: int
        default: 500
        required: false
extends_documentation_fragment:
  - hitachivantara.vspone_block.common.connection_info
"""

EXAMPLES = """
    # ######################################################################################
    # Task: Retrieve GAD pairs using the default batch size (500) from the beginning of the list.
    # ######################################################################################
    - name: Get all GAD pairs (default limit)
      hitachivantara.vspone_block.vsp.hv_vsp_one_gad_facts:
        connection_info: "{{ connection_info }}"
      register: result

    - name: Debug the result variable
      ansible.builtin.debug:
        var: result

    # ######################################################################################
    # Task: Retrieve a specific number of GAD pairs from the beginning of the list.
    # ######################################################################################
    - name: Get first 10 GAD pairs
      hitachivantara.vspone_block.vsp.hv_vsp_one_gad_facts:
        connection_info: "{{ connection_info }}"
        spec:
          count: 10
      register: result

    - name: Debug the result variable
      ansible.builtin.debug:
        var: result

    # ######################################################################################
    # Task: Retrieve first available gad pair.
    # ######################################################################################
    - name: Get first available GAD pair
      hitachivantara.vspone_block.vsp.hv_vsp_one_gad_facts:
        connection_info: "{{ connection_info }}"
        spec:
          count: 1
      register: result

    - name: Debug the result variable
      ansible.builtin.debug:
        var: result

    # ######################################################################################
    # Task: Filter GAD pairs by Consistency Group ID.
    # Returns an empty list if no pairs are associated with the specified group.
    # ######################################################################################
    - name: Get GAD pairs for Consistency Group 2
      hitachivantara.vspone_block.vsp.hv_vsp_one_gad_facts:
        connection_info: "{{ connection_info }}"
        spec:
          consistency_group_id: 2
      register: result

    - name: Debug the result variable
      ansible.builtin.debug:
        var: result

    # ######################################################################################
    # Task: Retrieve a single GAD pair from a specific Consistency Group.
    # ######################################################################################
    - name: Get a single GAD pair from Consistency Group 2
      hitachivantara.vspone_block.vsp.hv_vsp_one_gad_facts:
        connection_info: "{{ connection_info }}"
        spec:
          consistency_group_id: 2
          count: 1
      register: result

    # ######################################################################################
    # Task: Retrieve information for a specific LDEV and Mirror Unit.
    # Set count to 1 to find only this specific GAD pair LDEVID/MU.
    # ######################################################################################
    - name: Get specific GAD pair by LDEV and MU
      hitachivantara.vspone_block.vsp.hv_vsp_one_gad_facts:
        connection_info: "{{ connection_info }}"
        spec:
          primary_volume_id: 244
          mirror_unit_number: 3
          count: 1
      register: result

    - name: Debug the result variable
      ansible.builtin.debug:
        var: result

    # ######################################################################################
    # Task: Retrieve specific GAD pair using the default Mirror Unit (0).
    # Set count to 1 to find only this specific GAD pair LDEVID/MU.
    # ######################################################################################
    - name: Get GAD pair by LDEV ID (Default MU 0)
      hitachivantara.vspone_block.vsp.hv_vsp_one_gad_facts:
        connection_info: "{{ connection_info }}"
        spec:
          primary_volume_id: 244
          count: 1
      register: result

    # ######################################################################################
    # Task: Cursor-based batch retrieval.
    # Starts at LDEV 249 / MU 3 if present; otherwise, falls back to the next available
    # pair in numerical order. Results include all subsequent Mirror Units and volumes.
    # ######################################################################################
    - name: Get batch of 10 pairs starting from a gad pair
      hitachivantara.vspone_block.vsp.hv_vsp_one_gad_facts:
        connection_info: "{{ connection_info }}"
        spec:
          primary_volume_id: 249
          mirror_unit_number: 3
          count: 10
      register: result

    - name: Debug the result variable
      ansible.builtin.debug:
        var: result

    # ######################################################################################
    # Task: Sequential retrieval starting from a volume-level cursor.
    # Defaults to Mirror Unit 0. Retrieval starts from the specified ID or the next
    # available numerical match up to the maximum batch limit (500).
    # ######################################################################################
    - name: Get up to 500 pairs starting from Volume 249
      hitachivantara.vspone_block.vsp.hv_vsp_one_gad_facts:
        connection_info: "{{ connection_info }}"
        spec:
          primary_volume_id: 249
      register: result

    - name: Debug the result variable
      ansible.builtin.debug:
        var: result
"""

RETURN = """
ansible_facts:
  description: The list of GAD pairs retrieved from the storage system.
  returned: success
  type: dict
  contains:
    gad_pairs:
      description: List of dictionaries containing detailed GAD pair properties.
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

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_one_gad_reconciler import (
    VspOneGadReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPOneGadArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class VSPOneGadFactsManager:
    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPOneGadArguments().get_vsp_one_gad_facts_args()

        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        try:
            params_manager = VSPParametersManager(self.module.params)
            self.spec = params_manager.get_vsp_one_gad_facts_spec()
            self.connection_info = params_manager.get_connection_info()
        except Exception as e:
            self.module.fail_json(msg="Initialization failed: {0}".format(str(e)))

    def apply(self):
        self.logger.writeInfo("=== Start of VSP One GAD Facts Retrieval ===")
        registration_message = validate_ansible_product_registration()

        try:
            reconciler = VspOneGadReconciler(self.connection_info)
            gad_pairs = reconciler.get_gad_pairs_facts(self.spec)
            count = len(gad_pairs) if gad_pairs else 0

            response_dict = {"gad_pairs": gad_pairs if gad_pairs else [], "count": count}
            if self.spec.comments:
                response_dict["comments"] = self.spec.comments

            if registration_message:
                response_dict["user_consent_required"] = registration_message

            self.logger.writeInfo(f"Retrieved {count} GAD pairs.")
            self.logger.writeInfo("=== End of VSP One GAD Facts Retrieval ===")
            self.module.exit_json(changed=False, ansible_facts=response_dict)

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of VSP One GAD Facts Retrieval ===")
            self.module.fail_json(msg=str(e))


def main():
    module_instance = VSPOneGadFactsManager()
    module_instance.apply()


if __name__ == "__main__":
    main()
