#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_ldev_bulk
short_description: Manages multiple logical devices (LDEVs) in bulk on VSP block storage systems.
description:
  - This module is designed for bulk operations on logical devices (LDEVs) on VSP block storage systems.
  - It allows for efficient creation, modification, or deletion of multiple LDEVs in a single operation.
  - Supports parallel execution for faster processing of bulk LDEV operations.
  - Use this module when you need to perform operations on multiple LDEVs simultaneously.
  - For single LDEV operations, use the `hv_ldev` module instead.
  - For creating multiple volumes on VSP One Block or VSP E Series storage systems,
      you can also use `hv_vsp_one_volume` module for optimized execution.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/ldev.yml)
  - For examples to create multiple LDEVs, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/ldev_bulk.yml)
version_added: '4.7.0'
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
  - The output parameters C(entitlement_status), C(subscriber_id) and C(partner_id) were removed in version 3.4.0.
    They were also deprecated due to internal API simplification and are no longer supported.
options:
  state:
    description: The desired state for bulk LDEV operations.
    type: str
    required: false
    choices: ['present', 'absent', 'assign_virtual_ldev']
    default: 'present'
  storage_system_info:
    description: Information about the storage system. This field is an optional field.
    type: dict
    required: false
    suboptions:
      serial:
        description: The serial number of the storage system.
        type: str
        required: false
  spec:
    description: Specification for bulk LDEV operations. Supports creating, modifying, or deleting multiple LDEVs.
    type: dict
    required: true
    suboptions:
      pool_id:
        description: ID of the pool where the LDEVs will be created. Options pool_id and parity_group_id are mutually exclusive.
          Required for bulk creating multiple LDEVs within a pool
          /Creating multiple LDEVs within a range of LDEV IDs using parallel execution
          /Creating multiple LDEVs with capacity saving and data_reduction_share
          /Configuring QoS settings for multiple volumes
          /Creating multiple volumes with tiering policy
          /Creating multiple volumes with virtual ldev assignment.
        type: int
        required: false
      parity_group_id:
        description: ID of the parity_group where the LDEVs will be created. Options pool_id and parity_group_id are mutually exclusive.
          Required for bulk creating multiple LDEVs using a parity group and auto-free LDEV ID selection.
        type: str
        required: false
      size:
        description: Size for each LDEV. Can be specified in units such as GB, TB, or MB (e.g., '10GB', '5TB', '100MB', 200).
          This size will be applied to all LDEVs created in the bulk operation.
          Required for bulk creating multiple LDEVs within a range of LDEV IDs using parallel execution
          /Expanding the size of multiple LDEVs
          /Creating multiple LDEVs using a parity group and auto-free LDEV ID selection
          /Creating multiple LDEVs using external parity group and auto free LDEV ID selection
          /Creating multiple LDEVs with capacity saving and data_reduction_share
          /Configuring QoS settings for multiple new volumes
          /Creating multiple new volumes with tiering policy.
        type: str
        required: false
      name:
        description: >
          Name for a single LDEV (optional). For bulk operations, use the 'names' parameter instead.
          If given, the LDEV name will be 'name-<ldev_id>'. If not given and 'names' is not specified, assigns default names to LDEVs as
          "name-<ldev_id>" if start_ldev_id and end_ldev_id are specified,otherwise "smrha-<ldev_id>".
          This naming convention is applicable for both single and bulk LDEV creation.
        type: str
        required: false
      capacity_saving:
        description: >
          Whether to enable the capacity saving functions for all LDEVs in the bulk operation. Valid value is one of the following three options:
          - 1. compression -  Enable the capacity saving function (compression).
          - 2. compression_deduplication - Enable the capacity saving function (compression and deduplication).
          - 3 disabled - Disable the capacity saving function (compression and deduplication)
          Default value is disabled.
          This setting will be applied to all LDEVs created in the bulk operation.
          Optional for bulk creating multiple LDEVs within a range of LDEV IDs using parallel execution.
          Required for bulk creating multiple LDEVs with capacity saving and data_reduction_share.
        type: str
        required: false
      data_reduction_share:
        description: Specify whether to create data reduction shared volumes for all LDEVs in the bulk operation.
          This value is set to true for Thin Image Advance.
          This setting will be applied to all LDEVs created in the bulk operation.
          Required for bulk creating multiple LDEVs with capacity saving and data_reduction_share.
        type: bool
        required: false
      nvm_subsystem_name:
        description: Specify the NVM subsystem name where LDEVs will be presented.
          Can be used for bulk presenting multiple LDEVs to an NVM subsystem.
          Optional for bulk operations involving NVM subsystems.
        type: str
        required: false
      state:
        description:
          - State of the NVM subsystems task for bulk operations. This is valid only when nvm_subsystem_name is specified.
          - C(add_host_nqn) - Add the host NQNs to multiple LDEVs.
          - C(remove_host_nqn) - Remove the host NQNs from multiple LDEVs.
          - Optional for bulk operations with NVM subsystems.
        type: str
        required: false
        choices: ['add_host_nqn', 'remove_host_nqn']
        default: 'add_host_nqn'
      host_nqns:
        description: List of host NQNs to add to or remove from multiple LDEVs depending on the state value.
          When used in bulk operations, these NQNs will be applied to all specified LDEVs.
          Optional for bulk operations with NVM subsystems.
        type: list
        required: false
        elements: str
      is_relocation_enabled:
        description: Specify whether to enable the tier relocation setting for multiple HDT volumes.
          This setting will be applied to all LDEVs in the bulk operation.
          Optional for bulk changing settings for multiple volumes
          /Bulk creating multiple new volumes with tiering policy.
        type: bool
        required: false
      tier_level_for_new_page_allocation:
        description: Specify which tier of the HDT pool will be prioritized when a new page is allocated for multiple volumes.
          This setting will be applied to all LDEVs in the bulk operation.
          Optional for bulk creating multiple new volumes with tiering policy.
        type: str
        required: false
      tiering_policy:
        description: Tiering policy to be applied to multiple LDEVs in the bulk operation.
          This setting will be applied to all LDEVs in the bulk operation.
          Optional for bulk creating multiple new volumes with tiering policy.
        type: dict
        required: false
        suboptions:
          tier_level:
            description: Tier level, a value from 0 to 31. Applied to all LDEVs in the bulk operation.
              Optional for bulk creating multiple new volumes with tiering policy.
            type: int
            required: false
          tier1_allocation_rate_min:
            description: Tier1 min, a value from 1 to 100. Applied to all LDEVs in the bulk operation.
              Optional for bulk creating multiple new volumes with tiering policy.
            type: int
            required: false
          tier1_allocation_rate_max:
            description: Tier1 max, a value from 1 to 100. Applied to all LDEVs in the bulk operation.
              Optional for bulk creating multiple new volumes with tiering policy.
            type: int
            required: false
          tier3_allocation_rate_min:
            description: Tier3 min, a value from 1 to 100. Applied to all LDEVs in the bulk operation.
              Optional for bulk creating multiple new volumes with tiering policy.
            type: int
            required: false
          tier3_allocation_rate_max:
            description: Tier3 max, a value from 1 to 100. Applied to all LDEVs in the bulk operation.
              Optional for bulk creating multiple new volumes with tiering policy.
            type: int
            required: false
      force:
        description: Force delete multiple LDEVs. Deletes the LDEVs and removes them from hostgroups, iscsi targets or NVM subsystem namespace.
          When used with bulk operations, this will apply to all specified LDEVs in ldev_ids list.
          Required for bulk force deleting multiple LDEVs and removing them from hostgroups,
          iSCSI targets or NVM subsystem namespace.
        type: bool
        required: false
      should_shred_volume_enable:
        description: Shreds multiple LDEVs (basic volumes) or DP volumes. Overwrites each volume three times with dummy data.
          When used with bulk operations, this will apply to all specified LDEVs in ldev_ids list.
          Required for bulk shredding multiple existing volumes
          /Bulk shredding multiple existing volumes before deleting.
        type: bool
        required: false
      qos_settings:
        description: QoS settings to be applied to multiple LDEVs in the bulk operation.
          These settings will be applied to all LDEVs specified in ldev_ids or all newly created LDEVs.
          Required for bulk configuring QoS settings for multiple existing volumes
          /Bulk configuring QoS settings for multiple new volumes.
        type: dict
        required: false
        suboptions:
          upper_iops:
            description: Upper IOPS limit to be applied to all LDEVs in the bulk operation.
              Optional for bulk configuring QoS settings for multiple existing/new volumes.
            type: int
            required: false
          lower_iops:
            description: Lower IOPS limit to be applied to all LDEVs in the bulk operation.
              Optional for bulk configuring QoS settings for multiple existing/new volumes.
            type: int
            required: false
          upper_transfer_rate:
            description: Upper transfer rate limit to be applied to all LDEVs in the bulk operation.
              Optional for bulk configuring QoS settings for multiple existing/new volumes.
            type: int
            required: false
          lower_transfer_rate:
            description: Lower transfer rate limit to be applied to all LDEVs in the bulk operation.
              Optional for bulk configuring QoS settings for multiple existing/new volumes.
            type: int
            required: false
          upper_alert_allowable_time:
            description: Upper alert allowable time to be applied to all LDEVs in the bulk operation.
              Optional for bulk configuring QoS settings for multiple existing/new volumes.
            type: int
            required: false
          lower_alert_allowable_time:
            description: Lower alert allowable time to be applied to all LDEVs in the bulk operation.
              Optional for bulk configuring QoS settings for multiple existing/new volumes.
            type: int
            required: false
          response_priority:
            description: Response priority to be applied to all LDEVs in the bulk operation.
              Optional for bulk configuring QoS settings for multiple existing/new volumes.
            type: int
            required: false
          response_alert_allowable_time:
            description: Response alert allowable time to be applied to all LDEVs in the bulk operation.
              Optional for bulk configuring QoS settings for multiple existing/new volumes.
            type: int
            required: false
      is_compression_acceleration_enabled:
        description: Whether the compression accelerator of the capacity saving function is enabled for all LDEVs.
          This setting will be applied to all LDEVs in the bulk operation.
          Optional for bulk creating multiple LDEVs within a range of LDEV IDs using parallel execution
          /Bulk changing settings for multiple volumes.
        type: bool
        required: false
      data_reduction_process_mode:
        description: >
          The data reduction process mode of the capacity saving function for all LDEVs.
          This setting will be applied to all LDEVs in the bulk operation.
          Valid values are:
          - "post_process" -  Post-process mode.
          - "inline" - Inline mode.
          Optional for bulk changing settings for multiple volumes.
        choices: ["post_process", "inline"]
        type: str
      is_alua_enabled:
        description: Whether the ALUA (Asymmetric Logical Unit Access) is enabled for all LDEVs.
          This setting will be applied to all LDEVs in the bulk operation.
          Optional for bulk changing settings for multiple volumes.
        type: bool
        required: false
      is_full_allocation_enabled:
        description: Whether the LDEVs are full allocation volumes.
          This setting will be applied to all LDEVs in the bulk operation.
          Optional for bulk changing settings for multiple volumes.
        type: bool
        required: false
      should_format_volume:
        description: Whether to format multiple volumes after creation or for existing volumes.
          When set to true, all LDEVs specified in ldev_ids will be formatted.
          Required for bulk formatting multiple volumes.
        type: bool
        required: false
      format_type:
        description: >
          The format type for multiple volumes. Valid values are:
          - "quick" - Quick formatting.
          - "normal" - Normal formatting. It may take time to finish the formatting process for all volumes.
          This format type will be applied to all LDEVs in the bulk operation.
          Optional for bulk formatting multiple volumes.
        type: str
        required: false
        choices: ["quick", "normal"]
        default: "quick"
      start_ldev_id:
        description: >
          The starting LDEV ID for the range of LDEVs to be created in bulk.
          Used to define the beginning of the LDEV ID range for bulk creation.
          If not specified, a free LDEV ID will be assigned. Can be decimal or hexadecimal.
          Required for bulk creating multiple LDEVs within a range of LDEV IDs using parallel execution.
        type: str
        required: false
      end_ldev_id:
        description: >
          The ending LDEV ID for the range of LDEVs to be created in bulk.
          Used to define the end of the LDEV ID range for bulk creation.
          All LDEVs from start_ldev_id to end_ldev_id will be created. Can be decimal or hexadecimal.
          Required for bulk creating multiple LDEVs within a range of LDEV IDs using parallel execution.
        type: str
        required: false
      mp_blade_id:
        description: >
          The MP blade ID to which all LDEVs will be assigned. This is used for specifying the MP blade for multiple LDEVs.
          If not specified, the LDEVs will be assigned to the default MP blade.
          This setting will be applied to all LDEVs in the bulk operation.
          Optional for bulk setting MP blade ID for multiple volumes.
        type: int
        required: false
      clpr_id:
        description: >
          The CLPR (Control Logical Partition) ID to which all LDEVs will be assigned.
          This is used for specifying the CLPR for multiple LDEVs.
          If not specified, the LDEVs will be assigned to the default CLPR.
          This setting will be applied to all LDEVs in the bulk operation.
          Required for bulk setting CLPR ID for multiple volumes.
        type: int
        required: false
      should_reclaim_zero_pages:
        description: >
          Whether to reclaim zero pages of multiple DP volumes. This is used to reclaim space in multiple DP volumes.
          If set to true, it will reclaim the zero pages of all specified DP volumes.
          Required for bulk reclaiming zero pages of multiple DP volumes.
        type: bool
        required: false
      external_parity_group:
        description: >
          The external parity group ID to which the LDEVs will be assigned.
          This is used for specifying the external parity group for multiple LDEVs in bulk operations.
          If not specified, the LDEVs will be assigned to the default parity group.
          Optional for bulk creating multiple LDEVs using external parity group and auto free LDEV ID selection.
        type: str
        required: false
      is_parallel_execution_enabled:
        description: >
          Whether to enable parallel execution for bulk LDEV operations. This significantly speeds up bulk operations.
          If set to true, multiple LDEV operations will be executed in parallel.
          Highly recommended when working with large numbers of LDEVs.
          Required for bulk creating multiple LDEVs within a range of LDEV IDs using parallel execution.
        type: bool
        required: false
      should_stop_all_volume_format:
        description: >
          Whether to stop all ongoing volume format operations for multiple volumes.
          This is used to stop ongoing volume format tasks across multiple LDEVs.
          If set to true, it will stop all volume format operations.
          Optional for stopping all volume format operations in bulk.
        type: bool
      cylinder:
        description: >
          The cylinder number for Mainframe LDEVs. This is used for specifying the cylinder for multiple LDEVs.
          This setting will be applied to all mainframe LDEVs in the bulk operation.
        type: int
        required: false
      emulation_type:
        description: >
          The emulation type for Mainframe LDEVs. This is used for specifying the emulation type for multiple LDEVs.
          This setting will be applied to all mainframe LDEVs in the bulk operation.
          Example values are 3390-A and 3390-V.
        type: str
        required: false
      is_tse_volume:
        description: >
          Whether the LDEVs are TSE (Thin Provisioning with Space Efficiency) volumes.
          This is used for specifying if multiple LDEVs are TSE volumes.
          This setting will be applied to all LDEVs in the bulk operation.
        type: bool
        required: false
      is_ese_volume:
        description: >
          Whether the LDEVs are ESE (Enhanced Space Efficiency) volumes.
          This is used for specifying if multiple LDEVs are ESE volumes.
          This setting will be applied to all LDEVs in the bulk operation.
        type: bool
        required: false
      ssid:
        description: >
          The SSID (Subsystem ID) for Mainframe LDEVs. This is used for specifying the SSID for multiple LDEVs.
          If not specified, the default SSID will be used for all LDEVs. If specified, it will use the specified SSID.
          This setting will be applied to all mainframe LDEVs in the bulk operation.
        type: str
        required: false
      resource_group_id:
        description: >
          The resource group ID for multiple LDEVs. This is used for specifying the resource group for multiple LDEVs.
          This setting will be applied to all LDEVs in the bulk operation.
        type: int
        required: false
      ldev_ids:
        description: >
          A list of LDEV IDs for bulk operations. Specify multiple LDEV IDs to perform operations on them simultaneously.
          Use this for bulk delete, bulk update, bulk format, or other bulk operations on existing LDEVs.
          Example: [100, 101, 102, 103, 104].
        type: list
        elements: int
        required: false
      number_of_ldevs:
        description: >
          The number of LDEVs to be created in the bulk operation.
          The system will automatically assign free LDEV IDs for the specified number of LDEVs.
          Use this when you want to create a specific count of LDEVs without specifying exact LDEV IDs.
          Example: number_of_ldevs=10 will create 10 new LDEVs.
        type: int
        required: false
      vldev_ids:
        description: >
          A list of virtual LDEV IDs for bulk virtual LDEV assignment operations.
          Use this to assign virtual LDEVs to multiple LDEVs in bulk.
          Must be used in conjunction with ldev_ids and state='assign_virtual_ldev'.
        type: list
        elements: int
        required: false
      names:
        description: >
          Names configuration for multiple LDEVs in bulk operations.
          This is used for automatically generating sequential names for multiple LDEVs.
          Example: base_name="vol", start_number=1, number_of_digits=3 generates vol001, vol002, vol003, etc.
        type: dict
        required: false
        suboptions:
          base_name:
            description: >
              The base name prefix for the LDEVs in bulk operation.
              The actual name of each LDEV will be generated by appending a sequential number to this base name.
              Example: base_name="prod_vol" generates prod_vol001, prod_vol002, etc.
            type: str
            required: false
            default: "smrha"
          start_number:
            description: >
              The starting number for generating sequential LDEV names in bulk operations.
              Used in conjunction with base_name to generate names for multiple LDEVs.
              Example: start_number=5 with base_name="vol" generates vol005, vol006, etc.
            type: int
            required: false
            default: 0
          number_of_digits:
            description: >
              The number of digits for the sequential number in the generated LDEV names.
              Used for zero-padding. Example: number_of_digits=4 generates 0001, 0002, 0003, etc.
              Used in conjunction with base_name to generate names for multiple LDEVs.
            type: int
            required: false
            default: 3
"""

EXAMPLES = """
- name: Create multiple LDEVs within a range using parallel execution
  hitachivantara.vspone_block.vsp.hv_ldev_bulk:
    state: present
    connection_info:
      address: storage.company.com
      username: "admin"
      password: "passw0rd"
    spec:
      pool_id: 1
      size: "10GB"
      start_ldev_id: 100
      end_ldev_id: 110
      is_parallel_execution_enabled: true
      names:
        base_name: "bulk_vol"
        start_number: 1
        number_of_digits: 3

- name: Create multiple LDEVs with specific count
  hitachivantara.vspone_block.vsp.hv_ldev_bulk:
    state: present
    connection_info:
      address: storage.company.com
      username: "admin"
      password: "passw0rd"
    spec:
      pool_id: 1
      size: "20GB"
      number_of_ldevs: 5
      capacity_saving: "compression_deduplication"
      names:
        base_name: "prod_vol"
        start_number: 1

- name: Delete multiple LDEVs in bulk
  hitachivantara.vspone_block.vsp.hv_ldev_bulk:
    state: absent
    connection_info:
      address: storage.company.com
      username: "admin"
      password: "passw0rd"
    spec:
      ldev_ids: [100, 101, 102, 103, 104]
      force: true

- name: Update QoS settings for multiple LDEVs
  hitachivantara.vspone_block.vsp.hv_ldev_bulk:
    state: present
    connection_info:
      address: storage.company.com
      username: "admin"
      password: "passw0rd"
    spec:
      ldev_ids: [100, 101, 102]
      qos_settings:
        upper_iops: 1000
        lower_iops: 500
        upper_transfer_rate: 1000
        lower_transfer_rate: 500

- name: Format multiple volumes in bulk
  hitachivantara.vspone_block.vsp.hv_ldev_bulk:
    connection_info:
      address: storage.company.com
      username: "admin"
      password: "passw0rd"
    state: "present"
    spec:
      ldev_ids: [100, 101, 102, 103]
      should_format_volume: true
      format_type: "quick"

- name: Assign virtual LDEVs to multiple LDEVs
  hitachivantara.vspone_block.vsp.hv_ldev_bulk:
    connection_info:
      address: storage.company.com
      username: "admin"
      password: "passw0rd"
    state: "assign_virtual_ldev"
    spec:
      ldev_ids: [100, 101, 102]
      vldev_ids: [200, 201, 202]

- name: Reclaim zero pages for multiple DP volumes
  hitachivantara.vspone_block.vsp.hv_ldev_bulk:
    connection_info:
      address: storage.company.com
      username: "admin"
      password: "passw0rd"
    state: "present"
    spec:
      ldev_ids: [100, 101, 102]
      should_reclaim_zero_pages: true

- name: Create multiple mainframe LDEVs with specific configuration
  hitachivantara.vspone_block.vsp.hv_ldev_bulk:
    connection_info:
      address: storage.company.com
      username: "admin"
      password: "passw0rd"
    state: "present"
    spec:
      pool_id: 1
      cylinder: 65945
      emulation_type: "3390-V"
      number_of_ldevs: 10
      ssid: "000C"
      names:
        base_name: "mf_vol"
        start_number: 1
        number_of_digits: 4
"""

RETURN = r"""
volumes:
  description: Storage volume with its attributes.
  returned: success
  type: list
  elements: dict
  contains:
    canonical_name:
      description: Unique identifier for the volume.
      type: str
      sample: "naa.60060e8028273d005080273d00000102"
    clpr_id:
      description: CLPR (Control Logical Partition) ID.
      type: int
      sample: 0
    compression_acceleration_status:
      description: Status of compression accelerator.
      type: str
      sample: "ENABLED"
    cylinder:
      description: Cylinder number for mainframe volumes.
      type: int
      sample: 65945
    data_reduction_process_mode:
      description: Data reduction process mode.
      type: str
      sample: "inline"
    dedup_compression_progress:
      description: Progress percentage of deduplication and compression.
      type: int
      sample: -1
    dedup_compression_status:
      description: Status of deduplication and compression.
      type: str
      sample: "ENABLED"
    deduplication_compression_mode:
      description: Mode of deduplication and compression.
      type: str
      sample: "compression_deduplication"
    emulation_type:
      description: Emulation type of the volume.
      type: str
      sample: "3390-V-CVS"
    hostgroups:
      description: List of host groups associated with the volume.
      type: list
      elements: dict
      sample: []
    is_alua:
      description: Indicates if ALUA is enabled.
      type: bool
      sample: false
    is_command_device:
      description: Indicates if the volume is a command device.
      type: bool
      sample: null
    is_compression_acceleration_enabled:
      description: Whether compression accelerator is enabled.
      type: bool
      sample: true
    is_data_reduction_share_enabled:
      description: Indicates if data reduction share is enabled.
      type: bool
      sample: true
    is_device_group_definition_enabled:
      description: Indicates if device group definition is enabled.
      type: bool
      sample: null
    is_encryption_enabled:
      description: Indicates if encryption is enabled.
      type: bool
      sample: false
    is_full_allocation_enabled:
      description: Indicates if full allocation is enabled.
      type: bool
      sample: false
    is_relocation_enabled:
      description: Indicates if tier relocation is enabled.
      type: bool
      sample: null
    is_security_enabled:
      description: Indicates if security is enabled.
      type: bool
      sample: null
    is_user_authentication_enabled:
      description: Indicates if user authentication is enabled.
      type: bool
      sample: null
    is_write_protected:
      description: Indicates if write protection is enabled.
      type: bool
      sample: null
    is_write_protected_by_key:
      description: Indicates if write protection by key is enabled.
      type: bool
      sample: null
    iscsi_targets:
      description: List of iSCSI targets associated with the volume.
      type: list
      elements: dict
      sample: []
    ldev_id:
      description: Logical Device ID.
      type: int
      sample: 10010
    ldev_id_hex:
      description: Logical Device ID in hexadecimal.
      type: str
      sample: "00:27:1A"
    mp_blade_id:
      description: MP blade ID.
      type: int
      sample: 3
    name:
      description: Name of the volume.
      type: str
      sample: "smrha-258"
    num_of_ports:
      description: Number of ports associated with the volume.
      type: int
      sample: 2
    nvm_subsystems:
      description: List of NVMe subsystems associated with the volume.
      type: list
      elements: dict
      sample: []
    parent_volume_id:
      description: Parent volume ID for snapshot volumes.
      type: int
      sample: -1
    parent_volume_id_hex:
      description: Parent volume ID in hexadecimal format.
      type: str
      sample: "-0:00:01"
    parity_group_id:
      description: Parity group ID.
      type: str
      sample: "1-8"
    path_count:
      description: Path count to the volume.
      type: int
      sample: 2
    pool_id:
      description: Pool ID where the volume resides.
      type: int
      sample: 13
    ports:
      description: List of ports associated with the volume.
      type: list
      elements: dict
      contains:
        host_group_name:
          description: Host group name.
          type: str
          sample: "1C-G00"
        host_group_number:
          description: Host group number.
          type: int
          sample: 156
        lun:
          description: Logical Unit Number.
          type: int
          sample: 26
        port_id:
          description: Port identifier.
          type: str
          sample: "CL1-C"
      sample: [
        {
          "host_group_name": "1C-G00",
          "host_group_number": 156,
          "lun": 26,
          "port_id": "CL1-C"
        }
      ]
    provision_type:
      description: Provisioning type of the volume.
      type: str
      sample: "CVS"
    qos_settings:
      description: QoS settings for the volume.
      type: dict
      sample: null
    resource_group_id:
      description: Resource group ID of the volume.
      type: int
      sample: 0
    snapshots:
      description: List of snapshots associated with the volume.
      type: list
      elements: dict
      sample: []
    ssid:
      description: Subsystem ID for mainframe volumes.
      type: str
      sample: "000C"
    status:
      description: Current status of the volume.
      type: str
      sample: "NML"
    storage_serial_number:
      description: Serial number of the storage system.
      type: str
      sample: "70033"
    tiering_policy:
      description: Tiering policy details.
      type: dict
      sample: {}
    total_capacity:
      description: Total capacity of the volume.
      type: str
      sample: "54.71GB"
    total_capacity_in_mb:
      description: Total capacity of the volume in megabytes.
      type: float
      sample: 56023.04
    used_capacity:
      description: Used capacity of the volume.
      type: str
      sample: "0.00B"
    used_capacity_in_mb:
      description: Used capacity of the volume in megabytes.
      type: float
      sample: 0
    virtual_ldev_id:
      description: Virtual Logical Device ID.
      type: int
      sample: -1
    virtual_ldev_id_hex:
      description: Virtual Logical Device ID in hexadecimal.
      type: str
      sample: ""
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPVolumeArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    StateValue,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_volume,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class VSPVolume:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = VSPVolumeArguments().volume_bulk()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )

        try:
            params_manager = VSPParametersManager(self.module.params)
            self.spec = params_manager.set_volume_spec()
            self.connection_info = params_manager.get_connection_info()
            self.serial = params_manager.get_serial()
            self.state = params_manager.get_state()
        except Exception as e:
            self.logger.writeError(f"An error occurred during initialization: {str(e)}")
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of LDEV Bulk operation ===")
        registration_message = validate_ansible_product_registration()

        try:
            comments = []

            volume_data = self.direct_volume()

            if self.state == StateValue.ABSENT and not volume_data:
                volume_response = "Volume deleted"
            else:
                if isinstance(volume_data, str):
                    volume_response = volume_data
                else:
                    if isinstance(volume_data, dict):
                        comments = volume_data.get("comment", None)
                    volume_response = self.extract_volume_properties(volume_data)
                if self.spec.should_shred_volume_enable:
                    comments.append("Volume shredded successfully,")
                if self.spec.should_format_volume:
                    if self.spec.is_task_timeout:
                        comments.append(
                            "Volume format task is still in progress. It will finish after sometime "
                        )
                    else:
                        comments.append("Volume formatted successfully,")
                if self.spec.should_reclaim_zero_pages:
                    comments.append("Volume reclaimed to zero pages successfully,")

        except Exception as e:
            self.logger.writeError(f"An error occurred: {str(e)}")
            self.logger.writeInfo("=== End of LDEV Bulk operation ===")
            self.module.fail_json(msg=str(e))

        response = {"changed": self.connection_info.changed, "volumes": volume_response}

        if self.spec.comments:
            comments.extend(self.spec.comments)
        if comments:
            response["comments"] = comments

        if registration_message:
            response["user_consent_required"] = registration_message

        self.logger.writeInfo(f"{response}")
        self.logger.writeInfo("=== End of LDEV Bulk operation ===")
        self.module.exit_json(**response)

    def direct_volume(self):

        result = vsp_volume.VSPVolumeReconciler(
            self.connection_info,
            self.serial,
        ).volume_reconcile(self.state, self.spec)
        return result

    def extract_volume_properties(self, volume_data):
        if not volume_data:
            return None

        # self.logger.writeDebug('20240726 volume_data={}',volume_data)
        if isinstance(volume_data, list):
            volume_in_dict = [volume.to_dict() for volume in volume_data]
        elif isinstance(volume_data, dict):
            volume_in_dict = volume_data.get("lun")
        else:
            volume_in_dict = volume_data.to_dict() if volume_data else {}

        if not isinstance(volume_in_dict, list):
            return vsp_volume.VolumeCommonPropertiesExtractor(self.serial).extract(
                [volume_in_dict]
            )[0]
        else:
            return vsp_volume.VolumeCommonPropertiesExtractor(self.serial).extract(
                volume_in_dict
            )


def main():
    """
    :return: None
    """
    obj_store = VSPVolume()
    obj_store.apply()


if __name__ == "__main__":
    main()
