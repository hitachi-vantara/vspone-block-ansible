#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hewlett Packard Enterprise Development LP ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = \
    r'''
---
module: hpe_storagesystem_facts
short_description: This module provides information about the added HPE XP storage system.
description:
     - The M(hpe_storagesystem_facts) module provides the following operations
     - 1. Get Storage System

version_added: '02.9.0'
author:
  - Hewlett Packard Enterprise Development LP. VERSION 02.3.0.7
requirements:
options:
  collections:
    description:
      - Ansible collections name for HPE XP storage modules 
    type: string
    required: yes
    default: hpe.xp_storage
  data:
    required: yes
    description:
      - data has the following properties
      - =================================================================
      - Get Storage System
      - =================================================================
      - C(storage_serial:) Mandatory input. Storage system serial number.
      - C(query:) Optional input.List of string value with valid input value
      -      1. pools
      -      2. ports
      -      3. quorumdisks
      -      4. journalPool
      -      5. nextFreeGADConsistencyGroupId
      -      6. nextFreeHTIConsistencyGroupId
      -      7. nextFreeTCConsistencyGroupId
      -      8. nextFreeURConsistencyGroupId
      -      9. freeLogicalUnitList
      - =================================================================
'''

EXAMPLES = \
    r'''
- name: Testing Get Storage System
  hosts: localhost
  collections:
    - hpe.xp_storage
  gather_facts: false
  vars:
    - storage_serial: 123456
    - query:
      - nextFreeHTIConsistencyGroupId
      - quorumdisks
  tasks:
    - hpe_storagesystem_facts:
        storage_serial: '{{ storage_serial }}'
        query: '{{ query | default(None) }}'
      register: result
    - debug: var=result.storageSystem

'''

RETURN = r'''
'''

try:
    from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_messages import MessageID
    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_log import Log, \
    HiException
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_infra import StorageSystem
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_infra import StorageSystemManager
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.hpe.xp_storage.plugins.module_utils.hv_storagesystem_facts_runner as runner

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'supported_by': 'certified',
                    'status': ['stableinterface']}

logger = Log()


def main(module=None):
    fields = {'storage_serial': {'required': True, 'type': 'int'},
              'query': {
        'required': False,
        'type': 'list',
        'elements': 'str',
        'default': [],
    }}

    if module is None:
        module = AnsibleModule(argument_spec=fields)

    try:
        runner.runPlaybook(module)
    except HiException as ex:
        if HAS_MESSAGE_ID:
            logger.writeAMException(MessageID.ERR_AddRAIDStorageDevice)
        else:
            logger.writeAMException('0x0000')
        module.fail_json(msg=ex.format())
    except Exception as ex:
        try:

            # writeNameValue("Exception={}",ex)
            # writeNameValue("Exception={}",ex.message)

            storageSystem = StorageSystem(module.params['storage_serial'
                                                        ])
            if storageSystem.isSessionNotFound(ex.message):

                # always do one retry in case the webservice was restarted
                # writeMsg("perform auto re-register")
                # storageInfo={}

                StorageSystemManager.addStorgeSystemByJson()
                runner.runPlaybook(module)
            else:
                module.fail_json(msg=ex.message)
        except Exception as ex2:
            module.fail_json(msg=ex.message + '. ' + ex2.message)


if __name__ == '__main__':
    main()
