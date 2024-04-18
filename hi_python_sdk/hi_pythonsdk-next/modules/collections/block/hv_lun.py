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
module: hv_lun
short_description: This module manages LUN on Hitachi Storage System.
description:
     - The M(hv_lun) module provides the following LUN management operations.
     - 1. Create LUN on dynamic pool.
     - 2. Create LUN on parity group.
     - 3. Create multiple luns on dynamic pool.
     - 4. Create multiple luns with count.
     - 5. Expand LUN.
     - 6. Delete LUN.

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
  state:
    description:
      - set state to I(present) for create and update LUN
      - set state to I(absent) for delete LUN
    type: str
    default: present
    choices: [present, absent]
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
  spec:
    required: yes
    description:
      - data has the following properties
      - =================================================================
      - Create LUN in DP
      - =================================================================
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(ucp_name:) Mandatory input. String type. UCP system name.
      - C(lun:) Optional input. integer type. LUN id of the newly created LUN. Supported format can be decimal or HEX.  
        If not provided, the first free LDEV ID will automatically be selected.
      - C(pool_id :) Optional input. Integer type. Dynamic pool id present on the storage. Required only for new LUN.
      - C(size:) Optional input. String type. LUN size can be 3, 3GB or 3TB, default is MB. Required only for new LUN.
      - C(name:) Optional. String type. New name of the new/existing LUN.
      - C(capacity_saving:) Optional. String type.Valid values compression,deduplication and disable (default).
      - =================================================================
      - Create LUN in Parity group
      - =================================================================
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(ucp_name:) Mandatory input. String type. UCP system name.
      - C(lun:) Optional input. integer type. Supported format can be decimal or HEX. LUN id of the newly created LUN. 
        If not provided, the first free LDEV ID will automatically be selected.
      - C(parity_group :) Optional input. String type. Parity group present on the storage. Required only for new LUN.
      - C(size:) Optional input. String type. LUN size can be 3, 3GB or 3TB, default is MB.  Required only for new LUN.
      - C(name:) Optional. String type. New name of the new/existing LUN.
      - =================================================================
      - =================================================================
      - Create multiple luns on dynamic pool
      - =================================================================
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(ucp_name:) Mandatory input. String type. UCP system name.
      - C(luns:) Mandatory input. integer type. Supported format can be decimal or HEX. LUN id of the newly created LUN.
      - C(pool_id :) Optional input. Integer type. Dynamic pool id present on the storage. Required only for new LUN.
      - C(size:) Optional input . String type. LUN size can be 3, 3GB or 3TB, default is MB. Required only for new LUN.
      - C(name:) Optional. String type. New name of the new/existing LUN.
      - C(capacity_saving:) Optional. String type.Valid values compression,deduplication and disable (default).
      - =================================================================
      - =================================================================
      - Create multiple luns on dynamic pool with count
      - =================================================================
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(ucp_name:) Mandatory input. String type. UCP system name.
      - C(count:) Mandatory input. Integer type. Number of the luns to be created.
      - C(pool_id :) Mandatory input. Integer type. Dynamic pool id present on the storage.
      - C(size:) Mandatory input. String type. LUN size can be 3, 3GB or 3TB, default is MB.
      - C(capacity_saving:) Optional. String type.Valid values compression,deduplication and disable (default).
      - =================================================================
      - Expand LUN
      - =================================================================
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(ucp_name:) Mandatory input. String type. UCP system name.
      - C(luns:) Mandatory input. integer type. Supported format can be decimal or HEX. LUN id of the luns to be expanded.
      - C(size_gb:) Mandatory input. Integer type. New size of the LUN to be expanded, can be 3, 3GB or 3TB, default is MB. It should be more than existing LUN size.
      - C(capacity_saving:) Optional. String type.Valid values compression,deduplication and disable (default).
      - =================================================================
      - =================================================================
      - Delete LUN
      - =================================================================
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(ucp_name:) Mandatory input. String type. UCP system name.
      - C(luns:) Mandatory input. LUN id of the luns to be deleted.Supported format can be decimal or HEX.
      - C(name:) Optional. String type. Name of the LUN to be deleted. Ignored if luns value is provided. Operation is \
        aborted if more than 1 LUN with matching name is found.
      - =================================================================
      - =================================================================


'''

EXAMPLES = \
    r'''
- name: Testing Create LUN In DP
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: vars.yml
  vars:
    - storage_serial: 123456
    - ucp_name: UCP-CI-12345
    - pool_id: 27
    - size: 10.07GB
    - lun: 1416
    - name: AnsiJUNE
  tasks:
    - hv_lun:
        state: present
        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
        ucp_advisor_info:
          address: '{{ ucpadvisor_address }}'
          username: '{{ ucpadvisor_username }}'
          password: '{{ ucpadvisor_password }}'
        spec:
          pool_id: '{{ pool_id  | default(None) }}'
          name: '{{ name  | default(None) }}'
          size: '{{ size | default(None)}}'
          lun: '{{ lun | default(None) }}'
          capacity_saving: '{{ capacity_saving: | default(None) }}'
      register: result
    - debug: var=result

- name: Testing Create LUN In DP when LUN ID given in Hexadecimal form
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: vars.yml
  vars:
    - storage_serial: 123456
    - ucp_name: UCP-CI-12345
    - pool_id: 27
    - size: 10.07GB
    - lun: 00:06:40
    - name: TestJune16
  tasks:
    - hv_lun:
        state: present
        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
        ucp_advisor_info:
          address: '{{ ucpadvisor_address }}'
          username: '{{ ucpadvisor_username }}'
          password: '{{ ucpadvisor_password }}'
        spec:
          pool_id: '{{ pool_id  | default(None) }}'
          name: '{{ name  | default(None) }}'
          size: '{{ size | default(None)}}'
          lun: '{{ lun | default(None) }}'
          capacity_saving: '{{ capacity_saving: | default(None) }}'
      register: result
    - debug: var=result


- name: Create LUN In PG
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: vars.yml
  vars:
    - storage_serial: 123456
    - ucp_name: UCP-CI-12345
    - parity_group: 1-1
    - size: 1GB
    - lun: 6271
    - name: ansidec26
  tasks:
    - hv_lun:
        state: present
        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
        ucp_advisor_info:
          address: '{{ ucpadvisor_address }}'
          username: '{{ ucpadvisor_username }}'
          password: '{{ ucpadvisor_password }}'
        spec:
          parity_group: '{{ parity_group | default(None)}}'
          size: '{{ size | default(None) }}'
          name: '{{ name  | default(None) }}'
          lun: '{{ lun | default(None) }}'
      register: result
    - debug: var=result

- name: Testing Create Multiple LUN with ID In DP
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: vars.yml
  vars:
    - storage_serial: 123456
    - ucp_name: UCP-CI-12345
    - pool_id: 6
    - size: 10.08GB
    - luns:
      - 1577
      - 1578
  tasks:
    - hv_lun:
        state: present
        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
        ucp_advisor_info:
          address: '{{ ucpadvisor_address }}'
          username: '{{ ucpadvisor_username }}'
          password: '{{ ucpadvisor_password }}'
        spec:
          pool_id: '{{ pool_id  | default(None) }}'
          luns: '{{ item }}'
          size: '{{ size | default(None)}}'
          name: '{{ name | default(None) }}'
          capacity_saving: '{{ capacity_saving: | default(None) }}'
      with_items: '{{ luns }}'
      register: result
    - debug: var=result

- name: Testing Delete LUN
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: vars.yml
  vars:
    - storage_serial: 123456
    - ucp_name: UCP-CI-12345
    - luns:
    - name:  delete_lun_byName
  tasks:
    - hv_lun:
        state: absent
        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
        ucp_advisor_info:
          address: '{{ ucpadvisor_address }}'
          username: '{{ ucpadvisor_username }}'
          password: '{{ ucpadvisor_password }}'
        spec:
          luns: '{{ item }}'
          name: '{{ name | default(None) }}'
      with_items: '{{ luns }}'
      register: result
    - debug: var=result

- name: Testing Create Multiple LUN with count In DP
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: vars.yml
  vars:
    - storage_serial: 123456
    - ucp_name: UCP-CI-12345
    - pool_id: 6
    - size: 10.09GB
    - count: 2
  tasks:
    - hv_lun:
        state: present
        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
        ucp_advisor_info:
          address: '{{ ucpadvisor_address }}'
          username: '{{ ucpadvisor_username }}'
          password: '{{ ucpadvisor_password }}'
        spec:
          pool_id: '{{ pool_id  | default(None) }}'
          size: '{{ size }}'
          capacity_saving: '{{ capacity_saving: | default(None) }}'
          with_sequence:  end={{count}} start=1
      register: result
    - debug: var=result

- name: Testing Expand LUN
  hosts: localhost
  gather_facts: false
  pre_tasks:
    - include_vars: vars.yml
  vars:
    - storage_serial: 123456
    - ucp_name: UCP-CI-12345
    - luns: 836
    - size_gb: 30
  tasks:
    - hv_lun:
        state: present
        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
        ucp_advisor_info:
          address: '{{ ucpadvisor_address }}'
          username: '{{ ucpadvisor_username }}'
          password: '{{ ucpadvisor_password }}'
        spec:
         luns: '{{ luns }}'
         size: '{{size_gb}}'
         capacity_saving: '{{ capacity_saving: | default(None) }}'
      register: result
    - debug: var=result.lun

- name: Testing Expand LUN when LUN ID given in Hexadecimal form
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: vars.yml
  vars:
    - storage_serial: 123456
    - ucp_name: UCP-CI-12345
    - luns: 00:05:87
    - size_gb: 70
  tasks:
    - hv_lun:
        state: present
        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
        ucp_advisor_info:
          address: '{{ ucpadvisor_address }}'
          username: '{{ ucpadvisor_username }}'
          password: '{{ ucpadvisor_password }}'
        spec:
          luns: '{{ luns }}'
          size: '{{size_gb}}'
          capacity_saving: '{{ capacity_saving: | default(None) }}'
      register: result
    - debug: var=result.lun

-
  name: Testing Create Multiple LUN with ID In THP
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: vars.yml
  vars:
    - storage_serial: 123456
    - ucp_name: UCP-CI-12345
    - pool_id: 6
    - size: 0.09GB
    - luns:
      - 8019
      - 8018
  tasks:
    - hpe_lun:
        state: present
        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
        ucp_advisor_info:
          address: '{{ ucpadvisor_address }}'
          username: '{{ ucpadvisor_username }}'
          password: '{{ ucpadvisor_password }}'
        spec:
          pool_id: '{{ pool_id  | default(None) }}'
          luns: '{{ item }}'
          size: '{{ size | default(None) }}'
          name: '{{ name  | default(None) }}'
          capacity_saving: '{{ capacity_saving: | default(None) }}'
      with_items: '{{ luns }}'
      register: result
    - debug: var=result

    '''

RETURN = r'''
'''

import json
import re

import ansible_collections.hitachi.storage.plugins.module_utils.hv_lun_runner as runner
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
    fields = {
        'sku': {'required': False, 'type': 'str'},
        'state': {'default': 'present', 'choices': ['present', 'absent']},
        'storage_system_info': {'required': True, 'type': 'json'},
        'ucp_advisor_info': {'required': True, 'type': 'json'},
        'spec': {'required': True, 'type': 'json'},
    }

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
        module.fail_json(msg=ex.message)

if __name__ == '__main__':
    main()
