#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


__metaclass__ = type


DOCUMENTATION = """
---
module: hv_paritygroup_facts
short_description: retrieves information about parity groups from Hitachi VSP storage systems.
description:
     - This module gathers facts about parity groups from Hitachi VSP storage systems.
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
      - Specification for the parity group facts to be gathered.
    type: dict
    required: true
    suboptions:
      parity_group_id:
        description:
          - The parity group number of the parity group to retrieve.
        type: str
        required: false
"""

EXAMPLES = """
- name: Get a specific parity group
  tasks:
    - hv_paritygroup_facts:
        connection_info:
          address: storage1.company.com
          username: "admin"
          password: "secret"
          connection_type: "direct"
        spec:
          parity_group_id: 1-1

- name: Get all parity groups
  tasks:
    - hv_paritygroup_facts:
        connection_info:
          address: storage1.company.com
          username: "admin"
          password: "secret"
          connection_type: "direct"

"""

RETURN = """
paritygroup:
  description: The parity group information.
  returned: always
  type: list
  elements: dict
  sample:
    - copyback_mode: false
      drive_type: "SSD"
      free_capacity: "357.00GB"
      is_accelerated_compression: false
      is_encryption_enabled: false
      is_pool_array_group: false
      ldev_ids:
        - 6
        - 7
      parity_group_id: "1-1"
      raid_level: "RAID5"
      resource_group_id: -1
      resource_id: ""
      status: "NORMAL"
      total_capacity: "5.16TB"
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
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_paritygroup_facts_runner as runner
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPParityGroupArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_parity_group,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    camel_array_to_snake_case,
    camel_dict_to_snake_case,
)

logger = Log()


class VspParityGroupFactManager:
    def __init__(self):
        # VSPStoragePoolArguments
        self.argument_spec = VSPParityGroupArguments().parity_group_fact()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.get_parity_group_fact_spec()
        except Exception as e:
            self.module.fail_json(msg=str(e))

    def apply(self):
        try:
            if (
                self.params_manager.connection_info.connection_type.lower()
                == ConnectionTypes.GATEWAY
            ):
                self.gateway_parity_group_read()
            else:
                if self.spec.parity_group_id is not None:
                    parity_group = self.direct_parity_group_read(
                        self.spec.parity_group_id
                    )
                    parity_group_dict = parity_group.to_dict()
                    parity_group_data_extracted = vsp_parity_group.VSPParityGroupCommonPropertiesExtractor().extract_parity_group(
                        parity_group_dict
                    )
                    snake_case_parity_group_data = camel_dict_to_snake_case(
                        parity_group_data_extracted
                    )
                    self.module.exit_json(paritygroup=snake_case_parity_group_data)
                else:
                    all_parity_groups = self.direct_all_parity_groups_read()
                    parity_groups_list = all_parity_groups.data_to_list()
                    parity_groups_data_extracted = vsp_parity_group.VSPParityGroupCommonPropertiesExtractor().extract_all_parity_groups(
                        parity_groups_list
                    )
                    snake_case_parity_groups_data = camel_array_to_snake_case(
                        parity_groups_data_extracted
                    )
                    self.module.exit_json(paritygroup=snake_case_parity_groups_data)

        except HiException as ex:
            if HAS_MESSAGE_ID:
                logger.writeAMException(MessageID.ERR_GetParityGroups)
            else:
                logger.writeAMException("0x0000")
            self.module.fail_json(msg=ex.format())
        except Exception as ex:
            self.module.fail_json(msg=str(ex))

    def direct_all_parity_groups_read(self):
        result = vsp_parity_group.VSPParityGroupReconciler(
            self.params_manager.connection_info
        ).get_all_parity_groups()
        if result is None:
            self.module.fail_json("Couldn't read parity groups.")
        return result

    def direct_parity_group_read(self, pg_id):
        result = vsp_parity_group.VSPParityGroupReconciler(
            self.params_manager.connection_info
        ).get_parity_group(pg_id)
        if result is None:
            self.module.fail_json("Couldn't read parity group.")
        return result

    def gateway_parity_group_read(self):
        self.module.params["spec"] = self.module.params.get("spec")
        runner.runPlaybook(self.module)


def main(module=None):
    obj_store = VspParityGroupFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
