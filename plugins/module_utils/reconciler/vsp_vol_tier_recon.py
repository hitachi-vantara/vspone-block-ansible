from typing import Optional, List, Dict, Any
try:
    from ..common.ansible_common import (
        log_entry_exit,
        camel_to_snake_case,
        get_response_key,
    )
    from ..common.hv_log import Log
    from ..common.hv_constants import *
    from ..provisioner.vsp_vol_tier_provisioner import VSPVolTierProvisioner
    from ..message.vsp_hur_msgs import VSPHurValidateMsg
    from ..model.vsp_hur_models import HurSpec


except ImportError:
    from common.ansible_common import (
        log_entry_exit,
        camel_to_snake_case,
        get_response_key,
    )
    from common.hv_log import Log
    from common.hv_constants import *
    from provisioner.vsp_vol_tier_provisioner import VSPVolTierProvisioner
    from message.vsp_hur_msgs import VSPHurValidateMsg
    from model.vsp_hur_models import HurSpec

class VSPVolTierReconciler:
    def __init__(self, connection_info, serial, state):

        self.logger = Log()
        self.connectionInfo = connection_info
        self.storage_serial_number = serial
        self.provisioner = VSPVolTierProvisioner(connection_info, serial)
        self.state = state

    # 20240822 VSPVolTierReconciler
    @log_entry_exit
    def reconcile(self, spec: Any) -> Any:
        self.provisioner.apply_vol_tiering(spec)
    


    def __init__(self, serial):
        self.storage_serial_number = serial
        self.common_properties = {
            # "resourceId": str,
            "consistencyGroupId": int,
            "copyPaceTrackSize": int,
            "copyRate": int,
            "mirrorUnitId": int,
            "pairName": str,
            "primaryHexVolumeId": str,
            "primaryVSMResourceGroupName": str,
            "primaryVirtualHexVolumeId": str,
            "primaryVirtualStorageId": str,
            "primaryVirtualVolumeId": int,
            "primaryVolumeId": int,
            "primaryVolumeStorageId": int,
            "secondaryHexVolumeId": str,
            "secondaryVSMResourceGroupName": str,
            "secondaryVirtualStorageId": str,
            "secondaryVirtualVolumeId": int,
            "secondaryVolumeId": int,
            "secondaryVolumeStorageId": int,
            "status": str,
            "svolAccessMode": str,
            "type": str,
            "secondaryVirtualHexVolumeId": int,
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
                new_dict["partner_id"] = "apiadmin"
                new_dict[cased_key] = default_value
        return new_dict    