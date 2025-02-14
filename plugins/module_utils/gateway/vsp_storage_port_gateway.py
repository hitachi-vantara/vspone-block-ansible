try:
    from ..common.vsp_constants import Endpoints
    from .gateway_manager import VSPConnectionManager, UAIGConnectionManager
    from ..common.hv_log import Log
    from ..common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from ..model.vsp_storage_port_models import (
        PortInfo,
        VSPPortInfoUAIG,
        VSPPortsInfoUAIG,
        ShortPortInfo,
        ShortPortInfoList,
    )
    from ..common.vsp_constants import VSPPortSetting
    from ..common.hv_constants import CommonConstants
    from ..common.uaig_constants import Endpoints as UAIGEndpoints
    from ..common.uaig_utils import UAIGResourceID
except ImportError:
    from common.vsp_constants import Endpoints
    from .gateway_manager import VSPConnectionManager, UAIGConnectionManager
    from common.hv_log import Log
    from common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from model.vsp_storage_port_models import (
        PortInfo,
        VSPPortInfoUAIG,
        VSPPortsInfoUAIG,
        ShortPortInfo,
        ShortPortInfoList,
    )
    from common.vsp_constants import VSPPortSetting
    from common.hv_constants import CommonConstants
    from common.uaig_constants import Endpoints as UAIGEndpoints
    from common.uaig_utils import UAIGResourceID


logger = Log()


class VSPStoragePortDirectGateway:

    def __init__(self, connection_info):
        self.connectionManager = VSPConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )
        self.serial = None

    @log_entry_exit
    def set_serial(self, serial):
        self.serial = serial

    @log_entry_exit
    def get_all_storage_ports(self):
        endPoint = Endpoints.GET_PORTS_DETAILS
        portsInfo = self.connectionManager.get(endPoint)
        return ShortPortInfoList(
            dicts_to_dataclass_list(portsInfo["data"], ShortPortInfo)
        )

    @log_entry_exit
    def get_single_storage_port(self, port_id: str) -> PortInfo:
        endPoint = Endpoints.GET_ONE_PORT_WITH_MODE.format(port_id)
        portInfo = self.connectionManager.get(endPoint)
        return PortInfo(**portInfo)

    @log_entry_exit
    def change_port_settings(
        self, port_mode: str, port_id: str, enable_port_security: bool
    ) -> None:
        endPoint = Endpoints.UPDATE_PORT.format(port_id)
        data = {}
        if port_mode is not None:
            data[VSPPortSetting.PORT_MODE] = port_mode
        if enable_port_security is not None:
            data[VSPPortSetting.LUN_SECURITY_SETTING] = enable_port_security
        return self.connectionManager.patch(endPoint, data)


class VSPStoragePortUAIGateway:
    def __init__(self, connection_info):
        self.connection_manager = UAIGConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )
        self.connection_info = connection_info
        self.serial = None
        self.resource_id = None

    @log_entry_exit
    def set_serial(self, serial):
        self.serial = serial
        self.set_resource_id()

    @log_entry_exit
    def populate_header(self):
        headers = {}
        headers["partnerId"] = CommonConstants.PARTNER_ID
        if self.connection_info.subscriber_id is not None:
            headers["subscriberId"] = self.connection_info.subscriber_id
        return headers

    @log_entry_exit
    def set_resource_id(self):
        self.resource_id = UAIGResourceID().storage_resourceId(self.serial)
        logger.writeDebug(
            "GW:set_resource_id:serial = {}  resourceId = {}",
            self.serial,
            self.resource_id,
        )

    @log_entry_exit
    def get_all_storage_ports(self):
        self.set_resource_id()
        endPoint = UAIGEndpoints.UAIG_GET_PORTS.format(self.resource_id)
        headers = self.populate_header()

        portsInfo = self.connection_manager.get(endPoint, headers)
        # ports_info =  PortsInfo().dump_to_object(portsInfo)
        # return ports_info
        return VSPPortsInfoUAIG(
            dicts_to_dataclass_list(portsInfo["data"], VSPPortInfoUAIG)
        )

    @log_entry_exit
    def get_all_storage_ports_wo_subscriber(self):
        self.set_resource_id()
        endPoint = UAIGEndpoints.UAIG_GET_PORTS.format(self.resource_id)
        headers = {}
        headers["partnerId"] = CommonConstants.PARTNER_ID

        portsInfo = self.connection_manager.get(endPoint, headers)
        # ports_info =  PortsInfo().dump_to_object(portsInfo)
        # return ports_info
        return VSPPortsInfoUAIG(
            dicts_to_dataclass_list(portsInfo["data"], VSPPortInfoUAIG)
        )

    @log_entry_exit
    def tag_port(self, resource_id, port_id):
        headers = self.populate_header()
        pay_load = {
            "resourceId": port_id,
            "partnerId": CommonConstants.PARTNER_ID,
            "type": "Port",
        }
        if self.connection_info.subscriber_id is not None:
            pay_load["subscriberId"] = self.connection_info.subscriber_id

        endPoint = UAIGEndpoints.UAIG_TAG_PORT.format(resource_id)
        result = self.connection_manager.post(endPoint, pay_load, headers)
        return result

    @log_entry_exit
    def get_single_storage_port(self, port_id):
        headers = self.populate_header()
        pay_load = {
            "partnerId": CommonConstants.PARTNER_ID,
        }
        if self.connection_info.subscriber_id is not None:
            pay_load["subscriberId"] = self.connection_info.subscriber_id

        end_point = UAIGEndpoints.UAIG_GET_PORTS.format(self.resource_id)

        ports = self.connection_manager.getV3(end_point, pay_load, headers)
        # logger.writeDebug(
        #     "GW: 171 :ports = {}", ports
        # )
        for p in ports["data"]:
            if p["resourceId"] == port_id:
                return VSPPortInfoUAIG(**p)

        return None
