import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.hv_infra import StorageSystem, StorageSystemManager
from ansible.module_utils.hv_infra import Utils
from ansible.module_utils.hv_logger import MessageID
from ansible.module_utils.hv_log import Log, HiException

logger=Log()
moduleName="LUN facts"

def runPlaybook(module):
    logger.writeEnterModule(moduleName)
    
    data = json.loads(module.params["data"])
    lun = data.get("lun")
    count = data.get("max_count")
    lun_end = data.get("lun_end")
    name = data.get("name")

    storage_serial = module.params.get("storage_serial", None)
    logger.writeParam("storage_serial={}", storage_serial)
    logger.writeParam("lun={}", lun)
    logger.writeParam("name={}", name)
    logger.writeParam("count={}", count)
    logger.writeParam("lun_end={}", lun_end)
    
    if storage_serial == "":
        storage_serial=None
    if lun == "":
        lun=None
    if count == "":
        count=None
    if lun_end == "":
        lun_end=None
    if name == "":
        name=None
    
    if storage_serial is None:        
        if lun is not None and lun.startswith("naa."):
            storage_serial = "get.lun.naa"
        else:
            raise Exception("The storage_serial is missing.")
            
    storageSystem = StorageSystem(storage_serial)    

    if lun is not None:
        luns = []
        if lun.startswith("naa."):
            if count is None:
                lun = storageSystem.getLunByNaa(lun)
                if lun :
                  luns.append(lun)
            else:
                if int(count) < 1:
                    raise Exception( "The parameter 'count' must be a whole number greater than zero." )                #
                luns = storageSystem.getLunByCountByNaa(lun, count)
        elif count is not None:
            if int(count) < 1:
                raise Exception( "The parameter 'count' must be a whole number greater than zero." )
            if lun_end is not None:
                raise Exception( "Ambiguous parameters, max_count and lun_end cannot co-exist." )
            luns = storageSystem.getLunsByCount(lun, count)
        elif lun_end is not None:
            luns = storageSystem.getLunsByRange(lun, lun_end)
        else:
            lun = storageSystem.getLun(lun)
            if lun :
              luns.append(lun)
        if luns:
            logger.writeDebug("response: luns={}", luns)
    elif data.get("luns") is not None:
        ## terraform only
        logger.writeParam("luns={}", data["luns"])
        luns = [unit for unit in storageSystem.getAllLuns() if unit["LunNumber"] in data["luns"]]        
    elif data.get("name") is not None:
        logger.writeParam("name={}", data["name"])
        luns = [unit for unit in storageSystem.getAllLuns() if unit["Name"] == data["name"]]
    else:
        luns = storageSystem.getAllLuns()

    Utils.formatLuns(luns)
    logger.writeExitModule(moduleName)
    module.exit_json(luns=luns)

