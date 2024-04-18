#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type
import json
import time

from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystem, \
    Utils
from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log, \
    HiException

logger = Log()
moduleName = 'Resource Group'
dryRun = False


def writeNameValue(name, value):
    logger.writeInfo(name, value)


def writeMsg(msg):
    logger.writeDebug(msg)


def runPlaybook(module):
    logger.writeEnterModule(moduleName)

    resourceGroup = StorageSystem(module.params['primary_storage_serial_no'])
    data = json.loads(module.params['data'])
    result = {'changed': False}
    state = module.params['state']

    subobjState = data.get('state', 'present')
    if subobjState == '':
        subobjState = 'present'
    if subobjState not in ('present', 'absent'):
        raise Exception('Subobject state is neither present nor absent. Please set it to a valid value.'
                        )

    if state != 'absent':
        
        if data.get('host_group', None) != None:
            rg = resourceGroup.addHostGroupToResourceGroup(data.get('host_group', None), data.get('secondary_storage_serial_no', None))       
            result['resourceGroup'] = rg 
            logger.writeExitModule(moduleName)
            changed = True
        elif data.get('ldevId', None) != None:
            rg = resourceGroup.addLunToResourceGroup(data.get('ldevId', None), data.get('secondary_storage_serial_no', None))       
            result['resourceGroup'] = rg 
            logger.writeExitModule(moduleName)
            changed = True
        elif data.get('port', None) != None:
            rg = resourceGroup.addPortToResourceGroup(data.get('port', None), data.get('secondary_storage_serial_no', None))       
            result['resourceGroup'] = rg 
            logger.writeExitModule(moduleName)
            changed = True
    else:
        if data.get('host_group', None) != None:
            rg = resourceGroup.deleteHostGroupFromResourceGroup(data.get('host_group', None), data.get('secondary_storage_serial_no', None))       
            logger.writeExitModule(moduleName)
            changed = True
        elif data.get('ldevId', None) != None:
            rg = resourceGroup.deleteLunFromResourceGroup(data.get('ldevId', None), data.get('secondary_storage_serial_no', None))       
            result['resourceGroup'] = rg 
            logger.writeExitModule(moduleName)
            changed = True
        elif data.get('port', None) != None:
            rg = resourceGroup.deletePortFromResourceGroup(data.get('port', None), data.get('secondary_storage_serial_no', None))       
            result['resourceGroup'] = rg 
            logger.writeExitModule(moduleName)
            changed = True

    result['changed'] = changed
    module.exit_json(**result)

