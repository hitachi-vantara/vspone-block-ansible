import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.hv_infra import StorageSystem, HostMode, StorageSystemManager
from ansible.module_utils.hv_logger import MessageID
from ansible.module_utils.hv_log import Log, HiException

logger=Log()
moduleName="Host Group facts"

def writeNameValue(name, value):
    logger.writeDebug(name,value)

def runPlaybook(module):

        logger.writeEnterModule(moduleName)

        storageSystem = StorageSystem(module.params["storage_serial"])
        data = json.loads(module.params["data"])
        options = data.get("query", [])

        hostGroups = []
        ports = data.get("ports")
        
        if "name" in data:
            logger.writeParam("name={}", data["name"])
            if not ports:
                ports = storageSystem.getPorts()
            for port in ports:
                hg = storageSystem.getHostGroup(data["name"], port)
                if hg:
                    hostGroups.append(hg)
        elif "lun" in data:
            logger.writeParam("lun={}", data["lun"])
            hostGroups = storageSystem.getHostGroupsForLU(data["lun"])
            if ports:
                portSet = set(ports)
                hostGroups = [group for group in hostGroups if group["Port"] in portSet]
        else:
            hostGroups = storageSystem.getAllHostGroups()
            if ports:
                portSet = set(ports)
                hostGroups = [group for group in hostGroups if group["Port"] in portSet]

        for hg in hostGroups:
            hg["HostMode"] = HostMode.getHostModeName(hg["HostMode"])

            hg["HostModeOptions"] = [opt["hostModeOptionNumber"] for opt in hg["hostModeOptions"] or []]
            if hg.get("HostModeOptions", None) is None:
                hg["HostModeOptions"] = []
            if hg.get("hostModeOptions", None) is not None:
                writeNameValue("hostModeOptions={}",hg["hostModeOptions"])
                del hg["hostModeOptions"]

            if not options or "luns" in options:
                paths = hg.get("Paths",None)
                if paths:
                    writeNameValue("Paths={}",hg["Paths"])
                    for path in paths:
                        if "lupathHostID" in path:
                            path["hostGroupLunId"] = path["lupathHostID"]
                            del path["lupathHostID"]
                        if "lupathID" in path:
#                             path["lunId"] = path["lupathID"]
                            path["ldevId"] = path["lupathID"]
                            del path["lupathID"] 
                else:
                    hg["Paths"] = []  
            else:
                del hg["Paths"]              

            if options:
                if "wwns" not in options:
                    del hg["WWNS"]

        logger.writeExitModule(moduleName)
        module.exit_json(hostGroups=hostGroups)
    
