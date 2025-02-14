try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes
    from ..common.ansible_common import log_entry_exit
    from ..model.vsp_storage_port_models import (
        PortInfo,
        PortsInfo,
    )

except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes
    from common.ansible_common import log_entry_exit
    from model.vsp_storage_port_models import PortInfo, PortsInfo


class VSPStoragePortProvisioner:

    def __init__(self, connection_info):
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.STORAGE_PORT
        )
        self.config_gw = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_CONFIG_MAP
        )
        self.connection_info = connection_info
        self.portIdToPortInfoMap = None
        self.all_ports = None

    @log_entry_exit
    def get_single_storage_port(self, port_id: str) -> PortInfo:
        return self.gateway.get_single_storage_port(port_id)

    @log_entry_exit
    def filter_port_using_port_ids(self, port_ids: list) -> PortsInfo:
        # ports = self.get_all_storage_ports()
        # ports.data = [port for port in ports.data if port.portId in port_ids]
        # return ports

        result_ports = []
        for port_id in port_ids:
            port = self.get_single_storage_port(port_id)
            result_ports.append(port)

        return PortsInfo(data=result_ports)

    @log_entry_exit
    def get_all_storage_ports(self) -> PortsInfo:
        if self.portIdToPortInfoMap is None:
            self.portIdToPortInfoMap = {}
            ports = self.gateway.get_all_storage_ports()
            for port in ports.data:
                self.portIdToPortInfoMap[port.portId] = port
            return ports
        else:
            return PortsInfo(data=list(self.portIdToPortInfoMap.values()))

    @log_entry_exit
    def get_port_type(self, port_id):
        if self.portIdToPortInfoMap is None:
            self.portIdToPortInfoMap = {}
            self.all_ports = self.gateway.get_all_storage_ports()
            for port in self.all_ports.data:
                self.portIdToPortInfoMap[port.portId] = port
        port = self.portIdToPortInfoMap[port_id]
        return port.portType

    @log_entry_exit
    def change_port_settings(
        self, port_id: str, port_mode: str, enable_port_security: bool
    ) -> PortInfo:
        port_details = self.get_single_storage_port(port_id)
        if (
            (port_mode is None and enable_port_security is None)
            or (
                (
                    port_mode is not None
                    and port_details.portMode.lower() == port_mode.lower()
                )
                and (
                    enable_port_security is not None
                    and port_details.portSecuritySetting == enable_port_security
                )
            )
            or (
                port_mode is None
                and port_details.portSecuritySetting == enable_port_security
            )
            or (
                enable_port_security is None
                and port_details.portMode.lower() == port_mode.lower()
            )
        ):
            return port_details
        self.gateway.change_port_settings(port_mode, port_id, enable_port_security)
        self.connection_info.changed = True
        return self.get_single_storage_port(port_id)

    @log_entry_exit
    def is_out_of_band(self):
        return self.config_gw.is_out_of_band()
