#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


__metaclass__ = type


DOCUMENTATION = """
---
module: hv_storagesystem_facts
short_description: This module provides information about the a specific VSP/Pegasus storage system.
description:
  - This module gathers facts about a specific storage system.
version_added: '3.0.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.0.0
requirements:
options:
  storage_system_info:
    description:
      - Information about the storage system.
    type: dict
    required: true
    suboptions:
      serial:
        description:
          - The serial number of the storage system.
        type: str
        required: true
  connection_info:
    description: Information required to establish a connection to the storage system.
    type: dict
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
        default: 'direct'
      subscriber_id:
        description: Subscriber ID for multi-tenancy (required for "gateway" connection type).
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway (required for authentication either 'username,password' or api_token).
        type: str
        required: false
  spec:
    description:
      - Specification for the storage system facts to be gathered.
    type: dict
    required: false
    suboptions:
      query:
        description:
          - Additional information to be gathered.
        type: list
        elements: str
        choices: ['pools', 'ports', 'quorumdisks', 'journalPools', 'freeLogicalUnitList']
        required: false
"""

EXAMPLES = """
- name: Get Storage System without additional information for pools, ports, quorumdisks, journalPools and freeLogicalUnitList
  tasks:
    - hv_storagesystem_facts:
        storage_system_info:
          serial: '1234567890'
        connection_info:
          address: storage1.company.com
          username: "admin"
          password: "secret"
          connection_type: "direct"
- name: Get Storage System with additional information for pools, ports, quorumdisks, journalPools and freeLogicalUnitList
  vars:
    query:
      pools
      ports
      quorumdisks
      journalPools
      freeLogicalUnitList
  tasks:
    - hv_storagesystem_facts:
        storage_system_info:
          serial: '1234567890'
        connection_info:
          address: storage1.company.com
          username: "admin"
          password: "secret"
          connection_type: "direct"
        spec:
            query: {{ query }}
"""

RETURN = """
storage_system_info:
  description: The storage system information.
  returned: always
  type: dict
  elements: dict
  sample: {
    "controller_address": "192.168.1.101",
    "device_limits": {
      "external_group_number_range": {
        "is_valid": true,
        "max_value": 255,
        "min_value": 1
      },
      "external_group_sub_number_range": {
        "is_valid": true,
        "max_value": 255,
        "min_value": 1
      },
      "parity_group_number_range": {
        "is_valid": true,
        "max_value": 1,
        "min_value": 1
      },
      "parity_group_sub_number_range": {
        "is_valid": true,
        "max_value": 32,
        "min_value": 1
      }
    },
    "free_capacity": "15.92 TB",
    "free_capacity_in_mb": 16696806,
    "free_gad_consistency_group_id": -1,
    "free_local_clone_consistency_group_id": 2,
    "free_remote_clone_consistency_group_id": 3,
    "health_description": "",
    "health_status": "Normal",
    "management_address": "192.168.1.100",
    "microcode_version": "83-05-02/00",
    "model": "VSP_5100H",
    "operational_status": "Normal",
    "resource_state": "Healthy",
    "serial_number": "1234567890",
    "syslog_config": {
      "syslog_servers": [
        {
          "id": 1,
          "syslog_server_address": "192.168.0.187",
          "syslog_server_port": 514
        }
      ],
      "detailed": true
    },
    "total_capacity": "27.62 TB",
    "total_capacity_in_mb": 28958728,
    "storage_pools": [
      {
        "deduplication_enabled": true,
        "depletion_threshold_rate": 80,
        "dp_volumes": [
          {
            "logical_unit_id": 0,
            "size": "21.00 GB"
          },
          {
            "logical_unit_id": 3,
            "size": "21.00 GB"
          },
          {
            "logical_unit_id": 16,
            "size": "51.00 MB"
          }
        ],
        "free_capacity": 608635453440,
        "free_capacity_in_units": "566.84 GB",
        "ldev_ids": [
          1,
          2
        ],
        "name": "test_pool",
        "pool_id": 0,
        "replication_depletion_alert_rate": -1,
        "replication_usage_rate": -1,
        "resource_group_id": 0,
        "resource_id": "storagepool-jdgdff12534",
        "status": "NORMAL",
        "subscription_limit_rate": -1,
        "subscription_rate": 8469,
        "subscription_warning_rate": -1,
        "total_capacity": 648403746816,
        "total_capacity_in_unit": "603.87 GB",
        "type": "HDP",
        "utilization_rate": 6,
        "virtual_volume_count": 582,
        "warning_threshold_rate": 70
      },
      {
        "deduplication_enabled": true,
        "depletion_threshold_rate": 70,
        "dp_volumes": [
          {
            "logical_unit_id": 5,
            "size": "21.00 GB"
          }
        ],
        "free_capacity": 12771655680,
        "free_capacity_in_units": "11.89 GB",
        "ldev_ids": [
          3
        ],
        "name": "test_pool_2",
        "pool_id": 1,
        "replication_depletion_alert_rate": -1,
        "replication_usage_rate": -1,
        "resource_group_id": 0,
        "resource_id": "storagepool-kagfdfs63542",
        "status": "NORMAL",
        "subscription_limit_rate": -1,
        "subscription_rate": 867,
        "subscription_warning_rate": -1,
        "total_capacity": 12771655680,
        "total_capacity_in_unit": "11.89 GB",
        "type": "HDP",
        "utilization_rate": 6,
        "virtual_volume_count": 582,
        "warning_threshold_rate": 70
      }
    ]
  }
"""

try:
    from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_messages import (
        MessageID,
    )

    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_exceptions import (
    HiException,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_infra import (
    StorageSystem,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_infra import (
    StorageSystemManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPStorageSystemArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_storage_system,
)
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_storagesystem_facts_runner as runner
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.model.vsp_storage_system_models import (
    StorageSystemFactSpec,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    camel_dict_to_snake_case,
)
from dataclasses import asdict

logger = Log()


class VspStorageSystemFactManager:
    def __init__(self):
        self.argument_spec = VSPStorageSystemArguments().storage_system_fact()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.set_storage_system_fact_spec()
        except Exception as e:
            self.module.fail_json(msg=str(e))

    def apply(self):
        storage_system_data = None
        try:
            if (
                self.params_manager.connection_info.connection_type.lower()
                == ConnectionTypes.GATEWAY
            ):
                storage_system_data = self.gateway_storage_system_read()
            else:
                storage_system_data = asdict(self.direct_storage_system_read())

            # FIXME - gateway has these option
            # logger.writeDebug('150 storage_system_data={}', storage_system_data['StoragePools'])
            # logger.writeDebug('150 storage_system_data={}', storage_system_data['Ports'])
            # logger.writeDebug('150 storage_system_data={}', storage_system_data['QuorumDisks'])
            # logger.writeDebug('150 storage_system_data={}', storage_system_data['JournalPools'])
            if storage_system_data.get("StoragePools"):
                storage_system_data["storage_pools"] = storage_system_data[
                    "StoragePools"
                ]
            if storage_system_data.get("Ports"):
                storage_system_data["ports"] = storage_system_data["Ports"]
            if storage_system_data.get("QuorumDisks"):
                storage_system_data["quorum_disks"] = storage_system_data["QuorumDisks"]
            if storage_system_data.get("JournalPools"):
                storage_system_data["journal_pools"] = storage_system_data[
                    "JournalPools"
                ]
            storage_system_data_extracted = (
                vsp_storage_system.VSPStorageSystemCommonPropertiesExtractor().extract(
                    storage_system_data
                )
            )
            snake_case_storage_system_data = camel_dict_to_snake_case(
                storage_system_data_extracted
            )

        except Exception as e:
            self.module.fail_json(msg=str(e))

        self.module.exit_json(storageSystem=snake_case_storage_system_data)

    def direct_storage_system_read(self):
        result = vsp_storage_system.VSPStorageSystemReconciler(
            self.params_manager.connection_info,
            self.params_manager.storage_system_info.serial,
        ).get_storage_system(self.spec)
        if result is None:
            self.module.fail_json("Couldn't read storage system.")
        return result

    def gateway_storage_system_read(self):
        try:
            self.module.params["spec"] = self.module.params.get("spec")
            return runner.runPlaybook(self.module)
        except HiException as ex:
            if HAS_MESSAGE_ID:
                logger.writeAMException(MessageID.ERR_AddRAIDStorageDevice)
            else:
                logger.writeAMException("0x0000")
            self.module.fail_json(msg=ex.format())
        except Exception as ex:
            # sng,a2.4 - there is no ex.message?
            # if ex is None or ex.message is None:
            if ex is None:
                msg = "Failed during get storage facts, please check input parameters."
            else:
                msg = str(ex)
            self.module.fail_json(msg=msg)


def main(module=None):
    obj_store = VspStorageSystemFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
