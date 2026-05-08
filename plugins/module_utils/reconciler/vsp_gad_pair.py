from typing import Any
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import copy

from ..common.vsp_utils import (
    get_local_device_group_name_from_copy_pair_id,
    get_remote_device_group_name_from_copy_pair_id,
    get_serial_number_from_device_id,
)

try:
    from ..common.ansible_common import (
        log_entry_exit,
        camel_to_snake_case,
        volume_id_to_hex_format,
        convert_block_capacity,
        get_default_value,
    )
    from ..common.hv_log import Log
    from ..provisioner.vsp_gad_pair_provisioner import GADPairProvisioner
    from ..provisioner.vsp_volume_prov import VSPVolumeProvisioner
    from ..provisioner.vsp_host_group_provisioner import VSPHostGroupProvisioner
    from ..provisioner.vsp_iscsi_target_provisioner import VSPIscsiTargetProvisioner
    from ..provisioner.vsp_nvme_provisioner import VSPNvmeProvisioner
    from ..reconciler.vsp_volume import VSPVolumeReconciler
    from ..reconciler.vsp_nvme import VSPNvmeReconciler
    from ..reconciler.vsp_resource_group import VSPResourceGroupReconciler
    from ..provisioner.vsp_resource_group_provisioner import VSPResourceGroupProvisioner
    from ..reconciler.vsp_host_group import VSPHostGroupReconciler
    from ..reconciler.vsp_iscsi_target import VSPIscsiTargetReconciler
    from ..gateway.vsp_storage_system_gateway import VSPStorageSystemDirectGateway
    from ..model.vsp_gad_pairs_models import VspGadPairSpec
    from ..common.hv_constants import StateValue
    from ..message.vsp_gad_pair_msgs import GADPairValidateMSG
    from ..model.vsp_resource_group_models import (
        VSPResourceGroupFactSpec,
        VSPResourceGroupSpec,
        HostGroupInfo,
    )
    from ..model.vsp_gad_pairs_models import (
        VspBatchGadPairSpec,
    )
    from ..model.vsp_host_group_models import HostGroupSpec
    from ..model.vsp_iscsi_target_models import IscsiTargetSpec
    from ..model.vsp_nvme_models import VSPNvmeSubsystemSpec
    from ..model.vsp_resource_group_models import VSPResourceGroupSpec
    from ..model.vsp_volume_models import CreateVolumeSpec, LdevNamespec
    from ..message.vsp_true_copy_msgs import VSPTrueCopyValidateMsg
    from ..common.ansible_common_constants import MAX_WORKER_THREADS
    from ..provisioner.vsp_gad_pair_provisioner import GadHelperForSvol

except ImportError:
    from message.vsp_gad_pair_msgs import GADPairValidateMSG
    from common.ansible_common import (
        log_entry_exit,
        camel_to_snake_case,
        volume_id_to_hex_format,
        convert_block_capacity,
        get_default_value,
    )
    from common.hv_log import Log
    from provisioner.vsp_gad_pair_provisioner import GADPairProvisioner
    from provisioner.vsp_volume_prov import VSPVolumeProvisioner
    from reconciler.vsp_volume import VSPVolumeReconciler

    from provisioner.vsp_resource_group_provisioner import VSPResourceGroupProvisioner
    from gateway.vsp_storage_system_gateway import VSPStorageSystemDirectGateway
    from model.vsp_gad_pairs_models import VspGadPairSpec
    from common.hv_constants import StateValue
    from model.vsp_resource_group_models import (
        VSPResourceGroupFactSpec,
    )
    from model.vsp_gad_pairs_models import (
        VspBatchGadPairSpec,
    )
    from message.vsp_true_copy_msgs import VSPTrueCopyValidateMsg

logger = Log()


class VSPGadPairReconciler:

    def __init__(self, connection_info, secondary_connection_info=None, serial=None):
        self.connection_info = connection_info
        self.secondary_connection_info = secondary_connection_info
        self.storage_serial_number = serial
        if self.storage_serial_number is None:
            self.storage_serial_number = self.get_storage_serial_number()
        self.serial = self.storage_serial_number
        self.provisioner = GADPairProvisioner(self.connection_info, self.serial)
        self.provisioner_volume = VSPVolumeProvisioner(
            self.connection_info, self.serial
        )
        self.provisioner_rg = VSPResourceGroupProvisioner(
            self.connection_info, self.serial
        )

    @log_entry_exit
    def get_storage_serial_number(self):
        storage_gw = VSPStorageSystemDirectGateway(self.connection_info)
        storage_system = storage_gw.get_current_storage_system_info()
        return storage_system.serialNumber

    @log_entry_exit
    def gad_pair_reconcile(
        self, state: str, spec: VspGadPairSpec, secondary_connection_info: str
    ) -> Any:
        state = state.lower()
        if self.secondary_connection_info is None:
            raise ValueError(VSPTrueCopyValidateMsg.SECONDARY_CONNECTION_INFO.value)
        else:
            spec.secondary_connection_info = self.secondary_connection_info

        spec.remote_connection_info = secondary_connection_info
        spec.secondary_storage_connection_info = secondary_connection_info
        spec.secondary_connection_info = secondary_connection_info

        # sng20241114 - TODO
        spec.is_svol_readwriteable = False
        logger.writeDebug("sng20241114 copy_pair_name={}", spec.copy_pair_name)

        resp_data = None
        if state == StateValue.ABSENT:
            result = self.delete_gad_pair(spec)
            return result
        elif state == StateValue.PRESENT:
            resp_data = self.create_gad(spec)
            logger.writeDebug("RC:resp_data={}", resp_data)
        elif state == StateValue.SPLIT:
            resp_data = self.split_gad_pair(spec, None)
        elif state == StateValue.RE_SYNC:
            resp_data = self.resync_gad_pair(spec, None)
        elif state == StateValue.SWAP_SPLIT:
            resp_data = self.swap_split_gad_pair(spec, None)
        elif state == StateValue.SWAP_RESYNC:
            resp_data = self.swap_resync_gad_pair(spec, None)
        elif state == StateValue.RESIZE or state == StateValue.EXPAND:
            resp_data = self.resize_gad_pair(spec, None)
        else:
            return

        if resp_data:
            logger.writeDebug("RC:resp_data={}  state={}", resp_data, state)

            if isinstance(resp_data, str):
                # sng20241126 str message to display
                return resp_data

            resp_in_dict = resp_data.to_dict()

            # inject pvol and svol size in the output
            self.inject_pvol_svol_size(resp_in_dict, state)

            spec.secondary_storage_serial_number = (
                self.provisioner.get_secondary_serial_direct(spec)
            )
            pairs = [resp_in_dict]

            if state == StateValue.SWAP_SPLIT:
                self.connection_info.changed = True
                # sng20241123 you have do swap spit from the secondary storage,
                # but the pair is not swap yet, so we have to swap to show the fact correctly
                self.get_other_attributes(spec, pairs, True, True)
            else:
                # get pvol svol details
                self.get_other_attributes(spec, pairs)

            return DirectGADCopyPairInfoExtractor(self.storage_serial_number).extract(
                pairs
            )
        else:
            return None

    @log_entry_exit
    def inject_pvol_svol_size(self, resp_dict: dict, state=None) -> dict:
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
        return resp_dict

    @log_entry_exit
    def create_gad(self, spec: VspGadPairSpec):
        self.validate_create_spec(spec)

        pvol = self.provisioner.get_volume_by_id(spec.primary_volume_id)
        logger.writeDebug("RC:create_gad:pvol={} ", pvol)
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
        pair = self.provisioner.create_gad_pair(spec, pvol)
        if pair is None:
            raise ValueError(
                GADPairValidateMSG.CREATE_GAD_PAIR_FAILED.value.format(
                    spec.primary_volume_id
                )
            )
        logger.writeDebug(f"RC:gad_pair_reconcile:pair1={pair} type={type(pair)}")
        return pair

    @log_entry_exit
    def gad_batch_reconcile(
        self, state, spec: VspBatchGadPairSpec, secondary_connection_info: str
    ):
        spec.comments = []
        vsm_prov = None
        vsm = None
        unused, rg_id = self._get_vsm_details(spec)

        if spec.virtual_storage_serial_number is not None:
            vsm_prov = VSPResourceGroupProvisioner(
                self.connection_info, self.storage_serial_number
            )
            rg_spec = VSPResourceGroupFactSpec(query=["ldevs"])
            vsms = vsm_prov.get_resource_groups(rg_spec).data
            for vsm_object in vsms:
                if vsm_object.virtualSerialNumber == spec.virtual_storage_serial_number:
                    vsm = vsm_object
                    break
            if not vsm:
                raise ValueError(
                    f"Virtual Storage with id {spec.virtual_storage_serial_number} does not exist"
                )
            if vsm.lockStatus.lower() == "locked":
                raise ValueError(
                    f"Virtual Storage with id {spec.virtual_storage_serial_number} is locked"
                )

        matching_free_vols = None
        if spec.should_match_volume_ids is not None and spec.should_match_volume_ids:
            primary_vol_prov = VSPVolumeProvisioner(self.connection_info)
            matching_free_vols = primary_vol_prov.get_matching_free_ldevs(
                spec.number_of_pairs,
                spec.begin_primary_volume_id,
                spec.end_primary_volume_id,
                spec.begin_secondary_volume_id,
                spec.end_secondary_volume_id,
                secondary_connection_info,
            )
            logger.writeDebug("RC:create_gad_batch:matching_free_vols={}", matching_free_vols)

        primary_vol_rec = VSPVolumeReconciler(
            self.connection_info, self.storage_serial_number
        )
        secondary_vol_rec = VSPVolumeReconciler(
            self.secondary_connection_info, self.storage_serial_number
        )
        name_spec = LdevNamespec(
            base_name=spec.primary_volume_base_name,
            start_number=spec.primary_volume_base_name_start_number,
        )
        primary_volume_spec = CreateVolumeSpec(
            size=spec.volume_size,
            pool_id=spec.primary_pool_id,
            names=name_spec,
            number_of_ldevs=spec.number_of_pairs,
            capacity_saving=spec.capacity_saving,
        )
        primary_volume_spec.start_ldev_id = spec.begin_primary_volume_id
        if spec.number_of_pairs is None:
            primary_volume_spec.end_ldev_id = spec.end_primary_volume_id

        secondary_volume_spec = CreateVolumeSpec(
            size=spec.volume_size,
            pool_id=spec.secondary_pool_id,
            names=name_spec,
            number_of_ldevs=spec.number_of_pairs,
            capacity_saving=spec.capacity_saving,
        )
        secondary_volume_spec.start_ldev_id = spec.begin_secondary_volume_id
        if spec.number_of_pairs is None:
            secondary_volume_spec.end_ldev_id = spec.end_secondary_volume_id

        if matching_free_vols:
            primary_volume_spec.start_ldev_id = matching_free_vols[0]
            primary_volume_spec.end_ldev_id = matching_free_vols[-1]
            secondary_volume_spec.start_ldev_id = matching_free_vols[0]
            secondary_volume_spec.end_ldev_id = matching_free_vols[-1]

        primary_ldevs = primary_vol_rec.ldev_batch_operation(primary_volume_spec)
        primary_ldev_ids = [ldev.ldevId for ldev in primary_ldevs]

        if (
            primary_volume_spec.comments is not None
            and len(primary_volume_spec.comments) > 0
        ):
            spec.comments.extend(primary_volume_spec.comments if spec.comments else [])
            logger.writeDebug(
                "RC: gad_batch_reconcile: primary_volume_spec.comments={}",
                primary_volume_spec.comments,
            )
            if len(primary_ldev_ids) > 0:
                self._cleanup_ldevs(
                    primary_volume_spec, primary_ldev_ids, primary_vol_rec, force=False
                )
            return

        if vsm is not None or rg_id > 0:
            if not self._add_resource_to_vsm(
                spec,
                self.connection_info,
                primary_volume_spec,
                primary_vol_rec,
                vsm,
                vsm_prov,
                ldev_ids=primary_ldev_ids,
                ldevs=primary_ldevs,
                vsm_id=rg_id,
            ):
                return

        if spec.primary_hostgroups:
            if not self._handle_hg_vol_add(
                spec,
                primary_volume_spec,
                primary_vol_rec,
                primary_ldev_ids,
                self.connection_info,
                spec.primary_hostgroups,
                vsm,
                vsm_prov,
            ):
                return
        if spec.primary_iscsi_targets:
            if not self._handle_iscsi_target_vol_add(
                spec,
                primary_volume_spec,
                primary_vol_rec,
                primary_ldev_ids,
                self.connection_info,
                spec.primary_iscsi_targets,
                vsm,
                vsm_prov,
            ):
                return
        if spec.primary_nvm_subsystem:
            if not self._handle_nvme_vol_add(
                spec,
                primary_volume_spec,
                primary_vol_rec,
                primary_ldev_ids,
                self.connection_info,
                spec.primary_nvm_subsystem,
                vsm,
                vsm_prov,
            ):
                return

        # # secondary ldev creation

        secondary_ldevs = secondary_vol_rec.ldev_batch_operation(secondary_volume_spec)
        secondary_ldev_ids = [ldev.ldevId for ldev in secondary_ldevs]

        if (
            secondary_volume_spec.comments is not None
            and len(secondary_volume_spec.comments) > 0
        ):
            spec.comments.extend(
                secondary_volume_spec.comments if spec.comments else []
            )
            logger.writeDebug(
                "RC: gad_batch_reconcile: secondary_volume_spec.comments={}",
                secondary_volume_spec.comments,
            )
            if len(secondary_ldev_ids) > 0:
                self._cleanup_ldevs(
                    secondary_volume_spec,
                    secondary_ldev_ids,
                    secondary_vol_rec,
                    force=False,
                )
                self._cleanup_ldevs(
                    primary_volume_spec, primary_ldev_ids, primary_vol_rec
                )
            return

        gad_response = []
        gad_lock = threading.Lock()
        stop_event = threading.Event()

        def create_gad_pair(ldev_id, secondary_ldev_id):
            if stop_event.is_set():
                return
            try:
                # Use a copy of spec for each thread to avoid race conditions
                local_spec = copy.deepcopy(spec)
                local_spec.primary_volume_id = ldev_id
                local_spec.provisioned_secondary_volume_id = secondary_ldev_id
                local_spec.copy_pair_name = (
                    f"{spec.copy_pair_base_name}_{ldev_id}_{secondary_ldev_id}"
                )

                logger.writeDebug("RC: gad_batch_reconcile: local_spec={}", local_spec)

                gad_data = self.gad_pair_reconcile(
                    StateValue.PRESENT, local_spec, secondary_connection_info
                )

                with gad_lock:
                    gad_response.append(gad_data)
                    if ldev_id in primary_ldev_ids:
                        primary_ldev_ids.remove(ldev_id)
                        self.connection_info.changed = True
                    if secondary_ldev_id in secondary_ldev_ids:
                        secondary_ldev_ids.remove(secondary_ldev_id)
            except Exception as e:
                with gad_lock:
                    spec.comments.append(
                        f"Exception while creating GAD pair for volume {ldev_id}: {str(e)}"
                    )

        threads = []
        try:
            # Run the first pair synchronously (wait for completion)
            if primary_ldev_ids and secondary_ldev_ids:
                primary_ldev_ids.sort()
                secondary_ldev_ids.sort()
                create_gad_pair(primary_ldev_ids[0], secondary_ldev_ids[0])
                # Remove the first ids since they are already processed
                if len(gad_response) == 0:
                    # If the first pair creation failed, stop processing further pairs
                    raise ValueError(
                        spec.comments[-1]
                        if spec.comments
                        else "First GAD pair creation failed"
                    )
            logger.writeDebug(
                "RC: gad_batch_reconcile: first pair processed, remaining primary_ldev_ids={}, secondary_ldev_ids={}",
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
                    target=create_gad_pair, args=(primary_ldev_id, secondary_ldev_id)
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
            self._cleanup_volumes(
                primary_volume_spec, primary_ldev_ids, primary_vol_rec
            )
        if len(secondary_ldev_ids) > 0:
            self._cleanup_volumes(
                secondary_volume_spec, secondary_ldev_ids, secondary_vol_rec
            )
        # If any error occurred, return False
        if any(isinstance(r, bool) and r is False for r in gad_response):
            return False
        return gad_response

    def _handle_hg_vol_add(
        self,
        spec,
        volume_spec,
        vol_prov,
        ldev_ids,
        connection_info,
        hgs,
        vsm=None,
        vsm_prov=None,
    ):
        if vsm is not None:
            if not self._add_resource_to_vsm(
                spec,
                connection_info,
                volume_spec,
                vol_prov,
                vsm,
                vsm_prov,
                hgs=hgs,
                ldev_ids=ldev_ids,
            ):
                return
        hg_rec = VSPHostGroupReconciler(connection_info, None)

        for hg in hgs:
            hg_spec = HostGroupSpec(
                name=hg.name,
                port=hg.port,
                ldevs=ldev_ids,
                lun=hg.lun_id,
                state="present_ldev",
            )
            logger.writeDebug("RC: gad_batch_reconcile: hg_spec={}", hg_spec)
            try:
                unused, errors = hg_rec.provisioner.handle_multi_hg_with_present_ldevs(
                    None,
                    hg_name=hg.name,
                    ports=[hg.port],
                    ldevs=ldev_ids,
                    sub_state="present_ldev",
                )
                if len(errors) > 0:
                    spec.comments.append(
                        f"Failed to add ldevs to host group {hg.name}: {errors}"
                    )
                    self._cleanup_ldevs(volume_spec, ldev_ids, vol_prov)
                    return False

            except Exception as e:
                logger.writeDebug(
                    "RC: Exception while adding ldevs to host group {}: {}",
                    hg.name,
                    str(e),
                )
                spec.comments.append(
                    f"Exception while adding ldevs to host group {hg.name}: {str(e)}"
                )
                self._cleanup_ldevs(volume_spec, ldev_ids, vol_prov)
                return False

        return True

    def _handle_iscsi_target_vol_add(
        self,
        spec,
        volume_spec,
        vol_prov,
        ldev_ids,
        connection_info,
        iscsi_targets,
        vsm=None,
        vsm_prov=None,
    ):
        if vsm is not None:
            if not self._add_resource_to_vsm(
                spec,
                connection_info,
                volume_spec,
                vol_prov,
                vsm,
                vsm_prov,
                iscsi_targets=iscsi_targets,
                ldev_ids=ldev_ids,
            ):
                return

        iscsi_rec = VSPIscsiTargetReconciler(connection_info, None)
        for target in iscsi_targets:
            target_spec = IscsiTargetSpec(
                name=target.name,
                port=target.port,
                ldevs=ldev_ids,
                lun=target.lun_id,
                state="attach_ldev",
            )
            logger.writeDebug("RC: gad_batch_reconcile: target_spec={}", target_spec)
            try:
                target_data = iscsi_rec.iscsi_target_reconciler(
                    StateValue.PRESENT, target_spec
                )
                if target_data.comment is None:
                    spec.comments.append(
                        f"Failed to add ldevs to iSCSI target {target.name}"
                    )
                    volume_spec.ldev_ids = ldev_ids
                    vol_prov._handle_ldev_delete_operations(volume_spec)
                    return False

            except Exception as e:
                spec.comments.append(
                    f"Exception while adding ldevs to iSCSI target {target.name}: {str(e)}"
                )
                self._cleanup_ldevs(volume_spec, ldev_ids, vol_prov)
                return False

        return True

    def _handle_nvme_vol_add(
        self,
        spec,
        volume_spec,
        vol_prov,
        ldev_ids,
        connection_info,
        nvmes,
        vsm=None,
        vsm_prov=None,
    ):
        nvme_rec = VSPNvmeReconciler(connection_info, state=StateValue.PRESENT)
        nvmes_object = nvme_rec.get_nvme_subsystem_by_name(nvmes.name)

        if vsm is not None:
            if not self._add_resource_to_vsm(
                spec,
                connection_info,
                volume_spec,
                vol_prov,
                vsm,
                vsm_prov,
                hgs=spec.primary_hostgroups,
                iscsi_targets=spec.primary_iscsi_targets,
                nvmes=nvmes_object,
                ldev_ids=ldev_ids,
            ):
                return
        nvme_rec = VSPNvmeReconciler(connection_info, state=StateValue.PRESENT)
        name_spaces = [
            {"paths": nvmes.paths, "ldev_id": ldev_id} for ldev_id in ldev_ids
        ]
        nvme_spec = VSPNvmeSubsystemSpec(
            name=nvmes.name,
            namespaces=name_spaces,
            id=nvmes.id,
        )
        logger.writeDebug("RC: gad_batch_reconcile: nvme_spec={}", nvme_spec)
        try:
            unused = nvme_rec.reconcile_nvm_subsystem(nvme_spec)

        except Exception as e:
            spec.comments.append(
                f"Exception while adding ldevs to NVMe subsystem : {str(e)}"
            )
            self._cleanup_ldevs(volume_spec, ldev_ids, vol_prov)
            return False

        return True

    def _cleanup_volumes(self, volume_spec, ldev_ids, vol_prov, force=True):
        """Clean up logical devices (volumes) after failed operations."""
        helper_prov = GadHelperForSvol(vol_prov.connection_info, vol_prov.serial)
        for ldev in ldev_ids:
            logger.writeDebug("RC: Cleaning up ldev_id={}", ldev)
            try:
                vol = vol_prov.provisioner.get_volume_by_ldev_id(ldev)
                if vol:
                    if vol.nvmSubsystemId is not None:
                        helper_prov.delete_volume_when_nvme(
                            ldev, vol.nvmSubsystemId, None, vol.namespaceId, vol
                        )
                    else:
                        helper_prov.delete_volume(ldev, vol)
            except Exception as e:
                logger.writeDebug(
                    "RC: Exception while cleaning up ldev {}: {}".format(ldev, str(e))
                )
        self.connection_info.changed = False

    # Alias for backward compatibility
    _cleanup_ldevs = _cleanup_volumes

    def _add_resource_to_vsm(
        self,
        spec,
        connection_info,
        volume_spec,
        vol_prov,
        vsm,
        vsm_prov,
        ldev_ids=None,
        ldevs=None,
        hgs=None,
        iscsi_targets=None,
        nvmes=None,
        vsm_id=None,
    ):
        vsm_spec = VSPResourceGroupSpec()
        vsm_spec.state = "add_resource"
        rg_rec = VSPResourceGroupReconciler(
            connection_info=connection_info, state=StateValue.PRESENT
        )
        if ldevs:
            vsm_spec.ldevs = [ldev.ldevId for ldev in ldevs]
        if hgs:
            hgs = [HostGroupInfo(name=hg.name, port=hg.port) for hg in hgs]
            vsm_spec.host_groups = hgs
        if iscsi_targets:
            targets = [
                HostGroupInfo(name=target.name, port=target.port)
                for target in iscsi_targets
            ]
            vsm_spec.iscsi_targets = targets
        if nvmes:
            vsm_spec.nvm_subsystem_ids = [nvmes.nvmSubsystemId]
        vsm_spec.id = vsm.id if vsm else vsm_id
        try:
            rg = rg_rec.provisioner.get_resource_group_by_id(vsm_spec.id)
            rg_rec.update_resource_group(rg, vsm_spec)

            if ldevs:
                for ldev in ldevs:
                    vol_prov.provisioner.assign_vldev(ldev.ldevId, ldev.ldevId)

        except Exception as e:
            spec.comments.append(
                f"Exception while adding ldevs to virtual storage {vsm_spec.id}: {str(e)}"
            )
            logger.writeDebug(
                "RC: Exception while adding ldevs to virtual storage {}".format(str(e))
            )
            if vol_prov:
                # Cleanup already created pairs in case of failure
                self._cleanup_ldevs(volume_spec, ldev_ids, vol_prov)
            return False
        return True

    def _get_vsm_details(self, spec):
        if spec.primary_hostgroups:
            hg_prov = VSPHostGroupProvisioner(self.connection_info)
            hgs = [
                hg_prov.get_one_host_group(hg.port, hg.name).data
                for hg in spec.primary_hostgroups
            ]
            if any(hg is None for hg in hgs):
                raise ValueError(
                    f"One or more host groups do not exist: {[hg.name for hg in spec.primary_hostgroups]}"
                )
            rg_ids = set(hg.resourceGroupId for hg in hgs)
            if len(rg_ids) > 1:
                raise ValueError(
                    f"Host groups belong to different virtual storages: {rg_ids}"
                )
            return hgs, rg_ids.pop()
        elif spec.primary_iscsi_targets:
            iscsi_prov = VSPIscsiTargetProvisioner(self.connection_info)
            targets = [
                iscsi_prov.get_one_iscsi_target(target.port, target.name).data
                for target in spec.primary_iscsi_targets
            ]
            if any(target is None for target in targets):
                raise ValueError(
                    f"One or more iSCSI targets do not exist: {[target.name for target in spec.primary_iscsi_targets]}"
                )
            rg_ids = set(target.resourceGroupId for target in targets)
            if len(rg_ids) > 1:
                raise ValueError(
                    f"iSCSI targets belong to different virtual storages: {rg_ids}"
                )
            return targets, rg_ids.pop()
        else:
            nvme_prov = VSPNvmeProvisioner(self.connection_info)
            subsystem = nvme_prov.get_nvme_subsystem_by_name(
                spec.primary_nvm_subsystem.name
            )

            if subsystem is None:
                raise ValueError(
                    f"NVMe subsystem does not exist: {spec.primary_nvm_subsystem.name}"
                )
            return [subsystem], subsystem.resourceGroupId

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
            spec.secondary_hostgroups is None
            and spec.secondary_nvm_subsystem is None
            and spec.secondary_iscsi_targets is None
            and spec.provisioned_secondary_volume_id is None
            and spec.provisioned_secondary_volume_id is None
        ):
            raise ValueError(VSPTrueCopyValidateMsg.SECONDARY_HOSTGROUPS_OR_NVME.value)

        if self.secondary_connection_info is None:
            raise ValueError(VSPTrueCopyValidateMsg.SECONDARY_CONNECTION_INFO.value)
        else:
            spec.secondary_connection_info = self.secondary_connection_info
            spec.remote_connection_info = self.secondary_connection_info

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

        if spec.quorum_disk_id is None:
            raise ValueError(GADPairValidateMSG.QUORUM_DISK_ID.value)

    @log_entry_exit
    def create_update_gad_pair(self, spec, pair, pvol):
        if pair:
            return pair
        return self.provisioner.create_gad_pair(spec, pvol)

    @log_entry_exit
    def delete_gad_pair(self, spec):
        pair = self.provisioner.get_gad_pair_by_copy_group_and_copy_pair_name(spec)
        if pair is None:
            spec.comments = GADPairValidateMSG.GAD_PAIR_DOES_NOT_EXIST.value.format(
                spec.copy_group_name, spec.copy_pair_name
            )
            return "Gad pair not present"

        rsp = self.provisioner.delete_gad_pair(spec, pair)

        if rsp == GADPairValidateMSG.DELETE_GAD_FAIL_SPLIT_DIRECT.value:
            pair = self.provisioner.split_gad_pair(spec, pair)
            rsp = self.provisioner.delete_gad_pair(spec, pair)

        return rsp

    @log_entry_exit
    def split_gad_pair(self, spec, pair):
        self.validate_gad_spec_for_ops(spec)
        return self.provisioner.split_gad_pair(spec, pair)

    @log_entry_exit
    def validate_gad_spec_for_ops(self, spec: Any) -> None:
        # due to swap operations, primary_volume_id is not required,
        # but copy_pair_name is a must
        if spec.copy_pair_name is None:
            raise ValueError(VSPTrueCopyValidateMsg.COPY_PAIR_NAME.value)

    @log_entry_exit
    def resync_gad_pair(self, spec, pair):
        self.validate_gad_spec_for_ops(spec)
        return self.provisioner.resync_gad_pair(spec, pair)

    @log_entry_exit
    def swap_split_gad_pair(self, spec, pair):
        self.validate_gad_spec_for_ops(spec)
        return self.provisioner.swap_split_gad_pair(spec, pair)

    @log_entry_exit
    def swap_resync_gad_pair(self, spec, pair):
        self.validate_gad_spec_for_ops(spec)
        return self.provisioner.swap_resync_gad_pair(spec, pair)

    @log_entry_exit
    def resize_gad_pair(self, spec, pair):
        self.validate_gad_spec_for_ops(spec)
        return self.provisioner.resize_gad_pair(spec)

    def get_gad_copypairs(self, pairs):
        gad_pairs = []
        for pair in pairs:
            logger.writeDebug("RC:get_copypair_one:pair={}", pair)
            copyPairs = pair.get("copyPairs", None)
            if copyPairs is None:
                continue

            for copyPair in copyPairs:
                if (
                    copyPair["replicationType"] == "GAD"
                    and copyPair["svolStatus"] != "SMPL"
                    and copyPair.pvolStatus != "SMPL"
                ):
                    gad_pairs.append(copyPair)

        return gad_pairs

    # sng1104 - filter the copy group copy pairs by GAD
    def get_gad_from_copygroups(self, cgs):
        logger.writeDebug("RC:get_gad_from_copygroups:pair={}", cgs)
        gad_pairs = []
        for cg in cgs:
            logger.writeDebug("RC:cg={}", cg)
            if cg is None:
                continue
            copyPairs = cg.copyPairs
            if copyPairs is None:
                continue

            for copyPair in copyPairs:
                if (
                    copyPair.replicationType == "GAD"
                    and copyPair.svolStatus != "SMPL"
                    and copyPair.pvolStatus != "SMPL"
                ):
                    gad_pairs.append(copyPair.to_dict())

        return gad_pairs

    #  sng20241115 rec.gad_pair_facts
    def gad_pair_facts(self, spec=None):

        # logger.writeDebug("RC:sng20241115 secondary_connection_info={}", spec.secondary_connection_info)
        tc_pairs = self.provisioner.gad_pair_facts(spec)
        logger.writeDebug("RC:224 pairs={}", tc_pairs)
        if tc_pairs:
            # spec.secondary_storage_serial_number
            if hasattr(tc_pairs, "data"):
                # VspGadPairsInfo class
                cglistdict = tc_pairs.data
            else:
                cglistdict = tc_pairs.data_to_list()

            cglistdict = self.objs_to_dict(cglistdict)

            doMore = False
            # logger.writeDebug("RC: 299 spec ={}", spec)
            if spec.copy_group_name and spec.copy_pair_name:
                doMore = True
            logger.writeDebug("RC: 299 doMore ={}", doMore)
            self.get_other_attributes(spec, cglistdict, doMore)

            if len(cglistdict) == 1:
                self.inject_pvol_svol_size(cglistdict[0])
            # logger.writeDebug("RC:cglistdict={}", cglistdict)
            extracted_data = DirectGADCopyPairInfoExtractor(
                self.storage_serial_number
            ).extract(cglistdict)

        else:
            extracted_data = {}
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

            # DirectSpecificCopyGroupInfo?
            obj = obj.to_dict()
            items.append(obj)
        return items

    @log_entry_exit
    # sng20241115 virtual vldevid lookup
    # doSwap=true is only for swap-split
    def get_other_attributes(self, spec, gad_copy_pairs, doMore=True, doSwap=False):

        spec.secondary_storage_serial_number = (
            self.provisioner.get_secondary_serial_direct(spec)
        )
        copy_group_list = self.provisioner.get_copy_group_list()
        logger.writeDebug("RC::copy_group_list={}", copy_group_list)
        logger.writeDebug("RC::gad_copy_pairs={}", gad_copy_pairs)

        if not isinstance(gad_copy_pairs, list):
            gad_copy_pairs = [gad_copy_pairs]

        def process_pair(gad_copy_pair):
            self.get_other_attributes_from_copy_group(
                copy_group_list, gad_copy_pair, doSwap
            )

            gad_copy_pair["isAluaEnabled"] = False
            gad_copy_pair["primaryVirtualVolumeId"] = -1
            gad_copy_pair["secondaryVirtualVolumeId"] = -1

            if not doMore:
                return

            primary_volume_storage_id = get_serial_number_from_device_id(
                gad_copy_pair.get("pvolStorageDeviceId")
            )

            local_do_swap = doSwap
            if spec.secondary_storage_serial_number is not None:
                serial_str = str(spec.secondary_storage_serial_number).strip()
                if serial_str[0].isalpha():
                    serial_str = get_serial_number_from_device_id(serial_str)
                if int(serial_str) == int(primary_volume_storage_id):
                    local_do_swap = True

            pvol = gad_copy_pair["pvolLdevId"]
            svol = gad_copy_pair["svolLdevId"]
            spec.secondary_storage_connection_info = self.secondary_connection_info

            # Fetch primary volume info
            if local_do_swap:
                vol = self.provisioner.get_vol_remote(spec, pvol)
                rg = self.provisioner.get_resource_group_by_id_remote(
                    spec, vol.resourceGroupId
                )
                vsms = self.provisioner.get_vsm_all_remote(spec)
            else:
                vol = self.provisioner.get_volume_by_id(pvol)
                rg = self.provisioner.get_resource_group_by_id(vol.resourceGroupId)
                vsms = self.provisioner.get_vsm_all()

            virtualStorageDeviceId, virtualSerialNumber = self.get_vsm_info(
                vsms, vol.resourceGroupId
            )

            if vol.virtualLdevId:
                gad_copy_pair["primaryVirtualVolumeId"] = vol.virtualLdevId
            if vol.isAluaEnabled:
                gad_copy_pair["isAluaEnabled"] = vol.isAluaEnabled

            gad_copy_pair["primaryVSMResourceGroupName"] = rg.resourceGroupName
            gad_copy_pair["primaryVirtualStorageDeviceId"] = virtualStorageDeviceId
            gad_copy_pair["primaryVirtualSerialNumber"] = virtualSerialNumber

            # Fetch secondary volume info
            if local_do_swap:
                vol = self.provisioner.get_volume_by_id(svol)
                rg = self.provisioner.get_resource_group_by_id(vol.resourceGroupId)
                vsms = self.provisioner.get_vsm_all()
            else:
                vol = self.provisioner.get_vol_remote(spec, svol)
                rg = self.provisioner.get_resource_group_by_id_remote(
                    spec, vol.resourceGroupId
                )
                vsms = self.provisioner.get_vsm_all_remote(spec)

            virtualStorageDeviceId, virtualSerialNumber = self.get_vsm_info(
                vsms, vol.resourceGroupId
            )

            if vol.virtualLdevId:
                gad_copy_pair["secondaryVirtualVolumeId"] = vol.virtualLdevId
            gad_copy_pair["secondaryVSMResourceGroupName"] = rg.resourceGroupName
            gad_copy_pair["secondaryVirtualStorageDeviceId"] = virtualStorageDeviceId
            gad_copy_pair["secondaryVirtualSerialNumber"] = virtualSerialNumber

        if len(gad_copy_pairs) > 1:
            max_workers = min(len(gad_copy_pairs), MAX_WORKER_THREADS)
            executor = ThreadPoolExecutor(
                max_workers=max_workers, thread_name_prefix="ProcessGadPairs"
            )
            try:
                futures = [
                    executor.submit(process_pair, pair) for pair in gad_copy_pairs
                ]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.writeDebug("Error processing pair: {}", str(e))
            except KeyboardInterrupt:
                executor.shutdown(wait=False, cancel_futures=True)
                raise
            finally:
                executor.shutdown(wait=True)
        else:
            for pair in gad_copy_pairs:
                process_pair(pair)

        return

    def get_vsm_info(self, vsms, resourceGroupId):
        # VirtualStorageMachineInfoList
        for vsm in vsms.data:
            for rgid in vsm.resourceGroupIds:
                if rgid == resourceGroupId:
                    return vsm.virtualStorageDeviceId, vsm.virtualSerialNumber

    def get_other_attributes_from_copy_group(self, cglist, gad_copy_pair, doSwap):
        if cglist is None:
            return
        cgname = gad_copy_pair["copyGroupName"]

        logger.writeDebug("sng1104 392 cgname={}", cgname)
        logger.writeDebug("sng1104 392 gad_copy_pair={}", gad_copy_pair)

        for cg in cglist.data:
            if cgname == cg.copyGroupName:
                gad_copy_pair["muNumber"] = cg.muNumber

                if doSwap:

                    # sng20241123 the copy group from swap-split,
                    logger.writeDebug("sng1104 392 cg={}", cg)
                    # do swap
                    gad_copy_pair["localDeviceGroupName"] = cg.remoteDeviceGroupName
                    gad_copy_pair["remoteDeviceGroupName"] = cg.localDeviceGroupName

                else:
                    gad_copy_pair["localDeviceGroupName"] = cg.localDeviceGroupName
                    gad_copy_pair["remoteDeviceGroupName"] = cg.remoteDeviceGroupName

                logger.writeDebug("sng1104 392 gad_copy_pair={}", gad_copy_pair)
                return


class DirectGADCopyPairInfoExtractor:
    def __init__(self, serial):
        self.storage_serial_number = serial
        self.common_properties = {
            "consistencyGroupId": int,
            "copyRate": str,
            "copyPaceTrackSize": str,
            "copyGroupName": str,
            "copyPairName": str,
            "fenceLevel": str,
            "isAluaEnabled": bool,
            "quorumDiskId": int,
            "mirrorUnitId": int,
            "muNumber": int,
            "localDeviceGroupName": str,
            "remoteDeviceGroupName": str,
            "remoteMirrorCopyPairId": str,
            "primaryVirtualSerialNumber": int,
            "primaryVirtualVolumeId": int,
            "primaryVolumeIdHex": str,
            "primaryVSMResourceGroupName": str,
            "primaryVolumeStorageSerialNumber": str,
            "pvolLdevId": int,
            "pvolStatus": str,
            "pvolStorageDeviceId": str,
            "pvolVirtualLdevId": int,
            "secondaryVolumeIdHex": str,
            "secondaryVSMResourceGroupName": str,
            "secondaryVirtualSerialNumber": int,
            "secondaryVolumeStorageSerialNumber": str,
            "secondaryVirtualVolumeId": int,
            "svolLdevId": int,
            "svolStatus": str,
            "svolStorageDeviceId": str,
            "svolVirtualLdevId": int,
        }

        self.parameter_mapping = {
            "pvol_virtual_ldev_id": "primary_virtual_volume_id",
            "svol_virtual_ldev_id": "secondary_virtual_volume_id",
            "mu_number": "mirror_unit_number",
            "pvol_status": "primary_volume_status",
            "svol_status": "secondary_volume_status",
            "pvol_ldev_id": "primary_volume_id",
            "svol_ldev_id": "secondary_volume_id",
        }

    def fix_bad_camel_to_snake_conversion(self, key):
        new_key = key.replace("s_s_w_s", "ssws")
        new_key = key.replace("v_s_m", "vsm")
        return new_key

    @log_entry_exit
    def extract(self, responses):
        new_items = []

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
                if "s_s_w_s" in cased_key or "v_s_m" in cased_key:
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

        if new_dict.get("mirror_unit_id") == "":
            new_dict["mirror_unit_id"] = new_dict.get("mirror_unit_number", -1)

        if new_dict.get("primary_volume_id_hex") == "":
            new_dict["primary_volume_id_hex"] = volume_id_to_hex_format(
                new_dict.get("primary_volume_id")
            )
        if new_dict.get("secondary_volume_id_hex") == "":
            new_dict["secondary_volume_id_hex"] = volume_id_to_hex_format(
                new_dict.get("secondary_volume_id")
            )
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

        if new_dict.get("pvol_storage_device_id"):
            del new_dict["pvol_storage_device_id"]
        if new_dict.get("svol_storage_device_id"):
            del new_dict["svol_storage_device_id"]

        return new_dict

    @log_entry_exit
    def extract_dict(self, response):
        new_dict = {"storage_serial_number": self.storage_serial_number}
        for key, value_type in self.common_properties.items():
            # Get the corresponding key from the response or its mapped key
            response_key = response.get(key)
            # Assign the value based on the response key and its data type
            cased_key = camel_to_snake_case(key)
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
