#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'supported_by': 'certified',
                    'status': ['stableinterface']}

DOCUMENTATION = \
    r'''
---
module: hv_ucp_facts
short_description: This module provides UCP information on the specified Hitachi UCPA system.
description:
     - The M(hv_ucp_facts) module provides the UCP information on the specified Hitachi UCPA system.
version_added: '02.9.0'
author:
  - Hitachi Vantara, LTD. VERSION 02.3.0
options:
  collections:
    description:
      - Ansible collections name for Hitachi storage modules 
    type: string
    required: yes
    default: hitachi.storage
  data:
    required: yes
    description:
      - data has the following properties
      - =================================================================
      - Getting UCP information Facts
      - =================================================================
      - C(ucpadvisor_address:) Mandatory input. String type. UCPA address.
      - C(ucpadvisor_username:) Mandatory input. String type. UCPA user name.
      - C(ucpadvisor_password:) Mandatory input. String type. UCPA password in clear text.
      - C(name:) Optional input. String type. Get one UCP by name, case sensitive.
      - =================================================================
'''

EXAMPLES = \
    r'''
-
  name: Get All UCP Systems
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: vars.yml
  vars_files:
  tasks:
    - hv_ucp_facts:
        ucpadvisor_address: "{{ucpadvisor_address}}"
        ucpadvisor_username: "{{ucpadvisor_username}}"
        ucpadvisor_key: "{{ucpadvisor_password}}"
        name: "{{ name | default(None) }}"
      register: result
    - debug: var=result.ucps

'''

RETURN = r'''
'''

import json
import ansible_collections.hitachi.storage.plugins.module_utils.hv_ucp_facts_runner as runner
from ansible.module_utils.basic import AnsibleModule

try:
    from ansible_collections.hitachi.storage.plugins.module_utils.hv_logger import MessageID
    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False
from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log, \
    HiException

logger = Log()


def main(module=None):
    logger.writeDebug("Main")
    fields = {
              'serial_number': {'required': False, 'type': 'str'},
              'model': {'required': False, 'type': 'str'},
              'name': {'required': False, 'type': 'str'},
              'ucpadvisor_address': {'required': True, 'type': 'str'},
              'ucpadvisor_username': {'required': True, 'type': 'str'},
              'ucpadvisor_key': {'required': True, 'type': 'str'},
              }

    if module is None:
        module = AnsibleModule(argument_spec=fields)

    try:
        runner.runPlaybook(module)
    except HiException as ex:
        if HAS_MESSAGE_ID:
            #FIXME
            logger.writeAMException(MessageID.ERR_OPERATION_HOSTGROUP)
        else:
            logger.writeAMException("0X0000")
        # module.fail_json(msg=ex.format())
        module.fail_json(msg=ex)
    except Exception as ex:
        if HAS_MESSAGE_ID:
            #FIXME
            logger.writeAMException(MessageID.ERR_OPERATION_HOSTGROUP)
        else:
            logger.writeAMException("0X0000")
        # module.fail_json(msg=ex.format())
        module.fail_json(msg=str(ex))


if __name__ == '__main__':
    main()
