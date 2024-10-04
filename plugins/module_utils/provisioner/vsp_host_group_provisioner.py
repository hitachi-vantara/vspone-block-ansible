try:

    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import *
    from ..common.hv_log import Log
    from ..common.ansible_common import convert_hex_to_dec
    from ..model.vsp_host_group_models import *
    from ..common.ansible_common import dicts_to_dataclass_list
    from ..common.uaig_utils import UAIGResourceID

except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import *
    from common.hv_log import Log
    from common.ansible_common import convert_hex_to_dec
    from model.vsp_host_group_models import *
    from common.ansible_common import dicts_to_dataclass_list
    from common.uaig_utils import UAIGResourceID




class VSPHostGroupProvisioner:

    def __init__(self, connection_info):
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_HOST_GROUP
        )
        self.connection_info = connection_info
        self.serial = None

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

    def get_ports(self):
        return self.gateway.get_ports()

    def get_one_host_group(self, port_input, name):
        return self.gateway.get_one_host_group(port_input, name)
    
    def get_all_host_groups(self, serial):
        
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            res_id = UAIGResourceID().storage_resourceId(serial)
            return self.gateway.get_host_groups_for_resource_id(res_id)
    
    def create_host_group(self, port, name, wwns, luns, host_mode, host_mode_options):
        self.gateway.create_host_group(
            port, name, wwns, luns, host_mode, host_mode_options
        )

    def delete_host_group(self, hg, is_delete_all_luns):
        hg = self.gateway.delete_host_group(hg, is_delete_all_luns)

    def add_wwns_to_host_group(self, hg, wwns):
        self.gateway.add_wwns_to_host_group(hg, wwns)

    def delete_wwns_from_host_group(self, hg, wwns):
        self.gateway.delete_wwns_from_host_group(hg, wwns)

    def add_luns_to_host_group(self, hg, luns):
        self.gateway.add_luns_to_host_group(hg, luns)

    def delete_luns_from_host_group(self, hg, luns):
        self.gateway.delete_luns_from_host_group(hg, luns)

    def set_host_mode(self, hg, host_mode, host_mode_options):
        self.gateway.set_host_mode(hg, host_mode, host_mode_options)
