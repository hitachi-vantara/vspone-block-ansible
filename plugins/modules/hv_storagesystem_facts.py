#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


__metaclass__ = type


DOCUMENTATION = \
    r'''
---
module: hv_storagesystem_facts
short_description: This module provides information about the added Hitachi storage system.
description:
     - The M(hv_storagesystem_facts) module provides the Get Storage System operation

version_added: '02.9.0'
author:
  - Hitachi Vantara, LTD. VERSION 02.3.0
requirements:
options:
  collections:
    description:
      - Ansible collections name for Hitachi storage modules 
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
      - C(ucpadvisor_ansible_vault_user:) Mandatory input. String type. UCPA user name.
      - C(ucpadvisor_ansible_vault_secret:) Mandatory input. String type. UCPA password in clear text.
      - =================================================================
    default: n/a
  data:
    required: no
    description:
      - data has the following properties
      - =================================================================
      - Get Storage System
      - =================================================================
      - C(query:) Optional input.List of string value with valid input value
      -      1. pools
      -      2. ports
      -      3. quorumdisks
      -      4. journalPools
      -      5. freeLogicalUnitList
      - =================================================================
'''

EXAMPLES = \
    r'''
- name: Testing Get Storage System
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: vars.yml
  vars:
    - ucp_name: UCP-CI-12144
    - storage_serial: 123456
    - query:
      - quorumdisks
      - pools
  tasks:
    - hv_storagesystem_facts:

        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
          query: '{{ query | default(None) }}'

        ucp_advisor_info:
          address: "{{ucpadvisor_address}}"
          username: "{{ucpadvisor_ansible_vault_user}}"
          password: "{{ucpadvisor_ansible_vault_secret}}"

      register: result
    - debug: var=result.storageSystem

'''

RETURN = r'''
'''

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
import ansible_collections.hitachi.storage.plugins.module_utils.hv_storagesystem_facts_runner as runner

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'supported_by': 'certified',
                    'status': ['stableinterface']}

logger = Log()


def main(module=None):
    fields = {
        'storage_system_info': {'required': True, 'type': 'json'},
        'ucp_advisor_info': {'required': True, 'type': 'json'},
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

            # FIXME.sng - add write debug here

            storageSystem = StorageSystem(module.params['storage_serial'
                                                        ])
            if storageSystem.isSessionNotFound(ex.message):

                # always do one retry in case the webservice was restarted
                # writeMsg("perform auto re-register")
                # storageInfo={}

                StorageSystemManager.addStorgeSystemByJson()
                runner.runPlaybook(module)
            else:
                module.fail_json(msg=str(ex))
        except Exception as ex2:
            module.fail_json(msg=ex.message + '. ' + ex2.message)


if __name__ == '__main__':
    main()
