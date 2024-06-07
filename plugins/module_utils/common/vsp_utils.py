try:
    from ..common.hv_log import (
        Log,
    )
    from ..model.common_base_models import (
        ConnectionInfo,
        StorageSystemInfo,
        TenantInfo,
    )
    from ..model.vsp_volume_models import VolumeFactSpec, CreateVolumeSpec
    from ..model.vsp_host_group_models import GetHostGroupSpec, HostGroupSpec
    from ..model.vsp_shadow_image_pair_models import (
        GetShadowImageSpec,
        ShadowImagePairSpec,
    )
    from ..model.vsp_iscsi_target_models import IscsiTargetFactSpec, IscsiTargetSpec
    from ..model.vsp_storage_system_models import StorageSystemFactSpec
    from ..model.vsp_snapshot_models import SnapshotFactSpec, SnapshotReconcileSpec
    from ..model.vsp_storage_pool_models import PoolFactSpec
    from ..model.vsp_parity_group_models import ParityGroupFactSpec
    from ..common.hv_constants import ConnectionTypes, StateValue
    from ..common.vsp_constants import AutomationConstants
    from ..common.ansible_common import camel_to_snake_case
    from ..message.vsp_lun_msgs import VSPVolValidationMsg
    from ..message.vsp_snapshot_msgs import VSPSnapShotValidateMsg
    from ..message.vsp_parity_group_msgs import VSPParityGroupValidateMsg
    from ..message.vsp_storage_pool_msgs import VSPStoragePoolValidateMsg
    from ..message.vsp_iscsi_target_msgs import VSPIscsiTargetValidationMsg
    from ..message.vsp_host_group_msgs import VSPHostGroupValidationMsg
    from ..message.common_msgs import CommonMessage
    from ..message.vsp_shadow_image_pair_msgs import VSPShadowImagePairValidateMsg
except ImportError:
    from model.common_base_models import (
        ConnectionInfo,
        StorageSystemInfo,
        TenantInfo,
    )
    from model.vsp_volume_models import VolumeFactSpec, CreateVolumeSpec
    from model.vsp_host_group_models import GetHostGroupSpec, HostGroupSpec
    from model.vsp_shadow_image_pair_models import (
        GetShadowImageSpec,
        ShadowImagePairSpec,
    )
    from model.vsp_iscsi_target_models import IscsiTargetFactSpec, IscsiTargetSpec
    from model.vsp_snapshot_models import SnapshotFactSpec, SnapshotReconcileSpec
    from model.vsp_storage_system_models import StorageSystemFactSpec
    from model.vsp_storage_pool_models import PoolFactSpec
    from model.vsp_parity_group_models import ParityGroupFactSpec
    from common.hv_constants import ConnectionTypes, StateValue
    from common.ansible_common import camel_to_snake_case
    from message.vsp_lun_msgs import VSPVolValidationMsg
    from message.common_msgs import CommonMessage
    from common.vsp_constants import AutomationConstants
    from message.vsp_snapshot_msgs import VSPSnapShotValidateMsg
    from message.vsp_parity_group_msgs import VSPParityGroupValidateMsg
    from message.vsp_storage_pool_msgs import VSPStoragePoolValidateMsg
    from message.vsp_shadow_image_pair_msgs import VSPShadowImagePairValidateMsg
    from message.vsp_iscsi_target_msgs import VSPIscsiTargetValidationMsg
    from message.vsp_host_group_msgs import VSPHostGroupValidationMsg
    from common.hv_log import Log


#########################################################
### VSP Parameter manager ###
class VSPParametersManager:

    def __init__(self, params):
        self.params = params
        if (
            "storage_system_info" in self.params
            and self.params.get("storage_system_info") is not None
        ):
            self.storage_system_info = StorageSystemInfo(
                **self.params.get("storage_system_info", {"serial": None})
            )
        else:
            self.storage_system_info = StorageSystemInfo(**{"serial": None})
            if (
                self.params.get("connection_info").get("connection_type")
                == ConnectionTypes.GATEWAY
            ):
                raise ValueError(CommonMessage.STORAGE_SYSTEM_INFO_MISSING.value)

        self.connection_info = ConnectionInfo(**self.params.get("connection_info", {}))
        self.state = self.params.get("state", None)

        if "tenant_info" in self.params:
            self.tenant_info = TenantInfo(**self.params.get("tenant_info", {}))
        else:
            self.tenant_info = TenantInfo()

        VSPSpecValidators.validate_connection_info(self.connection_info)

    def get_state(self):
        return self.state

    def get_connection_info(self):
        return self.connection_info

    def get_serial(self):
        return self.storage_system_info.serial

    def get_tenant_info(self):
        return self.tenant_info

    def set_volume_fact_spec(self):

        input_spec = VolumeFactSpec(
            **self.params["spec"] if self.params["spec"] else {}
        )
        VSPSpecValidators().validate_volume_facts(input_spec)
        return input_spec

    def set_volume_spec(self):
        input_spec = CreateVolumeSpec(**self.params["spec"])
        VSPSpecValidators().validate_volume_spec(self.get_state(), input_spec)
        return input_spec

    def get_host_group_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = GetHostGroupSpec(**self.params["spec"])
        else:
            input_spec = GetHostGroupSpec()
        return input_spec

    def host_group_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = HostGroupSpec(**self.params["spec"])
            VSPSpecValidators().validate_host_group_spec(input_spec)
        else:
            input_spec = HostGroupSpec()
        return input_spec

    def set_shadow_image_pair_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = GetShadowImageSpec(**self.params["spec"])             
        else:
            input_spec = GetShadowImageSpec()
        return input_spec

    def set_storage_system_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = StorageSystemFactSpec(**self.params["spec"])
        else:
            input_spec = StorageSystemFactSpec()
        return input_spec

    def set_shadow_image_pair_spec(self):
        input_spec = ShadowImagePairSpec(**self.params["spec"])
        VSPSpecValidators.validate_shadow_image_module(input_spec,self.connection_info)
        return input_spec

    def get_iscsi_target_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = IscsiTargetFactSpec(**self.params["spec"])
        else:
            input_spec = IscsiTargetFactSpec()
        return input_spec

    def get_iscsi_target_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = IscsiTargetSpec(**self.params["spec"])
            VSPSpecValidators().validate_iscsi_target_spec(input_spec)
        else:
            input_spec = IscsiTargetSpec()
        return input_spec

    def get_snapshot_fact_spec(self):
        self.spec = SnapshotFactSpec(
            **self.params["spec"] if self.params["spec"] else {}
        )
        VSPSpecValidators().validate_snapshot_fact(self.spec)
        return self.spec

    def get_snapshot_reconcile_spec(self):
        self.spec = SnapshotReconcileSpec(
            **self.params["spec"], state=self.params["state"]
        )
        VSPSpecValidators().validate_snapshot_module_fact(
            self.spec, self.connection_info
        )
        return self.spec

    def get_pool_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = PoolFactSpec(**self.params["spec"])
            VSPSpecValidators().validate_storage_pool_fact(input_spec)
        else:
            input_spec = PoolFactSpec()
        return input_spec

    def get_parity_group_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = ParityGroupFactSpec(**self.params["spec"])
            VSPSpecValidators().validate_parity_group_fact(input_spec)
        else:
            input_spec = ParityGroupFactSpec()
        return input_spec


###########################################################################
## Arguments Managements ##
class VSPCommonParameters:

    @staticmethod
    def storage_system_info():
        return {
            "required": False,
            "type": "dict",
            "description": "Information about the storage system.",
            "options": {
                "serial": {
                    "required": False,
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
            "description": "Information about the storage system.",
            "options": {
                "state": {
                    "required": False,
                    "type": "str",
                    "choices": [
                        "present",
                        "absent",
                        "split",
                        "restore",
                        "resync",
                        "query",
                    ],
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
                    "no_log": True,
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
    def state():
        return {
            "required": False,
            "type": "str",
            "choices": ["present", "absent"],
            "default": "present",
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


class VSPVolumeArguments:

    common_arguments = {
        "storage_system_info": VSPCommonParameters.storage_system_info(),
        "connection_info": VSPCommonParameters.connection_info(),
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
    def volume_fact(cls):
        spec_options = {
            "lun": {
                "required": False,
                "type": "str",
                "description": "The ID of the LUN to get information for.",
            },
            "start_ldev_id": {
                "required": False,
                "type": "int",
                "description": "The start ID of the LUN to get information for.",
            },
            "end_ldev_id": {
                "required": False,
                "type": "int",
                "description": "The end ID of the LUN to get information for.",
            },
            "count": {
                "required": False,
                "type": "int",
                "description": "The maximum count of LUNs to return.",
            },
            "name": {
                "required": False,
                "type": "str",
                "description": "The name of the LUN.",
            },
        }

        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments

    @classmethod
    def volume(cls):
        spec_options = {
            "lun": {
                "required": False,
                "type": "str",
            },
            "pool_id": {
                "required": False,
                "type": "int",
            },
            "size": {
                "required": False,
                "type": "str",
            },
            "name": {
                "required": False,
                "type": "str",
            },
            "capacity_saving": {
                "required": False,
                "type": "str",
            },
            "parity_group": {
                "required": False,
                "type": "str",
            },
        }

        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments


class VSPHostGroupArguments:

    common_arguments = {
        "storage_system_info": VSPCommonParameters.storage_system_info(),
        "connection_info": VSPCommonParameters.connection_info(),
        "state": VSPCommonParameters.state(),
        "spec": {
            "required": False,
            "type": "dict",
            "description": "Specifications for the task.",
            "options": {},
        },
    }

    @classmethod
    def host_group_facts(cls):
        spec_options = {
            "query": {
                "required": False,
                "type": "list",
                "default": [],
                "description": "Filters LUNs and WWNs.",
            },
            "name": {
                "required": False,
                "type": "str",
                "description": "The name of the host group.",
            },
            "ports": {
                "required": False,
                "type": "list",
                "description": "The port of the host group.",
            },
            "lun": {"required": False, "type": "int", "description": "LDEV ID."},
        }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments

    @classmethod
    def host_group(cls):
        cls.common_arguments["spec"]["required"] = True
        spec_options = {
            "state": {
                "required": False,
                "type": "str",
                "default": "present",
                "description": "State of the host group tasks.",
            },
            "name": {
                "required": True,
                "type": "str",
                "description": "Name of the host group.",
            },
            "port": {
                "required": True,
                "type": "str",
                "description": "Fibre Channel port.",
            },
            "host_mode": {
                "required": False,
                "type": "str",
                "description": "Host mode of the host group.",
            },
            "host_mode_options": {
                "required": False,
                "type": "list",
                "description": "Host mode options of the host group.",
            },
            "luns": {
                "required": False,
                "type": "list",
                "description": "LUN ID in decimal or HEX of the LUN that you want to present.",
            },
            "wwns": {
                "required": False,
                "type": "list",
                "description": "List of host WWNs.",
            },
            "should_delete_all_luns": {
                "required": False,
                "type": "bool",
                "description": "If the value is true, destroy the logical units that are no longer attached to any host group.",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments


class VSPShadowImagePairArguments:

    shadow_image_pair_state = VSPCommonParameters.state()
    shadow_image_pair_state["choices"].extend(["split", "sync", "restore"])

    common_arguments = {
        "storage_system_info": VSPCommonParameters.storage_system_info(),
        "connection_info": VSPCommonParameters.connection_info(),
        "state": shadow_image_pair_state,
        "spec": {
            "required": False,
            "type": "dict",
            "description": "Specifications for the task.",
            "options": {},
        },
    }

    @classmethod
    def get_all_shadow_image_pair_fact(cls):
        spec_options = {
            "pvol": {
                "required": False,
                "type": "int",
                "description": "Primary volume id",
            },
        }

        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments

    @classmethod
    def shadow_image_pair(cls):
        spec_options = {
            "pvol": {
                "required": True,
                "type": "int",
                "description": "Primary volume id",
            },
            "svol": {
                "required": True,
                "type": "int",
                "description": "Secondary volume id",
            },
            "auto_split": {
                "required": False,
                "type": "bool",
                "description": "Auto split",
            },
            "new_consistency_group": {
                "required": False,
                "type": "bool",
                "description": "New consistency group",
            },
            "consistency_group_id": {
                "required": False,
                "type": "int",
                "description": "Consistency group id",
            },
            "copy_pace_track_size": {
                "required": False,
                "type": "str",
                "description": "Copy pace track size",
            },
            "enable_quick_mode": {
                "required": False,
                "type": "bool",
                "description": "Enable quick mode",
            },
            "enable_read_write": {
                "required": False,
                "type": "bool",
                "description": "Enable read write",
            },
            "copy_pace": {
                "required": False,
                "type": "str",
                "description": "Copy pace",
            },
            "pair_id": {
                "required": False,
                "type": "str",
                "description": "Pair Id",
            },
        }

        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments


class VSPSnapshotArguments:

    snapshot_image_state = VSPCommonParameters.state()
    snapshot_image_state["choices"].extend(["split", "sync", "restore"])

    common_arguments = {
        "storage_system_info": VSPCommonParameters.storage_system_info(),
        "connection_info": VSPCommonParameters.connection_info(),
        "spec": {
            "required": False,
            "type": "dict",
            "description": "Specifications for the task.",
            "options": {},
        },
        "state": snapshot_image_state,
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
            "auto_split": {
                "required": False,
                "type": "bool",
            },
            "mirror_unit_id": {
                "required": False,
                "type": "int",
            },
            "snapshot_group_name": {
                "required": False,
                "type": "str",
            },
        }

        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments


class VSPStorageSystemArguments:

    common_arguments = {
        "storage_system_info": VSPCommonParameters.storage_system_info(),
        "connection_info": VSPCommonParameters.connection_info(),
        "spec": {
            "required": False,
            "type": "dict",
            "description": "Specifications for the task.",
            "options": {},
        },
    }

    @classmethod
    def storage_system_fact(cls):
        spec_options = {
            "query": {
                "required": False,
                "type": "list",
                "description": "List of query options.",
            },
        }

        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments


class VSPIscsiTargetArguments:

    common_arguments = {
        "storage_system_info": VSPCommonParameters.storage_system_info(),
        "connection_info": VSPCommonParameters.connection_info(),
        "state": VSPCommonParameters.state(),
        "spec": {
            "required": False,
            "type": "dict",
            "description": "Specifications for the task.",
            "options": {},
        },
    }

    @classmethod
    def iscsi_target_facts(cls):
        spec_options = {
            "ports": {
                "required": False,
                "type": "list",
                "description": "The port of the iscsi target.",
            },
            "name": {
                "required": False,
                "type": "str",
                "description": "The name of the iscsi target.",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments

    @classmethod
    def iscsi_target(cls):
        cls.common_arguments["spec"]["required"] = True
        spec_options = {
            "state": {
                "required": False,
                "type": "str",
                "default": "present",
                "description": "State of the iscsi target tasks.",
            },
            "name": {
                "required": True,
                "type": "str",
                "description": "Name of the iscsi target.",
            },
            "port": {
                "required": True,
                "type": "str",
                "description": "iSCSI port.",
            },
            "host_mode": {
                "required": False,
                "type": "str",
                "description": "Host mode of the iscsi target.",
            },
            "host_mode_options": {
                "required": False,
                "type": "list",
                "description": "Host mode options of the iscsi target.",
            },
            "luns": {
                "required": False,
                "type": "list",
                "description": "LUN ID in decimal or HEX of the LUN that you want to present.",
            },
            "iqn_initiators": {
                "required": False,
                "type": "list",
                "description": "List of host IQN initiators.",
            },
            "chap_users": {
                "required": False,
                "type": "list",
                "description": "List of CHAP users.",
            },
            "should_delete_all_luns": {
                "required": False,
                "type": "bool",
                "description": "If the value is true, destroy the logical units that are no longer attached to any iSCSI Target.",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments


class VSPStoragePoolArguments:

    common_arguments = {
        "storage_system_info": VSPCommonParameters.storage_system_info(),
        "connection_info": VSPCommonParameters.connection_info(),
        "spec": {
            "required": False,
            "type": "dict",
            "description": "Specifications for the task.",
            "options": {},
        },
    }

    @classmethod
    def storage_pool_fact(cls):
        spec_options = {
            "pool_id": {
                "required": False,
                "type": "int",
                "description": "Pool number.",
            }
        }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments


class VSPParityGroupArguments:

    common_arguments = {
        "storage_system_info": VSPCommonParameters.storage_system_info(),
        "connection_info": VSPCommonParameters.connection_info(),
        "spec": {
            "required": False,
            "type": "dict",
            "description": "Specifications for the task.",
            "options": {},
        },
    }

    @classmethod
    def parity_group_fact(cls):
        spec_options = {
            "parity_group_id": {
                "required": False,
                "type": "str",
                "description": "Parity group number.",
            }
        }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments


##############################################################
### Validator functions ###
class VSPSpecValidators:

    def __init__(self):
        """TODO: will be used for common validators"""

    @staticmethod
    def validate_connection_info(conn_info: ConnectionInfo):

        if conn_info.connection_type == ConnectionTypes.DIRECT and conn_info.api_token:
            raise ValueError(VSPVolValidationMsg.DIRECT_API_TOKEN_ERROR.value)
        elif conn_info.username and conn_info.password and conn_info.api_token:
            raise ValueError(VSPVolValidationMsg.BOTH_API_TOKEN_USER_DETAILS.value)
        elif (
            not conn_info.username
            and not conn_info.password
            and not conn_info.api_token
        ):
            raise ValueError(VSPVolValidationMsg.NOT_API_TOKEN_USER_DETAILS.value)

    @staticmethod
    def validate_volume_facts(input_spec: VolumeFactSpec):

        if input_spec.lun:
            try:
                lun_value = int(input_spec.lun)
                if lun_value <= 0 or lun_value > AutomationConstants.LDEV_ID_MAX:
                    raise ValueError(VSPVolValidationMsg.LDEV_ID_OUT_OF_RANGE.value)
            except ValueError as e:
                if "invalid literal" not in str(e):
                    # Handle the case where the input is not a valid integer format
                    raise e
                else:
                    # Handle other ValueErrors, like out-of-range checks
                    pass

        if isinstance(input_spec.start_ldev_id, int) and (
            input_spec.start_ldev_id <= 0
            or input_spec.start_ldev_id > AutomationConstants.LDEV_ID_MAX
        ):
            raise ValueError(VSPVolValidationMsg.MAX_LDEV_ID_OUT_OF_RANGE.value)

        if input_spec.count and input_spec.end_ldev_id:
            raise ValueError(VSPVolValidationMsg.END_LDEV_AND_COUNT.value)
        elif isinstance(input_spec.count, int) and input_spec.count < 0:
            raise ValueError(VSPVolValidationMsg.COUNT_VALUE.value)

        if (
            isinstance(input_spec.start_ldev_id, int)
            and isinstance(input_spec.end_ldev_id, int)
            and input_spec.end_ldev_id < input_spec.start_ldev_id
        ):
            raise ValueError(VSPVolValidationMsg.START_LDEV_LESS_END.value)

    @staticmethod
    def validate_volume_spec(state, input_spec: CreateVolumeSpec):

        if isinstance(input_spec.lun, int) and not (
            0 <= int(input_spec.lun) < AutomationConstants.LDEV_MAX_NUMBER
        ):
            raise ValueError(VSPVolValidationMsg.LDEV_ID_OUT_OF_RANGE.value)
        if state == StateValue.ABSENT:
            # 2.3 gateway defines spec.lun for one set of logics,
            # it also defines spec.luns as str (not list) for other business logics, it's a mess
            if not input_spec.lun:
                raise ValueError(VSPVolValidationMsg.LUN_REQUIRED.value)

    @staticmethod
    def validate_snapshot_fact(input_spec: SnapshotFactSpec):
        if isinstance(input_spec.pvol, int) and input_spec.pvol < 0:
            raise ValueError(VSPSnapShotValidateMsg.PVOL_VALID_RANGE.value)
        if isinstance(input_spec.mirror_unit_id, int) and (
            input_spec.mirror_unit_id < 0
            or input_spec.mirror_unit_id > AutomationConstants.LDEV_MAX_MU_NUMBER
        ):
            raise ValueError(VSPSnapShotValidateMsg.MU_VALID_RANGE.value)

        if isinstance(input_spec.mirror_unit_id, int) and not isinstance(
            input_spec.pvol, int
        ):
            raise ValueError(VSPSnapShotValidateMsg.MU_VALID_PVOL_VALUE.value)

    @staticmethod
    def validate_snapshot_module_fact(
        spec: SnapshotReconcileSpec, conn: ConnectionInfo
    ):
        if spec.state == StateValue.PRESENT:
            if (
                conn.connection_type == ConnectionTypes.DIRECT
                and not spec.snapshot_group_name
            ):
                raise ValueError(VSPSnapShotValidateMsg.SNAPSHOT_GRP_NAME.value)

        if spec.state in (
            StateValue.RESTORE,
            StateValue.SYNC,
            StateValue.ABSENT,
        ) and (not spec.pvol or not spec.mirror_unit_id):
            raise ValueError(VSPSnapShotValidateMsg.MU_PVOL_REQUIRED.value)

        if spec.state == StateValue.SPLIT:
            if not isinstance(spec.pvol, int):
                raise ValueError(VSPSnapShotValidateMsg.PVOL_REQUIRED.value)
            
            if not isinstance(spec.pool_id, int) and not isinstance(
                spec.mirror_unit_id, int
            ):
                raise ValueError(VSPSnapShotValidateMsg.POOL_ID_REQUIRED.value)
            
            if (
                conn.connection_type == ConnectionTypes.DIRECT
                and not spec.snapshot_group_name
                and not isinstance(spec.mirror_unit_id, int)
            ):
                raise ValueError(VSPSnapShotValidateMsg.SNAPSHOT_GRP_NAME_SPLIT.value)

    @staticmethod
    def validate_parity_group_fact(input_spec: ParityGroupFactSpec):
        if input_spec.parity_group_id is None:
            raise ValueError(VSPParityGroupValidateMsg.EMPTY_PARITY_GROUP_ID.value)

    @staticmethod
    def validate_storage_pool_fact(input_spec: PoolFactSpec):
        if input_spec.pool_id is None:
            raise ValueError(VSPStoragePoolValidateMsg.EMPTY_POOL_ID.value)

    @staticmethod
    def validate_shadow_image_module(
        spec: ShadowImagePairSpec, conn: ConnectionInfo
    ):
        
        if spec.copy_pace is not None:
            options = ['SLOW','MEDIUM','FAST']
            if spec.copy_pace not in  options:
                raise ValueError(VSPShadowImagePairValidateMsg.COPY_PACE_VALUE.value)
        
        if spec.copy_pace_track_size is not None:
            options = ['SLOW','MEDIUM','FAST']
            if spec.copy_pace_track_size not in  options:
                raise ValueError(VSPShadowImagePairValidateMsg.COPY_PACE_TRACK_SIZE_VALUE.value)
            
        
    @staticmethod
    def validate_iscsi_target_spec(input_spec: IscsiTargetSpec):

        if input_spec.name:
            if len(input_spec.name) < AutomationConstants.ISCSI_NAME_LEN_MIN or len(input_spec.name) > AutomationConstants.ISCSI_NAME_LEN_MAX:
                raise ValueError(VSPIscsiTargetValidationMsg.ISCSI_NAME_OUT_OF_RANGE.value)

        if input_spec.iqn_initiators:
            for iqn_initiator in input_spec.iqn_initiators:
                if len(iqn_initiator) < AutomationConstants.IQN_LEN_MIN or len(iqn_initiator) > AutomationConstants.IQN_LEN_MAX:
                    raise ValueError(VSPIscsiTargetValidationMsg.IQN_OUT_OF_RANGE.value)

        if input_spec.luns:
            for lun in input_spec.luns:
                if lun < AutomationConstants.LDEV_ID_MIN or lun > AutomationConstants.LDEV_ID_MAX:
                    raise ValueError(VSPIscsiTargetValidationMsg.LUN_OUT_OF_RANGE.value)

        if input_spec.chap_users:
            for chap_user in input_spec.chap_users:
                if chap_user.chap_user_name:
                    if len(chap_user.chap_user_name) < AutomationConstants.CHAP_USER_NAME_LEN_MIN or len(chap_user.chap_user_name) > AutomationConstants.CHAP_USER_NAME_LEN_MAX:
                        raise ValueError(VSPIscsiTargetValidationMsg.CHAP_USER_NAME_OUT_OF_RANGE.value)
                if chap_user.chap_secret:
                    if len(chap_user.chap_secret) < AutomationConstants.CHAP_SECRET_LEN_MIN or len(chap_user.chap_secret) > AutomationConstants.CHAP_SECRET_LEN_MAX:
                        raise ValueError(VSPIscsiTargetValidationMsg.CHAP_SECRET_OUT_OF_RANGE.value)

        if input_spec.port:
            if len(input_spec.port) < AutomationConstants.NAME_PARAMS_MIN or len(input_spec.port) > AutomationConstants.NAME_PARAMS_MAX:
                raise ValueError(VSPIscsiTargetValidationMsg.PORT_OUT_OF_RANGE.value)

        if input_spec.host_mode:
            if len(input_spec.host_mode) < AutomationConstants.NAME_PARAMS_MIN or len(input_spec.host_mode) > AutomationConstants.NAME_PARAMS_MAX:
                raise ValueError(VSPIscsiTargetValidationMsg.HOST_MODE_OUT_OF_RANGE.value)

    @staticmethod
    def validate_host_group_spec(input_spec: HostGroupSpec):
        
        logger = Log()

        if input_spec.name:
            if len(input_spec.name) < AutomationConstants.HG_NAME_LEN_MIN or len(input_spec.name) > AutomationConstants.HG_NAME_LEN_MAX:
                raise ValueError(VSPHostGroupValidationMsg.HG_NAME_OUT_OF_RANGE.value)

        if input_spec.luns:
            for lun in input_spec.luns:
                logger.writeDebug('1000 lun={}',lun)
                # 2.4 MT - for composite playbook, gateway returns a str, direct returns a int
                lun = int(lun)
                if not isinstance( lun, int ) :
                    raise ValueError(VSPHostGroupValidationMsg.INVALID_PARAM_LUNS.value)
                    
                if lun < AutomationConstants.LDEV_ID_MIN or lun > AutomationConstants.LDEV_ID_MAX:
                    raise ValueError(VSPHostGroupValidationMsg.LUN_OUT_OF_RANGE.value)

        if input_spec.wwns:
            for wwn in input_spec.wwns:
                if len(wwn) < AutomationConstants.NAME_PARAMS_MIN or len(wwn) > AutomationConstants.NAME_PARAMS_MAX:
                    raise ValueError(VSPHostGroupValidationMsg.WWN_OUT_OF_RANGE.value)

        if input_spec.port:
            if len(input_spec.port) < AutomationConstants.NAME_PARAMS_MIN or len(input_spec.port) > AutomationConstants.NAME_PARAMS_MAX:
                raise ValueError(VSPHostGroupValidationMsg.PORT_OUT_OF_RANGE.value)

        if input_spec.host_mode:
            if len(input_spec.host_mode) < AutomationConstants.NAME_PARAMS_MIN or len(input_spec.host_mode) > AutomationConstants.NAME_PARAMS_MAX:
                raise ValueError(VSPHostGroupValidationMsg.HOST_MODE_OUT_OF_RANGE.value)

###############################################################
## Coommon functions ###
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
