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
    from ..provisioner.vsp_hur_provisioner import VSPHurProvisioner
    from ..message.vsp_hur_msgs import VSPHurValidateMsg
    from ..model.vsp_hur_models import HurSpec


except ImportError:
    from common.ansible_common import (
        log_entry_exit,
        camel_to_snake_case,
        get_response_key,
        volume_id_to_hex_format,
    )
    from common.hv_log import Log
    from common.hv_constants import *
    from provisioner.vsp_hur_provisioner import VSPHurProvisioner
    from message.vsp_hur_msgs import VSPHurValidateMsg
    from model.vsp_hur_models import HurSpec


logger = Log()

class VSPHurReconciler:
    def __init__(self, connection_info, serial, state):

        self.logger = Log()
        self.connectionInfo = connection_info
        self.storage_serial_number = serial
        self.provisioner = VSPHurProvisioner(connection_info, serial)
        self.state = state

    # 20240808 hur operations reconciler
    @log_entry_exit
    def delete_hur(self, spec):
        if spec.primary_volume_id is None:
            raise ValueError(VSPHurValidateMsg.PRIMARY_VOLUME_ID.value)
        if spec.mirror_unit_id is None:
            raise ValueError(VSPHurValidateMsg.MIRROR_UNIT_ID.value)
        return self.provisioner.delete_hur_pair(spec.primary_volume_id, spec.mirror_unit_id)
    @log_entry_exit
    def resync_hur(self, spec):
        if spec.primary_volume_id is None:
            raise ValueError(VSPHurValidateMsg.PRIMARY_VOLUME_ID.value)
        if spec.mirror_unit_id is None:
            raise ValueError(VSPHurValidateMsg.MIRROR_UNIT_ID.value)
        return self.provisioner.resync_hur_pair(spec.primary_volume_id, spec.mirror_unit_id)

    @log_entry_exit
    def split_hur(self, spec):
        if spec.primary_volume_id is None:
            raise ValueError(VSPHurValidateMsg.PRIMARY_VOLUME_ID.value)
        if spec.mirror_unit_id is None:
            raise ValueError(VSPHurValidateMsg.MIRROR_UNIT_ID.value)
        return self.provisioner.split_hur_pair(spec.primary_volume_id, spec.mirror_unit_id)

    @log_entry_exit
    def swap_split_hur(self, spec):
        if spec.primary_volume_id is None:
            raise ValueError(VSPHurValidateMsg.PRIMARY_VOLUME_ID.value)
        return self.provisioner.swap_split_hur_pair(spec.primary_volume_id)

    @log_entry_exit
    def swap_resync_hur(self, spec):
        if spec.primary_volume_id is None:
            raise ValueError(VSPHurValidateMsg.PRIMARY_VOLUME_ID.value)
        return self.provisioner.swap_resync_hur_pair(spec.primary_volume_id)

    @log_entry_exit
    def create_hur(self, spec):
        logger.writeDebug("RC:create_hur:spec={} ", spec)
        if spec.primary_volume_id is None:
            raise ValueError(VSPHurValidateMsg.PRIMARY_VOLUME_ID.value)
        if spec.secondary_hostgroups is None:
            raise ValueError(VSPHurValidateMsg.SECONDARY_HOSTGROUPS.value)
        
        pvol = self.provisioner.get_volume_by_id(spec.primary_volume_id)
        logger.writeDebug("RC:create_hur:pvol={} ", pvol)
        if not pvol:
            raise ValueError(VSPHurValidateMsg.PRIMARY_VOLUME_ID_DOES_NOT_EXIST.value.format(spec.primary_volume_id))

        # Does HUR need pvol attached to a hg, if yes, uncomment it    
        pvol_v2 = self.provisioner.get_volume_by_id_v2(pvol.storageId, pvol.resourceId)
        if pvol_v2.pathCount < 1:
            raise ValueError(VSPHurValidateMsg.PRIMARY_VOLUME_ID_NO_PATH.value.format(spec.primary_volume_id))

        
        return self.provisioner.create_hur(spec=spec)
    
    @log_entry_exit
    def reconcile_hur(self, spec: Any) -> Any:
        """
        Reconcile the HUR based on the desired state in the specification.
        """
        comment = None
        state = self.state.lower()
        resp_data = None
        if state == StateValue.ABSENT:
            # 20240905 comment
            result, comment = self.delete_hur(spec)
            # 20240912 we don't need the result
            result = ""
            return comment, result
        elif state == StateValue.PRESENT:
            resp_data = self.create_hur(spec=spec)
            self.logger.writeDebug("RC:resp_data={}", resp_data)
        elif state == StateValue.SPLIT:
            resp_data, comment = self.split_hur(spec)
        elif state == StateValue.RE_SYNC:
            resp_data, comment = self.resync_hur(spec)
        elif state == StateValue.SWAP_SPLIT:
            return self.swap_split_hur(spec)
        elif state == StateValue.SWAP_RESYNC:
            resp_data = self.swap_resync_hur(spec)

        if resp_data:
            # 20240905 no such self.logger.writeDebug("(self.connection_info={}",self.connection_info)
            self.logger.writeDebug("resp_data={}",resp_data)
            resp_in_dict = resp_data.to_dict()
            self.logger.writeDebug("resp_in_dict={}",resp_in_dict)
            return comment, HurInfoExtractor(
                self.storage_serial_number
            ).extract([resp_in_dict])[0]
        else:
            return "Data is not available yet.", None
    
    @log_entry_exit
    def check_storage_in_ucpsystem(self) -> bool:
        """
        Check if the storage is in the UCP system.
        """
        return self.provisioner.check_storage_in_ucpsystem()

    ## for testing only
    @log_entry_exit
    def get_all_hurpairs(self):
        
        result = self.provisioner.get_all_hurpairs(self.storage_serial_number)
        
        if True: 
            ##info and len([info]) > 0 :
            result2 = HurInfoExtractor(
                self.storage_serial_number
            ).extract(result)
        
        return result2
    
    @log_entry_exit
    def get_hur_facts(self, spec=None):

        ## 20240812 rec.get_hur_facts
        tc_pairs = self.provisioner.get_hur_facts_ext(
            pvol=spec.primary_volume_id, svol=spec.secondary_volume_id, mirror_unit_id=spec.mirror_unit_id
            )
        self.logger.writeDebug("RC:get_hur_facts:tc_pairs={}", tc_pairs)
        if tc_pairs is None:
            return []
        
        ## 20240812
        if False: ##spec.primary_volume_id is None:
            # extracted_data = HurInfoExtractor(self.storage_serial_number).extract(tc_pairs.data_to_list())
            extracted_data = HurInfoExtractor(self.storage_serial_number).extract(tc_pairs)
        else:
            # 20240812 - one pvol can have 3 pairs
            result = []
            for pair in tc_pairs:
                extracted_data = HurInfoExtractor(self.storage_serial_number).extract_dict(pair.to_dict())
                result.append(extracted_data)
            extracted_data = result
                
        return extracted_data
        
class HurInfoExtractor:
    def __init__(self, serial):
        self.storage_serial_number = serial
        self.common_properties = {
            # "resourceId": str,
            "consistencyGroupId": int,
            # "copyPaceTrackSize": int,
            "fenceLevel": str,
            "copyRate": int,
            "mirrorUnitId": int,
            # "pairName": str,
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
            "entitlementStatus": str,
            "partnerId": str,
            "subscriberId": str,
        }

    @log_entry_exit
    def extract(self, responses):
        new_items = []
        for response in responses:
            new_dict = {
                "storage_serial_number": self.storage_serial_number,
                }
            for key, value_type in self.common_properties.items():
                # Get the corresponding key from the response or its mapped key
                response_key = response.get(key)
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

            new_dict["partner_id"] = "apiadmin"
            if new_dict.get("primary_hex_volume_id") == "":
                new_dict["primary_hex_volume_id"] = volume_id_to_hex_format(new_dict.get("primary_volume_id"))
            if new_dict.get("secondary_hex_volume_id") == "":
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
            if response_key is not None:
                new_dict[cased_key] = value_type(response_key)
            else:
                # Handle missing keys by assigning default values
                default_value = (
                    "" if value_type == str else -1 if value_type == int else False
                )
                new_dict[cased_key] = default_value
            
        new_dict["partner_id"] = "apiadmin"
        if new_dict.get("primary_hex_volume_id") == "":
            new_dict["primary_hex_volume_id"] = volume_id_to_hex_format(new_dict.get("primary_volume_id"))
        if new_dict.get("secondary_hex_volume_id") == "":
            new_dict["secondary_hex_volume_id"] = volume_id_to_hex_format(new_dict.get("secondary_volume_id"))
        
        return new_dict
