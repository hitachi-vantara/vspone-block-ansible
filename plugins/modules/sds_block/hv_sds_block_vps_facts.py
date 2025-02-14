#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_sds_block_vps_facts
short_description: Retrieves information about Virtual Private Storages (VPS) of Hitachi SDS block storage system.
description:
  - This module retrieves information about Virtual Private Storages.
  - It provides details about a Virtual Private Storages such as number of servers created, number of volumes created etc.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/vps_facts.yml)
version_added: '3.1.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
options:
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
    description: Specification for retrieving VPS information.
    type: dict
    required: false
    suboptions:
      id:
        type: str
        description: ID of the VPS to retrieve information for.
        required: false
      name:
        type: str
        description: VPS name to retrieve information for.
        required: false
"""
EXAMPLES = """
- name: Retrieve information about all VPS
  hv_sds_block_vps_facts:
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"

- name: Retrieve information about a specific VPS by ID
  hv_sds_block_vps_facts:
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"

    spec:
      id: "464e1fd1-9892-4134-866c-6964ce786676"

- name: Retrieve information about a specific VPS user by name
  hv_sds_block_vps_facts:
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"

    spec:
      name: "VPS_01"
"""

RETURN = """
vps:
  description: A list of VPS.
  returned: always
  type: list
  elements: dict
  sample:
    {
        "vsp_info":
        [
            {
                "id": "d2c1fa60-5c41-486a-9551-ec41c74d9f01",
                "name": "VPS_01",
                "number_of_hbas_created": 0,
                "number_of_servers_created": 0,
                "number_of_sessions_created": 0,
                "number_of_user_groups_created": 0,
                "number_of_users_created": 0,
                "number_of_volume_server_connections_created": 0,
                "upper_limit_for_number_of_hbas": 400,
                "upper_limit_for_number_of_servers": 100,
                "upper_limit_for_number_of_sessions": 436,
                "upper_limit_for_number_of_user_groups": 256,
                "upper_limit_for_number_of_users": 256,
                "upper_limit_for_number_of_volume_server_connections": 100,
                "volume_settings": {
                    "capacity_of_volumes_created": 0,
                    "capacity_saving_of_volume": "Compression",
                    "number_of_volumes_created": 0,
                    "pool_id": "f5ef8935-ed38-4894-a90b-f821ab6d3d89",
                    "qos_param": {
                        "upper_alert_allowable_time_of_volume": -1,
                        "upper_limit_for_iops_of_volume": -1,
                        "upper_limit_for_transfer_rate_of_volume": -1
                    },
                    "saving_mode_of_volume": "Inline",
                    "upper_limit_for_capacity_of_single_volume": -1,
                    "upper_limit_for_capacity_of_volumes": 100,
                    "upper_limit_for_number_of_volumes": 50
                }
            }
        ],
        "vsp_summary_info": {
            "total_count": 1,
            "total_upper_limit_for_capacity_of_volumes": 100,
            "total_upper_limit_for_number_of_hbas": 400,
            "total_upper_limit_for_number_of_servers": 100,
            "total_upper_limit_for_number_of_sessions": 436,
            "total_upper_limit_for_number_of_user_groups": 256,
            "total_upper_limit_for_number_of_users": 256,
            "total_upper_limit_for_number_of_volume_server_connections": 100,
            "total_upper_limit_for_number_of_volumes": 50
        }
    }
"""
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_vps import (
    SDSBVpsReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBVpsArguments,
    SDSBParametersManager,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)

logger = Log()


class SDSBVpsFactsManager:
    def __init__(self):

        self.argument_spec = SDSBVpsArguments().vps_facts()
        logger.writeDebug(
            f"MOD:hv_sds_block_vps_facts:argument_spec= {self.argument_spec}"
        )
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()
        self.spec = parameter_manager.get_vps_fact_spec()
        logger.writeDebug(f"MOD:hv_sds_block_vsp_facts:spec= {self.spec}")

    def apply(self):

        registration_message = validate_ansible_product_registration()
        logger.writeInfo(f"{self.connection_info.connection_type} connection type")
        try:
            sdsb_reconciler = SDSBVpsReconciler(self.connection_info)
            vps = sdsb_reconciler.get_vps_facts(self.spec)

            logger.writeDebug(f"MOD:hv_sds_block_vps_facts:vps= {vps}")

        except Exception as e:
            self.module.fail_json(msg=str(e))
        data = {"vsp_info": vps}

        if registration_message:
            data["user_consent_required"] = registration_message
        self.module.exit_json(**data)


def main(module=None):
    obj_store = SDSBVpsFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
