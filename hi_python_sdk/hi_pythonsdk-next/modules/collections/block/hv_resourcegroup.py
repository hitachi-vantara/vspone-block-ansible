#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


__metaclass__ = type

DOCUMENTATION = \
    r'''
---
module: hv_resourcegroup
author: Hitachi Vantara, LTD. VERSION 02.3.0
short_description: This module manages resource group on Hitachi Storage System.
description:
     - The M(hv_resourcegroup) module provides the following resource group management operations
     - 1. Add HG to resource group.
     - 2. Delete HG from resource group.
     - 3. Add Lun to resource group.
     - 4. Delete Lun from resource group.
     - 5. Add Port to resource group.
     - 6. Delete Port from resource group.
     - 7. Add Parity Group to resource group.
     - 8. Delete Parity Group from resource group.
     - 8. Add Pool to resource group.
     - 8. Delete Pool from resource group.
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
      - Add HG
      - =================================================================
      - C(host_group:) Mandatory input. array type.HG details.
      - C(storage_serial:) Mandatory input. Storage system serial number.
      - =================================================================
      - Delete HG
      - =================================================================
      - C(host_group:) Mandatory input. array type.HG details.
      - C(storage_serial:) Mandatory input. Storage system serial number.
      - =================================================================
      - Add Luns
      - =================================================================
      - C(lun_ids:) Mandatory input. array type.Lun id array.
      - C(storage_serial:) Mandatory input. Storage system serial number.
      - =================================================================
      - Delete Luns
      - =================================================================
      - C(lun_ids:) Mandatory input. array type.Lun id array.
      - C(storage_serial:) Mandatory input. Storage system serial number.
      - =================================================================
      - Add Ports
      - =================================================================
      - C(ports_ids:) Mandatory input. array type.Port id array.
      - C(storage_serial:) Mandatory input. Storage system serial number.
      - =================================================================
      - Delete Ports
      - =================================================================
      - C(port_ids:) Mandatory input. array type.Port id array.
      - C(storage_serial:) Mandatory input. Storage system serial number.
      - =================================================================
      - Add Parity Group
      - C(parity_group_ids:) Mandatory input. array type.Parity Group id array.
      - C(storage_serial:) Mandatory input. Storage system serial number.
      - =================================================================
      - Delete Parity Group
      - =================================================================
      - C(parity_group_ids:) Mandatory input. array type.Parity Group id array.
      - C(storage_serial:) Mandatory input. Storage system serial number.
      - =================================================================
      - Add Pools
      - =================================================================
      - C(pool_ids:) Mandatory input. array type.Pool id array.
      - C(storage_serial:) Mandatory input. Storage system serial number.
      - =================================================================
      - Delete Pools
      - =================================================================
      - C(pool_ids:) Mandatory input. array type.Pool id array.
      - C(storage_serial:) Mandatory input. Storage system serial number.
      - =================================================================
      
      
'''
EXAMPLES = \
    r'''
-
  name: Add Host Group to resource group
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - primary_storage_serial_no: 123456
    - host_group:
        - name: test-ansible-hg-tc
        - port: CL1-A
    - secondary_storage_serial_no: 123457
  tasks:
    - hv_resourcegroup:
        state: present
        primary_storage_serial_no: '{{ primary_storage_serial_no | default(None) }}'
        data:
          host_group: '{{ host_group }}'
          secondary_storage_serial_no: '{{ secondary_storage_serial_no }}'
      register: result
    - debug: var=result.resourceGroup

-
  name: Delete Host Group from resource group
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - primary_storage_serial_no: 123456
    - host_group:
        - name: test-ansible-hg-tc
        - port: CL1-A
    - secondary_storage_serial_no: 123457
  tasks:
    - hv_resourcegroup:
        state: absent
        primary_storage_serial_no: '{{ primary_storage_serial_no | default(None) }}'
        data:
          host_group: '{{ host_group }}'
          secondary_storage_serial_no: '{{ secondary_storage_serial_no }}'
      register: result
    - debug: var=result

-
  name: Add Lun to resource group
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - primary_storage_serial_no: 123456
    - ldevId:
        - 121
    - secondary_storage_serial_no: 123457
  tasks:
    - hv_resourcegroup:
        state: present
        primary_storage_serial_no: '{{ primary_storage_serial_no | default(None) }}'
        data:
          ldevId: '{{ ldevId }}'
          secondary_storage_serial_no: '{{ secondary_storage_serial_no }}'
      register: result
    - debug: var=result.resourceGroup

-
  name: Delete Lun from resource group
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - primary_storage_serial_no: 123456
    - ldevId:
        - 121
    - secondary_storage_serial_no: 123457
  tasks:
    - hv_resourcegroup:
        state: absent
        primary_storage_serial_no: '{{ primary_storage_serial_no | default(None) }}'
        data:
          ldevId: '{{ ldevId }}'
          secondary_storage_serial_no: '{{ secondary_storage_serial_no }}'
      register: result
    - debug: var=result

-
  name: Add Port to resource group
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - primary_storage_serial_no: 123456
    - port:
        - CL1-A
    - secondary_storage_serial_no: 123457
  tasks:
    - hv_resourcegroup:
        state: present
        primary_storage_serial_no: '{{ primary_storage_serial_no | default(None) }}'
        data:
          port: '{{ port }}'
          secondary_storage_serial_no: '{{ secondary_storage_serial_no }}'
      register: result
    - debug: var=result.resourceGroup

-
  name: Delete Port from resource group
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars:
    - primary_storage_serial_no: 123456
    - port:
        - CL1-A
    - secondary_storage_serial_no: 123457
  tasks:
    - hv_resourcegroup:
        state: absent
        primary_storage_serial_no: '{{ primary_storage_serial_no | default(None) }}'
        data:
          port: '{{ port }}'
          secondary_storage_serial_no: '{{ secondary_storage_serial_no }}'
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
import ansible_collections.hitachi.storage.plugins.module_utils.hv_resourcegroup_runner as runner
ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'supported_by': 'certified',
                    'status': ['stableinterface']}

logger = Log()


def main(module=None):
    fields = {'primary_storage_serial_no': {'required': True, 'type': 'int'},
              'state': {'default': 'present', 'choices': ['present', 'absent']}, 'data': {'required': True, 'type': 'json'}}
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
            storageSystem = StorageSystem(module.params['primary_storage_serial_no'])
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
