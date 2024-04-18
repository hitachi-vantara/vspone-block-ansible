#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = \
    r'''
---
module: hv_storagepool
author: Hitachi Vantara, LTD. VERSION 02.3.0
short_description: This module manages storage pool on Hitachi Storage System.
description:
     - The M(hv_storagepool) module provides the following storage pool management operations
     - 1. create storage pool.
version_added: '02.9.0'
requirements:
options:
  collections:
    description:
      - Ansible collections name for Hitachi storage modules 
    type: string
    required: yes
    default: hitachi.storage
  state:
    description:
      - set state to I(present) for create and update host group
      - set state to I(absent) for delete host group
    type: str
    default: present
    choices: [present, absent]
  data:
    required: yes
    description:
      - data has the following properties
      - =================================================================
      - Add storage pool
      - =================================================================
      - C(storage_pool_name:) Mandatory input. String type. Storage pool name.
      - C(depletion_threshold_rate:) Mandatory input. integer type. Depletion threshold rate.
      - C(type :) Optional. string type. Valid values
      - 0 [HDP]
      - 1 [HDT]
      - 2 [HRT]
      - 3 [HTI]
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(warningThresholdRate:) Mandatory input. integer type. Warning threshold rate.
      - =================================================================
      - Delete Storage Pool
      - =================================================================
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(storage_pool_id:) Mandatory input. String type. Id of the Storage pool to be deleted.
      - =================================================================
      - Update Storage Pool
      - =================================================================
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(storage_pool_id:) Mandatory input. String type. Id of the Storage pool to be updated.
      - C(pool_volumes:) Mandatory input. array type. Volumes details to update capacity and parity group.
      - =================================================================
      - Update Storage Pool deduplication
      - =================================================================
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(storage_pool_id:) Mandatory input. String type. Id of the Storage pool to be updated.
      - C(enable_deduplication:) Mandatory input. String type. Deduplication status of the Storage pool to be updated.
      - =================================================================
'''
EXAMPLES = \
    r'''
- name: Adding Dynamic Pool
  hosts: localhost
  gather_facts: false
  vars:
    - storage_pool_name: test_pool
    - type: HDP
    - depletion_threshold_rate: 80
    - warningThresholdRate: 70
    - storage_serial: 12345
  tasks:
    - hv_storagepool:
        state: present
        storage_serial: '{{ storage_serial }}'
        data:
         storage_pool_name: '{{ storage_pool_name | default(omit)}}'
         type: '{{ type | default(None)}}'
         depletion_threshold_rate: '{{ depletion_threshold_rate }}'
         warningThresholdRate: '{{ warningThresholdRate | default(None)}}'
      register: result
    - debug: var=result.dynamicPools
-
  name: Delete Dynamic Pool
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - pool_id: 1
    - storage_serial: 12345
  tasks:
    - hv_storagepool:
        state: absent
        storage_serial: '{{ storage_serial }}'
        data:
          pool_id: '{{ pool_id }}'
      register: result
    - debug: var=result

-
  name: Update Dynamic Pool deduplication
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - enable_deduplication: true
    - pool_id: 1
    - storage_serial: 12345
  tasks:
    - hv_storagepool:
        state: present
        storage_serial: '{{ storage_serial }}'
        data:
          enable_deduplication: '{{ enable_deduplication }}'
          pool_id: '{{ pool_id | default(omit) }}'
      register: result
    - debug: var=result.dynamicPool

-
  name: Update Dynamic Pool 
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - pool_volumes: 
        capacity: 10GB
        parityGroupId: 1-1
    - pool_id: 1
    - storage_serial: 12345
  tasks:
    - hv_storagepool:
        state: present
        storage_serial: '{{ storage_serial }}'
        data:
          pool_id: '{{ pool_id | default(omit) }}'
          pool_volumes: '{{ pool_volumes }}'
      register: result
    - debug: var=result.dynamicPool

-
'''
RETURN = """
"""

try:
    from ansible_collections.hitachi.storage.plugins.module_utils.hv_logger import MessageID
    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False

from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log, \
    HiException
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystem, \
    StorageSystemManager
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.hitachi.storage.plugins.module_utils.hv_storagepool_runner as runner
ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'supported_by': 'certified',
                    'status': ['stableinterface']}

logger = Log()


def main(module=None):
    fields = {'storage_serial': {'required': True, 'type': 'int'},
              'state': {'default': 'present', 'choices': ['present', 'absent']}, 
              'data': {'required': False, 'type': 'json'}}
    if module is None:
        module = AnsibleModule(argument_spec=fields)

    try:
        runner.runPlaybook(module)
    except HiException as ex:
        if HAS_MESSAGE_ID:
            logger.writeAMException(MessageID.ERR_CREATE_DYNAMICPOOL)
        else:
            logger.writeAMException("0x000000")
        module.fail_json(msg=ex.format())
    except Exception as ex:
        try:
            storageSystem = StorageSystem(module.params['storage_serial'])
            if storageSystem.isSessionNotFound(ex.message):

                # always do one retry in case the webservice was restarted

                StorageSystemManager.addStorgeSystemByJson()
                runner.runPlaybook(module)
            else:
                module.fail_json(msg=ex.message)
        except Exception as ex2:
            module.fail_json(msg=ex.message + '. ' + ex2.message)


if __name__ == '__main__':
    main()
