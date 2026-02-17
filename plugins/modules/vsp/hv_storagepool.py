#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_storagepool
short_description: Manage storage pool information on VSP block storage systems.
description:
  - Create, update, or delete storage pool information on VSP block storage systems.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/storagepool.yml)
version_added: "3.1.0"
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
notes:
  - The output parameters C(subscriber_id) and C(partner_id) were removed in version 3.4.0.
    They were also deprecated due to internal API simplification and are no longer supported.
options:
  storage_system_info:
    description: Information about the storage system. This field is an optional field.
    type: dict
    required: false
    suboptions:
      serial:
        description: The serial number of the storage system.
        type: str
        required: false
  state:
    description:
      - The level of the storage pool task. Choices are C(present), C(absent), C(restore), C(tier_relocate), C(monitor_performance), C(init_capacity_saving).
      - In the case you need to execute C(restore) pool, you need the operation when the pool is blocked due to Shared memory volatilization.
    type: str
    required: false
    choices:
      [
        "present",
        "absent",
        "restore",
        "tier_relocate",
        "monitor_performance",
        "init_capacity_saving",
        "shrunk"
      ]
    default: "present"
  spec:
    description: Specification for the storage pool.
    type: dict
    required: false
    suboptions:
      id:
        description: Pool ID.
          Required for the Create a storage pool with a specific pool ID and LDEV numbers
          /Create a storage pool with a specific pool ID and start and end LDEV numbers
          /Expand pool by pool ID
          /Delete pool by pool ID
          /Performing performance monitoring of a pool
          /Performing tier relocation of a pool
          /Restoring a pool
          /Initializing the capacity saving function for a pool
          /Change Pool settings by pool ID with new parameters tasks.
        type: int
        required: false
      name:
        description: Name of the pool.
          Required for the Create a storage pool using required details
          /Create a storage pool using more details
          /Create a storage pool with a specific pool ID and LDEV numbers
          /Create a storage pool with a specific pool ID and start and end LDEV numbers
          /Create a Thin Image pool
          /Expand pool by pool name
          /Delete pool by pool name
          /Delete a pool including pool volumes
          /Change Pool settings by pool Name with new parameters tasks.
          Optional for the Change Pool settings by pool ID with new parameters task.
        type: str
        required: false
      type:
        description: Type of the pool. Supported types are C(HDT), C(HDP), C(HRT), C(HTI).
          Required for the Create a storage pool using required details
          /Create a storage pool using more details
          /Create a storage pool with a specific pool ID and LDEV numbers
          /Create a storage pool with a specific pool ID and start and end LDEV numbers
          /Create a Thin Image pool tasks.
          Optional for the Change Pool settings by pool ID with new parameters task.
        type: str
        required: false
        choices: ["HDT", "HDP", "HRT", "HTI"]
      should_enable_deduplication:
        description:
          - Whether to enable deduplication for the pool. This feature is applicable to the following models
          - VSP G200
          - VSP G400
          - VSP F400
          - VSP G600
          - VSP F600
          - VSP G800
          - VSP F800
          - VSP G400 with NAS module
          - VSP G600 with NAS module
          - VSP G800 with NAS module
          - VSP G1000
          - VSP G1500
          - VSP F1500
          - VSP N400
          - VSP N600
          - VSP N800
          - Optional for the Create a storage pool using more details/Create a Thin Image pool tasks.
        type: bool
        required: false
      depletion_threshold_rate:
        description: Depletion threshold rate for the pool (not applicable for Thin Image pool).
          Required for the Create a storage pool using more details
          /Change Pool settings by pool Name with new parameters tasks.
          Optional for the Create a Thin Image pool
          /Change Pool settings by pool ID with new parameters tasks.
        type: int
        required: false
      warning_threshold_rate:
        description: Warning threshold rate for the pool.
          Required for the Create a storage pool using more details
          /Create a Thin Image pool
          /Change Pool settings by pool Name with new parameters tasks.
          Optional for the Change Pool settings by pool ID with new parameters task.
        type: int
        required: false
      resource_group_id:
        description: ID of the resource group the pool belongs to.
          Optional for the Create a storage pool using more details
          /Create a Thin Image pool tasks.
        type: int
        required: false
      start_ldev_id:
        description: The first LDEV number in the range of consecutive LDEV numbers, if such a range is specified.
          Required for the Create a storage pool with a specific pool ID and start and end LDEV numbers task.
          Can be decimal or hexadecimal.
        type: str
        required: false
      end_ldev_id:
        description: The last LDEV number in the range of consecutive LDEV numbers, if such a range is specified.
          Required for the Create a storage pool with a specific pool ID and start and end LDEV numbers task.
          Can be decimal or hexadecimal.
        type: str
        required: false
      ldev_ids:
        description: LDEV numbers. Can be decimal or hexadecimal.
          Required for the Create a storage pool with a specific pool ID and LDEV numbers task.
        type: list
        elements: str
        required: false
      pool_volumes:
        description: Details about the volumes in the pool.
          Required for the Create a storage pool using required details
          /Create a storage pool using more details
          /Create a Thin Image pool
          /Expand pool by pool name
          /Expand pool by pool ID tasks.
        type: list
        required: false
        elements: dict
        suboptions:
          capacity:
            description: Capacity of the pool volume.
              Required for the Create a storage pool using required details
              /Create a storage pool using more details
              /Create a Thin Image pool
              /Expand pool by pool name
              /Expand pool by pool ID tasks.
            type: str
            required: false
          parity_group_id:
            description: ID of the parity group the volume belongs to.
              Required for the Create a storage pool using required details
              /Create a storage pool using more details
              /Create a Thin Image pool
              /Expand pool by pool name
              /Expand pool by pool ID tasks.
            type: str
            required: true
          cylinder:
            description: Cylinder size of the pool volume.
            type: int
            required: false
      operation_type:
        description: Specify the operation of tier relocation and performance monitoring.
          Required for the Performing performance monitoring of a pool
          /Performing tier relocation of a pool tasks.
        type: str
        required: false
        choices: ["start", "stop"]
      suspend_snapshot:
        description: Whether to suspend Thin Image pairs when the depletion threshold is exceeded.
          Required for the Change Pool settings by pool Name with new parameters task.
          Optional for the Change Pool settings by pool ID with new parameters task.
        type: bool
        required: false
      virtual_volume_capacity_rate:
        description: The subscription limit of a virtual volume to pool capacity (%).
          Required for the Change Pool settings by pool Name with new parameters task.
          Optional for the Change Pool settings by pool ID with new parameters task.
        type: int # Percentage value
        required: false
      monitoring_mode:
        description: Execution mode for performance monitoring (monitor mode) for HDT type.
          Required for the Change Pool settings by pool Name with new parameters task.
          Optional for the Change Pool settings by pool ID with new parameters task.
        type: str
        required: false
        choices: ["PM", "CM"]
      blocking_mode:
        description: Setting the protection function for a virtual volume.
          Required for the Change Pool settings by pool Name with new parameters task.
          Optional for the Change Pool settings by pool ID with new parameters task.
        type: str
        required: false
        choices: ["PF", "PB", "FB", "NB"]
      tier:
        description: HDT pool tier attribute.
          Required for the Change Pool settings by pool Name with new parameters task.
          Optional for the Change Pool settings by pool ID with new parameters task.
        type: dict
        required: false
        suboptions:
          tier_number:
            description: Tier number for the pool.
              Required for the Change Pool settings by pool Name with new parameters
              /Change Pool settings by pool ID with new parameters tasks.
            type: int
            required: false
          table_space_rate:
            description: Ratio of free space for new tiering (in percentage)
              Required for the Change Pool settings by pool Name with new parameters
              /Change Pool settings by pool ID with new parameters tasks.
            type: int
            required: false
          buffer_rate:
            description: Ratio of buffer areas for reallocation (in percentage)
              Required for the Change Pool settings by pool Name with new parameters
              /Change Pool settings by pool ID with new parameters tasks.
            type: int
            required: false
      should_delete_pool_volumes:
        description: Whether to delete pool volumes when the pool is deleted.
          Required for the Delete a pool including pool volumes task.
        type: bool
        required: false
      should_stop_shrinking:
        description: Whether to stop shrinking the pool.
          Required for the Shrink pool task.
        type: bool
        required: false
      pool_volume_ids:
        description: List of pool volume IDs to be removed from the pool.
          Required for the Shrink pool task.
        type: list
        elements: str
        required: false
      start_pool_volume_id:
        description: The first pool volume ID in the range of consecutive pool volume IDs to be removed from the pool.
          Required for the Shrink pool task.
        type: str
        required: false
      end_pool_volume_id:
        description: The last pool volume ID in the range of consecutive pool volume IDs to be removed from the pool.
          Required for the Shrink pool task.
        type: str
        required: false
"""

EXAMPLES = """
- name: Create a Storage Pool
  hitachivantara.vspone_block.vsp.hv_storagepool:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    state: "present"
    spec:
      name: "test_pool"
      type: "HDP"
      should_enable_deduplication: true
      depletion_threshold_rate: 80
      warning_threshold_rate: 70
      resource_group_id: 0
      pool_volumes:
        - capacity: "21.00 GB"
          parity_group_id: "1-2"

- name: Delete a Storage Pool by pool name
  hitachivantara.vspone_block.vsp.hv_storagepool:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    state: "absent"
    spec:
      name: "test_pool"

- name: Delete a Storage Pool including its volumes
  hitachivantara.vspone_block.vsp.hv_storagepool:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    state: "absent"
    spec:
      name: "test_pool"
      should_delete_pool_volumes: true

- name: Performing performance monitoring of a pool
  hitachivantara.vspone_block.vsp.hv_storagepool:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    state: "monitor_performance"
    spec:
      id: 48
      operation_type: "start"

- name: Performing tier relocation of a pool
  hitachivantara.vspone_block.vsp.hv_storagepool:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    state: "relocate"
    spec:
      id: 48
      operation_type: "start"

- name: Restoring a pool
  hitachivantara.vspone_block.vsp.hv_storagepool:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    state: "restore"
    spec:
      id: 48

- name: Initializing the capacity saving function for a pool
  hitachivantara.vspone_block.vsp.hv_storagepool:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    state: "init_capacity_saving"
    spec:
      id: 48

- name: Update an existing Storage Pool
  hitachivantara.vspone_block.vsp.hv_storagepool:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    state: "present"
    spec:
      name: "test_pool"
      warning_threshold_rate: 75
      depletion_threshold_rate: 85

- name: Update Storage Pool with new parameters
  hitachivantara.vspone_block.vsp.hv_storagepool:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    state: "present"
    spec:
      name: "test_pool"
      warning_threshold_rate: 78
      depletion_threshold_rate: 88
      virtual_volume_capacity_rate: 90
      monitoring_mode: "PF"
      blocking_mode: "PM"
      suspend_snapshot: true
      tier:
        tier_number: 1
        tablespace_rate: 60
        buffer_rate: 20
"""

RETURN = r"""
storage_pool:
  description: >
    The storage pool information.
  returned: always
  type: list
  elements: dict
  contains:
    auto_add_pool_vol:
      description: The auto add pool volume setting.
      type: str
      sample: ""
    available_physical_volume_capacity_mb:
      description: The available physical volume capacity in MB.
      type: int
      sample: 14591094
    available_volume_capacity_mb:
      description: The available volume capacity in MB.
      type: int
      sample: 14591094
    is_compression_acceleration_available:
      description: Indicates if compression acceleration is available.
      type: bool
      sample: true
    blocking_mode:
      description: The blocking mode of the pool.
      type: str
      sample: "NB"
    capacities_excluding_system_data:
      description: Capacity information excluding system data.
      type: dict
      contains:
        compressed_capacity:
          description: The compressed capacity.
          type: int
          sample: 0
        deduped_capacity:
          description: The deduplicated capacity.
          type: int
          sample: 0
        pre_compressed_capacity:
          description: The pre-compressed capacity.
          type: int
          sample: 0
        pre_dedupred_capacity:
          description: The pre-deduplicated capacity.
          type: int
          sample: 0
        pre_used_capacity:
          description: The pre-used capacity.
          type: int
          sample: 0
        reclaimed_capacity:
          description: The reclaimed capacity.
          type: int
          sample: 0
        system_data_capacity:
          description: The system data capacity.
          type: int
          sample: 1118208
        used_virtual_volume_capacity:
          description: The used virtual volume capacity.
          type: int
          sample: 258048
    compression_rate:
      description: The compression rate.
      type: int
      sample: 0
    dat:
      description: The DAT information.
      type: str
      sample: ""
    data_reduction_accelerate_comp_capacity_mb:
      description: The data reduction accelerate compression capacity in MB.
      type: int
      sample: 0
    data_reduction_accelerate_comp_including_system_data:
      description: Data reduction accelerate compression including system data.
      type: dict
      contains:
        is_reduction_capacity_available:
          description: Whether reduction capacity is available.
          type: bool
          sample: false
        is_reduction_rate_available:
          description: Whether reduction rate is available.
          type: bool
          sample: false
        reduction_capacity:
          description: The reduction capacity.
          type: int
          sample: -1
        reduction_rate:
          description: The reduction rate.
          type: int
          sample: -1
    data_reduction_accelerate_comp_rate:
      description: The data reduction accelerate compression rate.
      type: int
      sample: 0
    data_reduction_before_capacity_mb:
      description: The data reduction before capacity in MB.
      type: int
      sample: 0
    data_reduction_capacity_mb:
      description: The data reduction capacity in MB.
      type: int
      sample: 0
    data_reduction_including_system_data:
      description: Data reduction including system data.
      type: dict
      contains:
        is_reduction_capacity_available:
          description: Whether reduction capacity is available.
          type: bool
          sample: false
        is_reduction_rate_available:
          description: Whether reduction rate is available.
          type: bool
          sample: false
        reduction_capacity:
          description: The reduction capacity.
          type: int
          sample: -1
        reduction_rate:
          description: The reduction rate.
          type: int
          sample: -1
    data_reduction_rate:
      description: The data reduction rate.
      type: int
      sample: 0
    depletion_threshold:
      description: The depletion threshold.
      type: int
      sample: 80
    duplication_ldev_ids:
      description: List of duplication LDEV IDs.
      type: list
      elements: int
      sample: [32731, 32730, 32729, 32728]
    duplication_ldev_ids_hex:
      description: List of duplication LDEV IDs in hexadecimal format.
      type: list
      elements: str
      sample: ["00:7F:DB", "00:7F:DA", "00:7F:D9", "00:7F:D8"]
    duplication_number:
      description: The number of duplications.
      type: int
      sample: 8
    duplication_rate:
      description: The duplication rate.
      type: int
      sample: 0
    effective_capacity_mb:
      description: The effective capacity in MB.
      type: int
      sample: 14591766
    efficiency:
      description: The efficiency value.
      type: int
      sample: null
    first_ldev_id:
      description: The first LDEV ID.
      type: int
      sample: 32754
    formatted_capacity:
      description: The formatted capacity.
      type: int
      sample: -1
    has_blocked_pool_volume:
      description: Whether the pool has blocked pool volume.
      type: bool
      sample: null
    is_mainframe:
      description: Whether the pool is for mainframe.
      type: bool
      sample: false
    is_shrinking:
      description: Whether the pool is shrinking.
      type: bool
      sample: false
    located_volume_count:
      description: The count of located volumes.
      type: int
      sample: 29
    monitoring_mode:
      description: The monitoring mode.
      type: str
      sample: ""
    num_of_ldevs:
      description: The number of LDEVs.
      type: int
      sample: 12
    pool_action_mode:
      description: The pool action mode.
      type: str
      sample: ""
    pool_id:
      description: The pool ID.
      type: int
      sample: 0
    pool_name:
      description: The name of the pool.
      type: str
      sample: "test-ddp-pool_1"
    pool_status:
      description: The status of the pool.
      type: str
      sample: "NORMAL"
    pool_type:
      description: The type of the pool.
      type: str
      sample: "HDP"
    reserved_volume_count:
      description: The count of reserved volumes.
      type: int
      sample: 0
    snapshot_count:
      description: The count of snapshots.
      type: int
      sample: 1
    snapshot_used_capacity_mb:
      description: The snapshot used capacity in MB.
      type: int
      sample: 0
    suspend_snapshot:
      description: Whether snapshot is suspended.
      type: bool
      sample: true
    tier_operation_status:
      description: The tier operation status.
      type: str
      sample: ""
    tiers:
      description: List of tiers.
      type: list
      elements: dict
      sample: []
    total_located_capacity_mb:
      description: The total located capacity in MB.
      type: int
      sample: 33597984
    total_physical_capacity_mb:
      description: The total physical capacity in MB.
      type: int
      sample: 14591766
    total_pool_capacity_mb:
      description: The total pool capacity in MB.
      type: int
      sample: 14591766
    total_reserved_capacity_mb:
      description: The total reserved capacity in MB.
      type: int
      sample: 0
    used_capacity_rate:
      description: The used capacity rate.
      type: int
      sample: 1
    used_physical_capacity:
      description: The used physical capacity.
      type: int
      sample: -1
    used_physical_capacity_rate:
      description: The used physical capacity rate.
      type: int
      sample: 1
    virtual_volume_capacity_rate:
      description: The virtual volume capacity rate.
      type: int
      sample: -1
    warning_threshold:
      description: The warning threshold.
      type: int
      sample: 70
"""

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPStoragePoolArguments,
    VSPParametersManager,
)
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_storage_pool,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)


class VspStoragePoolManager:

    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPStoragePoolArguments().storage_pool()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.storage_pool_spec()
            self.serial = self.params_manager.get_serial()
            self.state = self.params_manager.get_state()
            self.connection_info = self.params_manager.get_connection_info()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        try:
            self.logger.writeInfo("=== Start of Storage Pool operation ===")
            registration_message = validate_ansible_product_registration()
            response, msg = vsp_storage_pool.VSPStoragePoolReconciler(
                self.connection_info, self.serial
            ).storage_pool_reconcile(self.state, self.spec)

            msg = response if isinstance(response, str) else msg
            result = response if not isinstance(response, str) else None
            response_dict = {
                "changed": self.connection_info.changed,
                "storage_pool": result,
                "msg": msg,
            }
            if registration_message:
                response_dict["user_consent_required"] = registration_message

            self.logger.writeInfo(f"{response_dict}")
            self.logger.writeInfo("=== End of Storage Pool operation ===")
            self.module.exit_json(**response_dict)
        except Exception as ex:
            self.logger.writeException(ex)
            self.logger.writeInfo("=== End of Storage Pool operation ===")
            self.module.fail_json(msg=str(ex))


def main(module=None):
    obj_store = VspStoragePoolManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
