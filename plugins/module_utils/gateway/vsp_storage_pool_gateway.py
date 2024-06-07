import json

try:
    from ..common.vsp_constants import Endpoints
    from .gateway_manager import VSPConnectionManager
    from ..common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from ..model.vsp_storage_pool_models import *
except ImportError:
    from common.vsp_constants import Endpoints
    from .gateway_manager import VSPConnectionManager
    from common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from model.vsp_storage_pool_models import *


class VSPStoragePoolDirectGateway:

    def __init__(self, connection_info):
        self.connectionManager = VSPConnectionManager(
            connection_info.address, connection_info.username, connection_info.password
        )

    @log_entry_exit
    def get_all_storage_pools(self):
        endPoint = Endpoints.GET_POOLS
        print(endPoint)
        storagePoolsDict = self.connectionManager.get(endPoint)
        return VSPPfrestStoragePoolList(
            dicts_to_dataclass_list(storagePoolsDict["data"], VSPPfrestStoragePool)
        )

    @log_entry_exit
    def get_storage_pool(self, pool_id):
        endPoint = Endpoints.GET_POOL.format(pool_id)
        print(endPoint)
        poolDict = self.connectionManager.get(endPoint)
        return VSPPfrestStoragePool(**poolDict)

    @log_entry_exit
    def get_ldevs(self, ldevs_query):
        endPoint = Endpoints.GET_LDEVS.format(ldevs_query)
        print(endPoint)
        rest_dpvolumes = self.connectionManager.get(endPoint)
        return VSPPfrestLdevList(
            dicts_to_dataclass_list(rest_dpvolumes["data"], VSPPfrestLdev)
        )
