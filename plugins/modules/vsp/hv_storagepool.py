#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_storagepool
short_description: Manage storage pool information on Hitachi VSP storage systems.
description:
  - Create, update, or delete storage pool information on Hitachi VSP storage systems.
  - This module is supported for both direct and gateway connection types.
  - For direct connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/storagepool.yml)
  - For gateway connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/storagepool.yml)
version_added: '3.1.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
options:
  storage_system_info:
    description:
      - Information about the storage system.
    type: dict
    required: false
    suboptions:
      serial:
        description:
          - Serial number of the storage system.
        type: str
        required: false
  state:
    description: The level of the storage pool task. Choices are 'present', 'absent' .
    type: str
    required: false
    choices: ['present', 'absent']
    default: 'present'

  connection_info:
    description:
      - Connection details for the storage system.
    type: dict
    required: true
    suboptions:
      address:
        description:
          - IP address or hostname of the UAI gateway or storage system.
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
        required: false
        choices: ['direct', 'gateway']
        default: 'direct'
      subscriber_id:
        description:
          - This field is valid for gateway connection type only. This is an optional field and only needed to support multi-tenancy environment.
        type: str
        required: false
      api_token:
        description:
          - Token to access UAI gateway (either 'username, password' or api_token is required).
        type: str
        required: false
  spec:
    description:
      - Specification for the storage pool.
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
          - Type of the pool. Supported types are HDT, HDP, HRT, HTI.
        type: str
        required: false
        choices:
          - HDT
          - HDP
          - HRT
          - HTI
      should_enable_deduplication:
        description: >
          Whether to enable deduplication for the pool. This feature is applicable to the following models:
          - VSP G200
          - VSP G400
          - VSP F400
          - VSP G600
          - VSP F600
          - VSP G800
          - VSP F800
          - VSP G400 with NAS module
          - VSP G600 with NAS module
          - VSP G800 with NAS module
          - VSP G1000
          - VSP G1500
          - VSP F1500
          - VSP N400
          - VSP N600
          - VSP N800
        type: bool
        required: false
      depletion_threshold_rate:
        description:
          - Depletion threshold rate for the pool (not applicable for Thin Image pool).
        type: int
        required: false
      warning_threshold_rate:
        description:
          - Warning threshold rate for the pool.
        type: int
        required: false
      resource_group_id:
        description:
          - ID of the resource group the pool belongs to .
        type: int
        required: false
      pool_volumes:
        description:
          - Details about the volumes in the pool.
        type: list
        required: false
        elements: dict
        suboptions:
          capacity:
            description:
              - Capacity of the pool volume.
            type: str
            required: true
          parity_group_id:
            description:
              - ID of the parity group the volume belongs to.
            type: str
            required: true

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

- name: Create Storage Pool using  direct connection
  tasks:
    - hv_storagepool:
        connection_info:
          address: storage1.company.com
          username: "gateway"
          password: "password"
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

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_storage_pool,
)
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPStoragePoolArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class VspStoragePoolManager:

    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPStoragePoolArguments().storage_pool()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
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
            self.logger.writeInfo("=== Start of Storage Pool operation ===")
            registration_message = validate_ansible_product_registration()
            response = vsp_storage_pool.VSPStoragePoolReconciler(
                self.connection_info, self.serial
            ).storage_pool_reconcile(self.state, self.spec)

            msg = (
                response
                if isinstance(response, str)
                else "Storage pool created/updated successfully."
            )
            result = response if not isinstance(response, str) else None
            response_dict = {
                "changed": self.connection_info.changed,
                "data": result,
                "msg": msg,
            }
            if registration_message:
                response_dict["user_consent_required"] = registration_message

            self.logger.writeInfo(f"{response_dict}")
            self.logger.writeInfo("=== End of Storage Pool operation ===")
            self.module.exit_json(**response_dict)
        except Exception as ex:
            self.logger.writeException(ex)
            self.logger.writeInfo("=== End of Storage Pool operation ===")
            self.module.fail_json(msg=str(ex))


def main(module=None):
    obj_store = VspStoragePoolManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
