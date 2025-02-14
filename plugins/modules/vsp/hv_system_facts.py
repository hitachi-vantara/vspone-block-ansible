#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_system_facts
short_description: Retrieves system information from Hitachi VSP storage systems.
description:
  - This module retrieves the system information from Hitachi VSP storage systems.
  - This module is supported only for gateway connection type.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/system_facts.yml)
version_added: '3.0.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
options:
  connection_info:
    description:
      - Information required to establish a connection to the storage system.
    type: dict
    required: true
    suboptions:
      address:
        description:
          - IP address or hostname of the UAI gateway.
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
        choices:
          - gateway
        default: gateway
      api_token:
        description:
          - Token value to access UAI gateway (required for authentication either 'username,password' or api_token).
        type: str
        required: false
      subscriber_id:
        description:
          - This field is valid for gateway connection type only. This is an optional field and only needed to support multi-tenancy environment.
        type: str
        required: false
  spec:
    description:
      - Special options for the module.
    type: dict
    required: false
    suboptions:
      refresh:
        description:
          - Force a refresh of the system information.
        type: bool
        required: false
        default: false
"""

EXAMPLES = """
-
  name: Get all storage systems
  tasks:
    - hv_system_facts:
        connection_info:
          address: gateway.company.com
          username: "{{management_username}}"
          password: "{{management_key}}"
      register: result
    - debug: var=result
"""

RETURN = """
storages:
  description: a list of storage system information.
  returned: always
  type: list
  elements: dict
  sample:
    - address: "196.168.0.126"
      entitlement_status: "assigned"
      gateway_address: "196.168.0.50"
      health_status: "NORMAL"
      microcode_version: "93-07-23-80/01"
      model: "VSP E1090H"
      partner_id: "partnerid"
      resource_id: "storage-12d27566fa9feb38f728801ae15997b3"
      resource_state: "Normal"
      serial_number: "715036"
"""

import ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_ucp_facts_runner as runner
from ansible.module_utils.basic import AnsibleModule

# from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
#     Log,
# )
# from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_exceptions import (
#     HiException,
# )

# ANSIBLE_METADATA = {
#     "metadata_version": "1.1",
#     "supported_by": "certified",
#     "status": ["stableinterface"],
# }

# try:
#     from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_messages import (
#         MessageID,
#     )

#     HAS_MESSAGE_ID = True
# except ImportError:
#     HAS_MESSAGE_ID = False


def main(module=None):
    # logger = Log()
    # logger.writeInfo("=== Start of System Facts ===")
    # logger.writeDebug("Main")
    fields = {
        "spec": {
            "required": False,
            "type": "dict",
            "options": {
                "refresh": {"required": False, "type": "bool", "default": False},
            },
        },
        "connection_info": {
            "required": True,
            "type": "dict",
            "options": {
                "address": {
                    "required": True,
                    "type": "str",
                },
                "username": {
                    "required": False,
                    "type": "str",
                },
                "password": {
                    "required": False,
                    "type": "str",
                    "no_log": True,
                },
                "api_token": {
                    "required": False,
                    "type": "str",
                    "no_log": True,
                },
                "subscriber_id": {
                    "required": False,
                    "type": "str",
                },
                "connection_type": {
                    "required": False,
                    "type": "str",
                    "choices": ["gateway"],
                    "default": "gateway",
                },
            },
        },
    }

    if module is None:
        module = AnsibleModule(argument_spec=fields, supports_check_mode=True)

    try:
        runner.runPlaybook(module)
    # except HiException as ex:
    # if HAS_MESSAGE_ID:
    #     logger.writeAMException(MessageID.ERR_OPERATION_HOSTGROUP)
    # else:
    #     logger.writeAMException("0X0000")
    # module.fail_json(msg=ex.format())
    # logger.writeException(ex)
    # logger.writeInfo("=== End of System Facts ===")
    # module.fail_json(msg=ex)
    except Exception as ex:
        # if HAS_MESSAGE_ID:
        #     logger.writeAMException(MessageID.ERR_OPERATION_HOSTGROUP)
        # else:
        #     logger.writeAMException("0X0000")
        # module.fail_json(msg=ex.format())
        # logger.writeInfo("=== End of System Facts ===")
        module.fail_json(msg=str(ex))


if __name__ == "__main__":
    main()
