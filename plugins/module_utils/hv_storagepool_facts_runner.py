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
from ansible_collections.hitachi.storage.plugins.module_utils.hv_storagemanager import StorageManager
from ansible_collections.hitachi.storage.plugins.module_utils.hv_ucpmanager import UcpManager

logger = Log()
moduleName = 'Storage Pool facts'


def writeNameValue(name, value):
    logger.writeInfo(name, value)


def writeMsg(msg):
    logger.writeInfo(msg)

def formatPools(pools):

    if pools is None:
        return
    
    for pool in pools:
        if pool is None:
            continue        
        for key in list(pool.keys()):
            if pool.get(key) is not None:
                if str(pool[key]) == str(-1):
                    pool[key] = ''


def runPlaybook(module):

    logger.writeEnterModule(moduleName)

    ucp_advisor_info = json.loads(module.params['ucp_advisor_info'])
    ucpadvisor_address = ucp_advisor_info.get('address', None)
    ucpadvisor_username = ucp_advisor_info.get('username', None)
    ucpadvisor_password = ucp_advisor_info.get('password', None)

    storage_system_info = json.loads(module.params['storage_system_info'])
    storage_serial = storage_system_info.get('serial', None)
    ucp_serial = storage_system_info.get('ucp_name', None)

    logger.writeDebug('20230606 storage_serial={}',storage_serial)
    logger.writeDebug('20230606 ucp_name={}',ucp_serial)    

    storageSystem = None
    try:
        storageSystem = StorageManager(
            ucpadvisor_address,
            ucpadvisor_username,
            ucpadvisor_password,
            storage_serial,
            ucp_serial
        )
    except Exception as ex:
        module.fail_json(msg=ex.message)

    if not storageSystem.isStorageSystemInUcpSystem():
        raise Exception("Storage system is not under the ucp system.")

    ## check the healthStatus=onboarding
    ucpManager = UcpManager(
        ucpadvisor_address,
        ucpadvisor_username,
        ucpadvisor_password,
        storage_serial,
        )
    if ucpManager.isOnboarding():
        raise Exception("Storage system is onboarding, please try again later.")

    poolId = None
    if module.params.get('data', None):
        data = json.loads(module.params['data'])
        poolId = data.get('pool_id', None)
    if poolId:
            storage_pool_details = storageSystem.getStoragePoolDetails(poolId)      
    else:
        storage_pool_details = storageSystem.getAllStoragePoolDetails() 

    formatPools(storage_pool_details)

    module.exit_json(storagePool=storage_pool_details)
