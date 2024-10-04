from typing import Optional, Any
import time

try:
    from ..common.ansible_common import log_entry_exit
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes, ConnectionTypes
    from ..common.hv_log import Log
    from ..common.hv_log_decorator import LogDecorator
    from ..common.vsp_constants import PairStatus, VolumePayloadConst, DefaultValues
    from ..common.ansible_common import is_pegasus_model
    from ..message.vsp_snapshot_msgs import VSPSnapShotValidateMsg
    from ..model.vsp_volume_models import CreateVolumeSpec
    from ..model.vsp_host_group_models import VSPHostGroupInfo
    from ..model.vsp_snapshot_models import DirectSnapshotInfo, UAIGSnapshotInfo
    from .vsp_volume_prov import VSPVolumeProvisioner
    from .vsp_host_group_provisioner import VSPHostGroupProvisioner
    from ..gateway.vsp_snapshot_gateway import (
        VSPHtiSnapshotDirectGateway,
        VSPHtiSnapshotUaiGateway,
    )
except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes, ConnectionTypes
    from common.hv_log import Log
    from common.hv_log_decorator import LogDecorator
    from common.vsp_constants import PairStatus, VolumePayloadConst, DefaultValues
    from common.ansible_common import is_pegasus_model
    from message.vsp_snapshot_msgs import VSPSnapShotValidateMsg
    from model.vsp_volume_models import CreateVolumeSpec
    from .vsp_volume_prov import VSPVolumeProvisioner
    from .vsp_host_group_provisioner import VSPHostGroupProvisioner
    from common.ansible_common import log_entry_exit
    from model.vsp_host_group_models import VSPHostGroupInfo
    from model.vsp_snapshot_models import DirectSnapshotInfo, UAIGSnapshotInfo
    from gateway.vsp_snapshot_gateway import (
        VSPHtiSnapshotDirectGateway,
        VSPHtiSnapshotUaiGateway,
    )


from typing import Optional, List, Dict, Any


# @LogDecorator.debug_methods
class VSPHtiSnapshotProvisioner:
    def __init__(self, connection_info, serial: str = None):
        self.logger = Log()
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_SNAPSHOT
        )
        self.connection_info = connection_info
        if self.connection_info.connection_type == ConnectionTypes.DIRECT:
            self.vol_provisioner = VSPVolumeProvisioner(self.connection_info)
        if connection_info.connection_type == ConnectionTypes.GATEWAY:
            self.gateway = VSPHtiSnapshotUaiGateway(connection_info)
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
            return resp.data_to_list()

    @log_entry_exit
    def get_one_snapshot(self, pvol: int, mirror_unit_id: int) -> Dict[str, Any]:

        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            snapshots = self.gateway.get_snapshot_by_pvol(pvol)
            # self.logger.writeDebug(f"20240719 snapshots={snapshots}")
            snapshot = [
                ssp for ssp in snapshots.data if ssp.mirrorUnitId == mirror_unit_id
            ]
            if not snapshot:
                msg = f"Snapshot Pair with Primary volume Id {pvol} and Mirror unit Id {mirror_unit_id} is not present"
                self.logger.writeDebug(msg)
                raise Exception(msg)
            # self.logger.writeDebug(f"20240801 expect good poolID here: {snapshot[0]}")
            return snapshot[0]
        else:
            try:
                resp = self.gateway.get_one_snapshot(pvol, mirror_unit_id)
                return resp
            except Exception as e:
                self.logger.writeError(f"An error occurred: {str(e)}")
                if "404" in str(e) or "Specified object does not exist" in str(e):
                    msg = f"Snapshot Pair with Primary volume Id {pvol} and Mirror unit Id {mirror_unit_id} is not present"
                    raise ValueError(msg)
                else:
                    raise ValueError(str(e))

    @log_entry_exit
    def create_snapshot(self, spec) -> Dict[str, Any]:
        if spec.mirror_unit_id:
            ssp = self.get_one_snapshot(spec.pvol, spec.mirror_unit_id)
            if ssp:
                return self.add_remove_svol_to_snapshot(spec, ssp)
            
        if spec.snapshot_group_name is None:
            raise ValueError(VSPSnapShotValidateMsg.SNAPSHOT_GRP_NAME.value)
        
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            return self.create_gateway_snapshot(spec)
        else:
            return self.create_direct_snapshot(spec)

    @log_entry_exit
    def add_remove_svol_to_snapshot(self, spec, ssp) -> Dict[str, Any]:
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
                ## remove the svol from the snapshot first
                self.gateway.unassign_svol_to_snapshot(spec.pvol, spec.mirror_unit_id)
                ## assign the new svol to the snapshot
                self.gateway.assign_svol_to_snapshot(
                    spec.pvol, spec.mirror_unit_id, spec.svol
                )
            else:
                return ssp
        return self.get_one_snapshot(spec.pvol, spec.mirror_unit_id)

    @log_entry_exit
    def create_direct_snapshot(self, spec) -> Dict[str, Any]:
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
            )
        except Exception as e:

            if port:
                self.vol_provisioner.delete_lun_path(port)
            self.vol_provisioner.delete_volume(
                svol_id, spec.is_data_reduction_force_copy
            )

            raise e
        self.logger.writeDebug(f"mirror_unit_id and pvol_id: {result}")
        mu_id = result.split(",")[1]
        ssp = self.get_one_snapshot(spec.pvol, mu_id)
        self.connection_info.changed = True
        return ssp

    @log_entry_exit
    def create_snapshot_svol(self, spec) -> int:
        hg_info = None
        hg_provisioner = VSPHostGroupProvisioner(self.connection_info)

        pvol = self.vol_provisioner.get_volume_by_ldev(spec.pvol)
        if pvol.emulationType == VolumePayloadConst.NOT_DEFINED:
            raise ValueError(VSPSnapShotValidateMsg.PVOL_NOT_FOUND.value)

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
            data_reduction_share=data_reduction_share,
            capacity_saving=capacity_saving,
        )

        svol_id = self.vol_provisioner.create_volume(vol_spec)

        # set the data reduction force copy to true
        spec.is_data_reduction_force_copy = (
            True
            if pvol.dataReductionMode
            and pvol.dataReductionMode != VolumePayloadConst.DISABLED
            else False
        )
        spec.can_cascade = spec.is_data_reduction_force_copy

        if pvol.ports is None and capacity_saving == VolumePayloadConst.DISABLED:
            raise ValueError(VSPSnapShotValidateMsg.PVOL_IS_NOT_IN_HG.value)
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
    def create_gateway_snapshot(self, spec) -> Dict[str, Any]:

        allocate_consistency_group = spec.allocate_consistency_group or False
        enable_quick_mode = spec.enable_quick_mode or False
        consistency_group_id = spec.consistency_group_id or -1
        is_clone = spec.is_clone or False
        dataReductionForceCopy = spec.is_data_reduction_force_copy or False
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
        )
        mirror_unit_id = self.find_mirror_unit_id(result)
        self.logger.writeDebug(f"mirror_unit_id: {mirror_unit_id}")
        ssp = self.get_one_snapshot(spec.pvol, mirror_unit_id)
        # self.logger.writeDebug(f"20240801 after prov.get_one_snapshot, ssp: {ssp}")
        self.connection_info.changed = True
        return ssp

    @log_entry_exit
    def find_mirror_unit_id(self, task_info: Dict[str, Any]) -> int:
        for attribute in task_info.get("data", {}).get("additionalAttributes", []):
            if attribute.get("type") == "mirrorUnitId":
                return int(attribute.get("id"))

        ## if mirror unit ID not found yet,
        ## see if it has gone thru entitlement
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

        raise ValueError("Mirror Unit ID not found in task info")

    @log_entry_exit
    def auto_split_snapshot(self, spec) -> Dict[str, Any]:
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
    def delete_snapshot(self, pvol: int, mirror_unit_id: int) -> Dict[str, Any]:
        try:
            ssp = self.get_one_snapshot(pvol, mirror_unit_id)
        except ValueError as e:
            return str(e)
        result = self.gateway.delete_snapshot(pvol, mirror_unit_id)
        self.connection_info.changed = True
        return

    @log_entry_exit
    def resync_snapshot(
        self, pvol: int, mirror_unit_id: int, enable_quick_mode: bool
    ) -> Dict[str, Any]:
        ssp = self.get_one_snapshot(pvol, mirror_unit_id)
        if ssp.status == PairStatus.PAIR:
            return ssp
        enable_quick_mode = enable_quick_mode or False
        _ = self.gateway.resync_snapshot(pvol, mirror_unit_id, enable_quick_mode)

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
    def clone_snapshot(self, pvol: int, mirror_unit_id: int, svol: int) -> Dict[str, Any]:
        # ssp = self.get_one_snapshot(pvol, mirror_unit_id)
        # if ssp.status == PairStatus.PAIR:
        #     return ssp
        resp_data = self.gateway.clone_snapshot(pvol, mirror_unit_id)
        # self.logger.writeError(f"20240719 resp_data: {resp_data}")
        ssp = f"Snapshot cloned successfully for {pvol} and mirror unit id {mirror_unit_id}"
        self.connection_info.changed = True
        return ssp

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
    def split_snapshots_by_gid(self, spec):
        return self.gateway.split_snapshot_using_ssg(spec.snapshot_group_id)

    @log_entry_exit
    def restore_snapshots_by_gid(self, spec):
        return self.gateway.restore_snapshot_using_ssg(
            spec.snapshot_group_id, spec.auto_split
        )

    @log_entry_exit
    def resync_snapshots_by_gid(self, spec):
        return self.gateway.resync_snapshot_using_ssg(spec.snapshot_group_id)

    @log_entry_exit
    def delete_snapshots_by_gid(self, spec):
        return self.gateway.delete_snapshot_using_ssg(spec.snapshot_group_id)

    @log_entry_exit
    def split_snapshot(
        self, pvol: int, mirror_unit_id: int, enable_quick_mode: bool
    ) -> Dict[str, Any]:

        ssp = self.get_one_snapshot(pvol, mirror_unit_id)

        if ssp.status == PairStatus.PSUS:
            return ssp
        enable_quick_mode = enable_quick_mode or False
        _ = self.gateway.split_snapshot(pvol, mirror_unit_id, enable_quick_mode)

        ## 20240816 - SPLIT: poll every 20 seconds for 10 mins for split status before returning
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
    ) -> Dict[str, Any]:
        ssp = self.get_one_snapshot(pvol, mirror_unit_id)
        if ssp.status == PairStatus.PAIR and auto_split is not True:
            return ssp
        enable_quick_mode = enable_quick_mode or False
        _ = self.gateway.restore_snapshot(
            pvol=pvol,
            mirror_unit_id=mirror_unit_id,
            enable_quick_mode=enable_quick_mode,
            auto_split=auto_split,
        )

        retryCount = 0
        while retryCount < 30:
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
