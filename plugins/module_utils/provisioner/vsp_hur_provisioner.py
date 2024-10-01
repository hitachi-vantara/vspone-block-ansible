from typing import Optional, List, Dict, Any
import time

try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes
    from ..common.uaig_utils import UAIGResourceID
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..model.vsp_hur_models import VSPHurPairInfoList
    from .vsp_true_copy_provisioner import RemoteReplicationHelperForSVol
    from ..message.vsp_hur_msgs import VSPHurValidateMsg
    from .vsp_true_copy_provisioner import RemoteReplicationHelperForSVol

except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes
    from common.uaig_utils import UAIGResourceID
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from model.vsp_hur_models import VSPHurPairInfoList
    from message.vsp_hur_msgs import VSPHurValidateMsg
    from .vsp_true_copy_provisioner import RemoteReplicationHelperForSVol


class VSPHurProvisioner:

    def __init__(self, connection_info, serial):
        self.logger = Log()
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_HUR
        )
        self.vol_gw = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_VOLUME
        )
        self.connection_info = connection_info
        self.serial = serial
        self.gateway.set_storage_serial_number(serial)

    @log_entry_exit
    def get_all_replication_pairs(self, device_id):
        return self.gateway.get_all_replication_pairs(device_id)

    @log_entry_exit
    def get_replication_pair_info_list(self, serial=None):
        if serial is None:
            serial = self.serial
        device_id = UAIGResourceID().storage_resourceId(serial)
        all_rep_pairs = self.gateway.get_all_replication_pairs(device_id)
        
        ## 20240918 - get hur facts with fetchAll=true
        ## we return all hur pairs un-filtered
        ## filter all hur by the storage serial
        ## in either primary or secondary storage
        
        ret_list = []
        for rp in all_rep_pairs.data:
            # self.logger.writeDebug(f"58 rp ={rp}")
            if serial:
                if str(serial) == str(rp.primaryVolumeStorageId) or str(serial) == str(rp.secondaryVolumeStorageId) :
                    ret_list.append(rp) ## 20240805
        return VSPHurPairInfoList(ret_list)

    @log_entry_exit
    def get_hur_pair_info_list(self, serial=None):
        if serial is None:
            serial = self.serial
        device_id = UAIGResourceID().storage_resourceId(serial)
        all_rep_pairs = self.gateway.get_all_replication_pairs(device_id)
        ret_list = []
        for rp in all_rep_pairs.data:
            ret_list.append(rp) ## 20240805
        return VSPHurPairInfoList(ret_list)
    
    @log_entry_exit
    def get_hur_facts(self, spec=None):
        # primary_volume_id = spec.get('primary_volume_id',None)
        primary_volume_id = spec.primary_volume_id
        if spec is None or (spec and primary_volume_id is None):
            return self.get_all_hurpairs()
        else:
            return self.get_all_hur_for_primary_vol_id(primary_volume_id)

    @log_entry_exit
    def get_all_hurpairs(self, serial=None):
        if serial is None:
            serial = self.serial
        device_id = UAIGResourceID().storage_resourceId(serial)
        all_rep_pairs = self.gateway.get_all_replication_pairs(device_id)

        filtered = [
            ssp.to_dict()
            for ssp in all_rep_pairs.data
            if True ## 20240805
        ]
        self.logger.writeDebug(f"filtered={filtered}")
        return filtered

    @log_entry_exit
    def get_hur_for_primary_vol_id(self, primary_vol_id):
        all_hurpairs = self.get_replication_pair_info_list()
        
        # 20240808 - one pvol can have 3 pairs, this only returns the first pair
        for tc in all_hurpairs.data:
            if tc.primaryVolumeId == primary_vol_id:
                return tc

        return None
    
    # 20240808 - get_hur_by_pvol_mirror, mirror id support 
    @log_entry_exit
    def get_hur_by_pvol_mirror(self, primary_vol_id, mirror_unit_id):
        all_hurpairs = self.get_replication_pair_info_list()
        
        for tc in all_hurpairs.data:
            if tc.primaryVolumeId == primary_vol_id and \
               tc.mirrorUnitId == mirror_unit_id :
                return tc

        return None 
       
    ## get_hur_facts_ext
    @log_entry_exit
    def get_hur_facts_ext(self, 
        pvol: Optional[int] = None, 
        svol: Optional[int] = None,
        mirror_unit_id: Optional[int] = None
    ):
        all_hurpairs = self.get_replication_pair_info_list()
        self.logger.writeDebug(f"all_hurpairs={all_hurpairs}")
        
        # 20240812 - get_hur_facts_ext
        result = [
            ssp
            for ssp in all_hurpairs.data
            if  (pvol is None or ssp.primaryVolumeId == pvol)
            and (svol is None or ssp.secondaryVolumeId == svol)
            and (mirror_unit_id is None or ssp.mirrorUnitId == mirror_unit_id)
        ]
        self.logger.writeDebug(f"result={result}")

        return result      
           
    @log_entry_exit
    def get_all_hur_for_primary_vol_id(self, primary_vol_id):
        all_hurpairs = self.get_replication_pair_info_list()
        
        # 20240808 - one pvol can have 3 pairs
        result = []
        for tc in all_hurpairs.data:
            if tc.primaryVolumeId == primary_vol_id:
                result.append(tc)

        return result        
           
    @log_entry_exit
    def get_hur_by_pvol_svol(self, pvol, svol):
        all_hurpairs = self.get_replication_pair_info_list()
        
        # 20240912 - get_hur_by_pvol_svol
        result = None
        
        for tc in all_hurpairs.data:
            if str(tc.primaryVolumeId) == pvol and str(tc.secondaryVolumeId) == svol :
                self.logger.writeDebug(f"151 tc: {tc}")
                result = tc
                break
                
        return result        
    
    @log_entry_exit
    def get_replication_pair_by_id(self, pair_id):
        device_id = UAIGResourceID().storage_resourceId(self.serial)
        pairs =  self.get_all_replication_pairs(device_id)
        for pair in pairs.data:
            if pair.resourceId == pair_id:
                return pair
        return None

    # 20240808 delete_hur_pair
    @log_entry_exit
    def delete_hur_pair(self, primary_volume_id, mirror_unit_id):
        self.connection_info.changed = False
        comment = None
        tc = self.get_hur_by_pvol_mirror(primary_volume_id, mirror_unit_id)
        if tc is None:
            # 20240908 delete_hur_pair Idempotent
            comment = VSPHurValidateMsg.PRIMARY_VOLUME_ID_DOES_NOT_EXIST.value.format(primary_volume_id)
            return tc, comment
            
        device_id = UAIGResourceID().storage_resourceId(self.serial)
        hurpair_id = tc.resourceId
        self.logger.writeDebug(f"device_id: {device_id}")
        self.logger.writeDebug(f"hurpair_id: {hurpair_id}")
        self.connection_info.changed = True
        return self.gateway.delete_hur_pair(device_id, hurpair_id), comment

    @log_entry_exit
    def resync_hur_pair(self, primary_volume_id, mirror_unit_id):
        tc = self.get_hur_by_pvol_mirror(primary_volume_id, mirror_unit_id)
        self.connection_info.changed = False
        if tc is None:
            raise ValueError(VSPHurValidateMsg.PRIMARY_VOLUME_ID_DOES_NOT_EXIST.value.format(primary_volume_id))
        
        comment = None
        if tc.status == "PAIR":
            comment = VSPHurValidateMsg.NO_RESYNC_NEEDED.value.format(
                tc.primaryVolumeId, tc.primaryVolumeStorageId,
                tc.secondaryVolumeId, tc.secondaryVolumeStorageId)
            return tc, comment
        
        device_id = UAIGResourceID().storage_resourceId(self.serial)
        tc_pair_id = tc.resourceId
        rep_pair_id = self.gateway.resync_hur_pair(device_id, tc_pair_id)
        self.logger.writeDebug(f"rep_pair_id: {rep_pair_id}")
        self.connection_info.changed = True
        info = self.get_replication_pair_by_id(rep_pair_id)
        self.logger.writeDebug(f"info: {info}")
        return info, comment

    @log_entry_exit
    def swap_resync_hur_pair(self, primary_volume_id):
        tc = self.get_hur_for_primary_vol_id(primary_volume_id)
        if tc is None:
            raise ValueError(VSPHurValidateMsg.PRIMARY_VOLUME_ID_DOES_NOT_EXIST.value.format(primary_volume_id))
        device_id = UAIGResourceID().storage_resourceId(self.serial)
        tc_pair_id = tc.resourceId
        rep_pair_id = self.gateway.swap_resync_hur_pair(device_id, tc_pair_id)
        self.get_replication_pair_by_id(rep_pair_id)

    @log_entry_exit
    def split_hur_pair(self, primary_volume_id, mirror_unit_id):
        tc = self.get_hur_by_pvol_mirror(primary_volume_id, mirror_unit_id)
        if tc is None:
            raise ValueError(VSPHurValidateMsg.PRIMARY_VOLUME_AND_MU_ID_WRONG.value.format(primary_volume_id, mirror_unit_id))
        
        comment = None
        self.connection_info.changed = False
        if tc.status == "PSUS":
            comment = VSPHurValidateMsg.ALREADY_SPLIT_PAIR.value.format(
                tc.primaryVolumeId, tc.primaryVolumeStorageId,
                tc.secondaryVolumeId, tc.secondaryVolumeStorageId)
            return tc, comment
            
        device_id = UAIGResourceID().storage_resourceId(self.serial)
        tc_pair_id = tc.resourceId
        rep_pair_id =  self.gateway.split_hur_pair(device_id, tc_pair_id)
        self.connection_info.changed = True
        self.logger.writeDebug(f"rep_pair_id: {rep_pair_id}")
        return self.get_replication_pair_by_id(rep_pair_id), comment

    @log_entry_exit
    def swap_split_hur_pair(self, primary_volume_id):
        tc = self.get_hur_for_primary_vol_id(primary_volume_id)
        if tc is None:
            raise ValueError(VSPHurValidateMsg.PRIMARY_VOLUME_ID_DOES_NOT_EXIST.value.format(primary_volume_id))
        device_id = UAIGResourceID().storage_resourceId(self.serial)
        tc_pair_id = tc.resourceId
        rep_pair_id = self.gateway.swap_split_hur_pair(device_id, tc_pair_id)
        return self.get_replication_pair_by_id(rep_pair_id)
    
    ## 20240830 convert HostGroupTC to HostGroupHUR 
    def convert_secondary_hostgroups(self, secondary_hostgroups):
        hgs = []
        for hg in secondary_hostgroups:
            ## we just take the first one
            ## not expect more than one
            del hg["hostGroupID"]
            del hg["resourceGroupID"]
            hgs.append(hg)
            return hgs
            
    ## 20240808 - prov.create_hur
    @log_entry_exit
    def create_hur(self, spec) -> Dict[str, Any]:
        
        consistency_group_id = spec.consistency_group_id or -1
        enable_delta_resync = spec.enable_delta_resync or False
        allocate_new_consistency_group = spec.allocate_new_consistency_group or False
   
        ## 20240808 - get secondary_hostgroups from RemoteReplicationHelperForSVol
        rr_prov = RemoteReplicationHelperForSVol(self.connection_info, spec.secondary_storage_serial_number)
        # secondary_hostgroups = rr_prov.get_secondary_hg_info()
        secondary_hostgroups = None
        try:
            secondary_hostgroups = rr_prov.get_secondary_hostgroups(spec.secondary_hostgroups)
        except Exception as ex:
            raise ValueError(ex)        
        self.logger.writeDebug(f"PV: 199 create_hur: rr_prov=  {rr_prov} secondary_hostgroups = {secondary_hostgroups}")
        
        secondary_hostgroups = self.convert_secondary_hostgroups(secondary_hostgroups)

        ##20240912 - hur get by pvol svol
        pvol, svol = self.gateway.create_hur(
            spec.primary_volume_id,
            consistency_group_id,
            enable_delta_resync,
            allocate_new_consistency_group,
            spec.secondary_storage_serial_number,
            spec.secondary_pool_id,
            
            ## 20240808 - do we always ignore the spec.secondary_hostgroups?
            # or it will be another option later
            # spec.secondary_hostgroups, 
            secondary_hostgroups,     
                
            spec.primary_volume_journal_id,     
            spec.secondary_volume_journal_id,     
        )
        
        ## id of the newly created pair
        self.logger.writeDebug(f"from create_hur pvol: {pvol}")
        self.logger.writeDebug(f"from create_hur svol: {svol}")

        if svol is None:
            hurPairResourceId = pvol
            ## 20240808 - get_hur_by hurPairResourceId
            return self.get_replication_pair_by_id(hurPairResourceId)
        else:
            
            # 20240912 - get_hur_by_pvol_svol retry
            response = None
            retryCount = 0
            while response is None and retryCount < 60:
                retryCount = retryCount + 1
                response=self.get_hur_by_pvol_svol(pvol, svol)        
                if response:
                    break
                time.sleep(1) 
                continue
            
            return response

    @log_entry_exit
    def check_storage_in_ucpsystem(self) -> bool:
        return self.gateway.check_storage_in_ucpsystem()
    
    @log_entry_exit
    def get_volume_by_id(self, primary_volume_id):
        device_id = UAIGResourceID().storage_resourceId(self.serial)
        volumes = self.vol_gw.get_volumes(device_id)
        # return vol_gw.get_volume_by_id(device_id, primary_volume_id)
        self.logger.writeDebug(f"PROV:get_volume_by_id:volumes: {volumes}")

        for v in volumes.data:
            self.logger.writeDebug(f"PROV:get_volume_by_id:volumes: {v.storageVolumeInfo['ldevId']} ")
            if str(v.storageVolumeInfo['ldevId']) == str(primary_volume_id):
                return v        
        return None

    @log_entry_exit
    def get_volume_by_id_v2(self, storage_id, volume_id):
        volume = self.vol_gw.get_volume_by_id_v2(storage_id, volume_id)
        # return vol_gw.get_volume_by_id(device_id, primary_volume_id)
        self.logger.writeDebug(f"PROV:get_volume_by_id_v2:volume: {volume}")
        
        return volume