#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_storagepool_facts
short_description: Retrieves storage pool information from Hitachi VSP storage systems.
description:
  - This module retrieves information about storage pools from Hitachi VSP storage systems.
  - This module is supported for both C(direct) and C(gateway) connection types.
  - For C(direct) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/storagepool_facts.yml)
  - For C(gateway) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/storagepool_facts.yml)
version_added: '3.0.0'
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
      - Information about the storage system. This field is required for gateway connection type only.
    type: dict
    required: false
    suboptions:
      serial:
        description: The serial number of the storage system.
        type: str
        required: false
  connection_info:
    description: Information required to establish a connection to the storage system.
    type: dict
    required: true
    suboptions:
      address:
        description: IP address or hostname of either the UAI gateway (if connection_type is C(gateway)) or
          the storage system (if connection_type is C(direct)).
        type: str
        required: true
      username:
        description: Username for authentication. This field is valid for C(direct) connection type only, and it is a required field.
        type: str
        required: false
      password:
        description: Password for authentication. This field is valid for C(direct) connection type only, and it is a required field.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['gateway', 'direct']
        default: 'direct'
      subscriber_id:
        description: This field is valid for C(gateway) connection type only. This is an optional field and only needed to support multi-tenancy environment.
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway. This is a required field for C(gateway) connection type.
        type: str
        required: false
  spec:
    description: Specification for the storage pool facts to be gathered.
    type: dict
    required: false
    suboptions:
      pool_id:
        description: The pool number of the specific pool to retrieve.
        type: int
        required: false
"""

EXAMPLES = """
- name: Get all pools for direct connection type
  hitachivantara.vspone_block.vsp.hv_storagepool_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
      connection_type: "direct"

- name: Get all pools for gateway connection type
  hitachivantara.vspone_block.vsp.hv_storagepool_facts:
    storage_system_info:
      serial: "811150"
    connection_info:
      address: storage1.company.com
      api_token: "api_token"
      connection_type: "gateway"

- name: Get a specific pool for direct connection type
  hitachivantara.vspone_block.vsp.hv_storagepool_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
      connection_type: "direct"
    spec:
      pool_id: 0
"""

RETURN = r"""
ansible_facts:
  description: >
    Dictionary containing the discovered properties of the storage pools.
  returned: always
  type: dict
  contains:
    storage_pool:
      description: The storage pool information.
      type: list
      elements: dict
      contains:
        deduplication_enabled:
          description: Indicates if deduplication is enabled.
          type: bool
          sample: false
        depletion_threshold_rate:
          description: The depletion threshold rate.
          type: int
          sample: 80
        dp_volumes:
          description: List of DP volumes.
          type: list
          elements: dict
          contains:
            logical_unit_id:
              description: The logical unit ID.
              type: int
              sample: 0
            size:
              description: The size of the volume.
              type: str
              sample: "21.00 GB"
        free_capacity:
          description: The free capacity in bytes.
          type: int
          sample: 6297747456
        free_capacity_in_units:
          description: The free capacity in human-readable units.
          type: str
          sample: "5.87 GB"
        ldev_ids:
          description: List of LDEV IDs.
          type: list
          elements: int
          sample: [1285]
        pool_id:
          description: The pool ID.
          type: int
          sample: 48
        pool_name:
          description: The name of the pool.
          type: str
          sample: "test_pool"
        pool_type:
          description: The type of the pool.
          type: str
          sample: "HDP"
        replication_data_released_rate:
          description: The replication data released rate.
          type: int
          sample: -1
        replication_depletion_alert_rate:
          description: The replication depletion alert rate.
          type: int
          sample: -1
        replication_usage_rate:
          description: The replication usage rate.
          type: int
          sample: -1
        resource_group_id:
          description: The resource group ID.
          type: int
          sample: -1
        status:
          description: The status of the pool.
          type: str
          sample: "NORMAL"
        subscription_limit_rate:
          description: The subscription limit rate.
          type: int
          sample: -1
        subscription_rate:
          description: The subscription rate.
          type: int
          sample: 0
        subscription_warning_rate:
          description: The subscription warning rate.
          type: int
          sample: -1
        total_capacity:
          description: The total capacity in bytes.
          type: int
          sample: 6297747456
        total_capacity_in_units:
          description: The total capacity in human-readable units.
          type: str
          sample: "5.87 GB"
        utilization_rate:
          description: The utilization rate.
          type: int
          sample: 0
        virtual_volume_count:
          description: The count of virtual volumes.
          type: int
          sample: 0
        warning_threshold_rate:
          description: The warning threshold rate.
          type: int
          sample: 70
        is_encrypted:
          description: Indicates if the pool is encrypted.
          type: bool
          sample: true
        subscriber_id:
          description: The subscriber ID.
          type: str
          sample: "subscriber_id"
        partner_id:
          description: The partner ID.
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
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.message.module_msgs import (
    ModuleMessage,
)


class VspStoragePoolFactManager:
    def __init__(self):
        self.logger = Log()

        self.argument_spec = VSPStoragePoolArguments().storage_pool_fact()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.get_pool_fact_spec()
            self.serial = self.params_manager.get_serial()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Storage Pool Facts ===")
        registration_message = validate_ansible_product_registration()
        try:
            result = vsp_storage_pool.VSPStoragePoolReconciler(
                self.params_manager.connection_info, self.serial
            ).storage_pool_facts(self.spec)
            if result is None:
                err_msg = ModuleMessage.STORAGE_POOL_NOT_FOUND.value
                self.logger.writeError(f"{err_msg}")
                self.logger.writeInfo("=== End of Storage Pool Facts ===")
                self.module.fail_json(msg=err_msg)

            data = {
                "storage_pool": result,
            }
            if registration_message:
                data["user_consent_required"] = registration_message
            self.logger.writeInfo(f"{data}")
            self.logger.writeInfo("=== End of Storage Pool Facts ===")
            self.module.exit_json(changed=False, ansible_facts=data)
        except Exception as ex:
            self.logger.writeException(ex)
            self.logger.writeInfo("=== End of Storage Pool Facts ===")
            self.module.fail_json(msg=str(ex))


def main():
    obj_store = VspStoragePoolFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
