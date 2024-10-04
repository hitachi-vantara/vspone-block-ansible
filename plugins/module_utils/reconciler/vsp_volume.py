try:
    from ..common.ansible_common import (
        convert_block_capacity,
        convert_to_bytes,
        log_entry_exit,
        camel_to_snake_case,
        camel_array_to_snake_case,
        snake_to_camel_case,
        process_size_string,
        get_response_key,
        volume_id_to_hex_format,
    )
    from ..common.uaig_utils import camel_to_snake_case_dict
    from ..common.hv_log import Log
    from ..common.hv_constants import StateValue
    from ..common.vsp_constants import VolumePayloadConst
    from ..model.common_base_models import ConnectionInfo
    from ..model.vsp_volume_models import (
        CreateVolumeSpec,
        VolumeFactSpec,
        VSPVolumeInfo,
        VSPVolumesInfo,
        VSPVolumeDetailInfo,
        VSPVolumeDetailInfoList,
        VSPVolumeSnapshotInfo,
        VSPVolumePortInfo,
        VSPVolumeNvmSubsystenInfo,
    )
    from ..provisioner.vsp_volume_prov import VSPVolumeProvisioner
    from ..provisioner.vsp_nvme_provisioner import VSPNvmeProvisioner
    from ..provisioner.vsp_storage_port_provisioner import VSPStoragePortProvisioner
    from ..provisioner.vsp_snapshot_provisioner import VSPHtiSnapshotProvisioner
    from ..message.vsp_lun_msgs import VSPVolValidationMsg
except ImportError:
    from common.ansible_common import (
        convert_block_capacity,
        convert_to_bytes,
        log_entry_exit,
        snake_to_camel_case,
        camel_to_snake_case,
        camel_array_to_snake_case,
        process_size_string,
        get_response_key,
        volume_id_to_hex_format,
    )
    from common.uaig_utils import camel_to_snake_case_dict
    from common.hv_log import Log
    from common.hv_constants import StateValue
    from common.vsp_constants import VolumePayloadConst
    from model.common_base_models import ConnectionInfo
    from model.vsp_volume_models import (
        CreateVolumeSpec,
        VolumeFactSpec,
        VSPVolumeInfo,
        VSPVolumesInfo,
        VSPVolumeDetailInfo,
        VSPVolumeDetailInfoList,
        VSPVolumeSnapshotInfo,
        VSPVolumePortInfo,
        VSPVolumeNvmSubsystenInfo,
    )    
    from provisioner.vsp_volume_prov import VSPVolumeProvisioner
    from provisioner.vsp_nvme_provisioner import VSPNvmeProvisioner
    from provisioner.vsp_storage_port_provisioner import VSPStoragePortProvisioner
    from provisioner.vsp_snapshot_provisioner import VSPHtiSnapshotProvisioner
    from message.vsp_lun_msgs import VSPVolValidationMsg

logger = Log()

class VSPVolumeSubstates:
    """
    Enum class for VSP Volume Substates
    """
    ADD_HOST_NQN = "add_host_nqn"
    REMOVE_HOST_NQN = "remove_host_nqn"

class VSPVolumeReconciler:
    """_summary_"""

    def __init__(self, connection_info: ConnectionInfo, serial: str):
        self.connection_info = connection_info
        self.serial = serial
        self.provisioner = VSPVolumeProvisioner(self.connection_info)
        self.port_prov = VSPStoragePortProvisioner(self.connection_info)
        self.nvme_provisioner = VSPNvmeProvisioner(self.connection_info, self.serial)

    @log_entry_exit
    def volume_reconcile(self, state: str, spec: CreateVolumeSpec):
        """Reconciler for volume management"""

        if state == StateValue.PRESENT:

            if spec.ldev_id is None and spec.name is None and spec.nvm_subsystem_name and spec.state is not None and spec.state == VSPVolumeSubstates.REMOVE_HOST_NQN :
                # ldev_id and name not present in the spec, but nvm_subsystem_name present
                self.update_nvm_subsystem(spec)
                return "NVM subsystem updated successfully."
            
            volume = None
            if spec.ldev_id:
                volume = self.provisioner.get_volume_by_ldev(spec.ldev_id)

            if not volume or volume.emulationType == VolumePayloadConst.NOT_DEFINED:
                spec.ldev_id = self.create_volume(spec)
                if spec.name:
                    self.update_volume_name(spec.ldev_id, spec.name)
            else:
                self.update_volume(volume, spec)
            
            vol = self.provisioner.get_volume_by_ldev(spec.ldev_id)
            return self.get_volume_detail_info(vol)

        elif state == StateValue.ABSENT:
            volume = self.provisioner.get_volume_by_ldev(spec.ldev_id)
            logger.writeDebug("RC:volume_reconcile:state=absent:volume={}", volume)
            if not volume or volume.emulationType == VolumePayloadConst.NOT_DEFINED:
                return None
            if spec.force is not None and spec.force == True:
                self.delete_volume_force(volume)
            else:
                if volume.numOfPorts and volume.numOfPorts > 0:
                    raise ValueError(VSPVolValidationMsg.PATH_EXIST.value)
                self.delete_volume(volume)

    @log_entry_exit
    def update_nvm_subsystem(self, spec):
            found = self.does_nvme_subsystem_exist(spec.nvm_subsystem_name)
            if not found:
                raise ValueError(VSPVolValidationMsg.NVM_SUBSYSTEM_DOES_NOT_EXIST.value.format(spec.nvm_subsystem_name))
            else:
                logger.writeDebug("RC:process_update_nvme:nvm_system={}", found)
                self.process_update_nvme(found, spec)

    @log_entry_exit
    def update_volume(self, volume_data: VSPVolumeInfo, spec: CreateVolumeSpec):
        found = False
        if spec.nvm_subsystem_name:
            found = self.does_nvme_subsystem_exist(spec.nvm_subsystem_name)
            if not found:
                raise ValueError(VSPVolValidationMsg.NVM_SUBSYSTEM_DOES_NOT_EXIST.value.format(spec.nvm_subsystem_name))
            else:
                logger.writeDebug("RC:process_update_nvme:nvm_system={}", found)

        # Expand the size if its required
        if spec.size:
            if "." in spec.size:
                raise ValueError(VSPVolValidationMsg.SIZE_INT_REQUIRED.value)

            size_in_bytes = convert_to_bytes(spec.size)
            expand_val = size_in_bytes - (
                volume_data.blockCapacity if volume_data.blockCapacity else 0
            )
            if expand_val > 0:
                enhanced_expansion = (
                    True
                    if volume_data.isDataReductionShareEnabled is not None
                    else False
                )
                self.provisioner.expand_volume_capacity(
                    volume_data.ldevId, expand_val, enhanced_expansion
                )
                self.connection_info.changed = True
            elif expand_val < 0:
                raise ValueError(VSPVolValidationMsg.VALID_SIZE.value)

        # update the volume by comparing the existing details
        if (
            spec.capacity_saving
            and spec.capacity_saving != volume_data.dataReductionMode
        ) or (spec.name and spec.name != volume_data.label):
            self.provisioner.change_volume_settings(
                volume_data.ldevId, spec.name, spec.capacity_saving
            )
            self.connection_info.changed = True
        if found:
            self.process_update_nvme(found, spec)
        return volume_data.ldevId

    @log_entry_exit
    def does_nvme_subsystem_exist(self, nvm_subsystem_name):
        ret_list = self.nvme_provisioner.get_nvme_subsystem_by_name(nvm_subsystem_name)
        if len(ret_list) == 0:
            return False
        else:
            return ret_list[0]

    @log_entry_exit
    def process_create_nvme(self, nvme_subsystem, spec):
        # if spec.state is None or empty during create, we will try to 
        # add host NQNs, based on the information provided in the spec.
        if spec.state == None or spec.state =="" or spec.state.lower() == VSPVolumeSubstates.ADD_HOST_NQN:
            if spec.host_nqns is not None and len(spec.host_nqns) > 0:
                logger.writeDebug("RC:host_nqns={}", spec.host_nqns)
                host_nqns_to_register = self.get_host_nqns_to_register(nvme_subsystem.nvmSubsystemId, spec.host_nqns)
                logger.writeDebug("RC:host_nqns_to_register={}", host_nqns_to_register)
                self.register_host_nqns(nvme_subsystem.nvmSubsystemId, host_nqns_to_register)
                ldev_found = self.is_ldev_present(nvme_subsystem.nvmSubsystemId, spec.ldev_id)
                logger.writeDebug("RC:process_create_nvme={}", ldev_found)
                if not ldev_found:
                    #add ldev to the nvme name space
                    object_id = self.create_namespace_for_ldev(nvme_subsystem.nvmSubsystemId, spec.ldev_id)
                    namespace_id = object_id.split(",")[-1]
                    logger.writeDebug("RC:namespace_id={}", namespace_id)
                else:
                    namespace_id = ldev_found.namespaceId
                    logger.writeDebug("RC:ldev_found={}", ldev_found)
            
                self.set_host_namespace_paths(nvme_subsystem.nvmSubsystemId, spec.host_nqns, namespace_id)
            else:
                ldev_found = self.is_ldev_present(nvme_subsystem.nvmSubsystemId, spec.ldev_id)
                logger.writeDebug("RC:process_create_nvme={}", ldev_found)
                if not ldev_found:
                    #add ldev to the nvme name space
                    object_id = self.create_namespace_for_ldev(nvme_subsystem.nvmSubsystemId, spec.ldev_id)
                    namespace_id = object_id.split(",")[-1]
                    logger.writeDebug("RC:namespace_id={}", namespace_id)
                else:
                    namespace_id = ldev_found.namespaceId
                    logger.writeDebug("RC:ldev_found={}", ldev_found)

    @log_entry_exit
    def set_host_namespace_paths(self, nvme_subsystem_id, hpst_nqns, namespace_id):
        for h in hpst_nqns:
            try:
                self.nvme_provisioner.set_host_namespace_path(nvme_subsystem_id, h, namespace_id)
                self.connection_info.changed = True
            except Exception as e:
                logger.writeDebug("RC:set_host_namespace_paths={}", str(e))
                logger.writeDebug("RC:set_host_namespace_paths:nvme_subsystem_id={} host_nqn = {} namespace_id = {}", nvme_subsystem_id, h, namespace_id)

        
    @log_entry_exit
    def create_namespace_for_ldev(self, nvme_subsystem_id, ldev_id):
        ret_value = self.nvme_provisioner.create_namespace(nvme_subsystem_id, ldev_id)
        self.connection_info.changed = True
        logger.writeDebug("RC:create_namespace_for_ldev={}", ret_value)

        return ret_value
    
    @log_entry_exit
    def is_ldev_present(self, nvme_subsystem_id, ldev_id):
        ret_list = self.nvme_provisioner.get_namespaces(nvme_subsystem_id)
        logger.writeDebug("RC:is_ldev_present={}", ret_list)
        for x in ret_list.data:
            if str(x.ldevId) == str(ldev_id):
                return x
        return False

    @log_entry_exit
    def register_host_nqns(self, nvme_subsystem_id, host_nqns):
        logger.writeDebug("RC:register_host_nqns={}", host_nqns)
        for x in host_nqns:
            self.nvme_provisioner.register_host_nqn(nvme_subsystem_id, x)
            self.connection_info.changed = True

    @log_entry_exit
    def get_host_nqns_to_register(self, nvme_subsystem_id, host_nqns):
        ret_list = self.nvme_provisioner.get_host_nqns(nvme_subsystem_id)
        host_nqn_dict = {}
        for host_nqn in ret_list.data:
            host_nqn_dict[host_nqn.hostNqn] = host_nqn
        
        result_list = []
        for x in host_nqns:
            if host_nqn_dict.get(x) is None:
                result_list.append(x)
        
        return result_list

    @log_entry_exit
    def process_update_nvme(self, nvme_subsystem, spec):

        # During update if spec.state is None, we just return
        if spec.state is None:
            return

        if spec.state.lower() == VSPVolumeSubstates.REMOVE_HOST_NQN:
            if spec.ldev_id is None:
              self.process_remove_host_nqns(nvme_subsystem, spec.host_nqns)
            else:
                self.remove_hqn_from_exiting_vol(nvme_subsystem, spec.host_nqns, spec.ldev_id)
        elif spec.state.lower() == VSPVolumeSubstates.ADD_HOST_NQN:
            if spec.ldev_id is None:
                return
            else:
                self.process_add_host_nqns(nvme_subsystem, spec.host_nqns, spec.ldev_id)
        else:
            return

    @log_entry_exit
    def process_add_host_nqns(self, nvme_subsystem, host_nqns, ldev_id):
        logger.writeDebug("RC:process_add_host_nqns:nvme_system={}", nvme_subsystem)
        if host_nqns is not None and len(host_nqns) > 0:
            host_nqns_to_register = self.get_host_nqns_to_register(nvme_subsystem.nvmSubsystemId, host_nqns)            
            logger.writeDebug("RC:process_add_host_nqns:host_nqns_to_register={}", host_nqns_to_register)
            self.register_host_nqns(nvme_subsystem.nvmSubsystemId, host_nqns_to_register)
            ldev_found = self.is_ldev_present(nvme_subsystem.nvmSubsystemId, ldev_id)
            logger.writeDebug("RC:process_add_host_nqns:ldev_found={} ldev_id = {} ldev type = {}", ldev_found, ldev_id, type(ldev_id))
            if not ldev_found:
                #add ldev to the nvme name space
                object_id = self.create_namespace_for_ldev(nvme_subsystem.nvmSubsystemId, ldev_id)
                namespace_id = object_id.split(",")[-1]
                logger.writeDebug("RC:namespace_id={}", namespace_id)
            else:
                namespace_id = ldev_found.namespaceId
                logger.writeDebug("RC:ldev_found={}", ldev_found)
            
            self.set_host_namespace_paths(nvme_subsystem.nvmSubsystemId, host_nqns, namespace_id)
        else:
            # If host_nqns is empty just create the namespace for ldev_id
            ldev_found = self.is_ldev_present(nvme_subsystem.nvmSubsystemId, ldev_id)
            logger.writeDebug("RC:process_create_nvme={}", ldev_found)
            if not ldev_found:
                #add ldev to the nvme name space
                object_id = self.create_namespace_for_ldev(nvme_subsystem.nvmSubsystemId, ldev_id)
                namespace_id = object_id.split(",")[-1]
                logger.writeDebug("RC:namespace_id={}", namespace_id)
            else:
                namespace_id = ldev_found.namespaceId
                logger.writeDebug("RC:ldev_found={}", ldev_found)

    @log_entry_exit
    def remove_hqn_from_nvm_subsystem(self, nvm, host_nqn):
        host_nqns = self.find_host_nqn_in_nvm_subsystem(nvm.nvmSubsystemId, host_nqn)
        if host_nqns and len(host_nqns) > 0:
            for x in host_nqns:
                self.nvme_provisioner.delete_host_nqn_by_id(x.hostNqnId)

    @log_entry_exit
    def remove_hqn_from_exiting_vol(self, nvme_subsystem, host_nqns, ldev_id):
        logger.writeDebug("RC:remove_hqn_from_exiting_vol:nvme_system={}", nvme_subsystem)
        ldev_found = self.is_ldev_present(nvme_subsystem.nvmSubsystemId, ldev_id)
        if not ldev_found:
            raise ValueError(VSPVolValidationMsg.LDEV_NOT_FOUND_IN_NVM.value.format(ldev_id, nvme_subsystem.nvmSubsystemName))
        else:
            host_nqns_to_remove = self.get_host_nqns_to_remove(nvme_subsystem.nvmSubsystemId, host_nqns)
            logger.writeDebug("RC:remove_hqn_from_exiting_vol:host_nqns_to_remove={}", host_nqns_to_remove)
            ldev_paths = self.find_ldevs_in_paths(nvme_subsystem.nvmSubsystemId, ldev_id)
            logger.writeDebug("RC:remove_hqn_from_exiting_vol:ldev_paths={}", ldev_paths)
            if ldev_paths and len(ldev_paths) > 0:
                for x in ldev_paths:
                    logger.writeDebug("RC:remove_hqn_from_exiting_vol:x={}", x)
                    if x.hostNqn in host_nqns_to_remove:
                        self.nvme_provisioner.delete_host_namespace_path_by_id(x.namespacePathId)
                        logger.writeDebug("RC:remove_hqn_from_exiting_vol:x={}", x)
                        paths = self.find_host_nqn_in_paths(nvme_subsystem.nvmSubsystemId, x.hostNqn)
                        logger.writeDebug("RC:remove_hqn_from_exiting_vol:paths={}", paths)
                        if len(paths) == 0:
                            logger.writeDebug("RC:remove_hqn_from_exiting_vol:remove_hqn_from_nvm_subsystem")
                            self.remove_hqn_from_nvm_subsystem(nvme_subsystem, x.hostNqn)


    @log_entry_exit
    def process_remove_host_nqns(self, nvme_subsystem, host_nqns):

        host_nqns_to_remove = self.get_host_nqns_to_remove(nvme_subsystem.nvmSubsystemId, host_nqns)
        logger.writeDebug("RC:process_remove_host_nqn:host_nqns_to_remove={}", host_nqns_to_remove)
        if len(host_nqns_to_remove) > 0:
            self.delete_host_nqns_from_nvme_subsystem(host_nqns_to_remove)
            self.connection_info.changed = True

    @log_entry_exit
    def get_host_nqns_to_remove(self, nvme_subsystem_id, host_nqns):
        ret_list = self.nvme_provisioner.get_host_nqns(nvme_subsystem_id)
        host_nqn_dict = {}
        for host_nqn in ret_list.data:
            host_nqn_dict[host_nqn.hostNqn] = host_nqn

        result_list = []
        for x in host_nqns:
            if host_nqn_dict.get(x):
                result_list.append(x)
        
        return result_list 
  
    @log_entry_exit
    def create_volume(self, spec: CreateVolumeSpec):
        logger.writeDebug("RC:create_volume:spec={}", spec)
        if spec.pool_id is not None and spec.parity_group:
            raise ValueError(VSPVolValidationMsg.POOL_ID_PARITY_GROUP.value)
        if spec.pool_id is None and not spec.parity_group:
            raise ValueError(VSPVolValidationMsg.NOT_POOL_ID_OR_PARITY_ID.value)
        if not spec.size:
            raise ValueError(VSPVolValidationMsg.SIZE_REQUIRED.value)
        if "." in spec.size:
            raise ValueError(VSPVolValidationMsg.SIZE_INT_REQUIRED.value)
        found = False
        if spec.nvm_subsystem_name:
            found = self.does_nvme_subsystem_exist(spec.nvm_subsystem_name)
            if not found:
                raise ValueError(VSPVolValidationMsg.NVM_SUBSYSTEM_DOES_NOT_EXIST.value.format(spec.nvm_subsystem_name))
            if spec.state is not None and spec.state.lower() == VSPVolumeSubstates.REMOVE_HOST_NQN:
                raise ValueError(VSPVolValidationMsg.CONTRADICT_INFO.value)
            else:
                logger.writeDebug("RC:create_volume:nvm_system={}", found)

        spec.size = process_size_string(spec.size)
        self.connection_info.changed = True
        volume_created = self.provisioner.create_volume(spec)
        if found:
            self.process_create_nvme(found, spec)
        return volume_created

    @log_entry_exit
    def get_snapshot_list_for_volume(self, volume, snapshots):
        retList = []
        if snapshots:
            for x in snapshots:
                if x['pvolLdevId'] == volume.ldevId or x['svolLdevId'] == volume.ldevId:
                    short_snapshot_object = VSPVolumeSnapshotInfo(x['pvolLdevId'], x['muNumber'], x['svolLdevId'])
                    retList.append(short_snapshot_object)
        return retList

    @log_entry_exit
    def get_all_snapshots(self):
        snapshot_prov = VSPHtiSnapshotProvisioner(self.connection_info)
        snapshots = snapshot_prov.get_snapshot_facts()
        return snapshots

    @log_entry_exit
    def get_nvm_subsystem_for_ldev(self, ldev_id):
        ldev_all = []
        nvms = self.nvme_provisioner.get_nvme_subsystems_by_namespace()
        for nvm in nvms.data:
            ldevs = self.find_ldevs_in_nvm_subsystem(nvm.nvmSubsystemId, ldev_id)
            if ldevs and len(ldevs) > 0:
                for x in ldevs:
                    ldev_all.append(x)

        logger.writeDebug("RC:get_nvm_subsystem_for_ldev:ldev_all={}", ldev_all)
        result_list = []
        ports =  self.nvme_provisioner.get_nvme_subsystems_by_port()
        logger.writeDebug("RC:get_nvm_subsystem_for_ldev:ports={}", ports)
        for l in ldev_all:
            for p in ports.data:
                if l.nvmSubsystemId == p.nvmSubsystemId:
                    item = VSPVolumeNvmSubsystenInfo(p.nvmSubsystemId, p.nvmSubsystemName, p.portIds)
                    result_list.append(item)
        return result_list

    @log_entry_exit
    def get_host_nqn_paths_for_nvm_subsystem(self, volume):
        nvm_ss_paths = self.nvme_provisioner.get_namespace_paths(volume.nvmSubsystemId)
        host_nqns = []
        for p in nvm_ss_paths.data:
            if p.namespaceId == int(volume.namespaceId) and p.ldevId == volume.ldevId:
                host_nqns.append(p.hostNqn)
        
        return host_nqns

    @log_entry_exit
    def get_nvm_subsystem_info(self, volume):
        host_nqns = self.get_host_nqn_paths_for_nvm_subsystem(volume)
        volume.numOfPorts = len(host_nqns)
        logger.writeDebug("RC:get_nvm_subsystem_info:no_of_ports={}", volume.numOfPorts)

        result_list = []
        nvm_ss = self.nvme_provisioner.get_nvme_subsystem_by_id(volume.nvmSubsystemId)
        logger.writeDebug("RC:get_nvm_subsystem_info:nvm_subsystem = {}", nvm_ss)
        item = VSPVolumeNvmSubsystenInfo(nvm_ss.nvmSubsystemId, nvm_ss.nvmSubsystemName, nvm_ss.portIds, host_nqns)
        result_list.append(item)
        return result_list

    
    @log_entry_exit
    def get_volume_detail_info(self, volume, all_snapshots=None):
        if all_snapshots:
            snapshots = self.get_snapshot_list_for_volume(volume, all_snapshots)
            volume.snapshots = snapshots
        volume.isEncryptionEnabled = self.is_encryption_enabled_on_volume(volume)
        hg_iscsi_tar_info = self.get_hostgroup_and_iscsi_target_info(volume)
        hostgroups = hg_iscsi_tar_info["hostgroups"]
        iscsi_targets = hg_iscsi_tar_info["iscsiTargets"]
        volume.hostgroups = hostgroups
        volume.iscsiTargets = iscsi_targets
        if volume.nvmSubsystemId:    
            nvm_subsystems = self.get_nvm_subsystem_info(volume)
            logger.writeDebug("RC:get_volume_detail_info:nvm_subsystem = {}", nvm_subsystems)
            volume.nvmSubsystems = nvm_subsystems
        return volume

    @log_entry_exit
    def get_volumes_detail_info(self, volumes):
        retList = []
        if volumes:
            all_snapshots = self.get_all_snapshots()
            logger.writeDebug("RC:get_volumes_detail_info:snapshots={}", all_snapshots)
            for volume in volumes:
                new_volume = self.get_volume_detail_info(volume, all_snapshots)
                retList.append(new_volume)
        return VSPVolumesInfo(data=retList)
    
    @log_entry_exit
    def is_encryption_enabled_on_volume(self, volume):

        # if there is parity group info then this is a basic volume
        if volume.numOfParityGroups is not None and volume.numOfParityGroups > 0:
            if volume.attributes is not None:
                if "ENCD" in volume.attributes:
                    return True
                else:
                    return False
            else:
                return False
        
        if volume.poolId is not None:
            pool_volumes =  self.provisioner.get_volumes_by_pool_id(volume.poolId)
            logger.writeDebug("RC:is_encryption_enabled_on_volume:pool_volumes={}", pool_volumes)
            if pool_volumes and len(pool_volumes.data) > 0:
                for v in pool_volumes.data:
                    if v.attributes is not None:
                        if "ENCD" not in v.attributes:
                            return False
                    else:
                        return False
                return True

        return False
    
    @log_entry_exit
    def get_hostgroup_and_iscsi_target_info(self, volume):
        hostgroups = []
        iscsi_targets = []
        if volume:
            if volume.numOfPorts is not None and volume.numOfPorts > 0:

                logger.writeDebug("RC:get_hostgroup_and_iscsi_target_info:ports={}", volume.ports)
                for port in volume.ports:
                    port_type = self.get_port_type(port["portId"])
                    if port_type == "ISCSI":
                        iscsi_targets.append(VSPVolumePortInfo(port["portId"], port["hostGroupNumber"], port["hostGroupName"]))
                    elif port_type == "FIBRE":
                        hostgroups.append(VSPVolumePortInfo(port["portId"], port["hostGroupNumber"], port["hostGroupName"]))
                    else:
                        pass
        ret_dict = {"hostgroups": hostgroups, "iscsiTargets": iscsi_targets}
        return ret_dict
    
    @log_entry_exit
    def get_port_type(self, port_id):   
        port_type = self.port_prov.get_port_type(port_id)
        return port_type

    @log_entry_exit
    def get_volumes(self, get_volume_spec: VolumeFactSpec):
        logger.writeDebug("RC:get_volumes:spec={}", get_volume_spec)
        if get_volume_spec.ldev_id:
            # new_volume = None
            volume = self.provisioner.get_volume_by_ldev(get_volume_spec.ldev_id)
            if volume:
                if get_volume_spec.is_detailed is not None and get_volume_spec.is_detailed == True:
                    
                    all_snapshots = self.get_all_snapshots()
                    volume = self.get_volume_detail_info(volume, all_snapshots)

                return VSPVolumesInfo(
                    data=[volume]
                )
        
        if get_volume_spec.start_ldev_id is not None and get_volume_spec.end_ldev_id is not None and get_volume_spec.count is None :
            get_volume_spec.count = get_volume_spec.end_ldev_id - get_volume_spec.start_ldev_id + 1
        volume_data = self.provisioner.get_volumes(
            get_volume_spec.start_ldev_id, get_volume_spec.count
        )

        if get_volume_spec.end_ldev_id:
            end_ldev_id = get_volume_spec.end_ldev_id
            volume_data.data = [
                volume for volume in volume_data.data if volume.ldevId <= end_ldev_id
            ]

        if get_volume_spec.name:
            volume_data.data = [
                volume
                for volume in volume_data.data
                if volume.label == get_volume_spec.name
            ]
        if get_volume_spec.is_detailed is not None and get_volume_spec.is_detailed == True:
            return self.get_volumes_detail_info(volume_data.data)
        else:
            return volume_data

    @log_entry_exit
    def update_volume_name(self, ldev_id, name):

        self.provisioner.change_volume_settings(ldev_id, name=name)

    @log_entry_exit
    def get_volume_by_name(self, name):

        volumes = self.provisioner.get_volumes()
        for volume in volumes.data:
            if volume.label == name:
                return volume

    @log_entry_exit
    def get_volume_by_id(self, id):

        volumes = self.provisioner.get_volumes()
        for volume in volumes.data:
            if volume.ldevId == int(id):
                return volume
        raise ValueError(VSPVolValidationMsg.VOLUME_NOT_FOUND.value.format(id))

    @log_entry_exit
    def delete_volume(self, volume: VSPVolumeInfo):
        ldev_id = volume.ldevId

        force_execute = (
            True
            if volume.dataReductionMode
            and volume.dataReductionMode.lower() != VolumePayloadConst.DISABLED
            else None
        )
        try :
            self.provisioner.delete_volume(ldev_id, force_execute)
            self.connection_info.changed = True
        except Exception as e:
            logger.writeError(f"An error occurred during initialization: {str(e)}")
            raise ValueError(VSPVolValidationMsg.VOLUME_HAS_PATH.value)


    @log_entry_exit
    def delete_volume_force(self, volume: VSPVolumeInfo):
        ports = volume.ports
        if ports:
            for port in ports:
                self.delete_lun_path(port)

        self.delete_host_ns_path_for_ldev(volume.ldevId)    
        self.delete_ldev_from_nvme_subsystem(volume.ldevId)
        
        
        self.delete_volume(volume)

    @log_entry_exit
    def delete_host_nqns_from_nvme_subsystem(self, host_nqns):
        for host_nqn in host_nqns:
            self.delete_host_ns_path_for_host_nqn(host_nqn)
            self.delete_host_nqn_from_nvme_subsystem(host_nqn)

    @log_entry_exit
    def delete_host_nqn_from_nvme_subsystem(self, host_nqn):
        nvms = self.nvme_provisioner.get_nvme_subsystems_by_nqn()
        
        for nvm in nvms.data:
            host_nqns = self.find_host_nqn_in_nvm_subsystem(nvm.nvmSubsystemId, host_nqn)
            if host_nqns and len(host_nqns) > 0:
                for x in host_nqns:
                    self.nvme_provisioner.delete_host_nqn_by_id(x.hostNqnId)

    @log_entry_exit
    def find_host_nqn_in_nvm_subsystem(self, nvm_subsystem_id, host_nqn):
        host_nqns_to_delete = []
        host_nqns = self.nvme_provisioner.get_host_nqns(nvm_subsystem_id)
        for hn in host_nqns.data:
            if hn.hostNqn == host_nqn:
                host_nqns_to_delete.append(hn)
        return host_nqns_to_delete

    @log_entry_exit
    def delete_ldev_from_nvme_subsystem(self, ldev_id):
        nvms = self.nvme_provisioner.get_nvme_subsystems_by_namespace()
        
        for nvm in nvms.data:
            ldevs = self.find_ldevs_in_nvm_subsystem(nvm.nvmSubsystemId, ldev_id)
            if ldevs and len(ldevs) > 0:
                for x in ldevs:
                    self.nvme_provisioner.delete_namespace(x.nvmSubsystemId, x.namespaceId)

    @log_entry_exit
    def find_ldevs_in_nvm_subsystem(self, nvm_subsystem_id, ldev_id):
        ldevs = []
        namespaces = self.nvme_provisioner.get_namespaces(nvm_subsystem_id)
        for ns in namespaces.data:
            if ns.ldevId == ldev_id:
                ldevs.append(ns)
        return ldevs

    @log_entry_exit
    def delete_host_ns_path_for_ldev(self, ldev_id):
        nvms = self.nvme_provisioner.get_nvme_subsystems_by_namespace()
        for nvm in nvms.data:
            ldev_paths = self.find_ldevs_in_paths(nvm.nvmSubsystemId, ldev_id)
            if ldev_paths and len(ldev_paths) > 0:
                # self.nvme_provisioner.delete_host_namespace_path(ldev_found.nvmSubsystemId, ldev_found.hostNqn, int(ldev_found.namespaceId))                
                for x in ldev_paths:
                    self.nvme_provisioner.delete_host_namespace_path_by_id(x.namespacePathId)

    @log_entry_exit
    def find_ldevs_in_paths(self, nvm_subsystem_id, ldev_id):
        ldevs = []
        paths = self.nvme_provisioner.get_namespace_paths(nvm_subsystem_id)
        for path in paths.data:
            logger.writeDebug(f"RC:find_ldevs_in_paths:path.ldevId={path.ldevId} ldev_id={ldev_id}")            
            if str(path.ldevId) == str(ldev_id):
                ldevs.append(path)
        return ldevs

    @log_entry_exit
    def delete_host_ns_path_for_host_nqn(self, host_nqn):
        nvms = self.nvme_provisioner.get_nvme_subsystems_by_nqn()
        for nvm in nvms.data:
            paths = self.find_host_nqn_in_paths(nvm.nvmSubsystemId, host_nqn)
            if paths and len(paths) > 0:
                # self.nvme_provisioner.delete_host_namespace_path(ldev_found.nvmSubsystemId, ldev_found.hostNqn, int(ldev_found.namespaceId))                
                for x in paths:
                    self.nvme_provisioner.delete_host_namespace_path_by_id(x.namespacePathId)

    @log_entry_exit
    def find_host_nqn_in_paths(self, nvm_subsystem_id, host_nqn):
        host_nqns_to_delete = []
        paths = self.nvme_provisioner.get_namespace_paths(nvm_subsystem_id)
        for path in paths.data:
            if path.hostNqn == host_nqn:
                host_nqns_to_delete.append(path)
        return host_nqns_to_delete

    @log_entry_exit
    def delete_lun_path(self, port):
        self.provisioner.delete_lun_path(port)

class VolumeCommonPropertiesExtractor:
    def __init__(self, serial):

        self.serial = serial
        self.common_properties = {
            "ldev_id": int,
            "deduplication_compression_mode": str,
            "emulation_type": str,
            "name": str,
            "parity_group_id": str,
            "pool_id": int,
            "resource_group_id": int,
            "status": str,
            "total_capacity": str,
            "used_capacity": str,
            "path_count": int,
            "provision_type": str,
            "logical_unit_id_hex_format": str,
            "canonical_name": str,
            "dedup_compression_progress": int,
            "dedup_compression_status": str,
            "is_alua": bool,
            "is_data_reduction_share_enabled": bool,
            "num_of_ports": int,
            # "ports": list,
            # "namespace_id": str,
            # "nvm_subsystem_id": str,
            "is_encryption_enabled": bool,
            "hostgroups": list,
            "iscsi_targets": list,
            "snapshots": list,
            "nvm_subsystems": list,
            "entitlement_status": str,
            "partner_id": str,
            "subscriber_id": str,
            "storage_serial_number": str,
            "tiering_policy": dict,
        }

# 20240824 - show vol tier after lun_runner

        self.parameter_mapping = {
            ## 20240914 - uca-1346 tieringProperties is changed to tieringPropertiesDto in the porcelain response
            "tiering_policy": "tieringPropertiesDto",
            # "tiering_policy": "tieringProperties",
            "is_alua": "isAluaEnabled",
            "is_data_reduction_share_enabled": "isDRS",
            "is_data_reduction_share_enabled": "isDataReductionSharedVolumeEnabled",
            "parity_group_id": "parityGroupIds",
            "path_count": "numOfPorts",
            "provision_type": "attributes",
            "total_capacity": "blockCapacity",
            "used_capacity": "numOfUsedBlock",
            "name": "label",
            "deduplication_compression_mode": "dataReductionMode",
            "dedup_compression_status": "dataReductionStatus",
            "dedup_compression_progress": "dataReductionProgressRate",

        }
        self.size_properties = ("total_capacity", "used_capacity")
        self.provision_type = "provision_type"
        self.hex_value = "logical_unit_id_hex_format"
        self.parity_group_id = "parity_group_id"
        self.num_of_ports = "num_of_ports"

    def process_list(self, response_key):
        new_items = []
        
        for item in response_key:
            new_dict = {}
            for key, value in item.items():
                key = camel_to_snake_case(key)
                value_type = type(value)
                if value is None:
                    default_value = (
                        ""
                        if value_type == str
                        else (
                            -1
                            if value_type == int
                            else [] if value_type == list else False
                        )
                    )
                    value = default_value
                new_dict[key] = value
            new_items.append(new_dict)
        return new_items
    
    @log_entry_exit
    def extract(self, responses):
        new_items = []
        for response in responses:
            logger.writeDebug("20240825 after gateway creatlun response={}", response)
            new_dict = {}
            
            
            for key, value_type in self.common_properties.items():

                cased_key = snake_to_camel_case(key)
                # Get the corresponding key from the response or its mapped key

                response_key = get_response_key(
                    response,
                    cased_key,
                    self.parameter_mapping.get(cased_key),
                    key,
                    self.parameter_mapping.get(key),
                )

                # Assign the value based on the response key and its data type

                if response_key or isinstance(response_key, int):
                    if key == self.provision_type or key == self.parity_group_id:
                        new_dict[key] = value_type(
                            response_key
                            if isinstance(response_key, str)
                            else ",".join(response_key)
                        )
                    elif key == self.num_of_ports:
                        new_dict[key] = value_type(response_key)
                        new_dict["path_count"] = value_type(response_key)

                    elif key in self.size_properties:
                        if type(response_key) == str:
                            new_dict[key] = value_type(response_key)
                        else:
                            new_dict[key] = value_type(
                                convert_block_capacity(response_key)
                            )
                    else:
                        new_dict[key] = value_type(response_key)
                elif key == "tiering_policy":
                    if response_key is not None:
                        logger.writeDebug("tieringProperties={}", response["tiering_policy"])
                        logger.writeDebug("tiering_policy={}", response["tiering_policy"])
                        new_dict["tiering_policy"] = self.process_list(response["tiering_policy"])
                        new_dict["tiering_policy"]["policy"] = self.process_list(response["tiering_policy"]["policy"])
                elif key == self.hex_value:
                    new_dict[key] = (
                        response_key
                        if response_key
                        else volume_id_to_hex_format(response.get("ldevId")).upper()
                    )
                else:
                    # Handle missing keys by assigning default values
                    default_value = (
                        "" if value_type == str else -1 if value_type == int else [] if value_type == list else False
                    )
                    new_dict[key] = default_value

                if value_type == list and response_key: 
                    new_dict[key] = self.process_list(response_key)  
                                 
                # 20240825 voltiering tieringProperties
                if key == 'tiering_policy' and value_type == dict and response_key: 
                    # logger.writeDebug("tieringProperties={}", response["tieringProperties"])
                    logger.writeDebug("tieringProperties={}", response["tieringPropertiesDto"])
                    logger.writeDebug("response_key={}", response_key)
                    logger.writeDebug("key={}", key)
                    new_dict[key] = camel_to_snake_case_dict(response_key)  
                    new_dict["tiering_policy"]["tier1_used_capacity_mb"] = new_dict["tiering_policy"]["tier1_used_capacity_m_b"]
                    new_dict["tiering_policy"]["tier2_used_capacity_mb"] = new_dict["tiering_policy"]["tier2_used_capacity_m_b"]
                    new_dict["tiering_policy"]["tier3_used_capacity_mb"] = new_dict["tiering_policy"]["tier3_used_capacity_m_b"]
                    new_dict[key]['policy'] = camel_to_snake_case_dict(response_key['policy'])  
                    del new_dict["tiering_policy"]["tier1_used_capacity_m_b"]
                    del new_dict["tiering_policy"]["tier2_used_capacity_m_b"]
                    del new_dict["tiering_policy"]["tier3_used_capacity_m_b"]
                      
            if new_dict.get("storage_serial_number") is None:
                new_dict["storage_serial_number"] = self.serial
                
            new_items.append(new_dict)
        return new_items
