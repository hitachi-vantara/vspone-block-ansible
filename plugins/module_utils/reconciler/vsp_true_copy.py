from typing import Optional, List, Dict, Any
try:
    from ..common.ansible_common import (
        log_entry_exit,
        camel_to_snake_case,
        get_response_key,
        volume_id_to_hex_format,
    )
    from ..common.hv_log import Log
    from ..common.hv_constants import *
    from ..provisioner.vsp_true_copy_provisioner import VSPTrueCopyProvisioner
    from ..message.vsp_true_copy_msgs import VSPTrueCopyValidateMsg
    from ..model.vsp_true_copy_models import TrueCopySpec


except ImportError:
    from common.ansible_common import (
        log_entry_exit,
        camel_to_snake_case,
        get_response_key,
        volume_id_to_hex_format,
    )
    from common.hv_log import Log
    from common.hv_constants import *
    from provisioner.vsp_true_copy_provisioner import VSPTrueCopyProvisioner
    from message.vsp_true_copy_msgs import VSPTrueCopyValidateMsg
    from model.vsp_true_copy_models import TrueCopySpec


logger = Log()
class VSPTrueCopyReconciler:
    def __init__(self, connection_info, serial, state=None):

        self.connection_info = connection_info
        self.storage_serial_number = serial
        self.provisioner = VSPTrueCopyProvisioner(connection_info, serial)
        if state:
            self.state = state

    @log_entry_exit
    def delete_true_copy(self, spec):
        if spec.primary_volume_id is None:
            raise ValueError(VSPTrueCopyValidateMsg.PRIMARY_VOLUME_ID.value)
        return self.provisioner.delete_true_copy_pair(spec.primary_volume_id)

    @log_entry_exit
    def resync_true_copy(self, spec):
        if spec.primary_volume_id is None:
            raise ValueError(VSPTrueCopyValidateMsg.PRIMARY_VOLUME_ID.value)
        return self.provisioner.resync_true_copy_pair(spec.primary_volume_id)

    @log_entry_exit
    def split_true_copy(self, spec):
        if spec.primary_volume_id is None:
            raise ValueError(VSPTrueCopyValidateMsg.PRIMARY_VOLUME_ID.value)
        return self.provisioner.split_true_copy_pair(spec.primary_volume_id)

    @log_entry_exit
    def swap_split_true_copy(self, spec):
        if spec.primary_volume_id is None:
            raise ValueError(VSPTrueCopyValidateMsg.PRIMARY_VOLUME_ID.value)
        return self.provisioner.swap_split_true_copy_pair(spec.primary_volume_id)

    @log_entry_exit
    def swap_resync_true_copy(self, spec):
        if spec.primary_volume_id is None:
            raise ValueError(VSPTrueCopyValidateMsg.PRIMARY_VOLUME_ID.value)
        return self.provisioner.swap_resync_true_copy_pair(spec.primary_volume_id)

    @log_entry_exit
    def create_true_copy(self, spec):
        logger.writeDebug("RC:create_true_copy:spec={} ", spec)
        if spec.primary_volume_id is None:
            raise ValueError(VSPTrueCopyValidateMsg.PRIMARY_VOLUME_ID.value)
        if spec.secondary_hostgroups is None:
            raise ValueError(VSPTrueCopyValidateMsg.SECONDARY_HOSTGROUPS.value)
        

        pvol = self.provisioner.get_volume_by_id(spec.primary_volume_id)
        logger.writeDebug("RC:create_true_copy:pvol={} ", pvol)
        if not pvol:
            raise ValueError(VSPTrueCopyValidateMsg.PRIMARY_VOLUME_ID_DOES_NOT_EXIST.value.format(spec.primary_volume_id))
        
        pvol_v2 = self.provisioner.get_volume_by_id_v2(pvol.storageId, pvol.resourceId)
        if pvol_v2.pathCount < 1:
            raise ValueError(VSPTrueCopyValidateMsg.PRIMARY_VOLUME_ID_NO_PATH.value.format(spec.primary_volume_id))

        
        return self.provisioner.create_true_copy(spec=spec)


    @log_entry_exit
    def reconcile_true_copy(self, spec: Any) -> Any:
        """
        Reconcile the TrueCopy based on the desired state in the specification.
        """
        state = self.state.lower()
        resp_data = None
        if state == StateValue.ABSENT:
            _ , comment = self.delete_true_copy(spec)
            # msg = "Truecopy pair {} has been deleted successfully.".format(result)
            return 
        elif state == StateValue.PRESENT:
            if spec.secondary_storage_serial_number is None:
                raise ValueError(VSPTrueCopyValidateMsg.SECONDARY_STORAGE_SN.value)
            if spec.secondary_pool_id is None:
                raise ValueError(VSPTrueCopyValidateMsg.SECONDARY_POOL_ID.value)
            resp_data = self.create_true_copy(spec=spec)
            
        elif state == StateValue.SPLIT:
            resp_data = self.split_true_copy(spec)
        elif state == StateValue.SYNC:
            resp_data = self.resync_true_copy(spec)
        elif state == StateValue.SWAP_SPLIT:
            resp_data = self.swap_split_true_copy(spec)
            self.connection_info.changed = True
        elif state == StateValue.SWAP_RESYNC:
            resp_data = self.swap_resync_true_copy(spec)
            self.connection_info.changed = True

        if resp_data:
            logger.writeDebug("RC:resp_data={}  state={}", resp_data, state)            

            resp_in_dict = resp_data.to_dict()

            return TrueCopyInfoExtractor(self.storage_serial_number).extract([resp_in_dict])
        else:
            return None
    
    @log_entry_exit
    def check_storage_in_ucpsystem(self) -> bool:
        """
        Check if the storage is in the UCP system.
        """
        return self.provisioner.check_storage_in_ucpsystem()

    @log_entry_exit
    def get_all_tc_pairs(self):
        tc_pairs = self.provisioner.get_all_tc_pairs(self.storage_serial_number)
        extracted_data = TrueCopyInfoExtractor(self.storage_serial_number).extract(tc_pairs)
        return extracted_data
    
    def get_true_copy_facts(self, spec=None):

        tc_pairs = self.provisioner.get_true_copy_facts(spec)
        logger.writeDebug("RC:get_true_copy_facts:tc_pairs={}", tc_pairs)
        # if spec.primary_volume_id is None:
        #     extracted_data = TrueCopyInfoExtractor(self.storage_serial_number).extract(tc_pairs.data_to_list())
        # else:
        if tc_pairs:
            extracted_data = TrueCopyInfoExtractor(self.storage_serial_number).extract(tc_pairs.data_to_list())
        else:
            extracted_data = {}
        return extracted_data
    
class TrueCopyInfoExtractor:
    def __init__(self, serial):
        self.storage_serial_number = serial
        self.common_properties = {
            # "resourceId": str,
            "consistencyGroupId": int,
            "storageId": str,
            "entitlementStatus": str,
            # "copyPaceTrackSize": int,
            "copyRate": int,
            "mirrorUnitId": int,
            "pairName": str,
            "primaryHexVolumeId": str,
            # "primaryVSMResourceGroupName": str,
            # "primaryVirtualHexVolumeId": str,
            # "primaryVirtualStorageId": str,
            # "primaryVirtualVolumeId": int,
            "primaryVolumeId": int,
            "primaryVolumeStorageId": int,
            "secondaryHexVolumeId": str,
            # "secondaryVSMResourceGroupName": str,
            # "secondaryVirtualStorageId": str,
            # "secondaryVirtualVolumeId": int,
            "secondaryVolumeId": int,
            "secondaryVolumeStorageId": int,
            "status": str,
            "svolAccessMode": str,
            "type": str,
            # "secondaryVirtualHexVolumeId": int,
            "partnerId": str,
            "subscriberId": str,
        }

    def fix_bad_camel_to_snake_conversion(self, key):
        new_key = key.replace("v_s_m", "vsm")
        return new_key

    @log_entry_exit  
    def extract(self, responses):
        new_items = []
        for response in responses:
            new_dict = {"storage_serial_number": self.storage_serial_number}
            for key, value_type in self.common_properties.items():
                # Get the corresponding key from the response or its mapped key
                response_key = response.get(key)
                # Assign the value based on the response key and its data type
                cased_key = camel_to_snake_case(key)
                if "v_s_m" in cased_key:
                    cased_key = self.fix_bad_camel_to_snake_conversion(cased_key)
                if response_key is not None:
                    new_dict[cased_key] = value_type(response_key)
                else:
                    # Handle missing keys by assigning default values
                    default_value = (
                        "" if value_type == str else -1 if value_type == int else False
                    )
            new_dict["partner_id"] = "apiadmin"
            if new_dict.get("primary_hex_volume_id") == "" or new_dict.get("primary_hex_volume_id") == None:
                new_dict["primary_hex_volume_id"] = volume_id_to_hex_format(new_dict.get("primary_volume_id"))
            if new_dict.get("secondary_hex_volume_id") == "" or new_dict.get("secondary_hex_volume_id") == None :
                new_dict["secondary_hex_volume_id"] = volume_id_to_hex_format(new_dict.get("secondary_volume_id"))
            new_items.append(new_dict)
        
        return new_items

    @log_entry_exit
    def extract_dict(self, response):
        new_dict = {"storage_serial_number": self.storage_serial_number}
        for key, value_type in self.common_properties.items():
            # Get the corresponding key from the response or its mapped key
            response_key = response.get(key)
            # Assign the value based on the response key and its data type
            cased_key = camel_to_snake_case(key)
            if "v_s_m" in cased_key:
                cased_key = self.fix_bad_camel_to_snake_conversion(cased_key)
            if response_key is not None:
                new_dict[cased_key] = value_type(response_key)
            else:
                # Handle missing keys by assigning default values
                default_value = (
                    "" if value_type == str else -1 if value_type == int else False
                )
                new_dict[cased_key] = default_value
        new_dict["partner_id"] = "apiadmin"
        if new_dict.get("primary_hex_volume_id") == "" or new_dict.get("primary_hex_volume_id") == None:
            new_dict["primary_hex_volume_id"] = volume_id_to_hex_format(new_dict.get("primary_volume_id"))
        if new_dict.get("secondary_hex_volume_id") == "" or new_dict.get("secondary_hex_volume_id") == None :
            new_dict["secondary_hex_volume_id"] = volume_id_to_hex_format(new_dict.get("secondary_volume_id")) 
    
        return new_dict
    
