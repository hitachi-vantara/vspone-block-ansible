from typing import Any

try:
    from ..provisioner.vsp_snapshot_provisioner import VSPHtiSnapshotProvisioner
    from ..common.ansible_common import (
        camel_to_snake_case,
        volume_id_to_hex_format,
        get_default_value,
    )
    from ..common.hv_log import Log
    from ..common.hv_log_decorator import LogDecorator
    from ..common.hv_constants import StateValue
    from ..message.vsp_snapshot_msgs import VSPSnapShotValidateMsg
    from ..model.vsp_snapshot_models import SnapshotGroupFactSpec
except ImportError:
    from provisioner.vsp_snapshot_provisioner import VSPHtiSnapshotProvisioner
    from common.ansible_common import (
        camel_to_snake_case,
        volume_id_to_hex_format,
        get_default_value,
    )
    from common.hv_log import Log
    from common.hv_log_decorator import LogDecorator
    from common.hv_constants import StateValue
    from message.vsp_snapshot_msgs import VSPSnapShotValidateMsg
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
        self.snapshotSpec = snapshotSpec
        self.provisioner = VSPHtiSnapshotProvisioner(self.connectionInfo, serial)

    def get_snapshot_facts(self, spec: Any) -> Any:
        """
        Retrieve snapshot facts based on the provided specification.
        """
        result = None
        if isinstance(spec, SnapshotGroupFactSpec):
            if spec.snapshot_group_name is None:
                return self.get_all_snapshot_groups()
            else:
                return self.get_snapshots_using_grp_name(spec.snapshot_group_name)
        else:
            result = self.provisioner.get_snapshot_facts(
                pvol=spec.pvol, mirror_unit_id=spec.mirror_unit_id
            )
        result2 = SnapshotCommonPropertiesExtractor(self.storage_serial_number).extract(
            result
        )
        # self.logger.writeDebug(f"5744resultspec: {result2}")
        return result2

    def get_all_snapshot_groups(self) -> Any:
        snapshot_groups = self.provisioner.get_snapshot_groups()
        if not snapshot_groups:
            return
        extracted_data = SnapshotGroupCommonPropertiesExtractor(
            self.storage_serial_number
        ).extract(snapshot_groups.data_to_list())
        # result = {"snapshot_groups": extracted_data}
        # return result
        return extracted_data

    def get_snapshots_using_grp_name(self, grp_name: Any) -> Any:
        grp_snapshots = self.provisioner.get_snapshots_by_grp_name(grp_name)
        if not grp_snapshots:
            return
        result = {
            "snapshot_group_name": grp_snapshots.snapshotGroupName,
            "snapshot_group_id": grp_snapshots.snapshotGroupId,
        }
        extracted_data = SnapshotCommonPropertiesExtractor(
            self.storage_serial_number
        ).extract(grp_snapshots.snapshots.to_dict())
        result["snapshots"] = extracted_data
        return result

    def reconcile_snapshot(self, spec: Any) -> Any:
        """
        Reconcile the snapshot based on the desired state in the specification.
        """
        state = spec.state.lower()
        resp_data = None
        if state == StateValue.ABSENT:
            msg = self.provisioner.delete_snapshot(
                pvol=spec.pvol, mirror_unit_id=spec.mirror_unit_id
            )
            return msg
        elif state == StateValue.PRESENT:
            if spec.pool_id is None:
                raise ValueError("Spec.pool_id is required for spec.state = present")

            resp_data = self.provisioner.create_snapshot(spec=spec)
            # self.logger.writeDebug(f"20240801 before calling extract, expect good poolId in resp_data: {resp_data}")
        elif state == StateValue.SPLIT:
            if spec.mirror_unit_id and spec.pvol:  # Just split
                resp_data = self.provisioner.split_snapshot(
                    pvol=spec.pvol,
                    mirror_unit_id=spec.mirror_unit_id,
                    enable_quick_mode=spec.enable_quick_mode,
                )
            else:  # Create then split
                resp_data = self.provisioner.auto_split_snapshot(spec=spec)
        elif state == StateValue.SYNC:
            resp_data = self.provisioner.resync_snapshot(
                pvol=spec.pvol,
                mirror_unit_id=spec.mirror_unit_id,
                enable_quick_mode=spec.enable_quick_mode,
            )
        elif state == StateValue.CLONE:
            resp_data = self.provisioner.clone_snapshot(
                pvol=spec.pvol,
                mirror_unit_id=spec.mirror_unit_id,
                svol=spec.svol,
            )
            return resp_data
        elif state == StateValue.RESTORE:
            resp_data = self.provisioner.restore_snapshot(
                pvol=spec.pvol,
                mirror_unit_id=spec.mirror_unit_id,
                enable_quick_mode=spec.enable_quick_mode,
                auto_split=spec.auto_split,
            )

        if resp_data:
            # self.logger.writeError(f"20240719 resp_data: {resp_data}")
            resp_in_dict = resp_data.to_dict()
            # self.logger.writeDebug(f"20240801 resp_data.to_dict: {resp_in_dict}")
            return SnapshotCommonPropertiesExtractor(
                self.storage_serial_number
            ).extract([resp_in_dict])[0]

    def snapshot_group_id_reconcile(self, spec: Any, state: str) -> Any:
        grp_functions = {
            StateValue.ABSENT: self.provisioner.delete_snapshots_by_gid,
            StateValue.SPLIT: self.provisioner.split_snapshots_by_gid,
            StateValue.SYNC: self.provisioner.resync_snapshots_by_gid,
            StateValue.RESTORE: self.provisioner.restore_snapshots_by_gid,
        }
        sng = self.provisioner.get_snapshot_grp_by_name(spec.snapshot_group_name)
        if not sng:
            return VSPSnapShotValidateMsg.SNAPSHOT_GROUP_NOT_FOUND.value
        grp_snapshots = self.provisioner.get_snapshots_by_grp_name(sng.snapshotGroupId)

        # if len(snapshots.snapshots) == 0:
        #     return VSPSnapShotValidateMsg.NO_SNAPSHOTS_FOUND.value

        spec.snapshot_group_id = sng.snapshotGroupId
        first_snapshot = grp_snapshots.snapshots.data[0]
        grp_functions[state](spec, first_snapshot)
        return (
            self.get_snapshots_using_grp_name(spec.snapshot_group_name)
            if state != StateValue.ABSENT
            else "Snapshot group deleted successfully"
        )

    def check_storage_in_ucpsystem(self) -> bool:
        """
        Check if the storage is in the UCP system.
        """
        return self.provisioner.check_storage_in_ucpsystem()

    def is_out_of_band(self):
        return self.provisioner.is_out_of_band()


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
            # "primaryOrSecondary":str,
            "primaryVolumeId": int,
            "primaryHexVolumeId": str,
            "secondaryVolumeId": int,
            "secondaryHexVolumeId": str,
            "svolAccessMode": str,
            "poolId": int,
            "consistencyGroupId": int,
            "mirrorUnitId": int,
            "copyRate": int,
            "copyPaceTrackSize": str,
            "status": str,
            "type": str,
            "isCloned": bool,
            "snapshotId": str,
            "isConsistencyGroup": bool,
            "canCascade": bool,
            "isRedirectOnWrite": bool,
            "isSVolWrittenTo": bool,
            "isSnapshotDataReadOnly": bool,
            "snapshotGroupName": str,
            "svolProcessingStatus": str,
            # "thinImagePropertiesDto": dict,
            # "thinImageProperties": dict,
            "entitlementStatus": str,
            "partnerId": str,
            "subscriberId": str,
            "pvolNvmSubsystemName": str,
            "svolNvmSubsystemName": str,
        }

        self.parameter_mapping = {
            "primaryVolumeId": "pvolLdevId",
            "secondaryVolumeId": "svolLdevId",
            "poolId": "snapshotPoolId",
            # "poolId": "snapshotReplicationId", # duplicate key
            "isConsistencyGroup": "isCTG",
            # 20240801 "poolId": "snapshotPoolId",
            "mirrorUnitId": "muNumber",
            "thinImagePropertiesDto": "properties",
            "isCloned": "isClone",
        }
        self.hex_values = {
            "primaryHexVolumeId": "pvolLdevId",
            "secondaryHexVolumeId": "svolLdevId",
        }

    def extract(self, responses):
        new_items = []
        for response in responses:
            new_dict = {"storage_serial_number": self.storage_serial_number}
            for key, value_type in self.common_properties.items():

                # Get the corresponding key from the response or its mapped key
                response_key = (
                    response.get(key)
                    if response.get(key) is not None
                    else response.get(self.parameter_mapping.get(key))
                )

                # Assign the value based on the response key and its data type
                cased_key = camel_to_snake_case(key)
                if response_key is not None:
                    new_dict[cased_key] = value_type(response_key)

                elif key in self.hex_values:
                    raw_key = self.hex_values.get(key)
                    new_dict[cased_key] = (
                        response_key
                        if response_key
                        else volume_id_to_hex_format(response.get(raw_key)).upper()
                    )
                else:
                    # Handle missing keys by assigning default values
                    default_value = get_default_value(value_type)
                    new_dict[cased_key] = default_value

            if not new_dict.get("snapshot_id"):
                new_dict["snapshot_id"] = (
                    str(response.get("primaryVolumeId"))
                    + ","
                    + str(response.get("mirrorUnitId"))
                )
            new_items.append(new_dict)
        return new_items

    def process_list(self, response_key):
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
