#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_iscsi_target_facts
short_description: Retrieves information about iscsi targets from Hitachi VSP storage systems.
description:
  - This module retrieves information about iscsi targets from Hitachi VSP storage systems.
  - This module is supported for both direct and gateway connection types.
  - For direct connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/iscsi_target_facts.yml)
  - For gateway connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/iscsi_target_facts.yml)
version_added: '3.0.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
options:
  storage_system_info:
    required: false
    type: dict
    description:
      - Information about the Hitachi storage system.
    suboptions:
      serial:
        description: Serial number of the Hitachi storage system.
        required: false
        type: str
  connection_info:
    description: Information required to establish a connection to the storage system.
    required: true
    type: dict
    suboptions:
      address:
        description: IP address or hostname of either the UAI gateway (if connection_type is gateway) or the storage system (if connection_type is direct).
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
        default: direct
      subscriber_id:
        description: This field is valid for gateway connection type only.This is an optional field and only needed to support multi-tenancy environment.
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway.This is a required field for gateway connection type.
        type: str
        required: false
  spec:
    description: Specification for retrieving iscsi target information.
    type: dict
    required: true
    suboptions:
      ports:
        description: List of ports of the iscsi target.
        required: false
        type: list
        elements: str
      name:
        description: Name of the iscsi target.
        required: false
        type: str
"""

EXAMPLES = """
- name: Get all iscsi targets with direct connection
  hv_iscsi_target_facts:
    connection_info:
      connection_type: "direct"
      address: storage1.example.com
      username: "dummy_username"
      password: "dummy_password"
  register: result

- name: Get iscsi targets by ports with direct connection
  hv_iscsi_target_facts:
    connection_info:
      connection_type: "direct"
      address: storage1.example.com
      username: "dummy_username"
      password: "dummy_password"
    spec:
      ports: ['CL4-C']
  register: result

- name: Get iscsi targets by ports and name with direct connection
  hv_iscsi_target_facts:
    connection_info:
      connection_type: "direct"
      address: storage1.example.com
      username: "dummy_username"
      password: "dummy_password"
    spec:
      name: 'iscsi-target-server-1'
      ports: ['CL4-C']
  register: result

- name: Get all iscsi targets with gateway connection
  hv_iscsi_target_facts:
    connection_info:
      connection_type: "gateway"
      address: gateway.example.com
      api_token: "dummy_api_token"
      subscriber_id: 811150
    storage_system_info:
      serial: 40014
  register: result

- name: Get iscsi targets by ports with gateway connection
  hv_iscsi_target_facts:
    connection_info:
      connection_type: "gateway"
      address: gateway.example.com
      api_token: "dummy_api_token"
      subscriber_id: 811150
    storage_system_info:
      serial: 40014
    spec:
      ports: ['CL4-C']
  register: result

- name: Get iscsi targets by ports and name with gateway connection
  hv_iscsi_target_facts:
    connection_info:
      connection_type: "gateway"
      address: gateway.example.com
      api_token: "dummy_api_token"
      subscriber_id: 811150
    storage_system_info:
      serial: 40014
    spec:
      name: 'iscsi-target-server-1'
      ports: ['CL4-C']
  register: result
"""

RETURN = """
Iscsi targets info:
  description: The iscsi targets information.
  returned: always
  type: list
  elements: dict
  sample:
    iscsi_targets: [
      {
        "auth_param": {
          "authentication_mode": "BOTH",
          "is_chap_enabled": true,
          "is_chap_required": false,
          "is_mutual_auth": false
        },
        "chap_users": [
          "chapuser1"
        ],
        "host_mode": {
          "host_mode": "VMWARE",
          "host_mode_options": [
            {
              "raid_option": "EXTENDED_COPY",
              "raid_option_number": 54
            }
          ]
        },
        "iqn": "iqn.rest.example.of.iqn.host",
        "iqn_initiators": [
          "iqn.2014-04.jp.co.hitachi:xxx.h70.i.62510.1a.ff"
        ],
        "iscsi_id": 1,
        "iscsi_name": "iscsi-name",
        "logical_units": [
          {
            "host_lun_id": 0,
            "logical_unit_id": 1
          }
        ],
        "partner_id": "partnerid",
        "port_id": "CL4-C",
        "resource_group_id": 0,
        "subscriber_id": "811150"
      }
    ]
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_iscsi_target import (
    VSPIscsiTargetReconciler,
    VSPIscsiTargetCommonPropertiesExtractor,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPIscsiTargetArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class VSPIscsiTargetFactsManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = VSPIscsiTargetArguments().iscsi_target_facts()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        parameterManager = VSPParametersManager(self.module.params)
        self.connection_info = parameterManager.get_connection_info()
        self.spec = parameterManager.get_iscsi_target_fact_spec()
        self.serial_number = parameterManager.get_serial()

    def apply(self):
        self.logger.writeInfo("=== Start of iSCSI Target Facts ===")
        iscsi_target_data_extracted = None
        registration_message = validate_ansible_product_registration()

        try:
            vsp_reconciler = VSPIscsiTargetReconciler(
                self.connection_info, self.serial_number
            )
            iscsi_targets = vsp_reconciler.get_iscsi_targets(self.spec)
            self.logger.writeDebug("iscsi_targets = {}", iscsi_targets)
            output_list = iscsi_targets.data_to_list()
            self.logger.writeDebug("output_list = {}", output_list)
            iscsi_target_data_extracted = (
                VSPIscsiTargetCommonPropertiesExtractor().extract(output_list)
            )

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of iSCSI Target Facts ===")
            self.module.fail_json(msg=str(e))
        data = {
            "iscsi_targets": iscsi_target_data_extracted,
        }
        if registration_message:
            data["user_consent_required"] = registration_message

        self.logger.writeInfo(f"{data}")
        self.logger.writeInfo("=== End of iSCSI Target Facts ===")
        self.module.exit_json(**data)


def main(module=None):
    obj_store = VSPIscsiTargetFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
