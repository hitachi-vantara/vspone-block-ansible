import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.hv_infra import StorageSystem, HostMode, Utils, StorageSystemManager
from ansible.module_utils.hv_htimanager import ReplicationStatus
from ansible.module_utils.hv_htimanager import HtiPairType
from ansible.module_utils.hv_logger import MessageID
from ansible.module_utils.hv_log import Log, HiException

logger=Log()
moduleName="Replication facts"

def getURPairs( storageSystem, lun, remote_serial, target_lun):
        if lun != -1:
            rclist = storageSystem.remoteManager.getRemoteClones(lun, remote_serial, None)
            pairs = [pair for pair in rclist if pair["Type"] == 6 and str(pair["PVol"]) == str(lun)]
        else:
            rclist = storageSystem.remoteManager.getRemoteClones(lun, remote_serial, target_lun)
            pairs = [pair for pair in rclist if pair["Type"] == 6]
        return pairs

def getTCPairs( storageSystem, lun, remote_serial, target_lun):
        if lun != -1:
            ## SIEAN-188 not able to use the GetTrueCopyPairs api, it wants the remote_serial,
            ## but we want to do noSVOL, so we will do it this way
            rclist = storageSystem.remoteManager.getTrueCopyPairsList(lun, remote_serial, target_lun)
            pairs = [pair for pair in rclist if pair["Type"] == "TRUE_COPY" and str(pair["PVol"]) == str(lun)]
        else:
            pairs = storageSystem.remoteManager.getTrueCopyPairsList(lun, remote_serial, target_lun)
            #pairs = [pair for pair in rclist if pair["Type"] == 5]
        return pairs
                    
def getGroupFacts(module, moduleName, storageSystem, grouping, snapshot_grp, consistency_group_id):
    pairs = []
            
    logger.writeEnter("getGroupFacts")
    logger.writeParam("grouping={}", grouping)
    
    if grouping is not None:
        if grouping == "snapshot group":
            logger.writeParam("snapshot_grp={}", snapshot_grp)
            pass
        if grouping == "consistency group":
            logger.writeParam("consistency_group_id={}", consistency_group_id)
            pass
         
    logger.writeExitModule(moduleName)
    module.exit_json(pairs=pairs)
                    
def runPlaybook(module):

        logger.writeEnterModule(moduleName)
        
        data = json.loads(module.params["data"])

        lun = data.get("lun", -1)
        target_lun = data.get("target_lun")
        copyType = data.get("copy_type")
        grouping = data.get("grouping")
        
        logger.writeParam("lun={}", lun)
        logger.writeParam("target_lun={}", target_lun)
        logger.writeParam("copyType={}", copyType)
        
        storageSystem = StorageSystem(module.params["storage_serial"])
        
        if copyType is None:
            getGroupFacts(module, moduleName, storageSystem, grouping, snapshot_grp, consistency_group_id)
        
        # allow virtual serial for GAD only
        if copyType != "gad" and storageSystem.isVirtualSerialInUse():
            raise Exception("Storage system {0} is not registered. Double-check the serial number or run the hv_storagesystem module with this storage system.".format(module.params["storage_serial"]))

        pairs = []

        if copyType == "ti":
            #Utils.logDebug("lun={0}".format(lun))
            pairs = storageSystem.htiManager.getHTIPairs(lun)
            if target_lun is not None:
                pairs = [pair for pair in pairs if str(pair.get("SVol")) == str(target_lun)]
            for pair in pairs:
                storageSystem.remoteManager.formatPairHTI(pair)
        elif copyType == "ur":
            #TODO: filter for UR from the list
            pairs = getURPairs(storageSystem, lun, None, None)
            pairs = storageSystem.remoteManager.getURPairsFromAll(pairs, lun)
        elif copyType == "tc":
            #TODO: filter for TC from the list
            pairs = getTCPairs(storageSystem, lun, None, None)
            #pairs = storageSystem.remoteManager.getTCPairsFromAll(pairs, lun)
        elif copyType == "gad":
            pairs = storageSystem.remoteManager.getGADPairs(lun)
            if target_lun is not None:
                pairs = [pair for pair in pairs if str(pair.get("SVol")) == str(target_lun)]
            for pair in pairs:
                Utils.formatGadPair(pair)

        logger.writeExitModule(moduleName)
        module.exit_json(pairs=pairs)

