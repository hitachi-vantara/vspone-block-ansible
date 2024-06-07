try:
    from ..common.ansible_common import (
        log_entry_exit,
        snake_to_camel_case,
        get_response_key,
    )
    from ..common.hv_log import Log
    from ..common.hv_constants import *
    from ..provisioner.vsp_parity_group_provisioner import VSPParityGroupProvisioner
    from ..model.vsp_parity_group_models import *
except ImportError:
    from common.ansible_common import (
        log_entry_exit,
        snake_to_camel_case,
        get_response_key,
    )
    from common.hv_log import Log
    from common.hv_constants import *
    from provisioner.vsp_parity_group_provisioner import VSPParityGroupProvisioner
    from model.vsp_parity_group_models import *


class VSPParityGroupReconciler:

    def __init__(self, connectionInfo):
        self.connectionInfo = connectionInfo
        self.provisioner = VSPParityGroupProvisioner(self.connectionInfo)
        # self._validate_parameters()

    @log_entry_exit
    def get_all_parity_groups(self):
        return self.provisioner.get_all_parity_groups()

    @log_entry_exit
    def get_parity_group(self, pg_id):
        return self.provisioner.get_parity_group(pg_id)


class VSPParityGroupCommonPropertiesExtractor:
    def __init__(self):
        self.common_properties = {
            "resource_id": str,
            "parity_group_id": str,
            "free_capacity": str,
            "resource_group_id": int,
            "total_capacity": str,
            "ldev_ids": list,
            "raid_level": str,
            "drive_type": str,
            "copyback_mode": bool,
            "status": str,
            "is_pool_array_group": bool,
            "is_accelerated_compression": bool,
            "is_encryption_enabled": bool,
        }

    @log_entry_exit
    def extract_parity_group(self, response):
        new_dict = {}
        for key, value_type in self.common_properties.items():
            cased_key = snake_to_camel_case(key)
            # Get the corresponding key from the response or its mapped key
            response_key = get_response_key(response, cased_key, key)

            # Assign the value based on the response key and its data type
            if response_key is not None:
                if key == "ldev_ids":
                    tmp_ldev_ids = []
                    for ldev_id in response_key:
                        if ldev_id is None:
                            tmp_ldev_ids.append(-1)
                        else:
                            tmp_ldev_ids.append(ldev_id)
                    new_dict[key] = value_type(tmp_ldev_ids)
                else:
                    new_dict[key] = value_type(response_key)
            else:
                # Handle for case of None response_key or missing keys by assigning default values
                default_value = (
                    ""
                    if value_type == str
                    else (
                        -1 if value_type == int else [] if value_type == list else False
                    )
                )
                new_dict[key] = default_value
        return new_dict

    @log_entry_exit
    def extract_all_parity_groups(self, responses):
        new_items = []
        for response in responses:
            new_dict = self.extract_parity_group(response)
            new_items.append(new_dict)
        return new_items
