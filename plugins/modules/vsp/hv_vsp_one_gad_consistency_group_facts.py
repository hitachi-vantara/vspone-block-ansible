#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = """
---
module: hv_vsp_one_gad_consistency_group_facts
short_description: Retrieves consistency group of GAD pairs from VSP One storage systems.
description:
  - This module allows to fetch consistency groups of GAD pairs on VSP One storage systems.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/vsp_one_gad_consistency_group_facts.yml)
version_added: '4.8.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.9
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: full
extends_documentation_fragment:
- hitachivantara.vspone_block.common.connection_with_type
options:
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
        description: Password for authentication. This field is required for secondary storage connection api_token is not provided.
        type: str
        required: false
      api_token:
        description: Value of the lock token to operate on locked resources. Provide this only when operation is on locked resources.
        type: str
        required: false
  spec:
    description: Specification for the GAD pairs task.
    type: dict
    required: false
    suboptions:
      consistency_group_id:
        description: Consistency group ID. Required for the Get GAD pair using consistency group ID task.
        type: int
        required: false
"""

EXAMPLES = """
- name: Get all consistency groups for GAD pairs
  hitachivantara.vspone_block.vsp.hv_gad_facts:
    connection_info:
      address: storage1.company.com
      username: "username"
      password: "password"
    secondary_connection_info:
      address: storage2.company.com
      username: "admin"
      password: "secret"

- name: Get specific consistency group for GAD pairs
  hitachivantara.vspone_block.vsp.hv_gad_facts:
    connection_info:
      address: storage1.company.com
      username: "username"
      password: "password"
    secondary_connection_info:
      address: storage2.company.com
      username: "admin"
      password: "secret"
    spec:
      consistency_group_id: 1
"""

RETURN = """
ansible_facts:
  description: >
    Dictionary containing the discovered properties of the GAD pairs.
  returned: success
  type: dict
  contains:
    gad_consistency_groups:
      description: Details of the GAD (Global Active Device) consistency group configuration.
      returned: success
      type: dict
      contains:
        id:
          description: Identifier of the GAD pair.
          type: int
          sample: 1
        io_preference:
          description: I/O preference setting for the GAD pair.
          type: str
          sample: "DISABLED"
        local_volume_io_modes:
          description: List of I/O modes for the local volumes.
          type: list
          elements: str
          sample: ["MIRROR"]
        local_volume_positions:
          description: Positions of the local volumes in the pair.
          type: list
          elements: str
          sample: ["PRIMARY"]
        local_volume_statuses:
          description: Statuses of the local volumes.
          type: list
          elements: str
          sample: ["PAIR"]
        mirror_unit_number:
          description: Mirror unit number associated with the pair.
          type: int
          sample: 0
        number_of_pairs:
          description: Total number of pairs in the configuration.
          type: int
          sample: 1
        pair_operation_modes_for_blocked_quorum_disk:
          description: Operation modes when quorum disk is blocked.
          type: list
          elements: str
          sample: ["QUORUMLESS"]
        quorum_disk_id:
          description: Identifier of the quorum disk.
          type: int
          sample: 22
        remote_connection_id:
          description: Remote storage connection details.
          type: dict
          contains:
            path_group_id:
              description: Path group ID for the remote connection.
              type: int
              sample: 0
            storage_model:
              description: Model of the remote storage system.
              type: str
              sample: "RH20ETP"
            storage_serial_number:
              description: Serial number of the remote storage system.
              type: str
              sample: "70041"
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


class VspOneGadCtgFactsManager:

    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPOneGadCtgArguments().vsp_one_gad_ctg_facts()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.get_vsp_one_gad_ctg_facts_spec()
            self.serial = self.params_manager.get_serial()
            self.connection_info = self.params_manager.get_connection_info()
            self.state = self.params_manager.get_state()
            self.secondary_connection_info = (
                self.params_manager.get_secondary_connection_info()
            )
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of VSP One GAD Consistency Group Facts ===")
        registration_message = validate_ansible_product_registration()
        try:
            reconciler = VSPOneGadCtgReconciler(
                self.connection_info,
                self.secondary_connection_info,
            )
            response = reconciler.gad_ctg_facts(self.spec)

            result = response if response else []
            count = 0
            if response is not None:
                if isinstance(response, list):
                    count = len(response)
                elif isinstance(response, dict):
                    count = 1
            response_dict = {
                "gad_consistency_groups": result,
                "count": count,
            }
            if registration_message:
                response_dict["user_consent_required"] = registration_message
            self.logger.writeInfo(f"{response_dict}")
            self.logger.writeInfo("=== End of VSP One GAD Consistency Group Facts ===")
            self.module.exit_json(changed=False, ansible_facts=response_dict)
        except Exception as ex:
            self.logger.writeException(ex)
            self.logger.writeInfo("=== End of VSP One GAD Consistency Group Facts ===")
            self.module.fail_json(msg=str(ex))


def main():
    obj_store = VspOneGadCtgFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
