#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type
import json

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystem, \
    StorageSystemManager
from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log, \
    HiException
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import Utils

logger = Log()
moduleName = 'Storage replication facts'


def writeNameValue(name, value):
    logger.writeInfo(name, value)


def writeMsg(msg):
    logger.writeInfo(msg)


def runPlaybook(module):

    logger.writeEnterModule(moduleName)
    storage_serial = module.params.get('storage_serial', None)
    pvolId = None
    pStorage = None
    if module.params.get('data', None):
        data = json.loads(module.params['data'])
        pStorage = data.get('primary_storage_serial_no')
        pvolId = data.get('pvol_id', None)
        
    if storage_serial == None:
        storage_serial = pStorage
    elif storage_serial == None and pStorage == None:
        raise Exception('Storage Serial number is a mandatory field.')
        
    storageReplication = StorageSystem(storage_serial)

    if pvolId:
            replType = module.params['repl_type']
            if replType.lower() not in ('tc', 'gad'):
                raise Exception('Replication type is neither tc nor gad. Please set it to a valid value.'
                                )
            storage_replication_details = storageReplication.getStorageReplicationDetails(pvolId, replType, storage_serial)            
    else:
        storage_replication_details = storageReplication.getAllStorageReplicationDetails() 

    module.exit_json(storageReplication=storage_replication_details)
