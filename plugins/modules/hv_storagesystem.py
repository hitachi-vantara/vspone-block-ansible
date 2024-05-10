#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


__metaclass__ = type

DOCUMENTATION = \
    r'''
---
module: hv_storagesystem
short_description: This module adds the storage system into the UCP system.
description:
     - The M(hv_storagesystem.py) module adds the storage systems into the UCP system. The UCP system must exist.

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
      - C(storage_address:) Mandatory input for add storage. String type. Storage system address used to add storage.
      - C(storage_ansible_vault_user:) Mandatory input for add storage. String type. Storage system user name used to add storage.
      - C(storage_ansible_vault_secret:) Mandatory input for add storage. String type. Storage system password used to add storage.
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
'''
EXAMPLES = \
    r'''
- name: Adding Storage System
  hosts: localhost
  gather_facts: false
  pre_tasks:
    - include_vars: ../ansible_vault_var/ansible.vault.vars.ucpa.yml
    - include_vars: ../ansible_vault_var/ansible.vault.vars.storage.yml
  vars:
    - ucp_name: UCP-CI-12144
  tasks:
    - hv_storagesystem:

        storage_system_info:
          serial: '{{ storage_serial }}'
          address: "{{storage_address}}"
          username: "{{storage_ansible_vault_user}}"
          password: "{{storage_ansible_vault_secret}}"
          ucp_name: '{{ ucp_name }}'

        ucp_advisor_info:
          address: "{{ucpadvisor_address}}"
          username: "{{ucpadvisor_ansible_vault_user}}"
          password: "{{ucpadvisor_ansible_vault_secret}}"

        state: present
      register: result
    - debug: var=result

-
  name: Deleting Storage System
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: ../ansible_vault_var/ansible.vault.vars.ucpa.yml
  vars:
    - storage_serial: "715035"
    - ucp_name: "ucp-202532"
  tasks:
    - hv_storagesystem:
        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
        ucp_advisor_info:
          address: "{{ucpadvisor_address}}"
          username: "{{ucpadvisor_ansible_vault_user}}"
          password: "{{ucpadvisor_ansible_vault_secret}}"
        state: absent
      register: result
    - debug: var=result
    

'''
RETURN = r'''
'''

import json
import os
import re

try:
    from ansible_collections.hitachi.storage.plugins.module_utils.hv_messages import MessageID
    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False
from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log, \
    HiException
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystem
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystemManager
from ansible_collections.hitachi.storage.plugins.module_utils.hv_ucpmanager import UcpManager
from ansible.module_utils.basic import AnsibleModule

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'supported_by': 'certified',
                    'status': ['stableinterface']}

logger = Log()
moduleName = 'Storage System'


def getStorageJson(storageProfile):
    logger.writeDebug('storageProfile={}', storageProfile)

    if storageProfile is None:
        storageProfile = './storage.json'
    else:

        # expect the input from playbook a list

        storageProfile = storageProfile[0]

    logger.writeParam('storageProfile={}', storageProfile)

    if not os.path.exists(storageProfile):
        raise Exception(
            'The storage profile {0} does not exist.'.format(storageProfile))

    # setenv for password decrypt

    storageProfile = os.path.abspath(storageProfile)
    os.environ['HV_STORAGE_ANSIBLE_PROFILE'] = storageProfile
    logger.writeDebug('abs storageProfile={}', storageProfile)
    logger.writeDebug('env storageProfile={}',
                      os.getenv('HV_STORAGE_ANSIBLE_PROFILE'))

    with open(storageProfile) as connectionFile:
        connections = json.load(connectionFile)

    return connections
 

def main(module=None):
    fields = {
        'state': {'default': 'present', 'choices': ['present', 'absent']},
        'storage_system_info': {'required': True, 'type': 'json'},
        'ucp_advisor_info': {'required': True, 'type': 'json'},
        }

    if module is None:
        module = AnsibleModule(argument_spec=fields)

    try:

        logger.writeEnterModule(moduleName)
        storage_system_info = json.loads(module.params['storage_system_info'])

        ########################################################### 
        # valid UCP

        ucp_serial = storage_system_info.get('ucp_name', None)
        logger.writeDebug('ucp_name={}', ucp_serial)

        if ucp_serial is None:
            raise Exception('The parameter ucp_name is required.')
        
        # x = re.search("^(UCP-CI|UCP-HC|UCP-RS|Logical-UCP)-\d{5,10}$", ucp_serial)
        # if not x:
        #     raise Exception('The UCP serial number is invalid.')
    
        ucp_advisor_info = json.loads(module.params['ucp_advisor_info'])
        ucpadvisor_address = ucp_advisor_info.get('address', None)
        ucpadvisor_ansible_vault_user = ucp_advisor_info.get('username', None)
        ucpadvisor_ansible_vault_secret = ucp_advisor_info.get('password', None)
        logger.writeDebug('ucpadvisor_address={}', ucpadvisor_address)
        logger.writeDebug('ucpadvisor_ansible_vault_user={}', ucpadvisor_ansible_vault_user)

        ucpManager = UcpManager(
            ucpadvisor_address,
            ucpadvisor_ansible_vault_user,
            ucpadvisor_ansible_vault_secret)
        
        # theUCP = ucpManager.getUcpSystem( ucp_serial )
        # logger.writeDebug('theUCP={}', theUCP)

        ########################################################### 
        # attach SS to UCP

        storage_serial = storage_system_info.get('serial', None)
        storage_address = storage_system_info.get('address', None)
        storage_ansible_vault_user = storage_system_info.get('username', None)
        storage_ansible_vault_secret = storage_system_info.get('password', None)
        logger.writeDebug('storage_serial={}', storage_serial)
        logger.writeDebug('20230620 storage_ansible_vault_user={}', storage_ansible_vault_user)

        # ucp is mantatory input
        # get the puma getway info out of it
        theUCP = ucpManager.getUcpSystem( ucp_serial )
        if theUCP is None:
            raise Exception("UCP {} is not found.".format(ucp_serial))
        
        ## to work with StorageSystem, it needs the serial, not name
        ucp_serial = theUCP["serialNumber"]

        state = module.params['state']
        if state != 'absent':
            
            gatewayIP = theUCP["gatewayAddress"]
            logger.writeDebug('20230616 gatewayIP={}', gatewayIP)

            results = \
                ucpManager.addStorageSystem(
                    storage_serial,
                    storage_address,
                    gatewayIP,
                    8444,
                    storage_ansible_vault_user,
                    storage_ansible_vault_secret,
                    False,
                    ucp_serial
                )

            logger.writeExitModule(moduleName)
            module.exit_json(storageSystems=results)
            # module.exit_json(storageSystems=results['storageSystems'],
                            # details=results['details'])
        else:
           results =  ucpManager.removeStorageSystem(
                storage_serial,
                ucp_serial,
                )
            #    module.exit_json(**results)
           module.exit_json(msg="Successfully deleted the storage system.")

    except EnvironmentError as ex:
        logger.writeDebug('EnvironmentError={}', ex)
        if ex is None or ex.strerror is None:
            msg = \
                'Failed to add storage, please check input parameters.'
        else:
            msg = ex.strerror
        module.fail_json(msg=msg)
    except Exception as ex:
        logger.writeDebug('Exception={}', ex)
        if ex is None or ex.message is None:
            msg = \
                'Failed during add storage, please check input parameters.'
        else:
            msg = ex.message
        module.fail_json(msg=msg, type=ex.__class__.__name__)


if __name__ == '__main__':
    main()
