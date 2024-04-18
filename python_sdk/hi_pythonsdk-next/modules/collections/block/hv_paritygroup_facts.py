#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = \
    r'''
---
module: hv_paritygroup_facts
short_description: This module provides information about the Hitachi storage parity group.
description:
     - The M(hv_paritygroup_facts) module provides the following operations
     - 1. Get Storage Parity Group

version_added: '02.9.0'
author:
  - Hitachi Vantara, LTD. VERSION 02.3.0
requirements:
options:
  collections:
    description:
      - Ansible collections name for Hitachi storage parity group modules 
    type: string
    required: yes
    default: hitachi.storage
  storage_system_info:
    required: yes
    description:
      - storage_system_info has the following properties
      - =================================================================
      - Storage System information
      - =================================================================
      - C(storage_serial:) Mandatory input. String type. Storage system serial number.
      - C(ucp_name:) Mandatory input. String type. UCP system name.
      - =================================================================
    default: n/a
  ucp_advisor_info:
    required: yes
    description:
      - ucp_advisor_info has the following properties
      - =================================================================
      - UCP Advisor information
      - =================================================================
      - C(ucpadvisor_address:) Mandatory input. String type. UCPA address.
      - C(ucpadvisor_username:) Mandatory input. String type. UCPA user name.
      - C(ucpadvisor_password:) Mandatory input. String type. UCPA password in clear text.
      - =================================================================
    default: n/a
'''

EXAMPLES = \
    r'''
-
  name: Get All Parity Group details
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: vars.ucpa.yml
  vars:
    - storage_serial: "715035"
    - ucp_name: "20-253"
  tasks:
    - hv_paritygroup_facts:
        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
        ucp_advisor_info:
          address: "{{ucpadvisor_address}}"
          username: "{{ucpadvisor_username}}"
          password: "{{ucpadvisor_password}}"
      register: result
    - debug: var=result.paritygroup

'''

RETURN = r'''
'''

import json

try:
    from ansible_collections.hitachi.storage.plugins.module_utils.hv_messages import MessageID
    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False
from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log, \
    HiException
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystem
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystemManager
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.hitachi.storage.plugins.module_utils.hv_paritygroup_facts_runner as runner
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import Utils

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'supported_by': 'certified',
                    'status': ['stableinterface']}

logger = Log()


def main(module=None):
    fields = {
        'storage_system_info': {'required': True, 'type': 'json'},
        'ucp_advisor_info': {'required': True, 'type': 'json'},
        'data': {'required': False, 'type': 'json'}
        }

    if module is None:
        module = AnsibleModule(argument_spec=fields)

    try:
        runner.runPlaybook(module)
    except HiException as ex:
        if HAS_MESSAGE_ID:
            logger.writeAMException(MessageID.ERR_CREATE_DYNAMICPOOL)
        else:
            logger.writeAMException('0x0000')
        module.fail_json(msg=ex.format())
    except Exception as ex:
        module.fail_json(msg=ex.message)


if __name__ == '__main__':
    main()
