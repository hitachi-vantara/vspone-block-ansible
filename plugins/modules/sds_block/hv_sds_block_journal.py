#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_sds_block_journal
short_description: Create and update Journals from storage system
description:
  - Create and update Journals from storage system.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/sds_block_journal.yml)
version_added: "4.6.0"
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
    description: The level of the journal task.
    type: str
    required: false
    choices: ['present', 'update', 'absent', 'shrink_journal', 'expand_journal']
    default: 'present'
  spec:
    description: Specification for the journal to be added to or updated in storage.
    type: dict
    required: false
    suboptions:
      id:
        description: The ID of the journal.
        type: str
        required: false
      number:
        description: Journal number to be created or updated.
        type: int
        required: false
      volume_ids:
        description: A list of IDs of the volumes to be added to a journal.
        type: list
        elements: str
      data_overflow_watch_in_sec:
        description: Monitoring time for data overflow (unit in seconds).
        type: int
        required: false
      enable_inflow_control:
        description: Specifies whether to restrict update I/O inflow to a journal volume (by delaying response to host I/Os).
        type: bool
        required: false
      enable_cache_mode:
        description: Specifies whether to enable the cache mode setting.
        type: bool
        required: false
      vps_id:
        description: The ID of the operation-target virtual private storage (VPS).
        type: str
        required: false
      vps_name:
        description: The name of the operation-target virtual private storage (VPS).
        type: str
        required: false
      mirror_unit:
        description: Mirror unit configuration for the journal.
        type: dict
        required: false
        suboptions:
          number:
            description: Mirror unit number.
            type: int
            required: true
          copy_pace:
            description: Copy pace setting for the mirror unit.
            type: str
            choices: ['L', 'M', 'H']
            required: false
          data_transfer_speed_bps:
            description: Data transfer speed in bytes per second.
            type: str
            choices: ['3M', '10M', '100M', '256M']
            required: false
"""

EXAMPLES = """
- name: Creates a journal and adds a journal volume to the journal
  hitachivantara.vspone_block.sds_block.hv_sds_block_journal:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    state: present
    spec:
      number: 3
      volume_ids:
        - "537be416-6d0d-4da6-98cd-fccb76bb3451"
      data_overflow_watch_in_sec: 60
      enable_inflow_control: false
      enable_cache_mode: false
      vps_id: "system"
- name: Update a existing journal
  hitachivantara.vspone_block.sds_block.hv_sds_block_journal:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    state: present
    spec:
      id: ""
      number: 3
      data_overflow_watch_in_sec: 150
      enable_inflow_control: false
      enable_cache_mode: true
      vps_id: "system"
      vps_name: "system"
      mirror_unit:
        number: 0
        copy_pace: "M"
        data_transfer_speed_bps: "3M"

- name: Get journal info by ID
  hitachivantara.vspone_block.sds_block.hv_sds_block_journal:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    state: present
    spec:
      id: "id-of-journal"
      number: 3

- name: Delete a journal
  hitachivantara.vspone_block.sds_block.hv_sds_block_journal:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    state: absent
    spec:
      id: "id-of-journal"
      number: 3

- name: Expand add volume to a journal
  hitachivantara.vspone_block.sds_block.hv_sds_block_journal:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    state: expand_journal
    spec:
      id: "id-of-journal"
      number: 3
      volume_ids:
        - "ad58c370-7a55-4bd5-91ce-70ed71050835"
      vps_id: "system"
      vps_name: "system"

- name: Shrink (delete volume from) a journal
  hitachivantara.vspone_block.sds_block.hv_sds_block_journal:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    state: shrink_journal
    spec:
      id: "id-of-journal"
      number: 3
      volume_ids:
        - "1322e160-fac4-4ac7-9b71-5c1c1ea294ca"
      vps_id: "system"
      vps_name: "system"
"""
RETURN = r"""
journals:
  description: >
    Dictionary containing journal information discovered or managed on the system.
  returned: always
  type: dict
  contains:
    data:
      description: List of journal entries.
      type: list
      elements: dict
      contains:
        id:
          description: Unique identifier of the journal.
          type: str
          sample: "551a8c21-caae-4d4f-8f5f-c4f3dbc5374f"
        journal_number:
          description: Journal number assigned by the system.
          type: int
          sample: 0
        storage_controller_id:
          description: Identifier of the associated storage controller.
          type: str
          sample: "f330c421-5c9b-4f3a-8b4f-12268053dc60"
        vps_id:
          description: VPS identifier associated with the journal.
          type: str
          sample: "(system)"
        vps_name:
          description: VPS name associated with the journal.
          type: str
          sample: "(system)"
        capacity:
          description: Capacity of the journal in megabytes or relevant unit.
          type: int
          sample: 11264
        block_capacity:
          description: Block capacity of the journal.
          type: int
          sample: 23068672
        volume_ids:
          description: List of associated journal volume IDs.
          type: list
          elements: str
          sample: ["2a0fa47c-2343-418b-b60f-18580cd86d67"]
        data_overflow_watch_in_seconds:
          description: Threshold (in seconds) for detecting data overflow in the journal.
          type: int
          sample: 60
        is_inflow_control_enabled:
          description: Indicates if inflow control is enabled for the journal.
          type: bool
          sample: true
        is_cache_mode_enabled:
          description: Indicates if cache mode is enabled for the journal.
          type: bool
          sample: true
        usage_rate:
          description: Current usage rate of the journal.
          type: str
          sample: ""
        q_marker:
          description: Queue marker information, if available.
          type: str
          sample: ""
        q_count:
          description: Queue count information, if available.
          type: str
          sample: ""
        status:
          description: Current operational status of the journal.
          type: str
          sample: "Normal"
        mirror_units:
          description: List of mirror units associated with the journal.
          type: list
          elements: dict
          contains:
            mu_number:
              description: Mirror unit number.
              type: int
              sample: 2
            consistency_group_id:
              description: Identifier of the consistency group the mirror unit belongs to.
              type: int
              sample: -1
            journal_status:
              description: Current status of the mirror unit.
              type: str
              sample: "SMPL"
            copy_pace:
              description: Copy pace setting for the mirror unit (e.g., L, M, H).
              type: str
              sample: "L"
            copy_speed:
              description: Copy speed configured for the mirror unit.
              type: str
              sample: "256M"
            number_of_active_paths:
              description: Number of active data paths for the mirror unit.
              type: str
              sample: ""
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBJournalArguments,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_journal_reconciler import (
    SDSBJournalReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class SDSBBJournalManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = SDSBJournalArguments().journals()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )
        try:
            parameter_manager = SDSBParametersManager(self.module.params)
            self.connection_info = parameter_manager.get_connection_info()
            self.spec = parameter_manager.get_journals_spec()
            self.state = parameter_manager.get_state()
            self.logger.writeDebug(f"MOD:hv_sds_journal:spec= {self.spec}")
        except Exception as e:
            self.logger.writeError(f"An error occurred during initialization: {str(e)}")
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB Journal Operation ===")
        journals = None
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_reconciler = SDSBJournalReconciler(self.connection_info)
            journals = sdsb_reconciler.reconcile_journal(self.spec, self.state)

            self.logger.writeDebug(f"MOD:hv_sds_journal:journals= {journals}")

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB journals Operation ===")
            self.module.fail_json(msg=str(e))

        data = {
            "changed": self.connection_info.changed,
            "journals": journals,
        }
        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo("=== End of SDSB Journals Operation ===")
        self.module.exit_json(**data)


def main():
    obj_store = SDSBBJournalManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
