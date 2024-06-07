from typing import Optional, Any
from ansible.module_utils.urls import urllib_error

try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes, ConnectionTypes
    from ..common.hv_log import Log
    from ..common.hv_log_decorator import LogDecorator
    from ..common.vsp_constants import PairStatus
except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes, ConnectionTypes
    from common.hv_log import Log
    from common.hv_log_decorator import LogDecorator
    from common.vsp_constants import PairStatus


from typing import Optional, List, Dict, Any


@LogDecorator.debug_methods
class VSPHtiSnapshotProvisioner:
    def __init__(self, connection_info, serial: str):
        self.logger = Log()
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_SNAPSHOT
        )
        self.connection_info = connection_info

        if connection_info.connection_type == ConnectionTypes.GATEWAY:
            self.gateway.set_storage_serial_number(serial)

    def get_snapshot_facts(
        self, pvol: Optional[int] = None, mirror_unit_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            snapshots = self.gateway.get_all_snapshots()
            self.logger.writeDebug(f"snapshots={snapshots}")
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

    def get_one_snapshot(self, pvol: int, mirror_unit_id: int) -> Dict[str, Any]:

        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            snapshots = self.gateway.get_snapshot_by_pvol(pvol)
            self.logger.writeDebug(f"snapshots={snapshots}")
            # TODO: Use v3 api to get all the snapshots and filter using pvol and mu
            snapshot = [
                ssp for ssp in snapshots.data if ssp.mirrorUnitId == mirror_unit_id
            ]
            if not snapshot:
                msg = f"Snapshot Pair with Pvol {pvol} MirrorUnitId {mirror_unit_id} does not exist"
                self.logger.writeDebug(msg)
                raise Exception(msg)
            return snapshot[0].to_dict()
        else:
            try:
                resp = self.gateway.get_one_snapshot(pvol, mirror_unit_id)
                return resp.to_dict()
            except Exception as e:
                self.logger.writeError(f"An error occurred: {str(e)}")
                if "404" in str(e):
                    msg = f"given snapshot not found for pvol={pvol} and mirror_unit_id={mirror_unit_id}"
                    raise ValueError(msg)

    def create_snapshot(self, spec) -> Dict[str, Any]:
        if spec.mirror_unit_id:
            ssp = self.get_one_snapshot(spec.pvol, spec.mirror_unit_id)
            if ssp:
                return ssp
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            return self.create_gateway_snapshot(spec)
        else:
            return self.create_direct_snapshot(spec)

    def create_direct_snapshot(self, spec) -> Dict[str, Any]:

        allocate_consistency_group = spec.allocate_consistency_group or False
        result = self.gateway.create_snapshot(
            spec.pvol,
            spec.pool_id,
            allocate_consistency_group,
            spec.snapshot_group_name,
            spec.auto_split,
        )
        self.logger.writeDebug(f"mirror_unit_id and pvol_id: {result}")
        mu_id = result.split(",")[1]
        ssp = self.get_one_snapshot(spec.pvol, mu_id)
        self.connection_info.changed = True
        return ssp

    def create_gateway_snapshot(self, spec) -> Dict[str, Any]:

        allocate_consistency_group = spec.allocate_consistency_group or False
        enable_quick_mode = spec.enable_quick_mode or False
        consistency_group_id = spec.consistency_group_id or -1
        result = self.gateway.create_snapshot(
            spec.pvol,
            spec.pool_id,
            allocate_consistency_group,
            consistency_group_id,
            enable_quick_mode,
        )
        mirror_unit_id = self.find_mirror_unit_id(result)
        self.logger.writeDebug(f"mirror_unit_id: {mirror_unit_id}")
        ssp = self.get_one_snapshot(spec.pvol, mirror_unit_id)
        self.connection_info.changed = True
        return ssp

    def find_mirror_unit_id(self, task_info: Dict[str, Any]) -> int:
        for attribute in task_info.get("data", {}).get("additionalAttributes", []):
            if attribute.get("type") == "mirrorUnitId":
                return int(attribute.get("id"))
        raise ValueError("Mirror Unit ID not found in task info")

    def auto_split_snapshot(self, spec) -> Dict[str, Any]:
        ssp = self.create_snapshot(spec)
        mirror_unit_id = (
            ssp.get("mirrorUnitId") if ssp.get("mirrorUnitId") else ssp.get("muNumber")
        )
        enable_quick_mode = spec.enable_quick_mode or False
        resp = self.split_snapshot(spec.pvol, mirror_unit_id, enable_quick_mode)
        self.connection_info.changed = True
        return resp

    def delete_snapshot(self, pvol: int, mirror_unit_id: int) -> Dict[str, Any]:
        ssp = self.get_one_snapshot(pvol, mirror_unit_id)
        result = self.gateway.delete_snapshot(pvol, mirror_unit_id)
        self.connection_info.changed = True
        return result

    def resync_snapshot(
        self, pvol: int, mirror_unit_id: int, enable_quick_mode: bool
    ) -> Dict[str, Any]:
        ssp = self.get_one_snapshot(pvol, mirror_unit_id)
        if ssp.get("status") == PairStatus.PAIR:
            return ssp
        enable_quick_mode = enable_quick_mode or False
        _ = self.gateway.resync_snapshot(pvol, mirror_unit_id, enable_quick_mode)
        ssp = self.get_one_snapshot(pvol, mirror_unit_id)
        self.connection_info.changed = True
        return ssp

    def split_snapshot(
        self, pvol: int, mirror_unit_id: int, enable_quick_mode: bool
    ) -> Dict[str, Any]:

        ssp = self.get_one_snapshot(pvol, mirror_unit_id)
        if ssp.get("status") == PairStatus.PSUS:
            return ssp
        enable_quick_mode = enable_quick_mode or False
        _ = self.gateway.split_snapshot(pvol, mirror_unit_id, enable_quick_mode)
        ssp = self.get_one_snapshot(pvol, mirror_unit_id)
        self.connection_info.changed = True
        return ssp

    def restore_snapshot(
        self, pvol: int, mirror_unit_id: int, enable_quick_mode: bool, auto_split: bool
    ) -> Dict[str, Any]:
        ssp = self.get_one_snapshot(pvol, mirror_unit_id)
        if ssp.get("status") == PairStatus.PAIR:
            return ssp
        enable_quick_mode = enable_quick_mode or False
        _ = self.gateway.restore_snapshot(
            pvol=pvol,
            mirror_unit_id=mirror_unit_id,
            enable_quick_mode=enable_quick_mode,
            auto_split=auto_split,
        )
        ssp = self.get_one_snapshot(pvol, mirror_unit_id)
        self.connection_info.changed = True
        return ssp

    def check_storage_in_ucpsystem(self) -> bool:
        return self.gateway.check_storage_in_ucpsystem()
