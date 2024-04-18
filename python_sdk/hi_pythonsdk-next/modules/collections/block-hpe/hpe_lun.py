#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hewlett Packard Enterprise Development LP ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'supported_by': 'certified',
                    'status': ['stableinterface']}

DOCUMENTATION = \
    r'''
---
module: hpe_lun
short_description: This module manages LUN on HPE XP Storage System.
description:
     - The M(hpe_lun) module provides the following LUN management operations.
     - 1. Create LUN on dynamic pool.
     - 2. Create LUN on parity group.
     - 3. Create multiple luns on dynamic pool.
     - 4. Create multiple luns with count.
     - 5. Expand LUN.
     - 6. Delete LUN.

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
  state:
    description:
      - set state to I(present) for create and update LUN
      - set state to I(absent) for delete LUN
    type: str
    default: present
    choices: [present, absent]
  data:
    required: yes
    description:
      - data has the following properties
      - =================================================================
      - Create LUN in THP
      - =================================================================
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(lun:) Optional input. integer type. LUN id of the newly created LUN. Supported format can be decimal or HEX.  
        If not provided, the first free LDEV ID will automatically be selected.
      - C(pool_id :) Optional input. Integer type. THP pool id present on the storage. Required only for new LUN.
      - C(size:) Optional input. String type. LUN size, user wants to create. Required only for new LUN.
      - C(name:) Optional. String type. New name of the new/existing LUN.
      - C(cap_saving:) Optional. String type.Valid values compression,deduplication and disable (default).
      - =================================================================
      - Create LUN in Parity group
      - =================================================================
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(lun:) Optional input. integer type. Supported format can be decimal or HEX. LUN id of the newly created LUN. 
        If not provided, the first free LDEV ID will automatically be selected.
      - C(parity_group :) Optional input. String type. Parity group present on the storage. Required only for new LUN.
      - C(size:) Optional input. String type. LUN size, user wants to create. Required only for new LUN.
      - C(name:) Optional. String type. New name of the new/existing LUN.
      - =================================================================
      - =================================================================
      - Create multiple luns on THP pool
      - =================================================================
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(luns:) Mandatory input. integer type. Supported format can be decimal or HEX. LUN id of the newly created LUN.
      - C(pool_id :) Optional input. Integer type. THP pool id present on the storage. Required only for new LUN.
      - C(size:) Optional input . String type. LUN size, user wants to create. Required only for new LUN.
      - C(name:) Optional. String type. New name of the new/existing LUN.
      - C(cap_saving:) Optional. String type.Valid values compression,deduplication and disable (default).
      - =================================================================
      - =================================================================
      - Create multiple luns on THP pool with count
      - =================================================================
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(count:) Mandatory input. Integer type. Number of the luns to be created.
      - C(pool_id :) Mandatory input. Integer type. THP pool id present on the storage.
      - C(size:) Mandatory input. String type. LUN size, user wants to create.
      - C(cap_saving:) Optional. String type.Valid values compression,deduplication and disable (default).
      - =================================================================
      - Expand LUN
      - =================================================================
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(luns:) Mandatory input. integer type. Supported format can be decimal or HEX. LUN id of the luns to be expanded.
      - C(size_gb:) Mandatory input. Integer type. Additional size of the LUN to be expanded.
      - C(cap_saving:) Optional. String type.Valid values compression,deduplication and disable (default).
      - =================================================================
      - =================================================================
      - Delete LUN
      - =================================================================
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(luns:) Mandatory input. LUN id of the luns to be deleted.Supported format can be decimal or HEX.
      - C(name:) Optional. String type. Name of the LUN to be deleted. Ignored if luns value is provided. Operation is 
        aborted if more than 1 LUN with matching name is found.
      - =================================================================
      - =================================================================


'''

EXAMPLES = \
    r'''
- name: Testing Create LUN In THP
  hosts: localhost
  collections:
    - hpe.xp_storage
  gather_facts: false
  vars:
    - pool_id: 27
    - size: 0.07GB
    - storage_serial: 123456
    - lun: 1416
    - name: AnsiJUNE
  tasks:
    - hpe_lun:
        state: present
        storage_serial: '{{ storage_serial }}'
        data:
          storage_pool:
            id: '{{ pool_id  | default(None) }}'
          name: '{{ name  | default(None) }}'
          size: '{{ size | default(None)}}'
          lun: '{{ lun | default(None) }}'
          cap_saving: '{{ cap_saving | default(None) }}'
      register: result
    - debug: var=result

- name: Testing Create LUN in THP when LUN ID given in Hexadecimal form
  hosts: localhost
  collections:
    - hpe.xp_storage
  gather_facts: false
  vars:
    - pool_id: 27
    - size: 0.07GB
    - storage_serial: 123456
    - lun: 00:06:40
    - name: TestJune16
  tasks:
    - hpe_lun:
        state: present
        storage_serial: '{{ storage_serial }}'
        data:
          storage_pool:
            id: '{{ pool_id  | default(None) }}'
          name: '{{ name  | default(None) }}'
          size: '{{ size | default(None)}}'
          lun: '{{ lun | default(None) }}'
          cap_saving: '{{ cap_saving | default(None) }}'
      register: result
    - debug: var=result


- name: Create LUN In PG
  hosts: localhost
  collections:
    - hpe.xp_storage
  gather_facts: false
  vars:
    - parity_group: 1-1
    - size: 1GB
    - lun: 6271
    - storage_serial: 123456
    - name: ansidec26
  tasks:
    - hpe_lun:
        state: present
        storage_serial: '{{ storage_serial }}'
        data:
          parity_group: '{{ parity_group | default(None)}}'
          size: '{{ size | default(None) }}'
          name: '{{ name  | default(None) }}'
          lun: '{{ lun | default(None) }}'
      register: result
    - debug: var=result

- name: Testing Create Multiple LUN with ID In THP
  hosts: localhost
  gather_facts: false
  vars:
    - pool_id: 6
    - size: 0.08GB
    - storage_serial: 123456
    - luns:
      - 1577
      - 1578
  tasks:
    - hpe_lun:
        state: present
        storage_serial: '{{ storage_serial }}'
        data:
          storage_pool:
          id: '{{ pool_id | default(None)}}'
          luns: '{{ item }}'
          size: '{{ size | default(None)}}'
          name: '{{ name | default(None) }}'
          cap_saving: '{{ cap_saving | default(None) }}'
      with_items: '{{ luns }}'
      register: result
    - debug: var=result

- name: Testing Delete LUN
  hosts: localhost
  collections:
    - hpe.xp_storage
  gather_facts: false
  vars:
    - luns:
    - name:  delete_lun_byName
    - storage_serial: 123456
  tasks:
    - hpe_lun:
        state: absent
        storage_serial: '{{ storage_serial }}'
        data:
          luns: '{{ item }}'
          name: '{{ name | default(None) }}'
      with_items: '{{ luns }}'
      register: result
    - debug: var=result

- name: Testing Create Multiple LUN with count In THP
  hosts: localhost
  collections:
    - hpe.xp_storage
  gather_facts: false
  vars:
    - pool_id: 6
    - size: 0.09GB
    - storage_serial: 123456
    - count: 2
  tasks:
    - hpe_lun:
        state: present
        storage_serial: '{{ storage_serial }}'
        data:
          storage_pool:
            id: '{{ pool_id }}'
          size: '{{ size }}'
          cap_saving: '{{ cap_saving | default(None) }}'
          with_sequence:  end={{count}} start=1
      register: result
    - debug: var=result

- name: Testing Expand LUN
  hosts: localhost
  collections:
    - hpe.xp_storage
  gather_facts: false
  vars:
    - storage_serial: 123456
    - luns: 836
    - size_gb: 3
  tasks:
    - hpe_lun:
        state: present
        storage_serial: '{{ storage_serial }}'
        data:
         luns: '{{ luns }}'
         size: '{{size_gb}}'
         cap_saving: '{{ cap_saving | default(None) }}'
      register: result
    - debug: var=result.lun

- name: Testing Expand LUN when LUN ID given in Hexadecimal form
  hosts: localhost
  collections:
    - hpe.xp_storage
  gather_facts: false
  vars:
    - storage_serial: 123456
    - luns: 00:05:87
    - size_gb: 7
  tasks:
    - hpe_lun:
        state: present
        storage_serial: '{{ storage_serial }}'
        data:
          luns: '{{ luns }}'
          size: '{{size_gb}}'
          cap_saving: '{{ cap_saving | default(None) }}'
      register: result
    - debug: var=result.lun

-
  name: Testing Create Multiple LUN with ID In THP
  hosts: localhost
  collections:
    - hpe.xp_storage
  gather_facts: false
  vars:
    - pool_id: 6
    - size: 0.09GB
    - storage_serial: 415056
    - luns:
      - 8019
      - 8018
  tasks:
    - hpe_lun:
        state: present
        storage_serial: '{{ storage_serial }}'
        data:
          storage_pool:
            id: '{{ pool_id | default(None) }}'
          luns: '{{ item }}'
          size: '{{ size | default(None) }}'
          name: '{{ name  | default(None) }}'
          cap_saving: '{{ cap_saving | default(None) }}'
      with_items: '{{ luns }}'
      register: result
    - debug: var=result

    '''

RETURN = r'''
'''

import json
import re

import ansible_collections.hpe.xp_storage.plugins.module_utils.hv_lun_runner as runner
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_infra import StorageSystem, \
    StorageSystemManager
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_infra import Utils
try:
    from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_logger import MessageID
    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_log import Log, \
    HiException

logger = Log()


def main(module=None):
    fields = {
        'storage_serial': {'required': True, 'type': 'int'},
        'sku': {'required': False, 'type': 'str'},
        'state': {'default': 'present', 'choices': ['present', 'absent']},
        'data': {'required': True, 'type': 'json'}}

    if module is None:
        module = AnsibleModule(argument_spec=fields)

    try:
        runner.runPlaybook(module)
    except HiException as ex:
        if HAS_MESSAGE_ID:
            logger.writeAMException(MessageID.ERR_OPERATION_LUN)
        else:
            logger.writeAMException("0x0000")
        module.fail_json(msg=ex.format())
    except Exception as ex:
        try:
            storageSystem = StorageSystem(module.params['storage_serial'])
            if storageSystem.isSessionNotFound(ex.message):
                StorageSystemManager.addStorgeSystemByJson()
                runner.runPlaybook(module)
            else:
                module.fail_json(msg=ex.message)
        except Exception as ex2:
            module.fail_json(msg=ex.message + '. ' + ex2.message)


if __name__ == '__main__':
    main()
