#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type
import json

DOCUMENTATION = \
    r'''
---
module: hv_storagereplication
author: Hitachi Vantara, LTD. VERSION 02.3.0
short_description: This module manages storage replication on Hitachi Storage System.
description:
     - The M(hv_storagereplication) module provides the following storage replication management operations
     - 1. Create TrueCopy storage replication.
     - 2. Resync TrueCopy storage replication.
     - 3. Split TrueCopy storage replication.
     - 4. Create Gad storage replication.
     - 5. Resync Gad storage replication.
     - 6. Split Gad storage replication.
     - 7. Testing Delete Storage Replication.
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
  repl_type:
    description:
      - set state to I(tc) for create and update true copy
      - set state to I(gad) for create and update gad
    type: str
    choices: [tc, gad]
  action_type:
    type: str
    choices: [resync, split]
  data:
    required: yes
    description:
      - data has the following properties
      - =================================================================
      - Create TrueCopy
      - =================================================================
      - C(primary_lun_id:) Mandatory input. int type. Primary Lun Id.
      - C(primary_ucp_system:) Mandatory input. string type. Primary ucp system.
      - C(primary_storage_serial_no :) Mandatory input. integer type. Primary serial number.
      - C(primary_host_group:) Mandatory input. array type. Primary HG details.
      - C(secondary_storage_pool_id:) Mandatory input. integer type. Pool Id.
      - C(secondary_ucp_system:) Mandatory input. string type. Secondary ucp system.
      - C(secondary_storage_serial_no:) Mandatory input. integer type. Secondary serial number.
      - C(secondary_storage_host_group:) Mandatory input. array type. Secondary HG details.
      - =================================================================
      - Resync TrueCopy
      - =================================================================
      - C(primary_storage_serial_no:) Mandatory input. integer type. Storage system serial number.
      - C(repl_pair_id:) Mandatory input. String type. Pool Id required to be update.
      - =================================================================
      - Split TrueCopy
      - =================================================================
      - C(primary_storage_serial_no:) Mandatory input. integer type. Storage system serial number.
      - C(repl_pair_id:) Mandatory input. String type. Pool Id required to be update.
      - =================================================================
       - Delete Storage Replication 
      - =================================================================
      - C(primary_storage_serial_no:) Mandatory input. integer type. Storage system serial number.
      - C(repl_pair_id:) Mandatory input. String type. Id of the replication pair to be deleted.
      - =================================================================
      
'''
EXAMPLES = \
    r'''
-
  name: Create TrueCopy
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - primary_lun_id: 1791
    - primary_storage_serial_no: 123456
    - secondary_storage_pool_id: 9
    - secondary_storage_serial_no: 123457
    - secondary_storage_host_group:
        - name: test-ansible-hg-tc
        - port: CL1-A
  tasks:
    - hv_storagereplication:
        state: present
        repl_type: tc
        data:
          primary_lun_id: '{{ primary_lun_id | default(None) }}'
          primary_storage_serial_no: '{{ primary_storage_serial_no | default(None) }}'
          secondary_storage_pool_id: '{{ secondary_storage_pool_id | default(None) }}'
          secondary_storage_serial_no: '{{ secondary_storage_serial_no | default(None) }}'
          secondary_storage_host_group: '{{ secondary_storage_host_group | default(None) }}'
      register: result
    - debug: var=result.storageReplication

-
  name: Resync TrueCopy
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - pvol_id: 121
    - primary_storage_serial_no: 12345
  tasks:
    - hv_storagereplication:
        state: present
        repl_type: tc
        action_type: resync
        data:
          primary_storage_serial_no: '{{ primary_storage_serial_no }}'
          pvol_id: '{{ pvol_id }}'
      register: result
    - debug: var=result.storageReplication

-
  name: Split TrueCopy
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - pvol_id: 121
    - primary_storage_serial_no: 12345
  tasks:
    - hv_storagereplication:
        state: present
        repl_type: tc
        action_type: split
        data:
          primary_storage_serial_no: '{{ primary_storage_serial_no }}'
          pvol_id: '{{ pvol_id }}'
      register: result
    - debug: var=result.storageReplication

-
  name: Create Gad
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - primary_lun_id: 1791
    - primary_storage_serial_no: 334566
    - quorum_disk_id: 1
    - secondary_storage_pool_id: 9
    - secondary_storage_serial_no: 123457
    - secondary_storage_host_group:
        - name: test-ansible-hg-tc
        - port: CL1-A
  tasks:
    - hv_storagereplication:
        state: present
        repl_type: gad
        data:
          primary_lun_id: '{{ primary_lun_id | default(None) }}'
          primary_storage_serial_no: '{{ primary_storage_serial_no | default(None) }}'
          quorum_disk_id: '{{ quorum_disk_id  | default(None) }}'
          secondary_storage_pool_id: '{{ secondary_storage_pool_id | default(None) }}'
          secondary_storage_serial_no: '{{ secondary_storage_serial_no | default(None) }}'
          secondary_storage_host_group: '{{ secondary_storage_host_group | default(None) }}'
      register: result
    - debug: var=result.storageReplication

-
  name: Resync Gad 
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - pvol_id: 121
    - primary_storage_serial_no: 12345
  tasks:
    - hv_storagereplication:
        state: present
        repl_type: gad
        action_type: resync
        data:
          primary_storage_serial_no: '{{ primary_storage_serial_no }}'
          pvol_id: '{{ pvol_id }}'
      register: result
    - debug: var=result.storageReplication

-
  name: Split Gad 
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - pvol_id: 121
    - primary_storage_serial_no: 12345
  tasks:
    - hv_storagereplication:
        state: present
        repl_type: gad
        action_type: split
        data:
          primary_storage_serial_no: '{{ primary_storage_serial_no }}'
          pvol_id: '{{ pvol_id }}'
      register: result
    - debug: var=result.storageReplication

-
  name: Delete TrueCopy
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - pvol_id: 121
    - primary_storage_serial_no: 12345
  tasks:
    - hv_storagereplication:
        state: absent
        repl_type: tc
        data:
          pvol_id: '{{ pvol_id }}'
          primary_storage_serial_no: '{{ primary_storage_serial_no }}'
      register: result
    - debug: var=result

-
  name: Delete GAD 
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - pvol_id: 121
    - primary_storage_serial_no: 12345
  tasks:
    - hv_storagereplication:
        state: absent
        repl_type: gad
        data:
          pvol_id: '{{ pvol_id }}'
          primary_storage_serial_no: '{{ primary_storage_serial_no }}'
      register: result
    - debug: var=result

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
import ansible_collections.hitachi.storage.plugins.module_utils.hv_storagereplication_runner as runner
ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'supported_by': 'certified',
                    'status': ['stableinterface']}

logger = Log()


def main(module=None):
    fields = {'primary_storage_serial_no': {'required': False, 'type': 'int'},
              'repl_type': {'required': True, 'type': 'str'},
              'action_type': {'required': False, 'type': 'str'},
              'state': {'default': 'present', 'choices': ['present', 'absent']}, 'data': {'required': False, 'type': 'json'}}
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
            data = json.loads(module.params['data'])
            storageSystem = StorageSystem(data.get('primary_storage_serial_no'))
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
