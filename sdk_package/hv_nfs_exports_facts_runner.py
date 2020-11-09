import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.hv_infra import StorageSystem, StorageSystemManager
from ansible.module_utils.hv_infra import Utils
from ansible.module_utils.hv_storage_enum import SNAPSHOT_OPTION_ENUM
from ansible.module_utils.hv_storage_enum import TRANSFER_TO_REPLICATION_TARGET_SETTING_ENUM
from ansible.module_utils.hv_storage_enum import LOCAL_READ_CACHE_OPTION_ENUM
from ansible.module_utils.hv_logger import MessageID
from ansible.module_utils.hv_log import Log, HiException
from ansible.module_utils.hv_hnas import HNASFileServer

logger=Log()
moduleName="HNAS NFS Exports facts"

def cleanResult(result):
    for item1 in result:
        for item2 in item1["nfsExports"]:
            item2["EVSIP"] = item2["Evs"]
            del item2["Evs"]
            item2["SnapshotOption"] = SNAPSHOT_OPTION_ENUM.getName(item2["SnapshotOption"])
            item2["ReadCacheOption"] = LOCAL_READ_CACHE_OPTION_ENUM.getName(item2["ReadCacheOption"])
            item2["transferToReplication"] = TRANSFER_TO_REPLICATION_TARGET_SETTING_ENUM.getName(item2["transferToReplication"])

def runPlaybook(module):
    
        logger.writeEnterModule(moduleName)

        ## we run on storage-connectors.json
        ## don't need much from the playbook
        fs = HNASFileServer()
        data = json.loads(module.params["data"])
        fileServerIP = data["fileServerIP"] 
        evs = data.get("evs",None) 
        nfs_export_name = data.get("nfs_export_name",None) 
        
        logger.writeParam("evs={}", evs)
        logger.writeParam("fileServerIP={}", fileServerIP)
        logger.writeParam("nfs_export_name={}", nfs_export_name)
         
        evss = fs.getEnterpriseVirtualServers(fileServerIP)
        
        result = []
        if evs is None:
            ## full
            for evs in evss:
                evs2 = fs.getNFSExports(fileServerIP, evs["IPAddress"])
                evs["nfsExports"] = evs2
                result.append(evs)
        else:
            for item in evss:
                if item["IPAddress"] == str(evs):
                    if nfs_export_name is None:
                        exports = fs.getNFSExports(fileServerIP, evs)
                    else:
                        exports = fs.getNFSExportsByName(fileServerIP, evs, nfs_export_name)
                    item["nfsExports"] = exports
                    result.append(item)
                    break;
            
        
        if result is not None:
            cleanResult(result)
                
        logger.writeExitModule(moduleName)
        module.exit_json(hnas=result)
        
