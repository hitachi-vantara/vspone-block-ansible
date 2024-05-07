#!/usr/bin/python
# -*- coding: utf-8 -*-

__metaclass__ = type
import json
import time

from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystem, \
    Utils
from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log

logger = Log()
moduleName = 'Storage Replication'
dryRun = False


def writeNameValue(name, value):
    logger.writeInfo(name, value)


def writeMsg(msg):
    logger.writeDebug(msg)



def runPlaybook(module):
    logger.writeEnterModule(moduleName)

    data = json.loads(module.params['data'])
    storage_serial = data.get('primary_storage_serial_no')
    if storage_serial == None:
        raise Exception('Primary Storage Serial Number is a mandatory field.'
                        )

    storageSystem = StorageSystem(storage_serial)
    result = {'changed': False}
    state = module.params['state']

    subobjState = data.get('state', 'present')
    if subobjState == '':
        subobjState = 'present'
    if subobjState not in ('present', 'absent'):
        raise Exception('Subobject state is neither present nor absent. Please set it to a valid value.'
                        )

    replType = module.params['repl_type']
    if replType.lower() not in ('tc', 'gad'):
        raise Exception('Replication type is neither tc nor gad. Please set it to a valid value.'
                        )

    actionType = module.params['action_type']
    if state != 'absent':
        primaryLunId = data.get('primary_lun_id', None)                    
        if primaryLunId and replType.lower() == 'tc':
            storage_replication = storageSystem.createStorageReplicationTc(data)       
            result['storageReplication'] = storage_replication
            changed = True
            logger.writeExitModule(moduleName)
        elif primaryLunId and replType.lower() == 'gad':
            storage_replication = storageSystem.createStorageReplicationGad(data)
            result['storageReplication'] = storage_replication
            changed = True
            logger.writeExitModule(moduleName)
        elif actionType == 'resync':
            storage_replication = storageSystem.resyncStorageReplication(data.get('pvol_id', None), replType)
            result['storageReplication'] = storage_replication
            changed = True
            logger.writeExitModule(moduleName)
        elif actionType == 'split':
            storage_replication = storageSystem.splitStorageReplication(data.get('pvol_id', None), replType)
            result['storageReplication'] = storage_replication
            changed = True
            logger.writeExitModule(moduleName)
    elif state == 'absent':
            storage_replication = storageSystem.deleteStorageReplication(data.get('pvol_id', None), replType)
            result['storageReplication'] = storage_replication
            changed = True
            logger.writeExitModule(moduleName)
    else:
        changed = False

    result['changed'] = changed
    module.exit_json(**result)

