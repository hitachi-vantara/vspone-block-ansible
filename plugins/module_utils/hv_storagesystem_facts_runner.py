#!/usr/bin/python
# -*- coding: utf-8 -*-

__metaclass__ = type
import json
import logging
import concurrent.futures

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_infra import (
    StorageSystem,
    StorageSystemManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_exceptions import (
    HiException,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_ucpmanager import (
    UcpManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    camel_dict_to_snake_case,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    camel_to_snake_case_dict,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    CommonConstants,
)

logger = Log()
moduleName = "Storage System facts"


def writeNameValue(name, value):
    logger.writeInfo(name, value)


#     name=name.replace("{}","{0}")
#     logging.debug(name.format(value))


def writeMsg(msg):
    logger.writeInfo(msg)

def getQuorumDisks(ucpManager):
    rresult={}
    rresult['rresult'] = ucpManager.getQuorumDisks()
    rresult['name'] ='getQuorumDisks'
    return rresult

def getJournalPools(ucpManager):
    rresult={}
    rresult['rresult'] = ucpManager.getJournalPools()
    rresult['name'] ='getJournalPools'
    return rresult

def getFreeLUList(ucpManager):
    rresult={}
    rresult['rresult'] = ucpManager.getFreeLUList()
    rresult['name'] ='getFreeLUList'
    return rresult

def getPorts(ucpManager):
    rresult={}
    rresult['rresult'] = ucpManager.getPorts()
    rresult['name'] ='getPorts'
    return rresult

def getStoragePools(ucpManager):
    rresult={}
    rresult['rresult'] = ucpManager.getStoragePools()
    rresult['name'] ='getStoragePools'
    return rresult

def getQueryResults(storageInfo, ucpManager, query):
    
    choices= ['ports', 'quorumdisks', 'journalPools', 'freeLogicalUnitList']
    for q in query:
        if q not in choices:
            raise Exception("The query"+str(query)+" must be one in: " + str(choices))
     
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        logger.writeDebug("83 query={}", query)
        futures = []
        if "quorumdisks" in query:
            futures.append(executor.submit(getQuorumDisks,ucpManager))
        if "ports" in query:
            futures.append(executor.submit(getPorts,ucpManager))
        if "pools" in query:
            ## pools are not supported anymore, just keeping it here for reference
            futures.append(executor.submit(getStoragePools,ucpManager))
        if 'journalPools' in query:
            futures.append(executor.submit(getJournalPools,ucpManager))
        if "freeLogicalUnitList" in query:
            futures.append(executor.submit(getFreeLUList,ucpManager))
            
        for future in concurrent.futures.as_completed(futures):
            rresult = future.result()
            if rresult['name'] == 'getStoragePools':
                storageInfo["StoragePools"] = rresult['rresult']
            if rresult['name'] == 'getPorts':
                storageInfo["Ports"] = rresult['rresult']
            if rresult['name'] == 'getQuorumDisks':
                storageInfo["QuorumDisks"] = rresult['rresult']
            if rresult['name'] == 'getJournalPools':
                storageInfo["JournalPools"] = rresult['rresult']
            if rresult['name'] == 'getFreeLUList':
                storageInfo["freeLogicalUnitList"] = rresult['rresult']
                
    return storageInfo
                

def runPlaybook(module):

    logger.writeEnterModule(moduleName)

    storage_system_info = module.params["storage_system_info"]
    storage_serial = storage_system_info.get("serial", None)

    connection_info = module.params["connection_info"]
    management_address = connection_info.get("address", None)
    management_username = connection_info.get("username", None)
    management_password = connection_info.get("password", None)
    subscriberId = connection_info.get("subscriber_id", None)
    api_token = connection_info.get("api_token", None)

    logger.writeDebug("management_address={}", management_address)
    logger.writeDebug("management_username={}", management_username)

    partnerId = CommonConstants.PARTNER_ID
   
    ########################################################
    # True: test the rest of the module using api_token
    
    if False:
        ucpManager = UcpManager(
            management_address,
            management_username,
            management_password,
            api_token,
            partnerId,
            subscriberId,
            storage_serial,
        )    
        api_token = ucpManager.getAuthTokenOnly()
        management_username = ''
    ########################################################
  
    ucpManager = UcpManager(
        management_address,
        management_username,
        management_password,
        api_token,
        partnerId,
        subscriberId,
        storage_serial,
    )
    if ucpManager.isOnboarding():
        raise Exception("Storage system is onboarding, please try again later.")

    storageInfo = ucpManager.formatStorageSystem(ucpManager.getStorageSystem())
    logger.writeDebug("{} storageInfo={}", moduleName, storageInfo)

    query = None
    if module.params["spec"]:
        spec = module.params["spec"]
        query = spec.get("query", None)

    if query:
        logger.writeParam("168 query={}", query)
        storageInfo = getQueryResults(storageInfo, ucpManager, query)

    # else:

    #     # default, when no query param is given

    #     storageInfo["StoragePools"] = ucpManager.getStoragePools()
    #     # storageInfo['Ports'] = storageSystem.getPorts()
    #     # storageInfo['QuorumDisks'] = storageSystem.getQuorumDisks()

    ## sng,a2.4 - expect only one ss here
    storageInfo.pop("ucpSystems", None)
    return storageInfo
    # module.exit_json(storageSystem=storageInfo)
