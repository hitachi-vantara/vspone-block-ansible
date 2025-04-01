try:
    from ..provisioner.vsp_shadow_image_pair_provisioner import (
        VSPShadowImagePairProvisioner,
    )
    from ..common.ansible_common import (
        snake_to_camel_case,
        log_entry_exit,
        volume_id_to_hex_format,
        get_default_value,
    )
    from ..common.hv_constants import (
        StateValue,
    )
    from ..common.hv_log import Log
    from ..common.hv_constants import ConnectionTypes
    from ..gateway.vsp_storage_system_gateway import VSPStorageSystemDirectGateway
except ImportError:
    from provisioner.vsp_shadow_image_pair_provisioner import (
        VSPShadowImagePairProvisioner,
    )
    from common.ansible_common import (
        snake_to_camel_case,
        log_entry_exit,
        volume_id_to_hex_format,
        get_default_value,
    )
    from common.hv_constants import StateValue
    from common.hv_log import Log
    from common.hv_constants import ConnectionTypes
    from gateway.vsp_storage_system_gateway import VSPStorageSystemDirectGateway
logger = Log()


class VSPShadowImagePairReconciler:

    def __init__(self, connectionInfo, serial, shadowImagePairSpec=None):
        self.connectionInfo = connectionInfo
        self.serial = serial
        self.shadowImagePairSpec = shadowImagePairSpec
        self.provisioner = VSPShadowImagePairProvisioner(self.connectionInfo)
        if self.serial is None:
            self.serial = self.get_storage_serial_number()

    @log_entry_exit
    def shadow_image_pair_facts(self, shadowImagePairSpec):
        if shadowImagePairSpec is None:
            data = self.provisioner.get_all_shadow_image_pairs(self.serial)
        else:
            data = self.provisioner.get_all_shadow_image_pairs(
                self.serial, shadowImagePairSpec.pvol
            )
        return ShadowImagePairPropertyExtractor(self.serial).extract(data)

    @log_entry_exit
    def shadow_image_pair_module(self, state):

        shadow_image_response = None

        shadow_image_data = None
        try:
            if self.shadowImagePairSpec.pvol and self.shadowImagePairSpec.svol:
                shadow_image_data = self.shadow_image_pair_get_by_pvol_and_svol(
                    self.shadowImagePairSpec.pvol, self.shadowImagePairSpec.svol
                )
        except Exception as e:
            logger.writeError(f"An error occurred: {str(e)}")
        pairId = None
        if shadow_image_data is not None:
            pairId = shadow_image_data.get("resourceId")
        if pairId is not None:
            self.shadowImagePairSpec.pair_id = pairId
        try:
            if state == StateValue.PRESENT:
                if pairId is not None:
                    shadow_image_response = shadow_image_data
                    self.connectionInfo.changed = False
                else:
                    shadow_image_response = self.shadow_image_pair_create(
                        self.shadowImagePairSpec
                    )
                    self.connectionInfo.changed = True
            elif state == StateValue.SPLIT:
                if pairId is not None:
                    if shadow_image_data.get("status") == "PSUS":
                        shadow_image_response = shadow_image_data
                        self.connectionInfo.changed = False
                    else:
                        shadow_image_response = self.shadow_image_pair_split(
                            self.shadowImagePairSpec
                        )
                        self.connectionInfo.changed = True
                else:
                    self.shadowImagePairSpec.auto_split = True
                    shadow_image_response = self.shadow_image_pair_create(
                        self.shadowImagePairSpec
                    )
                    self.connectionInfo.changed = True
            elif state == StateValue.SYNC:
                if pairId is not None:
                    if shadow_image_data.get("status") == "PAIR":
                        shadow_image_response = shadow_image_data
                        self.connectionInfo.changed = False
                    else:
                        shadow_image_response = self.shadow_image_pair_resync(
                            self.shadowImagePairSpec
                        )
                        self.connectionInfo.changed = True
                else:
                    shadow_image_response = "Shadow image pair is not available."
                    self.connectionInfo.changed = False
            elif state == StateValue.RESTORE:
                if pairId is not None:
                    if shadow_image_data.get("status") == "PAIR":
                        shadow_image_response = shadow_image_data
                        self.connectionInfo.changed = False
                    else:
                        shadow_image_response = self.shadow_image_pair_restore(
                            self.shadowImagePairSpec
                        )
                        self.connectionInfo.changed = True
                else:
                    shadow_image_response = "Shadow image pair is not available."
                    self.connectionInfo.changed = False
            elif state == StateValue.ABSENT:
                if pairId is not None:
                    shadow_image_response = self.shadow_image_pair_delete(
                        self.shadowImagePairSpec
                    )
                    self.connectionInfo.changed = True
                else:
                    shadow_image_response = "Shadow image pair is not available."
                    self.connectionInfo.changed = False

        except Exception as e:
            logger.writeError(f"An error occurred: {str(e)}")
            if (
                self.connectionInfo.connection_type is None
                or self.connectionInfo.connection_type == ConnectionTypes.DIRECT
            ):
                if e.args is not list:
                    for elm in e.args[0]:
                        if "message" == elm:
                            raise Exception(e.args[0]["message"])
                    raise Exception(e.args[0])
                    # if e.args[0]['message'] is not None:
                    #     raise Exception(e.args[0]['message'])
                    # else:
                    #     raise Exception(e.args[0])
                    # try:
                    #     if e.args[0]['message'] is not None:
                    #         raise Exception(e.args[0]['message'])
                    # except Exception as ex:
                    #     raise Exception(ex.args)
                elif "message" in e.args[0]:
                    raise Exception(e.args[0].get("message"))

                else:
                    raise Exception(e)
            logger.writeError(f"An error occurred: {str(e)}")
            raise Exception(str(e))

            # self.module.fail_json(msg=str(e))
        shadow_image_response = (
            ShadowImagePairPropertyExtractor(self.serial).extract_object(
                shadow_image_response
            )
            if isinstance(shadow_image_response, dict)
            else shadow_image_response
        )
        return shadow_image_response

    @log_entry_exit
    def get_storage_serial_number(self):
        storage_gw = VSPStorageSystemDirectGateway(self.connectionInfo)
        storage_system = storage_gw.get_current_storage_system_info()
        return storage_system.serialNumber

    @log_entry_exit
    def shadow_image_pair_create(self, shadowImagePairSpec):
        data = self.provisioner.create_shadow_image_pair(
            self.serial, shadowImagePairSpec
        )
        return data

    @log_entry_exit
    def shadow_image_pair_split(self, shadowImagePairSpec):
        data = self.provisioner.split_shadow_image_pair(
            self.serial, shadowImagePairSpec
        )
        return data

    @log_entry_exit
    def shadow_image_pair_resync(self, shadowImagePairSpec):
        data = self.provisioner.resync_shadow_image_pair(
            self.serial, shadowImagePairSpec
        )
        return data

    @log_entry_exit
    def shadow_image_pair_restore(self, shadowImagePairSpec):
        data = self.provisioner.restore_shadow_image_pair(
            self.serial, shadowImagePairSpec
        )
        return data

    @log_entry_exit
    def shadow_image_pair_get_by_pvol_and_svol(self, pvol, svol):
        data = self.provisioner.get_shadow_image_pair_by_pvol_and_svol(
            self.serial, pvol, svol
        )
        return data

    @log_entry_exit
    def shadow_image_pair_delete(self, shadowImagePairSpec):
        data = self.provisioner.delete_shadow_image_pair(
            self.serial, shadowImagePairSpec
        )
        return data

    @log_entry_exit
    def is_out_of_band(self):
        return self.provisioner.is_out_of_band()


class ShadowImagePairPropertyExtractor:
    def __init__(self, serial):
        self.entitlement_properties = {
            "partner_id": str,
            "subscriber_id": str,
            "entitlement_status": str,
        }
        self.common_properties = {
            # "resource_id": str,
            "consistency_group_id": int,
            "copy_pace_track_size": str,
            "copy_rate": int,
            "mirror_unit_id": int,
            "primary_hex_volume_id": str,
            "primary_volume_id": int,
            "storage_serial_number": str,
            "secondary_hex_volume_id": str,
            "secondary_volume_id": int,
            "status": str,
            "svol_access_mode": str,
            "type": str,
            "copy_group_name": str,
            "copy_pair_name": str,
            "pvol_nvm_subsystem_name": str,
            "svol_nvm_subsystem_name": str,
        }
        self.serial = serial

    def extract(self, responses):
        new_items = []
        for response in responses:
            # new_dict = {"storage_serial_number": self.serial}
            new_dict = {}
            for key, value_type in self.entitlement_properties.items():
                # Assign the value based on the response key and its data type
                cased_key = snake_to_camel_case(key)
                # Get the corresponding key from the response or its mapped key
                response_key = response.get(cased_key)

                if response_key is not None:
                    new_dict[key] = value_type(response_key)
                else:
                    # Handle missing keys by assigning default values
                    default_value = get_default_value(value_type)
                    new_dict[key] = default_value

            for key, value_type in self.common_properties.items():
                # Assign the value based on the response key and its data type
                cased_key = snake_to_camel_case(key)
                # Get the corresponding key from the response or its mapped key

                response_key = response.get(cased_key)

                if response_key is not None:
                    if key != "type":
                        new_dict[key] = value_type(response_key)
                else:
                    if key == "storage_serial_number":
                        new_dict[key] = self.serial
                    else:
                        # Handle missing keys by assigning default values
                        default_value = get_default_value(value_type)
                        new_dict[key] = default_value
            if new_dict.get("primary_hex_volume_id") == "":
                new_dict["primary_hex_volume_id"] = volume_id_to_hex_format(
                    new_dict.get("primary_volume_id")
                )
            if new_dict.get("secondary_hex_volume_id") == "":
                new_dict["secondary_hex_volume_id"] = volume_id_to_hex_format(
                    new_dict.get("secondary_volume_id")
                )
            new_items.append(new_dict)
        return new_items

    def extract_object(self, response):

        # new_dict = {"storage_serial_number": self.serial}
        new_dict = {}
        for key, value_type in self.entitlement_properties.items():
            # Assign the value based on the response key and its data type
            cased_key = snake_to_camel_case(key)
            # Get the corresponding key from the response or its mapped key
            response_key = response.get(cased_key)

            if response_key is not None:
                new_dict[key] = value_type(response_key)
            else:
                # Handle missing keys by assigning default values
                default_value = get_default_value(value_type)
                new_dict[key] = default_value
        for key, value_type in self.common_properties.items():
            # Assign the value based on the response key and its data type
            cased_key = snake_to_camel_case(key)
            # Get the corresponding key from the response or its mapped key
            response_key = response.get(cased_key)

            if response_key is not None:
                if key != "type":
                    new_dict[key] = value_type(response_key)
            else:
                if key == "storage_serial_number":
                    new_dict[key] = self.serial
                else:
                    # Handle missing keys by assigning default values
                    default_value = get_default_value(value_type)
                    new_dict[key] = default_value

        if new_dict.get("primary_hex_volume_id") == "":
            new_dict["primary_hex_volume_id"] = volume_id_to_hex_format(
                new_dict.get("primary_volume_id")
            )
        if new_dict.get("secondary_hex_volume_id") == "":
            new_dict["secondary_hex_volume_id"] = volume_id_to_hex_format(
                new_dict.get("secondary_volume_id")
            )
        return new_dict
