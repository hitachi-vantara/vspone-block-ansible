#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_truecopy_bulk
short_description: Manages bulk TrueCopy pairs on VSP block storage systems.
description:
  - This module allows for the bulk creation of TrueCopy pairs n VSP block storage systems
  - Enables efficient provisioning of multiple TrueCopy pairs in a single operation.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/truecopy_bulk.yml)
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
  state:
    description:
      - Set state to C(present) for creating HUR pairs in bulk.
    type: str
    required: false
    choices: ['present']
    default: 'present'
  secondary_connection_info:
    description: Information required to establish a connection to the secondary storage system.
    required: false
    type: dict
    suboptions:
      address:
        description:
          - IP address or hostname of the Hitachi storage system.
        type: str
        required: true
      username:
        description: Username for authentication. This is a required field if api_token is not provided.
        type: str
        required: false
      password:
        description: Password for authentication.This is a required field if api_token is not provided.
        type: str
        required: false
      api_token:
        description: This field is used to pass the value of the lock token of the secondary storage to operate on locked resources.
        type: str
        required: false
  spec:
    description: Specification for the bulk TrueCopy pairs task.
    type: dict
    required: true
    suboptions:
      copy_group_name:
        description: Name of the copy group.
        type: str
        required: true
      copy_pair_base_name:
        description:  Prefix for the copy pairs names. Actual copy pair names will be <copy_pair_base_name>_<primary_volume_id>_<secondary_volume_id>
        type: str
        required: true
      copy_pace:
        description: Copy pace to be used for the GAD pair, Supports 1 to 15.
        type: int
        required: false
        default: 3
      remote_device_group_name:
        description: Name of the remote device group. This is an optional field.
        type: str
        required: false
      local_device_group_name:
        description: Name of the local device group. This is an optional field.
        type: str
        required: false
      consistency_group_id:
        description: Consistency Group ID, 0 to 255. This is an optional field.
        type: int
        required: false
      fence_level:
        description: Specifies the primary volume fence level setting and determines if the host is denied access or continues to access
            the primary volume when the pair is suspended because of an error. This is an optional field.
        type: str
        required: false
        choices: ['NEVER', 'DATA', 'STATUS']
        default: 'NEVER'
      primary_pool_id:
        description: ID of the dynamic pool where the primary volumes will be created.
        type: int
        required: true
      secondary_pool_id:
        description: ID of the dynamic pool where the secondary volumes will be created.
        type: int
        required: true
      begin_primary_volume_id:
        description: Beginning primary volume ID for batch creation using existing volumes.
        type: str
        required: false
      end_primary_volume_id:
        description: Ending primary volume ID for batch creation using existing volumes.
        type: str
        required: false
      begin_secondary_volume_id:
        description:  Begin LDEV ID for secondary volume range.
        required: false
        type: str
      end_secondary_volume_id:
        description: End LDEV ID for secondary volume range.
        required: false
        type: str
      primary_hostgroups:
        description: List of hostgroup objects for the primary volumes.
        type: list
        elements: dict
        required: false
        suboptions:
          name:
            description: Name of the host group on the secondary storage system. This is required for create operation.
            type: str
            required: true
          port_id:
            description: Port of the host group on the secondary storage system. This is required for create operation.
            type: str
            required: true
          lun_id:
            description: LUN ID of the host group on the secondary storage system. This is not required for create operation.
            type: int
            required: false
      secondary_hostgroups:
        description: List of hostgroup objects for the secondary volumes.
        type: list
        elements: dict
        required: false
        suboptions:
          name:
            description: Name of the host group on the secondary storage system. This is required for create operation.
            type: str
            required: true
          port_id:
            description: Port of the host group on the secondary storage system. This is required for create operation.
            type: str
            required: true
          lun_id:
            description: LUN ID of the host group on the secondary storage system. This is not required for create operation.
            type: int
            required: false
      primary_iscsi_targets:
        description: The list of iscsi targets on the primary storage device.
        type: list
        elements: dict
        required: false
        suboptions:
          name:
            description: ISCSI target name.
            type: str
            required: true
          port_id:
            description: Port ID.
            type: str
            required: true
          lun_id:
            description: LUN ID.
            type: int
            required: false
      secondary_iscsi_targets:
        description: The list of iscsi targets on the secondary storage device.
        type: list
        elements: dict
        required: false
        suboptions:
          name:
            description: ISCSI target name for the secondary storage system.
            type: str
            required: true
          port_id:
            description: Port ID.
            type: str
            required: true
          lun_id:
            description: LUN ID.
            type: int
            required: false
      primary_nvm_subsystem:
        description: NVM subsystem details of the primary volume..
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
      data_reduction_share:
        description: Specify whether to create a data reduction shared volume.
          This value is set to true for Thin Image Advance.
        type: bool
        required: false
      do_initial_copy:
        description: Perform initial copy. This is an optional field during create operation.
        type: bool
        required: false
        default: true
      is_data_reduction_force_copy:
        description: Force copy for data reduction. This is an optional field during create operation.
        type: bool
        required: false
        default: true
      is_new_group_creation:
        description: Create a new copy group. This is an optional field during create operation.
        type: bool
        required: false
      path_group_id:
        description: >
          This is an optional field during create operation.
          Specify the path group ID in the range from 0 to 255. If you are unsure don't use this parameter.
          If you omit this value or specify 0, the lowest path group ID in the specified path group is used.
        type: int
        required: false
      volume_size:
        description: Size of volumes to create (e.g., '10GB', '1TB') to create TrueCopy pairs.
        type: str
        required: true
      primary_volume_base_name:
        description: Prefix for primary volume names when creating new volumes in bulk.
        type: str
        required: false
      primary_volume_base_name_start_number:
        description: The starting number that will be appended to primary_volume_base_name to generate the first volume name during bulk creation.
        type: int
        required: false
      primary_volume_base_name_number_of_digits:
        description: Number of digits to use for the suffix of primary volume names during bulk creation.
        type: int
        required: false
        choices: [1, 2, 3, 4, 5]
      is_consistency_group:
        description: >
          This is an optional field during create operation.
          Depending on the value, this attribute specifies whether to register the new pair in a consistency group.
          If true, the new pair is registered in a consistency group. If false, the new pair is not registered in a consistency group.
        type: bool
        required: false
        default: false
      number_of_pairs:
        description: Number of GAD pairs to create in batch.
        type: int
        required: true
      capacity_saving:
        description: Capacity saving mode for new volumes (e.g., 'compression', 'deduplication_compression').
        type: str
        required: false
"""

EXAMPLES = """
- name: Create a TrueCopy pairs in bulk mode
  hitachivantara.vspone_block.vsp.hv_truecopy_bulk:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    secondary_connection_info:
      address: storage2.company.com
      username: "admin"
      password: "secret"
    spec:
      number_of_pairs: 2
      copy_group_name: "rd_tc_cg_123"
      copy_pair_base_name: "rd_tc_cp_123_"
      primary_pool_id: 0
      secondary_pool_id: 0
      volume_size: "1GB"
      primary_hostgroups:
        - name: "snewar-common-hg-01"
          port_id: "CL2-A"
        - name: "snewar-common-hg-01"
          port_id: "CL2-B"
      secondary_hostgroups:
        - name: "snewar-common-hg-01"
          port_id: "CL2-A"
        - name: "snewar-common-hg-01"
          port_id: "CL2-B"
"""

RETURN = r"""
truecopy_info:
  description: List of TrueCopy pair objects returned by the module.
  returned: success
  type: list
  elements: dict
  contains:
    consistency_group_id:
      description: Consistency Group ID.
      type: int
      sample: -1
    copy_group_name:
      description: Name of the copy group.
      type: str
      sample: "ESD_TC_CG"
    copy_pair_name:
      description: Name of the copy pair.
      type: str
      sample: "ESD_TC_CP"
    copy_progress_rate:
      description: Deprecated.Copy progress rate.
      type: int
      sample: -1
    fence_level:
      description: Fence level.
      type: str
      sample: "NEVER"
    local_device_group_name:
      description:
        - Name of the local device group to retrieve TrueCopy pair information for.
      type: str
      sample: "tc_bulk_cg_1P_"
    primary_volume_id:
      description: Primary volume ID.
      type: int
      sample: 11
    primary_volume_id_hex:
      description: Primary volume ID in hex format.
      type: str
      sample: "00:00:0B"
    primary_volume_size:
      description: Size of the primary volume.
      type: str
      sample: "4.00GB"
    primary_volume_status:
      description: Primary volume status.
      type: str
      sample: "PAIR"
    primary_volume_storage_serial_number:
      description: Storage serial number of the primary volume.
      type: str
      sample: "810050"
    pvol_status:
      description: Deprecated. Use primary_volume_status instead.
      type: str
      sample: "PAIR"
    pvol_storage_device_id:
      description: Deprecated. PVOL storage device ID.
      type: str
      sample: "A00000970041"
    remote_device_group_name:
      description:
        - Name of the remote device group to retrieve TrueCopy pair information for.
      type: str
      sample: "tc_bulk_cg_1S_"
    remote_mirror_copy_pair_id:
      description: Remote mirror copy pair ID.
      type: str
      sample: "A00000970045,ESD_TC_CG,ESD_TC_CGP_,ESD_TC_CGS_,ESD_TC_CP"
    secondary_volume_id:
      description: Secondary volume ID.
      type: int
      sample: 11
    secondary_volume_id_hex:
      description: Secondary volume ID in hex format.
      type: str
      sample: "00:00:0B"
    secondary_volume_size:
      description: Size of the secondary volume.
      type: str
      sample: "4.00GB"
    secondary_volume_status:
      description: Secondary volume status.
      type: str
      sample: "PAIR"
    secondary_volume_storage_serial_number:
      description: Storage serial number of the secondary volume.
      type: str
      sample: "810045"
    storage_serial_number:
      description: Deprecated. Use primary_volume_storage_serial_number instead.
      type: str
      sample: "810050"
    svol_status:
      description: Deprecated. Use secondary_volume_status instead.
      type: str
      sample: "PAIR"
    svol_storage_device_id:
      description: Deprecated. SVOL storage device ID.
      type: str
      sample: "A34000810045"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPTrueCopyBatchArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_true_copy import (
    VSPTrueCopyReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log_decorator import (
    LogDecorator,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


@LogDecorator.debug_methods
class VSPSTrueCopyManager:

    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPTrueCopyBatchArguments().true_copy_batch()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.params_manager.connection_info
            self.storage_serial_number = self.params_manager.storage_system_info.serial
            self.spec = self.params_manager.true_copy_batch_spec()
            self.state = self.params_manager.get_state()
            self.secondary_connection_info = (
                self.params_manager.get_secondary_connection_info()
            )
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of TrueCopy Batch operation. ===")
        data = None
        registration_message = validate_ansible_product_registration()

        self.logger.writeDebug("state = {}", self.state)
        try:
            data = self.true_copy_module()
            if data is None:
                data = []
        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of TrueCopy Batch operation. ===")
            self.module.fail_json(msg=str(e))

        resp = {
            "changed": self.connection_info.changed,
            "truecopy_info": data,
        }
        if self.spec.comments:
            resp["comments"] = self.spec.comments

        if registration_message:
            resp["user_consent_required"] = registration_message

        self.logger.writeInfo(f"{resp}")
        self.logger.writeInfo("=== End of TrueCopy Batch operation. ===")
        self.module.exit_json(**resp)

    def true_copy_module(self):
        reconciler = VSPTrueCopyReconciler(
            self.connection_info,
            self.storage_serial_number,
            self.state,
            self.secondary_connection_info,
        )
        return reconciler.reconcile_true_copy_hatch(self.spec)


def main(module=None):
    """
    :return: None
    """
    obj_store = VSPSTrueCopyManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
