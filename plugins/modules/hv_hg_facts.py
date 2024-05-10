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
module: hv_hg_facts
short_description: This module provides Host Group information on the specified Hitachi storage system.
description:
     - The M(hv_hg_facts) module provides Host Group information on the specified Hitachi storage system.
version_added: '02.9.0'
author:
  - Hitachi Vantara, LTD. VERSION 02.3.0
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
  spec:
    required: yes
    description:
      - spec has the following properties
      - =================================================================
      - Getting Host Group information Facts
      - =================================================================
      - C(host_group_name:) Optional input. string type. Host group name.If specified, return host groups with the input name.
      - C(ports:) Optional input. array type. Storage FC port.If specified, return all host groups of the input FC ports.
      - C(lun:) Optional input. integer type. LDEV ID.If specified, return all host groups of the input LUN.
      - C(query:) Optional input. Valid values are
      - 1. wwns - Returns all the HBA WWNs available in the hostgroup
      - 2. luns - Returns all the LUNS mapped to the hostgroup
      - =================================================================
'''

EXAMPLES = \
    r'''

-
  name:  Show luns/wwns for hostgroups
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: ../ansible_vault_vars/ansible.vault.vars.ucpa.yml
  vars:
    - storage_serial: "715035"
    - ucp_name: "20-253"
    - host_group_name: test-ansible-hg-1
    - query:
      - luns
      - wwns
  tasks:
    - hv_hg_facts:

        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
          
        ucp_advisor_info:
          address: "{{ucpadvisor_address}}"
          username: "{{ucpadvisor_ansible_vault_user}}"
          password: "{{ucpadvisor_ansible_vault_secret}}"

        spec:
          query: '{{ query | default(omit) }}'
          lun: '{{ lun | default(omit) }}'
          name: '{{ host_group_name | default(omit) }}'
          ports: '{{ ports | default(omit) }}'
      register: result
    - debug: var=result.hostGroups
    
-
  name: Testing Get Host Group
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: ../ansible_vault_vars/ansible.vault.vars.ucpa.yml.20.90
  vars:
    - ucp_name: UCP-CI-71366
    - storage_serial: 446039
    - host_group_name: test-ansible-hg-1
    - ports:
      - CL1-A
      - CL2-B
  tasks:
    - hv_hg_facts:

        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
          
        ucp_advisor_info:
          address: "{{ucpadvisor_address}}"
          username: "{{ucpadvisor_ansible_vault_user}}"
          password: "{{ucpadvisor_ansible_vault_secret}}"

        spec:
          query: '{{ query | default(None) }}'
          lun: '{{ lun | default(None) }}'
          name: '{{ host_group_name | default(None) }}'
          ports: '{{ ports | default(None) }}'

      register: result
    - debug: var=result.hostGroups
'''

RETURN = r'''
'''

import json

import ansible_collections.hitachi.storage.plugins.module_utils.hv_hg_facts_runner as runner
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystem, \
    HostMode, StorageSystemManager
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
            logger.writeAMException(MessageID.ERR_OPERATION_HOSTGROUP)
        else:
            logger.writeAMException("0X0000")
        module.fail_json(msg=ex.format())
    except Exception as ex:
        module.fail_json(msg=str(ex))


if __name__ == '__main__':
    main()
