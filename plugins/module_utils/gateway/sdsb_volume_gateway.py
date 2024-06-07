try:
    from ..common.sdsb_constants import SDSBlockEndpoints
    from ..common.ansible_common import dicts_to_dataclass_list
    from .gateway_manager import SDSBConnectionManager
    from ..model.sdsb_volume_models import *
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
except ImportError:
    from common.sdsb_constants import SDSBlockEndpoints
    from common.ansible_common import dicts_to_dataclass_list
    from .gateway_manager import SDSBConnectionManager
    from model.sdsb_volume_models import *
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit

logger = Log()
moduleName = "SDS Block Compute Node"


class SDSBVolumeDirectGateway:

    def __init__(self, connection_info):

        self.connection_manager = SDSBConnectionManager(
            connection_info.address, connection_info.username, connection_info.password
        )

    @log_entry_exit
    def create_bulk_volume(
        self,
        pool_id,
        name,
        capacity,
        volume_count,
        start_number,
        num_of_digits,
        savings,
    ):

        end_point = SDSBlockEndpoints.POST_VOLUMES
        payload = {
            "poolId": pool_id,
            "name": name,
            "capacity": capacity,
            "nameParam": {
                "baseName": name,
                "startNumber": start_number,
                "numberOfDigits": num_of_digits,
            },
            "number": volume_count,
            "savingSetting": savings,
        }
        return self.connection_manager.post(end_point, payload)

    @log_entry_exit
    def create_volume(self, pool_id, name, capacity, savings):

        end_point = SDSBlockEndpoints.POST_VOLUMES
        payload = {
            "poolId": pool_id,
            "name": name,
            "capacity": capacity,
            "nameParam": {
                "baseName": name,
            },
            "savingSetting": savings,
        }
        return self.connection_manager.post(end_point, payload)

    @log_entry_exit
    def get_volumes(self):
        end_point = SDSBlockEndpoints.GET_VOLUMES
        logger.writeDebug("GW:get_volumes:end_point={}", end_point)
        volume_data = self.connection_manager.get(end_point)
        logger.writeDebug("GW:get_volumes:data={}", volume_data)
        return SDSBVolumesInfo(
            dicts_to_dataclass_list(volume_data["data"], SDSBVolumeInfo)
        )

    @log_entry_exit
    def get_volume_by_id(self, volume_id):
        end_point = SDSBlockEndpoints.GET_VOLUMES_BY_ID.format(volume_id)
        data = self.connection_manager.get(end_point)
        return SDSBVolumeInfo(**data)

    @log_entry_exit
    def get_volume_by_name(self, volume_name):
        key = "name"
        val = volume_name
        end_point = SDSBlockEndpoints.GET_VOLUMES_AND_QUERY.format(key, val)    
        data = self.connection_manager.get(end_point)
        logger.writeDebug(
            "GW:get_volume_by_name:data={} len={}", data, len(data.get("data"))
        )
        if data is not None and len(data.get("data")) > 0:
            return SDSBVolumeInfo(**data.get("data")[0])
        else:
            return None


    @log_entry_exit
    def delete_volume(self, volume_id):
        end_point = SDSBlockEndpoints.DELETE_VOLUMES.format(volume_id)
        volume_data = self.connection_manager.delete(end_point)
        return volume_data

    @log_entry_exit
    def update_volume(self, volume_id, name, nickname):
        end_point = SDSBlockEndpoints.PATCH_VOLUMES.format(volume_id)
        payload = {}

        if name: 
            payload["name"] = name

        if nickname:
            payload["nickname"] = nickname

        self.connection_manager.patch(end_point, payload)

    @log_entry_exit
    def expand_volume_capacity(self, volume_id, capacity):
        end_point = SDSBlockEndpoints.POST_VOLUMES_EXPAND.format(volume_id)
        payload = {
            "additionalCapacity": capacity,
        }
        self.connection_manager.post(end_point, payload)

class SDSBVolumeUAIGateway:
    pass
