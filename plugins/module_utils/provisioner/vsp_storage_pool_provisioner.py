try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes
    from ..common.ansible_common import log_entry_exit, convert_block_capacity
    from ..model.vsp_storage_pool_models import VSPStoragePool, VSPStoragePools
    from ..common.hv_constants import StateValue, ConnectionTypes
    from .vsp_parity_group_provisioner import VSPParityGroupProvisioner
    from ..common.uaig_utils import UAIGResourceID
    from ..message.vsp_storage_pool_msgs import VSPStoragePoolValidateMsg


except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes
    from common.ansible_common import log_entry_exit, convert_block_capacity
    from model.vsp_storage_pool_models import VSPStoragePool, VSPStoragePools
    from common.hv_constants import StateValue, ConnectionTypes
    from .vsp_parity_group_provisioner import VSPParityGroupProvisioner
    from common.uaig_utils import UAIGResourceID
    from message.vsp_storage_pool_msgs import VSPStoragePoolValidateMsg



from enum import Enum
import math


class POOL_STATUS(Enum):
    POOLSTAT_UNKNOWN = 0
    POOLSTAT_NORMAL = 1
    POOLSTAT_OVERTHRESHOLD = 2
    POOLSTAT_SUSPENDED = 3
    POOLSTAT_FAILURE = 4
    POOLSTAT_SHRINKING = 5
    POOLSTAT_REGRESSED = 6
    POOLSTAT_DETACHED = 7


def get_dppool_subscription_rate(volume_used_capacity, total_capacity):
    if total_capacity == 0:
        return -1
    return math.ceil((volume_used_capacity / total_capacity) * 100.0)


class VSPStoragePoolProvisioner:

    def __init__(self, connection_info):
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_STORAGE_POOL
        )
        self.connection_info = connection_info
        self.connection_type = connection_info.connection_type
        self.resource_id = None
        self.serial = None
        self.pg_info = None
        self.pg_prov = VSPParityGroupProvisioner(connection_info)

    def format_storage_pool(self, pool):

        storage_pool_dict = {}
        storage_pool_dict["poolId"] = pool.poolId
        storage_pool_dict["name"] = pool.poolName
        storage_pool_dict["type"] = pool.poolType
        if pool.isShrinking:
            storage_pool_dict["status"] = "SHRINKING"
        else:
            if pool.poolStatus == "POLN":
                storage_pool_dict["status"] = "NORMAL"
            elif pool.poolStatus == "POLF":
                storage_pool_dict["status"] = "OVER_THRESHOLD"
            elif pool.poolStatus == "POLS":
                storage_pool_dict["status"] = "SUSPENDED"
            elif pool.poolStatus == "POLE":
                storage_pool_dict["status"] = "FAILURE"
            else:
                storage_pool_dict["status"] = "UNKNOWN"

        storage_pool_dict["utilizationRate"] = pool.usedCapacityRate
        storage_pool_dict["freeCapacity"] = pool.availableVolumeCapacity * 1024 * 1024
        storage_pool_dict["freeCapacityInUnits"] = convert_block_capacity(
            storage_pool_dict.get("freeCapacity", -1), 1
        )
        storage_pool_dict["totalCapacity"] = pool.totalPoolCapacity * 1024 * 1024
        storage_pool_dict["totalCapacityInUnit"] = convert_block_capacity(
            storage_pool_dict.get("totalCapacity", -1), 1
        )
        storage_pool_dict["warningThresholdRate"] = pool.warningThreshold
        storage_pool_dict["depletionThresholdRate"] = pool.depletionThreshold
        storage_pool_dict["subscriptionLimitRate"] = pool.virtualVolumeCapacityRate
        if pool.poolType == "HTI":
            storage_pool_dict["virtualVolumeCount"] = pool.snapshotCount
        else:
            storage_pool_dict["virtualVolumeCount"] = pool.locatedVolumeCount
        storage_pool_dict["subscriptionRate"] = -1
        if pool.poolType != "HTI":
            storage_pool_dict["subscriptionRate"] = get_dppool_subscription_rate(
                pool.totalLocatedCapacity, pool.totalPoolCapacity
            )

        storage_pool_dict["ldevIds"] = []
        count_query = "count={}".format(16384)
        pool_query = "poolId={}".format(pool.poolId)
        pool_vol_query = "?" + count_query + "&" + pool_query
        ldevs = self.gateway.get_ldevs(pool_vol_query)
        for ldev in ldevs.data:
            storage_pool_dict["ldevIds"].append(ldev.ldevId)

        storage_pool_dict["dpVolumes"] = []
        count_query = "count={}".format(16384)
        ldev_option_query = "ldevOption=dpVolume"
        pool_query = "poolId={}".format(pool.poolId)
        dpvolume_query = "?" + count_query + "&" + ldev_option_query + "&" + pool_query
        dpvolumes = self.gateway.get_ldevs(dpvolume_query)
        for dpvol in dpvolumes.data:
            tmp_dpvol = {}
            tmp_dpvol["logicalUnitId"] = dpvol.ldevId
            tmp_dpvol["size"] = convert_block_capacity(dpvol.blockCapacity)
            storage_pool_dict["dpVolumes"].append(tmp_dpvol)
        return storage_pool_dict

    @log_entry_exit
    def get_all_storage_pools(self):
        pools = None
        storage_pools = self.gateway.get_all_storage_pools()
        if self.connection_type == ConnectionTypes.DIRECT:
            tmp_storage_pools = []
            # Get a list of storage pools

            for pool in storage_pools.data:
                tmp_storage_pools.append(
                    VSPStoragePool(**self.format_storage_pool(pool))
                )

            pools = VSPStoragePools(data=tmp_storage_pools)
        else:
            common_object = [
                VSPStoragePool(**pool.to_dict()) for pool in storage_pools.data
            ]
            pools = VSPStoragePools(data=common_object)
        for pool in pools.data:
            self.add_encryption_info(pool)

        return pools

    @log_entry_exit
    def add_encryption_info(self, pool):
        if not pool.ldevIds or len(pool.ldevIds) < 0:
            return
        first_ldev = pool.ldevIds[0]
        if self.pg_info is None:
            self.pg_info = self.pg_prov.get_all_parity_groups()
        for pg in self.pg_info.data:
            if first_ldev in pg.ldevIds:
                pool.isEncrypted = pg.isEncryptionEnabled
                break
        pool.isEncrypted = False

    @log_entry_exit
    def get_storage_pool(self, pool_fact_spec=None):
        if pool_fact_spec and pool_fact_spec.pool_id is not None:
            return self.get_storage_pool_by_id(pool_fact_spec.pool_id)
        else:
            return self.get_all_storage_pools()

    @log_entry_exit
    def create_storage_pool(self, pool_spec):

        if pool_spec.name is None or pool_spec.name == "":
            raise ValueError(VSPStoragePoolValidateMsg.POOL_NAME_REQUIRED.value)
        if pool_spec.type is None or pool_spec.type == "":
            raise ValueError(VSPStoragePoolValidateMsg.POOL_TYPE_REQUIRED.value)
        if pool_spec.pool_volumes is None:
            raise ValueError(VSPStoragePoolValidateMsg.POOL_VOLUME_REQUIRED.value)
        pool_spec.type = pool_spec.type.upper()
        pool_id = self.gateway.create_storage_mt_pool(pool_spec)
        self.connection_info.changed = True
        return self.get_storage_pool_by_resource_id(pool_id)

    @log_entry_exit
    def get_storage_pool_by_name_or_id(self, pool_name=None, id=None):
        storage_pools = self.get_all_storage_pools()
        for pool in storage_pools.data:
            if (pool_name and pool.name == pool_name) or (
                id is not None and pool.poolId == id
            ):
                return pool
        return None

    @log_entry_exit
    def get_storage_pool_by_id(self, pool_id):
        if self.connection_type == ConnectionTypes.DIRECT:
            pool = VSPStoragePool(
                **self.format_storage_pool(self.gateway.get_storage_pool_by_id(pool_id))
            )
            self.add_encryption_info(pool)
            return pool
        else:
            return self.get_storage_pool_by_name_or_id(id=pool_id)

    @log_entry_exit
    def get_storage_pool_by_resource_id(self, resource_id):
        storage_pools = self.get_all_storage_pools()
        for pool in storage_pools.data:
            if (pool.resourceId and pool.resourceId == resource_id) or (
                pool.poolId and pool.poolId == resource_id
            ):
                return pool
        return None

    @log_entry_exit
    def update_storage_pool(self, spec, pool):
        resource_id = (
            pool.poolId
            if self.connection_type == ConnectionTypes.DIRECT
            else pool.resourceId
        )
        if spec.pool_volumes is not None and len(spec.pool_volumes) > 0:
            _ = self.gateway.update_storage_pool(resource_id, spec)
        else:
            return pool
        pool = self.get_storage_pool_by_resource_id(resource_id)
        self.connection_info.changed = True
        return pool

    @log_entry_exit
    def delete_storage_pool(self, spec):
        pool = self.get_storage_pool_by_name_or_id(spec.name, spec.id)
        if pool is None:
            raise ValueError(VSPStoragePoolValidateMsg.POOL_DOES_NOT_EXIST.value)
        resource_id = (
            pool.poolId
            if self.connection_type == ConnectionTypes.DIRECT
            else pool.resourceId
        )
        self.connection_info.subscriber_id = pool.subscriberId
        _ = self.gateway.delete_storage_pool(resource_id)
        self.connection_info.changed = True
        return "Storage pool deleted successfully."

    @log_entry_exit
    def check_ucp_system(self, serial):
        if self.connection_info.connection_type == ConnectionTypes.DIRECT:
            return serial
        if not self.gateway.check_storage_in_ucpsystem(serial):
            raise ValueError(
                "UCP system is not available. Please try again or provide the correct serial number."
            )
        else:
            self.serial = serial
            self.resource_id = UAIGResourceID().storage_resourceId(self.serial)
            self.gateway.resource_id = self.resource_id
            self.pg_prov.resource_id = self.resource_id
            self.pg_prov.gateway.resource_id = self.resource_id
            return serial
