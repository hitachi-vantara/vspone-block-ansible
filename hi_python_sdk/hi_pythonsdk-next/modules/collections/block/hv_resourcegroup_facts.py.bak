#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = \
    r'''
---
module: hv_resourcegroup_facts
short_description: This module provides information about the Hitachi storage pool.
description:
     - The M(hv_resourcegroup_facts) module provides the following operations
     - 1. Get Resource Group details

version_added: '02.9.0'
author:
  - Hitachi Vantara, LTD. VERSION 02.3.0
requirements:
options:
  collections:
    description:
      - Ansible collections name for Hitachi resource group modules 
    type: string
    required: yes
    default: hitachi.storage
  data:
    required: yes
    description:
      - data has the following properties
      - =================================================================
      - Get Resource Group
      - =================================================================
      - C(primary_storage_serial_no:) Mandatory input. Storage system serial number.
      - C(secondary_storage_serial_no:) Mandatory input. String type. Secondary storage system serial number.
      - =================================================================

'''

EXAMPLES = \
    r'''
- 
  name: Get Resource Group details
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - primary_storage_serial_no: 123456
    - secondary_storage_serial_no: 123457
  tasks:
    - hv_storagereplication_facts:
        primary_storage_serial_no: '{{ primary_storage_serial_no }}'
        data:
          secondary_storage_serial_no: '{{ secondary_storage_serial_no }}'
      register: result
    - debug: var=result.resourceGroup

- 
  name: Get All Resource Group details
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - primary_storage_serial_no: 123456
  tasks:
    - hv_storagereplication_facts:
        primary_storage_serial_no: '{{ primary_storage_serial_no }}'
        data:
      register: result
    - debug: var=result.resourceGroup

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
import ansible_collections.hitachi.storage.plugins.module_utils.hv_resourcegroup_facts_runner as runner
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import Utils

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'supported_by': 'certified',
                    'status': ['stableinterface']}

logger = Log()


def main(module=None):
    fields = {'primary_storage_serial_no': {'required': True, 'type': 'int'},
              'data': {'required': False, 'type': 'json'}}

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
            storageSystem = StorageSystem(module.params['primary_storage_serial_no'
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
