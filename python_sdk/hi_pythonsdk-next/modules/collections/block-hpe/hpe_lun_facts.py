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
module: hpe_lun_facts
short_description: This module provides LUN information on the specified HPE XP storage system.
description:
     - The M(hpe_lun_facts) module provides the LUN information on the specified HPE XP storage system.
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
      - Getting LUN information
      - =================================================================
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(lun:) Optional input. LDEV ID in storage,supported format can be in decimal or HEX or Host LUN ID in canonical form.\
        If lun parameter is provided, it returns information of specified lun only. If the Host LUN ID is given in canonical\
        form, the LUN value must be prefixed with 'naa'. \
        Storage serial would be ignored and LUN details would be retrieved from any storage added to the current session
      - C(name:) Optional. String type. Name of the existing LUN.
      - C(max_count:) Optional. Integer type. This works along with the variable 'lun'. When specified, the next "max_count" number of\
        lun are displayed starting from LDEV ID specified by variable 'lun'
      - =================================================================
'''

EXAMPLES = \
    r'''

-
  name: Testing Get LUN in decimal
  hosts: localhost
  collections:
    - hpe.xp_storage
  gather_facts: false
  vars:
    - storage_serial: 12345
    - lun: 1395
    - max_count: 2
  tasks:
    - hpe_lun_facts:
        storage_serial: '{{ storage_serial | default(None) }}'
        data:
          lun: '{{ lun | default(None) }}'
          name: '{{ name | default(None) }}'
          max_count: '{{ max_count | default(None) }}'
      register: result
    - debug: var=result.luns
-
-
  name: Testing Get LUN in HEX
  hosts: localhost
  collections:
    - hpe.xp_storage
  gather_facts: false
  vars:
    - storage_serial: 12345
    - lun: 00:05:73
    - max_count: 2
  tasks:
    - hpe_lun_facts:
        storage_serial: '{{ storage_serial | default(None) }}'
        data:
          lun: '{{ lun | default(None) }}'
          name: '{{ name | default(None) }}'
          max_count: '{{ max_count | default(None) }}'
      register: result
    - debug: var=result.luns
-
-
  name: Testing Get LUN in canonical form
  hosts: localhost
  collections:
    - hpe.xp_storage
  gather_facts: false
  vars:
    - lun: naa.60060e80123ad00050403ad000000573
    - max_count: 2
  tasks:
    - hpe_lun_facts:
        storage_serial: '{{ storage_serial | default(None) }}'
        data:
          lun: '{{ lun | default(None) }}'
          name: '{{ name | default(None) }}'
          max_count: '{{ max_count | default(None) }}'
      register: result
    - debug: var=result.luns

'''

RETURN = r'''
'''

import json

import ansible_collections.hpe.xp_storage.plugins.module_utils.hv_lun_facts_runner as runner
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
    fields = {'storage_serial': {'required': False, 'type': 'str'},
              'data': {'required': True, 'type': 'json'}}

    if module is None:
        module = AnsibleModule(argument_spec=fields)

    try:
        runner.runPlaybook(module)
    except HiException as ex:
        if HAS_MESSAGE_ID:
            logger.writeAMException(MessageID.ERR_OPERATION_LUN)
        else:
            logger.writeAMException("0X0000")
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
