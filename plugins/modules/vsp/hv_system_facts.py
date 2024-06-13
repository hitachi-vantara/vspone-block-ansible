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

DOCUMENTATION = """
---
module: hv_system_facts
short_description: Retrives system information from Hitachi VSP storage systems.
description:
     - This module retrives the system information from Hitachi VSP storage systems.
version_added: '3.0.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.0.0
options:
  connection_info:
    description: Information required to establish a connection to the storage system.
    type: dict
    required: true
    suboptions:
      address:
        description: IP address or hostname of the UAI gateway.
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
        required: true
        choices: ['gateway']
      api_token:
        description: Token value to access UAI gateway (required for authentication either 'username,password' or api_token).
        type: str
        required: false
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

import json
import ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_ucp_facts_runner as runner
from ansible.module_utils.basic import AnsibleModule

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


def main(module=None):
    logger.writeDebug("Main")
    fields = {
        "serial_number": {"required": False, "type": "str"},
        "model": {"required": False, "type": "str"},
        "name": {"required": False, "type": "str"},
        "management_address": {"required": False, "type": "str"},
        "management_username": {"required": False, "type": "str"},
        "management_key": {"required": False, "type": "str"},
        "connection_info": {
            "required": True,
            "type": "dict",
            "description": "Information for establishing the connection.",
            "options": {
                "address": {
                    "required": True,
                    "type": "str",
                    "description": "The management address of the storage system.",
                },
                "username": {
                    "required": False,
                    "type": "str",
                    "description": "The username for authentication.",
                },
                "password": {
                    "required": False,
                    "type": "str",
                    "description": "The password or authentication key.",
                },
                "api_token": {
                    "required": False,
                    "type": "str",
                    "description": "The api token for the connection.",
                },
                "subscriber_id": {
                    "required": False,
                    "type": "str",
                    "description": "The subscriber ID.",
                },
                "connection_type": {
                    "required": False,
                    "type": "str",
                    "description": "The type of connection.",
                    "choices": ["gateway", "direct"],
                    "default": "direct",
                },
            },
        },
    }

    if module is None:
        module = AnsibleModule(argument_spec=fields)

    try:
        runner.runPlaybook(module)
    except HiException as ex:
        if HAS_MESSAGE_ID:
            # FIXME
            logger.writeAMException(MessageID.ERR_OPERATION_HOSTGROUP)
        else:
            logger.writeAMException("0X0000")
        # module.fail_json(msg=ex.format())
        module.fail_json(msg=ex)
    except Exception as ex:
        if HAS_MESSAGE_ID:
            # FIXME
            logger.writeAMException(MessageID.ERR_OPERATION_HOSTGROUP)
        else:
            logger.writeAMException("0X0000")
        # module.fail_json(msg=ex.format())
        module.fail_json(msg=str(ex))


if __name__ == "__main__":
    main()
