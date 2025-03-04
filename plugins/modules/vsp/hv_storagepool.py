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
  - This module is supported for both C(direct) and C(gateway) connection types.
  - For C(direct) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/storagepool.yml)
  - For C(gateway) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/storagepool.yml)
version_added: '3.1.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.8
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: full
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
    description: The level of the storage pool task. Choices are C(present), C(absent) .
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
          - Username for authentication. This field is valid for C(direct) connection type only, and it is a required field.
        type: str
        required: false
      password:
        description:
          - Password for authentication. This field is valid for C(direct) connection type only, and it is a required field.
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
          - This field is valid for C(gateway) connection type only. This is an optional field and only needed to support multi-tenancy environment.
        type: str
        required: false
      api_token:
        description:
          - Token to access UAI gateway. This is a required field for C(gateway) connection type.
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
        description:
          - Whether to enable deduplication for the pool. This feature is applicable to the following models
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
          - serial: "811150"
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
          - serial: "811150"
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
          - serial: "811150"
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
          - serial: "811150"

        state: "absent"
        spec:
          name: "test_pool"
"""

RETURN = r"""
storage_pool:
  description: >
    The storage pool information.
  returned: always
  type: list
  elements: dict
  contains:
    deduplication_enabled:
      description: Indicates if deduplication is enabled.
      type: bool
      sample: false
    depletion_threshold_rate:
      description: Depletion threshold rate for the pool.
      type: int
      sample: 80
    dp_volumes:
      description: List of DP volumes in the pool.
      type: list
      elements: dict
      contains:
        logical_unit_id:
          description: Logical unit ID of the volume.
          type: int
          sample: 0
        size:
          description: Size of the volume.
          type: str
          sample: "21.00 GB"
    free_capacity:
      description: Free capacity of the pool in bytes.
      type: int
      sample: 6297747456
    free_capacity_in_units:
      description: Free capacity of the pool in human-readable units.
      type: str
      sample: "5.87 GB"
    ldev_ids:
      description: List of LDEV IDs in the pool.
      type: list
      elements: int
      sample: [1285]
    pool_id:
      description: ID of the pool.
      type: int
      sample: 48
    pool_name:
      description: Name of the pool.
      type: str
      sample: "test_pool"
    pool_type:
      description: Type of the pool.
      type: str
      sample: "HDP"
    replication_data_released_rate:
      description: Replication data released rate.
      type: int
      sample: -1
    replication_depletion_alert_rate:
      description: Replication depletion alert rate.
      type: int
      sample: -1
    replication_usage_rate:
      description: Replication usage rate.
      type: int
      sample: -1
    resource_group_id:
      description: ID of the resource group the pool belongs to.
      type: int
      sample: -1
    status:
      description: Status of the pool.
      type: str
      sample: "NORMAL"
    subscription_limit_rate:
      description: Subscription limit rate.
      type: int
      sample: -1
    subscription_rate:
      description: Subscription rate.
      type: int
      sample: 0
    subscription_warning_rate:
      description: Subscription warning rate.
      type: int
      sample: -1
    total_capacity:
      description: Total capacity of the pool in bytes.
      type: int
      sample: 6297747456
    total_capacity_in_units:
      description: Total capacity of the pool in human-readable units.
      type: str
      sample: "5.87 GB"
    utilization_rate:
      description: Utilization rate of the pool.
      type: int
      sample: 0
    virtual_volume_count:
      description: Number of virtual volumes in the pool.
      type: int
      sample: 0
    warning_threshold_rate:
      description: Warning threshold rate for the pool.
      type: int
      sample: 70
    is_encrypted:
      description: Indicates if the pool is encrypted.
      type: bool
      sample: true
    subscriber_id:
      description: Subscriber ID for multi-tenancy environments.
      type: str
      sample: "subscriber_id"
    partner_id:
      description: Partner ID associated with the pool.
      type: str
      sample: "partner_id"
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
