#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


__metaclass__ = type


DOCUMENTATION = """
---
module: hv_storagepool_facts
short_description: This module provides information about the  storage pool.
description:
     - This module gathers facts about storage pools from a specified storage system.
version_added: '3.0.0'
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
      - Specification for the storage pool facts to be gathered.
    type: dict
    required: false
    suboptions:
      pool_id:
        description:
          - The pool number of the specific pool to retrieve.
        type: int
        required: false
"""

EXAMPLES = """
- name: Get all pools
  tasks:
    - hv_storagepool_facts:
        connection_info:
          address: storage1.company.com
          username: "admin"
          password: "secret"
          connection_type: "direct"

- name: Get a specific pool
  tasks:
    - hv_storagepool_facts:
        connection_info:
          address: storage1.company.com
          username: "admin"
          password: "secret"
          connection_type: "direct"
        spec:
          pool_id: 0

"""

RETURN = """
storagePool:
  description: The storage pool information.
  returned: always
  type: list
  elements: dict
  sample: 
    - deduplication_enabled: false
      depletion_threshold_rate: 80
      dp_volumes: 
        - logical_unit_id: 0
          size: "21.00 GB"
        - logical_unit_id: 3
          size: "21.00 GB"
      free_capacity: 6297747456
      free_capacity_in_units: "5.87 GB"
      ldev_ids: 
        - 1285
      pool_id: 48
      pool_name: "test_pool"
      pool_type: "HDP"
      replication_data_released_rate: -1
      replication_depletion_alert_rate: -1
      replication_usage_rate: -1
      resource_group_id: -1
      status: "NORMAL"
      subscription_limit_rate: -1
      subscription_rate: 0
      subscription_warning_rate: -1
      total_capacity: 6297747456
      total_capacity_in_units: "5.87 GB"
      utilization_rate: 0
      virtual_volume_count: 0
      warning_threshold_rate: 70
"""

import json

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
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_storage_pool,
)
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_storagepool_facts_runner as runner
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPStoragePoolArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    camel_array_to_snake_case,
    camel_dict_to_snake_case,
)
from dataclasses import asdict

logger = Log()


class VspStoragePoolFactManager:
    def __init__(self):
        self.argument_spec = VSPStoragePoolArguments().storage_pool_fact()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.get_pool_fact_spec()
        except Exception as e:
            self.module.fail_json(msg=str(e))

    def apply(self):
        try:
            if (
                self.params_manager.connection_info.connection_type.lower()
                == ConnectionTypes.GATEWAY
            ):
                self.gateway_storage_pool_read()
            else:
                if self.spec.pool_id is not None:
                    storage_pool = self.direct_storage_pool_read()
                    storage_pool_dict = {}
                    if storage_pool is not None:
                        storage_pool_dict = storage_pool.to_dict()
                    storage_pool_data_extracted = vsp_storage_pool.VSPStoragePoolCommonPropertiesExtractor().extract_pool(
                        storage_pool_dict
                    )
                    snake_case_storage_pool_data = camel_dict_to_snake_case(
                        storage_pool_data_extracted
                    )
                    self.module.exit_json(storagePool=snake_case_storage_pool_data)
                else:
                    all_storage_pools = self.direct_all_storage_pools_read()
                    storage_pools_list = all_storage_pools.data_to_list()
                    storage_pools_data_extracted = vsp_storage_pool.VSPStoragePoolCommonPropertiesExtractor().extract_all_pools(
                        storage_pools_list
                    )
                    snake_case_storage_pools_data = camel_array_to_snake_case(
                        storage_pools_data_extracted
                    )
                    self.module.exit_json(storagePool=snake_case_storage_pools_data)
        except HiException as ex:
            if HAS_MESSAGE_ID:
                logger.writeAMException(MessageID.ERR_GetStoragePools)
            else:
                logger.writeAMException("0x0000")
            self.module.fail_json(msg=ex.format())
        except Exception as ex:
            self.module.fail_json(msg=str(ex))

    def direct_all_storage_pools_read(self):
        result = vsp_storage_pool.VSPStoragePoolReconciler(
            self.params_manager.connection_info
        ).get_all_storage_pools()
        if result is None:
            self.module.fail_json("Couldn't read storage pools.")
        return result

    def direct_storage_pool_read(self):
        result = vsp_storage_pool.VSPStoragePoolReconciler(
            self.params_manager.connection_info
        ).get_storage_pool(self.spec)
        if result is None:
            self.module.fail_json("Couldn't read storage pools.")
        return result

    def gateway_storage_pool_read(self):
        self.module.params["spec"] = self.module.params.get("spec")
        runner.runPlaybook(self.module)


def main(module=None):
    obj_store = VspStoragePoolFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
