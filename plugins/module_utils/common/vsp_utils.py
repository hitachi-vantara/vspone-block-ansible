import re
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
    from ..model.vsp_snapshot_models import SnapshotFactSpec, SnapshotReconcileSpec, SnapshotGroupSpec, SnapshotGroupFactSpec
    from ..model.vsp_storage_pool_models import PoolFactSpec, StoragePoolSpec
    from ..model.vsp_parity_group_models import ParityGroupFactSpec
    from ..model.vsp_storage_port_models import PortFactSpec, ChangePortSettingSpec
    from ..model.vsp_hur_models import HurSpec, HurFactSpec
    from ..model.vsp_true_copy_models import TrueCopyFactSpec, TrueCopySpec
    from ..model.vsp_gad_pairs_models import VspGadPairSpec, GADPairFactSpec
    from ..model.vsp_nvme_models import VSPNvmeSubsystemFactSpec
    from ..model.uaig_subscriber_models import UnsubscribeSpec
    from ..common.hv_constants import ConnectionTypes, StateValue
    from ..common.vsp_constants import AutomationConstants
    from ..common.ansible_common import camel_to_snake_case, convert_to_bytes
    from ..message.vsp_lun_msgs import VSPVolValidationMsg
    from ..message.vsp_snapshot_msgs import VSPSnapShotValidateMsg
    from ..message.vsp_parity_group_msgs import VSPParityGroupValidateMsg
    from ..message.vsp_storage_pool_msgs import VSPStoragePoolValidateMsg
    from ..message.vsp_iscsi_target_msgs import VSPIscsiTargetValidationMsg
    from ..message.vsp_host_group_msgs import VSPHostGroupValidationMsg
    from ..message.vsp_true_copy_msgs import VSPTrueCopyValidateMsg
    from ..message.vsp_hur_msgs import VSPHurValidateMsg
    from ..message.common_msgs import CommonMessage
    from ..message.vsp_shadow_image_pair_msgs import VSPShadowImagePairValidateMsg
    from ..message.vsp_storage_port_msgs import VSPStoragePortValidateMsg
    from ..message.vsp_gad_pair_msgs import GADPairValidateMSG
    from ..message.gateway_msgs import GatewayValidationMsg
    from ..common.vsp_constants import BASIC_STORAGE_DETAILS


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
    from model.vsp_nvme_models import VSPNvmeSubsystemFactSpec
    from model.vsp_iscsi_target_models import IscsiTargetFactSpec, IscsiTargetSpec
    from model.vsp_snapshot_models import SnapshotFactSpec, SnapshotReconcileSpec, SnapshotGroupSpec, SnapshotGroupFactSpec
    from model.vsp_storage_system_models import StorageSystemFactSpec
    from model.vsp_storage_pool_models import PoolFactSpec, StoragePoolSpec
    from model.vsp_parity_group_models import ParityGroupFactSpec
    from model.vsp_storage_port_models import PortFactSpec, ChangePortSettingSpec
    from model.vsp_hur_models import HurSpec, HurFactSpec
    from model.vsp_true_copy_models import TrueCopyFactSpec, TrueCopySpec
    from model.vsp_gad_pairs_models import VspGadPairSpec, GADPairFactSpec
    from model.vsp_nvme_models import VSPNvmeSubsystemFactSpec
    from model.uaig_subscriber_models import UnsubscribeSpec

    from common.hv_constants import ConnectionTypes, StateValue
    from common.ansible_common import camel_to_snake_case, convert_to_bytes
    from message.vsp_lun_msgs import VSPVolValidationMsg
    from message.common_msgs import CommonMessage
    from common.vsp_constants import AutomationConstants
    from message.vsp_snapshot_msgs import VSPSnapShotValidateMsg
    from message.vsp_parity_group_msgs import VSPParityGroupValidateMsg
    from message.vsp_storage_pool_msgs import VSPStoragePoolValidateMsg
    from message.vsp_shadow_image_pair_msgs import VSPShadowImagePairValidateMsg
    from message.vsp_iscsi_target_msgs import VSPIscsiTargetValidationMsg
    from message.vsp_host_group_msgs import VSPHostGroupValidationMsg
    from message.vsp_storage_port_msgs import VSPStoragePortValidateMsg
    from message.vsp_true_copy_msgs import VSPTrueCopyValidateMsg
    from message.vsp_hur_msgs import VSPHurValidateMsg
    from message.vsp_gad_pair_msgs import GADPairValidateMSG
    from message.gateway_msgs import GatewayValidationMsg

    from common.hv_log import Log
    from common.vsp_constants import BASIC_STORAGE_DETAILS


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
        VSPSpecValidators.validate_shadow_image_module(input_spec, self.connection_info)
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
  

    def get_hur_fact_spec(self):
        self.spec = HurFactSpec(**self.params["spec"] if self.params["spec"] else {})
        VSPSpecValidators().validate_hur_fact(self.spec)
        return self.spec

    def get_snapshot_reconcile_spec(self):
        self.spec = SnapshotReconcileSpec(
            **self.params["spec"], state=self.params["state"]
        )
        VSPSpecValidators().validate_snapshot_module(self.spec, self.connection_info)
        return self.spec

    def get_pool_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = PoolFactSpec(**self.params["spec"])
            VSPSpecValidators().validate_storage_pool_fact(input_spec)
        else:
            input_spec = PoolFactSpec()
        return input_spec

    def storage_pool_spec(self):

        input_spec = StoragePoolSpec(**self.params["spec"])
        VSPSpecValidators().validate_storage_pool(input_spec, self.get_state())
        return input_spec

    def get_port_fact_spec(self):
        self.spec = PortFactSpec(**self.params["spec"] if self.params["spec"] else {})
        return self.spec

    def port_module_spec(self):
        self.spec = ChangePortSettingSpec(**self.params["spec"])
        VSPSpecValidators().validate_port_module(self.spec)
        return self.spec

    def get_parity_group_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = ParityGroupFactSpec(**self.params["spec"])
            VSPSpecValidators().validate_parity_group_fact(input_spec)
        else:
            input_spec = ParityGroupFactSpec()
        return input_spec

    def true_cpoy_spec(self):
        self.spec = TrueCopySpec(**self.params["spec"])
        VSPSpecValidators().validate_true_copy_module(self.spec)
        return self.spec

    def get_true_copy_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = TrueCopyFactSpec(**self.params["spec"])
            VSPSpecValidators().validate_true_copy_fact(input_spec)
        else:
            input_spec = TrueCopyFactSpec()
        return input_spec

    def get_nvme_subsystem_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = VSPNvmeSubsystemFactSpec(**self.params["spec"])
            VSPSpecValidators().validate_nvme_subsystem_fact(input_spec)
        else:
            input_spec = VSPNvmeSubsystemFactSpec()
        return input_spec

    def hur_spec(self):
        self.spec = HurSpec(**self.params["spec"])
        VSPSpecValidators().validate_hur_module(self.spec, self.state)
        return self.spec

    def gad_pair_spec(self):
        self.spec = VspGadPairSpec(**self.params["spec"])
        VSPSpecValidators().validate_gad_pair_spec(self.spec, self.state)
        return self.spec
    
    def gad_pair_fact_spec(self):
        self.spec = GADPairFactSpec(**self.params["spec"] if self.params["spec"] else {})
        return self.spec
    
    def snapshot_grp_spec(self):
        self.spec = SnapshotGroupSpec(**self.params["spec"] )
        return self.spec
    
    def snapshot_grp_fact_spec(self):
        self.spec = SnapshotGroupFactSpec(**self.params["spec"] )
        return self.spec

    def unsubscribe_spec(self):
        if "spec" in self.params and self.params["spec"] is not None and self.params["spec"]["resources"] is None:
            raise ValueError("Ensure resources is not empty.")

        self.spec = UnsubscribeSpec(**self.params["spec"])
        VSPSpecValidators().validate_unsubscribe_module(self.spec)
        return self.spec
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
            "ldev_id": {
                "required": False,
                "type": "str",
                "description": "The ID of the LDEV to get information for.",
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
            "is_detailed": {
                "required": False,
                "type": "bool",
                "description": "Determines whether details information for the LUN is diaplyed.",
            },
        }

        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments

    @classmethod
    def volume(cls):
        
        tiering_policy = {
            "tier_level": {
                "required": False,
                "type": "int",
            },
            "tier1_allocation_rate_min": {
                "required": False,
                "type": "int",
            },
            "tier1_allocation_rate_max": {
                "required": False,
                "type": "int",
            },
            "tier3_allocation_rate_min": {
                "required": False,
                "type": "int",
            },
            "tier3_allocation_rate_max": {
                "required": False,
                "type": "int",
            },
        }    
        
        spec_options = {
            "ldev_id": {
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
            "data_reduction_share": {
                "required": False,
                "type": "bool",
            },
            "force": {
                "required": False,
                "type": "bool",
                "description": "If true, the task will unmap the lun from hostgroup, iscsi target, and NVMe subsystem before delete the lun.",
            },
            "is_relocation_enabled": {
                "required": False,
                "type": "bool",
                "description": "Enable relocation.",
            },
            "tier_level_for_new_page_allocation": {
                "required": False,
                "type": "str",
                "description": "New page allocation tier level: High or Low",
            },
            "tiering_policy": {
                "required": False,
                "type": "dict",
                "options": tiering_policy,
                "description": "Tiering policy.",
            },
            "state": {
                "required": False,
                "type": "str",
                "choices": ["add_host_nqn", "remove_host_nqn"],
                "default": "add_host_nqn",
            }, 
            "nvm_subsystem_name": {
                "required": False,
                "type": "str",
            },
            "host_nqns": {
                "required": False,
                "type": "list",
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
            "ldevs": {
                "required": False,
                "type": "list",
                "description": "LDEV ID in decimal or HEX of the LDEV that you want to present.",
            },
            "wwns": {
                "required": False,
                "type": "list",
                "description": "List of host WWNs.",
            },
            "should_delete_all_ldevs": {
                "required": False,
                "type": "bool",
                "description": "If the value is true, destroy the logical devices that are no longer attached to any host group.",
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
            "primary_volume_id": {
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
            "primary_volume_id": {
                "required": True,
                "type": "int",
                "description": "Primary volume id",
            },
            "secondary_volume_id": {
                "required": True,
                "type": "int",
                "description": "Secondary volume id",
            },
            "auto_split": {
                "required": False,
                "type": "bool",
                "description": "Auto split",
            },
            "allocate_new_consistency_group": {
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
    snapshot_image_state["choices"].extend(["split", "sync", "restore", "clone"])

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
    def snapshot_grp_args(cls):
        spec_options = {
            "snapshot_group_name": {
                "required": True,
                "type": "str",
            },
            "auto_split": {
                "required": False,
                "type": "bool",
            },

        }

        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments
    
    @classmethod
    def snapshot_grp_fact_args(cls):
        spec_options = {
            "snapshot_group_name": {
                "required": True,
                "type": "str",
            }

        }

        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments
    
    @classmethod
    def get_snapshot_fact_args(cls):
        spec_options = {
            "primary_volume_id": {
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
            "primary_volume_id": {
                "required": True,
                "type": "int",
            },
            "pool_id": {
                "required": False,
                "type": "int",
            },
            "allocate_new_consistency_group": {
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
            "is_data_reduction_force_copy": {
                "required": False,
                "type": "bool",
            },
            "can_cascade": {
                "required": False,
                "type": "bool",
            },
            "is_clone": {
                "required": False,
                "type": "bool",
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
            "ldevs": {
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
            "should_delete_all_ldevs": {
                "required": False,
                "type": "bool",
                "description": "If the value is true, destroy the logical devices that are no longer attached to any iSCSI Target.",
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
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present", "absent"],
            "default": "present",
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

    @classmethod
    def storage_pool(cls):
        spec_options = {
            "id": {
                "required": False,
                "type": "int",
                "description": "Pool Id.",
            },
            "name": {
                "required": False,
                "type": "str",
            },
            "type": {
                "required": False,
                "type": "str",
                "choices": ["HDT", "HDP", "HRT", "HTI", "hdp", "hdt", "hrt", "hti"],
            },
            "should_enable_deduplication": {
                "required": False,
                "type": "bool",
            },
            "depletion_threshold_rate": {
                "required": False,
                "type": "int",
            },
            "warning_threshold_rate": {
                "required": False,
                "type": "int",
            },
            "resource_group_id": {
                "required": False,
                "type": "int",
            },
            "pool_volumes": {
                "required": False,
                "type": "list",
                "options": {
                    "capacity": {
                        "required": True,
                        "type": "str",
                    },
                    "parity_group_id": {
                        "required": True,
                        "type": "str",
                    },
                },
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments


class VSPStoragePortArguments:

    common_arguments = {
        "storage_system_info": VSPCommonParameters.storage_system_info(),
        "connection_info": VSPCommonParameters.connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present"],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "description": "Specifications for the task.",
            "options": {},
        },
    }

    @classmethod
    def storage_port_fact(cls):
        spec_options = {
            "ports": {
                "required": False,
                "type": "list",
                "description": "List of Ports",
            }
        }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments

    @classmethod
    def storage_port(cls):
        spec_options = {
            "port": {
                "required": True,
                "type": "str",
                "description": "Port Id",
            },
            "port_mode": {
                "required": False,
                "type": "str",
            },
            "enable_port_security": {
                "required": False,
                "type": "bool",
            },
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


class VSPTrueCopyArguments:

    common_arguments = {
        "storage_system_info": VSPCommonParameters.storage_system_info(),
        "connection_info": VSPCommonParameters.connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present", "absent", "sync", "split"],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "description": "Specifications for the task.",
            "options": {},
        },
    }

    @classmethod
    def true_copy(cls):
        spec_options = {
            "primary_volume_id": {
                "required": True,
                "type": "int",
                "description": "Primary volume Id.",
            },
            "consistency_group_id": {
                "required": False,
                "type": "int",
                "description": "Consistency group Id.",
            },
            "fence_level": {
                "required": False,
                "type": "str",
                "choices": ["NEVER", "DATA", "STATUS", "UNKNOWN"],
                "default": "NEVER",
                "description": "Fence level",
            },
            "allocate_new_consistency_group": {
                "required": False,
                "type": "bool",
                "default": False,
                "description": "Whether to create a new consistecy group.",
            },
            "secondary_storage_serial_number": {
                "required": False,
                "type": "int",
                "description": "Secondary storage serial number.",
            },
            "secondary_pool_id": {
                "required": False,
                "type": "int",
                "description": "Id of dynamic pool where the secondary volume will be created.",
            },
            "secondary_hostgroup": {
                "required": False,
                "type": "dict",
                "description": "hostgroup details of the secondary volume",
                "options": {
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
                },
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments

    @classmethod
    def true_copy_facts(cls):
        spec_options = {
            "primary_volume_id": {
                "required": False,
                "type": "int",
                "description": "Primary volume Id.",
            },
            "secondary_volume_id": {
                "required": False,
                "type": "int",
                "description": "Secondary volume Id.",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments

class VSPVolTierArguments:

    common_arguments = {
        "storage_system_info": VSPCommonParameters.storage_system_info(),
        "connection_info": VSPCommonParameters.connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": [
                "present",
                "absent",
            ],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "description": "Specifications for the task.",
            "options": {},
        },
    }

    @classmethod
    def get_args(cls):
        tiering_policy = {
            "tier_level": {
                "required": False,
                "type": "int",
            },
            "tier1_allocation_rate_min": {
                "required": False,
                "type": "int",
            },
            "tier1_allocation_rate_max": {
                "required": False,
                "type": "int",
            },
            "tier3_allocation_rate_min": {
                "required": False,
                "type": "int",
            },
            "tier3_allocation_rate_max": {
                "required": False,
                "type": "int",
            },
        }
        
        spec_options = {
            "ldev_id": {
                "required": True,
                "type": "int",
                "description": "Volume Id.",
            },
            "is_relocation_enabled": {
                "required": False,
                "type": "bool",
                "description": "Enable relocation.",
            },
            "tier_level_for_new_page_allocation": {
                "required": False,
                "type": "bool",
                "description": "New page allocation tier level.",
            },
            "tiering_policy": {
                "required": False,
                "type": "dict",
                "default": False,
                "description": "Tiering policy.",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments
    
class VSPHurArguments:

    common_arguments = {
        "storage_system_info": VSPCommonParameters.storage_system_info(),
        "connection_info": VSPCommonParameters.connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": [
                "present",
                "absent",
                "split",
                "resync",
            ],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "description": "Specifications for the task.",
            "options": {},
        },
    }

    @classmethod
    def hur(cls):
        spec_options = {
            "primary_volume_id": {
                "required": True,
                "type": "int",
                "description": "Primary volume Id.",
            },
            "mirror_unit_id": {
                "required": False,
                "type": "int",
                "description": "Mirror Unit Id is required other than the CREATE operation",
            },
            "consistency_group_id": {
                "required": False,
                "type": "int",
                "description": "Consistency group Id.",
            },
            "enable_delta_resync": {
                "required": False,
                "type": "bool",
                "default": False,
                "description": "Enable delta resync",
            },
            "allocate_new_consistency_group": {
                "required": False,
                "type": "bool",
                "default": False,
                "description": "Whether to create a new consistency group.",
            },
            "primary_volume_journal_id": {
                "required": False,
                "type": "int",
                "description": "Primary volume journal.",
            },
            "secondary_volume_journal_id": {
                "required": False,
                "type": "int",
                "description": "Secondary volume journal.",
            },
            "secondary_storage_serial_number": {
                "required": False,
                "type": "int",
                "description": "Secondary storage serial number.",
            },
            "secondary_pool_id": {
                "required": False,
                "type": "int",
                "description": "Id of dynamic pool where the secondary volume will be created.",
            },
            "secondary_hostgroup": {
                "required": False,
                "type": "dict",
                "description": "hostgroup details of the secondary volume",
                "options": {
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
                },
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments

    # 20240812 HUR facts spec
    @classmethod
    def get_hur_fact_args(cls):
        spec_options = {
            "primary_volume_id": {
                "required": False,
                "type": "int",
                "description": "Primary Volume Id.",
            },
            "secondary_volume_id": {
                "required": False,
                "type": "int",
                "description": "Secondary volume Id.",
            },
            "mirror_unit_id": {
                "required": False,
                "type": "int",
                "description": "Mirror Unit Id.",
            },
        }

        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments

class VSPNvmeSubsystemArguments:
    common_arguments = {
        "storage_system_info": VSPCommonParameters.storage_system_info(),
        "connection_info": VSPCommonParameters.connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present","absent"],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "description": "Specifications for the task.",
            "options": {},
        },
    }

    @classmethod
    def nvme_subsystem_facts(cls):
        spec_options = {
            "name": {
                "required": False,
                "type": "str",
                "description": "Name of the NVM Subsystem.",
            },
            "id": {
                "required": False,
                "type": "int",
                "description": "Id of the NVM Subsystem.",
            },
        }

        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments


class VSPGADArguments:

    common_arguments = {
        "storage_system_info": VSPCommonParameters.storage_system_info(),
        "connection_info": VSPCommonParameters.connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present", "absent", "split", "resync"],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "description": "Specifications for the task.",
            "options": {},
        },
    }

    @classmethod
    def gad_pair_fact_args(cls):
        spec_options ={
            "primary_volume_id": {
                "required": False,
                "type": "int",
                "description": "Primary Volume Id.",
            },
            }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments
    @classmethod
    def gad_pair_args_spec(cls):
        hg_options = {
            
            "name": {
                "required": True,
                "type": "str",
            },
            "enable_preferred_path": {
                "required": False,
                "type": "bool",
            },
            "port": {
                "required": True,
                "type": "int",
            },
        }

        spec_options = {
            "primary_storage_serial_number": {
                "required": False,
                "type": "str",
            },
            "secondary_storage_serial_number": {
                "required": False,
                "type": "str",
            },
            "primary_volume_id": {
                "required": True,
                "type": "int",
            },
            "secondary_pool_id": {
                "required": False,
                "type": "int",
            },
            "consistency_group_id": {
                "required": False,
                "type": "int",
            },
            "allocate_new_consistency_group": {
                "required": False,
                "type": "bool",
            },
            "set_alua_mode": {
                "required": False,
                "type": "bool",
            },
            "primary_hostgroups": {
                "required": False,
                "type": "list",
                "element": "dict",
                "options": hg_options,
            },
            "secondary_hostgroups": {
                "required": False,
                "type": "list",
                "element": "dict",
                "options": hg_options,
            },
            "primary_resource_group_name": {
                "required": False,
                "type": "str",
            },
            "secondary_resource_group_name": {
                "required": False,
                "type": "str",
            },
            "quorum_disk_id": {
                "required": False,
                "type": "int",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments


## 20240822 - VSPVolumeTieringArguments
class VSPVolumeTieringArguments:

    common_arguments = {
        "storage_system_info": VSPCommonParameters.storage_system_info(),
        "connection_info": VSPCommonParameters.connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present", "absent", "split", "resync"],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "description": "Specifications for the task.",
            "options": {},
        },
    }

    @classmethod
    def args_spec(cls):
        tiering_policy = {
            "tier_level": {
                "required": False,
                "type": "int",
            },
            "tier1_allocation_rate_min": {
                "required": False,
                "type": "int",
            },
            "tier1_allocation_rate_max": {
                "required": False,
                "type": "int",
            },
            "tier3_allocation_rate_min": {
                "required": False,
                "type": "int",
            },
            "tier3_allocation_rate_max": {
                "required": False,
                "type": "int",
            },
        }

        spec_options = {
            "ldev_id": {
                "required": True,
                "type": "int",
            },
            "is_relocation_enabled": {
                "required": False,
                "type": "bool",
            },
            "tier_level_for_new_page_allocation": {
                "required": False,
                "type": "bool",
            },
            "tiering_policy": {
                "required": False,
                "type": "list",
                "element": "dict",
                "options": tiering_policy,
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments

class VSPUnsubscriberArguments:

    common_arguments = {
        "storage_system_info": VSPCommonParameters.storage_system_info(),
        "connection_info": VSPCommonParameters.connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present", "absent", "sync", "split"],
            "default": "present",
        },
        "spec": {
            "required": True,
            "type": "dict",
            "description": "Specifications for the task.",
            "options": {},
        },
    }

    @classmethod
    def unsubscribe(cls):

        resource = {
            "type": {
                "required": True,
                "type": "str",
            },
            "values": {
                "required": True,
                "type": "list",
            },
        }        
        spec_options = {
            "resources": {
                "required": True,
                "type": list[resource],
                "description": "Array of resources to unsubscribe",
                #  "options": resource,
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments
##############################################################
### Validator functions ###
RE_INT = re.compile(r'^([0-9]+)$')
class VSPSpecValidators:

    RE_INT = re.compile(r'^([0-9]+)$')

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
        elif conn_info.subscriber_id:
            is_numeric = RE_INT.match(conn_info.subscriber_id)
            if is_numeric is None:
                raise ValueError(VSPVolValidationMsg.SUBSCRIBER_ID_NOT_NUMERIC.value)

    @staticmethod
    def validate_volume_facts(input_spec: VolumeFactSpec):

        if input_spec.ldev_id:
            try:
                lun_value = int(input_spec.ldev_id)
                if lun_value < 0 or lun_value > AutomationConstants.LDEV_ID_MAX:
                    raise ValueError(VSPVolValidationMsg.LDEV_ID_OUT_OF_RANGE.value)
            except ValueError as e:
                if "invalid literal" not in str(e):
                    # Handle the case where the input is not a valid integer format
                    raise e
                else:
                    # Handle other ValueErrors, like out-of-range checks
                    pass

        if isinstance(input_spec.start_ldev_id, int) and (
            input_spec.start_ldev_id < 0
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

        if isinstance(input_spec.ldev_id, int) and not (
            0 < int(input_spec.ldev_id) < AutomationConstants.LDEV_MAX_NUMBER
        ):
            raise ValueError(VSPVolValidationMsg.LDEV_ID_OUT_OF_RANGE.value)
        if state == StateValue.ABSENT:
            # 2.3 gateway defines spec.ldev for one set of logics,
            # it also defines spec.ldevs as str (not list) for other business logics, it's a mess
            if not input_spec.ldev_id:
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
    def validate_hur_fact(input_spec: HurFactSpec):
        if isinstance(input_spec.pvol, int) and input_spec.pvol < 0:
            raise ValueError(VSPSnapShotValidateMsg.PVOL_VALID_RANGE.value)
        if isinstance(input_spec.mirror_unit_id, int) and (
            input_spec.mirror_unit_id < 0
            or input_spec.mirror_unit_id > AutomationConstants.LDEV_MAX_MU_NUMBER
        ):
            raise ValueError(VSPSnapShotValidateMsg.MU_VALID_RANGE.value)

        if isinstance(input_spec.mirror_unit_id, int) and not isinstance(
            input_spec.primary_volume_id, int
        ):
            raise ValueError(VSPSnapShotValidateMsg.MU_VALID_PVOL_VALUE.value)

    @staticmethod
    def validate_snapshot_module(spec: SnapshotReconcileSpec, conn: ConnectionInfo):
        if spec.state == StateValue.PRESENT:
            if spec.snapshot_group_name is None:
                raise ValueError(VSPSnapShotValidateMsg.SNAPSHOT_GRP_NAME.value)
            if (
                conn.connection_type == ConnectionTypes.GATEWAY
                and spec.is_data_reduction_force_copy
                and not (spec.can_cascade or spec.is_clone)
            ):
                ##20240813 - validate TIA create
                raise ValueError(
                    VSPSnapShotValidateMsg.DATA_REDUCTION_FORCE_COPY_SNAP_MODE.value
                )
            if (
                conn.connection_type == ConnectionTypes.GATEWAY
                and not spec.allocate_consistency_group
                and not spec.consistency_group_id
            ):
                ## 20240820 - consistency_group_id
                # raise ValueError(VSPSnapShotValidateMsg.CONSISTENCY_GROUP.value)
                spec.allocate_consistency_group = False

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
    def validate_storage_pool(input_spec: StoragePoolSpec, state: str):

        if state == StateValue.PRESENT:
            
            if input_spec.pool_volumes is not None:
                for pool_volume in input_spec.pool_volumes:
                    if (
                        pool_volume.parity_group_id is None
                        and pool_volume.capacity is None
                    ):
                        raise ValueError(VSPStoragePoolValidateMsg.PG_ID_CAPACITY.value)
                    if (
                        pool_volume.parity_group_id is not None
                        and pool_volume.capacity is None
                    ):
                        raise ValueError(
                            VSPStoragePoolValidateMsg.MISSING_CAPACITY.value.format(
                                pool_volume.parity_group_id
                            )
                        )
                    if (
                        pool_volume.parity_group_id is None
                        and pool_volume.capacity is not None
                    ):
                        raise ValueError(
                            VSPStoragePoolValidateMsg.MISSING_PG_ID.value.format(
                                pool_volume.capacity
                            )
                        )
                    size_in_bytes = convert_to_bytes(pool_volume.capacity)
                    if size_in_bytes < AutomationConstants.POOL_SIZE_MIN:
                        raise ValueError(VSPStoragePoolValidateMsg.POOL_SIZE_MIN.value)
        if input_spec.id is not None and input_spec.name is not None:
            raise ValueError(VSPStoragePoolValidateMsg.BOTH_POOL_ID_AND_NAME.value)

    @staticmethod
    def validate_shadow_image_module(spec: ShadowImagePairSpec, conn: ConnectionInfo):

        if spec.copy_pace is not None:
            options = ["SLOW", "MEDIUM", "FAST"]
            if spec.copy_pace not in options:
                raise ValueError(VSPShadowImagePairValidateMsg.COPY_PACE_VALUE.value)

        if spec.copy_pace_track_size is not None:
            options = ["SLOW", "MEDIUM", "FAST"]
            if spec.copy_pace_track_size not in options:
                raise ValueError(
                    VSPShadowImagePairValidateMsg.COPY_PACE_TRACK_SIZE_VALUE.value
                )

    @staticmethod
    def validate_iscsi_target_spec(input_spec: IscsiTargetSpec):

        if input_spec.name:
            if (
                len(input_spec.name) < AutomationConstants.ISCSI_NAME_LEN_MIN
                or len(input_spec.name) > AutomationConstants.ISCSI_NAME_LEN_MAX
            ):
                raise ValueError(
                    VSPIscsiTargetValidationMsg.ISCSI_NAME_OUT_OF_RANGE.value
                )

        if input_spec.iqn_initiators:
            for iqn_initiator in input_spec.iqn_initiators:
                if (
                    len(iqn_initiator) < AutomationConstants.IQN_LEN_MIN
                    or len(iqn_initiator) > AutomationConstants.IQN_LEN_MAX
                ):
                    raise ValueError(VSPIscsiTargetValidationMsg.IQN_OUT_OF_RANGE.value)

        if input_spec.ldevs:
            for lun in input_spec.ldevs:
                if (
                    lun < AutomationConstants.LDEV_ID_MIN
                    or lun > AutomationConstants.LDEV_ID_MAX
                ):
                    raise ValueError(VSPIscsiTargetValidationMsg.LUN_OUT_OF_RANGE.value)

        if input_spec.chap_users:
            for chap_user in input_spec.chap_users:
                if chap_user.chap_user_name:
                    if (
                        len(chap_user.chap_user_name)
                        < AutomationConstants.CHAP_USER_NAME_LEN_MIN
                        or len(chap_user.chap_user_name)
                        > AutomationConstants.CHAP_USER_NAME_LEN_MAX
                    ):
                        raise ValueError(
                            VSPIscsiTargetValidationMsg.CHAP_USER_NAME_OUT_OF_RANGE.value
                        )
                if chap_user.chap_secret:
                    if (
                        len(chap_user.chap_secret)
                        < AutomationConstants.CHAP_SECRET_LEN_MIN
                        or len(chap_user.chap_secret)
                        > AutomationConstants.CHAP_SECRET_LEN_MAX
                    ):
                        raise ValueError(
                            VSPIscsiTargetValidationMsg.CHAP_SECRET_OUT_OF_RANGE.value
                        )

        if input_spec.port:
            if (
                len(input_spec.port) < AutomationConstants.NAME_PARAMS_MIN
                or len(input_spec.port) > AutomationConstants.NAME_PARAMS_MAX
            ):
                raise ValueError(VSPIscsiTargetValidationMsg.PORT_OUT_OF_RANGE.value)

        if input_spec.host_mode:
            if (
                len(input_spec.host_mode) < AutomationConstants.NAME_PARAMS_MIN
                or len(input_spec.host_mode) > AutomationConstants.NAME_PARAMS_MAX
            ):
                raise ValueError(
                    VSPIscsiTargetValidationMsg.HOST_MODE_OUT_OF_RANGE.value
                )

    @staticmethod
    def validate_host_group_spec(input_spec: HostGroupSpec):

        logger = Log()

        if input_spec.name:
            if (
                len(input_spec.name) < AutomationConstants.HG_NAME_LEN_MIN
                or len(input_spec.name) > AutomationConstants.HG_NAME_LEN_MAX
            ):
                raise ValueError(VSPHostGroupValidationMsg.HG_NAME_OUT_OF_RANGE.value)

        if input_spec.ldevs:
            for lun in input_spec.ldevs:
                logger.writeDebug("1000 lun={}", lun)
                # 2.4 MT - for composite playbook, gateway returns a str, direct returns a int
                lun = int(lun)
                if not isinstance(lun, int):
                    raise ValueError(VSPHostGroupValidationMsg.INVALID_PARAM_LDEVS.value)

                if (
                    lun < AutomationConstants.LDEV_ID_MIN
                    or lun > AutomationConstants.LDEV_ID_MAX
                ):
                    raise ValueError(VSPHostGroupValidationMsg.LUN_OUT_OF_RANGE.value)

        if input_spec.wwns:
            for wwn in input_spec.wwns:
                if (
                    len(wwn) < AutomationConstants.NAME_PARAMS_MIN
                    or len(wwn) > AutomationConstants.NAME_PARAMS_MAX
                ):
                    raise ValueError(VSPHostGroupValidationMsg.WWN_OUT_OF_RANGE.value)

        if input_spec.port:
            if (
                len(input_spec.port) < AutomationConstants.NAME_PARAMS_MIN
                or len(input_spec.port) > AutomationConstants.NAME_PARAMS_MAX
            ):
                raise ValueError(VSPHostGroupValidationMsg.PORT_OUT_OF_RANGE.value)

        if input_spec.host_mode:
            if (
                len(input_spec.host_mode) < AutomationConstants.NAME_PARAMS_MIN
                or len(input_spec.host_mode) > AutomationConstants.NAME_PARAMS_MAX
            ):
                raise ValueError(VSPHostGroupValidationMsg.HOST_MODE_OUT_OF_RANGE.value)

    @staticmethod
    def validate_port_module(input_spec):
        if (
            input_spec.port_mode is not None
            and input_spec.enable_port_security is not None
        ):
            raise ValueError(
                VSPStoragePortValidateMsg.PORT_MODE_LUN_SECURITY_COMBINATION.value
            )
        if len(input_spec.port) < 1:
            raise ValueError(VSPStoragePortValidateMsg.VALID_PORT_ID.value)

    @staticmethod
    def validate_true_copy_module(input_spec):

        if input_spec.consistency_group_id:
            cg_id = input_spec.consistency_group_id
            if (
                cg_id < AutomationConstants.CONSISTENCY_GROUP_ID_MIN
                or cg_id > AutomationConstants.CONSISTENCY_GROUP_ID_MAX
            ):
                raise ValueError(VSPTrueCopyValidateMsg.INVALID_CG_ID.value)

        if input_spec.secondary_hostgroups:
            for hg in input_spec.secondary_hostgroups:
                # if hg.id is None:
                #     raise ValueError(
                #         VSPTrueCopyValidateMsg.SECONDARY_HOSTGROUPS_ID.value
                #     )
                if hg.name is None:
                    raise ValueError(
                        VSPTrueCopyValidateMsg.SECONDARY_HOSTGROUPS_NAME.value
                    )
                if hg.port is None:
                    raise ValueError(
                        VSPTrueCopyValidateMsg.SECONDARY_HOSTGROUPS_PORT.value
                    )

    @staticmethod
    def validate_true_copy_fact(input_spec: TrueCopyFactSpec):
        # if input_spec.primary_volume_id is None and input_spec.secondary_volume_id is None:
        #     raise ValueError(VSPTrueCopyValidateMsg.PRIMARY_VOLUME_ID.value)
        pass

    @staticmethod
    def validate_nvme_subsystem_fact(input_spec: TrueCopyFactSpec):
        pass
    
    # 20240808 - validate_hur_module
    @staticmethod
    def validate_hur_module(input_spec, state):
        logger = Log()
        logger.writeDebug("input_spec={}", input_spec)
        logger.writeDebug("state={}", state)
        state = state.lower()

        if input_spec.mirror_unit_id is not None:
            if state == "present":
                raise ValueError("For create, mirror_unit_id is not allowed.")

            ## all other operations, other params are ignored
            return

        if input_spec.secondary_storage_serial_number is None:
            raise ValueError(VSPHurValidateMsg.SECONDARY_STORAGE_SN.value)
        if input_spec.secondary_pool_id is None:
            raise ValueError(VSPHurValidateMsg.SECONDARY_POOL_ID.value)

        # if input_spec.secondary_hostgroups is None:
        #     raise ValueError(VSPHurValidateMsg.SECONDARY_HOSTGROUPS.value)

        if input_spec.primary_volume_journal_id is None:
            raise ValueError(VSPHurValidateMsg.PRIMARY_JOURNAL_ID.value)
        if input_spec.secondary_volume_journal_id is None:
            raise ValueError(VSPHurValidateMsg.SECONDARY_JOURNAL_ID.value)

        if input_spec.consistency_group_id:
            cg_id = input_spec.consistency_group_id
            if (
                cg_id < AutomationConstants.CONSISTENCY_GROUP_ID_MIN
                or cg_id > AutomationConstants.CONSISTENCY_GROUP_ID_MAX
            ):
                raise ValueError(VSPHurValidateMsg.INVALID_CG_ID.value)
            if input_spec.allocate_new_consistency_group:
                raise ValueError(VSPHurValidateMsg.INVALID_CG_NEW.value)

        if input_spec.secondary_hostgroups:
            for hg in input_spec.secondary_hostgroups:
                # if hg.id is None:
                #     raise ValueError(VSPHurValidateMsg.SECONDARY_HOSTGROUPS_ID.value)
                if hg.name is None:
                    raise ValueError(VSPHurValidateMsg.SECONDARY_HOSTGROUPS_NAME.value)
                if hg.port is None:
                    raise ValueError(VSPHurValidateMsg.SECONDARY_HOSTGROUPS_PORT.value)

    @staticmethod
    def validate_gad_pair_spec(input_spec: VspGadPairSpec, state: str):

        def _validate_hostgroups(hostgroups, pos):
            for hg in hostgroups:
                
                if hg.name is None:
                    raise ValueError(
                        GADPairValidateMSG.HOSTGROUPS_NAME.value.format(pos)
                    )
                if hg.port is None:
                    raise ValueError(
                        GADPairValidateMSG.HOSTGROUPS_PORT.value.format(pos)
                    )

        if state.lower() == StateValue.PRESENT:
            if input_spec.primary_storage_serial_number is None:
                raise ValueError(GADPairValidateMSG.PRIMARY_STORAGE_SN.value)
            if input_spec.secondary_storage_serial_number is None:
                raise ValueError(GADPairValidateMSG.SECONDARY_STORAGE_SN.value)

            if input_spec.primary_volume_id is None:
                raise ValueError(GADPairValidateMSG.PRIMARY_VOLUME_ID.value)
            
            if input_spec.secondary_pool_id is None:
                raise ValueError(GADPairValidateMSG.SECONDARY_POOL_ID.value)

            if input_spec.primary_hostgroups :
                _validate_hostgroups(input_spec.primary_hostgroups, "Primary")

            if input_spec.secondary_hostgroups is None:
                raise ValueError(GADPairValidateMSG.SECONDARY_HOSTGROUPS.value)
            else:
                _validate_hostgroups(input_spec.secondary_hostgroups, "Secondary")
            
            if input_spec.consistency_group_id and input_spec.allocate_new_consistency_group:
                raise ValueError(GADPairValidateMSG.INCONSISTENCY_GROUP.value)

    @staticmethod
    def validate_unsubscribe_module(input_spec):
        # valid_type = [ "port", "volume", "hostgroup", "shadowimage", "storagepool", "iscsi_target", "hurpair", "gadpair", "truecopypair"]
        valid_type = [ "port", "volume", "hostgroup", "storagepool", "iscsitarget" ]
        if input_spec.resources is None or len(input_spec.resources) < 1:
            raise ValueError("Provide proper type and values for resources.")
                             
        if input_spec.resources is not None:
            for x in input_spec.resources:
                if x['type'].lower() not in valid_type:
                    raise ValueError(GatewayValidationMsg.UNSUPPORTED_RESOURCE_TYPE.value.format(x['type'], valid_type ))
                if x['values'] is None or x['values'] == "":
                    raise ValueError(GatewayValidationMsg.PROVIDE_RESOURCE_VALUE['values'])

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


class NAIDCalculator:
    array_family_map = {
        "ARRAY_FAMILY_DF": ["AMS", "HUS"],
        "ARRAY_FAMILY_R700": ["VSP"],
        "ARRAY_FAMILY_HM700": ["HUS-VM"],
        "ARRAY_FAMILY_R800": ["VSP G1000", "VSP G1500", "VSP F1500"],
        "ARRAY_FAMILY_HM800": [
            "VSP G200",
            "VSP G400",
            "VSP F400",
            "VSP N400",
            "VSP G600",
            "VSP F600",
            "VSP N600",
            "VSP G800",
            "VSP G130",
            "VSP G150",
            "VSP G350",
            "VSP G370",
            "VSP F350",
            "VSP F370",
            "VSP G700",
            "VSP F700",
            "VSP G900",
            "VSP F900",
        ],
        "ARRAY_FAMILY_R900": [
            "VSP 5000",
            "VSP 5000H",
            "VSP 5500",
            "VSP 5500H",
            "VSP 5200",
            "VSP 5200H",
            "VSP 5600",
            "VSP 5600H",
        ],
        "ARRAY_FAMILY_HM900": [
            "VSP E590",
            "VSP E790",
            "VSP E990",
            "VSP E1090",
            "VSP E1090H",
        ],
        "ARRAY_FAMILY_HM2000": [
            "VSP One B23",
            "VSP One B24",
            "VSP One B26",
            "VSP One B28",
        ],
    }

    def __init__(self, wwn_any_port=None, serial_number=None, device_type=None):
        global BASIC_STORAGE_DETAILS
        # Convert WWN to integer if it's in hexadecimal string format
        if isinstance(wwn_any_port, str):
            wwn_any_port = int(wwn_any_port, 16)
        self.wwn_any_port = wwn_any_port
        self.serial_number = serial_number
        self.array_family = self.get_array_family(device_type)

        # Mask and adjustment based on array family
        self.wwn_mask_and = 0xFFFFFF00
        self.serial_number_mask_or = 0x00000000

        self._apply_array_family_adjustments()

        # Apply masks
        self.wwn_part = self.wwn_any_port & 0xFFFFFFFF
        self.wwn_part &= self.wwn_mask_and
        self.serial_number |= self.serial_number_mask_or

        # Precompute high bytes since they don't change with LUN
        self.high_bytes = self._compute_high_bytes()

    def get_array_family(self, device_type):
        for array_family, models in self.array_family_map.items():
            for model in models:
                if (
                    model.replace(" ", "").lower()
                    == device_type.replace(" ", "").lower()
                ):
                    return array_family
        return "Unknown array family"

    def _apply_array_family_adjustments(self):
        if self.array_family == "ARRAY_FAMILY_DF":
            self.wwn_mask_and = 0xFFFFFFF0
        elif self.array_family == "ARRAY_FAMILY_HM700":
            while self.serial_number > 99999:
                self.serial_number -= 100000
            self.serial_number_mask_or = 0x50200000
        elif self.array_family == "ARRAY_FAMILY_R800":
            self.serial_number_mask_or = 0x00300000
        elif self.array_family == "ARRAY_FAMILY_HM800":
            while self.serial_number > 99999:
                self.serial_number -= 100000
            self.serial_number_mask_or = 0x50400000
        elif self.array_family == "ARRAY_FAMILY_R900":
            self.serial_number_mask_or = 0x00500000
        elif self.array_family == "ARRAY_FAMILY_HM900":
            if 400000 <= self.serial_number < 500000:
                self.serial_number_mask_or = 0x50400000
            elif 700000 <= self.serial_number < 800000:
                self.serial_number_mask_or = 0x50700000
            else:
                self.serial_number_mask_or = 0x50600000
            while self.serial_number > 99999:
                self.serial_number -= 100000
        elif self.array_family == "ARRAY_FAMILY_HM2000":
            self.serial_number_mask_or = 0x50800000
            while self.serial_number > 99999:
                self.serial_number -= 100000
        else:
            raise ValueError(f"Unsupported array family: {self.array_family}")

    def _compute_high_bytes(self):
        return (
            (0x60 << 56)
            | (0x06 << 48)
            | (0x0E << 40)
            | (0x80 << 32)
            | ((self.wwn_part >> 24) & 0xFF) << 24
            | ((self.wwn_part >> 16) & 0xFF) << 16
            | ((self.wwn_part >> 8) & 0xFF) << 8
            | (self.wwn_part & 0xFF)
        )

    def calculate_naid(self, lun):
        # Compute low bytes with the given LUN
        low_bytes = (
            ((self.serial_number >> 24) & 0xFF) << 56
            | ((self.serial_number >> 16) & 0xFF) << 48
            | ((self.serial_number >> 8) & 0xFF) << 40
            | (self.serial_number & 0xFF) << 32
            | 0x00 << 24
            | 0x00 << 16
            | ((lun >> 8) & 0xFF) << 8
            | (lun & 0xFF)
        )

        # Format NAID
        naid = f"naa.{self.high_bytes:012x}{low_bytes:016x}"
        return naid
