#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_gad_bulk
short_description: Manages batch GAD pairs on VSP block storage systems.
description:
  - This module allows for the batch creation of multiple GAD pairs on VSP block storage systems.
  - It supports creating GAD pairs with new volumes, existing volumes, or a range of volumes.
  - Enables efficient provisioning of multiple GAD pairs in a single operation.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/gad_pair_bulk.yml)
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
- hitachivantara.vspone_block.common.connection_with_type
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
        description: Password for authentication. This field is required for secondary storage connection if api_token is not provided.
        type: str
        required: false
      api_token:
        description: Value of the lock token to operate on locked resources.
        type: str
        required: false
  spec:
    description: Specification for the batch GAD pairs task.
    type: dict
    required: true
    suboptions:
      should_match_volume_ids:
        description: Specify whether the primary volume ID and secondary volume ID should match in gad pairs. Default value is false.
        type: bool
        required: false
      secondary_pool_id:
        description: Pool ID of the secondary storage system for creating secondary volumes.
        type: int
        required: false
      consistency_group_id:
        description: Consistency Group ID.
        type: int
        required: false
      allocate_new_consistency_group:
        description: Allocate and assign a new consistency group ID.
        type: bool
        required: false
      set_alua_mode:
        description: Set the ALUA mode to True for cross path server configuration.
        type: bool
        required: false
      primary_resource_group_name:
        description: The primary resource group name.
          Required for the Create GAD pair with cross path server configuration task.
        type: str
        required: false
      secondary_resource_group_name:
        description: The secondary resource group name.
        type: str
        required: false
      quorum_disk_id:
        description: The quorum disk ID. Required for the Create tasks.
        type: int
        required: false
      primary_hostgroups:
        description: The list of host groups on the primary storage device.
          Required for the Create GAD pair with server cluster configuration task.
        type: list
        elements: dict
        required: false
        suboptions:
          name:
            description: Host group name.
              Required for the Create GAD pair with server cluster configuration
              /Create GAD pair with cross path server configuration tasks.
            type: str
            required: true
          port_id:
            description: Port ID.
              Required for the Create GAD pair with server cluster configuration
              /Create GAD pair with cross path server configuration tasks.
            type: str
            required: true
      secondary_hostgroups:
        description: The list of host groups on the secondary storage device. Required for the Create tasks.
        type: list
        elements: dict
        required: false
        suboptions:
          name:
            description: Host group name. Required for the Create tasks.
            type: str
            required: true
          port_id:
            description: Port ID. Required for the Create tasks.
            type: str
            required: true
      primary_iscsi_targets:
        description: The list of iscsi targets on the primary storage device.
          Required for the Create GAD-ISCSI Pair task.
        type: list
        elements: dict
        required: false
        suboptions:
          name:
            description: ISCSI target name. Required for the Create GAD-ISCSI Pair task.
            type: str
            required: true
          port_id:
            description: Port ID. Required for the Create GAD-ISCSI Pair task.
            type: str
            required: true
      secondary_iscsi_targets:
        description: The list of iscsi targets on the secondary storage device.
          Required for the Create GAD-ISCSI Pair task.
        type: list
        elements: dict
        required: false
        suboptions:
          name:
            description: ISCSI target name. Required for the Create GAD-ISCSI Pair task.
            type: str
            required: true
          port_id:
            description: Port ID. Required for the Create GAD-ISCSI Pair task.
            type: str
            required: true
      local_device_group_name:
        description: The device group name in the local storage system.
          Optional for the Split/Resync/Swap-Split/Swap-Resync tasks.
        type: str
        required: false
      remote_device_group_name:
        description: The device group name in the remote storage system.
          Optional for the Split/Resync/Swap-Split/Swap-Resync tasks.
        type: str
        required: false
      copy_pair_base_name:
        description: Base name for copy pairs. Pairs will be named with incrementing numbers appended.
        type: str
        required: false
      path_group_id:
        description: Path group ID.
        type: int
        required: false
      copy_group_name:
        description: The name for the copy group.
        type: str
        required: false
      copy_pace:
        description: Copy pace to be used for the GAD pair, Supports 1 to 15.
        type: int
        required: false
        default: 3
      mirror_unit_number:
        description: The mirror unit number.
        type: str
        required: false
      fence_level:
        description: Fence level for the GAD pairs.
        type: str
        required: false
        choices: ['NEVER', 'DATA', 'STATUS', 'UNKNOWN']
        default: 'NEVER'
      is_data_reduction_force_copy:
        description: Whether to forcibly create a pair for data reduction volumes.
        type: bool
        required: false
        default: true
      do_initial_copy:
        description: Whether to perform an initial copy.
        type: bool
        required: false
        default: true
      is_consistency_group:
        description: Specify true for consistency group.
        type: bool
        required: false
      is_new_group_creation:
        description: Specify true for a new copy group name.
        type: bool
        required: false
      new_volume_size:
        description: New volume size for resize or expand operations.
        type: str
        required: false
      begin_secondary_volume_id:
        description: Beginning LDEV ID for secondary volume range.
        type: str
        required: false
      end_secondary_volume_id:
        description: End LDEV ID for secondary volume range.
        type: str
        required: false
      provisioned_secondary_volume_id:
        description: ID of the provisioned secondary volume for GAD pair creation.
        type: str
        required: false
      secondary_nvm_subsystem:
        description: NVM subsystem details of the secondary volume.
        type: dict
        required: false
        suboptions:
          name:
            description: Name of the NVM subsystem on the secondary storage system.
            type: str
            required: true
          paths:
            description: Host NQN paths information on the secondary storage system.
            type: list
            elements: str
            required: false
      primary_nvm_subsystem:
        description: NVM subsystem details of the primary volume.
        type: dict
        required: false
        suboptions:
          name:
            description: Name of the NVM subsystem on the primary storage system.
            type: str
            required: true
          paths:
            description: Host NQN paths information on the primary storage system.
            type: list
            elements: str
            required: false
      number_of_pairs:
        description: Number of GAD pairs to create in batch.
        type: int
        required: false
      begin_primary_volume_id:
        description: Beginning primary volume ID for batch creation using existing volumes.
        type: int
        required: false
      end_primary_volume_id:
        description: Ending primary volume ID for batch creation using existing volumes.
        type: int
        required: false
      primary_volume_base_name:
        description: Base name for primary volumes when creating new volumes in batch.
        type: str
        required: false
      primary_volume_base_name_start_number:
        description: Starting number for primary volume base name suffix.
        type: int
        required: false
      primary_pool_id:
        description: Pool ID for creating new primary volumes.
        type: int
        required: false
      volume_size:
        description: Size of volumes to create (e.g., '10GB', '1TB').
        type: str
        required: false
      capacity_saving:
        description: Capacity saving mode for new volumes (e.g., 'compression', 'compression_deduplication').
        type: str
        required: false
      virtual_storage_serial_number:
        description: Virtual storage serial number for GAD pair creation.
        type: str
        required: false
"""

EXAMPLES = """
- name: Batch create GAD pairs with host groups
  hitachivantara.vspone_block.vsp.hv_gad_bulk:
    connection_info:
      address: storage1.company.com
      username: "username"
      password: "password"
    secondary_connection_info:
      address: storage2.company.com
      username: "admin"
      password: "secret"
    spec:
      number_of_pairs: 5
      primary_pool_id: 0
      secondary_pool_id: 0
      volume_size: "10GB"
      capacity_saving: "compression"
      primary_volume_base_name: "gad_vol"
      primary_volume_base_name_start_number: 1
      copy_group_name: "batch_gad_cg"
      copy_pair_base_name: "batch_pair"
      quorum_disk_id: 0
      is_new_group_creation: true
      primary_hostgroups:
        - name: "primary_hg_1"
          port_id: "CL1-A"
          enable_preferred_path: true
      secondary_hostgroups:
        - name: "secondary_hg_1"
          port_id: "CL2-A"
          enable_preferred_path: false

- name: Batch create GAD pairs with host groups
  hitachivantara.vspone_block.vsp.hv_gad_bulk:
    connection_info:
      address: storage1.company.com
      username: "username"
      password: "password"
    secondary_connection_info:
      address: storage2.company.com
      username: "admin"
      password: "secret"
    spec:
      number_of_pairs: 5
      should_match_volume_ids: true
      primary_pool_id: 0
      secondary_pool_id: 0
      volume_size: "10GB"
      capacity_saving: "compression"
      primary_volume_base_name: "gad_vol"
      primary_volume_base_name_start_number: 1
      copy_group_name: "batch_gad_cg"
      copy_pair_base_name: "batch_pair"
      quorum_disk_id: 0
      is_new_group_creation: true
      primary_hostgroups:
        - name: "primary_hg_1"
          port_id: "CL1-A"
          enable_preferred_path: true
      secondary_hostgroups:
        - name: "secondary_hg_1"
          port_id: "CL2-A"
          enable_preferred_path: false

- name: Batch create GAD pairs with NVMe subsystems
  hitachivantara.vspone_block.vsp.hv_gad_bulk:
    connection_info:
      address: storage1.company.com
      username: "username"
      password: "password"
    secondary_connection_info:
      address: storage2.company.com
      username: "admin"
      password: "secret"
    spec:
      number_of_pairs: 3
      primary_pool_id: 0
      secondary_pool_id: 0
      volume_size: "20GB"
      copy_group_name: "nvme_gad_cg"
      copy_pair_base_name: "nvme_pair"
      quorum_disk_id: 0
      is_new_group_creation: true
      primary_nvm_subsystem:
        name: "primary-nvme-subsystem"
        paths:
          - "nqn.2014-08.com.example:nvme:primary-host"
      secondary_nvm_subsystem:
        name: "secondary-nvme-subsystem"
        paths:
          - "nqn.2014-08.com.example:nvme:secondary-host"

- name: Batch create GAD pairs with iSCSI targets
  hitachivantara.vspone_block.vsp.hv_gad_bulk:
    connection_info:
      address: storage1.company.com
      username: "username"
      password: "password"
    secondary_connection_info:
      address: storage2.company.com
      username: "admin"
      password: "secret"
    spec:
      number_of_pairs: 4
      primary_pool_id: 0
      secondary_pool_id: 0
      volume_size: "50GB"
      copy_group_name: "iscsi_gad_cg"
      copy_pair_base_name: "iscsi_pair"
      quorum_disk_id: 0
      is_new_group_creation: true
      primary_iscsi_targets:
        - name: "iscsi_hg_primary"
          port_id: "CL3-A"
      secondary_iscsi_targets:
        - name: "iscsi_target_secondary"
          port_id: "CL4-A"
          enable_preferred_path: false
"""

RETURN = """
gad_pairs:
  description: List of created GAD pair objects from the batch operation.
  returned: success
  type: list
  elements: dict
  contains:
    consistency_group_id:
      description: Consistency group ID.
      type: int
      sample: -1
    copy_group_name:
      description: Copy group name.
      type: str
      sample: "cp_group_840"
    copy_pace_track_size:
      description: Deprecated. Copy pace track size.
      type: int
      sample: ""
    copy_pair_name:
      description: Pair name.
      type: str
      sample: "gad_pair_840"
    copy_rate:
      description: Deprecated. Copy rate.
      type: str
      sample: ""
    fence_level:
      description: Fence level.
      type: str
      sample: "NEVER"
    is_alua_enabled:
      description: Whether ALUA is enabled or not.
      type: bool
      sample: false
    local_device_group_name:
      description: Local device group name.
      type: str
      sample: "cp_group_840S_"
    mirror_unit_id:
      description: Deprecated. Use mirror_unit_number instead.
      type: int
      sample: 0
    mirror_unit_number:
      description: Mirror unit number.
      type: int
      sample: 0
    primary_virtual_serial_number:
      description: Primary virtual serial number.
      type: int
      sample: -1
    primary_virtual_volume_id:
      description: Primary virtual volume id.
      type: int
      sample: -1
    primary_volume_id:
      description: Primary volume ID.
      type: int
      sample: 840
    primary_volume_id_hex:
      description: Primary volume ID in hexadecimal format.
      type: str
      sample: "00:03:48"
    primary_volume_status:
      description: Status of the GAD pair.
      type: str
      sample: "PSUE"
    primary_volume_storage_id:
      description: Deprecated. Use primary_volume_storage_serial_number instead.
      type: str
      sample: "810050"
    primary_volume_storage_serial_number:
      description: Primary volume storage serial number.
      type: str
      sample: "810050"
    primary_vsm_resource_group_name:
      description: Primary VSM resource group name.
      type: str
      sample: ""
    quorum_disk_id:
      description: Quorum disk ID.
      type: int
      sample: 21
    remote_device_group_name:
      description: Remote device group name.
      type: str
      sample: "cp_group_840P_"
    remote_mirror_copy_pair_id:
      description: Deprecated. Remote mirror copy pair ID.
      type: str
      sample: "A34000810050,cp_group_840,cp_group_840S_,cp_group_840P_,gad_pair_840"
    secondary_virtual_serial_number:
      description: Secondary virtual storage serial number.
      type: int
      sample: -1
    secondary_virtual_volume_id:
      description: Secondary virtual volume ID.
      type: int
      sample: -1
    secondary_volume_id:
      description: Secondary volume ID.
      type: int
      sample: 831
    secondary_volume_id_hex:
      description: Secondary volume ID in hexadecimal format.
      type: str
      sample: "00:03:3F"
    secondary_volume_status:
      description: Status of the GAD pair.
      type: str
      sample: "PSUE"
    secondary_volume_storage_id:
      description: Deprecated. Use secondary_volume_storage_serial_number instead.
      type: str
      sample: "810045"
    secondary_volume_storage_serial_number:
      description: Secondary volume storage serial number.
      type: str
      sample: "810045"
    secondary_vsm_resource_group_name:
      description: Secondary VSM resource group name.
      type: str
      sample: ""
comments:
  description: List of comments or warnings from the batch operation.
  returned: success
  type: list
  elements: str
  sample: []
"""


from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_gad_pair,
)
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPGADArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class VSPBatchGADPairManager:

    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPGADArguments().batch_gad_pair_args_spec()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.batch_gad_pair_spec()
            self.serial = self.params_manager.get_serial()
            self.state = self.params_manager.get_state()
            self.connection_info = self.params_manager.get_connection_info()
            self.secondary_connection_info = (
                self.params_manager.get_secondary_connection_info()
            )
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        try:
            registration_message = validate_ansible_product_registration()
            self.logger.writeInfo("=== Start of Batch GAD operation. ===")
            reconciler = vsp_gad_pair.VSPGadPairReconciler(
                self.connection_info, self.secondary_connection_info, self.serial
            )
            response = reconciler.gad_batch_reconcile(
                self.state, self.spec, self.secondary_connection_info
            )

            failed_json = {}
            if self.spec.comments:
                failed_json["gad_pairs"] = response
                str_comments = "\n".join(self.spec.comments)
                self.module.fail_json(msg=str_comments, exception=None, **failed_json)

            response_dict = {
                "changed": self.connection_info.changed,
                "gad_pairs": response,
                "comments": self.spec.comments if self.spec.comments else [],
            }
            if registration_message:
                response_dict["user_consent_required"] = registration_message

            self.logger.writeInfo(f"{response_dict}")
            self.logger.writeInfo("=== End of Batch GAD operation. ===")
            self.module.exit_json(**response_dict)
        except Exception as ex:
            self.logger.writeException(ex)
            self.logger.writeInfo("=== End of Batch GAD operation. ===")
            self.module.fail_json(msg=str(ex))


def main():
    obj_store = VSPBatchGADPairManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
