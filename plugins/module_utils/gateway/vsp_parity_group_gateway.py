import json

try:
    from ..common.vsp_constants import Endpoints
    from .gateway_manager import VSPConnectionManager
    from ..common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from ..model.vsp_parity_group_models import *
except ImportError:
    from common.vsp_constants import Endpoints
    from .gateway_manager import VSPConnectionManager
    from common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from model.vsp_parity_group_models import *


class VSPParityGroupDirectGateway:

    def __init__(self, connection_info):
        self.connectionManager = VSPConnectionManager(
            connection_info.address, connection_info.username, connection_info.password
        )

    @log_entry_exit
    def get_all_parity_groups(self):
        endPoint = Endpoints.GET_PARITY_GROUPS
        print(endPoint)
        parity_groups_dict = self.connectionManager.get(endPoint)
        return VSPPfrestParityGroupList(
            dicts_to_dataclass_list(parity_groups_dict["data"], VSPPfrestParityGroup)
        )

    @log_entry_exit
    def get_parity_group(self, parity_group_id):
        endPoint = Endpoints.GET_PARITY_GROUP.format(parity_group_id)
        print(endPoint)
        parity_group_dict = self.connectionManager.get(endPoint)
        return VSPPfrestParityGroup(**parity_group_dict)

    @log_entry_exit
    def get_all_external_parity_groups(self):
        endPoint = Endpoints.GET_EXTERNAL_PARITY_GROUPS
        print(endPoint)
        parity_groups_dict = self.connectionManager.get(endPoint)
        return VSPPfrestExternalParityGroupList(
            dicts_to_dataclass_list(
                parity_groups_dict["data"], VSPPfrestExternalParityGroup
            )
        )

    @log_entry_exit
    def get_external_parity_group(self, external_parity_group_id):
        endPoint = Endpoints.GET_EXTERNAL_PARITY_GROUP.format(external_parity_group_id)
        print(endPoint)
        parity_group_dict = self.connectionManager.get(endPoint)
        epg = VSPPfrestExternalParityGroup(**parity_group_dict)
        epg.spaces = dicts_to_dataclass_list(
            parity_group_dict.get("spaces", None), VSPPfrestParityGroupSpace
        )
        # return VSPPfrestExternalParityGroup(**parity_group_dict)
        return epg

    @log_entry_exit
    def get_ldevs(self, ldevs_query):
        endPoint = Endpoints.GET_LDEVS.format(ldevs_query)
        print(endPoint)
        rest_ldevs = self.connectionManager.get(endPoint)
        return VSPPfrestLdevList(
            dicts_to_dataclass_list(rest_ldevs["data"], VSPPfrestLdev)
        )
