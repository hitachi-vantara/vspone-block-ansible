from typing import Optional, List, Dict, Any

try:
    from ..common.uaig_constants import Endpoints
    from ..common.hv_constants import CommonConstants
    from ..common.ansible_common import dicts_to_dataclass_list
    from ..common.uaig_utils import UAIGResourceID
    from .gateway_manager import UAIGConnectionManager, VSPConnectionManager
    from ..model.vsp_snapshot_models import (
        DirectSnapshotsInfo,
        DirectSnapshotInfo,
        UAIGSnapshotsInfo,
        UAIGSnapshotInfo,
        SnapshotGroups,
        SnapshotGroupInfo,
    )
    from ..common.hv_log import Log
    from ..common.hv_log_decorator import LogDecorator
    from ..common.vsp_constants import Endpoints as DirectEndPoints
    from ..common.vsp_constants import VSPSnapShotReq, PEGASUS_MODELS
    from ..model.common_base_models import VSPStorageDevice
except ImportError:
    from common.uaig_constants import Endpoints
    from common.hv_constants import CommonConstants
    from common.ansible_common import dicts_to_dataclass_list
    from common.uaig_utils import UAIGResourceID
    from .gateway_manager import UAIGConnectionManager, VSPConnectionManager
    from model.vsp_snapshot_models import (
        DirectSnapshotsInfo,
        DirectSnapshotInfo,
        UAIGSnapshotsInfo,
        UAIGSnapshotInfo,
        SnapshotGroups,
        SnapshotGroupInfo,
    )
    from common.hv_log import Log
    from common.hv_log_decorator import LogDecorator
    from common.vsp_constants import Endpoints as DirectEndPoints
    from common.vsp_constants import VSPSnapShotReq, PEGASUS_MODELS
    from model.common_base_models import VSPStorageDevice


@LogDecorator.debug_methods
class VSPHtiSnapshotDirectGateway:
    def __init__(self, connection_info):
        self.logger = Log()
        self.rest_api = VSPConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )
        self.end_points = DirectEndPoints

    def get_all_snapshots(
        self, pvol: Optional[int] = None, mirror_unit_id: Optional[int] = None
    ) -> DirectSnapshotsInfo:
        storage_info = self.get_storage_details()

        pegasus_model = any(sub in storage_info.model for sub in PEGASUS_MODELS)
        self.logger.writeDebug(f"Storage Model: {storage_info.model}")
        if pegasus_model and not pvol:
            return self._get_pegasus_snapshots()
        else:
            return self._get_all_snapshots_pf_rest(pvol, mirror_unit_id)

    def _get_pegasus_snapshots(self):
        groups = self.rest_api.get(self.end_points.GET_SNAPSHOT_GROUPS)
        snapshots_lists = []
        for grp in groups["data"]:
            snapshots = self.rest_api.get(
                self.end_points.GET_SNAPSHOT_GROUPS_ONE.format(grp["snapshotGroupId"])
            )["snapshots"]
            snapshots_lists.extend(snapshots)

        return DirectSnapshotsInfo(
            dicts_to_dataclass_list(snapshots_lists, DirectSnapshotInfo)
        )

    def _get_all_snapshots_pf_rest(
        self, pvol: Optional[int] = None, mirror_unit_id: Optional[int] = None
    ) -> DirectSnapshotsInfo:
        if pvol and mirror_unit_id:
            object_id = f"pvolLdevId={pvol}&muNumber={mirror_unit_id}"
        elif pvol:
            object_id = f"pvolLdevId={pvol}"
        elif mirror_unit_id:
            object_id = f"muNumber={mirror_unit_id}"
        else:
            object_id = ""

        end_point = (
            self.end_points.GET_SNAPSHOTS_QUERY.format(object_id)
            if object_id
            else self.end_points.ALL_SNAPSHOTS
        )
        snapshots = self.rest_api.get(end_point)
        return DirectSnapshotsInfo(
            dicts_to_dataclass_list(snapshots["data"], DirectSnapshotInfo)
        )

    def get_one_snapshot(self, pvol: int, mirror_unit_id: int) -> DirectSnapshotInfo:
        object_id = f"{pvol},{mirror_unit_id}"
        end_point = self.end_points.GET_ONE_SNAPSHOTS.format(object_id)
        snapshot = self.rest_api.get(end_point)
        return DirectSnapshotInfo(**snapshot)

    def get_snapshot_by_pvol(self, pvol: int) -> DirectSnapshotsInfo:
        query = f"pvolLdevId={pvol}"
        end_point = self.end_points.GET_SNAPSHOTS_QUERY.format(query)
        snapshots = self.rest_api.get(end_point)
        return DirectSnapshotsInfo(
            dicts_to_dataclass_list(snapshots["data"], DirectSnapshotInfo)
        )

    def delete_snapshot(self, pvol: int, mirror_unit_id: int) -> Dict[str, Any]:
        object_id = f"{pvol},{mirror_unit_id}"
        end_point = self.end_points.GET_ONE_SNAPSHOTS.format(object_id)
        return self.rest_api.delete(end_point)

    def split_snapshot(self, pvol: int, mirror_unit_id: int, *args) -> Dict[str, Any]:
        return self._snapshot_action(
            pvol, mirror_unit_id, self.end_points.POST_SNAPSHOTS_SPLIT, data=None
        )

    def clone_snapshot(self, pvol: int, mirror_unit_id: int, *args) -> Dict[str, Any]:
        self.logger.writeDebug("clone_snapshot direct")
        return self._snapshot_action(
            pvol, mirror_unit_id, self.end_points.POST_SNAPSHOTS_CLONE, data=None
        )

    def assign_svol_to_snapshot(
        self, pvol: int, mirror_unit_id: int, svol: int, *args
    ) -> Dict[str, Any]:

        payload = {VSPSnapShotReq.parameters: {VSPSnapShotReq.svolLdevId: svol}}
        return self._snapshot_action(
            pvol, mirror_unit_id, self.end_points.POST_SNAPSHOTS_SVOL_ADD, data=payload
        )

    def unassign_svol_to_snapshot(
        self, pvol: int, mirror_unit_id: int, *args
    ) -> Dict[str, Any]:
        return self._snapshot_action(
            pvol, mirror_unit_id, self.end_points.POST_SNAPSHOTS_SVOL_REMOVE, data=None
        )

    def resync_snapshot(self, pvol: int, mirror_unit_id: int, *args) -> Dict[str, Any]:
        return self._snapshot_action(
            pvol, mirror_unit_id, self.end_points.POST_SNAPSHOTS_RESYNC, data=None
        )

    # Snapshot group related methods
    def get_snapshot_groups(self) -> Dict[str, Any]:
        ssgs = self.rest_api.get(self.end_points.GET_SNAPSHOT_GROUPS)
        return SnapshotGroups().dump_to_object(ssgs)

    def get_snapshots_using_group_id(self, gid):
        ss = self.rest_api.get(self.end_points.SNAPSHOTS_BY_GROUP_ID.format(gid))
        sng_grps = SnapshotGroupInfo(**ss)
        # snapshots=  DirectSnapshotsInfo().dump_to_object({"data": ss["snapshots"]})
        # sng_grps.snapshots = snapshots.data
        return sng_grps

    def split_snapshot_using_ssg(self, group_id: int, *args) -> Dict[str, Any]:
        end_point = self.end_points.SPLIT_SNAPSHOT_BY_GRP.format(group_id)
        return self.rest_api.post(end_point, data=None)

    def restore_snapshot_using_ssg(self, group_id: int, auto_split) -> Dict[str, Any]:
        payload = None
        if auto_split:
            payload = {}
            payload["parameters"] = {"autoSplit": auto_split}

        end_point = self.end_points.RESTORE_SNAPSHOT_BY_GRP.format(group_id)
        return self.rest_api.post(end_point, data=payload)

    def resync_snapshot_using_ssg(self, group_id: int, *args) -> Dict[str, Any]:
        end_point = self.end_points.RESYNC_SNAPSHOT_BY_GRP.format(group_id)
        return self.rest_api.post(end_point, data=None)

    def delete_snapshot_using_ssg(self, group_id: int, *args) -> Dict[str, Any]:
        end_point = self.end_points.SNAPSHOTS_BY_GROUP_ID.format(group_id)
        return self.rest_api.delete(end_point)

    def restore_snapshot(
        self, pvol: int, mirror_unit_id: int, auto_split: bool = False, **args
    ) -> Dict[str, Any]:
        return self._snapshot_action(
            pvol,
            mirror_unit_id,
            self.end_points.POST_SNAPSHOTS_RESTORE,
            auto_split=auto_split,
            data=None,
        )

    def get_storage_details(self) -> VSPStorageDevice:
        end_point = self.end_points.GET_STORAGE_INFO
        storage_info = self.rest_api.get(end_point)
        self.logger.writeDebug(f"Found storage details{storage_info}")
        return VSPStorageDevice(**storage_info)

    def create_snapshot(
        self,
        pvol: int,
        poolId: int,
        allocate_consistency_group: bool,
        snapshot_group_name: str,
        auto_split: bool,
        is_data_reduction_force_copy: bool,
        can_cascade: bool,
        svol: int,
        is_clone: bool,
    ) -> Dict[str, Any]:

        end_point, payload, pegasus_model = self._get_snapshot_payload(
            pvol,
            poolId,
            allocate_consistency_group,
            snapshot_group_name,
            auto_split,
            is_data_reduction_force_copy,
            can_cascade,
            svol,
            is_clone,
        )

        if pegasus_model:
            return self.rest_api.pegasus_post(end_point, payload)

        self.logger.writeDebug(f"Create Snapshot payload: {payload}")
        return self.rest_api.post(end_point, payload)

    def _snapshot_action(
        self,
        pvol: int,
        mirror_unit_id: int,
        end_point_template: str,
        auto_split: bool = False,
        data=None,
    ):
        # payload = None if not auto_split else {"parameters": {"autoSplit": auto_split}}
        object_id = f"{pvol},{mirror_unit_id}"
        end_point = end_point_template.format(object_id)
        return self.rest_api.post(end_point, data)

    def _get_snapshot_payload(
        self,
        pvol: int,
        poolId: int,
        allocate_consistency_group: bool,
        snapshot_group_name: str,
        auto_split: bool,
        is_data_reduction_force_copy: bool,
        can_cascade: bool,
        svol: int,
        is_clone: bool,
    ):

        end_point = self.end_points.SNAPSHOTS
        payload = {
            VSPSnapShotReq.pvolLdevId: pvol,
            VSPSnapShotReq.snapshotPoolId: poolId,
            VSPSnapShotReq.snapshotGroupName: snapshot_group_name,
        }
        # if auto_split is not None:
        #     payload[VSPSnapShotReq.autoSplit] = auto_split

        if is_data_reduction_force_copy:
            payload[VSPSnapShotReq.isDataReductionForceCopy] = (
                is_data_reduction_force_copy
            )

        if can_cascade is not None:
            payload[VSPSnapShotReq.canCascade] = can_cascade
        if svol is not None and svol != -1:
            payload[VSPSnapShotReq.svolLdevId] = svol
        if allocate_consistency_group is not None:
            payload[VSPSnapShotReq.isConsistencyGroup] = allocate_consistency_group
        if is_clone is not None:
            payload[VSPSnapShotReq.isClone] = is_clone
            payload[VSPSnapShotReq.canCascade] = True

        return end_point, payload, False


@LogDecorator.debug_methods
class VSPHtiSnapshotUaiGateway:
    def __init__(self, connection_info):
        self.logger = Log()
        self.rest_api = UAIGConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )
        self.end_points = Endpoints
        self.connectionInfo = connection_info

    def set_storage_serial_number(self, serial: str):
        self.storage_serial_number = serial

    def get_all_snapshots(self) -> UAIGSnapshotsInfo:
        storage_resourceId = UAIGResourceID().storage_resourceId(
            self.storage_serial_number
        )
        end_point = self.end_points.GET_SNAPSHOTS_V3.format(storage_resourceId)
        headers = self._populate_headers()
        snapshots = self.rest_api.get(end_point, headers)
        # self.logger.writeDebug(f"20240719 a: {snapshots["data"][0].get('snapshotPairInfo').get('thinImagePropertiesDto')}")
        info = UAIGSnapshotsInfo(
            dicts_to_dataclass_list(snapshots["data"], UAIGSnapshotInfo)
        )
        return info

    def get_one_snapshot(self, pvol: int, mirror_unit_id: int) -> UAIGSnapshotInfo:
        storage_resourceId = UAIGResourceID().storage_resourceId(
            self.storage_serial_number
        )
        snapshot_resourceId = UAIGResourceID().snapshot_resourceId(
            self.storage_serial_number, pvol, mirror_unit_id
        )
        end_point = self.end_points.GET_SNAPSHOT.format(
            storage_resourceId, snapshot_resourceId
        )
        snapshot = self.rest_api.get(end_point)
        return UAIGSnapshotInfo(**snapshot["data"])

    def get_one_snapshot_by_resourceId(
        self, snapshot_resourceId: str
    ) -> UAIGSnapshotInfo:
        storage_resourceId = UAIGResourceID().storage_resourceId(
            self.storage_serial_number
        )
        end_point = self.end_points.GET_SNAPSHOT.format(
            storage_resourceId, snapshot_resourceId
        )
        snapshot = self.rest_api.get(end_point)
        return UAIGSnapshotInfo(**snapshot["data"])

    def get_snapshot_by_pvol(self, pvol: int) -> UAIGSnapshotsInfo:
        storage_resourceId = UAIGResourceID().storage_resourceId(
            self.storage_serial_number
        )
        end_point = self.end_points.GET_SNAPSHOT_BY_PVOL.format(
            storage_resourceId, pvol
        )
        snapshots = self.rest_api.get(end_point)
        # self.logger.writeDebug(f"20240801 before: {snapshots["data"]}")
        info = UAIGSnapshotsInfo(
            dicts_to_dataclass_list(snapshots["data"], UAIGSnapshotInfo)
        )
        # self.logger.writeDebug(f"20240801 after: {info}")
        return info

    def delete_snapshot(self, pvol: int, mirror_unit_id: int) -> Dict[str, Any]:
        snapshot_resourceId = UAIGResourceID().snapshot_resourceId(
            self.storage_serial_number, pvol, mirror_unit_id
        )
        return self.delete_snapshot_by_resource_id(snapshot_resourceId)

    def delete_snapshot_by_resource_id(
        self, snapshot_resourceId: str
    ) -> Dict[str, Any]:
        storage_resourceId = UAIGResourceID().storage_resourceId(
            self.storage_serial_number
        )
        end_point = self.end_points.DELETE_SNAPSHOT.format(
            storage_resourceId, snapshot_resourceId
        )
        return self.rest_api.delete(end_point)

    def split_snapshot(
        self, pvol: int, mirror_unit_id: int, enable_quick_mode: bool
    ) -> Dict[str, Any]:
        snapshot_resourceId = UAIGResourceID().snapshot_resourceId(
            self.storage_serial_number, pvol, mirror_unit_id
        )
        return self._snapshot_action_by_resource_id(
            snapshot_resourceId, enable_quick_mode, self.end_points.SPLIT_SNAPSHOT
        )

    def resync_snapshot(
        self, pvol: int, mirror_unit_id: int, enable_quick_mode: bool
    ) -> Dict[str, Any]:
        snapshot_resourceId = UAIGResourceID().snapshot_resourceId(
            self.storage_serial_number, pvol, mirror_unit_id
        )
        return self._snapshot_action_by_resource_id(
            snapshot_resourceId, enable_quick_mode, self.end_points.RESYNC_SNAPSHOT
        )

    def clone_snapshot(self, pvol: int, mirror_unit_id: int) -> Dict[str, Any]:
        snapshot_resourceId = UAIGResourceID().snapshot_resourceId(
            self.storage_serial_number, pvol, mirror_unit_id
        )

        # for clone, enable_quick_mode may not be used
        enable_quick_mode = False

        return self._snapshot_action_by_resource_id(
            snapshot_resourceId, enable_quick_mode, self.end_points.CLONE_SNAPSHOT
        )

    def restore_snapshot(
        self, pvol: int, mirror_unit_id: int, enable_quick_mode: bool = False, **args
    ) -> Dict[str, Any]:
        snapshot_resourceId = UAIGResourceID().snapshot_resourceId(
            self.storage_serial_number, pvol, mirror_unit_id
        )
        return self._snapshot_action_by_resource_id(
            snapshot_resourceId, enable_quick_mode, self.end_points.RESTORE_SNAPSHOT
        )

    def create_snapshot(
        self,
        pvol: int,
        poolId: int,
        allocate_consistency_group: bool,
        consistency_group_id: str,
        enable_quick_mode: bool,
        is_clone: bool,
        dataReductionForceCopy: bool,
        snapshotGroupName: str,
        can_cascade: bool,
    ):
        storage_resourceId = UAIGResourceID().storage_resourceId(
            self.storage_serial_number
        )
        end_point = self.end_points.CREATE_SNAPSHOT_V3.format(storage_resourceId)
        payload = {
            "ucpSystem": CommonConstants.UCP_SERIAL,
            "primaryVolumeId": pvol,
            "poolId": poolId,
            "allocateConsistencyGroup": allocate_consistency_group,
            "consistencyGroupId": consistency_group_id,
            "enableQuickMode": enable_quick_mode,
        }

        if snapshotGroupName:
            payload["snapshotGroupName"] = snapshotGroupName

        if dataReductionForceCopy:
            #  TIA
            payload["isDataReductionForceCopy"] = dataReductionForceCopy
            payload["snapshotGroupName"] = snapshotGroupName
            payload["snapMode"] = "CASCADE"

        if is_clone:
            payload["snapMode"] = "CLONE"
        if can_cascade:
            payload["snapMode"] = "CASCADE"
        headers = self._populate_headers()
        self.logger.writeDebug(f"Create Snapshot payload: {payload}")
        return self.rest_api.post(end_point, payload, headers_input=headers)

    def get_ucpsystems(self) -> List[Dict[str, Any]]:
        end_point = self.end_points.GET_UCPSYSTEMS
        ucpsystems = self.rest_api.get(end_point)
        return ucpsystems["data"]

    def check_storage_in_ucpsystem(self) -> bool:
        storage_serial_number = self.storage_serial_number
        ucpsystems = self.get_ucpsystems()

        for u in ucpsystems:
            # if u.get("name") == CommonConstants.UCP_NAME:
            for s in u.get("storageDevices", []):
                if s.get("serialNumber") == storage_serial_number:
                    return s.get("healthState") != CommonConstants.ONBOARDING
        return False

    def _snapshot_action_by_resource_id(
        self, snapshot_resourceId: str, enable_quick_mode: bool, end_point_template: str
    ) -> Dict[str, Any]:
        storage_resourceId = UAIGResourceID().storage_resourceId(
            self.storage_serial_number
        )
        end_point = end_point_template.format(storage_resourceId, snapshot_resourceId)
        payload = {"enableQuickMode": enable_quick_mode}
        return self.rest_api.patch(end_point, payload)

    def _populate_headers(self) -> Dict[str, str]:
        headers = {"partnerId": CommonConstants.PARTNER_ID}
        if self.connectionInfo.subscriber_id is not None:
            headers["subscriberId"] = self.connectionInfo.subscriber_id
        return headers

    def unassign_svol_to_snapshot(self):
        pass

    def assign_svol_to_snapshot(self):
        pass

    def get_snapshot_groups(self):
        pass

    def get_snapshots_using_group_id(self):
        pass

    def split_snapshot_using_ssg(self):
        pass

    def restore_snapshot_using_ssg(self):
        pass

    def resync_snapshot_using_ssg(self):
        pass

    def delete_snapshot_using_ssg(self):
        pass
