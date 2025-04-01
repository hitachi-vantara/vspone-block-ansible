#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_gad_facts
short_description: Retrieves GAD pairs information from Hitachi VSP storage systems.
description:
  - This module allows to fetch GAD pairs on Hitachi VSP storage systems.
  - This module is supported for both C(direct) and C(gateway) connection types.
  - For C(direct) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/gad_pair_facts.yml)
  - For C(gateway) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/gad_pair_facts.yml)
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
        description: IP address or hostname of either the UAI gateway or the storage system.
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
        description: Token value to access UAI gateway.
        type: str
        required: false
  secondary_connection_info:
    description:
      - Information required to establish a connection to the secondary storage system.
      - This feild is required for C(direct) connection type only.
    required: false
    type: dict
    suboptions:
      address:
        description: IP address or hostname of the secondary storage.
        type: str
        required: true
      username:
        description: Username for authentication. This field is required for secondary storage connection.
        type: str
        required: false
      password:
        description: Password for authentication. This field is required for secondary storage connection
        type: str
        required: false
      api_token:
        description: Value of the lock token to operate on locked resources. Provide this only when operation is on locked resources.
        type: str
        required: false
  spec:
    description: Specification for the GAD pairs task.
    type: dict
    required: true
    suboptions:
      primary_volume_id:
        description: Primary Volume Id.
        type: int
        required: false
      copy_group_name:
          description: Copy Group Name.
          type: str
          required: False
      secondary_storage_serial_number:
          description: Secondary Storage Serial Number.
          type: int
          required: False
      secondary_volume_id:
          description: Secondary Volume Id.
          type: int
          required: False
      copy_pair_name:
          description: Copy Pair Name.
          type: str
          required: False
      local_device_group_name:
          description: Local Device Group Name.
          type: str
          required: False
      remote_device_group_name:
          description: Remote Device Group Name.
          type: str
          required: False
"""

EXAMPLES = """
- name: Get all GAD pairs for gateway connection type
  hitachivantara.vspone_block.vsp.hv_gad_facts:
    state: "present"
    storage_system_info:
      serial: 811150
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: 811150

- name: Get GAD pairs by primary volume id for gateway connection type
  hitachivantara.vspone_block.vsp.hv_gad_facts:
    storage_system_info:
      serial: 811150
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: 123456

- name: Get all GAD pairs  for direct connection type
  hitachivantara.vspone_block.vsp.hv_gad_facts:
    connection_info:
      address: storage1.company.com
      username: "username"
      password: "password"
      connection_type: "direct"
    secondary_connection_info:
      address: storage2.company.com
      username: "admin"
      password: "secret"

- name: Get GAD pairs by primary volume id for gateway connection type
  hitachivantara.vspone_block.vsp.hv_gad_facts:
    storage_system_info:
      serial: 811150
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: 123456
    spec:
      primary_volume_id: 11
"""

RETURN = """
ansible_facts:
  description: >
    Dictionary containing the discovered properties of the GAD pairs.
  returned: success
  type: dict
  contains:
    gad_pairs:
      description: List of GAD pairs with their attributes.
      type: list
      elements: dict
      contains:
        consistency_group_id:
          description: Consistency group ID.
          type: int
          sample: 1
        copy_pace_track_size:
          description: Copy pace track size.
          type: int
          sample: -1
        copy_rate:
          description: Copy rate.
          type: int
          sample: 0
        mirror_unit_id:
          description: Mirror unit ID.
          type: int
          sample: 1
        pair_name:
          description: Pair name.
          type: str
          sample: ""
        primary_hex_volume_id:
          description: Primary hex volume ID.
          type: str
          sample: "00:00:01"
        primary_v_s_m_resource_group_name:
          description: Primary VSM resource group name.
          type: str
          sample: ""
        primary_virtual_hex_volume_id:
          description: Primary virtual hex volume ID.
          type: str
          sample: "00:00:01"
        primary_virtual_storage_id:
          description: Primary virtual storage ID.
          type: str
          sample: ""
        primary_virtual_volume_id:
          description: Primary virtual volume ID.
          type: int
          sample: -1
        primary_volume_id:
          description: Primary volume ID.
          type: int
          sample: 1
        primary_volume_storage_id:
          description: Primary volume storage ID.
          type: int
          sample: 811111
        secondary_hex_volume_id:
          description: Secondary hex volume ID.
          type: str
          sample: "00:00:02"
        secondary_v_s_m_resource_group_name:
          description: Secondary VSM resource group name.
          type: str
          sample: ""
        secondary_virtual_hex_volume_id:
          description: Secondary virtual hex volume ID.
          type: int
          sample: -1
        secondary_virtual_storage_id:
          description: Secondary virtual storage ID.
          type: str
          sample: ""
        secondary_virtual_volume_id:
          description: Secondary virtual volume ID.
          type: int
          sample: -1
        secondary_volume_id:
          description: Secondary volume ID.
          type: int
          sample: 2
        secondary_volume_storage_id:
          description: Secondary volume storage ID.
          type: int
          sample: 811112
        status:
          description: Status of the GAD pair.
          type: str
          sample: "PAIR"
        storage_serial_number:
          description: Storage serial number.
          type: str
          sample: "811111"
        svol_access_mode:
          description: Secondary volume access mode.
          type: str
          sample: "READONLY"
        type:
          description: Type of GAD pair.
          type: str
          sample: "GAD"
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
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.message.module_msgs import (
    ModuleMessage,
)


class VSPGADPairManagerFact:

    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPGADArguments().gad_pair_fact_args()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.gad_pair_fact_spec()
            self.serial = self.params_manager.get_serial()
            self.connection_info = self.params_manager.get_connection_info()
            self.secondary_connection_info = (
                self.params_manager.get_secondary_connection_info()
            )

            # sng20241115 for the remote_connection_manager
            self.spec.secondary_connection_info = self.secondary_connection_info
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of GAD Facts ===")
        registration_message = validate_ansible_product_registration()
        try:
            reconciler = vsp_gad_pair.VSPGadPairReconciler(
                self.connection_info, self.secondary_connection_info, self.serial
            )
            if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
                self.validate_gw_ops(reconciler)
            response = reconciler.gad_pair_facts(self.spec)

            result = response if not isinstance(response, str) else None
            response_dict = {
                "gad_pair": result,
            }
            if registration_message:
                response_dict["user_consent_required"] = registration_message
            self.logger.writeInfo(f"{response_dict}")
            self.logger.writeInfo("=== End of GAD Facts ===")
            self.module.exit_json(changed=False, ansible_facts=response_dict)
        except Exception as ex:
            self.logger.writeException(ex)
            self.logger.writeInfo("=== End of GAD Facts ===")
            self.module.fail_json(msg=str(ex))

    def validate_gw_ops(self, reconciler):
        oob = reconciler.is_out_of_band()
        if oob is True:
            raise ValueError(ModuleMessage.OOB_NOT_SUPPORTED.value)
        return


def main(module=None):
    obj_store = VSPGADPairManagerFact()
    obj_store.apply()


if __name__ == "__main__":
    main()
