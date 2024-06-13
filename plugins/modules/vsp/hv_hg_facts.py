#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


__metaclass__ = type

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "supported_by": "certified",
    "status": ["stableinterface"],
}

DOCUMENTATION = '''
---
module: hv_hg_facts
short_description: Retrieves host group information from a specified Hitachi VSP storage system.
description:
     - This module fetches detailed information about host groups configured within a given Hitachi VSP storage system.
version_added: '3.0.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.0.0
options:
  storage_system_info:
    description:
      - Information about the Hitachi storage system.
    type: dict
    required: true
    suboptions:
      serial:
        description: Serial number of the Hitachi storage system.
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
    description: Specification for retrieving Host Group information.
    type: dict
    required: false
    suboptions:
      name:
        description: If specified, filters the results to include only the host groups with this name.
        type: str
        required: false
      ports:
        description: Filters the host groups to those associated with the specified Storage FC ports.
        type: list
        required: false
      query:
        description: Determines what information to return about the host groups. Can specify 'wwns' for HBA WWNs, 'luns' for mapped LUNs, or both.
        type: list
        elements: str
        required: false
        choices: ['wwns', 'luns']
'''

EXAMPLES = """
- name:  Show luns/wwns for hostgroups
  tasks:
    - hv_hg_facts:
        storage_system_info:
          serial: "ABC123"
        connection_info:
          address: gateway.company.com
          api_token: "api token value"
          connection_type: "gateway"
          subscriber_id: "sub123"
        spec:
          query: [ 'wwns', 'luns' ]
          name: 'test-ansible-hg-1'
          ports: [ 'CL1-A', 'CL2-B' ]
      register: result
    - debug: var=result.hostGroups
    
- name: Get Host Groups
  tasks:
    - hv_hg_facts:
        storage_system_info:
          serial: "ABC123"
        connection_info:
          address: gateway.company.com
          api_token: "api token value"
          connection_type: "gateway"
          subscriber_id: "sub123"
        spec:
          ports: [ 'CL1-A', 'CL2-B' ]
      register: result
    - debug: var=result.hostGroups
"""

RETURN = '''
hostGroups:
  type: list
  description: List of host groups retrieved from the storage system.
  returned: always
  elements: dict
  sample: [
    {
      "entitlement_status": "assigned",
      "host_group_id": 93,
      "host_group_name": "ansible-test-hg",
      "host_mode": "STANDARD",
      "host_mode_options": [
          {
              "host_mode_option": "EXTENDED_COPY",
              "host_mode_option_number": 54
          },
          {
              "host_mode_option": "VSTORAGE_APIS_ON_T10_STANDARDS",
              "host_mode_option_number": 63
          }
      ],
      "lun_paths": [
        {
          "ldevId": 166,
          "lunId": 0
        },
        {
          "ldevId": 206,
          "lunId": 1
        }
      ],
      "partner_id": "partnerid",
      "port": "CL1-A",
      "resource_group_id": 0,
      "storage_id": "storage-39f4eef0175c754bb90417358b0133c3",
      "subscriber_id": "12345",
      "wwns": [
        {
          "id": "1212121212121212",
          "name": ""
        }
      ]
    }
  ]
'''

import json
from dataclasses import dataclass, asdict

import ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_hg_facts_runner as runner
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_infra import (
    StorageSystem,
    HostMode,
    StorageSystemManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPHostGroupArguments,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    StateValue,
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_host_group,
)

try:
    from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_logger import (
        MessageID,
    )

    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_exceptions import (
    HiException,
)


from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPParametersManager,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    dicts_to_dataclass_list,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.model.vsp_host_group_models import *

logger = Log()


class VSPHostGroupFactsManager:
    def __init__(self):

        self.argument_spec = VSPHostGroupArguments().host_group_facts()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )

        self.params = VSPParametersManager(self.module.params)
        self.serial_number = self.params.storage_system_info.serial

        parameterManager = VSPParametersManager(self.module.params)
        self.spec = parameterManager.get_host_group_spec()
        self.connection_info = parameterManager.get_connection_info()

    def apply(self):
        logger = Log()
        host_group_data = None
        logger.writeInfo(
            f"{self.params.connection_info.connection_type} connection type"
        )
        try:
            if (
                self.params.connection_info.connection_type.lower()
                == ConnectionTypes.DIRECT
            ):
                host_group_data = self.direct_host_group_read()
                logger.writeDebug(f"host_group_data= {host_group_data}")
                host_group_data_result = (
                vsp_host_group.VSPHostGroupCommonPropertiesExtractor(
                    self.serial_number
                  ).extract(host_group_data)
                )
                host_group_data_extracted = {"hostGroups": host_group_data_result}

            elif (
                self.params.connection_info.connection_type.lower()
                == ConnectionTypes.GATEWAY
            ):
                host_group_list = self.gateway_host_group_read()
                host_group_data = {host_group_list}
                logger.writeDebug(f"host_group_data= {host_group_data}")
                host_group_data_extracted = (
                vsp_host_group.VSPHostGroupCommonPropertiesExtractor(
                    self.serial_number
                  ).extract_dict(host_group_data)
                )

        except Exception as e:
            self.module.fail_json(msg=str(e))

        self.module.exit_json(**host_group_data_extracted)

    def direct_host_group_read(self):
        result = vsp_host_group.VSPHostGroupReconciler(
            self.connection_info, self.serial_number
        ).get_host_groups(self.spec)
        if result is None:
            self.module.fail_json("Couldn't read host group ")
        return result.data_to_list()

    def gateway_host_group_read(self):
        self.module.params["spec"] = self.module.params.get("spec")
        try:
            return runner.runPlaybook(self.module)
        except HiException as ex:
            self.module.fail_json(msg=ex.format())
        except Exception as ex:
            self.module.fail_json(msg=str(ex))


def main(module=None):
    obj_store = VSPHostGroupFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
