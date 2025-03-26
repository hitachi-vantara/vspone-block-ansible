#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_storagesystem_facts
short_description:  retrieves storage system information from Hitachi VSP storage systems.
description:
  - This module gathers facts about a specific storage system.
  - This module is supported for both C(direct) and C(gateway) connection types.
  - For C(direct) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/storagesystem_facts.yml)
  - For C(gateway) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/storagesystem_facts.yml)
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
    description: Specification for the storage system facts to be gathered.
    type: dict
    required: false
    suboptions:
      refresh:
        description: >
          Indicates whether to refresh the storage system information. If set to true, the storage system information will be refreshed.
          Supported only for C(gateway) connection type only.
        type: bool
        required: false
      query:
        description: Additional information to be gathered.
        type: list
        elements: str
        choices: ['ports', 'quorumdisks', 'journalPools', 'freeLogicalUnitList']
        required: false
"""

EXAMPLES = """
- name: Get Storage System facts for direct connection
  hitachivantara.vspone_block.vsp.hv_storagesystem_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
      connection_type: "direct"

- name: Get Storage System facts for gateway connection
  hitachivantara.vspone_block.vsp.hv_storagesystem_facts:
    storage_system_info:
      serial: "811150"
    connection_info:
      address: gateway1.company.com
      api_token: "api token value"
      connection_type: "gateway"

- name: Get Storage System using query for direct connection
  hitachivantara.vspone_block.vsp.hv_storagesystem_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
      connection_type: "direct"
    spec:
      query: ["ports", "quorumdisks", "journalPools", "freeLogicalUnitList"]

- name: Get Storage System using query for gateway connection
  hitachivantara.vspone_block.vsp.hv_storagesystem_facts:
    storage_system_info:
      serial: "811150"
    connection_info:
      address: gateway1.company.com
      api_token: "api token value"
      connection_type: "gateway"
    spec:
      query: ["ports", "quorumdisks", "journalPools", "freeLogicalUnitList"]
"""

RETURN = r"""
ansible_facts:
  description: The gathered facts about the storage system.
  returned: always
  type: dict
  contains:
    storage_system_info:
      description: The storage system information.
      returned: always
      type: dict
      contains:
        controller_address:
          description: IP address of the controller.
          type: str
          sample: "192.168.1.101"
        device_limits:
          description: Limits for various device parameters.
          type: dict
          contains:
            external_group_number_range:
              description: Range for external group numbers.
              type: dict
              contains:
                is_valid:
                  description: Indicates if the range is valid.
                  type: bool
                  sample: true
                max_value:
                  description: Maximum value of the range.
                  type: int
                  sample: 255
                min_value:
                  description: Minimum value of the range.
                  type: int
                  sample: 1
            external_group_sub_number_range:
              description: Range for external group sub-numbers.
              type: dict
              contains:
                is_valid:
                  description: Indicates if the range is valid.
                  type: bool
                  sample: true
                max_value:
                  description: Maximum value of the range.
                  type: int
                  sample: 255
                min_value:
                  description: Minimum value of the range.
                  type: int
                  sample: 1
            parity_group_number_range:
              description: Range for parity group numbers.
              type: dict
              contains:
                is_valid:
                  description: Indicates if the range is valid.
                  type: bool
                  sample: true
                max_value:
                  description: Maximum value of the range.
                  type: int
                  sample: 1
                min_value:
                  description: Minimum value of the range.
                  type: int
                  sample: 1
            parity_group_sub_number_range:
              description: Range for parity group sub-numbers.
              type: dict
              contains:
                is_valid:
                  description: Indicates if the range is valid.
                  type: bool
                  sample: true
                max_value:
                  description: Maximum value of the range.
                  type: int
                  sample: 32
                min_value:
                  description: Minimum value of the range.
                  type: int
                  sample: 1
        free_capacity:
          description: Free capacity of the storage system.
          type: str
          sample: "15.92 TB"
        free_capacity_in_mb:
          description: Free capacity in megabytes.
          type: int
          sample: 16696806
        free_gad_consistency_group_id:
          description: Free GAD consistency group ID.
          type: int
          sample: -1
        free_local_clone_consistency_group_id:
          description: Free local clone consistency group ID.
          type: int
          sample: 2
        free_remote_clone_consistency_group_id:
          description: Free remote clone consistency group ID.
          type: int
          sample: 3
        health_description:
          description: Description of the health status.
          type: str
          sample: ""
        health_status:
          description: Health status of the storage system.
          type: str
          sample: "Normal"
        management_address:
          description: Management IP address of the storage system.
          type: str
          sample: "192.168.1.100"
        microcode_version:
          description: Microcode version of the storage system.
          type: str
          sample: "83-05-02/00"
        model:
          description: Model of the storage system.
          type: str
          sample: "VSP_5100H"
        operational_status:
          description: Operational status of the storage system.
          type: str
          sample: "Normal"
        resource_state:
          description: Resource state of the storage system.
          type: str
          sample: "Healthy"
        serial_number:
          description: Serial number of the storage system.
          type: str
          sample: "811150"
        syslog_config:
          description: Syslog configuration of the storage system.
          type: dict
          contains:
            syslog_servers:
              description: List of syslog servers.
              type: list
              elements: dict
              contains:
                id:
                  description: ID of the syslog server.
                  type: int
                  sample: 1
                syslog_server_address:
                  description: Address of the syslog server.
                  type: str
                  sample: "192.168.0.187"
                syslog_server_port:
                  description: Port of the syslog server.
                  type: int
                  sample: 514
            detailed:
              description: Indicates if detailed logging is enabled.
              type: bool
              sample: true
        total_capacity:
          description: Total capacity of the storage system.
          type: str
          sample: "27.62 TB"
        total_capacity_in_mb:
          description: Total capacity in megabytes.
          type: int
          sample: 28958728
"""

from dataclasses import asdict
from ansible.module_utils.basic import AnsibleModule

try:
    from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_messages import (
        MessageID,
    )

    HAS_MESSAGE_ID = True
except ImportError:
    HAS_MESSAGE_ID = False
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_exceptions import (
    HiException,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPStorageSystemArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_storage_system,
)
import ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_storagesystem_facts_runner as runner

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    camel_dict_to_snake_case,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.message.module_msgs import (
    ModuleMessage,
)


class VspStorageSystemFactManager:
    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPStorageSystemArguments().storage_system_fact()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.set_storage_system_fact_spec()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Storage System Facts ===")
        storage_system_data = None
        registration_message = validate_ansible_product_registration()
        try:
            if (
                self.params_manager.connection_info.connection_type.lower()
                == ConnectionTypes.GATEWAY
            ):
                storage_system_data = self.gateway_storage_system_read()
            else:
                storage_system_data = asdict(self.direct_storage_system_read())

            self.logger.writeDebug("233 self.spec = {}", self.spec.query)
            specQuery = self.spec.query
            if specQuery:

                if storage_system_data.get("StoragePools"):
                    storage_system_data["storage_pools"] = storage_system_data[
                        "StoragePools"
                    ]
                if storage_system_data.get("Ports"):
                    storage_system_data["ports"] = storage_system_data["Ports"]
                if storage_system_data.get("QuorumDisks"):
                    storage_system_data["quorum_disks"] = storage_system_data[
                        "QuorumDisks"
                    ]
                if storage_system_data.get("JournalPools"):
                    storage_system_data["journal_pools"] = storage_system_data[
                        "JournalPools"
                    ]

            storage_system_data_extracted = (
                vsp_storage_system.VSPStorageSystemCommonPropertiesExtractor().extract(
                    storage_system_data
                )
            )
            snake_case_storage_system_data = camel_dict_to_snake_case(
                storage_system_data_extracted
            )

        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of Storage System Facts ===")
            self.module.fail_json(msg=str(e))
        data = {
            "storage_system": snake_case_storage_system_data,
        }
        if registration_message:
            data["user_consent_required"] = registration_message
        if self.spec.refresh is True:
            data["warning/message"] = (
                "The storage refresh operation will be completed after 'health_status' is changed from 'REFRESHING' to 'NORMAL'."
                "This operation may take upto 10 minutes."
            )
        self.logger.writeInfo(f"{data}")
        self.logger.writeInfo("=== End of Storage System Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)

    def direct_storage_system_read(self):
        result = vsp_storage_system.VSPStorageSystemReconciler(
            self.params_manager.connection_info,
            self.params_manager.storage_system_info.serial,
        ).get_storage_system(self.spec)
        if result is None:
            raise ValueError(ModuleMessage.STORAGE_SYSTEM_NOT_FOUND.value)
        return result

    def gateway_storage_system_read(self):
        try:
            self.module.params["spec"] = self.module.params.get("spec")
            return runner.runPlaybook(self.module)
        except HiException as ex:
            if HAS_MESSAGE_ID:
                self.logger.writeAMException(MessageID.ERR_AddRAIDStorageDevice)
            else:
                self.logger.writeAMException("0x0000")
            raise Exception(ex.format())
        except Exception as ex:
            # sng,a2.4 - there is no ex.message?
            # if ex is None or ex.message is None:
            msg = None
            if ex is None:
                msg = "Failed during get storage facts, please check input parameters."
            else:
                msg = str(ex)
            raise Exception(msg)


def main():
    obj_store = VspStorageSystemFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
