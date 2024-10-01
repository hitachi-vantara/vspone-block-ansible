#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


__metaclass__ = type


DOCUMENTATION = """
---
module: hv_storagepool
short_description: Create, update, delete storage pool information from Hitachi VSP storage systems.
description:
  - This module creates, updates, or deletes information about storage pools from Hitachi VSP storage systems.
version_added: '3.1.0'
requirements: []
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
    description:
      - Information required to establish a connection to the storage system.
    type: dict
    required: true
    suboptions:
      address:
        description:
          - IP address or hostname of either the UAI gateway .
        type: str
        required: true
      username:
        description:
          - Username for authentication.
        type: str
        required: false
      password:
        description:
          - Password for authentication.
        type: str
        required: false
      connection_type:
        description:
          - Type of connection to the storage system.
        type: str
        required: True
        choices: ['gateway']
      subscriber_id:
        description:
          - Subscriber ID for multi-tenancy (required for "gateway" connection type).
        type: str
        required: false
      api_token:
        description:
          - Token value to access UAI gateway (required for authentication either 'username,password' or api_token).
        type: str
        required: false

  spec:
    description:
      - Specification for the storage pool facts to be gathered.
    type: dict
    required: false
    suboptions:
      id:
        description: 
          - Pool ID.
        type: int
        required: false
      name:
        description:
          - Name of the pool.
        type: str
        required: false
      type:
        description:
          - The type of the pool. Supported types are HDT, HDP, HRT, HTI.
        type: str
        required: false
        choices:
          - HDT
          - HDP
          - HRT
          - HTI
      should_enable_deduplication:
        description:
          - Whether to enable deduplication for the pool.
        type: bool
        required: false
      depletion_threshold_rate:
        description:
          - The depletion threshold rate for the pool.
        type: int
        required: false
      warning_threshold_rate:
        description:
          - The warning threshold rate for the pool.
        type: int
        required: false
      resource_group_id:
        description:
          - The ID of the resource group the pool belongs to.
        type: int
        required: false
      pool_volumes:
        description:
          - Details about the volumes in the pool.
        type: list
        required: false
        suboptions:
          capacity:
            description:
              - Capacity of the pool volume.
            type: str
            required: false
          parity_group_id:
            description:
              - ID of the parity group to which the volume belongs.
            type: str
            required: false

"""

EXAMPLES = """
- name: Create Storage Pool
  tasks:
    - hv_storagepool:
        connection_info:
          address: storage1.company.com
          api_token: "api_token"
          connection_type: "gateway"
        storage_system_info:
          - serial: "123456"
        state: "present"
        spec:
          name: "test_pool"
          type: "HDP"
          should_enable_deduplication: true
          depletion_threshold_rate: 80
          warning_threshold_rate: 70
          resource_group_id: 0
          pool_volumes:
            - capacity: "21.00 GB"
              parity_group_id: "1-2"

- name: Expand Storage Pool
  tasks:
    - hv_storagepool:
        connection_info:
          address: storage1.company.com
          api_token: "api_token"
          connection_type: "gateway"

        storage_system_info:
          - serial: "123456"
        state: "present"
        spec:
          name: "test_pool"
        
          pool_volumes:
            - capacity: "21.00 GB"
              parity_group_id: "1-5"
            - capacity: "21.00 GB"
              parity_group_id: "1-3"

- name: Delete Storage Pool
  tasks:
    - hv_storagepool:
        connection_info:
          address: storage1.company.com
          api_token: "api_token"
          connection_type: "gateway"

        storage_system_info:
          - serial: "123456"

        state: "absent"
        spec:
          name: "test_pool"



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
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)


class VspStoragePoolManager:

    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPStoragePoolArguments().storage_pool()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.storage_pool_spec()
            self.serial = self.params_manager.get_serial()
            self.state = self.params_manager.get_state()
            self.connection_info = self.params_manager.get_connection_info()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        try:
            response = vsp_storage_pool.VSPStoragePoolReconciler(
                self.connection_info, self.serial
            ).storage_pool_reconcile(self.state, self.spec)

            msg = response if isinstance(response, str) else "Storage pool created/updated successfully."
            result = response if not isinstance(response, str) else None
            response_dict = {
                "changed": self.connection_info.changed,
                "data": result,
                "msg": msg,
            }
            self.module.exit_json(**response_dict)
        except Exception as ex:
            self.logger.writeException(ex)
            self.module.fail_json(msg=str(ex))


def main():
    obj_store = VspStoragePoolManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
