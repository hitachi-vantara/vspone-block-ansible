#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hv_lun_facts
short_description: Retrieves information about logical units (LUNs) from Hitachi VSP storage systems.
description:
  - This module retrieves information about logical units (LUNs) from Hitachi VSP storage systems.
  - It provides details such as LUN IDs, names, and other relevant information.
version_added: '3.0.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.0.0
requirements:
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
    description: Specification for retrieving LUN information.
    type: dict
    required: false
    suboptions:
      lun:
        description: ID of the specific LUN to retrieve information for (Works only for gateway connection type).
        type: int
        required: false
      start_ldev_id:
        description: Starting LDEV ID for filtering LUNs.
        type: int
        required: false
      name:
        description: Name of the LUN.
        type: str
        required: false
      count:
        description: Number of LUNs to retrieve.
        type: int
        required: false
      end_ldev_id:
        description: Ending LDEV ID for filtering LUNs.
        type: int
        required: false
'''

EXAMPLES = '''
- name: Retrieve information about all LUNs
  hv_lun_facts:
    storage_system_info:
      serial: "ABC123"
    connection_info:
      address: gateway.company.com
      api_token: "api token value"
      connection_type: "gateway"
      subscriber_id: "sub123"
    spec:
      count: 10

- name: Retrieve information about a specific LUN
  hv_lun_facts:
    storage_system_info:
      serial: "ABC123"
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"
    spec:
      lun: 123
'''

RETURN = '''
luns:
  description: List of logical units (LUNs) managed by the module.
  returned: success
  type: list
  elements: dict
  sample: [
    {
      "ldev_id": 123,
      "deduplication_compression_mode": "Enabled",
      "emulation_type": "Fibre Channel",
      "name": "LUN1",
      "parity_group_id": "PG1",
      "pool_id": 1,
      "resource_group_id": 1,
      "status": "Online",
      "total_capacity": "10 GB",
      "used_capacity": "5 GB",
      "path_count": 2,
      "provision_type": "Thin Provisioning",
      "logical_unit_id_hex_format": "0x123456789ABCDEF",
      "canonical_name": "naa.123456789ABCDEF",
      "dedup_compression_progress": 100,
      "dedup_compression_status": "Completed",
      "is_alua": true
    }
  ]
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPVolumeArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    StateValue,
    ConnectionTypes,
)

import ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_lun_facts_runner as runner

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_volume,
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

logger = Log()


class VSPVolumeFactManager:
    def __init__(self):

        self.argument_spec = VSPVolumeArguments().volume_fact()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandatory , optional mandatory arguments
        )
        try:
            params_manager = VSPParametersManager(self.module.params)
            self.spec = params_manager.set_volume_fact_spec()
            self.connection_info = params_manager.get_connection_info()
            self.serial = params_manager.get_serial()
        except Exception as e:
            self.module.fail_json(msg=str(e))

    def apply(self):

        volume_data = None
        logger.writeInfo(f"{self.connection_info.connection_type} connection type")
        try:

            if self.connection_info.connection_type.lower() == ConnectionTypes.GATEWAY:
                volume_data = self.gateway_volume_read()
                logger.writeDebug("63 volume_data={}", volume_data)
            else:
                volume_data = self.direct_volume_read()

            volume_data_extracted = vsp_volume.VolumeCommonPropertiesExtractor(
                self.serial
            ).extract(volume_data)

        except Exception as e:
            self.module.fail_json(msg=str(e))

        self.module.exit_json(data=volume_data_extracted)

    def direct_volume_read(self):

        result = vsp_volume.VSPVolumeReconciler(
            self.connection_info,
            self.serial,
        ).get_volumes(self.spec)

        if not result:
            self.module.fail_json("Couldn't read volume ")
        return result.data_to_list()

    def gateway_volume_read(self):
        if self.module.params.get("spec"):
            self.module.params["spec"]["max_count"] = self.module.params.get(
                "spec"
            ).get("count")

            self.module.params["spec"]["lun_end"] = self.module.params.get("spec").get(
                "end_ldev_id"
            )

        try:
            return runner.runPlaybook(self.module)
        except HiException as ex:
            if HAS_MESSAGE_ID:
                logger.writeAMException(MessageID.ERR_OPERATION_LUN)
            else:
                logger.writeAMException("0X0000")
            self.module.fail_json(msg=ex.format())
        except Exception as ex:
            self.module.fail_json(msg=str(ex))


def main():
    """ """
    obj_store = VSPVolumeFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
