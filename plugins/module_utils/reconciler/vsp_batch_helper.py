from ..common.hv_log import Log
from ..message.vsp_hur_msgs import VspRemoteReplicationMsg

logger = Log()


class VspRemoteReplicationBatchHelper:

    @staticmethod
    def check_and_get_host_groups(hg_provisioner, host_groups):
        if not host_groups:
            logger.error("No host groups provided for remote replication.")
            raise ValueError(VspRemoteReplicationMsg.NO_HG_PROVIDED.value)

        valid_host_groups = []
        for hg in host_groups:
            host_group_info = hg_provisioner.get_one_host_group(hg.port, hg.name)
            logger.writeDebug(
                "RC:check_and_get_host_groups:host_group_info={}", host_group_info
            )
            if not host_group_info.data:
                raise ValueError(
                    VspRemoteReplicationMsg.HGS_DOES_NOT_EXIST.value.format(
                        hg.name, hg.port
                    )
                )
            else:
                valid_host_groups.append(host_group_info.data)

        if not valid_host_groups or len(valid_host_groups) == 0:
            logger.error(
                f"No valid host groups found for provisioner: {hg_provisioner}."
            )
            raise ValueError(VspRemoteReplicationMsg.NO_VALID_HG_PROVIDED.value)

        return valid_host_groups

    @staticmethod
    def check_and_get_iscsi_targets(hg_provisioner, iscsi_targets):
        if not iscsi_targets:
            logger.error("No iscsi_target provided for remote replication.")
            raise ValueError(VspRemoteReplicationMsg.NO_ISCSI_TARGET_PROVIDED.value)

        valid_iscsi_targets = []
        for target in iscsi_targets:
            iscsi_target_info = hg_provisioner.get_one_iscsi_target(
                target.port, target.name
            )
            logger.writeDebug(
                "RC:check_and_get_iscsi_targets:iscsi_target_info={}", iscsi_target_info
            )
            if not iscsi_target_info.data:
                raise ValueError(
                    VspRemoteReplicationMsg.ISCSI_TARGET_DOES_NOT_EXIST.value.format(
                        target.name, target.port
                    )
                )
            else:
                valid_iscsi_targets.append(iscsi_target_info.data)

        if not valid_iscsi_targets or len(valid_iscsi_targets) == 0:
            logger.error(
                f"No valid iscsi targets found for provisioner: {hg_provisioner}."
            )
            raise ValueError(
                VspRemoteReplicationMsg.NO_VALID_ISCSI_TARGET_PROVIDED.value
            )

        return valid_iscsi_targets

    @staticmethod
    def check_and_get_nvm_subsystem(nvm_prov, nvm_subsystem_spec):
        if not nvm_subsystem_spec:
            logger.error("No nvm subsystem provided for remote replication.")
            raise ValueError(VspRemoteReplicationMsg.NO_NVM_SUBSYSTEM_PROVIDED.value)

        nvm_subsystem_info = nvm_prov.get_nvme_subsystem_by_name(
            nvm_subsystem_spec.name
        )
        logger.writeDebug(
            "RC:check_and_get_nvm_subsystem:nvm_subsystem_info={}", nvm_subsystem_info
        )
        if not nvm_subsystem_info:
            raise ValueError(
                VspRemoteReplicationMsg.NVM_SUBSYSTEM_DOES_NOT_EXIST.value.format(
                    nvm_subsystem_spec.name
                )
            )
        else:
            return nvm_subsystem_info

    @staticmethod
    def get_free_ldev_ids(vol_prov, count, start_ldev=None, end_ldev=None):
        if start_ldev is None:
            start_ldev = 0
        if end_ldev is not None:
            end_ldev = int(end_ldev)
        free_ldevs = vol_prov.get_free_ldevs_from_meta(count, start_ldev, end_ldev)
        if not free_ldevs or len(free_ldevs) < count:
            raise ValueError(
                VspRemoteReplicationMsg.INSUFFICIENT_FREE_LDEVS.value.format(
                    count, len(free_ldevs)
                )
            )
        return free_ldevs

    @staticmethod
    def find_lun_ids_from_spec(hostgroups, hgs_from_spec, is_iscsi=False):

        logger.writeDebug(f"RC:find_lun_ids_from_spec:hostgroups={hostgroups}")
        logger.writeDebug(f"RC:find_lun_ids_from_spec:hgs_from_spec={hgs_from_spec}")
        hg_map = {}
        for spec_hg in hgs_from_spec:
            hg_map[spec_hg.name] = spec_hg

        logger.writeDebug(f"RC:find_lun_ids_from_spec:hg_map={hg_map}")
        lun_ids = {}
        for hg in hostgroups:
            hg_name = None
            if is_iscsi is not None and is_iscsi:
                hg_name = hg.iscsiName
            else:
                hg_name = hg.hostGroupName
            spec_hg = hg_map.get(hg_name, None)
            if spec_hg is None:
                raise ValueError(
                    f"Something went wrong, could not find the hostgroup or iscsi with name {hg_name} specified in the spec."
                )

            lun_ids[spec_hg.name] = spec_hg.lun_id

        return lun_ids

    @staticmethod
    def add_ldevs_to_host_groups(hg_provisioner, ldevs, host_groups, lun_ids):
        for i in range(0, len(host_groups)):
            hg = host_groups[i]
            hg_provisioner.add_ldevs_to_host_group(
                hg,
                ldevs,
                lun_ids.get(hg.hostGroupName, None),
            )

    @staticmethod
    def add_ldevs_to_iscsi_targets(iscsi_prov, ldevs, iscsi_targets, lun_ids):
        for i in range(0, len(iscsi_targets)):
            iscsi_target = iscsi_targets[i]
            iscsi_prov.add_ldevs_to_iscsi_target(
                iscsi_target,
                ldevs,
                lun_ids.get(iscsi_target.iscsiName, None),
            )

    @staticmethod
    def add_ldevs_to_nvm_subsystems(nvm_prov, ldevs, nvm_subsystem, spec_nvm_subsystem):
        try:
            nvm_subsystem_id = nvm_subsystem.nvmSubsystemId
            for ldev in ldevs:
                ns_id = VspRemoteReplicationBatchHelper.create_namespace_for_ldev(
                    nvm_prov, nvm_subsystem_id, ldev.ldevId, None
                )
                ns_id = ns_id.split(",")[-1]
                VspRemoteReplicationBatchHelper.create_namespace_paths(
                    nvm_prov, nvm_subsystem_id, ns_id, spec_nvm_subsystem
                )
        except Exception as ex:
            # err_msg = VspRemoteReplicationMsg.NVM_OPERATION_FAILED.value + str(ex)
            # logger.writeError(err_msg)
            # if setting the volume name fails, delete the secondary volume
            # if attaching the volume to the host group fails, delete the secondary volume
            # self.delete_volume_when_nvme(
            #     sec_vol_id,
            #     nvme_subsystem.nvmSubsystemId,
            #     spec.secondary_nvm_subsystem,
            #     pvolNameSpaceId,
            # )
            raise

    @staticmethod
    def create_namespace_for_ldev(nvm_prov, nvm_subsystem_id, ldev_id, ns_id):
        ns_id = nvm_prov.create_namespace(nvm_subsystem_id, ldev_id, ns_id)
        logger.writeDebug("PROV:add_svol_to_nvmesubsystem:ns_id = {}", ns_id)
        return ns_id

    @staticmethod
    def create_namespace_paths(nvm_prov, nvm_subsystem_id, namespace_id, nvmsubsystem):
        nqns = []
        if nvmsubsystem.paths is not None:
            nqns = nvmsubsystem.paths
        else:
            host_nqns = nvm_prov.get_host_nqns(nvm_subsystem_id)
            nqns = [nqn.hostNqn for nqn in host_nqns.data]

        for nqn in nqns:
            host_ns_path_id = nvm_prov.set_host_namespace_path(
                nvm_subsystem_id, nqn, namespace_id
            )
            logger.writeDebug(
                "PROV:create_namespace_paths:host_ns_path_id = {}", host_ns_path_id
            )
        return None
