from dataclasses import dataclass
from typing import Optional


@dataclass
class ClusterFactSpec:
    query: Optional[str] = None


@dataclass
class ClusterSpec:
    configuration_file: Optional[str] = None
    setup_user_password: Optional[str] = None
    host_name: Optional[str] = None
    fault_domain_name: Optional[str] = None
    is_master_node: Optional[bool] = False
    control_network_ip: Optional[str] = None
    control_network_subnet: Optional[str] = "255.255.255.0"
    control_network_mtu_size_in_byte: Optional[int] = 9000
    internode_network_ip: Optional[str] = None
    internode_network_subnet: Optional[str] = "255.255.255.0"

    config_file_location: Optional[str] = None
    node_id: Optional[str] = None
    node_name: Optional[str] = None
