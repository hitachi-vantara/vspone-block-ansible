try:
    from ..common.ansible_common import (
        log_entry_exit,
        snake_to_camel_case,
        get_response_key,
    )
    from ..common.hv_log import Log
    from ..common.hv_constants import *
    from ..provisioner.vsp_storage_pool_provisioner import VSPStoragePoolProvisioner
    from ..model.vsp_storage_pool_models import *
except ImportError:
    from common.ansible_common import (
        log_entry_exit,
        snake_to_camel_case,
        get_response_key,
    )
    from common.hv_log import Log
    from common.hv_constants import *
    from provisioner.vsp_storage_pool_provisioner import VSPStoragePoolProvisioner
    from model.vsp_storage_pool_models import *


class VSPStoragePoolReconciler:

    def __init__(self, connectionInfo):
        self.connectionInfo = connectionInfo
        self.provisioner = VSPStoragePoolProvisioner(self.connectionInfo)
        # self._validate_parameters()

    @log_entry_exit
    def get_all_storage_pools(self):
        return self.provisioner.get_all_storage_pools()

    @log_entry_exit
    def get_storage_pool(self, pool_fact_spec):
        return self.provisioner.get_storage_pool(pool_fact_spec)


class VSPStoragePoolCommonPropertiesExtractor:
    def __init__(self):
        self.common_properties = {
            "pool_id": int,
            "pool_name": str,
            "depletion_threshold_rate": int,
            "free_capacity": int,
            "free_capacity_in_units": str,
            "replication_data_released_rate": int,
            "replication_depletion_alert_rate": int,
            "replication_usage_rate": int,
            "resource_group_id": int,
            "status": str,
            "subscription_limit_rate": int,
            "total_capacity": int,
            "total_capacity_in_unit": str,
            "pool_type": str,
            "utilization_rate": int,
            "virtual_volume_count": int,
            "warning_threshold_rate": int,
            "subscription_rate": int,
            "subscription_warning_rate": int,
            "deduplication_enabled": bool,
            "ldev_ids": list,
            "dp_volumes": list,
        }

    @log_entry_exit
    def extract_pool(self, response):
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
                elif key == "dp_volumes":
                    common_dp_vol_properties = {"logical_unit_id": int, "size": str}
                    new_dict[key] = self.extract(response_key, common_dp_vol_properties)
                else:
                    new_dict[key] = value_type(response_key)
            else:
                # Handle for case of None response_key or missing keys by assigning default values
                default_value = (
                    "" if value_type == str else -1 if value_type == int else False
                )
                new_dict[key] = default_value
        return new_dict

    @log_entry_exit
    def extract_all_pools(self, responses):
        new_items = []
        for response in responses:
            new_dict = self.extract_pool(response)
            new_items.append(new_dict)
        return new_items

    @log_entry_exit
    def extract(self, responses, common_properties):
        new_items = []
        for response in responses:
            new_dict = {}
            for key, value_type in common_properties.items():
                cased_key = snake_to_camel_case(key)
                # Get the corresponding key from the response or its mapped key
                response_key = get_response_key(response, cased_key, key)

                # Assign the value based on the response key and its data type
                if response_key is not None:
                    new_dict[key] = value_type(response_key)
                else:
                    # Handle for case of None response_key or missing keys by assigning default values
                    default_value = (
                        "" if value_type == str else -1 if value_type == int else False
                    )
                    new_dict[key] = default_value
            new_items.append(new_dict)
        return new_items
