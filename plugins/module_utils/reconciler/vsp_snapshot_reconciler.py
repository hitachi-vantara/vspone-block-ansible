from typing import Optional, Any

try:
    from ..provisioner.vsp_snapshot_provisioner import VSPHtiSnapshotProvisioner
    from ..common.ansible_common import camel_to_snake_case,volume_id_to_hex_format
    from ..common.hv_log import Log
    from ..common.hv_log_decorator import LogDecorator
    from ..common.hv_constants import StateValue, ConnectionTypes
    from ..message.vsp_snapshot_msgs import VSPSnapShotValidateMsg
    from ..model.vsp_snapshot_models import SnapshotGroupFactSpec
except ImportError:
    from provisioner.vsp_snapshot_provisioner import VSPHtiSnapshotProvisioner
    from common.ansible_common import camel_to_snake_case,volume_id_to_hex_format
    from common.hv_log import Log
    from common.hv_log_decorator import LogDecorator
    from common.hv_constants import StateValue, ConnectionTypes
    from message.vsp_snapshot_msgs import VSPSnapShotValidateMsg
    from model.vsp_snapshot_models import SnapshotGroupFactSpec





@LogDecorator.debug_methods
class VSPHtiSnapshotReconciler:
    def __init__(
        self, connectionInfo: Any, serial: str=None, snapshotSpec: Optional[Any] = None
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
            return self.get_snapshots_using_grp_name(spec.snapshot_group_name)
        else:
            result = self.provisioner.get_snapshot_facts(
                    pvol=spec.pvol, mirror_unit_id=spec.mirror_unit_id
                )
        result2 = SnapshotCommonPropertiesExtractor(self.storage_serial_number).extract(
            result
        )
        #self.logger.writeDebug(f"5744resultspec: {result2}")
        return result2
    
    def get_snapshots_using_grp_name(self, grp_name: Any) -> Any:
        grp_snapshots = self.provisioner.get_snapshots_by_grp_name(grp_name)
        result = {"snapshot_group_name":grp_snapshots.snapshotGroupName, "snapshot_group_id":grp_snapshots.snapshotGroupId}
        extracted_data = SnapshotCommonPropertiesExtractor(self.storage_serial_number).extract(grp_snapshots.snapshots)
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

    def snapshot_group_id_reconcile(self, spec: Any, state:str) -> Any:
        grp_functions = {
            StateValue.ABSENT: self.provisioner.delete_snapshots_by_gid,
            StateValue.SPLIT: self.provisioner.split_snapshots_by_gid,
            StateValue.SYNC: self.provisioner.resync_snapshots_by_gid,
            StateValue.RESTORE: self.provisioner.restore_snapshots_by_gid,

        }
        sng = self.provisioner.get_snapshot_grp_by_name(spec.snapshot_group_name)
        if not sng:
            return ValueError(VSPSnapShotValidateMsg.SNAPSHOT_GROUP_NOT_FOUND.value)
        spec.snapshot_group_id = sng.snapshotGroupId
        grp_functions[state](spec)
        self.connectionInfo.changed = True
        return  self.get_snapshots_using_grp_name(spec.snapshot_group_name) if state != StateValue.ABSENT else "Snapshot group deleted successfully"
        
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

        }

        self.parameter_mapping = {
            "primaryVolumeId": "pvolLdevId",
            "secondaryVolumeId": "svolLdevId",
            "poolId": "snapshotPoolId",
            "poolId": "snapshotReplicationId",
            "isConsistencyGroup": "isCTG",
            #20240801 "poolId": "snapshotPoolId",
            "mirrorUnitId": "muNumber",
            "thinImagePropertiesDto": "properties",
            
        }
        self.hex_values = {"primaryHexVolumeId":"pvolLdevId", "secondaryHexVolumeId":"svolLdevId"}

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
                response_key = response.get(key)  if response.get(key) is not None  else response.get(
                    self.parameter_mapping.get(key)
                )
                
                ## there is no logger yet
                # self.logger.writeDebug(f"20240801 key: {key}")
                # self.logger.writeDebug(f"20240801 response_key: {response_key}")
                
                # Assign the value based on the response key and its data type
                cased_key = camel_to_snake_case(key)
                if response_key is not None:
                    new_dict[cased_key] = value_type(response_key)
                    
                    # no logger yet, self.logger.writeDebug(f"20240801 new_dict[cased_key]: {new_dict[cased_key]}")
                    
                # thinImagePropertiesDto
                # elif key == "thinImagePropertiesDto":
                #     new_dict[cased_key] = self.process_list(response_key)
                # elif key == "thinImageProperties":
                #     new_dict[cased_key] = self.process_list(response_key)

                elif key in self.hex_values:
                    raw_key = self.hex_values.get(key)
                    new_dict[cased_key] = (
                        response_key
                        if response_key
                        else volume_id_to_hex_format(response.get(raw_key)).upper() 
                    )
                else:
                    # Handle missing keys by assigning default values
                    default_value = (
                        "" if value_type == str else -1 if value_type == int else False
                    )
                    new_dict[cased_key] = default_value
                    
            if not new_dict.get('snapshot_id'):
                new_dict['snapshot_id'] = \
                    str(response.get('primaryVolumeId')) + "," + \
                    str(response.get('mirrorUnitId'))
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
                    default_value = (
                        ""
                        if value_type == str
                        else (
                            -1
                            if value_type == int
                            else [] if value_type == list else False
                        )
                    )
                    value = default_value
                new_dict[key] = value
            new_items.append(new_dict)
        return new_items         
