#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_hur_facts
short_description: Retrieves HUR information from Hitachi VSP storage systems.
description:
  - This module retrieves information about HURs from Hitachi VSP storage systems.
  - This module is supported for both C(direct) and C(gateway) connection types.
  - For C(direct) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/hur_facts.yml)
  - For C(gateway) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/hur_facts.yml)
version_added: '3.1.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.8
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: full
options:
  storage_system_info:
    description:
      - Information about the storage system. This field is required for gateway connection type only.
    type: dict
    required: false
    suboptions:
      serial:
        description: The serial number of the storage system.
        type: str
        required: false
  connection_info:
    description: Information required to establish a connection to the storage system.
    type: dict
    required: true
    suboptions:
      address:
        description: IP address or hostname of either the UAI gateway (if connection_type is C(gateway)) or
          the storage system (if connection_type is C(direct)).
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
      api_token:
        description: API token for authentication. This field is valid for C(gateway) connection type only, and it is a required field.
        type: str
        required: false
      subscriber_id:
        description: This field is valid for C(gateway) connection type only. This is an optional field and only needed to support multi-tenancy environment.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['gateway', 'direct']
        default: 'direct'
  secondary_connection_info:
    description: Information required to establish a connection to the secondary storage system.
      This field is required for direct connection type only.
    required: false
    type: dict
    suboptions:
      address:
        description: IP address or hostname of either the UAI gateway .
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
  spec:
    description: Specification for the HUR facts to be gathered.
    type: dict
    required: false
    suboptions:
      primary_volume_id:
        description: The primary volume identifier. If not provided, it will be omitted.
        type: int
        required: false
      secondary_volume_id:
        description: The secondary volume identifier. If not provided, it will be omitted.
        type: int
        required: false
      mirror_unit_id:
        description: The mirror unit identifier. If not provided, it will be omitted.
        type: int
        required: false
        choices: [0, 1, 2, 3]
      copy_group_name:
        description: The copy group name. If not provided, it will be omitted.
        type: str
        required: false
      secondary_storage_serial_number:
        description: The secondary storage serial number. If not provided, it will be omitted.
        type: int
        required: false
      copy_pair_name:
        description: The copy pair name. If not provided, it will be omitted.
        type: str
        required: false
      local_device_group_name:
        description: The local device group name. If not provided, it will be omitted.
        type: str
        required: false
      remote_device_group_name:
        description: The remote device group name. If not provided, it will be omitted.
        type: str
        required: false
"""

EXAMPLES = """
- name: Get all HUR pairs for direct connection type
  hv_truecopy_facts:
    connection_info:
      address: gateway.company.com
      username: "admin"
      password: "password"
    secondary_connection_info:
      address: storage2.company.com
      username: "admin"
      password: "secret"

- name: Get all HUR pairs for gateway connection for a specific subscriber for gateway connection type
  hv_truecopy_facts:
    storage_system_info:
      serial: "811150"
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: 123456

- name: Gather HUR facts with primary volume and mirror unit ID for direct connection type
  hitachivantara.vspone_block.vsp.hv_hur_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    secondary_connection_info:
      address: storage2.company.com
      username: "admin"
      password: "secret"
    spec:
      primary_volume_id: 111
      mirror_unit_id: 10

- name: Gather HUR facts with primary volume and mirror unit ID for gateway connection type
  hitachivantara.vspone_block.vsp.hv_hur_facts:
    storage_system_info:
      serial: "811150"
    connection_info:
      address: storage1.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: 123456
    spec:
      primary_volume_id: 111
      mirror_unit_id: 10

- name: Gather HUR facts for a specific primary volume for direct connection type
  hitachivantara.vspone_block.vsp.hv_hur_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    secondary_connection_info:
      address: storage2.company.com
      username: "admin"
      password: "secret"
    spec:
      primary_volume_id: 111

- name: Gather HUR facts for a specific primary volume for gateway connection type
  hitachivantara.vspone_block.vsp.hv_hur_facts:
    storage_system_info:
      serial: "811150"
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: 123456
    spec:
      primary_volume_id: 111

- name: Gather HUR facts for a specific secondary volume for direct connection type
  hitachivantara.vspone_block.vsp.hv_hur_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    secondary_connection_info:
      address: storage2.company.com
      username: "admin"
      password: "secret"
    spec:
      secondary_volume_id: 111

- name: Gather HUR facts for a specific secondary volume for gateway connection type
  hitachivantara.vspone_block.vsp.hv_hur_facts:
    storage_system_info:
      serial: "811150"
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: 123456
    spec:
      secondary_volume_id: 111
"""

RETURN = """
ansible_facts:
  description: >
    Dictionary containing the discovered properties of the HURs.
  returned: always
  type: dict
  contains:
    hurs:
      description: A list of HURs gathered from the storage system.
      type: list
      elements: dict
      contains:
        consistency_group_id:
          description: ID of the consistency group.
          type: int
          sample: 1
        copy_pace_track_size:
          description: Size of the copy pace track.
          type: int
          sample: -1
        copy_rate:
          description: Rate of the copy process.
          type: int
          sample: 0
        mirror_unit_id:
          description: ID of the mirror unit.
          type: int
          sample: 1
        primary_hex_volume_id:
          description: Hexadecimal ID of the primary volume.
          type: str
          sample: "00:00:01"
        primary_v_s_m_resource_group_name:
          description: Name of the primary VSM resource group.
          type: str
          sample: ""
        primary_virtual_hex_volume_id:
          description: Hexadecimal ID of the primary virtual volume.
          type: str
          sample: "00:00:01"
        primary_virtual_storage_id:
          description: ID of the primary virtual storage.
          type: str
          sample: ""
        primary_virtual_volume_id:
          description: ID of the primary virtual volume.
          type: int
          sample: -1
        primary_volume_id:
          description: ID of the primary volume.
          type: int
          sample: 1
        primary_volume_storage_id:
          description: Storage ID of the primary volume.
          type: int
          sample: 811111
        secondary_hex_volume_id:
          description: Hexadecimal ID of the secondary volume.
          type: str
          sample: "00:00:02"
        secondary_v_s_m_resource_group_name:
          description: Name of the secondary VSM resource group.
          type: str
          sample: ""
        secondary_virtual_hex_volume_id:
          description: Hexadecimal ID of the secondary virtual volume.
          type: str
          sample: -1
        secondary_virtual_storage_id:
          description: ID of the secondary virtual storage.
          type: str
          sample: ""
        secondary_virtual_volume_id:
          description: ID of the secondary virtual volume.
          type: int
          sample: -1
        secondary_volume_id:
          description: ID of the secondary volume.
          type: int
          sample: 2
        secondary_volume_storage_id:
          description: Storage ID of the secondary volume.
          type: int
          sample: 811112
        status:
          description: Status of the HUR.
          type: str
          sample: "PAIR"
        storage_serial_number:
          description: Serial number of the storage system.
          type: str
          sample: "811111"
        svol_access_mode:
          description: Access mode of the secondary volume.
          type: str
          sample: "READONLY"
        type:
          description: Type of the HUR.
          type: str
          sample: "HUR"
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
class VSPHurFactManager:

    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPHurArguments().get_hur_fact_args()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.params_manager.connection_info
            # sng20241115 for the secondary_connection_info remote_connection_manager
            self.secondary_connection_info = (
                self.params_manager.secondary_connection_info
            )
            self.storage_serial_number = self.params_manager.storage_system_info.serial
            self.spec = self.params_manager.get_hur_fact_spec()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of HUR Facts ===")
        hur_data = None
        registration_message = validate_ansible_product_registration()

        try:
            hur_data = self.get_hur_facts()
        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of HUR Facts ===")
            self.module.fail_json(msg=str(e))
        data = {
            "hurs": hur_data,
        }
        if registration_message:
            data["user_consent_required"] = registration_message

        self.logger.writeInfo(f"{data}")
        self.logger.writeInfo("=== End of HUR Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)

    def get_hur_facts(self):
        reconciler = VSPHurReconciler(
            self.connection_info, self.storage_serial_number, None
        )
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            found = reconciler.check_storage_in_ucpsystem()
            if not found:
                raise ValueError(ModuleMessage.STORAGE_SYSTEM_ONBOARDING.value)
            oob = reconciler.is_out_of_band()
            self.logger.writeDebug(f"oob = {oob}")
            if oob is True:
                raise ValueError(ModuleMessage.OOB_NOT_SUPPORTED.value)
        # sng20241115 for the remote_connection_manager
        self.spec.secondary_connection_info = self.secondary_connection_info
        result = reconciler.get_hur_facts(self.spec)
        return result


def main(module=None):
    """
    Create class instance and invoke apply
    :return: None
    """
    obj_store = VSPHurFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
