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
module: hv_ucp
short_description: This module adds, updates and deletes the UCP on the specified Hitachi UCPA system.
description:
     - The M(hv_ucp) module adds, updates and deletes the UCP on the specified Hitachi UCPA system.
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
  data:
    required: yes
    description:
      - data has the following properties
      - =================================================================
      - Add UCP System
      - =================================================================
      - C(ucpadvisor_address:) Mandatory input. String type. UCPA system address.
      - C(ucpadvisor_username:) Mandatory input. String type. UCPA system user name.
      - C(ucpadvisor_password:) Mandatory input. String type. UCPA system password in clear text.
      - C(serial_number:) Mandatory input. String type. UCP system serial number, must be minimum 5 digits and max 10 digits.
      - C(gateway_address:) Mandatory input. String type. Hitachi API geteway service address.
      - C(model:) Mandatory input. String type. UCP system model, must be "UCP CI" or "UCP HC" or "UCP RS" or "Logical UCP".
      - C(name:) Mandatory input. String type. UCP system name, example "UCP-CI-12345".
      - C(region:) Mandatory input. String type. UCP system region, must be "AMERICA" or "APAC" or "EMEA".
      - C(country:) Mandatory input. String type. UCP system country name, example "United States".
      - C(zipcode:) Mandatory input. String type. UCP system zipcode, must be a valid zipcode for the country.
      - =================================================================
'''

EXAMPLES = \
    r'''
-
  name: Adding UCP System
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: vars.yml
  vars:
    - serial_number: "20171"
    - gateway_address: 172.25.20.171
    - model: UCP CI
    - name: ucp-20-171
    - region: AMERICA
    - country: 'United States'
    - zipcode: '95054'
  tasks:
    - hv_ucp:
        state: present
        ucpadvisor_address: "{{ucpadvisor_address}}"
        ucpadvisor_username: "{{ucpadvisor_username}}"
        ucpadvisor_key: "{{ucpadvisor_password}}"
        serial_number: '{{ serial_number }}'
        gateway_address: '{{ gateway_address}}'
        model: '{{ model }}'
        name: '{{ name }}'
        region: '{{ region }}'
        country: '{{ country }}'
        zipcode: '{{ zipcode }}'
      register: result
    - debug: var=result
-
-
  name: Deleting UCP System
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: vars.yml
  vars:
    - name: ucp-20-171
  tasks:
    - hv_ucp:
        state: absent
        name: '{{ name }}'
        ucpadvisor_address: "{{ucpadvisor_address}}"
        ucpadvisor_username: "{{ucpadvisor_username}}"
        ucpadvisor_key: "{{ucpadvisor_password}}"
      register: result
    - debug: var=result
-
-
  name: Updating UCP System
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: vars.yml
  vars:
    - name: ucp-20-171
    - gateway_address: 172.25.20.35
    - region: APAC
    - country: India
    - zipcode: '560087'
  tasks:
    - hv_ucp:
        state: present
        name: '{{ name }}'
        ucpadvisor_address: "{{ucpadvisor_address}}"
        ucpadvisor_username: "{{ucpadvisor_username}}"
        ucpadvisor_key: "{{ucpadvisor_password}}"
        gateway_address: '{{ gateway_address  }}'
        region: '{{ region }}' 
        country: '{{ country  }}' 
        zipcode: '{{ zipcode  }}'
      register: result
    - debug: var=result
    
'''

RETURN = r'''
'''

import json

import ansible_collections.hitachi.storage.plugins.module_utils.hv_ucp_runner as runner
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
    fields = {'serial_number': {'required': False, 'type': 'str'},
              'state': {'default': 'present', 'choices': ['present', 'absent']},
              # 'state': {'required': True, 'type': 'str'},
              'ucpadvisor_address': {'required': True, 'type': 'str'},
              'ucpadvisor_username': {'required': True, 'type': 'str'},
              'ucpadvisor_key': {'required': True, 'type': 'str'},

              # two ways to deal with these params, 
              # 1)set required=False, then we have to handle it when they are missing,
              #   more work but we have full error handling
              # 2)set required=True, then you have to default(None) in the delete playbook,
              #   this is not bullet proof, if user did not set default(None) then the error message would look foolish
              'gateway_address': {'required': False, 'type': 'str'},
              'model': {'required': False, 'type': 'str'},
              'name': {'required': False, 'type': 'str'},
              'region': {'required': False, 'type': 'str'},
              'country': {'required': False, 'type': 'str'},
              'zipcode': {'required': False, 'type': 'str'}}

    if module is None:
        module = AnsibleModule(argument_spec=fields)

    try:
        runner.runPlaybook(module)
    except HiException as ex:
        if HAS_MESSAGE_ID:
            #FIXME
            logger.writeAMException(MessageID.ERR_OPERATION_HOSTGROUP)
        else:
            logger.writeAMException("0X0000")
        module.fail_json(msg=ex)
    except Exception as ex:
        if HAS_MESSAGE_ID:
            #FIXME
            logger.writeAMException(MessageID.ERR_OPERATION_HOSTGROUP)
        else:
            logger.writeAMException("0X0000")
        module.fail_json(msg=str(ex))


if __name__ == '__main__':
    main()
