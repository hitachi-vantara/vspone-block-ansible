#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hewlett Packard Enterprise Development LP ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

DOCUMENTATION = \
    r'''
---
module: hpe_storagesystem
short_description: This module registers storage systems listed in the storage.json file.
description:
     - The hpe_storagesystem.py module registers storage systems listed in the storage.json file (available in /opt/hpe/ansible/), 
       into a Red Hat Ansible session.
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
      - Register storage systems
      - =================================================================
      - C(storage.json:) Mandatory input.json file type.JSON file that contains connection information of the physical storage systems \
        and the storage gateway service.
      - =================================================================
'''
EXAMPLES = \
    r'''
-
  name: Adding Storage System from storage.json
  hosts: localhost
  collections:
    - hpe.xp_storage
  gather_facts: false
  vars:
    - storage_profile: /opt/hpe/ansible/storage.json
  tasks:
    - hpe_storagesystem:
        state: present
        storage_profile: '{{ storage_profile | default(omit) }}'
      register: result
    - debug: var=result

'''
RETURN = r'''
'''

import json
import os

try:
    from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_messages import MessageID
    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_log import Log, \
    HiException
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_infra import StorageSystem
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_infra import StorageSystemManager
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
        'hpeAPIGatewayService': {'required': False, 'type': 'str'},
        'state': {'default': 'present', 'choices': ['present', 'absent']},
        'useOutOfBandConnection': {'required': False, 'type': 'str'},
        'sanStorageSystems': {'required': False, 'type': 'list'},
        'nasStorageSystems': {'required': False, 'type': 'list'},
        'storage_profile': {'required': False, 'type': 'list'}, }

    if module is None:
        module = AnsibleModule(argument_spec=fields)

    try:

        logger.writeEnterModule(moduleName)
        logger.writeDebug(moduleName)

        # deduce the storage.json file path

        storageProfile = module.params.get('storage_profile', None)
        if storageProfile is None:

            # terraform provides configuration from module.params and not
            # from storage_profile json file

            storageJson = module.params
        else:
            storageJson = getStorageJson(storageProfile)

            # logger.writeDebug("storageJson={}", storageJson)

        hpeAPIGatewayService = None
        hpeAPIGatewayServicePort = None
        if 'hpeAPIGatewayService' in storageJson:
            hpeAPIGatewayService = \
                storageJson['hpeAPIGatewayService']
        if 'hpeAPIGatewayServicePort' in storageJson:
            hpeAPIGatewayServicePort = \
                storageJson['hpeAPIGatewayServicePort']

        logger.writeInfo(hpeAPIGatewayService)
        logger.writeInfo(hpeAPIGatewayServicePort)

        if hpeAPIGatewayService is None:
            raise Exception('hpeAPIGatewayService is not specified.'
                            )
        # if hpeAPIGatewayServicePort is None:
            # raise Exception('hpeAPIGatewayServicePort is not specified.'
                            # )

        sanStorageSystems = None
        nasStorageSystems = None
        if 'sanStorageSystems' in storageJson:
            sanStorageSystems = storageJson['sanStorageSystems']
        if 'nasStorageSystems' in storageJson:
            nasStorageSystems = storageJson['nasStorageSystems']

        if sanStorageSystems is None and nasStorageSystems is None:
            raise Exception('Both sanStorageSystems and nasStorageSystems are not specified.'
                            )

        isPhysicalServer = storageJson.get('useOutOfBandConnection',
                                           None)
        if isPhysicalServer is None:
            useOutOfBandConnection = False
        else:
            if isPhysicalServer.upper() == 'FALSE':
                useOutOfBandConnection = False
            else:
                useOutOfBandConnection = True

        logger.writeParam('useOutOfBandConnection={}',
                          useOutOfBandConnection)
        logger.writeDebug('getHomePath={}', Log.getHomePath())
        state = module.params['state']
        StorageSystemManager.logger = logger
        if state != 'absent':
            results = \
                StorageSystemManager.addStorgeSystem(hpeAPIGatewayService,
                                                    hpeAPIGatewayServicePort, sanStorageSystems,
                                                    nasStorageSystems, useOutOfBandConnection)

            logger.writeExitModule(moduleName)
            module.exit_json(storageSystems=results['storageSystems'],
                            details=results['details'])
        else:
            results =  StorageSystemManager.removeStorageSystems(hpeAPIGatewayService,
                                                    hpeAPIGatewayServicePort, sanStorageSystems)
            module.exit_json(**results)                 
    except EnvironmentError as ex:
        logger.writeDebug('EnvironmentError={}', ex)
        if ex is None or ex.strerror is None:
            msg = \
                'Failed to add storage, please check input parameters.'
        else:
            msg = ex.strerror
        module.fail_json(msg=msg)
    except HiException as ex:
        if HAS_MESSAGE_ID:
            logger.writeAMException(MessageID.ERR_AddRAIDStorageDevice)
        else:
            logger.writeAMException('0x0000')
        module.fail_json(msg=ex.format())
    except Exception as ex:
        logger.writeDebug('Exception={}', ex)
        if ex is None or ex.message is None:
            msg = \
                'Failed during add storage, please check input parameters.'
        else:
            msg = ex.message
        module.fail_json(msg=ex.message, type=ex.__class__.__name__)


if __name__ == '__main__':
    main()
