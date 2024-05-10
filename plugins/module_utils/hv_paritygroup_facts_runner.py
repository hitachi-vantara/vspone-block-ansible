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
moduleName = 'Storage Parity Group facts'


def writeNameValue(name, value):
    logger.writeInfo(name, value)


def writeMsg(msg):
    logger.writeInfo(msg)

def formatCapacityMB(valueMB, round_digits=4):

    # expected valueMB (from puma):
    # 5120 is 5120MB

    logger.writeDebug('formatCapacityMB, unformatted value={}', valueMB)

    ivalue = float(valueMB)
    if ivalue == 0:
        return '0'

    ivalue = ivalue / 1024 / 1024
    logger.writeDebug('40 formatCapacityMB, ivalue={}', ivalue)
    if ivalue >= 0:
        # drop the fraction
        v = ivalue * 1024 / 1024
        return str(round(v, round_digits)) + 'TB'


    ivalue = float(valueMB)
    ivalue = ivalue / 1024
    logger.writeDebug('46 formatCapacityMB, ivalue={}', ivalue)
    if ivalue >= 0:
        # drop the fraction
        v = ivalue * 1024 / 1024
        return str(round(v, round_digits)) + 'GB'

    ivalue = float(valueMB)
    logger.writeDebug('52 formatCapacityMB, ivalue={}', ivalue)
    return str(round(ivalue, round_digits)) + 'MB'

def formatCapacity(value, round_digits=4):

    Utils.logger.writeDebug('formatCapacity, value={}', value)
    oneK = 1024

    ivalue = float(value)
    # Utils.logger.writeParam('formatCapacity, ivalue={}', ivalue)
    if ivalue == 0:
        return '0'
    
    valueMB = ivalue / 1024 / 1024
    if valueMB > 0 :
        logger.writeDebug('41 formatCapacity, valueMB={}', valueMB)
        return formatCapacityMB(valueMB)

    return str(round(ivalue, round_digits)) + 'MB'

def formatPools( pools ):
    funcName = 'Runner:formatPools'
    logger.writeEnterSDK(funcName)
    try:
        for pool in pools:
            pool["totalCapacity"]=formatCapacity(pool["totalCapacity"])
            pool["freeCapacity"]=formatCapacity(pool["freeCapacity"])
        logger.writeExitSDK(funcName)
    except Exception as ex:
        logger.writeDebug('20230505 Exception={}',ex)

def runPlaybook(module):

    logger.writeEnterModule(moduleName)

    ucp_advisor_info = json.loads(module.params['ucp_advisor_info'])
    ucpadvisor_address = ucp_advisor_info.get('address', None)
    ucpadvisor_ansible_vault_user = ucp_advisor_info.get('username', None)
    ucpadvisor_ansible_vault_secret = ucp_advisor_info.get('password', None)

    storage_system_info = json.loads(module.params['storage_system_info'])
    storage_serial = storage_system_info.get('serial', None)
    ucp_serial = storage_system_info.get('ucp_name', None)

    logger.writeDebug('20230606 storage_serial={}',storage_serial)

    storageSystem = None
    try:
        storageSystem = StorageManager(
            ucpadvisor_address,
            ucpadvisor_ansible_vault_user,
            ucpadvisor_ansible_vault_secret,
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
        ucpadvisor_ansible_vault_user,
        ucpadvisor_ansible_vault_secret,
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
        storage_pool_details = storageSystem.getAllParityGroups() 

    formatPools(storage_pool_details)

    module.exit_json(paritygroup=storage_pool_details)
