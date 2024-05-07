#!/usr/bin/python
# -*- coding: utf-8 -*-

__metaclass__ = type
import json
import logging

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystem, \
    StorageSystemManager
from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log, \
    HiException
from ansible_collections.hitachi.storage.plugins.module_utils.hv_ucpmanager import UcpManager

logger = Log()
moduleName = 'Storage System facts'


def writeNameValue(name, value):
    logger.writeInfo(name, value)


#     name=name.replace("{}","{0}")
#     logging.debug(name.format(value))

def writeMsg(msg):
    logger.writeInfo(msg)


#     logging.debug(msg)

def runPlaybook(module):

    logger.writeEnterModule(moduleName)

    storage_system_info = json.loads(module.params['storage_system_info'])
    storage_serial = storage_system_info.get('serial', None)

    ucp_advisor_info = json.loads(module.params['ucp_advisor_info'])
    ucpadvisor_address = ucp_advisor_info.get('address', None)
    ucpadvisor_username = ucp_advisor_info.get('username', None)
    ucpadvisor_password = ucp_advisor_info.get('password', None)
    logger.writeDebug('ucpadvisor_address={}', ucpadvisor_address)
    logger.writeDebug('ucpadvisor_username={}', ucpadvisor_username)
    
    ucpManager = UcpManager(
        ucpadvisor_address,
        ucpadvisor_username,
        ucpadvisor_password,
        storage_serial,
        )
    if ucpManager.isOnboarding():
        raise Exception("Storage system is onboarding, please try again later.")

    storageInfo = \
        ucpManager.formatStorageSystem(ucpManager.getStorageSystem())
    logger.writeDebug('{} storageInfo={}', moduleName, storageInfo)

    query = storage_system_info.get('query', None)
    if query:

        logger.writeParam('query={}', query)

        # for prop in ("MicroCodeVersion", "GroupIdentifier", "FreeCapacityInMB", "TotalCapacityInMB", "IsHUVMCapable", "IsEnterpriseStorageDevice",
        #         "IsVirtual", "IsHM800Unified", "Controller0", "Controller1"):
        #     del storageInfo[prop]

        if 'pools' in query:
            storageInfo['StoragePools'] = \
                ucpManager.getStoragePools()
        if 'ports' in query:
            storageInfo['Ports'] = ucpManager.getPorts()
        if 'quorumdisks' in query:
            storageInfo['QuorumDisks'] = ucpManager.getQuorumDisks()
        if 'journalPools' in query:
            storageInfo['JournalPools'] = ucpManager.getJournalPools()
        # if 'nextFreeGADConsistencyGroupId' in query:
        #     storageInfo['nextFreeGADConsistencyGroupId'] = \
        #         storageSystem.getFreeGADConsistencyGroupId()
        # if 'nextFreeHTIConsistencyGroupId' in query:
        #     storageInfo['nextFreeHTIConsistencyGroupId'] = \
        #         storageSystem.getFreeHTIConsistencyGroupId()
        # if 'nextFreeTCConsistencyGroupId' in query:
        #     storageInfo['nextFreeTCConsistencyGroupId'] = \
        #         storageSystem.getFreeTCConsistencyGroupId()
        # if 'nextFreeURConsistencyGroupId' in query:
        #     storageInfo['nextFreeURConsistencyGroupId'] = \
        #         storageSystem.getFreeURConsistencyGroupId()
        if 'freeLogicalUnitList' in query:
            flulist = ucpManager.getFreeLUList()
            storageInfo['freeLogicalUnitList'] = flulist
        #     if flulist is not None:
        #         storageInfo['freeLogicalUnitCount'] = len(flulist)
    else:

        # default, when no query param is given

        storageInfo['StoragePools'] = ucpManager.getStoragePools()
        # storageInfo['Ports'] = storageSystem.getPorts()
        # storageInfo['QuorumDisks'] = storageSystem.getQuorumDisks()

    module.exit_json(storageSystem=storageInfo)
