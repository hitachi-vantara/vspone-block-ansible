#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


__metaclass__ = type


DOCUMENTATION = '''
---
module: hv_sds_block_storage_system_fact
short_description: Retrives information about a specific Hitachi SDS block storage system.
description:
     - This module gathers facts about a specific storage system.

version_added: '3.0.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.0.0
requirements:
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
        required: true
        choices: ['direct']
        default: 'direct'

'''

EXAMPLES = '''
- name: Testing Get Storage System
  hosts: localhost
  tasks:
    - hv_sds_block_storage_system_fact:
        connection_info:
          address: vssb.company.com
          username: "admin"
          password: "secret"
          connection_type: "direct"
'''

RETURN = '''
storagesystem:
  description: The storage system information.
  returned: always
  type: dict
  elements: dict/list
  sample: {
    "efficiency_data_reduction": 100,
    "free_pool_capacity_in_mb": 9518292,
    "health_statuses": [
      {
        "protection_domain_id": "",
        "status": "Normal",
        "type": "License"
      },
      {
        "protection_domain_id": "gsfd1234-123a-wer2-f234-123456789012",
        "status": "Normal",
        "type": "Pool"
      }
    ],
    "number_of_compute_ports": 3,
    "number_of_drives": 36,
    "number_of_fault_domains": 1,
    "number_of_storage_pools": 1,
    "number_of_total_servers": 16,
    "number_of_total_storage_nodes": 0,
    "number_of_total_volumes": 14,
    "total_efficiency": 210,
    "total_pool_capacity_in_mb": 9519048,
    "used_pool_capacity_in_mb": 756
  }
'''

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
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBStorageSystemArguments,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    sdsb_storage_system,
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


class SDSBStorageSystemFactManager:
    def __init__(self):
        self.argument_spec = SDSBStorageSystemArguments().storage_system_fact()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )
        try:
            self.params_manager = SDSBParametersManager(self.module.params)
        except Exception as e:
            self.module.fail_json(msg=str(e))

    def apply(self):
        sdsb_storage_system_data = None
        try:
            if (
                self.params_manager.connection_info.connection_type.lower()
                == ConnectionTypes.GATEWAY
            ):
                pass
            else:
                sdsb_storage_system_data = asdict(
                    self.direct_sdsb_storage_system_read()
                )
            snake_case_storage_system_data = camel_dict_to_snake_case(
                sdsb_storage_system_data
            )

        except Exception as e:
            self.module.fail_json(msg=str(e))

        self.module.exit_json(storageSystem=snake_case_storage_system_data)

    def direct_sdsb_storage_system_read(self):
        result = sdsb_storage_system.SDSBStorageSystemReconciler(
            self.params_manager.connection_info
        ).sdsb_get_storage_system()
        if result is None:
            self.module.fail_json("Couldn't read storage system.")
        return result


def main(module=None):
    obj_store = SDSBStorageSystemFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
