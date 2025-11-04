#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function


__metaclass__ = type


DOCUMENTATION = """
---
module: hv_sds_block_storage_controller
short_description: Edits the settings for the storage controller on Hitachi SDS Block storage systems.
description:
  - This module edits the settings for the storage controller on Hitachi SDS Block storage systems.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/sdsb_storage_controller.yml)
version_added: "4.2.0"
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
    description: The desired state of the storage pool.
    type: str
    required: false
    choices: ["present"]
    default: "present"
  spec:
    description: Specification for the storage controller.
    type: dict
    required: false
    suboptions:
      id:
        description: The ID of the storage controller. This field is required if name is not specified.
        type: str
        required: false
      is_detailed_logging_mode:
        description: Enable or disable the detailed logging mode.
        type: bool
        required: false
"""

EXAMPLES = """
- name: Edit storage controller settings for all storage controllers
  hitachivantara.vspone_block.sds_block.hv_sds_block_storage_controller:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    spec:
      is_detailed_logging_mode: true

- name: Edit storage controller settings by storage controller ID
  hitachivantara.vspone_block.sds_block.hv_sds_block_storage_controller:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    spec:
      id: "3f9bcecc-9ac5-4c21-abed-5b03e682e7b4"
      is_detailed_logging_mode: true
"""

RETURN = """
storage_pools:
  description: A list of storage pools.
  returned: always
  type: dict
  contains:
    storage_controllers:
      description: List of storage controller entries.
      type: list
      elements: dict
      contains:
        id:
          description: Unique identifier for the storage controller.
          type: str
          sample: "25244614-4af4-4922-839a-8528c9e4fd7f"
        allocatable_capacity:
          description: Total allocatable capacity in GB.
          type: int
          sample: 0
        currently_allocatable_capacity:
          description: Currently allocatable capacity in GB.
          type: int
          sample: 0
        used_capacity:
          description: Used capacity in GB.
          type: int
          sample: 0
        logical_limit:
          description: Logical limit of capacity usage.
          type: int
          sample: 0
        volume_maximum_capacity:
          description: Maximum volume capacity.
          type: int
          sample: 0
        free_capacity:
          description: Free capacity available in GB.
          type: int
          sample: 0
        status:
          description: Operational status of the storage controller.
          type: str
          sample: "Normal"
        meta_data_redundancy_of_cache_protection:
          description: Redundancy level for cache protection.
          type: int
          sample: 1
        active_storage_node_id:
          description: UUID of the active storage node.
          type: str
          sample: "7eb3f987-804f-4bc5-9d40-aff9392d507d"
        standby_storage_node_id:
          description: UUID of the standby storage node.
          type: str
          sample: "a8056f21-e4ee-4e3a-a139-bee4de98d8c7"
        secondary_standby_storage_node_id:
          description: UUID of the secondary standby node, if any.
          type: str
          sample: null
        is_detailed_logging_mode:
          description: Indicates if detailed logging mode is enabled.
          type: bool
          sample: false
        allocatable_capacity_usage_rate:
          description: Percentage of allocatable capacity used.
          type: int
          sample: 0
        currently_allocatable_capacity_usage_rate:
          description: Percentage of currently allocatable capacity used.
          type: int
          sample: 0
        capacity_status:
          description: Status of capacity health.
          type: str
          sample: "Normal"
        data_rebalance_status:
          description: Current status of data rebalance operation.
          type: str
          sample: "Stopped"
        data_rebalance_progress_rate:
          description: Progress rate of data rebalance in percentage.
          type: int
          sample: null
        total_volume_capacity:
          description: Total volume capacity.
          type: int
          sample: 0
        provisioned_volume_capacity:
          description: Provisioned volume capacity.
          type: int
          sample: 0
        other_volume_capacity:
          description: Capacity used by other volume types.
          type: int
          sample: 0
        temporary_volume_capacity:
          description: Capacity used by temporary volumes.
          type: int
          sample: 0
        capacities_excluding_system_data:
          description: Capacity details excluding system data.
          type: dict
          contains:
            used_volume_capacity:
              description: Used volume capacity excluding system data.
              type: int
              sample: 0
            compressed_capacity:
              description: Compressed capacity excluding system data.
              type: int
              sample: 0
            reclaimed_capacity:
              description: Reclaimed capacity excluding system data.
              type: int
              sample: 0
            system_data_capacity:
              description: Capacity used by system data.
              type: int
              sample: 0
            pre_used_capacity:
              description: Pre-used capacity before compression.
              type: int
              sample: 0
            pre_compressed_capacity:
              description: Pre-compressed capacity before optimization.
              type: int
              sample: 0
        pin_information:
          description: Additional pin-related configuration or state.
          type: raw
          sample: null
        primary_fault_domain_id:
          description: UUID of the primary fault domain.
          type: str
          sample: "355d32ce-c97f-4adf-9057-49d2e287974b"
"""
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_storage_controllers_reconciler import (
    SDSBStorageControllerReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBStorageControllerArguments,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class SDSBStorageControllerManager:
    def __init__(self):
        self.logger = Log()
        self.argument_spec = SDSBStorageControllerArguments().storage_controller()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )
        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()
        self.spec = parameter_manager.get_storage_controller_spec()
        self.state = parameter_manager.get_state()

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB Storage Controller Operation ===")
        storage_controller = None
        registration_message = validate_ansible_product_registration()
        try:
            sdsb_reconciler = SDSBStorageControllerReconciler(self.connection_info)
            storage_controller = sdsb_reconciler.reconcile_storage_controller(
                self.spec, self.state
            )
        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB Storage Controller Operation ===")
            self.module.fail_json(msg=str(e))
        msg = ""
        if storage_controller and self.connection_info.changed is True:
            msg = "Successfully updated the settings for the storage controller."

        data = {
            "changed": self.connection_info.changed,
            "storage_controllers": storage_controller,
            "message": msg,
        }
        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo(f"{data}")
        self.logger.writeInfo("=== End of SDSB Storage Controller Operation ===")
        self.module.exit_json(**data)


def main():
    obj_store = SDSBStorageControllerManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
