from typing import Any

try:
    from ..provisioner.vsp_snapshot_provisioner import VSPHtiSnapshotProvisioner
    from ..provisioner.vsp_snapshot_family_provisioner import (
        VSPSnapshotFamilyProvisioner,
    )
    from ..provisioner.vsp_storage_port_provisioner import VSPStoragePortProvisioner
    from ..gateway.vsp_storage_system_gateway import VSPStorageSystemDirectGateway
    from ..common.ansible_common import (
        camel_to_snake_case,
        volume_id_to_hex_format,
        get_default_value,
    )
    from ..common.hv_log import Log
    from ..common.hv_log_decorator import LogDecorator
    from ..common.hv_constants import StateValue
    from ..message.vsp_snapshot_msgs import VSPSnapShotValidateMsg
    from ..message.vsp_vclone_msgs import VSPVcloneValidateMsg
    from ..model.vsp_snapshot_models import SnapshotGroupFactSpec
except ImportError:
    from provisioner.vsp_snapshot_provisioner import VSPHtiSnapshotProvisioner
    from ..provisioner.vsp_snapshot_family_provisioner import (
        VSPSnapshotFamilyProvisioner,
    )
    from provisioner.vsp_storage_port_provisioner import VSPStoragePortProvisioner
    from gateway.vsp_storage_system_gateway import VSPStorageSystemDirectGateway
    from common.ansible_common import (
        camel_to_snake_case,
        volume_id_to_hex_format,
        get_default_value,
    )
    from common.hv_log import Log
    from common.hv_log_decorator import LogDecorator
    from common.hv_constants import StateValue
    from message.vsp_snapshot_msgs import VSPSnapShotValidateMsg
    from message.vsp_vclone_msgs import VSPVcloneValidateMsg
    from model.vsp_snapshot_models import SnapshotGroupFactSpec


@LogDecorator.debug_methods
class VSPHtiSnapshotReconciler:
    def __init__(
        self,
        connectionInfo: Any,
        serial=None,
        snapshotSpec=None,
    ):
        """
        Initialize the snapshot reconciler with connection info, storage serial number, and optional snapshot spec.
        """
        self.logger = Log()
        self.connectionInfo = connectionInfo
        self.storage_serial_number = serial
        if self.storage_serial_number is None:
            self.storage_serial_number = self.get_storage_serial_number()
        self.snapshotSpec = snapshotSpec
        self.provisioner = VSPHtiSnapshotProvisioner(self.connectionInfo, serial)
        self.port_provisioner = VSPStoragePortProvisioner(connectionInfo)
        self.sn_family_prov = VSPSnapshotFamilyProvisioner(
            self.connectionInfo, self.storage_serial_number
        )
        self.port_type_dict = {}
        self.get_port_type_dict()

    def get_port_type_dict(self):
        port_info = self.port_provisioner.get_all_storage_ports().data_to_list()
        # self.logger.writeDebug(f"20250324 port_info: {port_info}")
        for port in port_info:
            self.port_type_dict[port["portId"]] = port["portType"]
        # self.logger.writeDebug(f"20250324 self.port_type_dict: {self.port_type_dict}")

    def get_snapshot_facts(self, spec: Any) -> Any:
        """
        Retrieve snapshot facts based on the provided specification.
        """
        result = None
        if isinstance(spec, SnapshotGroupFactSpec):
            if spec.snapshot_group_name is None:
                self.logger.writeDebug(f"20250324 spec: {spec}")
                return self.get_all_snapshot_groups()
            else:
                self.logger.writeDebug(f"20250324 spec: {spec}")
                return self.get_snapshots_using_grp_name(spec.snapshot_group_name)
        else:
            self.logger.writeDebug(f"20250324 spec: {spec}")
            result = self.provisioner.get_snapshot_facts(
                pvol=spec.pvol, mirror_unit_id=spec.mirror_unit_id
            )
            self.logger.writeDebug(f"20250324 result: {result}")
        result2 = SnapshotCommonPropertiesExtractor(self.storage_serial_number).extract(
            result, self.port_type_dict
        )
        self.logger.writeDebug(f"20250324 result2: {result2}")
        return result2

    def get_storage_serial_number(self):
        storage_gw = VSPStorageSystemDirectGateway(self.connectionInfo)
        storage_system = storage_gw.get_current_storage_system_info()
        return storage_system.serialNumber

    def get_all_snapshot_groups(self) -> Any:
        snapshot_groups = self.provisioner.get_snapshot_groups()
        if not snapshot_groups:
            return
        extracted_data = SnapshotGroupCommonPropertiesExtractor(
            self.storage_serial_number
        ).extract(snapshot_groups.data_to_list())
        return extracted_data

    def get_snapshots_using_grp_name(self, grp_name: Any) -> Any:
        grp_snapshots = self.provisioner.get_snapshots_by_grp_name(grp_name)
        if not grp_snapshots:
            return
        grp_snapshots.snapshots.data = [
            snap
            for snap in grp_snapshots.snapshots.data
            if snap.status.lower() != "smpp"
        ]
        result = {
            "snapshot_group_name": grp_snapshots.snapshotGroupName,
            "snapshot_group_id": grp_snapshots.snapshotGroupId,
        }
        extracted_data = SnapshotCommonPropertiesExtractor(
            self.storage_serial_number
        ).extract(grp_snapshots.snapshots.to_dict(), self.port_type_dict)
        result["snapshots"] = extracted_data
        return result

    def create_vclone_from_snapshot(self, spec: Any) -> None:

        existing_snapshot = self.provisioner.get_snapshot_facts(
            pvol=spec.pvol, mirror_unit_id=spec.mirror_unit_id
        )
        if not existing_snapshot:
            raise ValueError(
                VSPSnapShotValidateMsg.SNAPSHOT_DOES_NOT_EXIST.value.format(
                    spec.primary_volume_id, spec.mirror_unit_id
                )
            )

        self.logger.writeDebug(
            f"RC:create_convert_to_vclone_snapshot:existing_snapshot= {existing_snapshot}"
        )
        sn_pair_status = existing_snapshot[0].get("status")
        if sn_pair_status == "PAIR" or sn_pair_status == "PSUS":
            if sn_pair_status == "PAIR":
                self.provisioner.create_vclone_from_snapshot(
                    pvol=spec.pvol, mirror_unit_id=spec.mirror_unit_id
                )
            elif sn_pair_status == "PSUS":
                self.provisioner.convert_vclone_from_snapshot(
                    pvol=spec.pvol, mirror_unit_id=spec.mirror_unit_id
                )
            return self.sn_family_prov.get_snapshot_family(spec.primary_volume_id)
        else:
            self.logger.writeDebug(
                f"Snapshot with primary volume ID {spec.primary_volume_id} and mirror unit ID {spec.mirror_unit_id} is already a VClone."
            )
            raise ValueError(
                VSPVcloneValidateMsg.NOT_CORRECT_STATE_FOR_VCLONE.value.format(
                    spec.primary_volume_id, spec.mirror_unit_id
                )
            )

    def process_vclone_operations(self, spec: Any) -> None:
        is_vclone_supported = self.sn_family_prov.is_vclone_supported()
        if not is_vclone_supported:
            raise ValueError(VSPVcloneValidateMsg.NOT_SUPPORTED_ON_THIS_STORAGE.value)
        if spec.primary_volume_id is None or spec.mirror_unit_id is None:
            raise ValueError(VSPVcloneValidateMsg.VCLONE_REQD_PARAMS_MISSING.value)

        operation_type = spec.operation_type
        if operation_type == "vclone":
            return self.create_vclone_from_snapshot(spec)
        elif operation_type == "restore":
            ret_value = self.provisioner.restore_snapshot_from_vclone(
                spec.primary_volume_id, spec.mirror_unit_id
            )
            self.logger.writeDebug(
                f"RC:process_vclone_operations:ret_value= {ret_value}"
            )
            return self.sn_family_prov.get_snapshot_family(spec.primary_volume_id)

        else:
            raise ValueError(
                VSPVcloneValidateMsg.INVALID_OPERATION_TYPE.value.format(
                    spec.operation_type
                )
            )

    def validate_operation_type(self, spec: Any) -> None:
        if spec.operation_type:
            valid_operations = ["start", "stop", "vclone", "restore"]
            if spec.operation_type.lower() not in valid_operations:
                raise ValueError(
                    VSPSnapShotValidateMsg.INVALID_OPERATION_TYPE_2.value.format(
                        spec.operation_type, "', '".join(valid_operations)
                    )
                )

            spec.operation_type = spec.operation_type.lower()

    def validate_operation_type_for_snapshot_group(self, spec: Any) -> None:
        if spec.operation_type:
            valid_operations = ["vclone", "restore"]
            if spec.operation_type.lower() not in valid_operations:
                raise ValueError(
                    VSPSnapShotValidateMsg.INVALID_OPERATION_TYPE_2.value.format(
                        spec.operation_type, "', '".join(valid_operations)
                    )
                )
            spec.operation_type = spec.operation_type.lower()

    def reconcile_snapshot(self, spec: Any) -> Any:
        """
        Reconcile the snapshot based on the desired state in the specification.
        """
        state = spec.state.lower()
        resp_data = None
        if state == StateValue.ABSENT:
            if spec.should_delete_tree:
                msg = self.provisioner.delete_ti_by_snapshot_tree(pvol=spec.pvol)
                return msg
            else:
                msg = self.provisioner.delete_snapshot(
                    pvol=spec.pvol,
                    mirror_unit_id=spec.mirror_unit_id,
                    should_delete_svol=spec.should_delete_svol,
                )
                return msg
        elif state == StateValue.PRESENT:
            self.validate_operation_type(spec)
            if spec.operation_type in ["vclone", "restore"]:
                return self.process_vclone_operations(spec)
            else:
                resp_data = self.provisioner.create_snapshot(spec=spec)
            # self.logger.writeDebug(f"20240801 before calling extract, expect good poolId in resp_data: {resp_data}")
        elif state == StateValue.SPLIT:
            if spec.mirror_unit_id and spec.pvol:  # Just split
                resp_data = self.provisioner.split_snapshot(
                    pvol=spec.pvol,
                    mirror_unit_id=spec.mirror_unit_id,
                    enable_quick_mode=spec.enable_quick_mode,
                    retention_period=spec.retention_period,
                )
            else:  # Create then split
                resp_data = self.provisioner.auto_split_snapshot(spec=spec)
        elif state == StateValue.SYNC:
            resp_data = self.provisioner.resync_snapshot(
                pvol=spec.pvol,
                mirror_unit_id=spec.mirror_unit_id,
                enable_quick_mode=spec.enable_quick_mode,
            )
        elif state == StateValue.DEFRAGMENT:
            resp_data = self.provisioner.delete_garbage_data_snapshot_tree(
                spec.primary_volume_id,
                operation_type=spec.operation_type,
            )
        elif state == StateValue.CLONE:
            resp_data = self.provisioner.clone_snapshot(
                pvol=spec.pvol,
                mirror_unit_id=spec.mirror_unit_id,
                svol=spec.svol,
                copy_speed=spec.copy_speed,
            )
            return resp_data
        elif state == StateValue.RESTORE:
            resp_data = self.provisioner.restore_snapshot(
                pvol=spec.pvol,
                mirror_unit_id=spec.mirror_unit_id,
                enable_quick_mode=spec.enable_quick_mode,
                auto_split=spec.auto_split,
            )

        if isinstance(resp_data, str):
            return resp_data
        elif resp_data:
            self.logger.writeError(f"20240719 resp_data: {resp_data}")
            resp_in_dict = resp_data.to_dict()
            # self.logger.writeDebug(f"20240801 resp_data.to_dict: {resp_in_dict}")
            return SnapshotCommonPropertiesExtractor(
                self.storage_serial_number
            ).extract([resp_in_dict], self.port_type_dict)

    def snapshot_group_id_reconcile(self, spec: Any, state: str) -> Any:

        self.validate_operation_type_for_snapshot_group(spec)
        if spec.operation_type in ["vclone", "restore"]:
            return self.process_vclone_operations_for_snapshot_group(spec)

        grp_functions = {
            StateValue.ABSENT: self.provisioner.delete_snapshots_by_gid,
            StateValue.SPLIT: self.provisioner.split_snapshots_by_gid,
            StateValue.SYNC: self.provisioner.resync_snapshots_by_gid,
            StateValue.RESTORE: self.provisioner.restore_snapshots_by_gid,
            StateValue.CLONE: self.provisioner.clone_snapshots_by_gid,
        }
        if spec.snapshot_group_name is None:
            return VSPSnapShotValidateMsg.SNAPSHOT_GROUP_NAME_MISSING.value
        grp_snapshots = self.provisioner.get_snapshots_by_grp_name(spec.snapshot_group_name)

        if not grp_snapshots:
            return VSPSnapShotValidateMsg.SNAPSHOT_GROUP_NOT_FOUND.value

        spec.snapshot_group_id = grp_snapshots.snapshotGroupId
        first_snapshot = grp_snapshots.snapshots.data[0]
        grp_functions[state](spec, first_snapshot)
        return (
            self.get_snapshots_using_grp_name(spec.snapshot_group_name)
            if state != StateValue.ABSENT
            else VSPSnapShotValidateMsg.SNAPSHOT_GROUP_DELETE_SUCCESS.value
        )

    def process_vclone_operations_for_snapshot_group(self, spec: Any) -> None:
        is_vclone_supported = self.sn_family_prov.is_vclone_supported()
        if not is_vclone_supported:
            raise ValueError(VSPVcloneValidateMsg.NOT_SUPPORTED_ON_THIS_STORAGE.value)
        if spec.snapshot_group_name is None:
            raise ValueError(
                VSPSnapShotValidateMsg.RESTORE_REQD_PARAMS_MISSING_FOR_GROUP.value
            )

        operation_type = spec.operation_type.lower()
        if operation_type == "vclone":
            return self.create_vclone_from_snapshot_group_name(spec)
        elif operation_type == "restore":
            return self.restore_snapshot_group_from_vclone(spec)
        else:
            raise ValueError(
                VSPSnapShotValidateMsg.INVALID_OPERATION_TYPE.value.format(
                    spec.operation_type
                )
            )

    def restore_snapshot_group_from_vclone(self, spec: Any) -> None:
        existing_snapshot_grp = self.provisioner.get_snapshots_by_gid(
            spec.snapshot_group_name
        )
        if not existing_snapshot_grp:
            raise ValueError(
                VSPSnapShotValidateMsg.SNAPSHOT_GROUP_DOES_NOT_EXIST.value.format(
                    spec.snapshot_group_name
                )
            )

        self.logger.writeDebug(
            f"RC:restore_snapshot_group_from_vclone:existing_snapshot= {existing_snapshot_grp}"
        )
        ret_value = self.provisioner.restore_snapshots_by_snapshot_group_name(
            spec.snapshot_group_name
        )
        self.logger.writeDebug(
            f"RC:restore_snapshot_group_from_vclone:ret_value= {ret_value}"
        )
        return self.get_snapshots_using_grp_name(spec.snapshot_group_name)

    def create_vclone_from_snapshot_group_name(self, spec: Any) -> None:
        existing_snapshot_grp = self.provisioner.get_snapshots_by_gid(
            spec.snapshot_group_name
        )
        if not existing_snapshot_grp:
            raise ValueError(
                VSPSnapShotValidateMsg.SNAPSHOT_GROUP_DOES_NOT_EXIST.value.format(
                    spec.snapshot_group_name
                )
            )

        self.logger.writeDebug(
            f"RC:create_convert_to_vclone_snapshot:existing_snapshot= {existing_snapshot_grp}"
        )
        if not self.is_status_same_for_all_snapshots(
            existing_snapshot_grp.snapshots.data
        ):
            raise ValueError(
                VSPSnapShotValidateMsg.NOT_ALL_SNAPSHOTS_IN_SAME_STATUS.value.format(
                    spec.snapshot_group_name
                )
            )

        sn_pair_status = existing_snapshot_grp.snapshots.data[0].status
        primary_volume_id = existing_snapshot_grp.snapshots.data[0].pvolLdevId
        if sn_pair_status == "PAIR" or sn_pair_status == "PSUS":
            if sn_pair_status == "PAIR":
                self.provisioner.create_vclone_from_snapshot_group_name(
                    spec.snapshot_group_name
                )

            elif sn_pair_status == "PSUS":
                self.provisioner.convert_vclone_from_snapshot_group_name(
                    spec.snapshot_group_name
                )
            return self.sn_family_prov.get_snapshot_family(primary_volume_id)
        else:
            self.logger.writeDebug(
                f"Snapshot with snapshot group name {spec.snapshot_group_name} is not in a valid state to create a VClone."
            )
            raise ValueError(
                VSPSnapShotValidateMsg.NOT_CORRECT_STATE_FOR_SNAPSHOT_GROUP.value.format(
                    spec.snapshot_group_name
                )
            )

    def is_status_same_for_all_snapshots(self, snapshots: Any) -> bool:
        status = snapshots[0].status
        for snapshot in snapshots:
            if snapshot.status != status:
                return False
        return True


class SnapshotGroupCommonPropertiesExtractor:
    def __init__(self, serial):
        self.storage_serial_number = serial
        self.common_properties = {
            "snapshotGroupName": str,
            "snapshotGroupId": str,
        }

    def extract(self, responses):
        new_items = []
        for response in responses:
            new_dict = {}
            # new_dict = {"storage_serial_number": self.storage_serial_number}
            for key, value_type in self.common_properties.items():
                response_key = response.get(key)
                cased_key = camel_to_snake_case(key)
                if response_key is not None:
                    new_dict[cased_key] = value_type(response_key)
                else:
                    default_value = get_default_value(value_type)
                    new_dict[cased_key] = default_value
            new_items.append(new_dict)
        return new_items


class SnapshotCommonPropertiesExtractor:
    def __init__(self, serial):
        self.storage_serial_number = serial
        self.common_properties = {
            "snapshotGroupName": str,
            # "primaryOrSecondary":str,
            "pvolLdevId": int,
            "svolLdevId": int,
            "poolId": int,
            "muNumber": int,
            "copyRate": int,
            "copyPaceTrackSize": str,
            "status": str,
            "type": str,
            "isClone": bool,
            "snapshotId": str,
            "isConsistencyGroup": bool,
            "canCascade": bool,
            "isRedirectOnWrite": bool,
            "isSnapshotDataReadOnly": bool,
            "svolProcessingStatus": str,
            "pvolNvmSubsystemName": str,
            "svolNvmSubsystemName": str,
            "pvolHostGroups": list,
            "svolHostGroups": list,
            "retentionPeriodInHours": int,
            "progressRate": int,
            "concordanceRate": int,
            "pvolProcessingStatus": str,
            "splitTime": str,
            "isWrittenInSvol": bool,
            "isVirtualCloneParentVolume": bool,
            "isVirtualCloneVolume": bool,
            "primary_volume_nvm_subsystem_name": str,
            "secondary_volume_nvm_subsystem_name": str,
            "pvol_iscsi_targets": list,
            "svol_iscsi_targets": list,
            "primary_volume_iscsi_targets": list,
            "secondary_volume_iscsi_targets": list,
            "primary_volume_host_groups": list,
            "secondary_volume_host_groups": list,
            "is_written_in_secondary_volume": bool,
            "primary_volume_processing_status": str,
            "secondary_volume_processing_status": str,
        }

        self.parameter_mapping = {
            "pvol_ldev_id": "primary_volume_id",
            "svol_ldev_id": "secondary_volume_id",
            "mu_number": "mirror_unit_id",
            "retention_period": "retention_period_in_hours",
        }

    def extract(self, responses, port_type_dict):
        logger = Log()
        new_items = []
        for response in responses:
            new_dict = {}
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

                if value_type == list and response_key:
                    # logger.writeDebug(f"20250324 response_key: {response_key}")
                    new_dict[cased_key] = self.process_list(response_key)
                    # logger.writeDebug(f"20250324 new_dict[key]: {new_dict[key]}")

            if new_dict.get("pvol_host_groups"):
                self.split_host_groups(
                    new_dict["pvol_host_groups"],
                    new_dict,
                    "pvolHostGroups",
                    port_type_dict,
                )

            if new_dict.get("svol_host_groups"):
                self.split_host_groups(
                    new_dict["svol_host_groups"],
                    new_dict,
                    "svolHostGroups",
                    port_type_dict,
                )

            if not new_dict.get("snapshot_id"):
                new_dict["snapshot_id"] = (
                    str(response.get("primaryVolumeId"))
                    + ","
                    + str(response.get("mirrorUnitId"))
                )
            new_dict["mirror_unit_number"] = new_dict.get("mirror_unit_id", -1)
            if (
                new_dict.get("primary_volume_id_hex") is None
                and new_dict.get("primary_volume_id") is not None
            ):
                new_dict["primary_volume_id_hex"] = volume_id_to_hex_format(
                    new_dict.get("primary_volume_id")
                )
            if (
                new_dict.get("secondary_volume_id_hex") is None
                and new_dict.get("secondary_volume_id") is not None
            ):
                new_dict["secondary_volume_id_hex"] = volume_id_to_hex_format(
                    new_dict.get("secondary_volume_id")
                )
            if new_dict.get("primary_volume_nvm_subsystem_name"):
                new_dict["primary_volume_nvm_subsystem_name"] = new_dict.get(
                    "pvol_nvm_subsystem_name"
                )

            if new_dict.get("secondary_volume_nvm_subsystem_name"):
                new_dict["secondary_volume_nvm_subsystem_name"] = new_dict.get(
                    "svol_nvm_subsystem_name"
                )
            if new_dict.get("is_written_in_svol") is not None:
                new_dict["is_written_in_secondary_volume"] = new_dict.get(
                    "is_written_in_svol"
                )
            if new_dict.get("pvol_processing_status") is not None:
                new_dict["primary_volume_processing_status"] = new_dict.get(
                    "pvol_processing_status"
                )
            if new_dict.get("svol_processing_status") is not None:
                new_dict["secondary_volume_processing_status"] = new_dict.get(
                    "svol_processing_status"
                )
            new_items.append(new_dict)
        return new_items

    def split_host_groups(self, items, new_dict, key, port_type_dict):
        logger = Log()
        # logger.writeDebug(f"20250324 key: {key}")
        # logger.writeDebug(f"20250324 items: {items}")
        if items is None:
            return

        its = []
        hgs = []
        for item in items:
            if item is None:
                continue

            port_id = item["port_id"]
            port_type = port_type_dict[port_id]
            if port_type == "ISCSI":
                its.append(item)
            else:
                hgs.append(item)

        if key == "pvolHostGroups":
            new_dict["pvol_iscsi_targets"] = its
            new_dict["primary_volume_iscsi_targets"] = its
            new_dict["pvol_host_groups"] = hgs
            new_dict["primary_volume_host_groups"] = hgs
        else:
            new_dict["svol_iscsi_targets"] = its
            new_dict["secondary_volume_iscsi_targets"] = its
            new_dict["svol_host_groups"] = hgs
            new_dict["secondary_volume_host_groups"] = hgs

        return

    def process_list(self, response_key):
        logger = Log()
        new_items = []

        if response_key is None:
            return []

        for item in response_key:
            new_dict = {}
            for key, value in item.items():
                key = camel_to_snake_case(key)
                value_type = type(value)
                if value is None:
                    default_value = get_default_value(value_type)
                    value = default_value
                new_dict[key] = value
            new_items.append(new_dict)
        return new_items
