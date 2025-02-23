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
  - This module is supported for both direct and gateway connection types.
  - For direct connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/gad_pair_facts.yml)
  - For gateway connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/gad_pair_facts.yml)
version_added: '3.1.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
options:
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
        description: IP address or hostname of either the UAI gateway or the storage system.
        type: str
        required: true
      username:
        description: Username for authentication.This field is valid for direct connection type only, and it is a required field.
        type: str
        required: false
      password:
        description: Password for authentication.This field is valid for direct connection type only, and it is a required field.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['gateway', 'direct']
        default: 'direct'
      subscriber_id:
        description: This field is valid for gateway connection type only.This is an optional field and only needed to support multi-tenancy environment.
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway (required for authentication either 'username,password' or api_token).
        type: str
        required: false
  secondary_connection_info:
    description:
      - Information required to establish a connection to the secondary storage system.
      - This feild is required for direct connection type only.
    required: false
    type: dict
    suboptions:
      address:
        description:
          - IP address or hostname of the secondary storage.
        type: str
        required: true
      username:
        description:
          - Username for authentication. This field is required for secondary storage connection.
        type: str
        required: false
      password:
        description:
          - Password for authentication. This field is required for secondary storage connection
        type: str
        required: false
      api_token:
        description:
          - Value of the lock token to operate on locked resources. Provide this onnly when operation is on locked resources.
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
- name: Get all GAD pairs
  hv_gad_facts:
    state: "present"
    storage_system_info:
      serial: 811150
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: 811150
- name: Get GAD pairs by primary volume id
  hv_gad_facts:
    storage_system_info:
      serial: 811150
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: 811150
    spec:
      primary_volume_id: 11
"""

RETURN = """
data:
  description: GAD pairs.
  returned: success
  type: dict
  elements: dict
  sample:
    {
        "consistency_group_id": 1,
        "copy_pace_track_size": -1,
        "copy_rate": 0,
        "mirror_unit_id": 1,
        "pair_name": "",
        "primary_hex_volume_id": "00:00:01",
        "primary_v_s_m_resource_group_name": "",
        "primary_virtual_hex_volume_id": "00:00:01",
        "primary_virtual_storage_id": "",
        "primary_virtual_volume_id": -1,
        "primary_volume_id": 1,
        "primary_volume_storage_id": 811111,
        "secondary_hex_volume_id": "00:00:02",
        "secondary_v_s_m_resource_group_name": "",
        "secondary_virtual_hex_volume_id": -1,
        "secondary_virtual_storage_id": "",
        "secondary_virtual_volume_id": -1,
        "secondary_volume_id": 2,
        "secondary_volume_storage_id": 811112,
        "status": "PAIR",
        "storage_serial_number": "811111",
        "svol_access_mode": "READONLY",
        "type": "GAD"
    }
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
            self.module.exit_json(**response_dict)
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
