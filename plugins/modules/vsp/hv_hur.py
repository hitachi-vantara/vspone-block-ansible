#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_hur
short_description: Manages HUR pairs on Hitachi VSP storage systems.
description:
  - This module allows for the creation, deletion, splitting, swap splitting, re-syncing and swap-resyncing of HUR pairs on Hitachi VSP storage systems.
  - This module is supported for both C(direct) and C(gateway) connection types.
  - swap_split and swap_resync are supported for C(direct) connection type only.
  - For C(direct) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/hur.yml)
  - For C(gateway) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/hur.yml)
version_added: '3.1.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.8
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: none
options:
  state:
    description: The level of the HUR pairs task.
      Note C(swap_split) and C(swap_resync) are supported for C(direct) connection type only.
    type: str
    required: false
    choices: ['present', 'absent', 'split', 'resync', 'resize', 'expand', 'swap_split', 'swap_resync']
    default: 'present'
  storage_system_info:
    description: Information about the Hitachi storage system. This field is required for gateway connection type only.
    type: dict
    required: false
    suboptions:
      serial:
        description: Serial number of the Hitachi storage system.
        type: str
        required: false
  secondary_connection_info:
    description: Information required to establish a connection to the secondary storage system.
    required: false
    type: dict
    suboptions:
      address:
        description: IP address or hostname of the secondary storage system.
        type: str
        required: true
      username:
        description: Username for authentication for the secondary storage system.
        type: str
        required: false
      password:
        description: Password for authentication for the secondary storage system.
        type: str
        required: false
      api_token:
        description: Value of the lock token to operate on locked resources.
        type: str
        required: false
  connection_info:
    description: Information required to establish a connection to the storage system.
    required: true
    type: dict
    suboptions:
      address:
        description: IP address or hostname of either the UAI gateway (if connection_type is C(gateway))
          or the storage system (if connection_type is C(direct)).
        type: str
        required: true
      username:
        description: Username for authentication. This field is valid for C(direct) connection type only, and it is a required field.
        type: str
        required: false
      password:
        description: Password for authentication. This field is valid for C(direct) connection type only, and it is a required field.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['gateway', 'direct']
        default: 'direct'
      subscriber_id:
        description: This field is valid for C(gateway) connection type only. This is an optional field and only needed to support multi-tenancy environment.
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway.
        type: str
        required: false
  spec:
    description: Specification for the HUR pairs task.
    type: dict
    required: true
    suboptions:
      primary_volume_id:
        description: Primary volume id.
        type: int
        required: false
      primary_volume_journal_id:
        description: Primary volume journal id, required for create.
        type: int
        required: false
      secondary_volume_journal_id:
        description: Secondary volume journal id, required for create.
        type: int
        required: false
      copy_group_name:
        description: Name of the copy group. This is valid for C(direct) connection type only and this is a required for create operation.
        type: str
        required: false
      copy_pair_name:
        description: Name of the copy pair. This is valid for C(direct) connection type only and this is a required for create operation.
        type: str
        required: false
      consistency_group_id:
        description: Consistency group ID, optional.
        type: int
        required: false
      local_device_group_name:
        description: Name of the local device group name. This is valid for C(direct) connection type only and this is an optional field.
        type: str
        required: false
      remote_device_group_name:
        description: Name of the remote device group name. This is valid for C(direct) connection type only and this is an optional field..
        type: str
        required: false
      mirror_unit_id:
        description: Mirror Unit Id, required for create operations in new copy group. Not required for pair creation in existing copy group.
        type: int
        choices: [0, 1, 2, 3]
        required: false
      secondary_pool_id:
        description: Id of dynamic pool on the secondary storage where the secondary volume will be created.
        type: int
        required: false
      secondary_hostgroup:
        description: Host group details of secondary volume.
        type: dict
        required: false
        suboptions:
          name:
            description: Name of the host group on the secondary storage system. This is required for create operation
              for both C(direct) and C(gateway) connections.
            type: str
            required: true
          port:
            description: Port of the host group on the secondary storage system. This is required for create operation
              for both C(direct) and C(gateway) connections.
            type: str
            required: true
      secondary_nvm_subsystem:
        description: NVM subsystem details of the secondary volume. Supported only for C(direct) connection type.
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
      fence_level:
        description: Specifies the primary volume fence level setting and determines if the host is denied access or continues to access
            the primary volume when the pair is suspended because of an error. This is an optional field for both C(direct) and C(gateway) connections.
        type: str
        required: false
        choices: ['ASYNC']
        default: 'ASYNC'
      allocate_new_consistency_group:
        description: Specify whether to allocate a new consistency group.
        type: bool
        required: false
        default: false
      enable_delta_resync:
        description: Specify whether to enable delta resync.
        type: bool
        required: false
        default: false
      is_consistency_group:
        description: Specify whether to enable consistency group.
        type: bool
        required: false
        default: false
      do_delta_resync_suspend:
        description: Specify whether to enable delta resync suspend.
        type: bool
        required: false
      is_new_group_creation:
        description: Specify whether to enable new group creation.
        type: bool
        required: false
      is_svol_readwriteable:
        description: Specify whether to enable secondary volume read writeable.
        type: bool
        required: false
      secondary_storage_serial_number:
        description: Secondary storage serial number.
        type: int
        required: false
      secondary_volume_id:
        description: Secondary volume id.
        type: int
        required: false
      new_volume_size:
        description: New volume size.
        type: str
        required: false
      begin_secondary_volume_id:
        description: Specify beginning ldev id for Ldev range for svol. This is used only for C(gateway) connection and is an optional field during
          create operation. If this field is specified, end_secondary_volume_id must also be specified.
          If this field is not specified, Ansible modules will try to create SVOL ID same as (or near to ) PVOL ID.
        required: false
        type: int
      end_secondary_volume_id:
        description: Specify end ldev id for Ldev range for svol. This is used only for C(gateway) connection and is an optional field during create operation.
          If this field is specified, begin_secondary_volume_id must also be specified.
          If this field is not specified, Ansible modules will try to create SVOL ID same as (or near to ) PVOL ID.
        required: false
        type: int
      do_initial_copy:
        description: Perform initial copy. This is used only for C(direct) connection and is an optional field during create operation.
        type: bool
        required: false
        default: true
      is_data_reduction_force_copy:
        description: Force copy for data reduction. This is used for both C(direct) and C(gateway) connections and is an optional field during create operation.
        type: bool
        required: false
        default: false
"""

EXAMPLES = """
- name: Create a HUR pair in new copy group for direct connection type
  hitachivantara.vspone_block.vsp.hv_hur:
    state: "present"
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    secondary_connection_info:
      address: storage2.company.com
      username: "admin"
      password: "secret"
    spec:
      copy_group_name: hur_copy_group_name_1
      copy_pair_name: hur_copy_pair_name_1
      primary_volume_id: 234
      secondary_pool_id: 0
      primary_volume_journal_id: 11
      secondary_volume_journal_id: 12
      local_device_group_name: hur_copy_group_name_1P_
      remote_device_group_name: hur_copy_group_name_1S_
      consistency_group_id: 0
      secondary_hostgroup:
        name: hg_1
        port: CL1-A
      mirror_unit_id: 0

- name: Create a HUR pair in existing copy group for direct connection type
  hitachivantara.vspone_block.vsp.hv_hur:
    state: "present"
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    secondary_connection_info:
      address: storage2.company.com
      username: "admin"
      password: "secret"
    spec:
      copy_group_name: "hur_copy_group_name_1"
      copy_pair_name: "hur_copy_pair_name_2"
      primary_volume_id: 334
      secondary_pool_id: 0
      secondary_hostgroup:
        name: hg_1
        port: CL1-A

- name: Split HUR pair for direct connection type
  hitachivantara.vspone_block.vsp.hv_hur:
    state: "split"
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    secondary_connection_info:
      address: storage2.company.com
      username: "admin"
      password: "secret"
    spec:
      local_device_group_name: hur_local_device_group_name_3
      remote_device_group_name: hur_remote_device_group_name_3
      copy_group_name: hur_copy_group_name_3
      copy_pair_name: hur_copy_pair_name_3
      is_svol_readwriteable: true

- name: Resync HUR pair for direct connection type
  hitachivantara.vspone_block.vsp.hv_hur:
    state: "resync"
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    secondary_connection_info:
      address: storage2.company.com
      username: "admin"
      password: "secret"
    spec:
      local_device_group_name: hur_local_device_group_name_3
      remote_device_group_name: hur_remote_device_group_name_3
      copy_group_name: hur_copy_group_name_3
      copy_pair_name: hur_copy_pair_name_3

- name: Delete HUR pair for direct connection type
  hitachivantara.vspone_block.vsp.hv_hur:
    state: "absent"
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    secondary_connection_info:
      address: storage2.company.com
      username: "admin"
      password: "secret"
    spec:
      local_device_group_name: hur_local_device_group_name_3
      remote_device_group_name: hur_remote_device_group_name_3
      copy_group_name: hur_copy_group_name_3
      copy_pair_name: hur_copy_pair_name_3
"""

RETURN = r"""
data:
  description: Newly created HUR pair object.
  returned: success
  type: dict
  contains:
    consistency_group_id:
      description: Consistency group ID.
      type: int
      sample: 9
    copy_group_name:
      description: Name of the copy group.
      type: str
      sample: "HUR_TEST_GROUP_ZM_1"
    copy_pair_name:
      description: Name of the copy pair.
      type: str
      sample: "HUR_TEST_PAIR_ZM_3"
    fence_level:
      description: Fence level setting.
      type: str
      sample: "ASYNC"
    mirror_unit_number:
      description: Mirror unit number.
      type: int
      sample: 2
    pvol_difference_data_management:
      description: Difference data management for primary volume.
      type: str
      sample: "S"
    pvol_journal_id:
      description: Journal ID for primary volume.
      type: int
      sample: 12
    pvol_ldev_id:
      description: LDEV ID for primary volume.
      type: int
      sample: 1848
    pvol_processing_status:
      description: Processing status for primary volume.
      type: str
      sample: "N"
    pvol_status:
      description: Status of primary volume.
      type: str
      sample: "PAIR"
    pvol_storage_device_id:
      description: Storage device ID for primary volume.
      type: str
      sample: "900000040014"
    pvol_storage_serial_number:
      description: Storage serial number for primary volume.
      type: str
      sample: "40014"
    remote_mirror_copy_pair_id:
      description: Remote mirror copy pair ID.
      type: str
      sample: "900000040015,HUR_TEST_GROUP_ZM_1,HUR_TEST_GROUP_ZM_1P_,HUR_TEST_GROUP_ZM_1S_,HUR_TEST_PAIR_ZM_3"
    replication_type:
      description: Replication type.
      type: str
      sample: "UR"
    svol_difference_data_management:
      description: Difference data management for secondary volume.
      type: str
      sample: "S"
    svol_journal_id:
      description: Journal ID for secondary volume.
      type: int
      sample: 32
    svol_ldev_id:
      description: LDEV ID for secondary volume.
      type: int
      sample: 1978
    svol_processing_status:
      description: Processing status for secondary volume.
      type: str
      sample: "N"
    svol_status:
      description: Status of secondary volume.
      type: str
      sample: "PAIR"
    svol_storage_device_id:
      description: Storage device ID for secondary volume.
      type: str
      sample: "900000040015"
    svol_storage_serial_number:
      description: Storage serial number for secondary volume.
      type: str
      sample: "40015"
"""


from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPHurArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_hur import (
    VSPHurReconciler,
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
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.message.module_msgs import (
    ModuleMessage,
)


@LogDecorator.debug_methods
class VSPSHurManager:

    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPHurArguments().hur()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )
        try:

            self.params_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.params_manager.get_connection_info()
            self.secondary_connection_info = (
                self.params_manager.get_secondary_connection_info()
            )
            self.storage_serial_number = self.params_manager.get_serial()
            self.spec = self.params_manager.hur_spec()
            self.state = self.params_manager.get_state()
            if self.secondary_connection_info:
                self.spec.secondary_connection_info = self.secondary_connection_info

        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of HUR operation. ===")
        self.logger.writeDebug(
            f"{self.params_manager.connection_info.connection_type} connection type"
        )
        registration_message = validate_ansible_product_registration()
        try:

            unused, data = self.hur_module()
            if data is None:
                data = []

        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of HUR operation. ===")
            self.module.fail_json(msg=str(e))

        # msg = comment
        # if msg is None:
        msg = self.get_message()
        if "already exits in copy group" in data:
            msg = "Please specify unique copy pair name."

        resp = {
            "changed": self.connection_info.changed,
            "hur_info": data,
            "msg": msg,
        }
        if registration_message:
            resp["user_consent_required"] = registration_message
        self.logger.writeInfo(f"{resp}")
        self.logger.writeInfo("=== End of HUR operation. ===")
        self.module.exit_json(**resp)

    def hur_module(self):
        reconciler = VSPHurReconciler(
            self.connection_info,
            self.storage_serial_number,
            self.state,
            self.secondary_connection_info,
        )
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            found = reconciler.check_storage_in_ucpsystem()
            if not found:
                raise ValueError(ModuleMessage.STORAGE_SYSTEM_ONBOARDING.value)
            oob = reconciler.is_out_of_band()
            if oob is True:
                raise ValueError(ModuleMessage.OOB_NOT_SUPPORTED.value)

        comment, result = reconciler.reconcile_hur(
            self.spec, self.secondary_connection_info
        )
        return comment, result

    def get_message(self):

        if self.state == "present":
            return "HUR Pair created successfully."
        elif self.state == "absent":
            return "HUR Pair deleted successfully."
        elif self.state == "resync":
            return "HUR Pair resynced successfully."
        elif self.state == "split":
            return "HUR Pair split successfully."
        elif self.state == "swap_split":
            return "HUR Pair swapped split successfully."
        elif self.state == "swap_resync":
            return "HUR Pair swapped resynced successfully"
        elif self.state == "resize" or self.state == "expand":
            return "HUR Pair expanded successfully"
        else:
            return "Unknown state provided."


def main(module=None):
    """
    :return: None
    """
    obj_store = VSPSHurManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
