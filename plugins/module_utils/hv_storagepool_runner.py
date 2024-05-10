#!/usr/bin/python
# -*- coding: utf-8 -*-

__metaclass__ = type
import json
import time

from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystem, \
    Utils
from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log

logger = Log()
moduleName = 'Storage Pool'
dryRun = False


def writeNameValue(name, value):
    logger.writeInfo(name, value)


def writeMsg(msg):
    logger.writeDebug(msg)


def createDynamicPool(
    storageSystem,
    name,
    depletionThresholdRate,
    types,
    warningThresholdRate,
    poolVolumes,
):
    storageSystem.createDynamicPool(name, depletionThresholdRate, types, warningThresholdRate, poolVolumes)

    
    # Load temporary filler data for now

    sp = {'SPName': name, 'Type': types}


def runPlaybook(module):
    logger.writeEnterModule(moduleName)

    storageSystem = StorageSystem(module.params['storage_serial'])
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
        name = data.get('storage_pool_name', None)
        deduplication = data.get('enable_deduplication', None)
        types = data.get('type', None)
        warningThresholdRate = data.get('warning_threshold_rate', None)
        depletionThresholdRate = data.get('depletionThresholdRate', None)
        poolVolumes = data.get('pool_volumes', None)
        
        if poolVolumes and not name:
            storage_pool = storageSystem.expandDynamicPool(data.get('pool_id', None), poolVolumes)       
            result['storagePool'] = storage_pool 
            logger.writeExitModule(moduleName)
            changed = True
        elif deduplication == True or deduplication == False and not name:
            storage_pool = storageSystem.updateStoragePoolDeduplication(data.get('pool_id', None), deduplication)       
            result['storagePool'] = storage_pool 
            changed = True
            logger.writeExitModule(moduleName)
        else:
            storage_pool = storageSystem.createDynamicPool(name, depletionThresholdRate, types, warningThresholdRate, poolVolumes)       
            result['storagePool'] = storage_pool
            changed = True
            logger.writeExitModule(moduleName)
    else:
        pool_id = data.get('pool_id', None)
        if not pool_id:
            raise Exception('pool_id is required.')
        
        storage_pool = storageSystem.deleteDynamicPool(pool_id)       
        result['storagePool'] = storage_pool
        changed = True
        logger.writeExitModule(moduleName)

    result['changed'] = changed
    module.exit_json(**result)

