#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_hg_facts
short_description: Retrieves host group information from a specified Hitachi VSP storage system.
description:
  - This module fetches detailed information about host groups configured within a given Hitachi VSP storage system.
  - This module is supported for both C(direct) and C(gateway) connection types.
  - For C(direct) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/hostgroup_facts.yml)
  - For C(gateway) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/hostgroup_facts.yml)
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
      - Information about the Hitachi storage system. This field is required for gateway connection type only.
    type: dict
    required: false
    suboptions:
      serial:
        description: Serial number of the Hitachi storage system.
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
        elements: str
      query:
        description: Determines what information to return about the host groups. Can specify 'wwns' for HBA WWNs, 'ldevs' for mapped LDEVs, or both.
        type: list
        elements: str
        required: false
        choices: ['wwns', 'ldevs']
        default: []
      lun:
        description: Filters the host groups to those associated with the specified LUN.
        type: int
        required: false
"""

EXAMPLES = """
- name: Show LDEVs/WWNs for host groups for gateway connection type
  hitachivantara.vspone_block.vsp.hv_hg_facts:
    storage_system_info:
      serial: "811150"
    connection_info:
      address: gateway.company.com
      api_token: "api token value"
      connection_type: "gateway"
      subscriber_id: 811150
    spec:
      query: ['wwns', 'ldevs']
      name: 'test-ansible-hg-1'
      ports: ['CL1-A', 'CL2-B']

- name: Get Host Groups of specific ports for gateway connection type
  hitachivantara.vspone_block.vsp.hv_hg_facts:
    storage_system_info:
      serial: "811150"
    connection_info:
      address: gateway.company.com
      api_token: "api token value"
      connection_type: "gateway"
    spec:
      ports: ['CL1-A', 'CL2-B']

- name: Get all host groups for direct connection type
  hitachivantara.vspone_block.vsp.hv_hg_facts:
    connection_info:
      address: storage1.company.com
      username: "dummy_user"
      password: "dummy_password"

- name: Get Host Groups of specific ports for direct connection type
  hitachivantara.vspone_block.vsp.hv_hg_facts:
    connection_info:
      address: storage1.company.com
      username: "dummy_user"
      password: "dummy_password"
    spec:
      ports: ['CL1-A', 'CL2-B']
"""

RETURN = """
ansible_facts:
  description: The collected host group facts.
  returned: always
  type: dict
  contains:
    hostGroups:
      description: List of host groups retrieved from the storage system.
      returned: always
      type: list
      elements: dict
      contains:
        entitlement_status:
          description: Entitlement status of the host group.
          type: str
          sample: "assigned"
        host_group_id:
          description: ID of the host group.
          type: int
          sample: 93
        host_group_name:
          description: Name of the host group.
          type: str
          sample: "ansible-test-hg"
        host_mode:
          description: Host mode of the host group.
          type: str
          sample: "STANDARD"
        host_mode_options:
          description: List of host mode options.
          type: list
          elements: dict
          contains:
            host_mode_option:
              description: Host mode option.
              type: str
              sample: "EXTENDED_COPY"
            host_mode_option_number:
              description: Host mode option number.
              type: int
              sample: 54
        lun_paths:
          description: List of LUN paths.
          type: list
          elements: dict
          contains:
            ldevId:
              description: LDEV ID.
              type: int
              sample: 166
            lunId:
              description: LUN ID.
              type: int
              sample: 0
        partner_id:
          description: Partner ID.
          type: str
          sample: "partnerid"
        port:
          description: Port associated with the host group.
          type: str
          sample: "CL1-A"
        resource_group_id:
          description: Resource group ID.
          type: int
          sample: 0
        storage_id:
          description: Storage ID.
          type: str
          sample: "storage-39f4eef0175c754bb90417358b0133c3"
        subscriber_id:
          description: Subscriber ID.
          type: str
          sample: "811150"
        wwns:
          description: List of WWNs.
          type: list
          elements: dict
          contains:
            id:
              description: WWN ID.
              type: str
              sample: "1212121212121212"
            name:
              description: Name associated with the WWN.
              type: str
              sample: ""
"""

from ansible.module_utils.basic import AnsibleModule

import ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_hg_facts_runner as runner

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPHostGroupArguments,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_host_group,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_exceptions import (
    HiException,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.message.module_msgs import (
    ModuleMessage,
)


class VSPHostGroupFactsManager:
    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPHostGroupArguments().host_group_facts()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        try:
            self.params = VSPParametersManager(self.module.params)
            self.serial_number = self.params.storage_system_info.serial
            self.spec = self.params.get_host_group_spec()
            self.connection_info = self.params.get_connection_info()

        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Host Group Facts ===")
        registration_message = validate_ansible_product_registration()
        host_group_data = None
        host_group_data_extracted = {}
        try:
            if (
                self.params.connection_info.connection_type.lower()
                == ConnectionTypes.DIRECT
            ):
                host_group_data = self.direct_host_group_read()
                self.logger.writeDebug(f"host_group_data= {host_group_data}")
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
                self.logger.writeDebug(f"host_group_data= {host_group_data}")
                host_group_data_extracted = (
                    vsp_host_group.VSPHostGroupCommonPropertiesExtractor(
                        self.serial_number
                    ).extract_dict(host_group_data)
                )

        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of Host Group Facts ===")
            self.module.fail_json(msg=str(e))
        if registration_message:
            host_group_data_extracted["user_consent_required"] = registration_message
        self.logger.writeInfo(f"{host_group_data_extracted}")
        self.logger.writeInfo("=== End of Host Group Facts ===")
        self.module.exit_json(changed=False, ansible_facts=host_group_data_extracted)

    def direct_host_group_read(self):
        result = vsp_host_group.VSPHostGroupReconciler(
            self.connection_info, self.serial_number
        ).get_host_groups(self.spec)
        if result is None:
            raise ValueError(ModuleMessage.HOST_GROUP_NOT_FOUND.value)
        return result.data_to_list()

    def gateway_host_group_read(self):
        self.module.params["spec"] = self.module.params.get("spec")
        try:
            return runner.runPlaybook(self.module)
        except HiException as ex:
            raise Exception(ex.format())
        except Exception as ex:
            raise Exception(str(ex))


def main():
    obj_store = VSPHostGroupFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
