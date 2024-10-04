
import time
from typing import Optional, List, Dict, Any
try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes
    from ..common.uaig_utils import UAIGResourceID
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..message.vsp_true_copy_msgs import VSPTrueCopyValidateMsg
    from ..model.vsp_true_copy_models import VSPReplicationPairInfo, VSPReplicationPairInfoList, VSPTrueCopyPairInfoList


except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes
    from common.uaig_utils import UAIGResourceID
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from message.vsp_true_copy_msgs import VSPTrueCopyValidateMsg
    from model.vsp_true_copy_models import VSPReplicationPairInfo, VSPReplicationPairInfoList, VSPTrueCopyPairInfoList

logger = Log()
class VSPTrueCopyProvisioner:

    def __init__(self, connection_info, serial):
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_TRUE_COPY
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
    def get_all_tc_pairs(self, serial=None):
        if serial is None:
            serial = self.serial
        device_id = UAIGResourceID().storage_resourceId(serial)

        ret_list = self.gateway.get_all_true_copy_pairs(device_id)
        # all_rep_pairs = self.gateway.get_all_replication_pairs(device_id)
        # ret_list = []
        # for rp in all_rep_pairs.data:
        #     if rp.type == "TRUE_COPY":
        #         ret_list.append(rp)
        return ret_list

    @log_entry_exit
    def get_tc_for_primary_vol_id(self, primary_vol_id):
        all_tc_pairs = self.get_all_tc_pairs()
        for tc in all_tc_pairs.data:
            if tc.primaryVolumeId == primary_vol_id:
                return tc

        return None

    @log_entry_exit
    def get_true_copy_facts(self, spec=None):
        tc_pairs = self.get_all_tc_pairs()
        logger.writeDebug(f"PV:get_true_copy_facts: tc_pairs=  {tc_pairs}")
        if spec is None:
            return tc_pairs
        else:
            ret_tc_pairs = self.apply_filters(tc_pairs.data, spec)
            return VSPTrueCopyPairInfoList(data=ret_tc_pairs)
        
    @log_entry_exit
    def apply_filters(self, tc_pairs, spec):
        result = tc_pairs
        if spec.primary_volume_id is not None:
            result = self.apply_filter_pvol(result, spec.primary_volume_id)
        if spec.secondary_volume_id is not None:
            result = self.apply_filter_svol(result, spec.secondary_volume_id)
        
        return result

    @log_entry_exit
    def apply_filter_pvol(self, tc_pairs, primary_vol_id):
        ret_val= []
        for tc in tc_pairs:
            if tc.primaryVolumeId == primary_vol_id:
                ret_val.append(tc)
        return ret_val

    @log_entry_exit
    def apply_filter_svol(self, tc_pairs, secondary_vol_id):
        ret_val= []

        for tc in tc_pairs:
            if tc.secondaryVolumeId == secondary_vol_id:
                ret_val.append(tc)
        return ret_val
           
    @log_entry_exit
    def get_replication_pair_by_id(self, pair_id):
        device_id = UAIGResourceID().storage_resourceId(self.serial)
        return self.gateway.get_replication_pair_by_id(device_id, pair_id)

    @log_entry_exit
    def delete_true_copy_pair(self, primary_volume_id):
        self.connection_info.changed = False
        comment = None        
        tc = self.get_tc_for_primary_vol_id(primary_volume_id)
        if tc is None:
            comment = VSPTrueCopyValidateMsg.NO_TC_PAIR_FOR_PRIMARY_VOLUME_ID.value.format(primary_volume_id)
            return tc, comment
        device_id = UAIGResourceID().storage_resourceId(self.serial)
        tc_pair_id = tc.resourceId
        self.connection_info.changed = True
        return self.gateway.delete_true_copy_pair(device_id, tc_pair_id), comment

    @log_entry_exit
    def resync_true_copy_pair(self, primary_volume_id):
        tc = self.get_tc_for_primary_vol_id(primary_volume_id)
        if tc is None:
            raise ValueError(VSPTrueCopyValidateMsg.NO_TC_PAIR_FOR_PRIMARY_VOLUME_ID.value.format(primary_volume_id))
        if tc.status == "PAIR":
            return tc
        device_id = UAIGResourceID().storage_resourceId(self.serial)
        tc_pair_id = tc.resourceId
        rep_pair_id = self.gateway.resync_true_copy_pair(device_id, tc_pair_id)
        pair = self.get_replication_pair_by_id(rep_pair_id)
        self.connection_info.changed = True
        return pair

    @log_entry_exit
    def swap_resync_true_copy_pair(self, primary_volume_id):
        tc = self.get_tc_for_primary_vol_id(primary_volume_id)
        if tc is None:
            raise ValueError(VSPTrueCopyValidateMsg.NO_TC_PAIR_FOR_PRIMARY_VOLUME_ID.value.format(primary_volume_id))
        device_id = UAIGResourceID().storage_resourceId(self.serial)
        tc_pair_id = tc.resourceId
        rep_pair_id = self.gateway.swap_resync_true_copy_pair(device_id, tc_pair_id)
        self.get_replication_pair_by_id(rep_pair_id)

    @log_entry_exit
    def split_true_copy_pair(self, primary_volume_id):
        tc = self.get_tc_for_primary_vol_id(primary_volume_id)
        if tc is None:
            raise ValueError(VSPTrueCopyValidateMsg.NO_TC_PAIR_FOR_PRIMARY_VOLUME_ID.value.format(primary_volume_id))
        if tc.status == "PSUS":
            return tc
        device_id = UAIGResourceID().storage_resourceId(self.serial)
        tc_pair_id = tc.resourceId
        rep_pair_id =  self.gateway.split_true_copy_pair(device_id, tc_pair_id)
        info = self.get_replication_pair_by_id(rep_pair_id)
        self.connection_info.changed = True
        return info

    @log_entry_exit
    def swap_split_true_copy_pair(self, primary_volume_id):
        tc = self.get_tc_for_primary_vol_id(primary_volume_id)
        if tc is None:
            raise ValueError(VSPTrueCopyValidateMsg.NO_TC_PAIR_FOR_PRIMARY_VOLUME_ID.value.format(primary_volume_id))
        device_id = UAIGResourceID().storage_resourceId(self.serial)
        tc_pair_id = tc.resourceId
        rep_pair_id = self.gateway.swap_split_true_copy_pair(device_id, tc_pair_id)
        return self.get_replication_pair_by_id(rep_pair_id)
        
    @log_entry_exit
    def create_true_copy(self, spec) -> Dict[str, Any]:
        
        #Handled idempotency
        tc_exits = self.get_tc_for_primary_vol_id(spec.primary_volume_id)
        if tc_exits: return tc_exits

        consistency_group_id = spec.consistency_group_id or -1
        fence_level = spec.fence_level or "NEVER"
        allocate_new_consistency_group = spec.allocate_new_consistency_group or False

        rr_prov = RemoteReplicationHelperForSVol(self.connection_info, spec.secondary_storage_serial_number)
        # secondary_hostgroups = rr_prov.get_secondary_hg_info()
        secondary_hostgroups = None
        try:
            secondary_hostgroups = rr_prov.get_secondary_hostgroups(spec.secondary_hostgroups)
        except Exception as ex:
            raise ValueError(ex)

        logger.writeDebug(f"PV:create_true_copy: secondary_hostgroups = {secondary_hostgroups}")

        result = self.gateway.create_true_copy(
            spec.primary_volume_id,
            consistency_group_id,
            fence_level,
            allocate_new_consistency_group,
            spec.secondary_storage_serial_number,
            spec.secondary_pool_id,
            secondary_hostgroups       
        )
        logger.writeDebug(f"create_true_copy: {result}")
        # get immediately after create returning Unable to find the resource. give 5 secs 
        time.sleep(5)
        #return self.get_replication_pair_by_id(result)
        pair =  self.get_tc_for_primary_vol_id(spec.primary_volume_id)
        self.connection_info.changed = True
        return pair

    @log_entry_exit
    def check_storage_in_ucpsystem(self) -> bool:
        return self.gateway.check_storage_in_ucpsystem()

    @log_entry_exit
    def get_volume_by_id(self, primary_volume_id):
        device_id = UAIGResourceID().storage_resourceId(self.serial)
        volumes = self.vol_gw.get_volumes(device_id)
        # return vol_gw.get_volume_by_id(device_id, primary_volume_id)
        logger.writeDebug(f"PROV:get_volume_by_id:volumes: {volumes}")

        for v in volumes.data:
            logger.writeDebug(f"PROV:get_volume_by_id:volumes: {v.storageVolumeInfo['ldevId']} ")
            if str(v.storageVolumeInfo['ldevId']) == str(primary_volume_id):
                return v        
        return None

    @log_entry_exit
    def get_volume_by_id_v2(self, storage_id, volume_id):
        volume = self.vol_gw.get_volume_by_id_v2(storage_id, volume_id)
        # return vol_gw.get_volume_by_id(device_id, primary_volume_id)
        logger.writeDebug(f"PROV:get_volume_by_id_v2:volume: {volume}")
        
        return volume

    
class RemoteReplicationHelperForSVol:

    DEFAULT_HOSTGROUP_NAME = "ANSIBLE_DEFAULT_HOSTGROUP"
    DEFAULT_HOST_MODE = "VMWARE_EXTENSION" #"STANDARD"

    def __init__(self, connection_info, serial):
        self.hg_gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_HOST_GROUP
        )
        self.sp_gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.STORAGE_PORT
        )   
        self.connection_info = connection_info
        self.serial = serial
        self.hg_gateway.set_serial(serial)
        self.hg_gateway.set_resource_id()
        self.sp_gateway.set_serial(serial)
        self.sp_gateway.set_resource_id()

    def get_secondary_hostgroups(self, secondary_hostgroups):
        hostgroups_list = self.validate_secondary_hostgroups(secondary_hostgroups)
        payload = self.create_secondary_hgs_payload(hostgroups_list)
        return payload

    def validate_secondary_hostgroups(self, secondary_hgs):
        logger.writeDebug("PROV:validate_secondary_hostgroups:hgs = {}", secondary_hgs)
        logger.writeDebug("PROV:validate_secondary_hostgroups:connection_info = {}", self.connection_info)

        hostgroup_list = []
        for hg in secondary_hgs:
            hostgroup = self.get_hg_by_name_port(hg.name, hg.port)
            if hostgroup is None:
                raise ValueError(VSPTrueCopyValidateMsg.NO_REMOTE_HG_FOUND.value.format(hg.name, hg.port))
            if self.connection_info.subscriber_id is not None:
                if self.connection_info.subscriber_id != hostgroup.subscriberId:
                    logger.writeDebug(f"PROV:validate_secondary_hostgroups:subscribeer_id = {self.connection_info.subscriber_id} hostgroup.subscriberId = {hostgroup.subscriberId}")
                    raise ValueError(VSPTrueCopyValidateMsg.HG_SUBSCRIBER_ID_MISMATCH.value.format(self.connection_info.subscriber_id))
            else:
                if hostgroup.subscriberId is not None:
                    logger.writeDebug(f"PROV:validate_secondary_hostgroups:subscribeer_id None but hostgroup.subscriberId = {hostgroup.subscriberId}")
                    raise ValueError(VSPTrueCopyValidateMsg.NO_SUB_PROVIDED_HG_HAS_SUB.value)
                            
            hostgroup_list.append(hostgroup)

        logger.writeDebug(f"PROV:validate_secondary_hostgroups:hostgroup_list = {hostgroup_list}")

        for hg in secondary_hgs:
            port = self.get_port_by_name(hg.port)
            if port is None:
                raise ValueError(f"Could not find port {hg.port}.")

            # if port.portInfo["portType"] != "FIBRE" or port.portInfo["mode"] != "SCSI":
            #     raise ValueError(VSPTrueCopyValidateMsg.WRONG_PORT_PROVIDED.value.format(port.resourceId, port.portInfo["portType"], port.portInfo["mode"]))
                       
            if self.connection_info.subscriber_id is not None:
                if self.connection_info.subscriber_id != port.subscriberId:
                    logger.writeDebug(f"PROV:validate_secondary_hostgroups:subscribeer_id = {self.connection_info.subscriber_id} port.subscriberId = {port.subscriberId}")
                    raise ValueError(VSPTrueCopyValidateMsg.PORT_SUBSCRIBER_ID_MISMATCH.value.format(self.connection_info.subscriber_id))
            else:
                if port.subscriberId is not None:
                    logger.writeDebug(f"PROV:validate_secondary_hostgroups:subscribeer_id None but port.subscriberId = {port.subscriberId}")       
                    raise ValueError(VSPTrueCopyValidateMsg.NO_SUB_PROVIDED_PORT_HAS_SUB.value)
        
        return hostgroup_list



    @log_entry_exit
    def get_hg_by_name_port(self, name, port):
        hgs = self.hg_gateway.get_host_groups_for_resource_id(self.get_resource_id())
        logger.writeDebug("PROV:get_hg_by_name_port:hgs = {}", hgs)
    
        for hg in hgs.data:
            if hg.hostGroupInfo["hostGroupName"] == name and hg.hostGroupInfo["port"] == port:
                return hg
        
        return None

    @log_entry_exit
    def get_port_by_name(self, port):
        ports = self.sp_gateway.get_all_storage_ports()
        logger.writeDebug("PROV:get_port_by_name:ports = {}", ports)
    
        for p in ports.data:
            if p.resourceId == port:
                return p
        
        return None

    @log_entry_exit
    def create_secondary_hgs_payload(self, hgs):
        ret_list = []
        for hg in hgs:
            item = {}
            item["hostGroupID"] = hg.hostGroupInfo["hostGroupId"]
            item["name"] = hg.hostGroupInfo["hostGroupName"]
            item["port"] = hg.hostGroupInfo["port"]
            item["resourceGroupID"] = hg.hostGroupInfo["resourceGroupId"] or 0
            ret_list.append(item)
        return ret_list

    @log_entry_exit
    def get_resource_id(self):        
        resource_id = UAIGResourceID().storage_resourceId(self.serial)
        logger.writeDebug("GW:get_resource_id:serial = {}  resourceId = {}", self.serial, resource_id)
        return resource_id

    @log_entry_exit
    def get_remote_ucp_serial(self):
        tc_gateway = GatewayFactory.get_gateway(
            self.connection_info, GatewayClassTypes.VSP_TRUE_COPY
        )
        return tc_gateway.get_remote_ucp_serial(self.serial)
    
    @log_entry_exit
    def get_ansible_default_hg(self):
        hgs = self.hg_gateway.get_host_groups_for_resource_id(self.get_resource_id())
        logger.writeDebug("GW:get_ansible_default_hg:hgs = {}", hgs)
    
        for hg in hgs.data:
            if hg.hostGroupInfo["hostGroupName"] == self.get_default_ansible_hg_name():
                return hg
        
        return None
    
    @log_entry_exit
    def get_ansible_default_hg_wo_sub(self):
        hgs = self.hg_gateway.get_host_groups_for_resource_id(self.get_resource_id())
        logger.writeDebug("GW:get_ansible_default_hg_wo_sub:hgs = {}", hgs)
    
        for hg in hgs.data:
            if hg.hostGroupInfo["hostGroupName"] == self.DEFAULT_HOSTGROUP_NAME:
                return hg
        
        return None    

    @log_entry_exit
    def get_secondary_hg_info(self):

        hg = self.get_ansible_default_hg()
        if not hg:
            # we did not find any default ansible host group, so we create one on the first FC port
            first_fc_port = self.get_first_fc_port()
            if first_fc_port is None:
                raise ValueError(VSPTrueCopyValidateMsg.REMOTE_REP_NO_MORE_PORTS_AVAILABLE.value)
            hg = self.create_default_ansible_hg(first_fc_port)
            logger.writeDebug("GW:get_secondary_hg_info:first_fc_port:hg = {}", hg)
            return self.get_secondary_hg_payload(hg)
        else:
            port = self.get_default_ansible_hg_port(hg.hostGroupInfo['port'])
            logger.writeDebug("GW:get_secondary_hg_info:first_fc_port:port = {}", port)
            if port is not None:
                if port.entitlementStatus == "unassigned":
                    self.tag_port(port)
                logger.writeDebug("PROV:get_secondary_hg_info:port ={}", port)
                return self.get_secondary_hg_payload(hg)
            else:
                logger.writeDebug("PROV:get_secondary_hg_info:err: could not find port for hostgroup = {}", hg)
                raise ValueError(VSPTrueCopyValidateMsg.REMOTE_REP_DID_NOT_FIND_PORT.value.format(hg.hostGroupInfo['port']))

    @log_entry_exit
    def get_default_ansible_hg_port(self, port_id):
        self.sp_gateway.set_serial(self.serial)
        self.sp_gateway.set_resource_id()
        ports = self.sp_gateway.get_all_storage_ports_wo_subscriber()
        for port in ports.data:
            logger.writeDebug(f"PROV:get_all_storage_ports_with_subscriber:ports = {port.portInfo['portType']} {port.portInfo['mode']} {port.resourceId} {port_id}" )
            if port.portInfo["portType"] == "FIBRE" and port.portInfo["mode"] == "SCSI" and port.resourceId == port_id:
                return port
        return None

    @log_entry_exit
    def get_all_fc_ports(self):
        self.sp_gateway.set_serial(self.serial)
        self.sp_gateway.set_resource_id()
        ports = self.sp_gateway.get_all_storage_ports()
        logger.writeDebug("GW:get_all_fc_ports:ports = {}", ports)

        fc_ports = []
        if len(ports.data) == 0:
            ports = self.sp_gateway.get_all_storage_ports_wo_subscriber()
            logger.writeDebug("GW:get_all_storage_ports_wo_subscriber:ports = {}", ports)
            # result = self.tag_first_unassigned_port(ports)    
            for port in ports.data:
                if port.portInfo["portType"] == "FIBRE" and port.portInfo["mode"] == "SCSI" and port.entitlementStatus == "unassigned":
                    fc_ports.append(port)
        else:
            for port in ports.data:
                if port.portInfo["portType"] == "FIBRE" and port.portInfo["mode"] == "SCSI":
                    fc_ports.append(port)            
        logger.writeDebug("GW:get_all_fc_ports:fc_ports = {}", fc_ports)
        return fc_ports            


    @log_entry_exit
    def default_ansible_hg_not_present_on_port(self, port):
        hg = self.get_ansible_default_hg_wo_sub()
        if hg is None:
            return True
        else: 
            # if the port of the hostgroup matches with the supplied port
            if str(hg.port) == str(port.portId):
                return False
            else:
                return True
        

    @log_entry_exit
    def get_first_fc_port(self):
        fc_ports = self.get_all_fc_ports()
        logger.writeDebug("PROV:get_first_fc_port:fc_ports = {}", fc_ports)

        for port in fc_ports:
            logger.writeDebug("PROV:get_first_fc_port:port = {}", port)
            if self.connection_info.subscriber_id is not None:
                logger.writeDebug(f"PROV:get_first_fc_port:inside sub = {port.subscriberId} {self.connection_info.subscriber_id}")
                # if the subscriber_id is present we check if this port is belongs to the subscriber
                if port.entitlementStatus == "assigned" and str(port.subscriberId) == str(self.connection_info.subscriber_id):
                    return port
                # the unassigned port we take does not have DEFAULT_HOSTGROUP_NAME
                if port.entitlementStatus == "unassigned" and self.default_ansible_hg_not_present_on_port(port):        
                    self.tag_port(port)
                    return port
            else: 
                if port.entitlementStatus == "unassigned":
                    return port
            
        return None

    @log_entry_exit
    def tag_port(self, port):
        if self.connection_info.subscriber_id == None:
            return
        logger.writeDebug("PROV:tag_port:fc_port = {}", port)
        self.sp_gateway.tag_port(port.storageId, port.resourceId)

    @log_entry_exit
    def get_default_ansible_hg_name(self):
        host_group_name = None
        if self.connection_info.subscriber_id is not None:
            host_group_name = self.DEFAULT_HOSTGROUP_NAME + "_" + self.connection_info.subscriber_id
        else:
            host_group_name = self.DEFAULT_HOSTGROUP_NAME

        return host_group_name  

    @log_entry_exit
    def create_default_ansible_hg(self, port):

        item = {}
        item["hostGroupName"] = self.get_default_ansible_hg_name()
        item["hostMode"] = self.DEFAULT_HOST_MODE
        item["port"] = port.resourceId
        item["ucpSystem"] = self.get_remote_ucp_serial()
        logger.writeDebug("PV:create_default_ansible_hg:item = {}", item)
        hg_id = self.hg_gateway.create_default_host_group(item)
        logger.writeDebug("PROV:create_default_ansible_hg:hg_id = {}", hg_id)
        count = 0
        hg = None
        while hg is None and count < 5:
            hg = self.hg_gateway.get_host_group_by_id(hg_id)
            count += 1
            time.sleep(5)
        return hg

    @log_entry_exit
    def get_secondary_hg_payload(self, hg):
        ret_list = []
        item = {}
        item["hostGroupID"] = hg.hostGroupInfo["hostGroupId"]
        item["name"] = hg.hostGroupInfo["hostGroupName"]
        item["port"] = hg.hostGroupInfo["port"]
        item["resourceGroupID"] = hg.hostGroupInfo["resourceGroupId"] or 0
        ret_list.append(item)
        return ret_list