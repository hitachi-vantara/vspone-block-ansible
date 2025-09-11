from enum import Enum


class SDSBClusterValidationMsg(Enum):
    NO_NAME_OR_ID_FOR_STORAGE_NODE = "Either node_name or node_id of the storage node must be specified to do this operation."
    STORAGE_NODE_NOT_FOUND = "Did not find storage node named {}."
    STORAGE_NODE_SETUP_PASSWD_REQD = (
        "Storage node setup_user_password is a required field, which is missing."
    )
    CONFIG_FILE_DOES_NOT_EXIST = (
        "File path ({}) provided for the configuration_file does not exist."
    )
    COFIG_FILE_OR_SROARGE_NODES_REQD = (
        "Either configuration_file or storage_nodes must be specified."
    )
    INVALID_SUBNET_MASK = "Subnet mask 255.255.255.255 or 0.0.0.0 cannot be specified."
    FD_NOT_IN_CLUSTER = "The fault_domain_name {} specified in the spec not present in the cluster, cluster's fault domains = {}."
    CONTROL_IP_ALREADY_IN_CLUSTER = (
        "The control_network_ip {} specified in the spec is already present in the cluster, "
        "cluster's control network IPs = {}."
    )
    INTER_NODE_IP_ALREADY_IN_CLUSTER = (
        "The internode_network_ip {} specified in the spec is already present in the cluster, cluster's inter node network IPs = {}."
    )
    COMPUTE_IP_ALREADY_IN_CLUSTER = "The compute_network_ip {} specified in the spec is already present in the cluster, cluster's compute network IPs = {}."
    SPEC_NONE = "Spec can't be null for add_storage_node operation."
    MACHINE_IMAGE_ID_REQD = (
        "For Azure, machine_image_id is a requird field for adding a node."
    )
    SPEC_REQD_CONFIG_CLOUD = (
        "On cloud platform spec is required to create a configuration file."
    )
    EXPORT_FILE_TYPE_REQD_CONFIG_CLOUD = "On the {} Cloud Platform, export_file_type is required to create a configuration file."
    INVALID_EXPORT_FILE_TYPE = (
        "Invalid value provided for export_file_type attribute in the spec for {} cloud platform."
        "Valid values for export_file_type for this cloud platform are {}."
    )
    MACHINE_IMAGE_ID_REQD_CONFIG_CLOUD = "On the {} Cloud Platform, machine_image_id is required for the specified operation to create a configuration file."
    NO_OF_DRIVES_REQD_CONFIG_CLOUD = "On the {} Cloud Platform, no_of_drives is required for the specified operation to create a configuration file."
    OPERATION_NOT_SUPPORTED_YET = "On the {} Cloud Platform, the specified operation to create a configuration file is not supported yet."
