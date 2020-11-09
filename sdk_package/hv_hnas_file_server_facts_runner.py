import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.hv_infra import StorageSystem, StorageSystemManager
from ansible.module_utils.hv_infra import Utils
from ansible.module_utils.hv_storage_enum import CLUSTER_HEALTH_ENUM, NODE_STATUS_ENUM
from ansible.module_utils.hv_logger import MessageID
from ansible.module_utils.hv_log import Log, HiException
from ansible.module_utils.hv_hnas import HNASFileServer

logger=Log()
moduleName="File server facts"

def cleanResult(result):
    result["ClusterHealth"] = CLUSTER_HEALTH_ENUM.getName(result["ClusterHealth"])
    if "MacId" in result:
        del result["MacId"]
    for node in result["Nodes"]:
        node["Status"] = NODE_STATUS_ENUM.getName(node["Status"])
        node["NodeId"] = node["ID"]
        del node["ID"]

def runPlaybook(module):
    
        logger.writeEnterModule(moduleName)
        
        ## we run on storage-connectors.json
        ## don't need much from the playbook
        fs = HNASFileServer()
        data = json.loads(module.params["data"])
        fileServerIP = data["fileServerIP"] 
        
        logger.writeParam("fileServerIP={}", fileServerIP)
         
        result = fs.getFileServerInfo(fileServerIP)
        
        if result is not None:
            cleanResult(result)
                
        logger.writeExit(moduleName)
        module.exit_json(hnas=result)

