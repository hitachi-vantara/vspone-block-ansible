#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


__metaclass__ = type

DOCUMENTATION = '''
---
module: hv_iscsi_target_facts
short_description: Retrieves information about iscsi targets from Hitachi VSP storage systems.
description:
  - This module retrieves information about iscsi targets from Hitachi VSP storage systems.
version_added: '3.0.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.0.0
requirements:
options:
  storage_system_info:
    description:
      - Information about the Hitachi storage system.
    suboptions:
      serial:
        description: Serial number of the Hitachi storage system.
        required: true
  connection_info:
    description: Information required to establish a connection to the storage system.
    required: true
    suboptions:
      address:
        description: IP address or hostname of either the UAI gateway (if connection_type is gateway) or the storage system (if connection_type is direct).
        type: str
        required: true
      username:
        description: Username for authentication.
        type: str
        required: false
      password:
        description: Password for authentication.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['gateway', 'direct']
        default: direct
      subscriber_id:
        description: Subscriber ID for multi-tenancy (required for "gateway" connection type).
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway (required for authentication either 'username,password' or api_token).
        type: str
        required: false
  spec:
    description: Specification for retrieving iscsi target information.
    suboptions:
      ports:
        description: List of ports of the iscsi target.
        required: false
      name:
        description: Name of the iscsi target.
        required: false
'''

EXAMPLES = '''
- name: Get all iscsi targets with direct connection
    hv_iscsi_target_facts:
    connection_info:
        connection_type: "direct"
        address: storage1.company.com
        username: "{{ ansible_vault_storage_username }}"
        password: "{{ ansible_vault_storage_secret }}"
    register: result

- name: Get iscsi targets by ports with direct connection
    hv_iscsi_target_facts:
    connection_info:
        connection_type: "direct"
        address: storage1.company.com
        username: "{{ ansible_vault_storage_username }}"
        password: "{{ ansible_vault_storage_secret }}"
    spec:
        ports: ['CL4-C']
    register: result

- name: Get iscsi targets by ports and name with direct connection
    hv_iscsi_target_facts:
    connection_info:
        connection_type: "direct"
        address: storage1.company.com
        username: "{{ ansible_vault_storage_username }}"
        password: "{{ ansible_vault_storage_secret }}"
    spec:
        name: 'iscsi-target-server-1'
        ports: ['CL4-C']
    register: result

- name: Get all iscsi targets with gateway connection
    hv_iscsi_target_facts:
    connection_info:
        connection_type: "gateway"
        address: gateway.company.com
        api_token: "{{ ansible_vault_gateway_api_token }}"
        subscriber_id: 12345
    storage_system_info:
        serial: 40014
    register: result

- name: Get iscsi targets by ports with gateway connection
    hv_iscsi_target_facts:
    connection_info:
        connection_type: "gateway"
        address: gateway.company.com
        api_token: "{{ ansible_vault_gateway_api_token }}"
        subscriber_id: 12345
    storage_system_info:
        serial: 40014
    spec:
        ports: ['CL4-C']
    register: result

- name: Get iscsi targets by ports and name with gateway connection
    hv_iscsi_target_facts:
    connection_info:
        connection_type: "gateway"
        address: gateway.company.com
        api_token: "{{ ansible_vault_gateway_api_token }}"
        subscriber_id: 12345
    storage_system_info:
        serial: 40014
    spec:
        name: 'iscsi-target-server-1'
        ports: ['CL4-C']
    register: result
'''

RETURN = '''
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
        "subscriber_id": "12345"
      }
    ]
'''

import json

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPIscsiTargetArguments,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_iscsi_target import (
    VSPIscsiTargetReconciler,
    VSPIscsiTargetCommonPropertiesExtractor,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_exceptions import (
    HiException,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPIscsiTargetArguments,
    VSPParametersManager,
)

logger = Log()


class VSPIscsiTargetFactsManager:
    def __init__(self):

        self.argument_spec = VSPIscsiTargetArguments().iscsi_target_facts()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )

        parameterManager = VSPParametersManager(self.module.params)
        self.connection_info = parameterManager.get_connection_info()
        self.spec = parameterManager.get_iscsi_target_fact_spec()
        self.serial_number = parameterManager.get_serial()

    def apply(self):
        logger = Log()
        iscsi_target_data = None
        iscsi_target_data_extracted = None

        logger.writeInfo(f"{self.connection_info.connection_type} connection type")
        try:
            vsp_reconciler = VSPIscsiTargetReconciler(
                self.connection_info, self.serial_number
            )
            iscsi_targets = vsp_reconciler.get_iscsi_targets(self.spec)
            logger.writeInfo("iscsi_targets = {}", iscsi_targets)
            output_list = iscsi_targets.data_to_list()
            logger.writeInfo("output_list = {}", output_list)
            iscsi_target_data_extracted = (
                VSPIscsiTargetCommonPropertiesExtractor().extract(output_list)
            )

        except Exception as e:
            self.module.fail_json(msg=str(e))

        self.module.exit_json(iscsi_targets=iscsi_target_data_extracted)


def main(module=None):
    obj_store = VSPIscsiTargetFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
