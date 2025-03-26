from typing import Optional, Any
import time
from typing import List, Dict

try:
    from ..common.ansible_common import log_entry_exit
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes, ConnectionTypes
    from ..common.hv_log import Log
    from ..common.vsp_constants import (
        PairStatus,
        VolumePayloadConst,
        DEFAULT_NAME_PREFIX,
    )
    from ..message.vsp_snapshot_msgs import VSPSnapShotValidateMsg
    from ..model.vsp_volume_models import CreateVolumeSpec
    from ..model.vsp_host_group_models import VSPHostGroupInfo
    from .vsp_nvme_provisioner import VSPNvmeProvisioner
    from ..model.vsp_snapshot_models import (
        DirectSnapshotsInfo,
        DirectSnapshotInfo,
        UAIGSnapshotInfo,
    )
    from .vsp_volume_prov import VSPVolumeProvisioner
    from .vsp_host_group_provisioner import VSPHostGroupProvisioner
    from ..common.uaig_utils import UAIGResourceID
    from ..gateway.vsp_snapshot_gateway import (
        VSPHtiSnapshotUaiGateway,
    )
    from ..gateway.vsp_volume import VSPVolumeUAIGateway
except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes, ConnectionTypes
    from common.hv_log import Log
    from common.vsp_constants import PairStatus, VolumePayloadConst, DEFAULT_NAME_PREFIX
    from common.uaig_utils import UAIGResourceID
    from message.vsp_snapshot_msgs import VSPSnapShotValidateMsg
    from model.vsp_volume_models import CreateVolumeSpec
    from .vsp_volume_prov import VSPVolumeProvisioner
    from .vsp_host_group_provisioner import VSPHostGroupProvisioner
    from .vsp_nvme_provisioner import VSPNvmeProvisioner
    from common.ansible_common import log_entry_exit
    from model.vsp_host_group_models import VSPHostGroupInfo
    from model.vsp_snapshot_models import (
        DirectSnapshotsInfo,
        DirectSnapshotInfo,
        UAIGSnapshotInfo,
    )
    from gateway.vsp_snapshot_gateway import (
        VSPHtiSnapshotUaiGateway,
    )
    from gateway.vsp_volume import VSPVolumeUAIGateway


# @LogDecorator.debug_methods
class VSPHtiSnapshotProvisioner:
    def __init__(self, connection_info, serial=None):
        self.logger = Log()
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_SNAPSHOT
        )
        self.connection_info = connection_info
        self.config_gw = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_CONFIG_MAP
        )
        self.vol_provisioner = VSPVolumeProvisioner(self.connection_info)
        if connection_info.connection_type == ConnectionTypes.GATEWAY:
            self.gateway = VSPHtiSnapshotUaiGateway(connection_info)
            self.serial_number = serial
            self.gateway.set_storage_serial_number(serial)

    @log_entry_exit
    def get_snapshot_facts(
        self, pvol: Optional[int] = None, mirror_unit_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            snapshots = self.gateway.get_all_snapshots()
            if pvol is not None:
                filtered_snapshots = [
                    ssp.to_dict()
                    for ssp in snapshots.data
                    if ssp.primaryVolumeId == pvol
                    and (mirror_unit_id is None or ssp.mirrorUnitId == mirror_unit_id)
                ]
                self.logger.writeDebug(f"filtered_snapshots={filtered_snapshots}")
                return filtered_snapshots
            return snapshots.data_to_list()
        else:
            resp = self.gateway.get_all_snapshots(pvol, mirror_unit_id)
            new_resp = self.fill_nvm_subsystem_info_for_snapshots(resp.data)
            return new_resp.data_to_list()

    @log_entry_exit
    def get_one_snapshot(self, pvol: int, mirror_unit_id: int):

        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            snapshots = self.gateway.get_snapshot_by_pvol(pvol)
            snapshot = [
                ssp for ssp in snapshots.data if ssp.mirrorUnitId == mirror_unit_id
            ]
            if not snapshot:
                msg = f"Snapshot Pair with Primary volume Id {pvol} and Mirror unit Id {mirror_unit_id} is not present"
                self.logger.writeError(msg)
                raise Exception(msg)

            return snapshot[0]
        else:
            try:
                resp = self.gateway.get_one_snapshot(pvol, mirror_unit_id)
                return self.fill_nvm_subsystem_info_for_one_snapshot(resp)
            except Exception as e:
                self.logger.writeError(f"An error occurred: {str(e)}")
                if "404" in str(e) or "Specified object does not exist" in str(e):
                    msg = f"Snapshot Pair with Primary volume Id {pvol} and Mirror unit Id {mirror_unit_id} is not present"
                    raise ValueError(msg)
                else:
                    raise ValueError(str(e))

    @log_entry_exit
    def fill_nvm_subsystem_info_for_snapshots(self, snapshots):
        self.logger.writeDebug(
            f"fill_nvm_subsystem_info_for_snapshots:snapshots= {snapshots}"
        )
        new_snapshots = []
        for sn in snapshots:
            new_sn = self.fill_nvm_subsystem_info_for_one_snapshot(sn)
            new_snapshots.append(new_sn)
        return DirectSnapshotsInfo(data=new_snapshots)

    @log_entry_exit
    def fill_nvm_subsystem_info_for_one_snapshot(self, snapshot):
        self.logger.writeDebug(
            f"fill_nvm_subsystem_info_for_one_snapshot:shadow_image_pair= {snapshot}"
        )
        pvol = snapshot.pvolLdevId
        svol = snapshot.svolLdevId
        if pvol:
            snapshot.pvolNvmSubsystemName = self.nvm_subsystem_name_for_ldev_id(pvol)
        if svol:
            snapshot.svolNvmSubsystemName = self.nvm_subsystem_name_for_ldev_id(svol)

        return snapshot

    @log_entry_exit
    def nvm_subsystem_name_for_ldev_id(self, ldev_id):
        volume = self.vol_provisioner.get_volume_by_ldev(ldev_id)
        if volume.nvmSubsystemId:
            nvm_subsystem_name = self.get_nvm_subsystem_name(volume)
            self.logger.writeDebug(
                "PROV:nvm_subsystem_name_for_ldev_id:nvm_subsystem_name = {}",
                nvm_subsystem_name,
            )
            return nvm_subsystem_name
        else:
            return None

    @log_entry_exit
    def get_nvm_subsystem_name(self, volume):
        nvm_provisioner = VSPNvmeProvisioner(self.connection_info)
        nvm_ss = nvm_provisioner.get_nvme_subsystem_by_id(volume.nvmSubsystemId)
        self.logger.writeDebug("PROV:get_nvm_subsystem_info:nvm_subsystem = {}", nvm_ss)

        return nvm_ss.nvmSubsystemName

    @log_entry_exit
    def create_snapshot(self, spec):
        if spec.mirror_unit_id:
            ssp = self.get_one_snapshot(spec.pvol, spec.mirror_unit_id)
            if ssp:
                return self.add_remove_svol_to_snapshot(spec, ssp)

        if spec.snapshot_group_name is None:
            err_msg = VSPSnapShotValidateMsg.SNAPSHOT_GRP_NAME.value
            self.logger.writeError(err_msg)
            raise ValueError(err_msg)

        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            return self.create_gateway_snapshot(spec)
        else:
            return self.create_direct_snapshot(spec)

    @log_entry_exit
    def add_remove_svol_to_snapshot(self, spec, ssp):
        if self.connection_info.connection_type == ConnectionTypes.DIRECT:
            if spec.svol is not None and spec.svol == -1 and ssp.svolLdevId is not None:
                self.gateway.unassign_svol_to_snapshot(spec.pvol, spec.mirror_unit_id)
            elif spec.svol is not None and spec.svol >= 0 and ssp.svolLdevId is None:
                self.gateway.assign_svol_to_snapshot(
                    spec.pvol, spec.mirror_unit_id, spec.svol
                )
            elif (
                ssp.svolLdevId is not None
                and spec.svol is not None
                and spec.svol != ssp.svolLdevId
            ):
                #  remove the svol from the snapshot first
                self.gateway.unassign_svol_to_snapshot(spec.pvol, spec.mirror_unit_id)
                #  assign the new svol to the snapshot
                self.gateway.assign_svol_to_snapshot(
                    spec.pvol, spec.mirror_unit_id, spec.svol
                )
            else:
                return ssp
        else:
            pass
        return self.get_one_snapshot(spec.pvol, spec.mirror_unit_id)

    @log_entry_exit
    def create_direct_snapshot(self, spec):
        svol_id, port = self.create_snapshot_svol(spec)
        try:
            result = self.gateway.create_snapshot(
                spec.pvol,
                spec.pool_id,
                spec.allocate_consistency_group,
                spec.snapshot_group_name,
                spec.auto_split,
                spec.is_data_reduction_force_copy,
                spec.can_cascade,
                svol_id,
                spec.is_clone,
            )
        except Exception as e:

            if port:
                self.vol_provisioner.delete_lun_path(port)
            self.vol_provisioner.delete_volume(
                svol_id, spec.is_data_reduction_force_copy
            )
            self.logger.writeException(e)
            raise e
        self.logger.writeDebug(f"mirror_unit_id and pvol_id: {result}")
        mu_id = result.split(",")[1]
        ssp = self.get_one_snapshot(spec.pvol, mu_id)
        self.connection_info.changed = True
        return ssp

    @log_entry_exit
    def create_snapshot_svol(self, spec):
        hg_info = None
        hg_provisioner = VSPHostGroupProvisioner(self.connection_info)

        pvol = self.vol_provisioner.get_volume_by_ldev(spec.pvol)
        if pvol.emulationType == VolumePayloadConst.NOT_DEFINED:
            err_msg = VSPSnapShotValidateMsg.PVOL_NOT_FOUND.value
            self.logger.writeError(err_msg)
            raise ValueError(err_msg)

        # Check if vvol or normal lun is required to create
        pool_id = (
            pvol.poolId
            if pvol.dataReductionMode
            and pvol.dataReductionMode != VolumePayloadConst.DISABLED
            else -1
        )
        capacity_saving = (
            pvol.dataReductionMode
            if pvol.dataReductionMode
            and pvol.dataReductionMode != VolumePayloadConst.DISABLED
            else VolumePayloadConst.DISABLED
        )
        data_reduction_share = (
            pvol.isDataReductionShareEnabled
            if pvol.isDataReductionShareEnabled
            else False
        )

        vol_spec = CreateVolumeSpec(
            pool_id=pool_id,
            size=pvol.byteFormatCapacity.replace(" ", "").replace(".00", ""),
            block_size=pvol.blockCapacity,
            data_reduction_share=data_reduction_share,
            capacity_saving=capacity_saving,
        )

        svol_id = self.vol_provisioner.create_volume(vol_spec)

        if pvol.label is not None and pvol.label != "":
            svol_name = pvol.label
        else:
            svol_name = f"{DEFAULT_NAME_PREFIX}-{pvol.ldevId}"
        self.vol_provisioner.change_volume_settings(svol_id, name=svol_name)

        # set the data reduction force copy to true
        spec.is_data_reduction_force_copy = (
            True
            if pvol.dataReductionMode
            and pvol.dataReductionMode != VolumePayloadConst.DISABLED
            and spec.is_data_reduction_force_copy is None
            else spec.is_data_reduction_force_copy
        )
        spec.can_cascade = (
            spec.is_data_reduction_force_copy
            if spec.can_cascade is None
            else spec.can_cascade
        )
        if pvol.nvmSubsystemId:
            ns_id = self.create_name_space_for_svol(pvol.nvmSubsystemId, svol_id)
        else:
            if pvol.ports is None and capacity_saving == VolumePayloadConst.DISABLED:
                err_msg = VSPSnapShotValidateMsg.PVOL_IS_NOT_IN_HG.value
                self.logger.writeError(err_msg)
                raise ValueError(err_msg)

            elif pvol.ports is not None and len(pvol.ports) > 0:

                hg_info = pvol.ports[0]
                hg = VSPHostGroupInfo(
                    port=hg_info["portId"], hostGroupId=hg_info["hostGroupNumber"]
                )

                hg_provisioner.add_luns_to_host_group(hg, luns=[svol_id])
                svol = self.vol_provisioner.get_volume_by_ldev(svol_id)
                if svol.ports:
                    hg_info = svol.ports[0]
            # Assign the svol and pvol to the host group

        return svol_id, hg_info

    @log_entry_exit
    def create_name_space_for_svol(self, nvm_subsystem_id, ldev_id):
        nvm_provisioner = VSPNvmeProvisioner(self.connection_info)
        return nvm_provisioner.create_namespace(nvm_subsystem_id, ldev_id)

    @log_entry_exit
    def create_gateway_snapshot(self, spec):

        storage_id = UAIGResourceID().storage_resourceId(self.serial_number)
        ldev_resource_id = UAIGResourceID().ldev_resourceId(
            self.serial_number, spec.pvol
        )
        try:
            pvol = self.vol_provisioner.get_volume_by_ldev_uaig(
                storage_id, ldev_resource_id
            )
        except Exception as e:
            self.logger.writeException(e)
            raise e  # ValueError(VSPSnapShotValidateMsg.PVOL_NOT_FOUND.value)

        allocate_consistency_group = spec.allocate_consistency_group or False
        enable_quick_mode = spec.enable_quick_mode or False
        consistency_group_id = spec.consistency_group_id or -1
        is_clone = spec.is_clone or False
        dataReductionForceCopy = spec.is_data_reduction_force_copy or pvol.isDRS
        can_cascade = spec.can_cascade or dataReductionForceCopy

        snapshotGroupName = spec.snapshot_group_name or ""
        self.logger.writeDebug(f"dataReductionForceCopy: {dataReductionForceCopy}")
        result = self.gateway.create_snapshot(
            spec.pvol,
            spec.pool_id,
            allocate_consistency_group,
            consistency_group_id,
            enable_quick_mode,
            is_clone,
            dataReductionForceCopy,
            snapshotGroupName,
            can_cascade,
        )
        mirror_unit_id = self.find_mirror_unit_id(result)
        self.logger.writeDebug(f"mirror_unit_id: {mirror_unit_id}")
        ssp = self.get_one_snapshot(spec.pvol, mirror_unit_id)
        # self.logger.writeDebug(f"20240801 after prov.get_one_snapshot, ssp: {ssp}")

        self.change_svol_name(pvol, ssp.secondaryVolumeId)

        self.connection_info.changed = True
        return ssp

    @log_entry_exit
    def change_svol_name(self, pvol, svol_id):
        vol_gateway = VSPVolumeUAIGateway(self.connection_info)
        storage_resourceId = UAIGResourceID().storage_resourceId(self.serial_number)
        ldev_resourceId = UAIGResourceID().ldev_resourceId(self.serial_number, svol_id)
        if pvol.name is not None and pvol.name != "":
            svol_name = pvol.name
        else:
            svol_name = f"{DEFAULT_NAME_PREFIX}-{pvol.ldevId}"

        response = vol_gateway.update_volume(
            storage_resourceId, ldev_resourceId, lu_name=svol_name
        )
        return response

    @log_entry_exit
    def find_mirror_unit_id(self, task_info: Dict[str, Any]) -> int:
        for attribute in task_info.get("data", {}).get("additionalAttributes", []):
            if attribute.get("type") == "mirrorUnitId":
                return int(attribute.get("id"))

        #  if mirror unit ID not found yet,
        #  see if it has gone thru entitlement
        return self.get_mirror_unit_id_tagged(task_info)

    @log_entry_exit
    def get_mirror_unit_id_tagged(self, task_response: Dict[str, Any]) -> int:
        self.logger.writeDebug(f"task_response: {task_response}")
        task_events = task_response["data"].get("events")
        if len(task_events):
            snapshot_resourceId = None
            for element in task_events:
                description = element.get("description", "")
                if "Successfully tagged snapshotpair" in description:
                    ss = description.split(" ")
                    snapshot_resourceId = ss[3]
                    break

            if snapshot_resourceId:
                self.logger.writeDebug(f"snapshot_resourceId: {snapshot_resourceId}")
                data = self.gateway.get_one_snapshot_by_resourceId(snapshot_resourceId)
                return int(data.mirrorUnitId)

        err_msg = VSPSnapShotValidateMsg.MIRROR_UNIT_ID_NOT_FOUND.value
        self.logger.writeError(err_msg)
        raise ValueError(err_msg)

    @log_entry_exit
    def auto_split_snapshot(self, spec):
        spec.auto_split = True
        ssp = self.create_snapshot(spec)
        mirror_unit_id = (
            ssp.mirrorUnitId if isinstance(ssp, UAIGSnapshotInfo) else ssp.muNumber
        )
        enable_quick_mode = spec.enable_quick_mode or False
        resp = self.split_snapshot(spec.pvol, mirror_unit_id, enable_quick_mode)
        self.connection_info.changed = True
        return resp

    @log_entry_exit
    def delete_snapshot(self, pvol: int, mirror_unit_id: int):
        try:
            self.get_one_snapshot(pvol, mirror_unit_id)
        except ValueError as e:
            return str(e)
        self.gateway.delete_snapshot(pvol, mirror_unit_id)
        self.connection_info.changed = True
        return

    @log_entry_exit
    def resync_snapshot(self, pvol: int, mirror_unit_id: int, enable_quick_mode: bool):
        ssp = self.get_one_snapshot(pvol, mirror_unit_id)
        if ssp.status == PairStatus.PAIR:
            return ssp
        enable_quick_mode = enable_quick_mode or False
        unused = self.gateway.resync_snapshot(pvol, mirror_unit_id, enable_quick_mode)

        retryCount = 0
        while retryCount < 30:
            ssp = self.get_one_snapshot(pvol, mirror_unit_id)
            if ssp.status == PairStatus.PAIR:
                break
            retryCount = retryCount + 1
            self.logger.writeDebug(f"Polling for resync status: {retryCount}")
            time.sleep(20)

        self.connection_info.changed = True
        return ssp

    @log_entry_exit
    def clone_snapshot(self, pvol: int, mirror_unit_id: int, svol: int):

        ssp = self.get_one_snapshot(pvol, mirror_unit_id)
        svol = (
            ssp.svolLdevId
            if isinstance(ssp, DirectSnapshotInfo)
            else ssp.secondaryVolumeId
        )
        unused = self.gateway.clone_snapshot(pvol, mirror_unit_id)
        ssp = f"Snapshot cloned successfully to secondary volume {svol}"
        self.connection_info.changed = True
        return ssp

    @log_entry_exit
    def get_snapshot_groups(self):
        return self.gateway.get_snapshot_groups()

    @log_entry_exit
    def get_snapshots_by_grp_name(self, grp_name):
        sgs = self.gateway.get_snapshot_groups()
        for sg in sgs.data:
            if sg.snapshotGroupName == grp_name:
                return self.get_snapshots_by_gid(sg.snapshotGroupId)

    @log_entry_exit
    def get_snapshots_by_gid(self, gid):
        return self.gateway.get_snapshots_using_group_id(gid)

    @log_entry_exit
    def get_snapshot_grp_by_name(self, grp_name):
        sgs = self.gateway.get_snapshot_groups()
        for sg in sgs.data:
            if sg.snapshotGroupName == grp_name:
                return sg

    @log_entry_exit
    def split_snapshots_by_gid(self, spec, first_snapshot):
        if first_snapshot.status == PairStatus.PSUS:
            # UCA-2602 for the case where the snapshot is already in PAIR status, do nothing, removed the check
            pass
        try:
            data = self.gateway.split_snapshot_using_ssg(spec.snapshot_group_id)
        except Exception as e:
            self.logger.writeError(f"An error occurred: {str(e)}")
            if "KART30000-E" in str(e) or "The command ended abnormally" in str(e):
                msg = (
                    f"Split Snapshot Pairs with Snapshot Group Id {spec.snapshot_group_id} failed ",
                    "Check if the snapshot group created in CTG mode or snapshot group contains two or more pairs that have the same volume as the P-VOL.",
                )
                error = {"msg": str(e), "cause": msg}
                raise ValueError(str(error))
            else:
                raise e
        self.connection_info.changed = True
        return data

    @log_entry_exit
    def restore_snapshots_by_gid(self, spec, first_snapshot):

        if first_snapshot.status == PairStatus.PAIR:
            # UCA-2602 for the case where the snapshot is already in PAIR status, do nothing, removed the check
            pass
        data = self.gateway.restore_snapshot_using_ssg(
            spec.snapshot_group_id, spec.auto_split
        )
        self.connection_info.changed = True
        return data

    @log_entry_exit
    def resync_snapshots_by_gid(self, spec, first_snapshot):

        if first_snapshot.status == PairStatus.PAIR:
            # UCA-2602 for the case where the snapshot is already in PAIR status, do nothing, removed the check
            pass
        data = self.gateway.resync_snapshot_using_ssg(spec.snapshot_group_id)
        self.connection_info.changed = True
        return data

    @log_entry_exit
    def delete_snapshots_by_gid(self, spec, *args):
        data = self.gateway.delete_snapshot_using_ssg(spec.snapshot_group_id)
        self.connection_info.changed = True
        return data

    @log_entry_exit
    def split_snapshot(self, pvol: int, mirror_unit_id: int, enable_quick_mode: bool):

        ssp = self.get_one_snapshot(pvol, mirror_unit_id)

        if ssp.status == PairStatus.PSUS:
            return ssp
        enable_quick_mode = enable_quick_mode or False
        unused = self.gateway.split_snapshot(pvol, mirror_unit_id, enable_quick_mode)

        #  20240816 - SPLIT: poll every 20 seconds for 10 mins for split status before returning
        retryCount = 0
        while retryCount < 30:
            ssp = self.get_one_snapshot(pvol, mirror_unit_id)
            if ssp.status == PairStatus.PSUS:
                break
            retryCount = retryCount + 1
            self.logger.writeDebug(f"Polling for split status: {retryCount}")
            time.sleep(20)

        self.connection_info.changed = True
        return ssp

    @log_entry_exit
    def restore_snapshot(
        self, pvol: int, mirror_unit_id: int, enable_quick_mode: bool, auto_split: bool
    ):
        ssp = self.get_one_snapshot(pvol, mirror_unit_id)
        if ssp.status == PairStatus.PAIR and auto_split is not True:
            return ssp
        enable_quick_mode = enable_quick_mode or False
        unused = self.gateway.restore_snapshot(
            pvol=pvol,
            mirror_unit_id=mirror_unit_id,
            enable_quick_mode=enable_quick_mode,
            auto_split=auto_split,
        )

        retryCount = 0
        while retryCount < 3:
            ssp = self.get_one_snapshot(pvol, mirror_unit_id)
            if ssp.status == PairStatus.PAIR:
                break
            retryCount = retryCount + 1
            self.logger.writeDebug(f"Polling for restore status: {retryCount}")
            time.sleep(20)

        self.connection_info.changed = True
        return ssp

    @log_entry_exit
    def check_storage_in_ucpsystem(self) -> bool:
        return self.gateway.check_storage_in_ucpsystem()

    @log_entry_exit
    def is_out_of_band(self):
        return self.config_gw.is_out_of_band()
