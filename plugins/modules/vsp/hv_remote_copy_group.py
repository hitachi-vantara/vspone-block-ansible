#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_remote_copy_group
short_description: Manages Remote Copy Group on Hitachi VSP storage systems.
description: >
  - This module allows for the splitting, swap-splitting, re-syncing, swap-resyncing and deletion of Remote Copy Group on Hitachi VSP storage systems.
  - It supports various remote copy pairs operations based on the specified task level.
  - The module supports the following replication types: HUR, TC, GAD.
  - This module is supported only for direct connection type.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/remote_copy_group.yml)
version_added: '3.2.0'
author:
  - Hitachi Vantara, LTD. (@hitachi-vantara)
options:
  state:
    description: The level of the Remote Copy Group pairs task. Choices are 'present', 'absent', 'split', 'resync', 'swap_split', 'swap-resync'.
    type: str
    required: false
    choices: ['present', 'absent', 'split', 'resync', 'swap_split', 'swap_resync']
    default: 'present'
  storage_system_info:
    description: Information about the Hitachi storage system.
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
        description: IP address or hostname of the Hitachi storage system .
        type: str
        required: true
      username:
        description: Username for authentication. This field is valid for direct connection type only, and it is a required field.
        type: str
        required: false
      password:
        description: Password for authentication. This field is valid for direct connection type only, and it is a required field.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['direct', 'gateway']
        default: 'direct'
      api_token:
        description: Value of the lock token to operate on locked resources.
        type: str
        required: false
      subscriber_id:
        description: >
          Subscriber ID is required for gateway connection type to support multi-tenancy. Not needed for direct connection or
          for gateway connection with single tenant. Not needed for this operation.
        type: str
        required: false
  secondary_connection_info:
    description:
      - Information required to establish a connection to the secondary storage system. Required for direct connection only.
    required: true
    type: dict
    suboptions:
      address:
        description:
          - IP address or hostname of the UAI gateway.
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
  spec:
    description: Specification for the Remote Copy Group task.
    type: dict
    required: true
    suboptions:
      copy_group_name:
        description: Copy group name, required for all operations.
        type: str
        required: true
      replication_type:
        description: Replication type, either hur, tc or gad.
        type: str
        required: false
        choices: ['UR', 'TC', 'GAD']
      is_svol_writable:
        description: is svol writable.
        type: bool
        required: false
      do_pvol_write_protect:
        description: do pvol write protect.
        type: bool
        required: false
      do_data_suspend:
        description: do data suspend.
        type: bool
        required: false
      local_device_group_name:
        description: local device group name.
        type: str
        required: false
      svol_operation_mode:
        description: svol operation mode.
        type: str
        required: false
      remote_device_group_name:
        description: remote device group name.
        type: str
        required: false
      is_consistency_group:
        description: whether is consistency group.
        type: bool
        required: false
      consistency_group_id:
        description: consistency group id.
        type: int
        required: false
      fence_level:
        description:
          - Specifies the primary volume fence level setting and determines if the host is denied access or continues to access
            the primary volume when the pair is suspended because of an error.
        type: str
        required: false
        choices: ['NEVER', 'DATA', 'STATUS']
      copy_pace:
        description: copy pace.
        type: int
        required: false
      do_failback:
        description: >
          Specify whether to perform a failback if a failure occurs in a 3DC cascade configuration.
          If set to true, the failback is performed. If set to false, the failback is not performed.
          If the value is omitted, false is assumed.
        type: bool
        required: false
        default: false
      failback_mirror_unit_number:
        description: >
          Specify the MU (mirror unit) number of the volume to be failed back.
          You can specify this attribute only if the do_failback attribute is set to true.
        type: int
        required: false
"""

EXAMPLES = """
- name: Split remote copy group for HUR
  hv_remote_copy_group:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"
    state: split
    spec:
      local_device_group_name: remote_copy_group_local_device_group_name_1
      remote_device_group_name: remote_copy_group_remote_device_group_name_1
      copy_group_name: remote_copy_group_copy_group_name_1
      replication_type: hur
      is_svol_writable: false
      do_data_suspend: false

- name: Resync remote copy group for HUR
  hv_remote_copy_group:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"
    state: resync
    spec:
      local_device_group_name: remote_copy_group_local_device_group_name_1
      remote_device_group_name: remote_copy_group_remote_device_group_name_1
      copy_group_name: remote_copy_group_copy_group_name_1
      replication_type: hur

- name: Swap split remote copy group for HUR
  hv_remote_copy_group:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"
    state: swap_split
    spec:
      local_device_group_name: remote_copy_group_local_device_group_name_1
      remote_device_group_name: remote_copy_group_remote_device_group_name_1
      copy_group_name: remote_copy_group_copy_group_name_1
      replication_type: hur

- name: Swap resync remote copy group for HUR
  hv_remote_copy_group:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"
    state: swap_resync
    spec:
      local_device_group_name: remote_copy_group_local_device_group_name_1
      remote_device_group_name: remote_copy_group_remote_device_group_name_1
      copy_group_name: remote_copy_group_copy_group_name_1
      replication_type: hur

- name: Delete remote copy group for HUR
  hv_remote_copy_group:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"
    state: absent
    spec:
      copy_group_name: remote_copy_group_copy_group_name_1

- name: Split remote copy group for TrueCopy
  hv_remote_copy_group:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"
    state: split
    spec:
      local_device_group_name: remote_copy_group_local_device_group_name_1
      remote_device_group_name: remote_copy_group_remote_device_group_name_1
      copy_group_name: remote_copy_group_copy_group_name_1
      replication_type: TC
      is_svol_writable: false
      do_pvol_write_protect: false

- name: Resync remote copy group for TrueCopy
  hv_remote_copy_group:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"
    state: resync
    spec:
      local_device_group_name: remote_copy_group_local_device_group_name_1
      remote_device_group_name: remote_copy_group_remote_device_group_name_1
      copy_group_name: remote_copy_group_copy_group_name_1
      replication_type: TC
      is_consistency_group: true
      consistency_group_id: 47
      fence_level: NEVER
      copy_pace: 3

- name: Swap split remote copy group for TrueCopy
  hv_remote_copy_group:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"
    state: swap_split
    spec:
      local_device_group_name: remote_copy_group_local_device_group_name_1
      remote_device_group_name: remote_copy_group_remote_device_group_name_1
      copy_group_name: remote_copy_group_copy_group_name_1
      replication_type: TC

- name: Swap resync remote copy group for TrueCopy
  hv_remote_copy_group:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"
    state: swap_resync
    spec:
      local_device_group_name: remote_copy_group_local_device_group_name_1
      remote_device_group_name: remote_copy_group_remote_device_group_name_1
      copy_group_name: remote_copy_group_copy_group_name_1
      replication_type: TC

- name: Delete remote copy group for TrueCopy
  hv_remote_copy_group:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"
    state: absent
    spec:
      copy_group_name: remote_copy_group_copy_group_name_1

- name: Split remote copy group for GAD
  hv_remote_copy_group:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"
    state: split
    spec:
      local_device_group_name: remote_copy_group_local_device_group_name_1
      remote_device_group_name: remote_copy_group_remote_device_group_name_1
      copy_group_name: remote_copy_group_copy_group_name_1
      replication_type: GAD

- name: Resync remote copy group for GAD
  hv_remote_copy_group:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"
    state: resync
    spec:
      local_device_group_name: remote_copy_group_local_device_group_name_1
      remote_device_group_name: remote_copy_group_remote_device_group_name_1
      copy_group_name: remote_copy_group_copy_group_name_1
      replication_type: GAD
      is_consistency_group: true
      consistency_group_id: 47

- name: Swap split remote copy group for GAD
  hv_remote_copy_group:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"
    state: swap_split
    spec:
      local_device_group_name: remote_copy_group_local_device_group_name_1
      remote_device_group_name: remote_copy_group_remote_device_group_name_1
      copy_group_name: remote_copy_group_copy_group_name_1
      replication_type: GAD

- name: Swap resync remote copy group for GAD
  hv_remote_copy_group:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"
    state: swap_resync
    spec:
      local_device_group_name: remote_copy_group_local_device_group_name_1
      remote_device_group_name: remote_copy_group_remote_device_group_name_1
      copy_group_name: remote_copy_group_copy_group_name_1
      replication_type: GAD

- name: Delete remote copy group for GAD
  hv_remote_copy_group:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"
    state: absent
    spec:
      copy_group_name: remote_copy_group_copy_group_name_1
"""

RETURN = """
data:
  description: Newly created remote copy group object.
  returned: success
  type: dict
  elements: dict
  sample:
    {
      "copy_group_name": "copygroupname001",
      "copy_pairs": [
          {
              "consistency_group_id": 51,
              "copy_group_name": "copygroupname001",
              "copy_pair_name": "copypairname00190",
              "fence_level": "ASYNC",
              "pvol_difference_data_management": "S",
              "pvol_i_o_mode": null,
              "pvol_journal_id": 37,
              "pvol_ldev_id": 1872,
              "pvol_processing_status": "N",
              "pvol_status": "PSUS",
              "pvol_storage_device_id": "900000040014",
              "quorum_disk_id": null,
              "remote_mirror_copy_pair_id": "900000040015,copygroupname001,copygroupname001P_,copygroupname001S_,copypairname00190",
              "replication_type": "UR",
              "svol_difference_data_management": "S",
              "svol_i_o_mode": null,
              "svol_journal_id": 40,
              "svol_ldev_id": 2180,
              "svol_processing_status": "N",
              "svol_status": "SSUS",
              "svol_storage_device_id": "900000040015"
          },
          {
              "consistency_group_id": 51,
              "copy_group_name": "copygroupname001",
              "copy_pair_name": "copypairname00191",
              "fence_level": "ASYNC",
              "pvol_difference_data_management": "S",
              "pvol_i_o_mode": null,
              "pvol_journal_id": 37,
              "pvol_ldev_id": 1964,
              "pvol_processing_status": "N",
              "pvol_status": "PSUS",
              "pvol_storage_device_id": "900000040014",
              "quorum_disk_id": null,
              "remote_mirror_copy_pair_id": "900000040015,copygroupname001,copygroupname001P_,copygroupname001S_,copypairname00191",
              "replication_type": "UR",
              "svol_difference_data_management": "S",
              "svol_i_o_mode": null,
              "svol_journal_id": 40,
              "svol_ldev_id": 2182,
              "svol_processing_status": "N",
              "svol_status": "SSUS",
              "svol_storage_device_id": "900000040015"
          },
          {
              "consistency_group_id": 51,
              "copy_group_name": "copygroupname001",
              "copy_pair_name": "copypairname00193",
              "fence_level": "ASYNC",
              "pvol_difference_data_management": "S",
              "pvol_i_o_mode": null,
              "pvol_journal_id": 37,
              "pvol_ldev_id": 1965,
              "pvol_processing_status": "N",
              "pvol_status": "PSUS",
              "pvol_storage_device_id": "900000040014",
              "quorum_disk_id": null,
              "remote_mirror_copy_pair_id": "900000040015,copygroupname001,copygroupname001P_,copygroupname001S_,copypairname00193",
              "replication_type": "UR",
              "svol_difference_data_management": "S",
              "svol_i_o_mode": null,
              "svol_journal_id": 40,
              "svol_ldev_id": 2184,
              "svol_processing_status": "N",
              "svol_status": "SSUS",
              "svol_storage_device_id": "900000040015"
          }
      ],
      "local_device_group_name": "copygroupname001P_",
      "remote_device_group_name": "copygroupname001S_",
      "remote_mirror_copy_group_id": "900000040015,copygroupname001,copygroupname001P_,copygroupname001S_",
      "remote_storage_device_id": "900000040015"
    }
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPRemoteCopyGroupArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_copy_groups import (
    VSPCopyGroupsReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log_decorator import (
    LogDecorator,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    camel_dict_to_snake_case,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.message.module_msgs import (
    ModuleMessage,
)


@LogDecorator.debug_methods
class VSPCopyGroupManager:

    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPRemoteCopyGroupArguments().get_copy_group_args()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.module = AnsibleModule(
                argument_spec=self.argument_spec,
                supports_check_mode=True,
                # can be added mandotary , optional mandatory arguments
            )
            self.secondary_connection_info = (
                self.params_manager.get_secondary_connection_info()
            )
            self.params_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.params_manager.connection_info
            self.storage_serial_number = self.params_manager.get_serial()
            self.spec = self.params_manager.copy_group_spec()
            self.state = self.params_manager.get_state()

        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Remote Copy Group operation ===")
        registration_message = validate_ansible_product_registration()
        try:

            data = self.copy_group_module()

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of Remote Copy Group operation ===")
            self.module.fail_json(msg=str(e))

        msg = data if isinstance(data, str) else self.get_message()
        data = data if not isinstance(data, str) else {"remote_copy_group_info": {}}

        if self.state == "split":
            if self.spec.is_svol_writable is not None:
                data["is_svol_writable"] = self.spec.is_svol_writable
            if self.spec.do_data_suspend is not None:
                data["do_data_suspend"] = self.spec.do_data_suspend
            if self.spec.do_pvol_write_protect is not None:
                data["do_pvol_write_protect"] = self.spec.do_pvol_write_protect

        if self.state == "absent":
            resp = {
                "changed": self.connection_info.changed,
                "remote_copy_group_info": {},
                "msg": msg,
            }
        else:
            resp = {
                "changed": self.connection_info.changed,
                "remote_copy_group_info": data,
                "msg": msg,
            }
        if registration_message:
            resp["user_consent_required"] = registration_message

        self.logger.writeInfo(f"{resp}")
        self.logger.writeInfo("=== End of Remote Copy Group operation ===")
        self.module.exit_json(**resp)

    def copy_group_module(self):
        reconciler = VSPCopyGroupsReconciler(
            self.connection_info,
            self.storage_serial_number,
            self.state,
            self.secondary_connection_info,
        )
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            found = reconciler.check_storage_in_ucpsystem()
            if not found:
                raise ValueError(ModuleMessage.STORAGE_SYSTEM_ONBOARDING.value)

        result = reconciler.copy_group_reconcile_direct(
            self.state, self.spec, self.secondary_connection_info
        )
        result = (
            camel_dict_to_snake_case(result)
            if not isinstance(result, str) and result is not None
            else result
        )
        return result

    def get_message(self):

        if self.state == "absent":
            return "Copy Group deleted successfully."
        elif self.state == "resync":
            return "Copy Group  resynced successfully."
        elif self.state == "split":
            return "Copy Group  split successfully."
        elif self.state == "swap_split":
            return "Copy Group  swapped split successfully."
        elif self.state == "swap_resync":
            return "Copy Group  swapped resynced successfully"
        else:
            return "Unknown state provided."


def main():
    """
    :return: None
    """
    obj_store = VSPCopyGroupManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
