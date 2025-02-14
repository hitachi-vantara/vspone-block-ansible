#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_sds_block_compute_port_authentication
short_description: Manages Hitachi SDS block storage system compute port authentication mode settings.
description:
  - This module manages compute port authentication mode settings.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/port_auth.yml)
version_added: '3.0.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
options:
  state:
    description: The level of the compute port authentication task. Choices are 'present'.
    type: str
    required: false
    choices: ['present', 'absent']
    default: 'present'
  connection_info:
    description: Information required to establish a connection to the storage system.
    required: true
    type: dict
    suboptions:
      address:
        description: IP address or hostname of the storage system.
        type: str
        required: true
      username:
        description: Username for authentication.
        type: str
        required: true
      password:
        description: Password for authentication.
        type: str
        required: true
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['direct']
        default: 'direct'
  spec:
    description: Specification for the compute port authentication task.
    type: dict
    required: true
    suboptions:
      port_name:
        description: Port name.
        type: str
        required: false
      state:
        description: The state of the port authorization task. Choices are 'add_chap_user', 'remove_chap_user'.
        type: str
        required: false
        choices: ['add_chap_user', 'remove_chap_user']
      authentication_mode:
        description: Authentication mode. Choices are 'CHAP', 'CHAP_complying_with_initiator_setting', 'None'.
        type: str
        required: false
        choices: ['CHAP', 'CHAP_complying_with_initiator_setting', 'None']
      is_discovery_chap_authentication:
        description: When true is specified, CHAP authentication at the time of discovery is enabled.
        type: bool
        required: false
      target_chap_users:
        description: List of target CHAP user name.
        type: list
        required: false
        elements: str
"""

EXAMPLES = """
- name: Set port authentication mode
  hv_sds_block_compute_port_authentication:
    state: present
    connection_info:
      address: vssb.company.com
      api_token: "api_token_value"
      connection_type: "direct"
    spec:
      port_name: "iqn.1994-04.jp.co.hitachi:rsd.sph.t.0a85a.000"
      authentication_mode: "CHAP"
      target_chap_users: ["chapuser1"]
"""

RETURN = """
data:
  description: The compute port information.
  returned: always
  type: dict
  elements: dict
  sample:
    {
      "chap_users_info": [
          {
              "id": "a083ca8f-e925-474a-b63b-d9b06b2d02ad",
              "initiator_chap_user_name": "",
              "target_chap_user_name": "RD-chap-user-1"
          },
          {
              "id": "342fac65-d0f8-4fc6-9afc-5adaddca23c5",
              "initiator_chap_user_name": "chapuser1",
              "target_chap_user_name": "newchapuser2"
          }
      ],
      "port_auth_info": {
          "auth_mode": "CHAP",
          "id": "0f13e320-53e7-4088-aa11-418636b58376",
          "is_discovery_chap_auth": false,
          "is_mutual_chap_auth": true
      },
      "port_info": {
          "configured_port_speed": "Auto",
          "fc_information": null,
          "id": "0f13e320-53e7-4088-aa11-418636b58376",
          "interface_name": "eth2",
          "iscsi_information": {
              "delayed_ack": true,
              "ip_mode": "ipv4",
              "ipv4_information": {
                  "address": "10.76.34.52",
                  "default_gateway": "10.76.34.1",
                  "subnet_mask": "255.255.255.0"
              },
              "ipv6_information": {
                  "default_gateway": "",
                  "global_address1": "",
                  "global_address_mode": "Manual",
                  "linklocal_address": "",
                  "linklocal_address_mode": "Auto",
                  "subnet_prefix_length1": 0
              },
              "is_isns_client_enabled": false,
              "isns_servers": [
                  {
                      "index": 1,
                      "port": 3205,
                      "server_name": ""
                  }
              ],
              "mac_address": "b4:96:91:c8:76:0c",
              "mtu_size": 9000
          },
          "name": "iqn.1994-04.jp.co.hitachi:rsd.sph.t.0a85a.001",
          "nickname": "001-iSCSI-001",
          "nvme_tcp_information": null,
          "port_speed": "25G",
          "port_speed_duplex": "25Gbps Full",
          "protection_domain_id": "645c36b6-da9e-44bb-b711-430e06c7ad2b",
          "protocol": "iSCSI",
          "status": "Normal",
          "status_summary": "Normal",
          "storage_node_id": "c3be292d-fe72-48c9-8780-3a0cbb5fbff6",
          "type": "Universal"
      }
  }
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    StateValue,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_port_auth import (
    SDSBPortAuthReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_properties_extractor import (
    PortDetailPropertiesExtractor,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBPortAuthArguments,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)

logger = Log()


class SDSBPortAuthManager:
    def __init__(self):

        self.argument_spec = SDSBPortAuthArguments().port_auth()
        logger.writeDebug(
            f"MOD:hv_sds_block_port_authentication:argument_spec= {self.argument_spec}"
        )
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        parameter_manager = SDSBParametersManager(self.module.params)
        self.state = parameter_manager.get_state()
        self.connection_info = parameter_manager.get_connection_info()
        # logger.writeDebug(f"MOD:hv_sds_block_chap_user_facts:argument_spec= {self.connection_info}")
        self.spec = parameter_manager.get_port_auth_spec()
        logger.writeDebug(f"MOD:hv_sds_block_port_authentication:spec= {self.spec}")

    def apply(self):
        port_auth = None
        port_auth_data_extracted = None
        registration_message = validate_ansible_product_registration()
        logger.writeInfo(f"{self.connection_info.connection_type} connection type")
        try:
            sdsb_reconciler = SDSBPortAuthReconciler(self.connection_info)
            logger.writeDebug(
                f"MOD:hv_sds_block_port_authentication:apply:spec= {self.spec}"
            )
            port_auth = sdsb_reconciler.reconcile_port_auth(self.state, self.spec)

            logger.writeDebug(
                f"MOD:hv_sds_block_port_authentication:port_auth= {port_auth}"
            )
            if self.state.lower() == StateValue.PRESENT:
                # output_dict = port_auth.data_to_list()
                output_dict = port_auth.to_dict()
                port_auth_data_extracted = PortDetailPropertiesExtractor().extract_dict(
                    output_dict
                )

        except Exception as e:
            self.module.fail_json(msg=str(e))

        response = {
            "changed": self.connection_info.changed,
            "data": port_auth_data_extracted,
        }
        if registration_message:
            response["user_consent_required"] = registration_message
        self.module.exit_json(**response)


def main(module=None):
    obj_store = SDSBPortAuthManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
