try:
    from ..common.hv_constants import Http
    from ..common.sdsb_constants import ModuleArgs
    from ..model.uaig_subscriber_models import SubscriberFactSpec, SubscriberSpec
    from ..model.uaig_password_model import PasswordSpec
    from ..model.common_base_models import (
        ConnectionInfo,
        StorageSystemInfo,
        TenantInfo,
    )
    from ..common.ansible_common import camel_to_snake_case
    from ..message.gateway_msgs import GatewayValidationMsg
except ImportError:
    from model.common_base_models import (
        ConnectionInfo,
        StorageSystemInfo,
        TenantInfo,
    )
    from model.uaig_subscriber_models import SubscriberFactSpec, SubscriberSpec
    from model.uaig_password_model import PasswordSpec
    from common.ansible_common import camel_to_snake_case
    from message.gateway_msgs import GatewayValidationMsg


import hashlib


class UAIGCommonParameters:

    @staticmethod
    def storage_system_info():
        return {
            "required": True,
            "type": "dict",
            "description": "Information about the storage system.",
            "options": {
                "serial": {
                    "required": True,
                    "type": "str",
                    "description": "The serial number of the storage system.",
                }
            },
        }

    @staticmethod
    def task_level():
        return {
            "required": True,
            "type": "dict",
            "description": "State of the task.",
            "options": {
                "state": {
                    "required": False,
                    "type": "str",
                    "choices": ["present", "absent"],
                    "default": "present",
                }
            },
        }

    @staticmethod
    def connection_info():
        return {
            "required": True,
            "type": "dict",
            "description": "Information for establishing the connection.",
            "options": {
                "address": {
                    "required": True,
                    "type": "str",
                    "description": "The management address of the storage system.",
                },
                "username": {
                    "required": False,
                    "type": "str",
                    "description": "The username for authentication.",
                },
                "password": {
                    "required": False,
                    "type": "str",
                    "description": "The password or authentication key.",
                },
                "api_token": {
                    "required": False,
                    "type": "str",
                    "description": "The api token for the connection.",
                },
                "subscriber_id": {
                    "required": False,
                    "type": "str",
                    "description": "The subscriber ID.",
                },
                "connection_type": {
                    "required": False,
                    "type": "str",
                    "description": "The type of connection.",
                    "choices": ["gateway", "direct"],
                    "default": "direct",
                },
            },
        }

    @staticmethod
    def tenant_info():
        return {
            "required": False,
            "type": "dict",
            "description": "Tenant Information",
            "options": {
                "partnerId": {
                    "required": False,
                    "type": "str",
                    "description": "Partner Id.",
                },
                "subscriberId": {
                    "required": False,
                    "type": "str",
                    "description": "Subscriber Id.",
                },
            },
        }


class UAIGParametersManager:

    def __init__(self, params):
        self.params = params
        self.storage_system_info = StorageSystemInfo(
            **self.params.get("storage_system_info", {})
        )
        self.connection_info = ConnectionInfo(**self.params.get("connection_info", {}))
        self.spec = None


    def _validate_parameters(self):
        pass


class GatewayArguments:

    common_arguments = {
        "connection_info": UAIGCommonParameters.connection_info(),
        "spec": {
            "required": False,
            "type": "dict",
            "description": "Specifications for the task.",
            "options": {},
        },
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present", "absent"],
            "default": "present",
        },
    }

    @classmethod
    def get_subscriber_fact(cls):
        spec_options = {
            "subscriber_id": {
                "required": False,
                "type": "str",
                "description": "The ID of the subscriber to get information for.",
            },
        }

        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments

    @classmethod
    def gateway_subscriber(cls):
        spec_options = {
            "subscriber_id": {
                "required": True,
                "type": "str",
                "description": "The ID of the new subscriber to be created.",
            },
            "name": {
                "required": False,
                "type": "str",
                "description": "The name of the new subscriber to be created.",
            },
            "soft_limit": {
                "required": False,
                "type": "str",
                "description": "Limit in %.",
            },
            "hard_limit": {
                "required": False,
                "type": "str",
                "description": "Limit in %.",
            },
            "quota_limit": {
                "required": False,
                "type": "str",
                "description": "Capacity in GB",
            },
            "description": {
                "required": False,
                "type": "str",
                "description": "Description about subscriber.",
            },
        }

        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments

    @classmethod
    def gateway_password(cls):
        gw_arguments = {
            "connection_info": {
                "required": True,
                "type": "dict",
                "options": {},
            },
            "spec": {
                "required": False,
                "type": "dict",
                "description": "Specifications for the task.",
                "options": {},
            },
        }
        connection_option = {
            "uai_gateway_address": {
                "required": True,
                "type": "str",
                "description": "The UAI gateway address of the storage system.",
            },
            "api_token": {
                "required": True,
                "type": "str",
                "description": "The api token for the connection.",
            },
        }
        spec_options = {
            "password": {
                "required": True,
                "type": "str",
                "description": "The new password value to be updated.",
            },
        }
        gw_arguments["connection_info"]["options"] = connection_option
        gw_arguments["spec"]["options"] = spec_options
        return gw_arguments


class GatewayParametersManager:

    def __init__(self, params):
        self.params = params
        self.connection_info = ConnectionInfo(**self.params.get("connection_info", {}))
        self.spec = None
        self.connection_info_map = self.params["connection_info"]
        self.spec_map = self.params["spec"]
        if "tenant_info" in self.params:
            self.tenant_info = TenantInfo(**self.params.get("tenant_info", {}))
        else:
            self.tenant_info = TenantInfo()
        self.state = self.params.get("state", None)

    def get_state(self):
        return self.state

    def get_tenant_info(self):
        return self.tenant_info

    def set_subscriber_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            self.spec = SubscriberFactSpec(self.params.get("spec", {}).get("subscriber_id"))
        else:
            self.spec = SubscriberFactSpec()

    def set_subscriber_spec(self, state):
        input_spec = SubscriberSpec(**self.params.get("spec", {}))
        GatewaySpecValidators().validate_subscriber(state, input_spec)
        return input_spec

    def set_admin_password_spec(self):
        input_spec = PasswordSpec(**self.params.get("spec", {}))
        return input_spec

    def get_connection_info(self):
        address = self.connection_info_map.get("management_address")
        username = self.connection_info_map.get("username")
        password = self.connection_info_map.get("password")
        api_token = self.connection_info_map.get("api_token")
        connection_type = self.connection_info_map.get("connection_type")
        return ConnectionInfo(address, username, password, api_token, connection_type)

    def _validate_parameters(self):
        pass


class UAIGSnapshotArguments:

    common_arguments = {
        "storage_system_info": UAIGCommonParameters.storage_system_info(),
        "connection_info": UAIGCommonParameters.connection_info(),
        "spec": {
            "required": False,
            "type": "dict",
            "description": "Specifications for the task.",
            "options": {},
        },
        "task_level": {
            "required": False,
            "type": "dict",
            "description": "state for the task.",
            "options": {},
        },
    }

    @classmethod
    def get_snapshot_fact_args(cls):
        spec_options = {
            "pvol": {
                "required": False,
                "type": "int",
                "description": "Primary Volume Id.",
            },
            "mirror_unit_id": {
                "required": False,
                "type": "int",
                "description": "Mirror Unit Id.",
            },
        }

        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments

    @classmethod
    def get_snapshot_reconcile_args(cls):
        spec_options = {
            "pvol": {
                "required": True,
                "type": "int",
            },
            "pool_id": {
                "required": False,
                "type": "int",
            },
            "allocate_consistency_group": {
                "required": False,
                "type": "bool",
            },
            "consistency_group_id": {
                "required": False,
                "type": "int",
            },
            "enable_quick_mode": {
                "required": False,
                "type": "bool",
            },
            "mirror_unit_id": {
                "required": False,
                "type": "int",
            },
        }

        task_level_options = {
            "state": {
                "required": False,
                "type": "str",
                "choices": ["present", "absent", "split", "resync", "restore"],
                "default": "present",
            }
        }

        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments["task_level"]["options"] = task_level_options
        return cls.common_arguments


def camel_to_snake_case_dict_array(items):
    new_items = []
    if items:
        for item in items:
            new_dict = camel_to_snake_case_dict(item)
            new_items.append(new_dict)
    return new_items


def camel_to_snake_case_dict(response):
    new_dict = {}
    try:
        for key in response.keys():
            cased_key = camel_to_snake_case(key)
            new_dict[cased_key] = response[key]
    except:
        pass

    return new_dict


class UAIGResourceID:

    def get_md5_hash(self, data):
        md5_hash = hashlib.md5()
        md5_hash.update(data.encode("utf-8"))
        return md5_hash.hexdigest()

    def storage_resourceId(self, storage_serial_number):
        str_for_hash = f"{storage_serial_number}"
        return f"storage-{self.get_md5_hash(str_for_hash)}"

    def ldev_resourceId(self, storage_serial_number, ldev):
        str_for_hash = f"{storage_serial_number}:{ldev}"
        return f"storagevolume-{self.get_md5_hash(str_for_hash)}"

    def snapshot_resourceId(self, storage_serial_number, pvol, mirror_unit_id):
        storage_resourceId = self.storage_resourceId(storage_serial_number)
        return f"ssp-{storage_resourceId}-{pvol}-{mirror_unit_id}"

    def localpair_resourceId(self, p_vol, s_vol, primary_storage_serial_number):
        str_for_hash = f"{p_vol}:{s_vol}:{primary_storage_serial_number}"
        return f"localpair-{self.get_md5_hash(str_for_hash)}"


class GatewaySpecValidators:

    def __init__(self):
        """TODO: will be used for common validators"""

    @staticmethod
    def validate_subscriber(state, input_spec: SubscriberSpec):

        if state == "present":
            if not input_spec.subscriber_id:
                raise ValueError(GatewayValidationMsg.SUBSCRIBER_ID_MISSING.value)
            if not input_spec.name:
                raise ValueError(GatewayValidationMsg.SUBSCRIBER_NAME_MISSING.value)
            if not input_spec.quota_limit:
                raise ValueError(GatewayValidationMsg.QUOTA_LIMIT_MISSING.value)
        if state == "present" or state == "update":
            if input_spec.name:
                if len(input_spec.name) < 3 or len(input_spec.name) > 255:
                    raise ValueError(GatewayValidationMsg.NAME_LENGTH.value)
            if input_spec.quota_limit:
                try:
                    if int(input_spec.quota_limit) < 1:
                        raise ValueError(GatewayValidationMsg.QUOTA_LIMIT.value)
                except:
                    raise ValueError(GatewayValidationMsg.QUOTA_LIMIT.value)
            if input_spec.subscriber_id:
                try:
                    if not int(input_spec.subscriber_id):
                        raise ValueError(GatewayValidationMsg.ID_NUMERIC.value)
                except:
                    raise ValueError(GatewayValidationMsg.ID_NUMERIC.value)
                if (
                        len(input_spec.subscriber_id) < 1
                        or len(input_spec.subscriber_id) > 15
                    ):
                        raise ValueError(GatewayValidationMsg.ID_LENGTH.value)
            if input_spec.soft_limit:
                try:
                    if (
                        int(input_spec.soft_limit) < 0
                        or int(input_spec.soft_limit) > 99
                    ):
                        raise ValueError(GatewayValidationMsg.SOFT_LIMIT.value)
                except:
                    raise ValueError(GatewayValidationMsg.SOFT_LIMIT.value)
            if input_spec.hard_limit:
                try:
                    if (
                        int(input_spec.hard_limit) < 1
                        or int(input_spec.hard_limit) > 100
                    ):
                        raise ValueError(GatewayValidationMsg.HARD_LIMIT.value)
                except:
                    raise ValueError(GatewayValidationMsg.HARD_LIMIT.value)
            if input_spec.soft_limit and input_spec.hard_limit:
                try:
                    if int(input_spec.hard_limit) <= int(input_spec.soft_limit):
                        raise ValueError(GatewayValidationMsg.HARD_LIMIT_GREATER.value)
                except:
                    raise ValueError(GatewayValidationMsg.HARD_LIMIT_GREATER.value)
