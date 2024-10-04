#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


__metaclass__ = type


DOCUMENTATION = """
---
module: hv_storagepool_facts
short_description: Retrieves storage pool information from Hitachi VSP storage systems.
description:
     - This module retrieves information about storage pools from Hitachi VSP storage systems.
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
      is_encrypted: true
      subscriber_id: "subscriber_id"
      partner_id: "partner_id"
"""

import json

try:
    from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_messages import (
        MessageID,
    )

    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
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


class VspStoragePoolFactManager:
    def __init__(self):
        self.logger = Log()

        self.argument_spec = VSPStoragePoolArguments().storage_pool_fact()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.get_pool_fact_spec()
            self.serial = self.params_manager.get_serial()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        try:
            result = vsp_storage_pool.VSPStoragePoolReconciler(
                self.params_manager.connection_info, self.serial
            ).storage_pool_facts(self.spec)
            if result is None:
                self.module.fail_json("Couldn't find any storage pool.")
            self.module.exit_json(storagePool=result)
        except Exception as ex:
            self.logger.writeException(ex)

            self.module.fail_json(msg=str(ex))


def main():
    obj_store = VspStoragePoolFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
