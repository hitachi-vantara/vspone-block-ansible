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
module: hv_lun_facts
short_description: This module provides LUN information on the specified Hitachi storage system.
description:
     - The M(hv_lun_facts) module provides the LUN information on the specified Hitachi storage system.
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
      - C(ucpadvisor_username:) Mandatory input. String type. UCPA user name.
      - C(ucpadvisor_password:) Mandatory input. String type. UCPA password in clear text.
      - =================================================================
    default: n/a
  spec:
    required: no
    description:
      - spec has the following properties
      - =================================================================
      - Logical Unit information
      - =================================================================
      - C(lun:) Optional input. LDEV ID in storage,supported format can be in decimal or HEX or Host LUN ID in canonical form.
        If lun parameter is provided, it returns information of specified lun only. If the Host LUN ID is given in canonical
        form, the LUN value must be prefixed with 'naa'. 
        Storage serial would be ignored and LUN details would be retrieved from any storage added to the current session
      - C(name:) Optional. String type. Name of the existing LUN.
      - C(max_count:) Optional. Integer type. This works along with the variable 'lun'. When specified, the next "max_count" number of
        lun are displayed starting from LDEV ID specified by variable 'lun'
      - =================================================================
    default: n/a
'''

EXAMPLES = \
    r'''

-
  name: Testing Get LUN
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: vars.yml
  vars:
    - storage_serial: "446039"
    - ucp_name: "UCP-CI-446039"
    - max_count: 10
  tasks:
    - hv_lun_facts:

        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'

        ucp_advisor_info:
          address: "{{ucpadvisor_address}}"
          username: "{{ucpadvisor_username}}"
          password: "{{ucpadvisor_password}}"

        spec:
          lun: '{{ lun | default(omit) }}'
          name: '{{ name | default(omit) }}'
          max_count: '{{ max_count | default(omit) }}'

      register: result
    - debug: var=result.luns
-
-
  name: Testing Get LUN in hex
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: vars.yml
  vars:
    - storage_serial: "611032"
    - ucp_name: "UCP-CI-12144"
    - lun: 00:05:6F
  tasks:
    - hv_lun_facts:

        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'

        ucp_advisor_info:
          address: "{{ucpadvisor_address}}"
          username: "{{ucpadvisor_username}}"
          password: "{{ucpadvisor_password}}"

        spec:
          lun: '{{ lun | default(omit) }}'
          name: '{{ name | default(omit) }}'
          max_count: '{{ max_count | default(omit) }}'

      register: result
    - debug: var=result.luns

-
-
  name: Testing Get LUN in canonical name
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: vars.yml
  vars:
    - storage_serial: "611032"
    - ucp_name: "UCP-CI-12144"
    - lun: "naa.60060e80212b180050602b180000056f"
  tasks:
    - hv_lun_facts:

        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'

        ucp_advisor_info:
          address: "{{ucpadvisor_address}}"
          username: "{{ucpadvisor_username}}"
          password: "{{ucpadvisor_password}}"

        spec:
          lun: '{{ lun | default(omit) }}'
          name: '{{ name | default(omit) }}'
          max_count: '{{ max_count | default(omit) }}'

      register: result
    - debug: var=result.luns


'''

RETURN = r'''
'''

import json

import ansible_collections.hitachi.storage.plugins.module_utils.hv_lun_facts_runner as runner
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystem, \
    StorageSystemManager
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import Utils
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
            logger.writeAMException("0X0000")
        module.fail_json(msg=ex.format())
    except Exception as ex:
        module.fail_json(msg=str(ex))

if __name__ == '__main__':
    main()
