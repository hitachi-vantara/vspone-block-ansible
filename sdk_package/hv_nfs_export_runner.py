import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.hv_infra import StorageSystem, StorageSystemManager
from ansible.module_utils.hv_infra import Utils
from ansible.module_utils.hv_hnas import HNASFileServer
from ansible.module_utils.hv_logger import MessageID
from ansible.module_utils.hv_log import Log, HiException

logger=Log()
moduleName="HNAS NFS Exports"

def cleanResult(result):
    pass

def runPlaybook(module):
    
        logger.writeEnterModule(moduleName)

        ## we run on storage-connectors.json
        ## don't need much from the playbook
        fs = HNASFileServer()
        data = json.loads(module.params["data"])
        evs = data["evs"]
        fileServerIP = data["fileServerIP"]
        fileSystem = data.get("file_system",None)         
        exportName = data["export_name"] 
        
        #path = "/test3"        
        #accessConfig = "*"
                
        path = data.get("path",None)
        accessConfig = data.get("access_config", None)
         
        logger.writeParam("evs={}", evs)
        logger.writeParam("fileServerIP={}", fileServerIP)
        logger.writeParam("fileSystem={}", fileSystem)
        logger.writeParam("exportName={}", exportName)
        logger.writeParam("path={}", path)
        logger.writeParam("accessConfig={}", accessConfig)
        logger.writeParam("state={}", module.params["state"])
        
        if path is not None and "\\" in path:
            raise Exception("Backslash is not valid in path.")
        
        
        if module.params["state"] == "present":
            
            logger.writeInfo("create")
            if path == "/" :
                raise Exception("The virtual volume root directory cannot be the root directory of the file system ")
            
            result = fs.createNFSExport(fileServerIP, evs, exportName, fileSystem, path, accessConfig, 
                                    0, 0, 0)
        else:
            ## delete
            logger.writeInfo("delete")
            result = fs.deleteNFSExport(fileServerIP, evs, exportName)                  
        
        if result is not None:
            cleanResult(result)
                
        logger.writeExitModule(moduleName)
        module.exit_json(hnas=result)
        
