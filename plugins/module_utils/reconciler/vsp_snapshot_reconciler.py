from typing import Optional, Any

try:
    from ..provisioner.vsp_snapshot_provisioner import VSPHtiSnapshotProvisioner
    from ..common.ansible_common import camel_to_snake_case
    from ..common.hv_log import Log
    from ..common.hv_log_decorator import LogDecorator
    from ..common.hv_constants import StateValue, ConnectionTypes
except ImportError:
    from provisioner.vsp_snapshot_provisioner import VSPHtiSnapshotProvisioner
    from common.ansible_common import camel_to_snake_case
    from common.hv_log import Log
    from common.hv_log_decorator import LogDecorator
    from common.hv_constants import StateValue, ConnectionTypes



@LogDecorator.debug_methods
class VSPHtiSnapshotReconciler:
    def __init__(
        self, connectionInfo: Any, serial: str, snapshotSpec: Optional[Any] = None
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
        result = self.provisioner.get_snapshot_facts(
            pvol=spec.pvol, mirror_unit_id=spec.mirror_unit_id
        )
        return SnapshotCommonPropertiesExtractor(self.storage_serial_number).extract(
            result
        )

    def reconcile_snapshot(self, spec: Any) -> Any:
        """
        Reconcile the snapshot based on the desired state in the specification.
        """
        state = spec.state.lower()
        resp_data = None
        if state == StateValue.ABSENT:
            return self.provisioner.delete_snapshot(
                pvol=spec.pvol, mirror_unit_id=spec.mirror_unit_id
            )
        elif state == StateValue.PRESENT:
            if spec.pool_id is None:
                raise ValueError("Spec.pool_id is required for spec.state = present")
            resp_data = self.provisioner.create_snapshot(spec=spec)
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
        elif state == StateValue.RESTORE:
            resp_data = self.provisioner.restore_snapshot(
                pvol=spec.pvol,
                mirror_unit_id=spec.mirror_unit_id,
                enable_quick_mode=spec.enable_quick_mode,
                auto_split=spec.auto_split,
            )

        if resp_data:
            return SnapshotCommonPropertiesExtractor(
                self.storage_serial_number
            ).extract([resp_data])[0]

    def check_storage_in_ucpsystem(self) -> bool:
        """
        Check if the storage is in the UCP system.
        """
        return self.provisioner.check_storage_in_ucpsystem()


class SnapshotCommonPropertiesExtractor:
    def __init__(self, serial):
        self.storage_serial_number = serial
        self.common_properties = {
            "snapshotGroupName":str,
            "primaryOrSecondary":str,
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
            "entitlementStatus": str,
            "snapshotId": str,
            "partnerId": str,
            "subscriberId": str,
        }

        self.parameter_mapping = {
            "primaryVolumeId": "pvolLdevId",
            "secondaryVolumeId": "svolLdevId",
            "poolId": "snapshotPoolId",
            "mirrorUnitId": "muNumber",
        }

    def extract(self, responses):
        new_items = []
        for response in responses:
            # response = (
            #     response.get("snapshotPairInfo")
            #     if response.get("snapshotPairInfo")
            #     else response
            # )
            new_dict = {"storage_serial_number": self.storage_serial_number}
            for key, value_type in self.common_properties.items():
                # Get the corresponding key from the response or its mapped key
                response_key = response.get(key) or response.get(
                    self.parameter_mapping.get(key)
                )
                # Assign the value based on the response key and its data type
                cased_key = camel_to_snake_case(key)
                if response_key is not None:
                    new_dict[cased_key] = value_type(response_key)
                else:
                    # Handle missing keys by assigning default values
                    default_value = (
                        "" if value_type == str else -1 if value_type == int else False
                    )
                    new_dict[cased_key] = default_value
            new_items.append(new_dict)
        return new_items
