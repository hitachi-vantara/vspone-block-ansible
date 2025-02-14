try:
    from ..provisioner.uaig_subscriber_provisioner import SubscriberProvisioner
    from ..common.ansible_common import (
        camel_to_snake_case,
        snake_to_camel_case,
        camel_array_to_snake_case,
        get_default_value,
    )
except ImportError:
    from provisioner.uaig_subscriber_provisioner import SubscriberProvisioner
    from common.ansible_common import (
        camel_to_snake_case,
        snake_to_camel_case,
        camel_array_to_snake_case,
        get_default_value,
    )


class SubscriberReconciler:

    def __init__(self, connectionInfo, subscriberSpec=None):
        self.connectionInfo = connectionInfo
        self.subscriberSpec = subscriberSpec
        self.provisioner = SubscriberProvisioner(self.connectionInfo)

    def get_subscriber_facts(self, getSubscriberSpec):
        if getSubscriberSpec is None:
            data = self.provisioner.get_subscriber_facts(None)
        else:
            data = self.provisioner.get_subscriber_facts(
                getSubscriberSpec.subscriber_id
            )
        if data:
            if getSubscriberSpec is None or not getSubscriberSpec.subscriber_id:
                return SubscriberPropertiesExtractor().extract(data)
            else:
                return SubscriberPropertiesExtractor().extractValue(data)
        return data

    def create_subscriber(self, createSubscriberSpec):
        data = self.provisioner.create_subscriber(
            SubscriberPropertiesExtractor().extractRequestIntoCamelCase(
                createSubscriberSpec, None
            )
        )
        return SubscriberPropertiesExtractor().extractValue(data)[0]

    def update_subscriber(self, updateSubscriberSpec, existing_subscriber):
        data = self.provisioner.update_subscriber(
            SubscriberPropertiesExtractor().extractRequestIntoCamelCase(
                updateSubscriberSpec, existing_subscriber
            )
        )
        return SubscriberPropertiesExtractor().extractValue(data)[0]

    def delete_subscriber(self, deleteSubscriberSpec):
        return self.provisioner.delete_subscriber(deleteSubscriberSpec.subscriber_id)


class SubscriberPropertiesExtractor:
    def __init__(self):
        self.common_properties = {
            "name": str,
            "subscriberId": str,
            "partnerId": str,
            "type": str,
            "time": int,
            "softLimit": str,
            "hardLimit": str,
            "usedQuota": str,
            "quotaLimit": str,
            "usedQuotaInPercent": float,
            "state": str,
            "message": str,
        }

        self.parameter_mapping = {
            "softLimit": "softLimitInPercent",
            "hardLimit": "hardLimitInPercent",
            "quotaLimit": "quotaLimitInGb",
            "usedQuota": "usedQuotaInGb",
        }

    def extractValue(self, response):
        new_items = []
        new_dict = {}
        for key, value_type in self.common_properties.items():
            # Get the corresponding key from the response or its mapped key
            if not isinstance(response, list):
                response_key = response.get(key)

                if response_key is not None:
                    if key in self.parameter_mapping:
                        key = self.parameter_mapping[key]
                    key = camel_to_snake_case(key)
                    new_dict[key] = value_type(response_key)
                else:
                    # Handle missing keys by assigning default values
                    default_value = get_default_value(value_type)
                    if key in self.parameter_mapping:
                        key = self.parameter_mapping[key]
                    key = camel_to_snake_case(key)
                    if key == "used_quota_in_percent":
                        new_dict[key] = 0
                    elif key == "used_quota_in_gb":
                        new_dict[key] = "0"
                    else:
                        new_dict[key] = default_value
        new_items.append(new_dict)
        new_items = camel_array_to_snake_case(new_items)

        return new_items

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
                    new_dict[key] = value_type(response_key)
                else:
                    # Handle missing keys by assigning default values
                    default_value = get_default_value(value_type)
                    if key in self.parameter_mapping:
                        key = self.parameter_mapping[key]
                    key = camel_to_snake_case(key)
                    if key == "used_quota_in_percent":
                        new_dict[key] = 0
                    elif key == "used_quota_in_gb":
                        new_dict[key] = "0"
                    else:
                        new_dict[key] = default_value
            new_items.append(new_dict)
        new_items = camel_array_to_snake_case(new_items)
        return new_items

    def extractRequestIntoCamelCase(self, request, existing_item):
        new_dict = {}
        if existing_item is None:
            for key, value_type in request.__dict__.items():

                # Assign the value based on the response key and its data type
                if value_type is not None:
                    new_key = snake_to_camel_case(key)
                    new_dict[new_key] = value_type
            return new_dict
        else:
            new_dict["name"] = existing_item["name"]
            if existing_item.get("soft_limit_in_percent"):
                new_dict["softLimit"] = existing_item["soft_limit_in_percent"]
            if existing_item.get("hard_limit_in_percent"):
                new_dict["hardLimit"] = existing_item["hard_limit_in_percent"]
            new_dict["quotaLimit"] = existing_item["quota_limit_in_gb"]
            for key, value_type in request.__dict__.items():

                # Assign the value based on the response key and its data type
                new_key = snake_to_camel_case(key)
                if value_type is not None:
                    new_dict[new_key] = value_type
            return new_dict
