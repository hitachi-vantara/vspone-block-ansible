import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.hv_infra import StorageSystem, HostMode, StorageSystemManager
from ansible.module_utils.hv_logger import MessageID
from ansible.module_utils.hv_log import Log, HiException

logger=Log()
moduleName="Host Group"
dryRun=False

def writeNameValue(name, value):
    logger.writeDebug(name,value)
#     name=name.replace("{}","{0}")
#     logging.debug(name.format(value))

def writeMsg(msg):
    logger.writeDebug(msg)
#     logging.debug(msg)


def preDeleteHostGroup(storageSystem, hostGroups, hgName, port):
    hgs = [hostGroup 
                  for hostGroup in hostGroups 
                    if hostGroup["HgName"] == hgName and
                       hostGroup["Port"] == port
                  ]
    #only expecting one
    hg = hgs[0]
    #unpresent all luns
    hgLuns = set(path["lupathID"] for path in hg.get("Paths",None) or [])
    for lun in hgLuns:
        storageSystem.unpresentLun(lun, hgName, port)

def createHostGroup(storageSystem, hgName, port, newWWN, newLun, hostmodename, hostoptlist):
    
    storageSystem.createHostGroup(hgName, port, newWWN)
    
    hostmode = HostMode.getHostModeNum(hostmodename or "LINUX")
    if hostoptlist is None:
        hostoptlist = [41, 51]
    storageSystem.setHostMode(hgName, port, hostmode, hostoptlist)
    for lun in newLun:
        storageSystem.presentLun(lun, hgName, port)
    # Load temporary filler data for now
    hg = {"HgName": hgName, "Port": port}

## hostGroups is input/output, input is not none and is not always empty
## knownPortSet are the ports already known to have the hg
## and the hg objects are in the input hostGroups already 
## this is to handle the case in which
## the user given only one port to create, we then sync up the hg in all other ports 
def getHostGroupsByScanAllPorts(storageSystem, hgName, knownPortSet, hostGroups): 
      
    logger.writeDebug("Enter getHostGroupsByScanAllPorts")
    ports = storageSystem.getPorts()
    for port in ports:
        if knownPortSet is not None and port in knownPortSet:
            continue
        hg = storageSystem.getHostGroup(hgName, port)
        if hg:
            hostGroups.append(hg)
    
def runPlaybook(module):

        logger.writeEnterModule(moduleName)

        storageSystem = StorageSystem(module.params["storage_serial"])
        data = json.loads(module.params["data"])
        result = {"changed": False}
        state = module.params["state"]

        subobjState = data.get("state", "present")
        if subobjState == "":
            subobjState="present"
        if subobjState not in ("present", "absent"):
            raise Exception("Subobject state is neither present nor absent. Please set it to a valid value.")

        ports = data.get("ports", None)
        hgName = data.get("host_group_name", None)
        if not hgName: raise Exception("name is required.")
        hostmodename = data.get("host_mode", None)
        hostoptlist = data.get("host_mode_options", None)
        wwns = data.get("wwns", None)
        luns = data.get("luns", [])
        
        if ports == "":
            ports=None
        if hostmodename == "":
            hostmodename=None
        if hostoptlist == "":
            hostoptlist=None
        if wwns == "":
            wwns=None
        if luns == "":
            luns=[]
            
        if wwns is not None:
            # upper case the wwns playbook input since the response from services are in upper (SIEAN 280)
            wwns2 = []
            for wwn in wwns:
                # SIEAN 284 - in case wwn is all number
                wwn=str(wwn)
                wwns2.append(wwn.upper())
            newWWN = set(map(str,wwns2))
        else:
            newWWN = set()

        newLun = set(map(int, luns))

        logger.writeParam("state={}", state)
        logger.writeParam("subobjState={}", subobjState)
        logger.writeParam("ports={}", ports)
        logger.writeParam("hgName={}", hgName)
        logger.writeParam("hostmodename={}", hostmodename)
        logger.writeParam("hostoptlist={}", hostoptlist)
        logger.writeParam("newWWN={}", newWWN)
        logger.writeParam("luns={}", luns)
        
        hostGroups = []
        
        if ports :
            for port in ports:
                writeNameValue("hgName={}",hgName)
                writeNameValue("port{}=",port)
                hg1 = storageSystem.getHostGroup(hgName, port)
                writeNameValue("hg1={}",hg1)
                if hg1 is not None:
                    hostGroups.append(hg1)
        else:
            ## getHostGroup list by name so we will know this is create or modify
            getHostGroupsByScanAllPorts(storageSystem, hgName, None, hostGroups)
        
        changed = False

        if len(hostGroups) == 0:
            # No host groups found 
            # Enter create mode
            # In this case, if state is absent, we do nothing.
            if state != "absent":

                writeMsg("Create Mode =========== ")
                
                if not ports:
                    raise Exception("Host group does not exist; cannot create host groups without ports parameter.")
                else:
                    for port in ports:
                        
                        writeNameValue("createHostGroup={}",hgName)
                        writeNameValue("port={}",port)
                        writeNameValue("newWWN={}",newWWN)
                        storageSystem.createHostGroup(hgName, port, newWWN)

                        hostmode = hostmodename
                        if hostmodename is not None:
                            hostmode = HostMode.getHostModeNum(hostmodename or "LINUX")
                            
                        #if hostoptlist is None:
                            #hostoptlist = [47, 51]
                        if hostoptlist is not None and hostmode is not None:
                            writeNameValue("setHostMode={}",hgName)
                            writeNameValue("port={}",port)
                            writeNameValue("hostmode={}",hostmode)
                            writeNameValue("hostoptlist={}",hostoptlist)
                            storageSystem.setHostMode(hgName, port, hostmode, hostoptlist)
                            
                        for lun in newLun:
                            writeNameValue("presentLun={}",lun)
                            storageSystem.presentLun(lun, hgName, port)
                        # Load temporary filler data for now
                        hg = {"HgName": hgName, "Port": port}
                        hostGroups.append(hg)
                        changed = True
                        
                        
                    ## if we want to support the case:
                    ## the user given one lun, one port to create hg, 
                    ## do sync up the hg in all other ports
                    ## then we need to call getHostGroupsByScanAllPorts(storageSystem, hgName, ?, hostGroups)

                        
        elif state == "absent":
            # Delete mode.
            writeMsg("Delete hgs from the list  =========== ")

            okToDelete = True
            for hg in hostGroups:
                writeNameValue("Paths={}",hg["Paths"])
                if hg["Paths"] is None:
                    continue
                if len( hg["Paths"] )>0 :
                    writeNameValue("Paths={}",hg["Paths"][0])
                    ## hg has presented lun
                    okToDelete=False

            if okToDelete:
                for hg in hostGroups:
                    writeNameValue("del hg={}",hg)
                    writeNameValue("del HgName={}",hg["HgName"])
                    writeNameValue("del Port={}",hg["Port"])
                    writeNameValue( "calling deleteHostGroup, dryRun={}", dryRun )
                    
                    if not dryRun:
                            storageSystem.deleteHostGroup(hg["HgName"], hg["Port"])
                            changed = True
            else:
                result["comment"] = "Hostgroup has luns presented. Please make sure to unpresent all lun prior deleting hostgroup."
                writeMsg("NO Delete with comment")
                        
                        
        else:
            # Modify mode. Certain operations only occur if state is overwrite.
            writeMsg("Update Mode =========== ")
            
            
            # check for add/remove hostgroup for each given port
            oldports = [hostGroup["Port"] for hostGroup in hostGroups if hostGroup["HgName"] == hgName]
            oldports = set(oldports)       

            if ports is not None:
                newports = set(map(str,ports))
            else:
                # ports is not given in the playbook, we will apply the change to all existing ports (SIEAN 281 282)
                writeMsg("apply update to all existing ports")
                newports = set(oldports)            
            
            addPort = newports - oldports
            delPort = oldports & newports
            
            writeNameValue("oldports={}",oldports)
            writeNameValue("newports={}",newports)
            writeNameValue("addPort={}",addPort)
            writeNameValue("delPort={}",delPort)
            
            newports = None
            
            if addPort and subobjState == "present": 
                writeMsg("create hg by addPort")
                writeNameValue("hostGroups={}",hostGroups)
                ## use the first element in the hostgroup list for cloning               
                hg = hostGroups[0]
                
                newports=addPort
                
                # get hostoptlist from the existing hg
                writeNameValue("hostModeOptions={}",hg["hostModeOptions"])
                hgHMO = [opt["hostModeOptionNumber"] for opt in hg["hostModeOptions"] or []]
                hmName = HostMode.getHostModeName(hg["HostMode"])
                writeNameValue("hmName={}",hmName)
                
                # to create hg, you must have a list of ports to add
                for port in addPort:
                    ## clone an existing host group
                    ## then add it to the existing hg list
                    ## then let it go thru the add/remove process below
                    writeNameValue("Paths={}",hg.get("Paths",None))
                    hgLun = set(path["lupathID"] for path in hg.get("Paths",None) or [])
                    
                    if dryRun:
                        writeMsg("DRYRUN = TRUE")
                        continue
                    
                    ## update mode subobjState create
                    createHostGroup(storageSystem, hgName, port, 
                                    hg["WWNS"], hgLun, hmName, hgHMO)
                    
                    hgtmp = storageSystem.getHostGroup(hgName, port)
                    if hgtmp is not None:
                        ## to help oob performance
                        ## add the newly created hg to list instead of getAllHostGroups
                        hostGroups.append(hgtmp)
                    
                changed = True
                
              ## this is incorrect, you del hg not on subobjState, del only on state
#             if delPort and subobjState == "absent":
#                 writeMsg("update hg, del port")
#                 for port in delPort:
#                     ##sss 
#                     preDeleteHostGroup(storageSystem, hostGroups, hgName, port)
#                     storageSystem.deleteHostGroup(hgName, port)
#                 changed = True  
                
                
            ## at this point, hostGroups has the list of hg to update
            ## whether it is create with 1..n ports or
            ## update with 0..n ports in the input
            ## update with no ports given mean apply change to all ports
            
            # process each existing group, check for add/remove hg attributes
            writeMsg("walk thru each host group, check for update ======================")
            
            oldports = [hostGroup["Port"] for hostGroup in hostGroups if hostGroup["HgName"] == hgName]
            oldports = set(oldports)       

            if ports is not None:
                newports = set(map(str,ports))
            else:
                writeMsg("apply update to all existing ports")
                newports = set(oldports)            
            
            addPort = newports - oldports
            delPort = oldports & newports
            
            writeNameValue("oldports={}",oldports)
            writeNameValue("newports={}",newports)
            writeNameValue("addPort={}",addPort)
            writeNameValue("delPort={}",delPort)
            
            writeNameValue("state={}",state)
            writeNameValue("subobjState={}",subobjState)

            if subobjState == "present":
                ## update per the list provided, if new port, 
                ## it would have been created above 
                portsToUpdate = newports
            else:
                ## remove attributes from list, only if it exists
                portsToUpdate = delPort
            
            for hgPort in portsToUpdate:
                hg = [hostGroup for hostGroup in hostGroups if hostGroup["Port"] == hgPort]
                writeNameValue("update hg={}",hg)
                if hg is None or len(hg)==0:
                    continue
                hg = hg[0]
                if "Port" not in hg:
                    continue
                writeNameValue("update HgName={}",hg["HgName"])
                writeNameValue("update Port={}",hg["Port"])

                port = hg["Port"]            
                writeNameValue("processing port={}",port)

                if dryRun:
                    writeMsg("DRYRUN = TRUE")
                    continue

                writeMsg("check hostmode and hostoptlist for update")
                if hostmodename is not None or hostoptlist is not None:
                    if hostmodename is not None:
                        hostmode = HostMode.getHostModeNum(hostmodename)
                    else:
                        hostmode = hg["HostMode"]
                    ## for hostmode, you can only update, no delete
                    writeNameValue("update hostmode={}",hostmode)

                    hgHMO = [opt["hostModeOptionNumber"] for opt in hg["hostModeOptions"] or []]
                    if hostoptlist is not None:
                        ## hostoptlist is the user input
                        
                        oldlist = set(hgHMO)
                        newlist = set(hostoptlist)
                        addlist = newlist - oldlist
                        dellist = oldlist & newlist
                        
                        if subobjState == "present":
                            ## add = new - old
                            #hostopt = hgHMO + list(set(hostoptlist) - set(hgHMO))
                            hostopt = hgHMO + list(addlist)
                        else:
                            ## del = old & new
                            hostopt = list( set(hgHMO) - set(hostoptlist) )
                    else:
                        hostopt = hgHMO
                    writeNameValue("update hostopt={}",hostopt)
                        
                    if hostmode != hg["HostMode"] or set(hostopt) != set(hgHMO):
                        writeMsg("call setHostMode()")
                        storageSystem.setHostMode(hgName, port, hostmode, hostopt)
                        changed = True

                writeMsg("check wwns for update")
                if wwns is not None:        # If wwns is present, add or overwrite wwns
                    hgWWN = set(hg["WWNS"])
                    addWWN = newWWN - hgWWN
                    delWWN = hgWWN & newWWN
                    
                    writeNameValue("old hgWWN={}",hgWWN)
                    writeNameValue("newWWN={}",newWWN)
                    writeNameValue("addWWN={}",addWWN)
                    writeNameValue("delWWN={}",delWWN)
                    
                    if addWWN and subobjState == "present":
                        storageSystem.addWWN(hgName, port, addWWN)
                        changed = True
                    if delWWN and subobjState == "absent":
                        storageSystem.removeWWN(hgName, port, delWWN)
                        changed = True

                writeMsg("check luns for update")
                if luns is not None:        # If luns is present, present or overwrite luns
                    hgLun = set(path["lupathID"] for path in hg.get("Paths",None) or [])
                    addLun = newLun - hgLun
                    delLun = hgLun & newLun
                    if subobjState == "present":
                        for lun in addLun:
                            storageSystem.presentLun(lun, hgName, port)
                            changed = True

                    else:
                        for lun in delLun:
                            storageSystem.unpresentLun(lun, hgName, port)
                            changed = True



        if changed and state != "absent":

                ## dump the hg after the change
                hostGroups = refreshHostGroups(storageSystem, hostGroups)
                for hg in hostGroups:
                    hg["HostMode"] = HostMode.getHostModeName(hg["HostMode"])
        
#         for hg in hostGroups:
#             hg["HostMode"] = HostMode.getHostModeName(hg["HostMode"])
#             hg["hostModeOptions"] = [opt["hostModeOptionNumber"] for opt in hg["hostModeOptions"] or []]
# 
#             hg["luns"] = set(path["lupathID"] for path in hg.get("Paths",None) or [])
#             del hg["Paths"]


        formatHgs(hostGroups)
        logger.writeExitModule(moduleName)
        #module.exit_json(changed = changed, hostGroups = hostGroups)
        result["changed"] = changed
        result["hostGroups"] = hostGroups
        module.exit_json(**result)

def formatHgs(hostGroups):
    if hostGroups is None:
        return

    writeNameValue("hostGroups={}",hostGroups)
    for hg in hostGroups:
        writeNameValue("HostMode={}",hg["HostMode"])
        hg["HostMode"] = HostMode.getHostModeName(hg["HostMode"])
        hg["HostModeOptions"] = [opt["hostModeOptionNumber"] for opt in hg["hostModeOptions"] or []]
        if hg.get("HostModeOptions", None) is None:
            hg["HostModeOptions"] = []
        if hg.get("hostModeOptions", None) is not None:
            writeNameValue("hostModeOptions={}",hg["hostModeOptions"])
        if "hostModeOptions" in hg:
            del hg["hostModeOptions"]
        
#         hg["luns"] = set(path["lupathID"] for path in hg.get("Paths",None) or [])
        
        paths = hg.get("Paths",None)
        if paths:
            writeNameValue("Paths={}",hg["Paths"])
            for path in paths:
                if "lupathHostID" in path:
                    path["hostGroupLunId"] = path["lupathHostID"]
                    del path["lupathHostID"]
                if "lupathID" in path:
                    #path["lunId"] = path["lupathID"]
                    path["ldevId"] = path["lupathID"]
                    del path["lupathID"]
        else:
            hg["Paths"] = []
                
        
#         hg["luns"] = [path["lupathID"] for path in hg["Paths"] or []]
#         if "Paths" in hg:
#             del hg["Paths"]
    
#     for hostGroup in hostGroups:
#         if "Paths" in hostGroup and hostGroup["Paths"] is None:
#             hostGroup["Paths"] = []
#         if hostGroup["hostModeOptions"] is None:
#             hostGroup["hostModeOptions"] = []
#         if hostGroup["WWNS"] is None:
#             hostGroup["WWNS"] = []

## given the hostGroups list, refresh in hg in the list
def refreshHostGroups(storageSystem, hostGroups):
    if hostGroups is None:
        return
            
    hgs = []
    for hostGroup in hostGroups:
        hg = storageSystem.getHostGroup(hostGroup["HgName"], hostGroup["Port"])
        hgs.append(hg)
    
    return hgs
