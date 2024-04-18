#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


__metaclass__ = type


DOCUMENTATION = \
    r'''
---
module: hv_storagereplication_facts
short_description: This module provides information about the Hitachi storage replication.
description:
     - The M(hv_storagereplication_facts) module provides the following operations
     - 1. Get Storage Pool

version_added: '02.9.0'
author:
  - Hitachi Vantara, LTD. VERSION 02.3.0
requirements:
options:
  collections:
    description:
      - Ansible collections name for Hitachi storage replication modules 
    type: string
    required: yes
    default: hitachi.storage
  repl_type:
    description:
      - set state to I(tc) for create and update true copy
      - set state to I(gad) for create and update gad
    type: str
    choices: [tc, gad]
  data:
    required: yes
    description:
      - data has the following properties
      - =================================================================
      - Get All Storage Replication
      - =================================================================
      - C(primary_storage_serial_no:) Mandatory input. Storage system serial number.
      - =================================================================
'''

EXAMPLES = \
    r'''
- name: Get TC pair details
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - primary_storage_serial_no: 123456
    - pvol_id: 121
  tasks:
    - hv_storagereplication_facts:
        repl_type: tc
        data:
          pvol_id: '{{ pvol_id | default(omit) }}'
          primary_storage_serial_no: '{{ primary_storage_serial_no  | default(None) }}'
      register: result
    - debug: var=result.storageReplication


- name: Get Gad pair details
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - primary_storage_serial_no: 123456
    - pvol_id: 121
  tasks:
    - hv_storagereplication_facts:
        repl_type: gad
        data:
          pvol_id: '{{ pvol_id | default(omit) }}'
          primary_storage_serial_no: '{{ primary_storage_serial_no  | default(None) }}'
      register: result
    - debug: var=result.storageReplication


- name: Get All Storage Replication Pair details
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - storage_serial: 123456
  tasks:
    - hv_storagereplication_facts:
        storage_serial: '{{ storage_serial  | default(None) }}'
      register: result
    - debug: var=result.storageReplication

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
import ansible_collections.hitachi.storage.plugins.module_utils.hv_storagereplication_facts_runner as runner
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import Utils

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'supported_by': 'certified',
                    'status': ['stableinterface']}

logger = Log()


def main(module=None):
    fields = {'storage_serial': {'required': False, 'type': 'int'},
              'repl_type': {'required': False, 'type': 'str'}, 'data': {'required': False, 'type': 'json'}}

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
        try:
            storageSystem = StorageSystem(module.params['storage_serial'
                                                        ])
            if storageSystem.isSessionNotFound(ex.message):
                StorageSystemManager.addStorgeSystemByJson()
                runner.runPlaybook(module)
            else:
                module.fail_json(msg=ex.message)
        except Exception as ex2:
            module.fail_json(msg=ex.message + '. ' + ex2.message)


if __name__ == '__main__':
    main()
