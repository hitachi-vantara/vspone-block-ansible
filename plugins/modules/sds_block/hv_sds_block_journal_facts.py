#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_sds_block_journal_facts
short_description: Retrieve journal information from storage SDS Block storage system
description:
  - Collects journal details from the storage SDS Block storage system.
  - For usage examples, refer to
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/sdsb_journal_facts.yml)
version_added: "4.6.0"
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.9
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: full
extends_documentation_fragment:
  - hitachivantara.vspone_block.common.sdsb_connection_info
options:
  spec:
    description: Filter criteria for retrieving journal information.
    type: dict
    required: false
    suboptions:
      storage_controller_id:
        type: str
        description: The ID of the storage controller to filter journals.
        required: false
      number:
        type: int
        description: Journal number to filter journals.
        required: false
      vps_id:
        type: str
        description: The ID of the virtual private storage (VPS) to filter journals.
        required: false
      vps_name:
        type: str
        description: The name of the virtual private storage (VPS) to filter journals.
        required: false
"""

EXAMPLES = """
- name: Get all journal
  hitachivantara.vspone_block.sds_block.hv_sds_journal_facts:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"

- name: Get journal by VSP ID
  hitachivantara.vspone_block.sds_block.hv_sds_journal_facts:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      vsp_id: "system"

- name: Get journal by Storage Controller ID
  hitachivantara.vspone_block.sds_block.hv_sds_journal_facts:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      storage_controller_id: "f330c421-5c9b-4f3a-8b4f-12268053dc60"

- name: Get journal by number
  hitachivantara.vspone_block.sds_block.hv_sds_journal_facts:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      number: "0"
"""

RETURN = r"""
ansible_facts:
  description: >
    Dictionary containing Journal information discovered from the system.
  returned: always
  type: dict
  contains:
    journals:
      description: List of journal.
      type: list
      elements: dict
      contains:
        id:
          description: Journal ID.
          type: str
          sample: "551a8c21-caae-4d4f-8f5f-c4f3dbc5374f"
        journal_number:
          description: Journal number.
          type: int
          sample: 0
        storage_controller_id:
          description: Storage controller ID.
          type: str
          sample: "f330c421-5c9b-4f3a-8b4f-12268053dc60"
        vps_id:
          description: The ID of a virtual private storage (VPS) to which the resource to be obtained belongs.
          type: str
          sample: "(system)"
        vps_name:
          description: The name of the virtual private storage (VPS) to which the resource to be obtained belongs.
          type: str
          sample: "(system)"
        capacity:
          description: Journal volume capacity.
          type: int
          sample: 11264
        block_capacity:
          description: The number of journal volume blocks.
          type: int
          sample: 23068672
        volume_ids:
          description: A list of IDs of the volumes composing a journal volume.
          type: list
          sample: ["2a0fa47c-2343-418b-b60f-18580cd86d67"]
        data_overflow_watch_in_seconds:
          description: Monitoring time for data overflow.
          type: int
          sample: 60
        is_inflow_control_enabled:
          description: Indicates whether to restrict update I/O inflow to a journal volume.
          type: bool
          sample: true
        is_cache_mode_enabled:
          description: Indicates whether the cache mode setting is enabled.
          type: bool
          sample: true
        usage_rate:
          description: Usage of a journal volume.
          type: int
          sample: ""
        q_marker:
          description: The latest sequence number written to the cache.
          type: str
          sample: ""
        q_count:
          description: The number of qMarkers remaining in the master journal volume.
          type: int
          sample: ""
        status:
          description: Journal status.
          type: str
          sample: "Normal"
        mirror_units:
          description: A list of mirror units of the volumes registered in a journal.
          type: list
          elements: dict
          contains:
            mu_number:
              description: The mirror number (MU number).
              type: int
              sample: 2
            consistency_group_id:
              description: Consistency group ID.
              type: int
              sample: -1
            journal_status:
              description: The journal status of a mirror.
              type: str
              sample: "SMPL"
            copy_pace:
              description: Copy speed.
              type: str
              sample: "L"
            copy_speed:
              description: Data-transfer speed.
              type: str
              sample: "256M"
            number_of_active_paths:
              description: The number of paths of an active link.
              type: int
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


class SDSBJournalFactsManager:

    def __init__(self):

        self.logger = Log()
        self.argument_spec = SDSBJournalArguments().get_journal_facts_args()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        try:
            parameter_manager = SDSBParametersManager(self.module.params)
            self.connection_info = parameter_manager.get_connection_info()
            self.spec = parameter_manager.get_journal_spec()
            self.logger.writeDebug(f"MOD:hv_sds_journal_facts:spec= {self.spec}")
        except Exception as e:
            self.logger.writeError(f"An error occurred during initialization: {str(e)}")
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB Journal Facts ===")
        journals = None
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_reconciler = SDSBJournalReconciler(self.connection_info)
            journals = sdsb_reconciler.get_journals(self.spec)

            self.logger.writeDebug(f"MOD:hv_sds_journal_facts:journals= {journals}")

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB Journal Facts ===")
            self.module.fail_json(msg=str(e))

        data = {"journals": journals}
        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo("=== End of SDSB Journal Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)


def main():
    obj_store = SDSBJournalFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
