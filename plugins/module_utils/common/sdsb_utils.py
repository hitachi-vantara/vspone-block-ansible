import re

try:
    from ..common.hv_constants import ConnectionTypes
    from ..common.sdsb_constants import AutomationConstants
    from ..message.sdsb_connection_msgs import SDSBConnectionValidationMsg
    from ..message.sdsb_volume_msgs import SDSBVolValidationMsg
    from ..message.sdsb_job_msgs import SDSBJobValidationMsg
    from ..message.sdsb_event_log_msgs import SDSBEventLogValidationMsg
    from ..message.sdsb_storage_pool_msgs import SDSBStoragePoolValidationMsg
    from ..message.sdsb_estimated_capacity_msgs import SDSBEstimatedCapacityValidateMsg
    from ..model.common_base_models import ConnectionInfo
    from ..model.sdsb_volume_models import VolumeFactSpec, VolumeSpec
    from ..model.sdsb_job_models import JobFactSpec
    from ..model.sdsb_compute_node_models import ComputeNodeFactSpec, ComputeNodeSpec
    from ..model.sdsb_storage_node_models import (
        StorageNodeFactSpec,
        StorageNodeSpec,
        StorageNodeBmcAccessSettingFactSpec,
    )
    from ..model.sdsb_storage_pool_models import StoragePoolFactSpec, StoragePoolSpec
    from ..model.sdsb_cluster_models import ClusterFactSpec, ClusterSpec
    from ..model.sdsb_chap_user_models import ChapUserFactSpec, ChapUserSpec
    from ..model.sdsb_event_logs_model import EventLogFactSpec
    from ..model.sdsb_drive_models import SDSBDriveFactSpec, SDSBDriveSpec
    from ..model.sdsb_control_port_model import SDSBControlPortSpec
    from ..model.sdsb_fault_domain_model import SDSBFaultDomainSpec
    from ..model.sdsb_users_model import SDSBUsersSpec
    from ..model.sdsb_storage_controller_model import (
        SDSBStorageControllerFactSpec,
        SDSBStorageControllerSpec,
    )
    from ..model.sdsb_port_auth_models import PortAuthSpec
    from ..model.sdsb_port_models import PortFactSpec
    from ..model.sdsb_vps_models import VpsFactSpec, VpsSpec
    from ..model.sdsb_snapshot_models import SDSBSnapshotSpec, SDSBSnapshotFactsSpec
    from ..model.sdsb_capacity_management_settings_model import (
        SDSBCapacityManagementSettingsFactSpec,
    )
    from ..model.sdsb_estimated_capacity_model import SDSBEstimatedCapacityFactSpec
except ImportError:
    from common.hv_constants import ConnectionTypes
    from common.sdsb_constants import AutomationConstants
    from message.sdsb_connection_msgs import SDSBConnectionValidationMsg
    from message.sdsb_volume_msgs import SDSBVolValidationMsg
    from message.sdsb_job_msgs import SDSBJobValidationMsg
    from message.sdsb_event_log_msgs import SDSBEventLogValidationMsg
    from message.sdsb_storage_pool_msgs import SDSBStoragePoolValidationMsg
    from message.sdsb_estimated_capacity_msgs import SDSBEstimatedCapacityValidateMsg
    from model.common_base_models import ConnectionInfo
    from model.sdsb_volume_models import VolumeFactSpec, VolumeSpec
    from model.sdsb_job_models import JobFactSpec
    from model.sdsb_compute_node_models import ComputeNodeFactSpec, ComputeNodeSpec
    from model.sdsb_storage_node_models import (
        StorageNodeFactSpec,
        StorageNodeSpec,
        StorageNodeBmcAccessSettingFactSpec,
    )
    from model.sdsb_storage_pool_models import StoragePoolFactSpec, StoragePoolSpec
    from model.sdsb_cluster_models import ClusterFactSpec, ClusterSpec
    from model.sdsb_chap_user_models import ChapUserFactSpec, ChapUserSpec
    from model.sdsb_event_logs_model import EventLogFactSpec
    from model.sdsb_drive_models import SDSBDriveFactSpec, SDSBDriveSpec
    from model.sdsb_control_port_model import SDSBControlPortSpec
    from model.sdsb_fault_domain_model import SDSBFaultDomainSpec
    from model.sdsb_users_model import SDSBUsersSpec
    from model.sdsb_storage_controller_model import (
        SDSBStorageControllerFactSpec,
        SDSBStorageControllerSpec,
    )
    from model.sdsb_port_auth_models import PortAuthSpec
    from model.sdsb_port_models import PortFactSpec
    from model.sdsb_vps_models import VpsFactSpec, VpsSpec
    from model.sdsb_snapshot_models import SDSBSnapshotSpec, SDSBSnapshotFactsSpec
    from model.sdsb_capacity_management_settings_model import (
        SDSBCapacityManagementSettingsFactSpec,
    )
    from model.sdsb_estimated_capacity_model import SDSBEstimatedCapacityFactSpec


# SDSB Parameter manager
class SDSBParametersManager:

    def __init__(self, params):
        self.params = params
        self.connection_info = ConnectionInfo(**self.params.get("connection_info", {}))
        self.state = self.params.get("state", None)

        SDSBSpecValidators.validate_connection_info(self.connection_info)

    def get_state(self):
        return self.state

    def get_connection_info(self):
        return self.connection_info

    def get_volume_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = VolumeFactSpec(**self.params["spec"])
        else:
            input_spec = VolumeFactSpec()
        return input_spec

    def get_volume_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = VolumeSpec(**self.params["spec"])
            SDSBSpecValidators().validate_volume_spec(self.get_state(), input_spec)
        else:
            input_spec = VolumeSpec()
        return input_spec

    def get_compute_node_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = ComputeNodeFactSpec(**self.params["spec"])
        else:
            input_spec = ComputeNodeFactSpec()
        return input_spec

    def get_compute_node_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = ComputeNodeSpec(**self.params["spec"])
        else:
            input_spec = ComputeNodeSpec()
        return input_spec

    def get_compute_port_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = PortFactSpec(**self.params["spec"])
        else:
            input_spec = PortFactSpec()
        return input_spec

    def get_cluster_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = ClusterSpec(**self.params["spec"])
        else:
            input_spec = ClusterSpec()
        return input_spec

    def get_cluster_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = ClusterFactSpec(**self.params["spec"])
        else:
            input_spec = ClusterFactSpec()
        return input_spec

    def get_job_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = JobFactSpec(**self.params["spec"])
            SDSBSpecValidators.validate_job_facts_spec(input_spec)
            return input_spec
        else:
            return None

    def get_storage_node_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = StorageNodeSpec(**self.params["spec"])
        else:
            input_spec = StorageNodeSpec()
        return input_spec

    def get_storage_node_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = StorageNodeFactSpec(**self.params["spec"])
            return input_spec
        else:
            return None

    def get_storage_pool_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = StoragePoolSpec(**self.params["spec"])
            SDSBSpecValidators.validate_storage_pool_spec(input_spec)
        else:
            input_spec = StoragePoolSpec()
        return input_spec

    def get_storage_pool_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = StoragePoolFactSpec(**self.params["spec"])
            return input_spec
        else:
            return None

    def get_storage_node_bmc_access_setting_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = StorageNodeBmcAccessSettingFactSpec(**self.params["spec"])
            return input_spec
        else:
            return None

    def get_chap_user_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = ChapUserFactSpec(**self.params["spec"])
        else:
            input_spec = ChapUserFactSpec()
        return input_spec

    def get_event_log_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = EventLogFactSpec(**self.params["spec"])
            SDSBSpecValidators.validate_event_log_facts_spec(input_spec)
        else:
            input_spec = EventLogFactSpec()
        return input_spec

    def get_drive_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = SDSBDriveSpec(**self.params["spec"])
            SDSBSpecValidators.validate_drive_spec(input_spec)
        else:
            input_spec = SDSBDriveSpec()
        return input_spec

    def get_drives_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = SDSBDriveFactSpec(**self.params["spec"])
        else:
            input_spec = SDSBDriveFactSpec()
        return input_spec

    def get_fault_domain_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = SDSBFaultDomainSpec(**self.params["spec"])
        else:
            input_spec = SDSBFaultDomainSpec()
        return input_spec

    def get_users_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = SDSBUsersSpec(**self.params["spec"])
        else:
            input_spec = SDSBUsersSpec()
        return input_spec

    def get_storage_controller_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = SDSBStorageControllerSpec(**self.params["spec"])
        else:
            input_spec = SDSBStorageControllerSpec()
        return input_spec

    def get_capacity_management_settings_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = SDSBCapacityManagementSettingsFactSpec(**self.params["spec"])
        else:
            input_spec = SDSBCapacityManagementSettingsFactSpec()
        return input_spec

    def get_estimated_capacity_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = SDSBEstimatedCapacityFactSpec(**self.params["spec"])
            SDSBSpecValidators().validate_estimated_capacity_fact_spec(input_spec)
        else:
            input_spec = SDSBEstimatedCapacityFactSpec()
        return input_spec

    def get_storage_controller_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = SDSBStorageControllerFactSpec(**self.params["spec"])
        else:
            input_spec = SDSBStorageControllerFactSpec()
        return input_spec

    def get_control_port_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = SDSBControlPortSpec(**self.params["spec"])
        else:
            input_spec = SDSBControlPortSpec()
        return input_spec

    def get_chap_user_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = ChapUserSpec(**self.params["spec"])
        else:
            input_spec = ChapUserSpec()
        return input_spec

    def get_port_auth_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = PortAuthSpec(**self.params["spec"])
        else:
            input_spec = PortAuthSpec()
        return input_spec

    def get_vps_fact_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = VpsFactSpec(**self.params["spec"])
        else:
            input_spec = VpsFactSpec()
        return input_spec

    def get_vps_spec(self):
        if "spec" in self.params and self.params["spec"] is not None:
            input_spec = VpsSpec(**self.params["spec"])
        else:
            input_spec = VpsSpec()
        return input_spec

    def get_ticket_mgmt_spec(self):

        return self.params.get("spec", {})

    def get_sdsb_snapshot_spec(self):

        input_spec = SDSBSnapshotSpec(**self.params["spec"])

        return input_spec

    def get_sdsb_snapshot_facts_spec(self):

        input_spec = SDSBSnapshotFactsSpec(**self.params["spec"])

        return input_spec


class SDSBCommonParameters:

    @staticmethod
    def get_connection_info():
        return {
            "required": True,
            "type": "dict",
            "options": {
                "address": {
                    "required": True,
                    "type": "str",
                },
                "username": {
                    "required": True,
                    "type": "str",
                },
                "password": {
                    "required": True,
                    "type": "str",
                    "no_log": True,
                },
                "connection_type": {
                    "required": False,
                    "type": "str",
                    "choices": [
                        "direct"
                    ],  # Removed gateway connection type as it is not supported
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


class UAIGTokenArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
    }
    common_arguments["connection_info"]["options"].pop("connection_type")

    @classmethod
    def get_arguments(cls):
        return cls.common_arguments


class SDSBComputeNodeArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present", "absent"],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def compute_node(cls):
        spec_options = {
            "id": {
                "required": False,
                "type": "str",
            },
            "name": {
                "required": False,
                "type": "str",
            },
            "os_type": {
                "required": False,
                "type": "str",
            },
            "state": {
                "required": False,
                "type": "str",
                "choices": [
                    "add_iscsi_initiator",
                    "remove_iscsi_initiator",
                    "attach_volume",
                    "detach_volume",
                    "add_host_nqn",
                    "remove_host_nqn",
                ],
            },
            "iscsi_initiators": {"required": False, "type": "list", "elements": "str"},
            "host_nqns": {"required": False, "type": "list", "elements": "str"},
            "volumes": {"required": False, "type": "list", "elements": "str"},
            "should_delete_all_volumes": {
                "required": False,
                "type": "bool",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments["spec"]["required"] = True
        return cls.common_arguments

    @classmethod
    def compute_node_facts(cls):
        spec_options = {
            "names": {
                "required": False,
                "type": "list",
                "elements": "str",
            },
            "hba_name": {
                "required": False,
                "type": "str",
            },
            # "vps_name": {
            #     "required": False,
            #     "type": "str",
            #     "description": "Compute nodes that belongs to this vps",
            # },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments.pop("state")
        cls.common_arguments["spec"]["required"] = False
        return cls.common_arguments


class SDSBClusterArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": [
                "present",
                "add_storage_node",
                "remove_storage_node",
                "download_config_file",
                "stop_removing_storage_node",
                "replace_storage_node",
            ],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def cluster(cls):
        control_network_option = {
            "control_network_ip": {
                "required": True,
                "type": "str",
            },
            "control_network_subnet": {
                "required": False,
                "type": "str",
                "default": "255.255.255.0",
            },
            "control_network_mtu_size": {
                "required": False,
                "type": "int",
                "default": 1500,
            },
        }
        internode_network_option = {
            "internode_network_ip": {
                "required": True,
                "type": "str",
            },
            "internode_network_subnet": {
                "required": False,
                "type": "str",
                "default": "255.255.255.0",
            },
            "internode_network_mtu_size": {
                "required": False,
                "type": "int",
                "default": 9000,
            },
        }
        compute_network_option = {
            "compute_port_protocol": {
                "required": False,
                "type": "str",
                "choices": ["iSCSI", "NVMe/TCP"],
                "default": "iSCSI",
            },
            "compute_network_ip": {
                "required": True,
                "type": "str",
            },
            "compute_network_subnet": {
                "required": False,
                "type": "str",
                "default": "255.255.255.0",
            },
            "compute_network_gateway": {
                "required": False,
                "type": "str",
            },
            "is_compute_network_ipv6_mode": {
                "required": False,
                "type": "bool",
                "default": False,
            },
            "compute_network_ipv6_globals": {
                "required": False,
                "type": "list",
                "elements": "str",
            },
            "compute_network_ipv6_subnet_prefix": {
                "required": False,
                "type": "str",
            },
            "compute_network_ipv6_gateway": {
                "required": False,
                "type": "str",
            },
            "compute_network_mtu_size": {
                "required": False,
                "type": "int",
                "default": 9000,
            },
        }
        control_internode_network_option = {
            "control_internode_network_route_destinations": {
                "required": False,
                "type": "list",
                "elements": "str",
                "default": ["default"],
            },
            "control_internode_network_route_gateways": {
                "required": False,
                "type": "list",
                "elements": "str",
            },
            "control_internode_network_route_interfaces": {
                "required": False,
                "type": "list",
                "elements": "str",
                "default": ["control"],
            },
        }
        storage_node_option = {
            "host_name": {
                "required": True,
                "type": "str",
            },
            "fault_domain_name": {
                "required": True,
                "type": "str",
            },
            "is_cluster_master_role": {
                "required": False,
                "type": "bool",
                "default": False,
            },
            "number_of_fc_target_port": {
                "required": False,
                "type": "int",
                "default": 0,
            },
            "control_network": {
                "required": True,
                "type": "dict",
                "options": control_network_option,
            },
            "internode_network": {
                "required": True,
                "type": "dict",
                "options": internode_network_option,
            },
            "control_internode_network": {
                "required": False,
                "type": "dict",
                "options": control_internode_network_option,
            },
            "compute_networks": {
                "required": True,
                "type": "list",
                "elements": "dict",
                "options": compute_network_option,
            },
        }
        spec_options = {
            "configuration_file": {
                "required": False,
                "type": "str",
            },
            "setup_user_password": {
                "required": False,
                "type": "str",
                "no_log": True,
            },
            "config_file_location": {
                "required": False,
                "type": "str",
            },
            "refresh": {
                "required": False,
                "type": "bool",
                "default": False,
            },
            "storage_nodes": {
                "required": False,
                "type": "list",
                "elements": "dict",
                "options": storage_node_option,
            },
            "node_id": {
                "required": False,
                "type": "str",
            },
            "node_name": {
                "required": False,
                "type": "str",
            },
            "machine_image_id": {
                "required": False,
                "type": "str",
            },
            "is_capacity_balancing_enabled": {
                "required": False,
                "type": "bool",
            },
            "controller_id": {
                "required": False,
                "type": "str",
            },
            "export_file_type": {
                "required": False,
                "type": "str",
                "choices": [
                    "Normal",
                    "AddStorageNodes",
                    # "ReplaceStorageNode",
                    "AddDrives",
                    # "ReplaceDrive",
                ],
                "default": "Normal",
            },
            "no_of_drives": {
                "required": False,
                "type": "int",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments

    @classmethod
    def cluster_facts(cls):
        cls.common_arguments.pop("state")
        cls.common_arguments.pop("spec")
        return cls.common_arguments


class SDSBJobArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "spec": {
            "required": False,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def job_facts(cls):
        spec_options = {
            "id": {
                "required": False,
                "type": "str",
            },
            "count": {
                "required": False,
                "type": "int",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments["spec"]["required"] = False
        return cls.common_arguments


class SDSBStorageNodeArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present", "maintenance", "restore"],
            "default": "present",
        },
        "spec": {
            "required": True,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def storage_node(cls):
        spec_options = {
            "name": {
                "required": False,
                "type": "str",
            },
            "id": {
                "required": False,
                "type": "str",
            },
            "is_capacity_balancing_enabled": {
                "required": False,
                "type": "bool",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments

    @classmethod
    def storage_node_facts(cls):
        spec_options = {
            "fault_domain_id": {
                "required": False,
                "type": "str",
            },
            "id": {
                "required": False,
                "type": "str",
            },
            "name": {
                "required": False,
                "type": "str",
            },
            "cluster_role": {
                "required": False,
                "type": "str",
                "choices": ["Master", "Worker"],
            },
            "protection_domain_id": {
                "required": False,
                "type": "str",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments.pop("state")
        cls.common_arguments["spec"]["required"] = False
        return cls.common_arguments


class SDSBStoragePoolArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present", "expand"],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def storage_pool(cls):
        spec_options = {
            "name": {
                "required": False,
                "type": "str",
            },
            "id": {
                "required": False,
                "type": "str",
            },
            "drive_ids": {
                "required": False,
                "type": "list",
                "elements": "str",
            },
            "rebuild_capacity_policy": {
                "required": False,
                "type": "str",
                "choices": ["Fixed", "Variable"],
            },
            "number_of_tolerable_drive_failures": {
                "required": False,
                "type": "int",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments["spec"]["required"] = True
        return cls.common_arguments

    @classmethod
    def storage_pool_facts(cls):
        spec_options = {
            "names": {
                "required": False,
                "type": "list",
                "elements": "str",
            },
            "id": {
                "required": False,
                "type": "str",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments.pop("state")
        cls.common_arguments["spec"]["required"] = False
        return cls.common_arguments


class SDSBVolumeArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present", "absent"],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def volume(cls):
        spec_options = {
            "id": {
                "required": False,
                "type": "str",
            },
            "name": {
                "required": False,
                "type": "str",
            },
            "nickname": {
                "required": False,
                "type": "str",
            },
            "capacity": {
                "required": False,
                "type": "str",
            },
            "capacity_saving": {
                "required": False,
                "type": "str",
            },
            "pool_name": {
                "required": False,
                "type": "str",
            },
            # "vps_name": {
            #     "required": False,
            #     "type": "str",
            # },
            "state": {
                "required": False,
                "type": "str",
                "choices": [
                    "add_compute_node",
                    "remove_compute_node",
                ],
            },
            "compute_nodes": {
                "required": False,
                "type": "list",
                "elements": "str",
            },
            "qos_param": {
                "required": False,
                "type": "dict",
                "options": {
                    "upper_limit_for_iops": {
                        "required": False,
                        "type": "int",
                    },
                    "upper_limit_for_transfer_rate_mb_per_sec": {
                        "required": False,
                        "type": "int",
                    },
                    "upper_alert_allowable_time_in_sec": {
                        "required": False,
                        "type": "int",
                    },
                },
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments["spec"]["required"] = True
        return cls.common_arguments

    @classmethod
    def volume_facts(cls):
        spec_options = {
            "count": {
                "required": False,
                "type": "int",
                "default": 500,
            },
            "names": {
                "required": False,
                "type": "list",
                "elements": "str",
            },
            "nicknames": {
                "required": False,
                "type": "list",
                "elements": "str",
            },
            "capacity_saving": {
                "required": False,
                "type": "str",
                "choices": ["Disabled", "Compression"],
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments.pop("state")
        cls.common_arguments["spec"]["required"] = False
        return cls.common_arguments


class SDSBPortArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "spec": {
            "required": False,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def port_facts(cls):
        spec_options = {
            "nicknames": {
                "required": False,
                "type": "list",
                "elements": "str",
            },
            "names": {
                "required": False,
                "type": "list",
                "elements": "str",
            },
            # 'protocol': {'required': False, 'type': 'str', 'description': 'Compute nodes that belongs to this vps'},
        }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments


class SDSBPortAuthArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present", "absent"],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def port_auth(cls):
        spec_options = {
            "port_name": {
                "required": False,
                "type": "str",
            },
            "state": {
                "required": False,
                "type": "str",
                "choices": [
                    "add_chap_user",
                    "remove_chap_user",
                ],
            },
            "authentication_mode": {
                "required": False,
                "type": "str",
                "choices": [
                    "CHAP",
                    "CHAP_complying_with_initiator_setting",
                    "None",
                ],
            },
            "is_discovery_chap_authentication": {
                "required": False,
                "type": "bool",
            },
            "target_chap_users": {
                "required": False,
                "type": "list",
                "elements": "str",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments["spec"]["required"] = True
        return cls.common_arguments


class SDSBSnapshotArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present", "absent", "restore"],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def snapshot_args(cls):
        spec_options = {
            "name": {
                "required": False,
                "type": "str",
            },
            "master_volume_name": {
                "required": False,
                "type": "str",
            },
            "master_volume_id": {
                "required": False,
                "type": "str",
            },
            "snapshot_volume_name": {
                "required": False,
                "type": "str",
            },
            "snapshot_volume_id": {
                "required": False,
                "type": "str",
            },
            "operation_type": {
                "required": False,
                "type": "str",
                "choices": ["prepare_and_finalize", "prepare", "finalize"],
            },
            "vps_id": {"required": False, "type": "str"},
            "vps_name": {"required": False, "type": "str"},
            "qos": {
                "required": False,
                "type": "dict",
                "options": {
                    "upper_limit_for_iops": {"required": False, "type": "int"},
                    "upper_limit_for_transfer_rate": {"required": False, "type": "int"},
                    "upper_alert_allowable_time": {"required": False, "type": "int"},
                },
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments["spec"]["required"] = True
        return cls.common_arguments

    @classmethod
    def snapshot_facts_args(cls):
        spec_options = {
            "master_volume_name": {
                "required": False,
                "type": "str",
            },
            "master_volume_id": {
                "required": False,
                "type": "str",
            },
            "snapshot_volume_name": {
                "required": False,
                "type": "str",
            },
            "snapshot_volume_id": {
                "required": False,
                "type": "str",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments["spec"]["required"] = True
        cls.common_arguments.pop("state")
        return cls.common_arguments


class SDSBTicketManagementArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present", "absent"],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def ticket_management(cls):
        spec_options = {
            "max_age_days": {
                "required": False,
                "type": "int",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments


class SDSBChapUserArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present", "absent"],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def chap_user(cls):
        spec_options = {
            "id": {
                "required": False,
                "type": "str",
            },
            "target_chap_user_name": {
                "required": False,
                "type": "str",
            },
            "target_chap_secret": {
                "required": False,
                "type": "str",
                "no_log": True,
            },
            "initiator_chap_user_name": {
                "required": False,
                "type": "str",
            },
            "initiator_chap_secret": {
                "required": False,
                "type": "str",
                "no_log": True,
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments["spec"]["required"] = True
        return cls.common_arguments

    @classmethod
    def chap_user_facts(cls):
        spec_options = {
            "id": {
                "required": False,
                "type": "str",
            },
            "target_chap_user_name": {
                "required": False,
                "type": "str",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments["spec"]["required"] = False
        cls.common_arguments.pop("state")

        return cls.common_arguments


class SDSBEventLogsArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present", "absent"],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def event_log_facts(cls):
        spec_options = {
            "severity": {
                "required": False,
                "type": "str",
                "choices": ["Info", "Warning", "Error", "Critical"],
            },
            "severity_ge": {
                "required": False,
                "type": "str",
                "choices": ["Info", "Warning", "Error", "Critical"],
            },
            "start_time": {
                "required": False,
                "type": "str",
                # "format": "date-time",
            },
            "end_time": {
                "required": False,
                "type": "str",
                # "format": "date-time",
            },
            "max_events": {
                "required": False,
                "type": "int",
                "default": 1000,
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments["spec"]["required"] = False
        cls.common_arguments.pop("state")

        return cls.common_arguments


class SDSBDrivesArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present", "absent"],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def drive(cls):
        spec_options = {
            "id": {
                "required": True,
                "type": "str",
            },
            "should_drive_locator_led_on": {
                "required": False,
                "type": "bool",
                "default": False,
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments["spec"]["required"] = True

        return cls.common_arguments

    @classmethod
    def drives_facts(cls):
        spec_options = {
            "status_summary": {
                "required": False,
                "type": "str",
                "choices": ["Normal", "Warning", "Error"],
            },
            "status": {
                "required": False,
                "type": "str",
                "choices": ["Offline", "Normal", "TemporaryBlockage", "Blockage"],
            },
            "storage_node_id": {
                "required": False,
                "type": "str",
                # "format": "uuid",
            },
            "locator_led_status": {
                "required": False,
                "type": "str",
                "choices": ["On", "Off"],
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments["spec"]["required"] = False
        cls.common_arguments.pop("state")

        return cls.common_arguments


class SDSBStotagrNodeBmcAccessSettingArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "spec": {
            "required": False,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def storage_node_bmc_access_setting_facts(cls):
        spec_options = {
            "id": {
                "required": True,
                "type": "str",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        return cls.common_arguments


class SDSBControlPortArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "spec": {
            "required": False,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def control_port_facts(cls):
        spec_options = {
            "id": {
                "required": False,
                "type": "str",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments["spec"]["required"] = False
        # cls.common_arguments.pop("state")

        return cls.common_arguments

    @classmethod
    def storage_node_nw_setting_port_facts(cls):
        spec_options = {
            "id": {
                "required": False,
                "type": "str",
            },
            "storage_node_name": {
                "required": False,
                "type": "str",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments["spec"]["required"] = False
        # cls.common_arguments.pop("state")

        return cls.common_arguments


class SDSBFaultDomainArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present", "absent"],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def fault_domain_facts(cls):
        spec_options = {
            "id": {
                "required": False,
                "type": "str",
            },
            "name": {
                "required": False,
                "type": "str",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments["spec"]["required"] = False
        cls.common_arguments.pop("state")

        return cls.common_arguments


class SDSBUsersArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present", "update"],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def users(cls):
        spec_options = {
            # "id": {
            #     "required": False,
            #     "type": "str",
            # },
            "user_id": {
                "required": False,
                "type": "str",
            },
            "password": {
                "required": False,
                "type": "str",
                "no_log": True,
            },
            "user_group_ids": {
                "required": False,
                "type": "list",
                "elements": "str",
            },
            "authentication": {
                "required": False,
                "type": "str",
                "choices": ["local", "external"],
                "default": "local",
            },
            "is_enabled_console_login": {
                "required": False,
                "type": "bool",
                "default": True,
            },
            "current_password": {
                "required": False,
                "type": "str",
                "no_log": True,
            },
            "new_password": {
                "required": False,
                "type": "str",
                "no_log": True,
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments["spec"]["required"] = False
        # cls.common_arguments.pop("state")

        return cls.common_arguments

    @classmethod
    def user_facts(cls):
        spec_options = {
            "id": {
                "required": False,
                "type": "str",
            },
            # "name": {
            #     "required": False,
            #     "type": "str",
            # },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments["spec"]["required"] = False
        cls.common_arguments.pop("state")

        return cls.common_arguments


class SDSBCapacityManagementSettingsArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present"],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def capacity_management_settings(cls):
        spec_options = {
            "storage_controller_id": {
                "required": False,
                "type": "str",
            },
            "is_detailed_logging_mode": {
                "required": False,
                "type": "bool",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options

        return cls.common_arguments

    @classmethod
    def capacity_management_settings_facts(cls):
        spec_options = {
            "storage_controller_id": {
                "required": False,
                "type": "str",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments.pop("state")

        return cls.common_arguments


class SDSBEstimatedCapacityArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "spec": {
            "required": True,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def estimated_capacity_facts(cls):
        spec_options = {
            "id": {
                "required": False,
                "type": "str",
            },
            "name": {
                "required": False,
                "type": "str",
            },
            "number_of_storage_nodes": {
                "required": True,
                "type": "int",
            },
            "number_of_drives": {
                "required": True,
                "type": "int",
            },
            "number_of_tolerable_drive_failures": {
                "required": True,
                "type": "int",
            },
            "query": {
                "required": True,
                "type": "str",
                "choices": ["specified_configuration", "updated_configuration"],
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options

        return cls.common_arguments


class SDSBStorageControllerArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present"],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def storage_controller(cls):
        spec_options = {
            "id": {
                "required": False,
                "type": "str",
            },
            "is_detailed_logging_mode": {
                "required": False,
                "type": "bool",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options

        return cls.common_arguments

    @classmethod
    def storage_controller_facts(cls):
        spec_options = {
            "primary_fault_domain_id": {
                "required": False,
                "type": "str",
            },
            "primary_fault_domain_name": {
                "required": False,
                "type": "str",
            },
            "id": {
                "required": False,
                "type": "str",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments.pop("state")

        return cls.common_arguments


class SDSBStorageSystemArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
    }

    @classmethod
    def storage_system_fact(cls):
        return cls.common_arguments


class SDSBVpsArguments:

    common_arguments = {
        "connection_info": SDSBCommonParameters.get_connection_info(),
        "state": {
            "required": False,
            "type": "str",
            "choices": ["present", "absent"],
            "default": "present",
        },
        "spec": {
            "required": False,
            "type": "dict",
            "options": {},
        },
    }

    @classmethod
    def vps(cls):
        spec_options = {
            "vps_name": {
                "required": False,
                "type": "str",
            },
            "vps_id": {
                "required": False,
                "type": "str",
            },
            # "id": {
            #     "required": False,
            #     "type": "str",
            # },
            # "name": {
            #     "required": False,
            #     "type": "str",
            # },
            # "upper_limit_for_number_of_user_groups": {
            #     "required": False,
            #     "type": "int",
            # },
            # "upper_limit_for_number_of_users": {
            #     "required": False,
            #     "type": "int",
            # },
            # "upper_limit_for_number_of_sessions": {
            #     "required": False,
            #     "type": "int",
            # },
            # "upper_limit_for_number_of_servers": {
            #     "required": False,
            #     "type": "int",
            # },
            # "volume_settings": {
            #     "required": False,
            #     "type": "list",
            # },
            "capacity_saving": {
                "required": False,
                "type": "str",
                "choices": ["Disabled", "Compression"],
                "default": "Disabled",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments["spec"]["required"] = True
        return cls.common_arguments

    @classmethod
    def vps_facts(cls):
        spec_options = {
            "id": {
                "required": False,
                "type": "str",
            },
            "name": {
                "required": False,
                "type": "str",
            },
        }
        cls.common_arguments["spec"]["options"] = spec_options
        cls.common_arguments.pop("state")
        cls.common_arguments["spec"]["required"] = False
        return cls.common_arguments


# Validator functions
class SDSBSpecValidators:

    @staticmethod
    def validate_connection_info(conn_info: ConnectionInfo):

        if conn_info.connection_type == ConnectionTypes.DIRECT and conn_info.api_token:
            raise ValueError(SDSBConnectionValidationMsg.DIRECT_API_TOKEN_ERROR.value)
        elif conn_info.username and conn_info.password and conn_info.api_token:
            raise ValueError(
                SDSBConnectionValidationMsg.BOTH_API_TOKEN_USER_DETAILS.value
            )
        elif (
            not conn_info.username
            and not conn_info.password
            and not conn_info.api_token
        ):
            raise ValueError(
                SDSBConnectionValidationMsg.NOT_API_TOKEN_USER_DETAILS.value
            )

    @staticmethod
    def validate_volume_spec(state, input_spec: VolumeSpec):

        if input_spec.qos_param:
            if input_spec.qos_param.upper_limit_for_iops:
                if input_spec.qos_param.upper_limit_for_iops != -1:
                    if (
                        input_spec.qos_param.upper_limit_for_iops
                        < AutomationConstants.QOS_UPPER_LIMIT_IOPS_MIN
                        or input_spec.qos_param.upper_limit_for_iops
                        > AutomationConstants.QOS_UPPER_LIMIT_IOPS_MAX
                    ):
                        raise ValueError(
                            SDSBVolValidationMsg.QOS_UPPER_LIMIT_IOPS_OUT_OF_RANGE.value
                        )
            if input_spec.qos_param.upper_limit_for_transfer_rate_mb_per_sec:
                if input_spec.qos_param.upper_limit_for_transfer_rate_mb_per_sec != -1:
                    if (
                        input_spec.qos_param.upper_limit_for_transfer_rate_mb_per_sec
                        < AutomationConstants.QOS_UPPER_LIMIT_XFER_RATE_MIN
                        or input_spec.qos_param.upper_limit_for_transfer_rate_mb_per_sec
                        > AutomationConstants.QOS_UPPER_LIMIT_XFER_RATE_MAX
                    ):
                        raise ValueError(
                            SDSBVolValidationMsg.QOS_UPPER_LIMIT_XFER_RATE_OUT_OF_RANGE.value
                        )
            if input_spec.qos_param.upper_alert_allowable_time_in_sec:
                if input_spec.qos_param.upper_alert_allowable_time_in_sec != -1:
                    if (
                        input_spec.qos_param.upper_alert_allowable_time_in_sec
                        < AutomationConstants.QOS_UPPER_ALERT_ALLOWABLE_TIME_OUT_MIN
                        or input_spec.qos_param.upper_alert_allowable_time_in_sec
                        > AutomationConstants.QOS_UPPER_ALERT_ALLOWABLE_TIME_OUT_MAX
                    ):
                        raise ValueError(
                            SDSBVolValidationMsg.QOS_UPPER_ALERT_ALLOWABLE_TIME_OUT_OF_RANGE.value
                        )

    @staticmethod
    def validate_job_facts_spec(spec: JobFactSpec):
        if spec and spec.count:
            if (
                spec.count < AutomationConstants.JOB_COUNT_MIN
                or spec.count > AutomationConstants.JOB_COUNT_MAX
            ):
                raise ValueError(SDSBJobValidationMsg.INVALID_COUNT.value)

    @staticmethod
    def validate_event_log_facts_spec(spec: EventLogFactSpec):
        if spec and spec.severity and spec.severity_ge:
            raise ValueError(SDSBEventLogValidationMsg.BOTH_SEVERITY_SPECIFIED.value)

    @staticmethod
    def validate_drive_spec(spec: SDSBDriveSpec):
        if spec and spec.id is None:
            raise ValueError(SDSBEventLogValidationMsg.BOTH_SEVERITY_SPECIFIED.value)

    @staticmethod
    def validate_storage_pool_spec(spec):
        if spec.name is None and spec.id is None:
            raise ValueError(SDSBStoragePoolValidationMsg.BOTH_ID_AND_NAME_NONE.value)
        if spec and spec.number_of_tolerable_drive_failures:
            if (
                spec.number_of_tolerable_drive_failures < 0
                or spec.number_of_tolerable_drive_failures > 23
            ):
                raise ValueError(
                    SDSBStoragePoolValidationMsg.TOLERABLE_DRIVES_OUT_OF_RANGE.value
                )
        if (
            spec
            and spec.rebuild_capacity_policy and spec.rebuild_capacity_policy == "Fixed"
            and spec.number_of_tolerable_drive_failures is None
        ):
            raise ValueError(
                SDSBStoragePoolValidationMsg.MUST_SPECIFY_NO_OF_TOLERABLE_DRIVES.value
            )
        if (
            spec
            and spec.number_of_tolerable_drive_failures
            and spec.rebuild_capacity_policy is None
        ):
            raise ValueError(
                SDSBStoragePoolValidationMsg.MUST_SPECIFY_REBUILD_CAPACITY_POLICY.value
            )

    @staticmethod
    def validate_estimated_capacity_fact_spec(spec):
        if spec.id is None and spec.name is None:
            raise ValueError(
                SDSBEstimatedCapacityValidateMsg.BOTH_ID_AND_NAME_NONE.value
            )
        # if spec.number_of_storage_nodes is None and spec.number_of_drives is None and spec.number_of_tolerable_drive_failures is None:
        #     raise ValueError(SDSBEstimatedCapacityValidateMsg.ONE_INPUT_NEEDED.value)


def camel_to_snake(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def convert_keys_to_snake_case(obj):
    if isinstance(obj, dict):
        return {
            camel_to_snake(k): convert_keys_to_snake_case(v) for k, v in obj.items()
        }
    elif isinstance(obj, list):
        return [convert_keys_to_snake_case(item) for item in obj]
    else:
        return obj


# Function to recursively replace None with ""
def replace_nulls(obj):
    if isinstance(obj, dict):
        return {k: replace_nulls(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [replace_nulls(item) for item in obj]
    elif obj is None:
        return ""
    else:
        return obj
