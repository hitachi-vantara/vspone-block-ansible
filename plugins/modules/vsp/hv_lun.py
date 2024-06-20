#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_lun
short_description: Manages logical units (LUNs) on Hitachi VSP storage systems.
description:
  - This module allows for the creation, modification, or deletion of logical units (LUNs) on Hitachi VSP storage systems.
  - It supports operations such as creating a new LUN, updating an existing LUN, or deleting a LUN.
version_added: '3.0.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.0.0
requirements:
options:
  state:
    description: The desired state of the LUN.
    type: str
    required: false
    choices: ['present', 'absent']
    default: 'present'
  storage_system_info:
    description: Information about the Hitachi storage system.
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
        description: Subscriber ID for multi-tenancy (required for 'gateway' connection type).
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway (required for authentication either 'username,password' or api_token).
        type: str
        required: false
  spec:
    description: Specification for the LUN.
    type: dict
    required: true
    suboptions:
      pool_id:
        description: ID of the pool where the LUN will be created. Options pool_id and parity_group_id are mutually exclusive.
        type: int
        required: false
      parity_group:
        description: ID of the parity_group where the LUN will be created. Options pool_id and parity_group_id are mutually exclusive.
        type: int
        required: false
      size:
        description: Size of the LUN. Can be specified in units such as GB, TB, or MB (e.g., '10GB', '5TB', '100MB', 200).
        type: str
        required: false
      lun:
        description: ID of the LUN (required for delete and update operations), for new it will assigned to this lun if it's free.
        type: int
        required: false
      name:
        description: Name of the LUN (optional).
        type: str
        required: false
      capacity_saving:
        description: Whether capacity saving is (compression, compression_deduplication or disabled). Default is disabled.
        type: str
        required: false
      data_reduction_share:
        description: Specify whether to create a data reduction shared volume( Default =True for thin image advance direct connect).
        type: bool
        required: false
"""

EXAMPLES = """
- name: Create a new LUN
  hv_lun:
    state: present
    storage_system_info:
      serial: "ABC123"
      connection_info:
        address: gateway.company.com
        api_token: "api_token_value"
        connection_type: "gateway"
        subscriber_id: "sub123"
    spec:
      pool_id: 1
      size: "10GB"
      name: "New LUN"
      capacity_saving: "compression_deduplication"
      data_reduction_share: True

- name: Update an existing LUN
  hv_lun:
    state: present
    storage_system_info:
      serial: "ABC123"
      connection_info:
        address: gateway.company.com
        api_token: "api_token_value"
        connection_type: "gateway"
        subscriber_id: "sub123"
    spec:
      lun: 123
      size: "5TB"
      capacity_saving: "disabled"

- name: Delete a LUN
  hv_lun:
    state: absent
    storage_system_info:
      serial: "ABC123"
      connection_info:
        address: gateway.company.com
        api_token: "api_token_value"
        connection_type: "gateway"
        subscriber_id: "sub123"
    spec:
      lun: 123
"""

RETURN = """
luns:
  description: Info of a logical unit (LUN).
  returned: success
  type: dict
  sample: {
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
    "naa_id": "naa.123456789ABCDEF"
    "dedup_compression_progress": 100,
    "dedup_compression_status": "Completed",
    "is_alua": true,
    "is_data_reduction_share_enabled": true
  }
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPVolumeArguments,
    VSPParametersManager,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    StateValue,
    ConnectionTypes,
    CommonConstants,
)
import ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_lun_runner as runner

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_volume,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    StateValue,
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


class VSPVolume:
    def __init__(self):

        self.argument_spec = VSPVolumeArguments().volume()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )

        try:
            params_manager = VSPParametersManager(self.module.params)
            self.spec = params_manager.set_volume_spec()
            self.connection_info = params_manager.get_connection_info()
            self.serial = params_manager.get_serial()
            self.state = params_manager.get_state()
        except Exception as e:
            logger.writeError(f"An error occurred during initialization: {str(e)}")
            self.module.fail_json(msg=str(e))

    def apply(self):

        logger.writeInfo(f"{self.connection_info.connection_type} connection type")

        try:
            comment = None
            isGateway = False
            if self.connection_info.connection_type.lower() == ConnectionTypes.GATEWAY:
                isGateway = True
                volume_data = self.gateway_volume()
                logger.writeDebug("volume_data={}", volume_data)
                ## volume_data={'changed': False, 'lun': None, 'comment': 'LUN not found. (Perhaps it has already been deleted?)', 'skipped': True}
                self.connection_info.changed = volume_data.get("changed")
            else:
                volume_data = self.direct_volume()

            if self.state == StateValue.ABSENT and isGateway:
                comment = volume_data.get("comment", None)
                volume_response = []
            elif self.state == StateValue.ABSENT and not volume_data:
                volume_response = "Volume deleted"
            else:
                if isinstance(volume_data, dict):
                  comment = volume_data.get("comment", None)
                volume_response = self.extract_volume_properties(volume_data)

        except Exception as e:
            logger.writeError(f"An error occurred: {str(e)}")
            self.module.fail_json(msg=str(e))

        response = {"changed": self.connection_info.changed, "data": volume_response}
        if comment:
            response["comment"] = comment

        self.module.exit_json(**response)

    def direct_volume(self):

        result = vsp_volume.VSPVolumeReconciler(
            self.connection_info,
            self.serial,
        ).volume_reconcile(self.state, self.spec)

        return result

    def gateway_volume(self):

        try:
            return runner.runPlaybook(self.module)
        except HiException as ex:
            if HAS_MESSAGE_ID:
                logger.writeAMException(MessageID.ERR_OPERATION_LUN)
            else:
                logger.writeAMException("0X0000")
            self.module.fail_json(msg=ex.format())
        except Exception as ex:
            logger.writeError(
                f"An error occurred during gateway volume operation: {str(ex)}"
            )
            self.module.fail_json(msg=str(ex))

    def extract_volume_properties(self, volume_data):
        if not volume_data:
            return None

        # logger.writeDebug('115 volume_data={}',volume_data)
        logger.writeDebug("115 type={}", type(volume_data))
        if isinstance(volume_data, dict):
            volume_dict = volume_data.get("lun")
        else:
            volume_dict = volume_data.to_dict() if volume_data else {}
        return vsp_volume.VolumeCommonPropertiesExtractor(self.serial).extract(
            [volume_dict]
        )[0]


def main():
    """
    :return: None
    """
    obj_store = VSPVolume()
    obj_store.apply()


if __name__ == "__main__":
    main()
