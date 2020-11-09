import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.hv_infra import StorageSystem, StorageSystemManager
from ansible.module_utils.hv_infra import Utils
from ansible.module_utils.hv_logger import MessageID
from ansible.module_utils.hv_log import Log, HiException
from ansible.module_utils.hv_hnas import HNASFileServer

logger=Log()
moduleName="EVS facts"

def cleanResult(result):
    pass

def runPlaybook(module):

        logger.writeEnterModule(moduleName)

        ## we run on storage-connectors.json
        ## don't need much from the playbook
        fs = HNASFileServer()
        data = json.loads(module.params["data"])
        fileServerIP = data["fileServerIP"] 
        evs = data.get("evs",None) 
        
        logger.writeParam("fileServerIP={}", fileServerIP)
        logger.writeParam("evs={}", evs)
                        
        result = []
        evss = fs.getEnterpriseVirtualServers(fileServerIP)           
        if evs is not None:
            for item in evss:
                if item["IPAddress"] == str(evs):
                    result.append(item)
                    break 
        else:
            result = evss                          
        
        if result is not None:
            cleanResult(result)
                
        logger.writeExit(moduleName)
        module.exit_json(hnas=result)
        
