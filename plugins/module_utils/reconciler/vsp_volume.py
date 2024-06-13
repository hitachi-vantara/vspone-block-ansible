try:
    from ..common.ansible_common import (
        convert_block_capacity,
        convert_to_bytes,
        log_entry_exit,
        snake_to_camel_case,
        process_size_string,
        get_response_key,
        volume_id_to_hex_format
    )
    from ..common.hv_constants import StateValue
    from ..common.vsp_constants import VolumePayloadConst
    from ..model.common_base_models import ConnectionInfo
    from ..model.vsp_volume_models import VSPVolumeInfo, VSPVolumesInfo
    from ..model.vsp_volume_models import (
        CreateVolumeSpec,
        VolumeFactSpec,
        VSPVolumeInfo,
    )
    from ..provisioner.vsp_volume_prov import VSPVolumeProvisioner
    from ..message.vsp_lun_msgs import VSPVolValidationMsg
except ImportError:
    from common.ansible_common import (
        convert_block_capacity,
        convert_to_bytes,
        log_entry_exit,
        snake_to_camel_case,
        process_size_string,
        get_response_key,
        volume_id_to_hex_format
    )
    from common.vsp_constants import VolumePayloadConst

    from common.hv_constants import StateValue
    from model.common_base_models import ConnectionInfo
    from model.vsp_volume_models import CreateVolumeSpec, VolumeFactSpec, VSPVolumeInfo
    from provisioner.vsp_volume_prov import VSPVolumeProvisioner


class VSPVolumeReconciler:
    """_summary_"""

    def __init__(self, connection_info: ConnectionInfo, serial: str):
        self.connection_info = connection_info
        self.serial = serial
        self.provisioner = VSPVolumeProvisioner(self.connection_info)

    @log_entry_exit
    def volume_reconcile(self, state: str, spec: CreateVolumeSpec):
        """Reconciler for volume management"""

        if state == StateValue.PRESENT:
            volume = None
            if spec.lun:
                volume = self.provisioner.get_volume_by_ldev(spec.lun)
            if not volume or volume.emulationType == VolumePayloadConst.NOT_DEFINED:
                spec.lun = self.create_volume(spec)
                if spec.name:
                    # Set name after ldev is created
                    self.update_volume_name(spec.lun, spec.name)
            else:
                self.update_volume(volume, spec)
            return self.provisioner.get_volume_by_ldev(spec.lun)

        elif state == StateValue.ABSENT:
            volume = self.provisioner.get_volume_by_ldev(spec.lun)
            if not volume or volume.emulationType == VolumePayloadConst.NOT_DEFINED:
                return None
            self.delete_volume(volume)

    @log_entry_exit
    def update_volume(self, volume_data: VSPVolumeInfo, spec: CreateVolumeSpec):

        # Expand the size if its required
        if spec.size:
            if "." in spec.size:
                raise ValueError(VSPVolValidationMsg.SIZE_INT_REQUIRED.value)
            size_in_bytes = convert_to_bytes(spec.size)
            expand_val = size_in_bytes - (
                volume_data.blockCapacity if volume_data.blockCapacity else 0
            )
            if expand_val > 0:
                enhanced_expansion = True if volume_data.isDataReductionShareEnabled is not None else False
                self.provisioner.expand_volume_capacity(volume_data.ldevId, expand_val, enhanced_expansion)
                self.connection_info.changed = True
            elif expand_val < 0:
                raise ValueError(VSPVolValidationMsg.VALID_SIZE.value)

        # update the volume by comparing the existing details
        if (
            spec.capacity_saving
            and spec.capacity_saving != volume_data.dataReductionMode
        ) or (spec.name and spec.name != volume_data.label):
            self.provisioner.change_volume_settings(
                volume_data.ldevId, spec.name, spec.capacity_saving
            )
            self.connection_info.changed = True

        return volume_data.ldevId

    @log_entry_exit
    def create_volume(self, spec: CreateVolumeSpec):
        
        if isinstance(spec.pool_id, int) and spec.parity_group:
            raise ValueError(VSPVolValidationMsg.POOL_ID_PARITY_GROUP.value)
        if not isinstance(spec.pool_id, int) and not spec.parity_group:
            raise ValueError(VSPVolValidationMsg.NOT_POOL_ID_OR_PARITY_ID.value)
        if not spec.size:
            raise ValueError(VSPVolValidationMsg.SIZE_REQUIRED.value)
        if "." in spec.size:
            raise ValueError(VSPVolValidationMsg.SIZE_INT_REQUIRED.value)
        spec.size = process_size_string(spec.size)
        self.connection_info.changed = True
        return self.provisioner.create_volume(spec)

    @log_entry_exit
    def get_volumes(self, get_volume_spec: VolumeFactSpec):

        if get_volume_spec.lun:
            return VSPVolumesInfo(data=[self.provisioner.get_volume_by_ldev(get_volume_spec.lun)])
     
        volume_data = self.provisioner.get_volumes(
            get_volume_spec.start_ldev_id, get_volume_spec.count
        )

        if get_volume_spec.end_ldev_id:
            end_ldev_id = get_volume_spec.end_ldev_id
            volume_data.data = [
                volume for volume in volume_data.data if volume.ldevId <= end_ldev_id 
            ]

        if get_volume_spec.name:
            volume_data.data = [
                volume for volume in volume_data.data if volume.label == get_volume_spec.name
            ]

        return volume_data

    @log_entry_exit
    def update_volume_name(self, ldev_id, name):

        self.provisioner.change_volume_settings(ldev_id, name=name)

    @log_entry_exit
    def get_volume_by_name(self, name):

        volumes = self.provisioner.get_volumes()
        for volume in volumes.data:
            if volume.label == name:
                return volume
            
    @log_entry_exit
    def get_volume_by_id(self, id):

        volumes = self.provisioner.get_volumes()
        for volume in volumes.data:
            if volume.ldevId == int(id):
                return volume
        raise ValueError(VSPVolValidationMsg.VOLUME_NOT_FOUND.value.format(id))

    @log_entry_exit
    def delete_volume(self, volume:VSPVolumeInfo):
        ldev_id = volume.ldevId
        force_execute = True if volume.dataReductionMode and volume.dataReductionMode.lower() != VolumePayloadConst.DISABLED else None
        self.provisioner.delete_volume(ldev_id, force_execute)
        self.connection_info.changed = True


class VolumeCommonPropertiesExtractor:
    def __init__(self, serial):

        self.serial = serial
        self.common_properties = {
            "ldev_id": int,
            "deduplication_compression_mode": str,
            "emulation_type": str,
            "name": str,
            "parity_group_id": str,
            # "parity_group_ids": list,
            "pool_id": int,
            "resource_group_id": int,
            "status": str,
            "total_capacity": str,
            "used_capacity": str,
            "path_count": int,
            "provision_type": str,
            "logical_unit_id_hex_format": str,
            "naa_id": str,
            "dedup_compression_progress": int,
            "dedup_compression_status": str,
            "is_alua": bool,
        }

        self.parameter_mapping = {
            "is_alua": "isAluaEnabled",
            "parity_group_id": "parityGroupIds",
            "path_count": "num_ports",
            "naa_id": "canonicalName",
            "provision_type": "attributes",
            "total_capacity": "blockCapacity",
            "used_capacity": "numOfUsedBlock",
            "name": "label",
            "deduplication_compression_mode": "dataReductionMode",
            "dedup_compression_status": "dataReductionStatus",
            "dedup_compression_progress": "dataReductionProgressRate",
        }
        self.size_properties = ("total_capacity", "used_capacity")
        self.provision_type = "provision_type"
        self.hex_value = "logical_unit_id_hex_format"
        self.parity_group_id = "parity_group_id"
    @log_entry_exit
    def extract(self, responses):
        new_items = []
        for response in responses:
            new_dict = {"storage_serial_number": self.serial}
            if response.get("isDataReductionShareEnabled") is not None:
                new_dict["is_data_reduction_share_enabled"] = response.get("isDataReductionShareEnabled")
            for key, value_type in self.common_properties.items():

                cased_key = snake_to_camel_case(key)
                # Get the corresponding key from the response or its mapped key

                response_key = get_response_key(
                    response,
                    cased_key,
                    self.parameter_mapping.get(cased_key),
                    key,
                    self.parameter_mapping.get(key),
                )

                # Assign the value based on the response key and its data type

                if response_key or isinstance(response_key, int):
                    if key == self.provision_type or key ==  self.parity_group_id:
                        new_dict[key] = value_type(
                            response_key
                            if isinstance(response_key, str)
                            else ",".join(response_key)
                        )
                    
                    elif key in self.size_properties:
                        if type(response_key) == str:
                            new_dict[key] = value_type(response_key)
                        else:
                            new_dict[key] = value_type(
                                convert_block_capacity(response_key)
                            )
                    else:
                        new_dict[key] = value_type(response_key)
                elif key == self.hex_value:
                        new_dict[key] = response_key if response_key else volume_id_to_hex_format(response.get("ldevId"))
                else:
                    # Handle missing keys by assigning default values
                    default_value = (
                        "" if value_type == str else -1 if value_type == int else False
                    )
                    new_dict[key] = default_value
            new_items.append(new_dict)
        return new_items
