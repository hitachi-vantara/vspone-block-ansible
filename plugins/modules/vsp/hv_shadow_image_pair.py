#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_shadow_image_pair
short_description: Manages shadow image pairs on Hitachi VSP storage systems.
description:
  - This module allows for the creation, deletion, splitting, syncing and restoring of shadow image pairs on Hitachi VSP storage systems.
  - It supports various shadow image pairs operations based on the specified task level.
  - This module is supported for both C(direct) and C(gateway) connection types.
  - For C(direct) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/shadow_image_pair.yml)
  - For C(gateway) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/shadow_image_pair.yml)
version_added: '3.0.0'
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
    description: The level of the shadow image pairs task. Choices are C(present), C(absent), C(split), C(restore), C(sync).
    type: str
    required: false
    choices: ['present', 'absent', 'split', 'restore', 'sync']
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
  connection_info:
    description: Information required to establish a connection to the storage system.
    required: true
    type: dict
    suboptions:
      address:
        description: IP address or hostname of either the UAI gateway (if connection_type is C(gateway) ) or
          the storage system (if connection_type is C(direct)).
        type: str
        required: true
      username:
        description: Username for authentication.This field is valid for C(direct) connection type only, and it is a required field.
        type: str
        required: false
      password:
        description: Password for authentication.This field is valid for C(direct) connection type only, and it is a required field.
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
        description:
          Token value to access UAI gateway. This is a required field for C(gateway) connection type.
          This field is used for C(direct) connection type to pass the value of the lock token to operate on locked resources.
        type: str
        required: false
  spec:
    description: Specification for the shadow image pairs task.
    type: dict
    required: true
    suboptions:
      primary_volume_id:
        description: Primary volume id.
        type: int
        required: true
      secondary_volume_id:
        description: Secondary volume id.
        type: int
        required: false
      secondary_pool_id:
        description: Secondary storage pool id.
        type: int
        required: false
      auto_split:
        description: Auto split.
        type: bool
        required: false
      allocate_new_consistency_group:
        description: New consistency group.
        type: bool
        required: false
      consistency_group_id:
        description: Consistency group id.
        type: int
        required: false
      copy_pace_track_size:
        description: Copy pace track size.
        type: str
        required: false
        choices: ['SLOW', 'MEDIUM', 'FAST']
      enable_quick_mode:
        description: Enable quick mode.
        type: bool
        required: false
      enable_read_write:
        description: Enable read write.
        type: bool
        required: false
      pair_id:
        description: Pair Id.
        type: str
        required: false
      is_data_reduction_force_copy:
        description: Enable data reduction force copy.
        type: bool
        required: false
"""

EXAMPLES = """
- name: Create a shadow image pair for gateway connection type
  hitachivantara.vspone_block.vsp.hv_shadow_image_pair:
    state: "present"
    storage_system_info:
      serial: 811150
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: 123456
    spec:
      primary_volume_id: 274
      secondary_volume_id: 277
      allocate_new_consistency_group: true
      copy_pace_track_size: "MEDIUM"

- name: Create shadow image pair for non-existing secondary volume for direct connection type
  hitachivantara.vspone_block.vsp.hv_shadow_image_pair:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    state: "present"
    spec:
      primary_volume_id: 274
      secondary_pool_id: 1
      allocate_new_consistency_group: true
      copy_pace_track_size: "MEDIUM"
      enable_quick_mode: false
      auto_split: true

- name: Split shadow image pair for gateway connection type
  hitachivantara.vspone_block.vsp.hv_shadow_image_pair:
    state: "split"
    storage_system_info:
      serial: 811150
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: 123456
    spec:
      primary_volume_id: 274
      secondary_volume_id: 277
      enable_quick_mode: true
      enable_read_write: false

- name: Sync shadow image pair for gateway connection type
  hitachivantara.vspone_block.vsp.hv_shadow_image_pair:
    state: "sync"
    storage_system_info:
      serial: 811150
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: 123456
    spec:
      primary_volume_id: 274
      secondary_volume_id: 277
      enable_quick_mode: true

- name: Create and Auto-Split shadow image pair for gateway connection type
  hitachivantara.vspone_block.vsp.hv_shadow_image_pair:
    state: "split"
    storage_system_info:
      serial: 811150
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: 123456
    spec:
      primary_volume_id: 274
      secondary_volume_id: 277
      copy_pace_track_size: "MEDIUM"

- name: Restore shadow image pair for gateway connection type
  hitachivantara.vspone_block.vsp.hv_shadow_image_pair:
    state: "restore"
    storage_system_info:
      serial: 811150
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: 123456
    spec:
      primary_volume_id: 274
      secondary_volume_id: 277
      enable_quick_mode: true

- name: Delete shadow image pair for gateway connection type
  hitachivantara.vspone_block.vsp.hv_shadow_image_pair:
    state: "absent"
    storage_system_info:
      serial: 811150
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: 123456
    spec:
      primary_volume_id: 274
      secondary_volume_id: 277
"""

RETURN = """
data:
  description: Newly created shadow image pair object.
  returned: success
  type: dict
  contains:
    consistency_group_id:
      description: Consistency group id.
      type: int
      sample: -1
    copy_pace_track_size:
      description: Copy pace track size.
      type: str
      sample: "MEDIUM"
    copy_rate:
      description: Copy rate.
      type: int
      sample: 100
    entitlement_status:
      description: Entitlement status.
      type: str
      sample: "assigned"
    mirror_unit_id:
      description: Mirror unit id.
      type: int
      sample: -1
    partner_id:
      description: Partner id.
      type: str
      sample: "partner123"
    primary_hex_volume_id:
      description: Primary hex volume id.
      type: str
      sample: "00:01:12"
    primary_volume_id:
      description: Primary volume id.
      type: int
      sample: 274
    resource_id:
      description: Resource id.
      type: str
      sample: "localpair-2749fed78e8d23a61ed17a8af71c85f8"
    secondary_hex_volume_id:
      description: Secondary hex volume id.
      type: str
      sample: "00:01:17"
    secondary_volume_id:
      description: Secondary volume id.
      type: int
      sample: 279
    status:
      description: Status.
      type: str
      sample: "PAIR"
    storage_serial_number:
      description: Storage serial number.
      type: str
      sample: "811150"
    subscriber_id:
      description: Subscriber id.
      type: str
      sample: "subscriber123"
    svol_access_mode:
      description: Svol access mode.
      type: str
      sample: "READONLY"
    pvol_nvm_subsystem_name:
      description: Primary volume's nvm subsystem name.
      type: str
      sample: "smrha-3950276934"
    svol_nvm_subsystem_name:
      description: Secondary volume's nvm subsystem name.
      type: str
      sample: "smrha-3950276934"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPShadowImagePairArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    StateValue,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_shadow_image_pair_reconciler,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    operation_constants,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.message.module_msgs import (
    ModuleMessage,
)


class VSPShadowImagePairManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = VSPShadowImagePairArguments().shadow_image_pair()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )

        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.params_manager.get_connection_info()
            self.serial = self.params_manager.get_serial()
            self.state = self.params_manager.get_state()
            if self.state is None:
                self.state = StateValue.PRESENT
            self.logger.writeDebug(f"State: {self.state}")

            self.spec = self.params_manager.set_shadow_image_pair_spec()

        except Exception as e:
            self.logger.writeError(f"An error occurred during initialization: {str(e)}")
            self.module.fail_json(msg=str(e))

    def shadow_image_pair(self):
        reconciler = vsp_shadow_image_pair_reconciler.VSPShadowImagePairReconciler(
            self.params_manager.connection_info,
            self.params_manager.storage_system_info.serial,
            self.spec,
        )
        if self.connection_info.connection_type.lower() == ConnectionTypes.GATEWAY:
            oob = reconciler.is_out_of_band()
            if oob is True:
                raise ValueError(ModuleMessage.OOB_NOT_SUPPORTED.value)

        return reconciler.shadow_image_pair_module(self.state)

    def apply(self):
        self.logger.writeInfo("=== Start of Shadow Image operation. ===")
        registration_message = validate_ansible_product_registration()
        self.logger.writeInfo(
            f"{self.params_manager.connection_info.connection_type} connection type"
        )
        shadow_image_resposne = None
        try:
            shadow_image_resposne = self.shadow_image_pair()

        except Exception as e:
            self.logger.writeError(f"An error occurred: {str(e)}")
            self.logger.writeInfo("=== End of Shadow Image operation. ===")
            self.module.fail_json(msg=str(e))
        operation = operation_constants(self.module.params["state"])
        msg = (
            f"Shadow image pair {operation} successfully."
            if not isinstance(shadow_image_resposne, str)
            else shadow_image_resposne
        )
        response = {
            "changed": self.connection_info.changed,
            "data": (
                shadow_image_resposne
                if not isinstance(shadow_image_resposne, str)
                else None
            ),
            "msg": msg,
        }
        if registration_message:
            response["registration_message"] = registration_message
        self.logger.writeInfo(f"{response}")
        self.logger.writeInfo("=== End of Shadow Image operation. ===")
        self.module.exit_json(**response)


def main(module=None):

    obj_store = VSPShadowImagePairManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
