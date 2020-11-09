import json
import time
import logging

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.hv_infra import StorageSystem, HostMode, Utils, StorageSystemManager
from ansible.module_utils.hv_htimanager import ReplicationStatus
from ansible.module_utils.hv_logger import MessageID
from ansible.module_utils.hv_log import Log, HiException

logger = Log()
moduleName = "Replication facts"


def getURPairs(storageSystem, lun, remote_serial, target_lun):
        if lun != -1:
            rclist = storageSystem.remoteManager.getRemoteClones(lun, remote_serial, None)
            pairs = [pair for pair in rclist if pair["Type"] == 6 and str(pair["PVol"]) == str(lun)]
        else:
            rclist = storageSystem.remoteManager.getRemoteClones(lun, remote_serial, target_lun)
            pairs = [pair for pair in rclist if pair["Type"] == 6]
        return pairs


def getTCPairs(storageSystem, lun, remote_serial, target_lun):
        if lun != -1:
            rclist = storageSystem.remoteManager.getRemoteClones(lun, remote_serial, target_lun)
            pairs = [pair for pair in rclist if pair["Type"] == 5 and str(pair["PVol"]) == str(lun)]
        else:
            rclist = storageSystem.remoteManager.getRemoteClones(lun, remote_serial, target_lun)
            pairs = [pair for pair in rclist if pair["Type"] == 5]
        return pairs

def getDataParamBool(data, key, defaultValue):
    
        val = data.get(key)
        if val=="":
            val=None
        if val is None:
            return defaultValue
        
        val = val.upper()
        if val == 'TRUE':
            return True
        if val == 'FALSE':
            return False
        else:
            raise Exception("Invalid value for parameter {}, must be true or false.".format(key))

def manageGroupSnapshot(module, state, storageSystem, subtask, snapshot_grp):
        data = json.loads(module.params["data"])
        htiManager = storageSystem.htiManager

        if state == 'absent':
            htiManager.manageSnapshotGroup('delete', snapshot_grp)
        elif subtask == 'split' or  subtask == 'resync' or  subtask == 'restore' :
            ##FIXME, is enable_quick_mode required in the playbook, or has a default
            enableQuickMode = getDataParamBool(data, "enable_quick_mode", True)
            htiManager.manageSnapshotGroup(subtask, snapshot_grp, enableQuickMode)
        else:
            raise Exception("Unknown subtask.")

def getReplicationType(data):
        copyType = data.get("copy_type")
        if copyType == "":
            return None
        if copyType is None:
            raise Exception("copy_type must be specified.")
        if copyType == "tc":
            return "TRUE_COPY"
        if copyType == "ur":
            return "HUR"
        if copyType == "gad":
            return "GAD"
        if copyType == "hti":
            return "SHADOW_IMAGE"
        
        raise Exception("Unknown value in copy_type: {}".format(copy_type))

def manageGroupCtg(module, state, storageSystem, subtask, consistency_group_id):
    
        if int(consistency_group_id)<0  or int(consistency_group_id)>255:
            raise Exception("consistency_group_id is between 0 and 255.")
    
        htiManager = storageSystem.htiManager
        data = json.loads(module.params["data"])        
        replicationType = getReplicationType(data)
        if replicationType=="TRUE_COPY"  or replicationType=="HUR" or  replicationType=="GAD"  :
            logger.writeDebug("replicationType = {}",replicationType)                    
        else:
            raise Exception("copy_type must be tc, ur or gad.")
        
        if state == 'absent':
            htiManager.deleteConsistencyGroup(consistency_group_id, replicationType)
        elif subtask == 'split':
            enable_read_write = getDataParamBool(data, "enable_read_write", False)
            if enable_read_write and replicationType=="HUR":
                raise Exception("copy_type must be tc or gad for split consistency group with enable_read_write.")
            else:
                htiManager.splitConsistencyGroup(consistency_group_id, replicationType, enable_read_write)
        elif subtask == 'resync':
            htiManager.resyncConsistencyGroup(consistency_group_id, replicationType)
        else:
            raise Exception("Subtask not implemented.")

def disallowCopyType(module):
        data = json.loads(module.params["data"])
        copyType = data.get("copy_type")
        logger.writeParam("copyType={}", copyType)
        if copyType is not None:
            raise Exception("Only the grouping or the copy_type can be specified.")

def manageGroup(module, moduleName, state, storageSystem, grouping, subtask, snapshot_grp, consistency_group_id):

    logger.writeEnter("manageGroup")
    logger.writeParam("grouping={}", grouping)
    logger.writeParam("subtask={}", subtask)
    logger.writeParam("state={}", state)
    
    if state != 'absent' and subtask is None:
        raise Exception("Please specify subtask.")
    
    result = {}
    htiManager = storageSystem.htiManager
    
    if grouping == "snapshot group":
        logger.writeParam("snapshot_grp={}", snapshot_grp)
        disallowCopyType(module)
        if snapshot_grp is None:
            raise Exception("snapshot_grp is required.")
        manageGroupSnapshot(module, state, storageSystem, subtask, snapshot_grp)
    if grouping == "consistency group":
        logger.writeParam("consistency_group_id={}", consistency_group_id)
        if consistency_group_id is None:
            raise Exception("consistency_group_id is required.")
        manageGroupCtg(module, state, storageSystem, subtask, consistency_group_id)
         
    result["changed"] = True
    logger.writeExitModule(moduleName)
    module.exit_json(**result)

def runPlaybook(module):

        logger.writeEnterModule(moduleName)
        
        result = {}
        storage_serial = module.params["storage_serial"]
        state = module.params["state"]        
        data = json.loads(module.params["data"])
        
        copyType = data.get("copy_type")
        grouping = data.get("grouping")
        consistency_group_id = data.get("consistency_group_id")
        snapshot_grp = data.get("snapshot_grp")
        subtask = data.get("subtask")
        
        if subtask=="":
            subtask=None
        if copyType=="":
            copyType=None
        if grouping=="":
            grouping=None
        if consistency_group_id=="":
            consistency_group_id=None
        if snapshot_grp=="":
            snapshot_grp=None
                        
        logger.writeParam("copyType={}", copyType)        
        logger.writeParam("grouping={}", grouping)        
        logger.writeParam("storage_serial={}", storage_serial)        
#         if copyType is not None and grouping is not None:  
#             raise Exception("Only the grouping or the copy_type can be specified.")
        if copyType is None and grouping is None:  
            raise Exception("Either the grouping or the copy_type must be specified.")
                
        storageSystem = StorageSystem(storage_serial)
        if storageSystem.isVirtualSerialInUse():
            # allow virtual serial for GAD only
            if grouping is not None or copyType != "gad":
                raise Exception("Storage system {0} is not registered. Double-check the serial number or run the hv_storagesystem module with this storage system.".format(storage_serial))
        
        if grouping is not None:
            ## branch to grouping code
            ## NOTE: it does not return, will either exit normally or raise exception
            manageGroup(module, moduleName, state, storageSystem, grouping, subtask, snapshot_grp, consistency_group_id) 

        #####################################################################################################
        #####################################################################################################


        #####################################################################################################
        ### Handle Local and Remote Replications
        

        lun = data.get("lun")
        target_lun = data.get("target_lun", None)
        remote_serial = data.get("target_serial")
        logicalUnit = None
        dataPool = data.get("data_pool", -1)
        mirror_id = data.get("mirror_id", None)
        delete_target_lun = data.get("delete_target_lun", False)
        enable_quick_mode = data.get("enable_quick_mode", True)
                
        if lun=="":
            lun=None
        if target_lun=="":
            target_lun=None
        if remote_serial=="":
            remote_serial=None
        if logicalUnit=="":
            logicalUnit=None
        if dataPool=="":
            dataPool=None
        if mirror_id=="":
            mirror_id=None
        if delete_target_lun=="":
            delete_target_lun=None
        if enable_quick_mode=="":
            enable_quick_mode=None
                
        logger.writeParam("state={}", state)
        logger.writeParam("subtask={}", subtask)
        logger.writeParam("lun={}", lun)
        logger.writeParam("target_lun={}", target_lun)
        logger.writeParam("copyType={}", copyType)        
        
        logger.writeParam("state={}", state)
        logger.writeParam("subtask={}", subtask)
        logger.writeParam("lun={}", lun)
        logger.writeParam("target_lun={}", target_lun)
        logger.writeParam("copyType={}", copyType)        

        auto_split = data.get("auto_split", False)
        ctg_id = data.get("consistency_group_id", -1)
        snapshot_grp = data.get("snapshot_grp", None)
        allocateConsistencyGroup = data.get("allocate_consistency_group", None)
       
        targetResourceId = data.get("target_resource_group_id", None)
        targetPoolId = data.get("target_pool_id", None)
        targetHostGroup = data.get("target_host_group", None)


        if storageSystem.isVirtualSerialInUse() == False:
            if lun is not None:
                logicalUnit = storageSystem.getLun(lun)
            if logicalUnit is None:
                raise Exception("lun not found or was not supplied!")

        if copyType == "ti":
            htiManager = storageSystem.htiManager
            htiPair = None
            if target_lun is not None and str(target_lun) != str(-1):
                # # getHTIPair with target_lun= -1 will return the pair without sVol,
                # # that will stop the createHTI
                module.log(json.dumps(htiManager.getHTIPairs(lun)))
                htiPair = htiManager.getHTIPair(lun, target_lun, mirror_id)
                module.log("HTI Pair: {}".format(htiPair))
            if mirror_id is not None:
                htiPair = htiManager.getHTIPair(lun, target_lun, mirror_id)
                if htiPair is not None:
                    target_lun = htiPair.get("SVol", None)

            if state == "absent":  # Delete mode
                if htiPair is not None:
                    htiManager.deleteHTIPair(lun, target_lun, delete_target_lun)
                    storageSystem.remoteManager.formatPairHTI(htiPair)                    
                    result["pair"] = htiPair
                else:
                    result["comments"] = "There is no HTI Pair for this lun combination."
            elif subtask is None:  # Create mode
                
        	if dataPool < 0:
           	    raise Exception("invalid dataPool value!")

                target_lun = data.get("target_lun", None)
                if target_lun is None:
                    target_lun = -1

                # if target_lun is None:
                    # done in the vro service
                    # target_lun = htiManager.createVVOLAutoNum(lun)
                # elif storageSystem.getLun(target_lun) is None:
                    # done in the vro service
                    # htiManager.createVVOL(lun, target_lun)

                if htiPair is None:

                    # # SIEAN-189
                    if snapshot_grp is not None and str(ctg_id) != "-1":
                        raise Exception("Ambiguous input: when snapshot group is given, consistency group id is not considered.")
                    
                    # # SIEAN-34
                    if snapshot_grp is None and allocateConsistencyGroup is not None:
                        raise Exception("Ambiguous input: allocate_consistency_group is considered only when snapshot group is given.")
                    
                    module.log("Creating HTI Pair")
                    
                    htiPair = htiManager.createHTIPair(lun, target_lun, dataPool,
                              snapshot_grp, ctg_id, auto_split, allocateConsistencyGroup)
                    
                    if type(htiPair) is int:
                        # createPair returns a int for the svol,
                        # the other api returns the pair json
                        svol = htiPair
                        htiPair = htiManager.getHTIPair(lun, svol, None)
                        target_lun = svol
                    else:
                        if htiPair is not None:
                            target_lun = htiPair.get("SVol", None)
                                        
                    # # see SIEAN-133, auto split works fine for 2 out of 3 of the apis,
                    # # only this api has timing issue needs extra code
                    if snapshot_grp is None or (ctg_id is None or str(ctg_id) == "-1"):
                        if auto_split:
                            time.sleep(3.0)
                            # # SIEAN-189, due to timing issue in the back end,
                            # # need to sleep then do another get to make sure it is not already split,
                            # # else we would get he "already split" error msg
                            htiPair = htiManager.getHTIPair(lun, target_lun, None)                            
                            if htiPair["Status"] != ReplicationStatus.PSUS.value:
                                htiManager.splitHTIPair(lun, target_lun, True)
                                htiPair = htiManager.getHTIPair(lun, target_lun, None)                            
                    
                    storageSystem.remoteManager.formatPairHTI(htiPair)                    
                    result["pair"] = htiPair
                else:
                    result["pair"] = htiPair
                    result["comments"] = "HTI Pair (SVOL={0}, MirrorId={1}) already exists!".format(target_lun, htiPair["MirrorId"])
            elif subtask == "split":
                if htiPair is not None:
                    if htiPair["Status"] != ReplicationStatus.PSUS.value:
                        htiManager.splitHTIPair(lun, target_lun, enable_quick_mode)
                    else:
                        result["comments"] = "HTI Pair is already split."
                else:
                    raise Exception("Cannot split: HTI Pair does not exist!")
            elif subtask == "resync":
                if htiPair is not None:
                    if htiPair["Status"] != ReplicationStatus.PAIR.value:
                        htiManager.resyncHTIPair(lun, target_lun, enable_quick_mode)
                    else:
                        result["comments"] = "HTI Pair is already paired."
                else:
                    raise Exception("Cannot resync: HTI Pair does not exist!")
            elif subtask == "restore":
                if htiPair is not None:
                    if htiPair["Status"] != ReplicationStatus.PAIR.value:
                        htiManager.restoreHTIPair(lun, target_lun, enable_quick_mode)
                    else:
                        result["comments"] = "HTI Pair is already paired."
                else:
                    raise Exception("Cannot restore: HTI Pair does not exist!")

        elif copyType == "tc":  # Incomplete, to do in future release
            remote_serial = data.get("target_storage_serial", None)
            copy_pace = data.get("copy_pace", 3)
            enable_read_write = data.get("enable_read_write", False)
            if remote_serial is None:
                raise Exception("Cannot manage TC Pairs without remote_serial param")

            tcManager = storageSystem.remoteManager
            
            # logger.writeInfo("calling getTCPairs")
            tcPair = getTCPairs(storageSystem, lun, None, None)
            if tcPair is not None and len(tcPair) > 0:
                # expect the returned tcPair is a list
                tcPair = tcPair[0]
            else:
                tcPair = None
            # logger.writeInfo("tcPair={}", tcPair)
            
            if state == "absent":  # Delete mode
                if tcPair is None:
                    # the getTCPairs throws an exception in the service,
                    # it does not get here, that is why we don't see this in the output
                    result["comments"] = "TC Pair already deleted." 
                else: 
                    pair = tcManager.deleteTCPair(lun, remote_serial, target_lun)
                    result["PVOL"] = lun
                    if target_lun is not None:
                      result["SVOL"] = target_lun
            elif subtask is None:

                # # createTC
                target_pool_id = data.get("target_pool_id", None)
                target_lun = data.get("target_lun", None)
                if target_pool_id is None and target_lun is None:
                    raise Exception("Either target_pool_id or target_lun is required")
                if target_pool_id  and target_lun :
                    raise Exception("Either target_pool_id or target_lun is allowed, not both")

                if tcPair is not None:
                    tcPair = tcManager.formatPairTC(tcPair)
                    result["pair"] = tcPair
                    result["comments"] = "TC Pair already exists."  
                else:                              
                    if target_pool_id is None:
                        pair = tcManager.createTC(lun, remote_serial, data.get("target_lun", None),
                               data.get("fence_level", None), data.get("consistency_group_id", None),
                               data.get("allocate_consistency_group", False), data.get("copy_pace", 3))
                    else:
                        pair = tcManager.createTC_tpi(lun, remote_serial, target_pool_id,
                               data.get("fence_level", None), data.get("consistency_group_id", None),
                               data.get("allocate_consistency_group", False), data.get("copy_pace", 3))
    
                    pair = tcManager.formatPairTC(pair)
                    result["pair"] = pair

            elif subtask == "resync":
                if tcPair is not None:
                    if tcPair["Status"] != ReplicationStatus.PAIR.value:
                        rsp = tcManager.resyncTC(lun, remote_serial, target_lun, copy_pace)
                        if rsp is None:
                          result["comments"] = "The pair is already in PAIR status."
                    else:
                        result["comments"] = "TC Pair is already in RESYNC state."
                else:
                    raise Exception("Cannot resync: TC Pair does not exist!")
            elif subtask == "split":
                if tcPair is not None:
                    if tcPair["Status"] != ReplicationStatus.PSUS.value:
                        rsp = tcManager.splitTC(lun, remote_serial, target_lun, enable_read_write)
                        if rsp is None:
                          result["comments"] = "The pair is already split."
                    else:
                        result["comments"] = "TC Pair is already split."
                else:
                    raise Exception("Cannot split: TC Pair does not exist!")

        elif copyType == "ur":  # UR Incomplete, to do in future release
            remote_serial = data.get("target_storage_serial", None)
            copy_pace = data.get("copy_pace", 3)
            enable_read_write = data.get("enable_read_write", False)
            if remote_serial is None:
                raise Exception("Cannot manage UR Pairs without remote_serial param")

            tcManager = storageSystem.remoteManager
            tcPair = tcManager.getURPairByPVol(lun, remote_serial, target_lun)
            if state == "absent":  # Delete mode
                # pair=tcManager.deleteRemoteClone(lun, remote_serial, target_lun)
                # result["pair"] = pair
                pair = tcManager.deleteURPair(lun, remote_serial, target_lun)
                # result["comment"] = resp["comment"]
                # result["failed"] = resp["failed"]
                result["PVOL"] = lun
                if target_lun is not None:
                  result["SVOL"] = target_lun
            # elif target_lun is not None:
            #    tcPair = tcManager.getRemoteClones(lun, remote_serial, target_lun)
            #    module.log("TC Pair: {}".format(tcPair))
            elif subtask is None:
                
                    # # createUR

                    oldPair = None
                    if tcPair is not None:
                        oldPair = tcPair.get("PVol", None)                    
                    
                    if oldPair is not None:
                        result["pair"] = tcPair
                        result["comments"] = "UR Pair already exists."  
                    else:                
                        ctg_id = data.get("consistency_group_id", None)
                        allocate_ctg = data.get("allocate_consistency_group", False)
                        if ctg_id is None:
                            # # SIEAN-156 
                            # # from puma: "consistencyGroupId is invalid or allocateConsistencyGroup must be true"
                            allocate_ctg = True
        
                        target_pool_id = data.get("target_pool_id", None)
                        if target_pool_id is None:
                            pair = tcManager.createUR(lun, remote_serial, data.get("target_lun", None),
                               ctg_id,
                               allocate_ctg,
                               data.get("copy_pace", 3),
                               data.get("enable_delta_resync", False),
                               data.get("lun_journal_id", None),
                               data.get("target_lun_journal_id", None))
                        else:
                            pair = tcManager.createUR_tpi(lun, remote_serial, target_pool_id,
                               ctg_id,
                               allocate_ctg,
                               data.get("copy_pace", 3),
                               data.get("enable_delta_resync", False),
                               data.get("lun_journal_id", None),
                               data.get("target_lun_journal_id", None))
    
                        # # FIXME: not sure why this is not the same as createTC,
                        # # the caller would get "No JSON object could be decoded",
                        # # do a GET for now
                        pair = tcManager.getURPairByPVol(lun, remote_serial, target_lun)
                        pair = tcManager.formatPairUR(pair)
                        result["pair"] = pair
            elif subtask == "resync":
                if tcPair is not None:
                    if tcPair["Status"] != ReplicationStatus.PAIR.value:
                        rsp = tcManager.resyncUR(lun, remote_serial, target_lun, copy_pace)
                        if rsp is None:
                          result["comments"] = "The pair is already in PAIR status."
                    else:
                        result["comments"] = "UR Pair is already in RESYNC state."

                else:
                    raise Exception("Cannot resync: UR Pair does not exist!")
            elif subtask == "split":
            	enable_read_write = data.get("enable_read_write", False)
                if tcPair is not None:
                    if tcPair["Status"] != ReplicationStatus.PSUS.value:
                        rsp = tcManager.splitUR(lun, remote_serial, target_lun, enable_read_write)
                        if rsp is None:
                          result["comments"] = "The pair is already split."
                        # tcManager.splitRemoteClone(lun, remote_serial, target_lun)
                    else:
                        result["comments"] = "UR Pair is already split."
                else:
                    raise Exception("Cannot split: UR Pair does not exist!")

        elif copyType == "gad":

            # # GAD Handler
            gadManager = storageSystem.remoteManager
            gadPair = None
            gadPairVbox = None
            if lun is not None:
                pairs = gadManager.getGADPairs(lun)
                if pairs: 
                    gadPair = pairs[0]
                    gadPairVbox = pairs

            if state == "absent":  # Delete mode
                if gadPair is not None:
                    gadManager.deleteGADPair(lun)
                    result["changed"] = True
                    result["PVOL"] = lun
                else:
                    result["comments"] = "The GAD Pair does not exist."
            elif subtask == "split":
                if gadPair is not None:
                    if gadPair["Status"] != ReplicationStatus.PSUS.value:
                        gadManager.splitGADPair(lun)
                        result["changed"] = True
                    else:
                        result["comments"] = "GAD Pair is already split."
                else:
                    raise Exception("Cannot split: GAD Pair does not exist!")
            elif subtask == "resync":
                if gadPair is not None:
                    if gadPair["Status"] != ReplicationStatus.PAIR.value:
                        gadManager.resyncGADPair(lun)
                        result["changed"] = True
                    else:
                        result["comments"] = "GAD Pair is already synced."
                else:
                    raise Exception("Cannot resync: GAD Pair does not exist!")
                
            # Create mode
            elif gadPairVbox is not None and "PVol" in gadPairVbox:
                result["comments"] = "A GAD pair for this PVOL already exists."
            else:
                quorum_disk_id = data.get("quorum_disk_id")
                if quorum_disk_id is None:
                    raise Exception("Quorum Disk ID is required.")
                if targetPoolId is None:
                    raise Exception("Target Pool ID is required.")

                pairs = None
                lun = data.get("lun")
                targetResourceId = data.get("target_resource_group_id", None)
                targetHostGroup = data.get("target_host_group", None)
                ctgID = data.get("consistency_group_id", None)
                allocateCtg = data.get("allocate_consistency_group", False)
                quorum_id = quorum_disk_id
                remote_serial = data.get("target_storage_serial", None)
                if ctgID is None:
                  pairs = gadManager.createGADPairVbox(lun, remote_serial, targetResourceId, quorum_id, targetPoolId, targetHostGroup, allocateCtg)
                else:
                  pairs = gadManager.createGADPairVboxCtgid(lun, remote_serial, targetResourceId, quorum_id, targetPoolId, targetHostGroup, ctgID)

                result["changed"] = True
                if pairs:
                    result["pair"] = Utils.formatGadPair(pairs)

        else:
            raise Exception("Copy Type was not supplied or is invalid!")

        logger.writeExitModule(moduleName)
        module.exit_json(**result)

