#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)
from __future__ import absolute_import, division, print_function


__metaclass__ = type


DOCUMENTATION = """
---
module: hv_sds_block_storage_pool
short_description: Manages storage pool on Hitachi SDS Block storage systems.
description:
  - This module allows the expansion of the storage pool on Hitachi SDS Block storage systems.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/storage_pool.yml)
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
    description: The desired state of the storage pool.
    type: str
    required: true
    # default: "present"
    choices: ["expand"]
  spec:
    description: Specification for the storage pool.
    type: dict
    required: true
    suboptions:
      name:
        description: The name of the storage pool.
        type: str
        required: false
      id:
        description: The ID of the storage pool.
        type: str
        required: false
      drive_ids:
        description: The drive ids to be added to the pool.
        type: list
        required: false
        elements: str
"""

EXAMPLES = """
- name: Expand storage pool by pool name
  hitachivantara.vspone_block.sds_block.hv_sds_block_storage_pool:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    state: "expand"
    spec:
      name: "SP01"
      drive_ids: ["6a14d3cb-264f-41b1-81c0-cdbfab73d358"]

- name: Expand storage pool by pool ID
  hitachivantara.vspone_block.sds_block.hv_sds_block_storage_pool:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    state: "expand"
    spec:
      id: "3f9bcecc-9ac5-4c21-abed-5b03e682e7b4"
      drive_ids: ["6a14d3cb-264f-41b1-81c0-cdbfab73d358"]
"""

RETURN = """
storage_pools:
  description: A list of storage pools.
  returned: always
  type: dict
  contains:
    storage_pool_info:
      description: Information about the storage pool.
      type: dict
      contains:
        blocked_physical_capacity_mb:
          description: The blocked capacity in the effective physical capacity of the storage pool in MiB.
          type: int
          sample: 0
        capacity_manage:
          description: Capacity management.
          type: dict
          contains:
            maximum_reserve_rate:
              description: Maximum reserve rate (unit -%). -1 indicates the capacity is unlimited.
              type: int
              sample: -1
            threshold_depletion:
              description: The Depletion threshold (unit - %).
              type: int
              sample: 80
            threshold_storage_controller_depletion:
              description: The depletion threshold of the storage controller managing the storage pool (unit - %)
              type: int
              sample: 95
            threshold_warning:
              description: The warning threshold (unit - %).
              type: int
              sample: 80
            used_capacity_rate:
              description: Usage rate (unit - %).
              type: int
              sample: 80
        data_redundancy:
          description: Redundancy of user data. Value of 0 means no redundancy, and -1 means that the user data has been lost.
          type: int
          sample: 1
        encryption_status:
          description: The state of storage pool data encryption.
          type: str
          sample: "Disabled"
        free_capacity_mb:
          description: The available capacity of the storage pool in MiB.
          type: int
          sample: 7425600
        id:
          description: The ID of the storage pool.
          type: str
          sample: "fa632b0d8-0ae6-408c-ad41-555cdde9fe83"
        meta_data_physical_capacity_mb:
          description: The capacity for control information in the total physical capacity of the storage pool in MiB.
          type: int
          sample: 3563650
        name:
          description: The name of the storage pool.
          type: str
          sample: "SP01"
        number_of_volumes:
          description: The number of volumes belonging to the storage pool.
          type: int
          sample: 3
        other_volume_capacity_mb:
          description: The total capacity of other volumes that have been created on this storage controller in MiB.
          type: int
          sample: 0
        protection_domain_id:
          description: The ID of the protection domain to which the volume is belonging.
          type: str
          sample: "4090c412-edf2-4368-8175-1f60507afbb8"
        provisioned_volume_capacity_mb:
          description: The total capacity of provisioned volumes that have been created on this storage controller in MiB.
          type: int
          sample: 2969
        rebuild_capacity_policy:
          description: Rebuild capacity policy.
          type: str
          sample: "Fixed"
        rebuild_capacity_resource_setting:
          description: Resource type and the number of resources of rebuild capacity.
          type: dict
          contains:
            number_of_tolerable_drive_failures:
              description: The number of drive failures that can be tolerated.
              type: int
              sample: 1
        rebuild_capacity_status:
          description: The status of securing rebuild capacity.
          type: str
          sample: "Sufficient"
        rebuildable_resources:
          description: Resource for which Rebuild is possible.
          type: dict
          contains:
            number_of_drives:
              description: The number of drives for which Rebuild is possible.
              type: int
              sample: 1
        redundant_policy:
          description: User data protection method.
          type: str
          sample: "Mirroring"
        redundant_type:
          description: User data protection type.
          type: str
          sample: "Duplication"
        reserved_physical_capacity_mb:
          description: The internally reserved area in the effective physical capacity of the storage pool in MiB.
            This area cannot be configured redundantly.
          type: int
          sample: 3574368
        saving_effects:
          description: Effect of the data reduction function on the storage pool.
          type: dict
          contains:
            calculation_end_time:
              description: Date and time the calculation ended.
              type: str
              sample: "2025-07-10T22:50:34Z"
            calculation_start_time:
              description: Date and time the calculation started.
              type: str
              sample: "2025-07-10T22:49:52Z"
            data_reduction_without_system_data_status:
              description: Status of the reduction effect of the data reduction function.
              type: str
              sample: "NoTargetData"
            total_efficiency_status:
              description: Status of total efficiency.
              type: str
              sample: "NoTargetData"
        status:
          description: The storage pool status.
          type: str
          sample: "Normal"
        status_summary:
          description: The summary of the storage pool status.
          type: str
          sample: "Normal"
        storage_controller_capacities_general_status:
          description: Summary information about the capacity status of all the storage controllers managing the storage pool.
          type: str
          sample: "Normal"
        temporary_volume_capacity_mb:
          description: The total capacity of temporary volumes that have been created on this storage controller in MiB.
          type: int
          sample: 0
        total_capacity_mb:
          description: The logical capacity of the storage pool in MiB.
          type: int
          sample: 2370312
        total_physical_capacity_mb:
          description: The total physical capacity of the storage pool in MiB.
          type: int
          sample: 10683344
        total_raw_capacity_mb:
          description: The effective physical capacity in the total physical capacity of the storage pool in MiB.
          type: int
          sample: 8340192
        total_volume_capacity_mb:
          description: The total capacity of volumes that have been created on this storage controller in MiB.
          type: int
          sample: 2969
        usable_physical_capacity_mb:
          description: The capacity which can be used as the logical capacity in the effective physical capacity of the storage pool in MiB.
          type: int
          sample: 4765824
        used_capacity_mb:
          description: The used capacity of the storage pool in MiB.
          type: int
          sample: 0
"""
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_storage_pool import (
    SDSBStoragePoolReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBStoragePoolArguments,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class SDSBStoragePoolManager:
    def __init__(self):
        self.logger = Log()
        self.argument_spec = SDSBStoragePoolArguments().storage_pool()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )
        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()
        self.spec = parameter_manager.get_storage_pool_spec()
        self.state = parameter_manager.get_state()

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB Storage Pool Operation ===")
        storage_nodes = None
        registration_message = validate_ansible_product_registration()
        try:
            sdsb_reconciler = SDSBStoragePoolReconciler(
                self.connection_info, self.state
            )
            storage_nodes = sdsb_reconciler.reconcile_storage_pool(self.spec)
        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB Storage Pool Operation ===")
            self.module.fail_json(msg=str(e))
        msg = ""
        if storage_nodes:
            msg = (
                "The storage system will generate additional jobs for capacity and metadata allocation."
                "Please wait for these tasks to finish and then verify the storage pool capacity."
            )
        data = {
            "changed": self.connection_info.changed,
            "storage_nodes": storage_nodes,
            "message": msg,
        }
        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo(f"{data}")
        self.logger.writeInfo("=== End of SDSB Storage Pool Operation ===")
        self.module.exit_json(changed=False, ansible_facts=data)


def main():
    obj_store = SDSBStoragePoolManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
