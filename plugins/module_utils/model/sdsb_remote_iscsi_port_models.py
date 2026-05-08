from dataclasses import dataclass
from typing import Optional


@dataclass
class SDSBRemoteIscsciPortFactSpec:
    id: Optional[str] = None
    local_port: Optional[str] = None
    local_port_id: Optional[str] = None
    remote_serial: Optional[str] = None
    remote_storage_system_type: Optional[str] = None
    remote_port: Optional[str] = None
    remote_port_id: Optional[str] = None

    def __post_init__(self):
        if self.local_port_id is not None:
            self.local_port = self.local_port_id
        if self.remote_port_id is not None:
            self.remote_port = self.remote_port_id


@dataclass
class SDSBRemoteIscsciPortSpec:
    id: Optional[str] = None
    local_port: Optional[str] = None
    local_port_id: Optional[str] = None
    remote_serial: Optional[str] = None
    remote_storage_system_type: Optional[str] = None
    remote_port: Optional[str] = None
    remote_port_id: Optional[str] = None
    remote_ip_address: Optional[str] = None
    remote_tcp_port: Optional[int] = None
    is_detailed_logging_mode: Optional[bool] = None
    remote_storage_port_ip_address: Optional[str] = None

    def is_empty(self):
        if self.id is None and self.is_detailed_logging_mode is None:
            return True
        else:
            return False

    def __post_init__(self):
        if self.remote_storage_port_ip_address is not None:
            self.remote_ip_address = self.remote_storage_port_ip_address
        if self.local_port_id is not None:
            self.local_port = self.local_port_id
        if self.remote_port_id is not None:
            self.remote_port = self.remote_port_id
