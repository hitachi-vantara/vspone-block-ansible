try:
    from ..provisioner.uaig_subscriber_resource_provisioner import (
        SubscriberResourceProvisioner,
    )
    from ..message.gateway_msgs import GatewayValidationMsg
    from ..common.ansible_common import (
        camel_to_snake_case,
        camel_array_to_snake_case,
    )
except ImportError:
    from provisioner.uaig_subscriber_resource_provisioner import (
        SubscriberResourceProvisioner,
    )
    from common.ansible_common import (
        camel_to_snake_case,
        camel_array_to_snake_case,
    )


class SubscriberResourceReconciler:

    def __init__(self, connection_info, storage_serial):
        self.connection_info = connection_info
        self.provisioner = SubscriberResourceProvisioner(self.connection_info)
        self.storage_serial = storage_serial

    def get_subscriber_resource_facts(self):

        if self.connection_info.subscriber_id is None:
            raise ValueError(
                GatewayValidationMsg.SUBSCRIBER_ID_FOR_RESOURCE_MISSING.value
            )

        data = self.provisioner.get_subscriber_resource_facts(
            self.connection_info.subscriber_id
        )
        if data:
            if self.storage_serial is not None:
                data = self.apply_filter_serial(data)
            return SubscriberResourcePropertiesExtractor().extract(data)

        return []

    def apply_filter_serial(self, data):
        new_data = []
        for x in data:
            if x["deviceId"] == self.storage_serial:
                new_data.append(x)
        return new_data


class SubscriberResourcePropertiesExtractor:
    def __init__(self):
        self.common_properties = {
            "deviceId": str,
            # "resourceId": str,
            # "partnerId": str,
            # "subscriberId": str,
            "type": str,
            "resourceValue": str,
            # "time": int,
            "totalCapacity": int,
        }

        self.parameter_mapping = {
            "deviceId": "storageSerial",
            # "hardLimit": "hardLimitInPercent",
            # "quotaLimit": "quotaLimitInGb",
            # "usedQuota": "usedQuotaInGb",
        }

        self.size = ["total_capacity"]

    def extract(self, responses):
        new_items = []
        for response in responses:
            new_dict = {}
            for key, value_type in self.common_properties.items():
                # Get the corresponding key from the response or its mapped key
                response_key = response.get(key)

                if response_key is not None:
                    if key in self.parameter_mapping:
                        key = self.parameter_mapping[key]

                    key = camel_to_snake_case(key)
                    if key in self.size:
                        response_key = self.convert_capacity_to_gb(response_key)
                        new_dict[key] = response_key
                    else:
                        new_dict[key] = value_type(response_key)
                # else:
                # Handle missing keys by assigning default values
                # default_value = get_default_value(value_type)
                # if key in self.parameter_mapping:
                #     key = self.parameter_mapping[key]
                # key = camel_to_snake_case(key)
                # if key == "used_quota_in_percent":
                #     new_dict[key] = 0
                # elif key == "used_quota_in_gb":
                #     new_dict[key] = "0"
                # else:
                #     new_dict[key] = default_value
            new_items.append(new_dict)
        new_items = camel_array_to_snake_case(new_items)
        return new_items

    def convert_capacity_to_gb(self, size):
        size /= 1024 * 1024 * 1024
        return f"{size:.2f}GB"
