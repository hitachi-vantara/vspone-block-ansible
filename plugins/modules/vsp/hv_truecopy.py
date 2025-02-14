#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_truecopy
short_description: Manages TrueCopy pairs on Hitachi VSP storage systems.
description: >
  - This module allows for the creation, deletion, splitting, re-syncing and resizing of TrueCopy pairs for
    both direct and gateway connections on Hitachi VSP storage systems.
  - It also allows swap-splitting and swap-resyncing operations of TrueCopy pairs for direct connection on
    Hitachi VSP storage systems.
  - It supports various TrueCopy pairs operations based on the specified task level.
  - This module is supported for both direct and gateway connection types.
  - swap_split and swap_resync are supported for direct connection type only.
  - For direct connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/truecopy.yml)
  - For gateway connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/truecopy.yml)
version_added: '3.1.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
options:
  state:
    description:
      - The level of the TrueCopy pairs task. Choices are 'present', 'absent', 'resize', 'resync', 'split', 'swap-split', 'swap-resync'.
    type: str
    required: false
    choices: ['present', 'absent', 'resize', 'resync', 'split', 'swap_split', 'swap_resync']
    default: 'present'
  storage_system_info:
    description:
      - Information about the Hitachi storage system.
    type: dict
    required: false
    suboptions:
      serial:
        description:
          - Serial number of the Hitachi storage system.
        type: str
        required: false
  secondary_connection_info:
    description:
      - Information required to establish a connection to the secondary storage system. Required for direct connection only. Not needed for gateway connection.
    required: false
    type: dict
    suboptions:
      address:
        description:
          - IP address or hostname of either the UAI gateway or Hitachi storage system.
        type: str
        required: true
      username:
        description:
          - Username for authentication.
        type: str
        required: false
      password:
        description:
          - Password for authentication.
        type: str
        required: false
      api_token:
        description: Value of the lock token to operate on locked resources.
        type: str
        required: false
  connection_info:
    description:
      - Information required to establish a connection to the storage system.
    required: true
    type: dict
    suboptions:
      address:
        description: IP address or hostname of either the UAI gateway or Hitachi storage system.
        type: str
        required: true
      username:
        description:
          - Username for authentication. Required for direct connection. Not needed for gateway connection as it uses API token.
        type: str
        required: false
      password:
        description:
          - Password for authentication. Required for direct connection. Not needed for gateway connection as it uses API token.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system. Two types of connections are supported, 'direct' and 'gateway'.
        type: str
        required: false
        choices: ['direct', 'gateway']
        default: 'direct'
      subscriber_id:
        description: >
          Subscriber ID is required for gateway connection type to support multi-tenancy. Not needed for direct connection or
          for gateway connection with single tenant.
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway for gateway connection. Value of the lock token to operate on locked resources for direct connection.
        type: str
        required: false
  spec:
    description: Specification for the TrueCopy pairs task.
    type: dict
    required: false
    suboptions:
      copy_group_name:
        description: >
          Name of the copy group. This field is used only for direct connection. This is a required field for create operation.
          For other operations, this field is optional, but when provided, the time to complete the operation is faster.
        type: str
        required: false
      copy_pair_name:
        description: >
          Name of the copy pair. This field is used only for direct connection. This is a required field for create operation.
          For other operations, this field is optional, but when provided, the time to complete the operation is faster.
        type: str
        required: false
      remote_device_group_name:
        description: Name of the remote device group. This field is used only for direct connection. This is an optional field.
        type: str
        required: false
      local_device_group_name:
        description: Name of the local device group. This field is used only for direct connection. This is an optional field.
        type: str
        required: false
      primary_volume_id:
        description:
          - Primary volume ID. This is a required field for create operation for both direct and gateway connections.
        type: int
        required: false
      consistency_group_id:
        description:
          - Consistency Group ID, 0 to 255. This is an optional field for both direct and gateway connections.
        type: int
        required: false
      fence_level:
        description:
          - Specifies the primary volume fence level setting and determines if the host is denied access or continues to access
            the primary volume when the pair is suspended because of an error. This is an optional field for both direct and gateway connections.
        type: str
        required: false
        choices: ['NEVER', 'DATA', 'STATUS']
        default: 'NEVER'
      allocate_new_consistency_group:
        description: >
          Allocate and assign a new consistency group ID, cannot be true if consistency_group_id is specified.
          This is used only for gateway connection and is an optional field.
        type: bool
        required: false
        default: false
      secondary_storage_serial_number:
        description:
          - Secondary storage serial number. This is used only for gateway connection and required for create.
        type: int
        required: false
      secondary_pool_id:
        description:
          - ID of the dynamic pool where the secondary volume will be created. This is required for create operation for both direct and gateway connections.
        type: int
        required: false
      copy_pace:
        description: Copy speed.
        type: str
        required: false
      is_svol_readwriteable:
        description: It is applicable for split pair operation only. If true, the secondary volume will be read-writeable after split.
        type: bool
        required: false
        default: false
      secondary_hostgroup:
        description:
          - Host group details of the secondary volume.
        type: dict
        required: false
        suboptions:
          name:
            description:
              - Name of the host group on the secondary storage system. This is required for create operation for both direct and gateway connections.
            type: str
            required: true
          port:
            description:
              - Port of the host group on the secondary storage system. This is required for create operation for both direct and gateway connections.
            type: str
            required: true
      do_initial_copy:
        description:
          - Perform initial copy. This is used only for direct connection and is an optional field during create operation.
        type: bool
        required: false
        default: true
      is_data_reduction_force_copy:
        description:
          - Force copy for data reduction. This is used for both direct and gateway connections and is an optional field during create operation.
        type: bool
        required: false
        default: false
      is_new_group_creation:
        description:
          - Create a new copy group. This is used only for direct connection and is an optional field during create operation.
        type: bool
        required: false
        default: false
      path_group_id:
        description: >
          This is used only for direct connection and is an optional field during create operation.
          Specify the path group ID in the range from 0 to 255. If you are unsure don't use this parameter.
          If you omit this value or specify 0, the lowest path group ID in the specified path group is used.
        type: int
        required: false
      new_volume_size:
        description:
          - Required only for resize operation for both direct and gateway connections. Value should be grater than the current volume size.
        type: str
        required: false
      secondary_volume_id:
        description: Secondary volume id.
        type: int
        required: false
      is_consistency_group:
        description: >
          This is used only for direct connection and is an optional field during create operation.
          Depending on the value, this attribute specifies whether to register the new pair in a consistency group.
          If true, the new pair is registered in a consistency group. If false, the new pair is not registered in a consistency group.
        type: bool
        required: false
        default: false
      begin_secondary_volume_id:
        description: >
          Specify beginning ldev id for Ldev range for svol. This is used only for gateway connection and is an optional field during
          create operation. If this field is specified, end_secondary_volume_id must also be specified.
          If this field is not specified, Ansible modules will try to create SVOL ID same as (or near to ) PVOL ID.
        required: false
        type: int
      end_secondary_volume_id:
        description: >
          Specify end ldev id for Ldev range for svol. This is used only for gateway connection and is an optional field during create operation.
          If this field is specified, begin_secondary_volume_id must also be specified.
          If this field is not specified, Ansible modules will try to create SVOL ID same as (or near to ) PVOL ID.
        required: false
        type: int
"""

EXAMPLES = """
- name: Create a TrueCopy pair for gateway connection
  hv_truecopy:
    state: "present"
    storage_system_info:
      serial: 123456
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: "sub123"
    spec:
      primary_volume_id: 11
      consistency_group_id: -1
      fence_level: 'NEVER'
      allocate_new_consistency_group: false
      secondary_storage_serial_number: 123456
      secondary_pool_id: 1

- name: Split a TrueCopy pair for gateway connection
  hv_truecopy:
    state: "split"
    storage_system_info:
      serial: 123456
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: "sub123"
    spec:
      primary_volume_id: 11

- name: Resync a TrueCopy pair for gateway connection
  hv_truecopy:
    state: "resync"
    storage_system_info:
      serial: 123456
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: "sub123"
    spec:
      primary_volume_id: 11

- name: Delete a TrueCopy pair for gateway connection
  hv_truecopy:
    state: "absent"
    storage_system_info:
      serial: 123456
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: "sub123"
    spec:
      primary_volume_id: 11

- name: Create a TrueCopy pair for direct connection
  hv_truecopy:
    state: "present"
    storage_system_info:
      serial: 123456
    connection_info:
      address: 172.1.1.126
      username: "admin"
      password: "secret"
    secondary_connection_info:
      address: 172.1.1.127
      username: "admin"
      password: "secret"
    spec:
      copy_group_name: "copy_group_name_1"
      copy_pair_name: "copy_pair_name_1"
      primary_volume_id: 11
      is_consistency_group: true
      fence_level: 'NEVER'
      secondary_pool_id: 1
      secondary_hostgroup:
        name: ansible_test_group
        port: CL1-A

- name: Split a TrueCopy pair for direct connection
  hv_truecopy:
    state: "split"
    storage_system_info:
      serial: 123456
    connection_info:
      address: 172.1.1.126
      username: "admin"
      password: "secret"
    secondary_connection_info:
      address: 172.1.1.127
      username: "admin"
      password: "secret"
    spec:
      copy_group_name: "copy_group_name_1"
      copy_pair_name: "copy_pair_name_1"

- name: Resync a TrueCopy pair for direct connection
  hv_truecopy:
    state: "resync"
    storage_system_info:
      serial: 123456
    connection_info:
      address: 172.1.1.126
      username: "admin"
      password: "secret"
    secondary_connection_info:
      address: 172.1.1.127
      username: "admin"
      password: "secret"
    spec:
      copy_group_name: "copy_group_name_1"
      copy_pair_name: "copy_pair_name_1"

- name: Swap-split a TrueCopy pair for direct connection
  hv_truecopy:
    state: "swap_split"
    storage_system_info:
      serial: 123456
    connection_info:
      address: 172.1.1.126
      username: "admin"
      password: "secret"
    secondary_connection_info:
      address: 172.1.1.127
      username: "admin"
      password: "secret"
    spec:
      copy_group_name: "copy_group_name_1"
      copy_pair_name: "copy_pair_name_1"

- name: Swap-resync a TrueCopy pair for direct connection
  hv_truecopy:
    state: "swap_resync"
    storage_system_info:
      serial: 123456
    connection_info:
      address: 172.1.1.126
      username: "admin"
      password: "secret"
    secondary_connection_info:
      address: 172.1.1.127
      username: "admin"
      password: "secret"
    spec:
      copy_group_name: "copy_group_name_1"
      copy_pair_name: "copy_pair_name_1"

- name: Delete a TrueCopy pair for direct connection
  hv_truecopy:
    state: "swap_resync"
    storage_system_info:
      serial: 123456
    connection_info:
      address: 172.1.1.126
      username: "admin"
      password: "secret"
    secondary_connection_info:
      address: 172.1.1.127
      username: "admin"
      password: "secret"
    spec:
      copy_group_name: "copy_group_name_1"
      copy_pair_name: "copy_pair_name_1"

- name: Increase the size of the volumes of a TrueCopy pair for direct connection
  hv_truecopy:
    state: "resize"
    storage_system_info:
      serial: 123456
    connection_info:
      address: 172.1.1.126
      username: "admin"
      password: "secret"
    secondary_connection_info:
      address: 172.1.1.127
      username: "admin"
      password: "secret"
    spec:
      copy_group_name: "copy_group_name_1"
      copy_pair_name: "copy_pair_name_1"
      new_volume_size: 4GB
"""

RETURN = """
data:
  description: Newly created TrueCopy pair object for direct connection.
  returned: success
  type: dict
  elements: dict
  sample:
        {
          "consistency_group_id": -1,
          "copy_group_name": "TC_TEST_1107",
          "copy_pair_name": "rd_copy_pair_202",
          "copy_progress_rate": -1,
          "entitlement_status": "",
          "fence_level": "NEVER",
          "partner_id": "",
          "primary_hex_volume_id": "00:02:77",
          "primary_or_secondary": "",
          "primary_volume_id": 631,
          "pvol_status": "PAIR",
          "pvol_storage_device_id": "A34000810045",
          "remote_mirror_copy_pair_id": "A34000810045,TC_TEST_1107,TC_TEST_1107P_,TC_TEST_1107S_,rd_copy_pair_202",
          "secondary_hex_volume_id": "00:00:ca",
          "secondary_volume_id": 202,
          "status": "",
          "storage_serial_number": "810050",
          "subscriber_id": "",
          "svol_access_mode": "",
          "svol_status": "PAIR",
          "svol_storage_device_id": "A34000810050"
    }
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPTrueCopyArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
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
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.message.module_msgs import (
    ModuleMessage,
)


@LogDecorator.debug_methods
class VSPSTrueCopyManager:

    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPTrueCopyArguments().true_copy()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:

            self.params_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.params_manager.connection_info
            self.storage_serial_number = self.params_manager.storage_system_info.serial
            self.spec = self.params_manager.true_cpoy_spec()
            self.state = self.params_manager.get_state()
            self.secondary_connection_info = (
                self.params_manager.get_secondary_connection_info()
            )

        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of TrueCopy operation. ===")
        data = None
        registration_message = validate_ansible_product_registration()
        self.logger.writeDebug(
            f"{self.params_manager.connection_info.connection_type} connection type"
        )
        self.logger.writeDebug("state = {}", self.state)
        try:
            data = self.true_copy_module()

        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of TrueCopy operation. ===")
            self.module.fail_json(msg=str(e))

        resp = {
            "changed": self.connection_info.changed,
            # "truecopy_info": data,
            # "msg": self.get_message(),
        }

        if data is not None and isinstance(data, list) or isinstance(data, dict):
            resp["truecopy_info"] = data

        if data is not None and isinstance(data, str):
            resp["msg"] = data
        else:
            resp["msg"] = self.get_message()

        if registration_message:
            resp["user_consent_required"] = registration_message
        self.logger.writeInfo(f"{resp}")
        self.logger.writeInfo("=== End of TrueCopy operation. ===")
        self.module.exit_json(**resp)

    def true_copy_module(self):
        reconciler = VSPTrueCopyReconciler(
            self.connection_info,
            self.storage_serial_number,
            self.state,
            self.secondary_connection_info,
        )
        if self.connection_info.connection_type.lower() == ConnectionTypes.GATEWAY:
            found = reconciler.check_storage_in_ucpsystem()
            if not found:
                raise ValueError(ModuleMessage.STORAGE_SYSTEM_ONBOARDING.value)
            oob = reconciler.is_out_of_band()
            self.logger.writeDebug(f"oob = {oob}")
            if oob is True:
                raise ValueError(ModuleMessage.OOB_NOT_SUPPORTED.value)
        return reconciler.reconcile_true_copy(self.spec)

    def get_message(self):

        if self.state == "present":
            return "TrueCopy Pair created successfully."
        elif self.state == "absent":
            return "TrueCopy Pair deleted successfully."
        elif self.state == "resize":
            return "TrueCopy Pair resized successfully."
        elif self.state == "resync":
            return "TrueCopy Pair resynced successfully."
        elif self.state == "split":
            return "TrueCopy Pair split successfully."
        elif self.state == "swap_split":
            return "TrueCopy Pair swap_split successfully."
        elif self.state == "swap_resync":
            return "TrueCopy Pair swap_resynced successfully."
        else:
            return "Unknown state provided."


def main(module=None):
    """
    :return: None
    """
    obj_store = VSPSTrueCopyManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
