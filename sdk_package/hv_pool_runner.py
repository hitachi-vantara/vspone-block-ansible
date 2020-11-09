#!/usr/bin/python

import json
import re

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.hv_infra import StorageSystem, StorageSystemManager
from ansible.module_utils.hv_infra import Utils
from ansible.module_utils.hv_logger import Logger, MessageID
from ansible.module_utils.hv_log import Log
from ansible.module_utils.hv_storage_enum import PoolType

logger=Log()

def parseRate(rate, default):
    if not rate:
        rate = default

    if isinstance(rate, str):
        rate = float(rate.replace('%', ''))

    if 0 < rate < 1: # Assume percentage
        rate = int(rate * 100)
    else:
        rate = int(rate)

    return rate

def runPlaybook(module):
    storageSystem = StorageSystem(module.params["storage_serial"])
    data = json.loads(module.params["data"])
    storageSystem.logger.writeParam("data={}", json.dumps(data))

    poolId = data.get("id")
    poolName = data.get("name")
    pool = None
    if poolId is not None:
        pool = storageSystem.getDynamicPool(poolId)

        if pool is None:
            raise Exception("No pool found for the id {}. If you are creating a pool, do not supply a pool id.".format(poolId))
        elif poolName is not None and pool.get("Name") != poolName:
            raise Exception("Consistency error: pool ID does not match pool name. Please use either the id or the name and remove the other parameter.")
    elif poolName is not None:
        matchingPools = [dp for dp in storageSystem.getStoragePools() if dp.get("Name") == poolName]
        if matchingPools:
            pool = matchingPools[0]
    else:
        raise Exception("No pool id or name specified.")

    storageSystem.logger.writeParam("pool={}", json.dumps(pool))

    if module.params["state"] == "absent":
        if pool:
            storageSystem.deleteDynamicPool(pool["Id"])
    else:
        changed = False
        if not pool:
            storageSystem.logger.writeInfo("Creating Dynamic Pool")
            if not poolName:
                raise Exception("No name specified for creating new dynamic pool")
            if not data.get("luns"): # This also covers if the luns list is empty
                raise Exception("No luns specified for creating new dynamic pool")
            if not data.get("type"):
                raise Exception("No dynamic pool type specified for creating new dynamic pool")
            pool = storageSystem.createDynamicPool(data["name"], data["luns"], data["type"])
        else:
            storageSystem.logger.writeInfo("Modifying Dynamic Pool")

            if data.get("type"): # Create Pool Idempotency check
                poolType = PoolType.fromString(data["type"])
                if poolType.value != pool["Type"]:
                    raise Exception("Pool exists with a different pool type than the input.")

            oldluns = set(pool["ComponentIds"])
            newluns = set(data.get("luns") or [])
            if data.get("state") == "absent":
                removeluns = oldluns & newluns
                if oldluns - removeluns == []:
                    raise Exception("Cannot remove all luns from a dynamic pool.")
                elif removeluns:
                    storageSystem.shrinkDynamicPool(pool["Id"], removeluns)
                    changed = True
            else:
                addluns = newluns - oldluns
                if addluns:
                    storageSystem.expandDynamicPool(pool["Id"], addluns)
                    changed = True

        # TODO: After SIEVRO-311 is resolved, add back subscription warning
        #subscription_warning = parseRate(data.get("subscription_warning", pool["SubscriptionWarningRate"]))
        subscription_limit = parseRate(data.get("subscription_limit"), pool["SubscriptionLimitRate"])
        #if subscription_warning != pool["SubscriptionWarningRate"] or subscription_limit != pool["SubscriptionLimitRate"]:
            #storageSystem.setDynamicPoolSubscriptionLimit(poolId, subscription_warning, subscription_limit, data.get("subscription_notify", False))
        if subscription_limit != pool["SubscriptionLimitRate"]:
            storageSystem.setDynamicPoolSubscriptionLimit(pool["Id"], -1, subscription_limit, data.get("subscription_notify", False))
            changed = True

        capacity_warning = parseRate(data.get("capacity_warning"), pool["WarningThresholdRate"])
        capacity_depletion = parseRate(data.get("capacity_depletion"), pool["DepletionThresholdRate"])
        if capacity_warning != pool["WarningThresholdRate"] or capacity_depletion != pool["DepletionThresholdRate"]:
            if capacity_warning <= capacity_depletion:
                storageSystem.setDynamicPoolCapacityThreshold(pool["Id"], capacity_warning, capacity_depletion, data.get("capacity_notify", False))
                changed = True
            else:
                raise Exception("Cannot set Warning Threshold higher than Depletion Threshold.")

        if changed:
            pool = storageSystem.getDynamicPool(pool["Id"])

    Utils.formatPool(pool)
    module.exit_json(pool=pool)

