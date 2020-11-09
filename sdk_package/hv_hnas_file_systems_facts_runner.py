import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.hv_infra import StorageSystem, StorageSystemManager
from ansible.module_utils.hv_infra import Utils
from ansible.module_utils.hv_logger import MessageID
from ansible.module_utils.hv_log import Log, HiException
from ansible.module_utils.hv_hnas import HNASFileServer

oneGB = 1024*1024*1024
logger=Log()
moduleName="HNAS File System facts"

def blankNullValues(collection):
    for k,v in collection.items():
        if v is None:
            collection[k] = ""        

def getGB(value):
    logger.writeInfo("getGB, value=", value)
    gb = int(value) / oneGB
    return str(gb) + "GB"

def formatItem(item):
        logger.writeInfo("formatItem=", item)
        blankNullValues(item)
        item["ExpansionLimitInGB"] = getGB(item["ExpansionLimit"])
        del item["ExpansionLimit"]
        item["FreeCapacityInGB"] = getGB(item["FreeCapacity"])
        del item["FreeCapacity"]
        item["TotalCapacityInGB"] = getGB(item["TotalCapacity"])
        del item["TotalCapacity"]
        item["UsedCapacityInGB"] = getGB(item["UsedCapacity"])
        del item["UsedCapacity"]
        item["EVSName"] = item["Evs"]
        del item["Evs"]    
        del item["ReadOnly"]    
        
def cleanResult(result):
    if result is None:
        return
    
    if isinstance( result, list ) :   
        logger.writeInfo("result is a list")
        for item in result:
            if item is None:
                continue
            formatItem(item)
    else:
        logger.writeInfo("result is not a list")
        formatItem(result)
            


def runPlaybook(module):
    
        logger.writeEnterModule(moduleName)

        ## we run on storage-connectors.json
        ## don't need much from the playbook
        fs = HNASFileServer()
        data = json.loads(module.params["data"])
        fileServerIP = data["fileServerIP"]        
        file_system = data.get("file_system",None)
         
        logger.writeParam("fileServerIP={}", fileServerIP)
        logger.writeParam("file_system={}", file_system)
                 
        if file_system is None:
            result = fs.getFileSystems(fileServerIP)
        else:
            result = fs.getFileSystem(fileServerIP,file_system)
        
        if result is not None:
            cleanResult(result)
                
        logger.writeExitModule(moduleName)
        module.exit_json(hnas=result)
        
