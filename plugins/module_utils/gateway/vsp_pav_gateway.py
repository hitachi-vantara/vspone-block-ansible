try:
    from ..common.vsp_constants import Endpoints
    from .gateway_manager import VSPConnectionManager
    from ..common.ansible_common import log_entry_exit
    from ..model.vsp_pav_models import VSPPavLdevResponseList
except ImportError:
    from common.vsp_constants import Endpoints
    from .gateway_manager import VSPConnectionManager
    from common.ansible_common import log_entry_exit
    from model.vsp_pav_models import VSPPavLdevResponseList


class VSPPavLdevGateway:

    def __init__(self, connection_info):
        self.connectionManager = VSPConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )

    @log_entry_exit
    def get_all_pav_ldevs(self):
        endPoint = Endpoints.GET_PAV_LDEVS
        pav_ldevs_dict = self.connectionManager.get(endPoint)
        return VSPPavLdevResponseList().dump_to_object(pav_ldevs_dict)

    @log_entry_exit
    def get_pav_ldev_by_cu(self, cu_number: int):
        endPoint = Endpoints.GET_PAV_LDEV_BY_CU.format(cu_number)
        try:
            pav_ldev_dict = self.connectionManager.get(endPoint)
            return VSPPavLdevResponseList().dump_to_object(pav_ldev_dict)
        except Exception as e:
            return None

    @log_entry_exit
    def unassign_pav_ldev(self, alias_ldev_ids: list[int]):
        endPoint = Endpoints.PAV_UNASSIGN_LDEV
        payload = {"parameters": {"aliasLdevIds": alias_ldev_ids}}
        return self.connectionManager.post(endPoint, payload)

    @log_entry_exit
    def assign_pav_ldev(self, alias_ldev_ids: list[int], base_ldev_id: int):
        endPoint = Endpoints.PAV_ASSIGN_LDEV
        payload = {
            "parameters": {
                "aliasLdevIds": alias_ldev_ids,
                "baseLdevId": base_ldev_id,
            }
        }
        return self.connectionManager.post(endPoint, payload)
