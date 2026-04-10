import threading
from typing import Any
import copy

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
    from ..provisioner.vsp_true_copy_provisioner import VSPTrueCopyProvisioner
    from ..provisioner.vsp_host_group_provisioner import VSPHostGroupProvisioner
    from ..provisioner.vsp_iscsi_target_provisioner import VSPIscsiTargetProvisioner
    from ..provisioner.vsp_nvme_provisioner import VSPNvmeProvisioner
    from ..provisioner.vsp_volume_prov import VSPVolumeProvisioner
    from ..gateway.vsp_storage_system_gateway import VSPStorageSystemDirectGateway
    from ..message.vsp_true_copy_msgs import VSPTrueCopyValidateMsg, TrueCopyFailedMsg
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
    from provisioner.vsp_true_copy_provisioner import VSPTrueCopyProvisioner
    from provisioner.vsp_host_group_provisioner import VSPHostGroupProvisioner
    from provisioner.vsp_iscsi_target_provisioner import VSPIscsiTargetProvisioner
    from provisioner.vsp_nvme_provisioner import VSPNvmeProvisioner
    from provisioner.vsp_volume_prov import VSPVolumeProvisioner
    from gateway.vsp_storage_system_gateway import VSPStorageSystemDirectGateway
    from message.vsp_true_copy_msgs import VSPTrueCopyValidateMsg, TrueCopyFailedMsg

logger = Log()


class VSPTrueCopyReconciler:
    def __init__(
        self, connection_info, serial=None, state=None, secondary_connection_info=None
    ):

        self.connection_info = connection_info
        self.storage_serial_number = serial
        self.secondary_connection_info = None
        self.provisioner = VSPTrueCopyProvisioner(connection_info, serial)
        if state:
            self.state = state
        if secondary_connection_info:
            self.secondary_connection_info = secondary_connection_info
        if self.storage_serial_number is None:
            self.storage_serial_number = self.get_storage_serial_number()

    @log_entry_exit
    def get_storage_serial_number(self):
        storage_gw = VSPStorageSystemDirectGateway(self.connection_info)
        storage_system = storage_gw.get_current_storage_system_info()
        return storage_system.serialNumber

    @log_entry_exit
    def delete_true_copy(self, spec):
        self.validate_tc_spec_for_ops(spec)
        try:
            pair_id = self.provisioner.delete_true_copy_pair(spec)
            return pair_id
        except Exception as e:
            logger.writeError("RC:delete_true_copy:exception={}", str(e))
            self.connection_info.changed = False
            spec.comments = TrueCopyFailedMsg.DELETE_PAIR_FAILED.value + str(e)
            # return None, str(e)
            return None

    @log_entry_exit
    def validate_tc_spec_for_ops_resize(self, spec: Any) -> None:
        self.validate_tc_spec_for_ops(spec)
        if spec.new_volume_size is None:
            raise ValueError(VSPTrueCopyValidateMsg.NEW_VOLUME_SIZE.value)

    @log_entry_exit
    def validate_tc_spec_for_ops(self, spec: Any) -> None:

        if spec.primary_volume_id:
            if spec.copy_group_name is None:
                raise ValueError(VSPTrueCopyValidateMsg.COPY_GROUP_NAME.value)

        if spec.copy_group_name:
            if spec.copy_pair_name is None and spec.primary_volume_id is None:
                raise ValueError(
                    VSPTrueCopyValidateMsg.PVOL_ID_OR_CP_NAME_NEEDED_WITH_CG_NAME.value
                )

    @log_entry_exit
    def resync_true_copy(self, spec):
        self.validate_tc_spec_for_ops(spec)
        return self.provisioner.resync_true_copy_pair(spec)

    @log_entry_exit
    def split_true_copy(self, spec):
        self.validate_tc_spec_for_ops(spec)
        return self.provisioner.split_true_copy_pair(spec)

    @log_entry_exit
    def swap_split_true_copy(self, spec):
        self.validate_tc_spec_for_ops(spec)
        return self.provisioner.swap_split_true_copy_pair(spec)

    @log_entry_exit
    def swap_resync_true_copy(self, spec):
        self.validate_tc_spec_for_ops(spec)
        return self.provisioner.swap_resync_true_copy_pair(spec)

    @log_entry_exit
    def resize_true_copy(self, spec):
        self.validate_tc_spec_for_ops_resize(spec)
        return self.provisioner.resize_true_copy_copy_pair(spec)

    @log_entry_exit
    def create_true_copy(self, spec):
        self.validate_create_spec(spec)
        pvol = self.provisioner.get_volume_by_id(spec.primary_volume_id)
        logger.writeDebug("RC:create_true_copy:pvol={} ", pvol)
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
        return self.provisioner.create_true_copy(spec=spec)

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
                    VSPTrueCopyValidateMsg.SECONDARY_VOLUME_ID_OUT_OF_RANGE.value
                )

    @log_entry_exit
    def reconcile_true_copy(self, spec: Any) -> Any:
        """
        Reconcile the TrueCopy based on the desired state in the specification.
        """
        state = self.state.lower()
        if self.secondary_connection_info is None:
            raise ValueError(VSPTrueCopyValidateMsg.SECONDARY_CONNECTION_INFO.value)
        else:
            spec.secondary_connection_info = self.secondary_connection_info

        resp_data = None
        if state == StateValue.ABSENT:
            result = self.delete_true_copy(spec)
            return result
        elif state == StateValue.PRESENT:
            resp_data = self.create_true_copy(spec=spec)
            logger.writeDebug("RC:resp_data={}", resp_data)
        elif state == StateValue.SPLIT:
            resp_data = self.split_true_copy(spec)
        elif state == StateValue.RE_SYNC:
            resp_data = self.resync_true_copy(spec)
        elif state == StateValue.SWAP_SPLIT:
            resp_data = self.swap_split_true_copy(spec)
        elif state == StateValue.SWAP_RESYNC:
            resp_data = self.swap_resync_true_copy(spec)
        elif state == StateValue.RESIZE or state == StateValue.EXPAND:
            resp_data = self.resize_true_copy(spec)

        if resp_data:
            logger.writeDebug("RC:resp_data={}  state={}", resp_data, state)
            if isinstance(resp_data, dict):
                return resp_data

            resp_in_dict = resp_data.to_dict()
            logger.writeDebug("RC:reconcile_true_copy:tc_pairs={}", resp_in_dict)

            return self.inject_pvol_svol_size_then_return(resp_in_dict, state=state)
        else:
            return None

    @log_entry_exit
    def inject_pvol_svol_size_then_return(self, resp_dict: dict, state=None) -> dict:
        if state and state == StateValue.SWAP_SPLIT:
            # for swap split, the primary and secondary connection are swapped, so we need to get the sizes accordingly
            pvolData = self.provisioner.get_volume_by_id(
                resp_dict["svolLdevId"], include_drs=False
            )
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
        return DirectTrueCopyInfoExtractor(self.storage_serial_number).extract(
            [resp_dict]
        )

    @log_entry_exit
    def validate_tc_fact_spec(self, spec: Any) -> None:
        if self.secondary_connection_info is None:
            raise ValueError(VSPTrueCopyValidateMsg.SECONDARY_CONNECTION_INFO.value)
        else:
            spec.secondary_connection_info = self.secondary_connection_info

    def get_true_copy_facts(self, spec=None):
        self.validate_tc_fact_spec(spec)
        tc_pairs = self.provisioner.get_true_copy_facts(
            spec, self.storage_serial_number
        )
        logger.writeDebug("RC:get_true_copy_facts:tc_pairs={}", tc_pairs)

        if tc_pairs is None:
            return []
        else:
            if len(tc_pairs.data) == 1:
                return self.inject_pvol_svol_size_then_return(
                    tc_pairs.data[0].to_dict()
                )
            extracted_data = DirectTrueCopyInfoExtractor(
                self.storage_serial_number
            ).extract(tc_pairs.data_to_list())
        return extracted_data

    @log_entry_exit
    def reconcile_true_copy_hatch(self, spec):

        state = self.state.lower()

        if self.secondary_connection_info is None:
            raise ValueError(VSPTrueCopyValidateMsg.SECONDARY_CONNECTION_INFO.value)
        else:
            spec.secondary_connection_info = self.secondary_connection_info

        resp_data = None
        if state == StateValue.PRESENT:
            resp_data = self.create_tc_batch(spec)
            logger.writeDebug("RC:resp_data={}", resp_data)
            return resp_data

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
    def create_tc_batch(self, spec):

        primary_free_vols = self.get_free_ldevs_for_storage(spec, is_primary=True)
        logger.writeDebug("RC:create_tc_batch:primary_free_vols={}", primary_free_vols)
        secondary_free_vols = self.get_free_ldevs_for_storage(spec, is_primary=False)
        logger.writeDebug(
            "RC:create_tc_batch:secondary_free_vols={}", secondary_free_vols
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
                "RC:create_tc_batch:primary_hostgroups={}", primary_hostgroups
            )
            secondary_hostgroups = self.check_and_get_host_groups(
                spec, is_primary=False
            )
            logger.writeDebug(
                "RC:create_tc_batch:secondary_hostgroups={}", secondary_hostgroups
            )
        elif (
            spec.primary_iscsi_targets is not None
            and spec.secondary_iscsi_targets is not None
        ):
            primary_iscsi_targets = self.check_and_get_iscsi_targets(
                spec, is_primary=True
            )
            logger.writeDebug(
                "RC:create_tc_batch:primary_iscsi_targets={}", primary_iscsi_targets
            )
            secondary_iscsi_targets = self.check_and_get_iscsi_targets(
                spec, is_primary=False
            )
            logger.writeDebug(
                "RC:create_tc_batch:secondary_iscsi_targets={}", secondary_iscsi_targets
            )
        elif (
            spec.primary_nvm_subsystem is not None
            and spec.secondary_nvm_subsystem is not None
        ):
            primary_nvm_subsystem = self.check_and_get_nvm_subsystem(
                spec, is_primary=True
            )
            logger.writeDebug(
                "RC:create_tc_batch:primary_nvm_subsystem={}", primary_nvm_subsystem
            )
            secondary_nvm_subsystem = self.check_and_get_nvm_subsystem(
                spec, is_primary=False
            )
            logger.writeDebug(
                "RC:create_tc_batch:secondary_nvm_subsystem={}", secondary_nvm_subsystem
            )
        else:
            raise ValueError(
                VspRemoteReplicationMsg.HOST_GROUPS_OR_IST_OR_NVME_MISSING.value
            )
        primary_vol_rec = VSPVolumeReconciler(
            self.connection_info, self.storage_serial_number
        )
        primary_volume_spec = self.construct_create_volume_spec(
            spec, primary_free_vols, is_primary=True
        )
        primary_ldev_ids = self.create_ldevs_on_storage(
            primary_volume_spec, primary_vol_rec
        )
        logger.writeDebug("RC:create_tc_batch:primary_ldev_ids={}", primary_ldev_ids)

        if primary_ldev_ids is None:
            raise ValueError(
                VspRemoteReplicationMsg.FAILED_TO_CREATE_LDEVS.value.format("primary")
            )
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
            "RC:create_tc_batch:secondary_ldev_ids={}", secondary_ldev_ids
        )
        if secondary_ldev_ids is None:
            raise ValueError(
                VspRemoteReplicationMsg.FAILED_TO_CREATE_LDEVS.value.format("secondary")
            )
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
        tc_response = []
        tc_lock = threading.Lock()
        stop_event = threading.Event()

        def create_tc_pair(primary_ldev_id, secondary_ldev_id):
            if stop_event.is_set():
                return
            logger.writeDebug("RC:create_tc_pair_for_index:spec={}", spec)
            try:
                # Use a copy of spec for each thread to avoid race conditions
                local_spec = copy.deepcopy(spec)
                local_spec.primary_volume_id = primary_ldev_id
                local_spec.provisioned_secondary_volume_id = secondary_ldev_id
                local_spec.copy_pair_name = (
                    f"{spec.copy_pair_base_name}_{primary_ldev_id}_{secondary_ldev_id}"
                )

                logger.writeDebug("RC: tc_batch_reconcile: local_spec={}", local_spec)
                logger.writeDebug(
                    "RC:create_tc_pair_for_index:spec.is_data_reduction_force_copy={}",
                    spec.is_data_reduction_force_copy,
                )

                result = self.reconcile_true_copy(local_spec)
                with tc_lock:
                    if result is not None and len(result) > 0:
                        tc_response.append(result[0])
                    if primary_ldev_id in primary_ldev_ids:
                        primary_ldev_ids.remove(primary_ldev_id)
                        self.connection_info.changed = True
                    if secondary_ldev_id in secondary_ldev_ids:
                        secondary_ldev_ids.remove(secondary_ldev_id)
                    if local_spec.comments:
                        spec.comments.append(local_spec.comments)
            except Exception as e:
                with tc_lock:
                    spec.comments.append(
                        VSPTrueCopyValidateMsg.TC_BATCH_CREATION_ERROR.value.format(
                            primary_ldev_id, secondary_ldev_id
                        )
                        + " "
                        + str(e)
                    )

        threads = []
        try:
            # Run the first pair synchronously (wait for completion)
            if primary_ldev_ids and secondary_ldev_ids:
                create_tc_pair(primary_ldev_ids[0], secondary_ldev_ids[0])
                # Remove the first ids since they are already processed
                # primary_ldev_ids.remove(primary_ldev_ids[0])
                # secondary_ldev_ids.remove(secondary_ldev_ids[0])
                if len(tc_response) == 0:
                    # If the first pair creation failed, stop processing further pairs
                    raise ValueError(
                        VSPTrueCopyValidateMsg.TC_BATCH_CREATION_ERROR.value.format(
                            primary_ldev_ids[0], secondary_ldev_ids[0]
                        )
                    )
                else:
                    logger.writeDebug(
                        "RC: tc_batch_reconcile: first pair created successfully, output={}",
                        tc_response[0],
                    )
            logger.writeDebug(
                "RC: tc_batch_reconcile: first pair processed, remaining primary_ldev_ids={}, secondary_ldev_ids={}",
                primary_ldev_ids,
                secondary_ldev_ids,
            )
            spec.is_new_group_creation = False
            # Run the rest concurrently
            for primary_ldev_id, secondary_ldev_id in zip(
                primary_ldev_ids, secondary_ldev_ids
            ):
                logger.writeDebug(
                    "RC: tc_batch_reconcile: creating thread for primary_ldev_id={}, secondary_ldev_id={}",
                    primary_ldev_id,
                    secondary_ldev_id,
                )

                t = threading.Thread(
                    target=create_tc_pair, args=(primary_ldev_id, secondary_ldev_id)
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
        if any(isinstance(r, bool) and r is False for r in tc_response):
            return False

        # extracted_data = DirectHurCopyPairInfoExtractor(
        #     self.storage_serial_number
        # ).extract(tc_response)
        return tc_response

    def _cleanup_ldevs(self, volume_spec, ldev_ids, vol_prov, force=True):
        volume_spec.ldev_ids = ldev_ids
        volume_spec.force = force
        vol_prov._handle_ldev_delete_operations(volume_spec)
        self.connection_info.changed = False


class DirectTrueCopyInfoExtractor:
    def __init__(self, serial):
        self.storage_serial_number = serial
        self.common_properties = {
            "consistencyGroupId": int,
            "copyGroupName": str,
            "copyPairName": str,
            "copyProgressRate": int,
            "fenceLevel": str,
            "localDeviceGroupName": str,
            "remoteDeviceGroupName": str,
            "pvolLdevId": int,
            "svolLdevId": int,
            "primaryVolumeIdHex": str,
            "pvolStatus": str,
            "primaryVolumeStatus": str,
            "svolStatus": str,
            "secondaryVolumeStatus": str,
            "pvolStorageDeviceId": str,
            "svolStorageDeviceId": str,
            "remoteMirrorCopyPairId": str,
            "secondaryVolumeIdHex": str,
            "primaryVolumeStorageSerialNumber": str,
            "secondaryVolumeStorageSerialNumber": str,
        }

        self.parameter_mapping = {
            "pvol_ldev_id": "primary_volume_id",
            "svol_ldev_id": "secondary_volume_id",
        }

    def fix_bad_camel_to_snake_conversion(self, key):
        new_key = key.replace("v_s_m", "vsm")
        return new_key

    @log_entry_exit
    def extract(self, responses):
        new_items = []
        for response in responses:
            new_dict = {"storage_serial_number": self.storage_serial_number}

            if response.get("primaryVolumeSize"):
                new_dict["primary_volume_size"] = response.get("primaryVolumeSize")
            if response.get("secondaryVolumeSize"):
                new_dict["secondary_volume_size"] = response.get("secondaryVolumeSize")

            for key, value_type in self.common_properties.items():
                # Get the corresponding key from the response or its mapped key
                response_key = response.get(key)
                # Assign the value based on the response key and its data type
                cased_key = camel_to_snake_case(key)
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

        if new_dict.get("secondary_volume_storage_serial_number") == "":
            new_dict["secondary_volume_storage_serial_number"] = (
                get_serial_number_from_device_id(
                    new_dict.get("svol_storage_device_id", "")
                )
            )

        return new_dict

    @log_entry_exit
    def extract_dict(self, response):
        new_dict = {"storage_serial_number": self.storage_serial_number}
        for key, value_type in self.common_properties.items():
            # Get the corresponding key from the response or its mapped key
            response_key = response.get(key)
            # Assign the value based on the response key and its data type
            cased_key = camel_to_snake_case(key)
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
