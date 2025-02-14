try:

    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes, ConnectionTypes
    from ..common.hv_log import Log
    from ..common.ansible_common import convert_hex_to_dec
    from ..common.uaig_utils import UAIGResourceID
    from ..common.ansible_common import log_entry_exit


except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes, ConnectionTypes
    from common.hv_log import Log
    from common.ansible_common import convert_hex_to_dec
    from common.uaig_utils import UAIGResourceID
    from common.ansible_common import log_entry_exit


class VSPHostGroupProvisioner:

    def __init__(self, connection_info):
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_HOST_GROUP
        )
        self.connection_info = connection_info
        self.serial = None
        self.all_hgs = None

    @log_entry_exit
    def get_host_groups(
        self, ports_input=None, name_input=None, lun_input=None, query=None
    ):
        logger = Log()
        logger.writeDebug("PROV:get_host_groups:serial = {}", self.serial)
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            self.gateway.set_serial(self.serial)
        if name_input == "":
            name_input = None

        if lun_input is not None and ":" in str(lun_input):
            lun_input = convert_hex_to_dec(lun_input)
            logger.writeDebug("Hex converted lun={0}".format(lun_input))
        if lun_input == "":
            lun_input = None

        port_set = None
        if ports_input:
            port_set = set(ports_input)
        logger.writeInfo("port_set={0}".format(port_set))
        is_get_wwns = False
        if query and "wwns" in query:
            is_get_wwns = True

        is_get_luns = False
        if query and "ldevs" in query or lun_input is not None:
            is_get_luns = True
        host_groups = self.gateway.get_host_groups(
            ports_input, name_input, is_get_wwns, is_get_luns
        )
        if lun_input is not None:
            new_data = []
            for hg in host_groups.data:
                logger.writeInfo("lun_input {}", lun_input)
                for lun in hg.lunPaths:
                    if lun_input == lun.ldevId:
                        new_data.append(hg)
            host_groups.data = new_data

        return host_groups

    @log_entry_exit
    def get_ports(self):
        return self.gateway.get_ports()

    @log_entry_exit
    def get_one_host_group(self, port_input, name):
        return self.gateway.get_one_host_group(port_input, name)

    @log_entry_exit
    def get_one_host_group_using_hg_port_id(self, port_id, hg_id):
        logger = Log()

        if not self.all_hgs:
            self.all_hgs = self.get_all_host_groups(self.serial)

        logger.writeDebug(f"self.all_hgs{self.all_hgs}")
        if self.all_hgs:
            for hg in self.all_hgs.data:
                # logger.writeDebug(f"hg.portId={hg.portId}, hg.hostGroupNumber={hg.hostGroupNumber}")
                # logger.writeDebug(f"port_id={port_id}, hg_id={hg_id}")
                if hg.portId == port_id and hg.hostGroupNumber == hg_id:
                    return hg
        return None

    @log_entry_exit
    def get_all_host_groups(self, serial):

        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            res_id = UAIGResourceID().storage_resourceId(serial)
            return self.gateway.get_host_groups_for_resource_id(res_id)
        else:
            return self.gateway.get_all_hgs()

    @log_entry_exit
    def create_host_group(self, port, name, wwns, luns, host_mode, host_mode_options):
        self.gateway.create_host_group(
            port, name, wwns, luns, host_mode, host_mode_options
        )

    @log_entry_exit
    def delete_host_group(self, hg, is_delete_all_luns):
        hg = self.gateway.delete_host_group(hg, is_delete_all_luns)

    @log_entry_exit
    def add_wwns_to_host_group(self, hg, wwns):
        self.gateway.add_wwns_to_host_group(hg, wwns)

    @log_entry_exit
    def delete_wwns_from_host_group(self, hg, wwns):
        self.gateway.delete_wwns_from_host_group(hg, wwns)

    @log_entry_exit
    def add_luns_to_host_group(self, hg, luns):
        self.gateway.add_luns_to_host_group(hg, luns)

    @log_entry_exit
    def delete_luns_from_host_group(self, hg, luns):
        self.gateway.delete_luns_from_host_group(hg, luns)

    @log_entry_exit
    def set_host_mode(self, hg, host_mode, host_mode_options):
        self.gateway.set_host_mode(hg, host_mode, host_mode_options)
