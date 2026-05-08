import threading
from typing import Any
import copy

from ..provisioner.vsp_journal_volume_provisioner import VSPJournalVolumeProvisioner
from ..message.vsp_hur_msgs import VspRemoteReplicationMsg
from ..model.vsp_volume_models import CreateVolumeSpec, LdevNamespec
from ..reconciler.vsp_batch_helper import VspRemoteReplicationBatchHelper
from ..reconciler.vsp_volume import VSPVolumeReconciler
from ..common.vsp_utils import (
    get_local_device_group_name_from_copy_pair_id,
    get_remote_device_group_name_from_copy_pair_id,
    get_serial_number_from_device_id,
)

try:
    from ..common.ansible_common import (
        log_entry_exit,
        camel_to_snake_case,
        convert_block_capacity,
        volume_id_to_hex_format,
        get_default_value,
    )
    from ..common.hv_log import Log
    from ..common.hv_constants import StateValue
    from ..provisioner.vsp_hur_provisioner import VSPHurProvisioner
    from ..provisioner.vsp_host_group_provisioner import VSPHostGroupProvisioner
    from ..provisioner.vsp_iscsi_target_provisioner import VSPIscsiTargetProvisioner
    from ..provisioner.vsp_nvme_provisioner import VSPNvmeProvisioner
    from ..provisioner.vsp_volume_prov import VSPVolumeProvisioner
    from ..gateway.vsp_storage_system_gateway import VSPStorageSystemDirectGateway
    from ..model.vsp_copy_groups_models import (
        DirectCopyPairInfo,
    )
    from ..message.vsp_hur_msgs import VSPHurValidateMsg
    from ..message.vsp_true_copy_msgs import VSPTrueCopyValidateMsg
except ImportError:
    from common.ansible_common import (
        log_entry_exit,
        camel_to_snake_case,
        convert_block_capacity,
        volume_id_to_hex_format,
        get_default_value,
    )
    from common.hv_log import Log
    from common.hv_constants import StateValue
    from provisioner.vsp_hur_provisioner import VSPHurProvisioner
    from provisioner.vsp_host_group_provisioner import VSPHostGroupProvisioner
    from provisioner.vsp_iscsi_target_provisioner import VSPIscsiTargetProvisioner
    from provisioner.vsp_nvme_provisioner import VSPNvmeProvisioner
    from gateway.vsp_storage_system_gateway import VSPStorageSystemDirectGateway
    from model.vsp_copy_groups_models import DirectCopyPairInfo
    from message.vsp_hur_msgs import VSPHurValidateMsg
    from message.vsp_true_copy_msgs import VSPTrueCopyValidateMsg

logger = Log()


class VSPHurReconciler:
    def __init__(self, connection_info, serial, state, secondary_connection_info=None):

        self.connection_info = connection_info
        self.storage_serial_number = serial
        self.provisioner = VSPHurProvisioner(connection_info, serial)
        self.state = state
        self.secondary_connection_info = secondary_connection_info
        if self.storage_serial_number is None:
            self.storage_serial_number = self.get_storage_serial_number()

    @log_entry_exit
    def get_storage_serial_number(self):
        storage_gw = VSPStorageSystemDirectGateway(self.connection_info)
        storage_system = storage_gw.get_current_storage_system_info()
        return storage_system.serialNumber

    # 20240808 hur operations reconciler
    @log_entry_exit
    def delete_hur(self, spec):
        return self.provisioner.delete_hur_pair(spec)

    @log_entry_exit
    def resync_hur(self, spec):
        return self.provisioner.resync_hur_pair(spec)

    @log_entry_exit
    def split_hur(self, spec):
        return self.provisioner.split_hur_pair(spec)

    @log_entry_exit
    def swap_split_hur(self, spec):
        return self.provisioner.swap_split_hur_pair(spec)

    @log_entry_exit
    def secondary_takeover_hur(self, spec):
        return self.provisioner.secondary_takeover_hur_pair(spec)

    @log_entry_exit
    def swap_resync_hur(self, spec):
        return self.provisioner.swap_resync_hur_pair(spec)

    @log_entry_exit
    def create_hur(self, spec):
        self.validate_create_spec(spec)

        pvol = self.provisioner.get_volume_by_id(spec.primary_volume_id)
        logger.writeDebug("RC:create_hur:pvol={} ", pvol)
        if not pvol or pvol.emulationType.upper() == "NOT DEFINED":
            raise ValueError(
                VSPTrueCopyValidateMsg.PRIMARY_VOLUME_ID_DOES_NOT_EXIST.value.format(
                    spec.primary_volume_id
                )
            )

        if pvol.numOfPorts is None or pvol.numOfPorts < 1:
            raise ValueError(
                VSPTrueCopyValidateMsg.PRIMARY_VOLUME_ID_NO_PATH.value.format(
                    spec.primary_volume_id
                )
            )

        return self.provisioner.create_hur_pair(spec)

    @log_entry_exit
    def validate_create_spec(self, spec: Any) -> None:
        if spec.primary_volume_id is None:
            raise ValueError(VSPTrueCopyValidateMsg.PRIMARY_VOLUME_ID.value)

        if (
            spec.secondary_pool_id is None
            and spec.provisioned_secondary_volume_id is None
        ):
            raise ValueError(VSPTrueCopyValidateMsg.SECONDARY_POOL_ID.value)

        if (
            spec.secondary_hostgroup is not None
            and spec.secondary_hostgroups is not None
        ):
            raise ValueError(VSPTrueCopyValidateMsg.BOTH_HGS_ARE_SPECIFIED.value)

        if spec.secondary_hostgroup is not None and spec.secondary_hostgroups is None:
            spec.secondary_hostgroups = spec.secondary_hostgroup

        if (
            spec.secondary_hostgroups is None
            and spec.secondary_nvm_subsystem is None
            and spec.secondary_iscsi_targets is None
            and spec.provisioned_secondary_volume_id is None
        ):
            raise ValueError(VSPTrueCopyValidateMsg.SECONDARY_HOSTGROUPS_OR_NVME.value)

        if self.secondary_connection_info is None:
            raise ValueError(VSPTrueCopyValidateMsg.SECONDARY_CONNECTION_INFO.value)
        else:
            spec.secondary_connection_info = self.secondary_connection_info
        if spec.copy_group_name is None:
            raise ValueError(VSPTrueCopyValidateMsg.COPY_GROUP_NAME.value)
        if spec.copy_pair_name is None:
            raise ValueError(VSPTrueCopyValidateMsg.COPY_PAIR_NAME.value)

        if (
            spec.provisioned_secondary_volume_id
            and spec.begin_secondary_volume_id
            and spec.end_secondary_volume_id
        ):
            if (
                spec.provisioned_secondary_volume_id < spec.begin_secondary_volume_id
            ) or (spec.provisioned_secondary_volume_id > spec.end_secondary_volume_id):
                raise ValueError(
                    VSPHurValidateMsg.SECONDARY_VOLUME_ID_OUT_OF_RANGE.value
                )

    @log_entry_exit
    def validate_hur_spec_ctg(self, spec: Any) -> None:
        # sng20250125 this should be in validate_hur_module
        # but calls to validate_hur_module are bypassed in favor of the common validations
        # "HUR must be registered in a consistency group"
        if spec.consistency_group_id:
            if spec.allocate_new_consistency_group:
                raise ValueError(VSPHurValidateMsg.INVALID_CG_NEW.value)
        else:
            if spec.allocate_new_consistency_group is None:
                raise ValueError(VSPHurValidateMsg.INVALID_CTG_BOTH_NONE.value)
            else:
                if not spec.allocate_new_consistency_group:
                    # sng20250125 validate_hur_spec_ctg, default is auto-assign CTG
                    spec.allocate_new_consistency_group = True
                    # if we don't want the default then raise error
                    # raise ValueError(VSPHurValidateMsg.INVALID_CTG_NONE.value)

    @log_entry_exit
    def validate_hur_spec_for_ops_resize(self, spec: Any) -> None:
        if spec.new_volume_size is None:
            raise ValueError(VSPHurValidateMsg.NEW_VOLUME_SIZE.value)

    @log_entry_exit
    def resize_hur_copy(self, spec):
        self.validate_hur_spec_for_ops_resize(spec)
        return self.provisioner.resize_hur_copy_pair(spec)

    @log_entry_exit
    def reconcile_hur(self, spec) -> Any:
        """
        Reconcile the HUR based on the desired state in the specification.
        """
        state = self.state.lower()
        if self.secondary_connection_info is None:
            raise ValueError(VSPTrueCopyValidateMsg.SECONDARY_CONNECTION_INFO.value)
        else:
            spec.secondary_connection_info = self.secondary_connection_info
        resp_data = None
        if state == StateValue.ABSENT:
            result = self.delete_hur(spec)
            return result
        elif state == StateValue.PRESENT:
            resp_data = self.create_hur(spec)
            logger.writeDebug("RC:resp_data={}", resp_data)
        elif state == StateValue.SPLIT:
            resp_data = self.split_hur(spec)
        elif state == StateValue.RE_SYNC:
            resp_data = self.resync_hur(spec)
        elif state == StateValue.SWAP_SPLIT:
            resp_data = self.swap_split_hur(spec)
        elif state == StateValue.TAKEOVER:
            resp_data = self.secondary_takeover_hur(spec)
            return resp_data
        elif state == StateValue.SWAP_RESYNC:
            resp_data = self.swap_resync_hur(spec)
        elif state == StateValue.RESIZE or state == StateValue.EXPAND:
            resp_data = self.resize_hur_copy(spec)

        if resp_data:
            logger.writeDebug("RC:resp_data={}  state={}", resp_data, state)
            if isinstance(resp_data, dict):
                return resp_data

            resp_in_dict = resp_data.to_dict()
            logger.writeDebug("RC:reconcile_hur:hur_pairs={}", resp_in_dict)
            self.get_other_attributes(resp_in_dict)

            return self.inject_pvol_svol_size_then_return(resp_in_dict, state)
        else:
            return None

    @log_entry_exit
    def inject_pvol_svol_size_then_return(self, resp_dict: dict, state=None) -> dict:
        if state and state == StateValue.SWAP_SPLIT:
            # for swap split, the primary and secondary connection are swapped, so we need to get the sizes accordingly
            pvolData = self.provisioner.get_volume_by_id(resp_dict["svolLdevId"])
            resp_dict["primaryVolumeSize"] = convert_block_capacity(
                pvolData.blockCapacity
            )
            secondary_vol_prov = VSPVolumeProvisioner(self.secondary_connection_info)
            svolData = secondary_vol_prov.get_volume_by_ldev_id(
                resp_dict["pvolLdevId"], include_drs=False
            )
            resp_dict["secondaryVolumeSize"] = convert_block_capacity(
                svolData.blockCapacity
            )
        else:
            pvolData = self.provisioner.get_volume_by_id(resp_dict["pvolLdevId"])
            resp_dict["primaryVolumeSize"] = convert_block_capacity(
                pvolData.blockCapacity
            )
            secondary_vol_prov = VSPVolumeProvisioner(self.secondary_connection_info)
            svolData = secondary_vol_prov.get_volume_by_ldev_id(
                resp_dict["svolLdevId"], include_drs=False
            )
            resp_dict["secondaryVolumeSize"] = convert_block_capacity(
                svolData.blockCapacity
            )
        return DirectHurCopyPairInfoExtractor(self.storage_serial_number).extract(
            [resp_dict]
        )

    @log_entry_exit
    def get_other_attributes(self, hur_pairs):

        copy_group_list = self.provisioner.get_copy_group_list()
        logger.writeDebug("RC::copy_group_list={}", copy_group_list)
        logger.writeDebug("RC::hur_pairs={}", hur_pairs)

        # in case input is not a list
        if not isinstance(hur_pairs, list):
            hur_pairs = [hur_pairs]

        for hur_pair in hur_pairs:

            self.get_other_attributes_from_copy_group(copy_group_list, hur_pair)

            if hur_pair.get("muNumber"):
                logger.writeDebug("sng1104 muNumber={}", hur_pair["muNumber"])

            # logger.writeDebug(
            #     "sng1104 localDeviceGroupName={}", hur_pair["localDeviceGroupName"]
            # )
            # logger.writeDebug(
            #     "sng1104 remoteDeviceGroupName={}", hur_pair["remoteDeviceGroupName"]
            # )

        return

    def get_other_attributes_from_copy_group(self, cglist, hur_pair):
        if cglist is None:
            return
        cgname = hur_pair["copyGroupName"]

        logger.writeDebug("sng1104 392 cgname={}", cgname)
        logger.writeDebug("sng1104 392 hur_pair={}", hur_pair)

        for cg in cglist.data:
            if cgname == cg.copyGroupName:
                hur_pair["muNumber"] = cg.muNumber
                hur_pair["localDeviceGroupName"] = cg.localDeviceGroupName
                hur_pair["remoteDeviceGroupName"] = cg.remoteDeviceGroupName
                logger.writeDebug("sng1104 393 hur_pair={}", hur_pair)
                return

    @log_entry_exit
    def validate_hur_fact_spec(self, spec: Any) -> None:
        if self.secondary_connection_info is None:
            raise ValueError(VSPTrueCopyValidateMsg.SECONDARY_CONNECTION_INFO.value)
        else:
            spec.secondary_connection_info = self.secondary_connection_info

    @log_entry_exit
    def get_hur_facts(self, spec=None):

        self.validate_hur_fact_spec(spec)
        tc_pairs = self.provisioner.hur_pair_facts_direct(spec)
        logger.writeDebug("RC:get_hur_facts:tc_pairs={}", tc_pairs)

        if isinstance(tc_pairs, DirectCopyPairInfo):
            tc_pairs = [tc_pairs.to_dict()]
        elif isinstance(tc_pairs, list):
            tc_pairs = self.objs_to_dict(tc_pairs)
        logger.writeDebug("RC:get_hur_facts:tc_pairs={}", tc_pairs)

        self.get_other_attributes(tc_pairs)

        if len(tc_pairs) == 1:
            return self.inject_pvol_svol_size_then_return(tc_pairs[0])
        extracted_data = DirectHurCopyPairInfoExtractor(
            self.storage_serial_number
        ).extract(tc_pairs)
        return extracted_data

    # convert objs in the input to dict
    def objs_to_dict(self, objs):

        if not isinstance(objs, list):
            return objs

        items = []
        for obj in objs:
            if isinstance(obj, dict):
                items.append(obj)
                continue

            # DirectCopyPairInfo?
            obj = obj.to_dict()
            items.append(obj)
        return items

    @log_entry_exit
    def get_free_ldevs_for_storage(self, spec, is_primary=True):
        try:
            vol_prov = VSPVolumeProvisioner(
                self.connection_info if is_primary else spec.secondary_connection_info
            )
            return VspRemoteReplicationBatchHelper.get_free_ldev_ids(
                vol_prov,
                count=spec.number_of_pairs,
                start_ldev=(
                    spec.begin_primary_volume_id
                    if is_primary
                    else spec.begin_secondary_volume_id
                ),
                end_ldev=(
                    spec.end_primary_volume_id
                    if is_primary
                    else spec.end_secondary_volume_id
                ),
            )
        except Exception as e:
            storage_type = "primary" if is_primary else "secondary"
            err_msg = (
                VspRemoteReplicationMsg.STORAGE_INFO.value.format(storage_type)
                + " "
                + str(e)
            )
            logger.writeError(
                "RC: get_free_ldevs_for_storage: Error occurred while getting free LDEVs for {} storage: {}".format(
                    storage_type, err_msg
                )
            )
            raise ValueError(err_msg)

    @log_entry_exit
    def check_and_get_host_groups(self, spec, is_primary=True):
        try:
            hg_prov = VSPHostGroupProvisioner(
                self.connection_info if is_primary else spec.secondary_connection_info
            )
            host_groups = (
                spec.primary_hostgroups if is_primary else spec.secondary_hostgroups
            )
            return VspRemoteReplicationBatchHelper.check_and_get_host_groups(
                hg_prov, host_groups
            )
        except Exception as e:
            storage_type = "primary" if is_primary else "secondary"
            err_msg = (
                VspRemoteReplicationMsg.STORAGE_INFO.value.format(storage_type)
                + " "
                + str(e)
            )
            logger.writeError(
                "RC: check_and_get_host_groups: Error occurred while checking host groups for {} storage: {}".format(
                    storage_type, err_msg
                )
            )
            raise ValueError(err_msg)

    @log_entry_exit
    def check_and_get_iscsi_targets(self, spec, is_primary=True):
        try:
            hg_prov = VSPIscsiTargetProvisioner(
                self.connection_info if is_primary else spec.secondary_connection_info
            )
            iscsi_targets = (
                spec.primary_iscsi_targets
                if is_primary
                else spec.secondary_iscsi_targets
            )
            return VspRemoteReplicationBatchHelper.check_and_get_iscsi_targets(
                hg_prov, iscsi_targets
            )
        except Exception as e:
            storage_type = "primary" if is_primary else "secondary"
            err_msg = (
                VspRemoteReplicationMsg.STORAGE_INFO.value.format(storage_type)
                + " "
                + str(e)
            )
            logger.writeError(
                "RC: check_and_get_iscsi_targets: Error occurred while checking iscsi targets for {} storage: {}".format(
                    storage_type, err_msg
                )
            )
            raise ValueError(err_msg)

    @log_entry_exit
    def check_and_get_nvm_subsystem(self, spec, is_primary=True):
        try:
            nvm_prov = VSPNvmeProvisioner(
                self.connection_info if is_primary else spec.secondary_connection_info
            )
            nvm_subsystem = (
                spec.primary_nvm_subsystem
                if is_primary
                else spec.secondary_nvm_subsystem
            )
            return VspRemoteReplicationBatchHelper.check_and_get_nvm_subsystem(
                nvm_prov, nvm_subsystem
            )
        except Exception as e:
            storage_type = "primary" if is_primary else "secondary"
            err_msg = (
                VspRemoteReplicationMsg.STORAGE_INFO.value.format(storage_type)
                + " "
                + str(e)
            )
            logger.writeError(
                "RC: check_and_get_host_groups: Error occurred while checking host groups for {} storage: {}".format(
                    storage_type, err_msg
                )
            )
            raise ValueError(err_msg)

    @log_entry_exit
    def construct_create_volume_spec(self, spec, free_ldevs, is_primary=True):
        name_spec = LdevNamespec(
            base_name=spec.primary_volume_base_name,
            start_number=spec.primary_volume_base_name_start_number,
            number_of_digits=spec.primary_volume_base_name_number_of_digits,
        )
        volume_spec = CreateVolumeSpec(
            size=spec.volume_size,
            pool_id=spec.primary_pool_id if is_primary else spec.secondary_pool_id,
            names=name_spec,
            number_of_ldevs=spec.number_of_pairs,
            capacity_saving=spec.capacity_saving,
            data_reduction_share=spec.data_reduction_share,
            is_compression_acceleration_enabled=spec.is_compression_acceleration_enabled,
        )
        volume_spec.start_ldev_id = free_ldevs[0]
        volume_spec.end_ldev_id = free_ldevs[-1]
        logger.writeDebug(
            "RC: construct_create_volume_spec: volume_spec={}", volume_spec
        )
        return volume_spec

    @log_entry_exit
    def create_ldevs_on_storage(self, volume_spec, vol_prov):

        ldevs = vol_prov.ldev_batch_operation(volume_spec)
        ldev_ids = [ldev.ldevId for ldev in ldevs]
        logger.writeDebug("RC: create_ldevs_on_storage: ldev_ids={}", ldevs)
        logger.writeDebug("RC: volume_spec.comments={}", volume_spec.comments)

        if volume_spec.comments is not None and len(volume_spec.comments) > 0:
            volume_spec.comments.append(
                volume_spec.comments if volume_spec.comments else []
            )
            if len(ldev_ids) > 0:
                self._cleanup_ldevs(volume_spec, ldev_ids, vol_prov)
            return None
        return ldev_ids

    @log_entry_exit
    def add_ldevs_to_hostgroups(self, spec, hostgroups, ldev_ids, is_primary=True):

        spec_hostgroups = (
            spec.primary_hostgroups if is_primary else spec.secondary_hostgroups
        )
        lun_ids = VspRemoteReplicationBatchHelper.find_lun_ids_from_spec(
            hostgroups, spec_hostgroups, is_iscsi=False
        )
        hg_prov = VSPHostGroupProvisioner(
            self.connection_info if is_primary else spec.secondary_connection_info
        )
        VspRemoteReplicationBatchHelper.add_ldevs_to_host_groups(
            hg_prov, ldev_ids, hostgroups, lun_ids
        )

    @log_entry_exit
    def add_ldevs_to_iscsi_targets(
        self, spec, iscsi_targets, ldev_ids, is_primary=True
    ):

        spec_iscsi_targets = (
            spec.primary_iscsi_targets if is_primary else spec.secondary_iscsi_targets
        )
        lun_ids = VspRemoteReplicationBatchHelper.find_lun_ids_from_spec(
            iscsi_targets, spec_iscsi_targets, is_iscsi=True
        )
        iscsi_prov = VSPIscsiTargetProvisioner(
            self.connection_info if is_primary else spec.secondary_connection_info
        )
        VspRemoteReplicationBatchHelper.add_ldevs_to_iscsi_targets(
            iscsi_prov, ldev_ids, iscsi_targets, lun_ids
        )

    @log_entry_exit
    def add_ldevs_to_nvm_subsystem(
        self, spec, nvm_subsystem, ldev_ids, is_primary=True
    ):

        try:
            spec_nvm_subsystem = (
                spec.primary_nvm_subsystem
                if is_primary
                else spec.secondary_nvm_subsystem
            )
            nvm_prov = VSPNvmeProvisioner(
                self.connection_info if is_primary else spec.secondary_connection_info
            )
            VspRemoteReplicationBatchHelper.add_ldevs_to_nvm_subsystem(
                nvm_prov, ldev_ids, nvm_subsystem, spec_nvm_subsystem
            )
        except Exception as e:
            storage_type = "primary" if is_primary else "secondary"
            err_msg = (
                VspRemoteReplicationMsg.NVM_OPERATION_FAILED.value.format(
                    "adding LDEVs to NVMe subsystem",
                    nvm_subsystem.subsystemName,
                    storage_type,
                )
                + " "
                + str(e)
            )
            logger.writeError(
                "RC: add_ldevs_to_nvm_subsystem: Error occurred while adding LDEVs to NVMe subsystem for {} storage: {}".format(
                    storage_type, err_msg
                )
            )
            raise ValueError(err_msg)

    @log_entry_exit
    def does_journal_id_exist(self, spec, journal_id, is_primary=True):
        try:
            journal_prov = VSPJournalVolumeProvisioner(
                self.connection_info if is_primary else spec.secondary_connection_info
            )
            journal = journal_prov.check_journal_pool_id_exists(journal_id)
            logger.writeDebug(
                "RC: does_journal_id_exist: journal_id={} exists={} for {} storage".format(
                    journal_id,
                    journal is not None,
                    "primary" if is_primary else "secondary",
                )
            )
            if journal is None:
                raise ValueError(
                    VspRemoteReplicationMsg.JOURNAL_ID_DOES_NOT_EXIST.value.format(
                        journal_id, "primary" if is_primary else "secondary"
                    )
                )
            return True
        except Exception as e:
            storage_type = "primary" if is_primary else "secondary"
            err_msg = (
                VspRemoteReplicationMsg.STORAGE_INFO.value.format(storage_type)
                + " "
                + str(e)
            )
            logger.writeError(
                "RC: does_journal_id_exist: Error occurred while checking journal ID existence for {} storage: {}".format(
                    storage_type, err_msg
                )
            )
            raise ValueError(err_msg)

    @log_entry_exit
    def get_free_journal_id(self, spec, is_primary=True):
        try:
            journal_prov = VSPJournalVolumeProvisioner(
                self.connection_info if is_primary else spec.secondary_connection_info
            )
            free_journal_pools = journal_prov.get_unused_journal_pools()
            logger.writeDebug(
                "RC: get_free_journal_id: free_journal_pools={} for {} storage".format(
                    free_journal_pools, "primary" if is_primary else "secondary"
                )
            )
            if not free_journal_pools or len(free_journal_pools) == 0:
                raise ValueError(
                    VSPHurValidateMsg.NO_FREE_JOURNAL_POOL.value.format(
                        "primary" if is_primary else "secondary"
                    )
                )
            return free_journal_pools[0].get("journal_pool_id")
        except Exception as e:
            storage_type = "primary" if is_primary else "secondary"
            err_msg = (
                VspRemoteReplicationMsg.STORAGE_INFO.value.format(storage_type)
                + " "
                + str(e)
            )
            logger.writeError(
                "RC: get_free_journal_id: Error occurred while getting free journal ID for {} storage: {}".format(
                    storage_type, err_msg
                )
            )
            raise ValueError(err_msg)

    @log_entry_exit
    def create_hur_batch(self, spec):
        # get free ldev ids
        if spec.should_match_volume_ids is not None and spec.should_match_volume_ids:
            primary_vol_prov = VSPVolumeProvisioner(self.connection_info)
            matching_free_vols = primary_vol_prov.get_matching_free_ldevs(
                spec.number_of_pairs,
                spec.begin_primary_volume_id,
                spec.end_primary_volume_id,
                spec.begin_secondary_volume_id,
                spec.end_secondary_volume_id,
                spec.secondary_connection_info,
            )
            logger.writeDebug("RC:create_hur_batch:matching_free_vols={}", matching_free_vols)
            primary_free_vols = matching_free_vols
            secondary_free_vols = matching_free_vols
        else:
            primary_free_vols = self.get_free_ldevs_for_storage(spec, is_primary=True)
            logger.writeDebug("RC:create_hur_batch:primary_free_vols={}", primary_free_vols)
            secondary_free_vols = self.get_free_ldevs_for_storage(spec, is_primary=False)
            logger.writeDebug("RC:create_hur_batch:secondary_free_vols={}", secondary_free_vols)

        if spec.primary_journal_id is None:
            primary_journal = self.get_free_journal_id(spec, is_primary=True)
            spec.primary_journal_id = primary_journal
            logger.writeDebug(
                "RC:create_hur_batch:primary_journal_id={}", primary_journal
            )
        if spec.secondary_journal_id is None:
            secondary_journal = self.get_free_journal_id(spec, is_primary=False)
            spec.secondary_journal_id = secondary_journal
            logger.writeDebug(
                "RC:create_hur_batch:secondary_journal_id={}", secondary_journal
            )
        primary_hostgroups = None
        secondary_hostgroups = None
        primary_iscsi_targets = None
        secondary_iscsi_targets = None
        primary_nvm_subsystem = None
        secondary_nvm_subsystem = None
        if (
            spec.primary_hostgroups is not None
            and spec.secondary_hostgroups is not None
        ):
            primary_hostgroups = self.check_and_get_host_groups(spec, is_primary=True)
            logger.writeDebug(
                "RC:create_hur_batch:primary_hostgroups={}", primary_hostgroups
            )
            secondary_hostgroups = self.check_and_get_host_groups(
                spec, is_primary=False
            )
            logger.writeDebug(
                "RC:create_hur_batch:secondary_hostgroups={}", secondary_hostgroups
            )
        elif (
            spec.primary_iscsi_targets is not None
            and spec.secondary_iscsi_targets is not None
        ):
            primary_iscsi_targets = self.check_and_get_iscsi_targets(
                spec, is_primary=True
            )
            logger.writeDebug(
                "RC:create_hur_batch:primary_iscsi_targets={}", primary_iscsi_targets
            )
            secondary_iscsi_targets = self.check_and_get_iscsi_targets(
                spec, is_primary=False
            )
            logger.writeDebug(
                "RC:create_hur_batch:secondary_iscsi_targets={}",
                secondary_iscsi_targets,
            )
        elif (
            spec.primary_nvm_subsystem is not None
            and spec.secondary_nvm_subsystem is not None
        ):
            primary_nvm_subsystem = self.check_and_get_nvm_subsystem(
                spec, is_primary=True
            )
            logger.writeDebug(
                "RC:create_hur_batch:primary_nvm_subsystem={}", primary_nvm_subsystem
            )
            secondary_nvm_subsystem = self.check_and_get_nvm_subsystem(
                spec, is_primary=False
            )
            logger.writeDebug(
                "RC:create_hur_batch:secondary_nvm_subsystem={}",
                secondary_nvm_subsystem,
            )
        else:
            raise ValueError(
                VspRemoteReplicationMsg.HOST_GROUPS_OR_IST_OR_NVME_MISSING.value
            )

        # Provision Primary Volumes
        primary_vol_rec = VSPVolumeReconciler(
            self.connection_info, self.storage_serial_number
        )
        primary_volume_spec = self.construct_create_volume_spec(
            spec, primary_free_vols, is_primary=True
        )
        primary_ldev_ids = self.create_ldevs_on_storage(
            primary_volume_spec, primary_vol_rec
        )
        logger.writeDebug("RC:create_hur_batch:primary_ldev_ids={}", primary_ldev_ids)

        if primary_ldev_ids is None:
            raise ValueError(
                VspRemoteReplicationMsg.FAILED_TO_CREATE_LDEVS.value.format("primary")
            )

        # Provision Secondary Volumes
        secondary_vol_rec = VSPVolumeReconciler(
            self.secondary_connection_info, self.storage_serial_number
        )
        secondary_volume_spec = self.construct_create_volume_spec(
            spec, secondary_free_vols, is_primary=False
        )
        secondary_ldev_ids = self.create_ldevs_on_storage(
            secondary_volume_spec, secondary_vol_rec
        )

        logger.writeDebug(
            "RC:create_hur_batch:secondary_ldev_ids={}", secondary_ldev_ids
        )
        if secondary_ldev_ids is None:
            raise ValueError(
                VspRemoteReplicationMsg.FAILED_TO_CREATE_LDEVS.value.format("secondary")
            )

        if spec.should_match_volume_ids is not None and spec.should_match_volume_ids:
            # --- Strict ID Validation and Sorting ---
            # Sort both to ensure a consistent baseline for comparison
            primary_ldev_ids.sort()
            secondary_ldev_ids.sort()
            # Strict Equality Check (Checks length, values, and order)
            if primary_ldev_ids != secondary_ldev_ids:
                err_msg = (
                    f"LDEV ID mismatch detected! HUR requires identical IDs on both sides. "
                    f"Primary created: {primary_ldev_ids}, "
                    f"Secondary created: {secondary_ldev_ids}"
                )
                logger.writeError(f"RC: {err_msg}")
                raise ValueError(err_msg)
            logger.writeInfo("RC: Validated identical LDEV IDs on Primary and Secondary.")

        if primary_hostgroups and secondary_hostgroups:
            self.add_ldevs_to_hostgroups(
                spec, primary_hostgroups, primary_ldev_ids, is_primary=True
            )
            self.add_ldevs_to_hostgroups(
                spec, secondary_hostgroups, secondary_ldev_ids, is_primary=False
            )
        elif primary_iscsi_targets and secondary_iscsi_targets:
            self.add_ldevs_to_iscsi_targets(
                spec, primary_iscsi_targets, primary_ldev_ids, is_primary=True
            )
            self.add_ldevs_to_iscsi_targets(
                spec, secondary_iscsi_targets, secondary_ldev_ids, is_primary=False
            )
        elif primary_nvm_subsystem and secondary_nvm_subsystem:
            self.add_ldevs_to_nvm_subsystem(
                spec, primary_nvm_subsystem, primary_ldev_ids, is_primary=True
            )
            self.add_ldevs_to_nvm_subsystem(
                spec, secondary_nvm_subsystem, secondary_ldev_ids, is_primary=False
            )
        else:
            raise ValueError(
                VspRemoteReplicationMsg.HOST_GROUPS_OR_IST_OR_NVME_MISSING.value
            )
        spec.comments = []
        hur_response = []
        hur_lock = threading.Lock()
        stop_event = threading.Event()

        def create_hur_pair(primary_ldev_id, secondary_ldev_id):
            if stop_event.is_set():
                return
            logger.writeDebug("RC:create_hur_pair_for_index:spec={}", spec)
            try:
                # Use a copy of spec for each thread to avoid race conditions
                local_spec = copy.deepcopy(spec)
                local_spec.primary_volume_id = primary_ldev_id
                local_spec.provisioned_secondary_volume_id = secondary_ldev_id
                local_spec.copy_pair_name = (
                    f"{spec.copy_pair_base_name}_{primary_ldev_id}_{secondary_ldev_id}"
                )
                local_spec.primary_volume_journal_id = spec.primary_journal_id
                local_spec.secondary_volume_journal_id = spec.secondary_journal_id
                # local_spec.is_new_group_creation = spec.is_new_group_creation
                logger.writeDebug("RC: hur_batch_reconcile: local_spec={}", local_spec)
                logger.writeDebug(
                    "RC:create_hur_pair_for_index:spec.is_data_reduction_force_copy={}",
                    spec.is_data_reduction_force_copy,
                )

                result = self.reconcile_hur(local_spec)
                with hur_lock:
                    if result is not None and len(result) > 0:
                        hur_response.append(result[0])
                    if primary_ldev_id in primary_ldev_ids:
                        primary_ldev_ids.remove(primary_ldev_id)
                        self.connection_info.changed = True
                    if secondary_ldev_id in secondary_ldev_ids:
                        secondary_ldev_ids.remove(secondary_ldev_id)
                    if local_spec.comments:
                        spec.comments.append(local_spec.comments)
            except Exception as e:
                with hur_lock:
                    spec.comments.append(
                        f"Exception while creating HUR pair for volume {primary_ldev_id} and secondary_volume_id={secondary_ldev_id}: {str(e)}"
                    )

        threads = []
        try:
            # Run the first pair synchronously (wait for completion)
            if primary_ldev_ids and secondary_ldev_ids:
                primary_ldev_ids.sort()
                secondary_ldev_ids.sort()
                create_hur_pair(primary_ldev_ids[0], secondary_ldev_ids[0])
                # Remove the first ids since they are already processed
                if len(hur_response) == 0:
                    # If the first pair creation failed, stop processing further pairs
                    raise ValueError(
                        spec.comments[-1]
                        if spec.comments
                        else "Failed to create the first HUR pair, stopping batch processing"
                    )
            logger.writeDebug(
                "RC: hur_batch_reconcile: first pair processed, remaining primary_ldev_ids={}, secondary_ldev_ids={}",
                primary_ldev_ids,
                secondary_ldev_ids,
            )
            spec.is_new_group_creation = False
            # Run the rest concurrently
            for primary_ldev_id, secondary_ldev_id in zip(
                primary_ldev_ids, secondary_ldev_ids
            ):
                logger.writeDebug(
                    "RC: gad_batch_reconcile: creating thread for primary_ldev_id={}, secondary_ldev_id={}",
                    primary_ldev_id,
                    secondary_ldev_id,
                )

                t = threading.Thread(
                    target=create_hur_pair, args=(primary_ldev_id, secondary_ldev_id)
                )
                threads.append(t)
                t.start()

            for t in threads:
                t.join()
        except KeyboardInterrupt:
            stop_event.set()
            for t in threads:
                t.join(timeout=1.0)
            raise
        except Exception as e:
            pass

        if len(primary_ldev_ids) > 0:
            self._cleanup_ldevs(primary_volume_spec, primary_ldev_ids, primary_vol_rec)
        if len(secondary_ldev_ids) > 0:
            self._cleanup_ldevs(
                secondary_volume_spec, secondary_ldev_ids, secondary_vol_rec
            )

        # If any error occurred, return False
        if any(isinstance(r, bool) and r is False for r in hur_response):
            return False

        return hur_response

    def _cleanup_ldevs(self, volume_spec, ldev_ids, vol_prov, force=True):
        volume_spec.ldev_ids = ldev_ids
        volume_spec.force = force
        vol_prov._handle_ldev_delete_operations(volume_spec)
        self.connection_info.changed = False

    @log_entry_exit
    def reconcile_hur_batch(self, spec):

        state = self.state.lower()

        if self.secondary_connection_info is None:
            raise ValueError(VSPTrueCopyValidateMsg.SECONDARY_CONNECTION_INFO.value)
        else:
            spec.secondary_connection_info = self.secondary_connection_info

        resp_data = None
        if state == StateValue.PRESENT:
            resp_data = self.create_hur_batch(spec)
            logger.writeDebug("RC:resp_data={}", resp_data)
            return resp_data


class DirectHurCopyPairInfoExtractor:
    def __init__(self, serial):
        self.storage_serial_number = serial
        self.common_properties = {
            "consistencyGroupId": int,
            "copyGroupName": str,
            "copyPairName": str,
            "copyRate": int,
            "fenceLevel": str,
            "muNumber": int,
            "mirrorUnitId": int,
            "localDeviceGroupName": str,
            "remoteDeviceGroupName": str,
            "primaryJournalPool": str,
            "primaryVolumeIdHex": str,
            "primaryVolumeStatus": str,
            "primaryVolumeStorageSerialNumber": str,
            "pvolJournalId": int,
            "pvolLdevId": int,
            "pvolStatus": str,
            "pvolStorageDeviceId": str,
            "remoteMirrorCopyPairId": str,
            "secondaryJournalPool": str,
            "secondaryVolumeIdHex": str,
            "secondaryVolumeStatus": str,
            "secondaryVolumeStorageSerialNumber": str,
            "svolJournalId": int,
            "svolLdevId": int,
            "svolStatus": str,
            "svolStorageDeviceId": str,
        }

        self.parameter_mapping = {
            "mu_number": "mirror_unit_number",
            "pvol_journal_id": "primary_journal_id",
            "svol_journal_id": "secondary_journal_id",
            "pvol_ldev_id": "primary_volume_id",
            "svol_ldev_id": "secondary_volume_id",
        }

    def fix_bad_camel_to_snake_conversion(self, key):
        new_key = key.replace("s_s_w_s", "ssws")
        return new_key

    @log_entry_exit
    def extract(self, responses):
        new_items = []
        if responses is None:
            return new_items
        if isinstance(responses, dict):
            responses = [responses]

        for response in responses:
            new_dict = {}

            if response.get("primaryVolumeSize"):
                new_dict["primary_volume_size"] = response.get("primaryVolumeSize")
            if response.get("secondaryVolumeSize"):
                new_dict["secondary_volume_size"] = response.get("secondaryVolumeSize")

            for key, value_type in self.common_properties.items():
                # Get the corresponding key from the response or its mapped key
                if response is None:
                    return new_items
                response_key = response.get(key)
                # Assign the value based on the response key and its data type
                cased_key = camel_to_snake_case(key)
                if "s_s_w_s" in cased_key:
                    cased_key = self.fix_bad_camel_to_snake_conversion(cased_key)
                if cased_key in self.parameter_mapping.keys():
                    cased_key = self.parameter_mapping[cased_key]
                if response_key is not None:
                    new_dict[cased_key] = response_key
                else:
                    # Handle missing keys by assigning default values
                    default_value = get_default_value(value_type)
                    new_dict[cased_key] = default_value

            new_dict = self.standardize_output(new_dict)

            new_items.append(new_dict)

        return new_items

    @log_entry_exit
    def standardize_output(self, new_dict):
        if new_dict.get("primary_volume_id_hex") == "":
            if (
                new_dict.get("primary_volume_id") is not None
                and new_dict.get("primary_volume_id") != ""
            ):
                new_dict["primary_volume_id_hex"] = volume_id_to_hex_format(
                    new_dict.get("primary_volume_id")
                )
        if new_dict.get("secondary_volume_id_hex") == "":
            if (
                new_dict.get("secondary_volume_id") is not None
                and new_dict.get("secondary_volume_id") != ""
            ):
                new_dict["secondary_volume_id_hex"] = volume_id_to_hex_format(
                    new_dict.get("secondary_volume_id")
                )
        if new_dict.get("primary_volume_status") == "":
            new_dict["primary_volume_status"] = new_dict.get("pvol_status")

        if new_dict.get("secondary_volume_status") == "":
            new_dict["secondary_volume_status"] = new_dict.get("svol_status")

        if new_dict.get("local_device_group_name") == "":
            new_dict["local_device_group_name"] = (
                get_local_device_group_name_from_copy_pair_id(
                    new_dict.get("remote_mirror_copy_pair_id", "")
                )
            )

        if new_dict.get("remote_device_group_name") == "":
            new_dict["remote_device_group_name"] = (
                get_remote_device_group_name_from_copy_pair_id(
                    new_dict.get("remote_mirror_copy_pair_id", "")
                )
            )

        if new_dict.get("primary_volume_storage_serial_number") == "":
            new_dict["primary_volume_storage_serial_number"] = (
                get_serial_number_from_device_id(
                    new_dict.get("pvol_storage_device_id", "")
                )
            )
            new_dict["primary_volume_storage_id"] = get_serial_number_from_device_id(
                new_dict.get("pvol_storage_device_id", "")
            )

        if new_dict.get("secondary_volume_storage_serial_number") == "":
            new_dict["secondary_volume_storage_serial_number"] = (
                get_serial_number_from_device_id(
                    new_dict.get("svol_storage_device_id", "")
                )
            )
            new_dict["secondary_volume_storage_id"] = get_serial_number_from_device_id(
                new_dict.get("svol_storage_device_id", "")
            )

        new_dict["mirror_unit_id"] = new_dict.get("mirror_unit_number", -1)

        if new_dict.get("primary_journal_pool") == "":
            new_dict["primary_journal_pool"] = new_dict.get("primary_journal_id")

        if new_dict.get("secondary_journal_pool") == "":
            new_dict["secondary_journal_pool"] = new_dict.get("secondary_journal_id")

        if new_dict.get("mu_number"):
            new_dict.pop("mu_number")

        return new_dict

    @log_entry_exit
    def extract_dict(self, response):
        new_dict = {"storage_serial_number": self.storage_serial_number}
        for key, value_type in self.common_properties.items():
            # Get the corresponding key from the response or its mapped key
            response_key = response.get(key)
            # Assign the value based on the response key and its data type
            cased_key = camel_to_snake_case(key)
            if "s_s_w_s" in cased_key:
                cased_key = self.fix_bad_camel_to_snake_conversion(cased_key)
            if cased_key in self.parameter_mapping.keys():
                cased_key = self.parameter_mapping[cased_key]
            if response_key is not None:
                new_dict[cased_key] = value_type(response_key)
            else:
                # Handle missing keys by assigning default values
                default_value = get_default_value(value_type)
                new_dict[cased_key] = default_value

        new_dict = self.standardize_output(new_dict)
        return new_dict
