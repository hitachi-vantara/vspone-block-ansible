try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes
    from ..common.ansible_common import log_entry_exit, convert_block_capacity
    from ..model.vsp_storage_pool_models import *

except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes
    from common.ansible_common import log_entry_exit, convert_block_capacity
    from model.vsp_storage_pool_models import *
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

    def format_storage_pool(self, pool):
        storage_pool_dict = {}
        storage_pool_dict["poolId"] = pool.poolId
        storage_pool_dict["poolName"] = pool.poolName
        storage_pool_dict["poolType"] = pool.poolType
        if pool.isShrinking == True:
            storage_pool_dict["status"] = "SHRINKING"
        else:
            match pool.poolStatus:
                case "POLN":
                    storage_pool_dict["status"] = "NORMAL"
                case "POLF":
                    storage_pool_dict["status"] = "OVER_THRESHOLD"
                case "POLS":
                    storage_pool_dict["status"] = "SUSPENDED"
                case "POLE":
                    storage_pool_dict["status"] = "FAILURE"
                case _:
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
        tmp_storage_pools = []
        # Get a list of storage pools
        storage_pools = self.gateway.get_all_storage_pools()
        for pool in storage_pools.data:
            tmp_storage_pools.append(VSPStoragePool(**self.format_storage_pool(pool)))

        return VSPStoragePools(tmp_storage_pools)

    @log_entry_exit
    def get_storage_pool(self, pool_fact_spec):
        if pool_fact_spec.pool_id is not None:
            storage_pool = self.gateway.get_storage_pool(pool_fact_spec.pool_id)
            return VSPStoragePool(**self.format_storage_pool(storage_pool))
        else:
            return None
