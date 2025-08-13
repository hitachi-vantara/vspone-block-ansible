import time
import os
from typing import Any

try:
    from ..provisioner.sdsb_cluster_provisioner import SDSBClusterProvisioner
    from ..provisioner.sdsb_storage_node_provisioner import SDSBStorageNodeProvisioner
    from ..common.hv_constants import StateValue
    from ..common.hv_log import Log
    from ..common.ansible_common import (
        log_entry_exit,
        unzip_targz,
    )
    from ..model.sdsb_cluster_models import ControlInternodeNetworkSpec
    from ..message.sdsb_cluster_msgs import SDSBClusterValidationMsg
except ImportError:
    from provisioner.sdsb_cluster_provisioner import SDSBClusterProvisioner
    from provisioner.sdsb_storage_node_provisioner import SDSBStorageNodeProvisioner
    from common.hv_log import Log
    from common.ansible_common import (
        log_entry_exit,
        unzip_targz,
    )
    from model.sdsb_cluster_models import ControlInternodeNetworkSpec
    from message.sdsb_cluster_msgs import SDSBClusterValidationMsg

logger = Log()


def get_json_for_config_file(file_path):
    result = {}
    current_section = None
    headers = []

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  # skip empty lines

            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1]
                result[current_section] = []
                headers = []
                continue

            if current_section:
                # Handle the first line of the section as headers
                if not headers:
                    headers = line.split(",")
                    continue

                # Parse data lines
                values = line.split(",")
                row_dict = {
                    headers[i]: values[i] if i < len(values) else ""
                    for i in range(len(headers))
                }
                result[current_section].append(row_dict)

    return result


class SDSBClusterReconciler:

    def __init__(self, connection_info, state=None):
        self.connection_info = connection_info
        self.provisioner = SDSBClusterProvisioner(self.connection_info)
        self.state = state

    @log_entry_exit
    def get_clusters(self, spec=None):
        json_object = self.get_cluster_config()
        new_json = SDSBClusterExtractor().extract(json_object)
        return new_json

    @log_entry_exit
    def get_cluster_config(self):
        dest_folder = self.download_and_unzip_config_file()
        file_name = "SystemConfigurationFile.csv"
        file_path = f"{dest_folder}/{file_name}"
        json_object = get_json_for_config_file(file_path)
        return json_object

    @log_entry_exit
    def reconcile_cluster(self, spec: Any) -> Any:
        state = self.state.lower()
        logger.writeDebug(f"spec = {spec}")
        resp_data = None
        if state == StateValue.ADD_STORAGE_NODE:
            resp_data = self.add_storage_node(spec=spec)
        elif state == StateValue.REMOVE_STORAGE_NODE:
            resp_data = self.remove_storage_node(spec=spec)
        elif state == StateValue.DOWNLOAD_CONFIG_FILE:
            resp_data = self.download_config_file(spec=spec)
        if resp_data:
            return resp_data

    @log_entry_exit
    def validate_input_for_storage_nodes(self, spec, json_object):
        logger.writeDebug(f"spec = {spec}")

        if spec.storage_nodes is None or len(spec.storage_nodes) == 0:
            raise ValueError(
                SDSBClusterValidationMsg.COFIG_FILE_OR_SROARGE_NODES_REQD.value
            )

        cluster_fault_domains = json_object.get("fault_domains")
        cluster_fault_domain_names = []
        for x in cluster_fault_domains:
            cluster_fault_domain_names.append(x.get("fault_domain_name"))

        cluster_control_nw_ips = []
        cluster_inter_node_nw_ips = []
        cluster_compute_nw_ips = []
        control_internode_nw_route_gws = set()
        cluster_nodes = json_object.get("nodes")
        logger.writeDebug(f"cluster_nodes = {cluster_nodes}")
        for x in cluster_nodes:
            cluster_control_nw_ips.append(x.get("control_network_ip"))
            cluster_inter_node_nw_ips.append(x.get("internode_network_ip"))
            cluster_compute_nw_ips.append(
                x.get("compute_network_ip_1")
            )  # Add logic to find out compute_network_ip_2 etc.
            control_internode_nw_route_gws.add(
                x.get("control_internode_network_route_gateway_1")
            )

        # logger.writeDebug(f"cluster_control_nw_ips = {cluster_control_nw_ips}")
        # logger.writeDebug(f"cluster_inter_node_nw_ips = {cluster_inter_node_nw_ips}")
        # logger.writeDebug(f"cluster_compute_nw_ips = {cluster_compute_nw_ips}")
        # logger.writeDebug(f"control_internode_nw_route_gws = {control_internode_nw_route_gws}")

        for storage_node in spec.storage_nodes:
            if storage_node.fault_domain_name not in cluster_fault_domain_names:
                raise ValueError(
                    SDSBClusterValidationMsg.FD_NOT_IN_CLUSTER.value.format(
                        storage_node.fault_domain_name, cluster_fault_domain_names
                    )
                )
            if (
                storage_node.control_network.control_network_ip
                in cluster_control_nw_ips
            ):
                raise ValueError(
                    SDSBClusterValidationMsg.CONTROL_IP_ALREADY_IN_CLUSTER.value.format(
                        storage_node.control_network.control_network_ip,
                        cluster_control_nw_ips,
                    )
                )
            if (
                storage_node.internode_network.internode_network_ip
                in cluster_inter_node_nw_ips
            ):
                raise ValueError(
                    SDSBClusterValidationMsg.INTER_NODE_IP_ALREADY_IN_CLUSTER.value.format(
                        storage_node.internode_network.internode_network_ip,
                        cluster_inter_node_nw_ips,
                    )
                )
            spec_compute_nws = storage_node.compute_networks
            for x in spec_compute_nws:
                if x.compute_network_ip in cluster_compute_nw_ips:
                    raise ValueError(
                        SDSBClusterValidationMsg.COMPUTE_IP_ALREADY_IN_CLUSTER.value.format(
                            x.compute_network_ip,
                            cluster_compute_nw_ips,
                        )
                    )
            if storage_node.control_network.control_network_subnet:
                subnet_mask = storage_node.control_network.control_network_subnet
                if subnet_mask == "255.255.255.255" or subnet_mask == "0.0.0.0":
                    raise ValueError(SDSBClusterValidationMsg.INVALID_SUBNET_MASK.value)
            if storage_node.internode_network.internode_network_subnet:
                subnet_mask = storage_node.internode_network.internode_network_subnet
                if subnet_mask == "255.255.255.255" or subnet_mask == "0.0.0.0":
                    raise ValueError(SDSBClusterValidationMsg.INVALID_SUBNET_MASK.value)
            if storage_node.compute_networks and len(storage_node.compute_networks):
                for cn in storage_node.compute_networks:
                    if cn.compute_network_subnet:
                        subnet_mask = cn.compute_network_subnet
                        if subnet_mask == "255.255.255.255" or subnet_mask == "0.0.0.0":
                            raise ValueError(
                                SDSBClusterValidationMsg.INVALID_SUBNET_MASK.value
                            )

            if storage_node.control_internode_network is None:
                storage_node.control_internode_network = ControlInternodeNetworkSpec()
                storage_node.control_internode_network.control_internode_network_route_destinations = [
                    "default"
                ]
                storage_node.control_internode_network.control_internode_network_route_gateways = list(
                    control_internode_nw_route_gws
                )
                storage_node.control_internode_network.control_internode_network_route_interfaces = [
                    "control"
                ]
            else:
                if (
                    storage_node.control_internode_network.control_internode_network_route_destinations
                    is None
                ):
                    storage_node.control_internode_network.control_internode_network_route_destinations = [
                        "default"
                    ]
                if (
                    storage_node.control_internode_network.control_internode_network_route_gateways
                    is None
                ):
                    storage_node.control_internode_network.control_internode_network_route_gateways = list(
                        control_internode_nw_route_gws
                    )
                if (
                    storage_node.control_internode_network.control_internode_network_route_interfaces
                    is None
                ):
                    storage_node.control_internode_network.control_internode_network_route_interfaces = [
                        "control"
                    ]

            logger.writeDebug(f"spec2 = {spec}")

    @log_entry_exit
    def get_line_entries(self, spec):
        lines = []
        for storage_node in spec.storage_nodes:
            host_name = storage_node.host_name
            fault_domain_name = storage_node.fault_domain_name
            cluster_master_role = ""
            if storage_node.is_cluster_master_role is True:
                cluster_master_role = "clustermaster"
            control_nw_ip_v4 = storage_node.control_network.control_network_ip
            control_nw_ip_v4_subnet = (
                storage_node.control_network.control_network_subnet
            )
            control_nw_ip_v4_size = (
                storage_node.control_network.control_network_mtu_size
            )

            internode_nw_ip_v4 = storage_node.internode_network.internode_network_ip
            internode_nw_ip_v4_subnet = (
                storage_node.internode_network.internode_network_subnet
            )
            internode_nw_ip_v4_size = (
                storage_node.internode_network.internode_network_mtu_size
            )
            control_internode_network = storage_node.control_internode_network
            ctrl_in_nw_route_dests = ""
            for (
                x
            ) in control_internode_network.control_internode_network_route_destinations:
                ctrl_in_nw_route_dests = ctrl_in_nw_route_dests + x + ","

            ctrl_in_nw_route_gws = ""
            for x in control_internode_network.control_internode_network_route_gateways:
                ctrl_in_nw_route_gws = ctrl_in_nw_route_gws + x + ","

            ctrl_in_nw_route_if = ""
            for (
                x
            ) in control_internode_network.control_internode_network_route_interfaces:
                ctrl_in_nw_route_if = ctrl_in_nw_route_if + x + ","

            no_of_fc_ports = 0
            if storage_node.number_of_fc_target_port:
                no_of_fc_ports = storage_node.number_of_fc_target_port

            compute_nw_str = ""
            for x in storage_node.compute_networks:
                if x.compute_port_protocol:
                    compute_nw_str = compute_nw_str + x.compute_port_protocol + ","
                else:
                    compute_nw_str = compute_nw_str + "iSCSI" + ","
                compute_nw_str = compute_nw_str + x.compute_network_ip + ","
                compute_nw_str = compute_nw_str + x.compute_network_subnet + ","
                compute_nw_str = (
                    compute_nw_str + x.compute_network_gateway + ","
                )  # Find the GW from the file??
                if (
                    x.is_compute_network_ipv6_mode
                    and x.is_compute_network_ipv6_mode is True
                ):
                    compute_nw_str = compute_nw_str + "Enable" + ","
                    # Add code for IP v6 entries
                else:
                    compute_nw_str = compute_nw_str + "Disable" + ","
                    compute_nw_str = compute_nw_str + ",,,"
                compute_nw_str = compute_nw_str + str(x.compute_network_mtu_size)

            line = (
                f"{host_name},{fault_domain_name},{cluster_master_role},{control_nw_ip_v4},{control_nw_ip_v4_subnet},{control_nw_ip_v4_size},"
                f"{internode_nw_ip_v4},{internode_nw_ip_v4_subnet},{internode_nw_ip_v4_size},{ctrl_in_nw_route_dests}{ctrl_in_nw_route_gws}"
                f"{ctrl_in_nw_route_if}{no_of_fc_ports},{compute_nw_str}"
            )

            lines.append(line)

        return lines

    @log_entry_exit
    def add_storage_node(self, spec=None):
        cloud_platforms = ["Google, Inc.", "Msft", "aws", "AWS", "Aws"]
        platform = self.provisioner.get_platform()
        logger.writeDebug(f"add_storage_node:spec = {spec}  platform = {platform}")
        if platform in cloud_platforms and spec.setup_user_password is None:
            spec.setup_user_password = "Hitachi1"  # set dummpy password for clouds

        if spec.setup_user_password is None:
            raise ValueError(
                SDSBClusterValidationMsg.STORAGE_NODE_SETUP_PASSWD_REQD.value
            )
        if spec.configuration_file:
            if not os.path.isfile(spec.configuration_file):
                raise ValueError(
                    SDSBClusterValidationMsg.CONFIG_FILE_DOES_NOT_EXIST.value.format(
                        spec.configuration_file
                    )
                )
        else:
            dest_folder = self.download_and_unzip_config_file()
            file_name = "SystemConfigurationFile.csv"
            file_path = f"{dest_folder}/{file_name}"
            json_object = get_json_for_config_file(file_path)
            logger.writeDebug(f"json_object = {json_object}")
            new_json = SDSBClusterExtractor().extract(json_object)
            logger.writeDebug(f"new_json = {new_json}")
            self.validate_input_for_storage_nodes(spec, new_json)
            line_entries = self.get_line_entries(spec)
            self.append_lines_to_config_file(file_path, line_entries)
            spec.configuration_file = file_path
            # msg = f"""
            # Testing the construction of the file line
            # Here is the line:
            # {line_entries}
            # """
            # return msg

        resp = self.provisioner.add_storage_node(
            spec.configuration_file, spec.setup_user_password
        )
        msg = f"""
        Successfully started add storage node to the cluster job. This is a long running operation, and might take an hour or so.
        You can check the status of the job started periodically using hv_sds_block_job_facts module.
        ID for this job = {resp}
        """
        self.connection_info.changed = True
        return msg

    @log_entry_exit
    def append_lines_to_config_file(self, file_path, lines_to_append):
        try:
            # Open the file in append mode ('a')
            with open(file_path, "a") as file:
                # Iterate through the list of lines and write each to the file
                for line in lines_to_append:
                    file.write(line)
            logger.writeDebug(
                f"Lines {lines_to_append} successfully appended to {file_path}"
            )

        except IOError as e:
            raise ValueError(f"Error appending to file: {e}")

    @log_entry_exit
    def remove_storage_node(self, spec):
        if spec.node_id is None and spec.node_name is None:
            raise ValueError(
                SDSBClusterValidationMsg.NO_NAME_OR_ID_FOR_STORAGE_NODE.value
            )
        try:
            if spec.node_id is None:
                storage_node_prov = SDSBStorageNodeProvisioner(self.connection_info)
                spec.node_id = storage_node_prov.get_node_id_by_node_name(
                    spec.node_name
                )
                if spec.node_id is None:
                    raise ValueError(
                        SDSBClusterValidationMsg.STORAGE_NODE_NOT_FOUND.value.format(
                            spec.node_name
                        )
                    )
            resp = self.provisioner.remove_storage_node(spec.node_id)
            msg = f"""
            Successfully started remove storage node from the cluster job. This is a long running operation, and might take few hours.
            You can check the status of the job started periodically using hv_sds_block_job_facts module.
            ID for this job = {resp}
            """
            self.connection_info.changed = True
            return msg
        except Exception as e:
            logger.writeException(e)
            raise Exception(e)

    @log_entry_exit
    def create_config_file(self, spec=None):
        logger.writeDebug(f"PROV:create_config_file:spec={spec}")
        if spec and spec.export_file_type:
            self.provisioner.create_config_file(spec.export_file_type)
        else:
            self.provisioner.create_config_file("normal")

    @log_entry_exit
    def download_and_unzip_config_file(self, spec=None):
        try:
            time_stamp = time.time_ns()
            file_name = f"/tmp/config_file_{time_stamp}.zip"
            self.provisioner.download_config_file(file_name)

            file_to_unzip = file_name
            if spec is None or spec.config_file_location is None:
                destination_folder = f"/tmp/{time_stamp}"
            else:
                destination_folder = spec.config_file_location
            resp = unzip_targz(file_to_unzip, destination_folder)
            if "Successfully" in resp:
                return destination_folder
            else:
                return None
        except Exception as e:
            logger.writeException(e)
            raise Exception(e)

    @log_entry_exit
    def download_config_file(self, spec):
        try:
            if spec.refresh and spec.refresh is True:
                self.create_config_file(spec)
                self.connection_info.changed = True
            resp = self.download_and_unzip_config_file(spec)
            if resp:
                return f"Successfully downloaded SystemConfigurationFile.csv in the directory {resp}."
            else:
                return "Failed to  downloaded SystemConfigurationFile.csv in the directory."
        except Exception as e:
            logger.writeException(e)
            raise Exception(e)

    @log_entry_exit
    def get_storage_time_settings(self):
        return self.provisioner.get_storage_time_settings()


class SDSBClusterExtractor:
    def __init__(self):
        self.parameter_mapping = {
            "General": "general",
            "SSHConnectWait(sec)": "ssh_connection_wait_in_sec",
            "ClusterReadyWait(sec)": "cluster_ready_wait_in_sec",
            "StartupWait(sec)": "startup_wait_in_sec",
            "ReplicaSetMemberAddWait(sec)": "replica_set_member_add_wait_in_sec",
            "ReplicaSetCompletionWait(sec)": "replica_set_completion_wait_in_sec",
            "DataModelCRUDOperationWait(sec)": "data_model_crud_operation_wait_in_sec",
            "Watchdog-msec": "watchdog_in_msec",
            "CSVversion": "cvs_version",
            "Cluster": "cluster",
            "ClusterName": "cluster_name",
            "vCenterServerHostName": "vcenter_server_host_name",
            "DataCenterName": "data_center_name",
            "TemplateFileName": "template_file_name",
            "NtpServer1": "ntp_server_1",
            "NtpServer2": "ntp_server_2",
            "Timezone": "time_zone",
            "DnsServer1": "dns_server_1",
            "DnsServer2": "dns_server_2",
            "ClusterIpv4Address": "cluster_ip_v4_address",
            "ProtectionDomains": "protection_domains",
            "ProtectionDomainName": "protection_domain_name",
            "StoragePoolName": "storage_pool_name",
            "RedundantPolicy": "redundant_policy",
            "RedundantType": "redundant_type",
            "AsyncProcessingResourceUsageRate": "async_processing_resource_usage_rate",
            "FaultDomains": "fault_domains",
            "FaultDomainName": "fault_domain_name",
            "FCPortSetting": "fc_port_setting",
            "Topology": "topology",
            "Speed": "speed",
            "Nodes": "nodes",
            "HostName": "host_name",
            "VMName": "vm_name",
            "ClusterMasterRole": "cluster_master_role",
            "ControlNWIPv4": "control_network_ip",
            "ControlNWIPv4Subnet": "control_network_subnet",
            "ControlNWMTUSize": "control_network_mtu_size",
            "InterNodeNWPortGroupName": "internode_network_port_group_name",
            "InterNodeNWIPv4": "internode_network_ip",
            "InterNodeNWIPv4Subnet": "internode_network_subnet",
            "InterNodeNWMTUSize": "internode_network_mtu_size",
            "ControlInterNodeNWIPv4RouteDestination1": "control_internode_network_route_destination_1",
            "ControlInterNodeNWIPv4RouteGateway1": "control_internode_network_route_gateway_1",
            "ControlInterNodeNWIPv4RouteInterface1": "control_internode_network_route_interface_1",
            "NumberOfFCTargetPort": "number_of_fc_target_port",
            "ComputePortProtocol1": "compute_port_protocol_1",
            "ComputeNWPortGroupName1": "compute_network_port_group_name_1",
            "ComputeNWIPv4Address1": "compute_network_ip_1",
            "ComputeNWIPv4Subnet1": "compute_network_subnet_1",
            "ComputeNWIPv4Gateway1": "compute_network_gateway_1",
            "ComputeNWIPv6Mode1": "compute_network_ip_v6_mode_1",
            "ComputeNWIPv6Global1_1": "compute_network_ipv6_global_1_1",
            "ComputeNWIPv6SubnetPrefix1": "compute_network_ipv6_subnet_prefix_1",
            "ComputeNWIPv6Gateway1": "compute_network_ipv6_gateway_1",
            "ComputeNWMTUSize1": "compute_network_mtu_size_1",
        }

    def process_list(self, response_key):
        new_items = []

        if response_key is None:
            return []
        for item in response_key:
            new_dict = {}
            for key, value in item.items():
                key = self.parameter_mapping.get(key, None)
                # key = camel_to_snake_case(key)

                if value is None:
                    # default_value = get_default_value(value_type)
                    # value = default_value
                    continue
                if key is None:
                    continue
                new_dict[key] = value
            new_items.append(new_dict)

        return new_items

    def process_dict(self, response_key):

        if response_key is None:
            return {}

        new_dict = {}
        for key in response_key.keys():
            value = response_key.get(key, None)
            key = self.parameter_mapping.get(key, None)
            # key = camel_to_snake_case(key)

            if value is None:
                # default_value = get_default_value(value_type)
                # value = default_value
                continue
            if key is None:
                continue
            new_dict[key] = value

        return new_dict

    def extract(self, old_dict):
        new_dict = {}
        for key in old_dict.keys():
            # if key in self.parameter_mapping.keys():
            new_key = self.parameter_mapping.get(key, None)
            if new_key is None:
                continue
            # new_key = camel_to_snake_case(key)
            value = old_dict[key]
            value_type = type(value)
            if value_type == list:
                new_dict[new_key] = self.process_list(value)
            elif value_type == dict:
                new_dict[new_key] = self.process_dict(value)
            else:
                new_dict[new_key] = old_dict[key]

        return new_dict
