#!/usr/bin/python
# -*- coding: utf-8 -*-

__metaclass__ = type
import json

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystem, \
    StorageSystemManager
from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log, \
    HiException
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import Utils

logger = Log()
moduleName = 'Resource Group facts'


def writeNameValue(name, value):
    logger.writeInfo(name, value)


def writeMsg(msg):
    logger.writeInfo(msg)


def runPlaybook(module):

    logger.writeEnterModule(moduleName)
    storage_serial = module.params.get('primary_storage_serial_no', None)
    resourceGroup = StorageSystem(storage_serial)
    secondary_storage_serial = None
    if module.params.get('data', None):
        data = json.loads(module.params['data'])
        secondary_storage_serial = data.get('secondary_storage_serial_no', None)
    if secondary_storage_serial:
            resourceGroup = resourceGroup.getResourceGroupsDetails(secondary_storage_serial)      
    else:
        resourceGroup = resourceGroup.getAllResourceGroups()

    module.exit_json(resourceGroup=resourceGroup)
