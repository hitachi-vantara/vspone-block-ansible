import json
import logging

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.hv_infra import StorageSystem, StorageSystemManager
from ansible.module_utils.hv_logger import MessageID
from ansible.module_utils.hv_log import Log, HiException

logger=Log()
moduleName="Storage System facts"

def writeNameValue(name, value):
    logger.writeInfo(name,value)
#     name=name.replace("{}","{0}")
#     logging.debug(name.format(value))

def writeMsg(msg):
    logger.writeInfo(msg)
#     logging.debug(msg)

def runPlaybook(module):

        logger.writeEnterModule(moduleName)

        storageSystem = StorageSystem(module.params["storage_serial"])
        storageInfo = storageSystem.getInfo()

        if module.params["query"]:
            
            logger.writeParam("query={}", module.params["query"])
            
            for prop in ("MicroCodeVersion", "GroupIdentifier", "FreeCapacityInMB", "TotalCapacityInMB", "IsHUVMCapable", "IsEnterpriseStorageDevice",
                    "IsVirtual", "IsHM800Unified", "Controller0", "Controller1"):
                del storageInfo[prop]

            if "pools" in module.params["query"]:
                storageInfo["StoragePools"] = storageSystem.getStoragePools()
            if "ports" in module.params["query"]:
                storageInfo["Ports"] = storageSystem.getPorts()
            if "quorumdisks" in module.params["query"]:
                storageInfo["QuorumDisks"] = storageSystem.getQuorumDisks()
            if "journalPool" in module.params["query"]:
                storageInfo["JournalPool"] = storageSystem.getJournalPools()
            if "nextFreeGADConsistencyGroupId" in module.params["query"]:
                storageInfo["nextFreeGADConsistencyGroupId"] = storageSystem.getFreeGADConsistencyGroupId()
            if "nextFreeHTIConsistencyGroupId" in module.params["query"]:
                storageInfo["nextFreeHTIConsistencyGroupId"] = storageSystem.getFreeHTIConsistencyGroupId()
            if "nextFreeTCConsistencyGroupId" in module.params["query"]:
                storageInfo["nextFreeTCConsistencyGroupId"] = storageSystem.getFreeTCConsistencyGroupId()
            if "nextFreeURConsistencyGroupId" in module.params["query"]:
                storageInfo["nextFreeURConsistencyGroupId"] = storageSystem.getFreeURConsistencyGroupId()
            if "freeLogicalUnitList" in module.params["query"]:
                flulist = storageSystem.getFreeLUList()
                storageInfo["freeLogicalUnitList"] = flulist
                if flulist is not None:
                    storageInfo["freeLogicalUnitCount"] = len(flulist)
        else:
            ## default, when no query param is given
            storageInfo["StoragePools"] = storageSystem.getStoragePools()
            storageInfo["Ports"] = storageSystem.getPorts()
            storageInfo["QuorumDisks"] = storageSystem.getQuorumDisks()

        del storageInfo["SessionId"]
        module.exit_json(storageSystem=storageInfo)
