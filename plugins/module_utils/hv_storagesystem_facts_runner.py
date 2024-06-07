#!/usr/bin/python
# -*- coding: utf-8 -*-

__metaclass__ = type
import json
import logging

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


#     logging.debug(msg)


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

        logger.writeParam("query={}", query)

        # for prop in ("MicroCodeVersion", "GroupIdentifier", "FreeCapacityInMB", "TotalCapacityInMB", "IsHUVMCapable", "IsEnterpriseStorageDevice",
        #         "IsVirtual", "IsHM800Unified", "Controller0", "Controller1"):
        #     del storageInfo[prop]

        if "pools" in query:
            storageInfo["StoragePools"] = ucpManager.getStoragePools()
        if "ports" in query:
            storageInfo["Ports"] = ucpManager.getPorts()
        if "quorumdisks" in query:
            storageInfo["QuorumDisks"] = ucpManager.getQuorumDisks()
        if "journalPools" in query:
            storageInfo["JournalPools"] = ucpManager.getJournalPools()
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
        if "freeLogicalUnitList" in query:
            flulist = ucpManager.getFreeLUList()
            storageInfo["freeLogicalUnitList"] = flulist
        #     if flulist is not None:
        #         storageInfo['freeLogicalUnitCount'] = len(flulist)
    else:

        # default, when no query param is given

        storageInfo["StoragePools"] = ucpManager.getStoragePools()
        # storageInfo['Ports'] = storageSystem.getPorts()
        # storageInfo['QuorumDisks'] = storageSystem.getQuorumDisks()

    ## sng,a2.4 - expect only one ss here
    storageInfo.pop("ucpSystems", None)
    return storageInfo
    # module.exit_json(storageSystem=storageInfo)
