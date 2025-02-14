from typing import Any, Dict, List


try:
    from ..common.vsp_constants import Endpoints
    from ..common.uaig_constants import Endpoints as UAIGEndpoints

    from .gateway_manager import VSPConnectionManager, UAIGConnectionManager
    from ..common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from ..model.vsp_storage_pool_models import (
        UAIGStoragePool,
        VSPPfrestStoragePoolList,
        VSPPfrestStoragePool,
        UAIGStoragePools,
        VSPPfrestLdevList,
        VSPPfrestLdev,
    )
    from ..model.vsp_storage_pool_models import StoragePoolSpec
    from ..common.uaig_constants import StoragePoolPayloadConst
    from ..common.hv_constants import CommonConstants, HEADER_NAME_CONSTANT, PoolType

except ImportError:
    from common.vsp_constants import Endpoints
    from common.uaig_constants import Endpoints as UAIGEndpoints
    from .gateway_manager import VSPConnectionManager, UAIGConnectionManager
    from common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from model.vsp_storage_pool_models import (
        UAIGStoragePool,
        VSPPfrestStoragePoolList,
        VSPPfrestStoragePool,
        UAIGStoragePools,
        VSPPfrestLdevList,
        VSPPfrestLdev,
    )
    from model.vsp_storage_pool_models import StoragePoolSpec
    from common.uaig_constants import StoragePoolPayloadConst
    from common.hv_constants import CommonConstants, HEADER_NAME_CONSTANT, PoolType


class VSPStoragePoolDirectGateway:

    def __init__(self, connection_info):
        self.connectionManager = VSPConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )

    @log_entry_exit
    def get_all_storage_pools(self):
        endPoint = Endpoints.GET_POOLS
        storagePoolsDict = self.connectionManager.get(endPoint)
        return VSPPfrestStoragePoolList(
            dicts_to_dataclass_list(storagePoolsDict["data"], VSPPfrestStoragePool)
        )

    @log_entry_exit
    def get_storage_pool_by_id(self, pool_id):
        endPoint = Endpoints.GET_POOL.format(pool_id)
        poolDict = self.connectionManager.get(endPoint)
        return VSPPfrestStoragePool(**poolDict)

    @log_entry_exit
    def get_ldevs(self, ldevs_query):
        endPoint = Endpoints.GET_LDEVS.format(ldevs_query)
        rest_dpvolumes = self.connectionManager.get(endPoint)
        return VSPPfrestLdevList(
            dicts_to_dataclass_list(rest_dpvolumes["data"], VSPPfrestLdev)
        )

    @log_entry_exit
    def create_storage_pool(self, spec):
        endPoint = Endpoints.POST_POOL
        payload = {}
        payload[StoragePoolPayloadConst.POOL_ID] = spec.pool_id
        payload[StoragePoolPayloadConst.POOL_NAME] = spec.name
        payload[StoragePoolPayloadConst.POOL_TYPE] = (
            PoolType.HDT if spec.type.upper() == PoolType.HRT else spec.type.upper()
        )

        if isinstance(spec.warning_threshold_rate, int):
            payload[StoragePoolPayloadConst.WARNING_THRESHOLD] = (
                spec.warning_threshold_rate
            )
        if isinstance(spec.depletion_threshold_rate, int):
            payload[StoragePoolPayloadConst.DEPLETION_THRESHOLD] = (
                spec.depletion_threshold_rate
            )
        if spec.ldev_ids:
            payload[StoragePoolPayloadConst.LDEV_IDS] = spec.ldev_ids
        if spec.should_enable_deduplication:
            payload[StoragePoolPayloadConst.IS_ENABLE_DEDUPLICATION] = (
                spec.duplication_ldev_ids
            )

        url = self.connectionManager.post(endPoint, payload)
        pool_id = url.split("/")[-1]
        if spec.type.upper() == PoolType.HRT:
            spec.type = PoolType.RT
            try:
                self.change_storage_pool_settings(pool_id, spec)
            except Exception as e:
                self.delete_storage_pool(pool_id)
                raise e
        return pool_id

    @log_entry_exit
    def delete_storage_pool(self, pool_id):
        endPoint = Endpoints.GET_POOL.format(pool_id)
        return self.connectionManager.delete(endPoint)

    @log_entry_exit
    def update_storage_pool(self, pool_id, spec):
        endPoint = Endpoints.POOL_EXPAND.format(pool_id)
        payload = {
            StoragePoolPayloadConst.PARAMETERS: {
                StoragePoolPayloadConst.LDEV_IDS: spec.ldev_ids
            }
        }

        return self.connectionManager.post(endPoint, payload)

    @log_entry_exit
    def change_storage_pool_settings(self, pool_id, spec):
        endPoint = Endpoints.GET_POOL.format(pool_id)
        payload = {}
        # will add more parameters as needed

        if spec.type:
            payload[StoragePoolPayloadConst.POOL_TYPE] = spec.type

        unused = self.connectionManager.patch(endPoint, payload)
        return pool_id


class VSPStoragePoolUAIGateway:

    def __init__(self, connection_info):
        self.connectionManager = UAIGConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )

        #  Set the resource id
        self.serial_number = None
        self.resource_id = None

        #  Set the headers
        self.headers = {HEADER_NAME_CONSTANT.PARTNER_ID: CommonConstants.PARTNER_ID}
        if connection_info.subscriber_id is not None:
            self.headers[HEADER_NAME_CONSTANT.SUBSCRIBER_ID] = (
                connection_info.subscriber_id
            )
        self.UCP_SYSTEM = CommonConstants.UCP_SERIAL

    @log_entry_exit
    def get_all_porcelain_storage_pools(self):
        #  Get the storage pools
        endPoint = UAIGEndpoints.GET_POOLS.format(self.resource_id)
        storagePoolsDict = self.connectionManager.get(endPoint)
        return UAIGStoragePools(
            dicts_to_dataclass_list(storagePoolsDict["data"], UAIGStoragePool)
        )

    @log_entry_exit
    def get_all_storage_pools(self):
        #  Get the storage pools for multi-tenant
        endPoint = UAIGEndpoints.MT_STORAGE_POOL.format(self.resource_id)
        storagePoolsDict = self.connectionManager.get(
            endPoint, headers_input=self.headers
        )
        return UAIGStoragePools(
            dicts_to_dataclass_list(storagePoolsDict["data"], UAIGStoragePool)
        )

    @log_entry_exit
    def get_storage_pool_by_id(self, pool_id):
        #  Get the storage pool
        endPoint = UAIGEndpoints.SINGLE_POOL.format(self.resource_id, pool_id)
        poolDict = self.connectionManager.get(endPoint)
        return UAIGStoragePool(**poolDict["data"])

    @log_entry_exit
    def delete_storage_pool(self, pool_id):
        #  Delete the storage pool
        endPoint = (
            UAIGEndpoints.SINGLE_POOL_V3.format(self.resource_id, pool_id)
            + "?isDelete=true"
        )
        return self.connectionManager.delete(endPoint, headers_input=self.headers)

    @log_entry_exit
    def update_storage_pool(self, pool_id, spec: StoragePoolSpec):
        #  Update the storage pool
        payload = {}
        payload[StoragePoolPayloadConst.POOL_VOLUMES] = []
        for volume in spec.pool_volumes:
            payload[StoragePoolPayloadConst.POOL_VOLUMES].append(
                {
                    StoragePoolPayloadConst.PARITY_GROUP_ID: volume.parity_group_id,
                    StoragePoolPayloadConst.CAPACITY: volume.capacity,
                }
            )
        endPoint = UAIGEndpoints.SINGLE_POOL.format(self.resource_id, pool_id)
        return self.connectionManager.patch(endPoint, payload)

    @log_entry_exit
    def create_storage_pool(self, spec: StoragePoolSpec):
        #  Create the storage pool for multi-tenant
        payload = {}
        payload[StoragePoolPayloadConst.UCP_SYSTEM] = self.UCP_SYSTEM
        payload[StoragePoolPayloadConst.NAME] = spec.name
        payload[StoragePoolPayloadConst.TYPE] = spec.type
        payload[StoragePoolPayloadConst.POOL_VOLUMES] = []
        for volume in spec.pool_volumes:
            payload[StoragePoolPayloadConst.POOL_VOLUMES].append(
                {
                    StoragePoolPayloadConst.PARITY_GROUP_ID: volume.parity_group_id,
                    StoragePoolPayloadConst.CAPACITY: volume.capacity,
                }
            )

        if isinstance(spec.resource_group_id, int):
            payload[StoragePoolPayloadConst.RESOURCE_GROUP_ID] = spec.resource_group_id
        if isinstance(spec.warning_threshold_rate, int):
            payload[StoragePoolPayloadConst.WARNING_THRESHOLD_RATE] = (
                spec.warning_threshold_rate
            )
        if isinstance(spec.depletion_threshold_rate, int):
            payload[StoragePoolPayloadConst.DEPLETION_THRESHOLD_RATE] = (
                spec.depletion_threshold_rate
            )
        if spec.type != PoolType.HTI:
            if spec.should_enable_deduplication:
                payload[StoragePoolPayloadConst.IS_ENABLE_DEDUPLICATION] = (
                    spec.should_enable_deduplication
                )
        endPoint = UAIGEndpoints.MT_STORAGE_POOL.format(self.resource_id)

        return self.connectionManager.post_subtask_ext(
            endPoint, payload, headers_input=self.headers
        )

    @log_entry_exit
    def get_ucpsystems(self) -> List[Dict[str, Any]]:
        end_point = UAIGEndpoints.GET_UCPSYSTEMS
        ucpsystems = self.connectionManager.get(end_point)
        return ucpsystems["data"]

    @log_entry_exit
    def get_all_parity_groups(self) -> List[Dict[str, Any]]:
        end_point = UAIGEndpoints.GET_PARITY_GROUPS.format(self.resource_id)
        ucpsystems = self.connectionManager.get(end_point)
        return ucpsystems["data"]

    def check_storage_in_ucpsystem(self, serial) -> bool:

        ucpsystems = self.get_ucpsystems()

        for u in ucpsystems:
            # if u.get("name") == CommonConstants.UCP_NAME:
            for s in u.get("storageDevices"):
                if s.get("serialNumber") == str(serial):
                    if s.get("healthStatus") != CommonConstants.ONBOARDING:
                        return True

        return False
