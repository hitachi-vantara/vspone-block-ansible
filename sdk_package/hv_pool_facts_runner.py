import json

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.hv_infra import StorageSystem, StorageSystemManager
from ansible.module_utils.hv_infra import Utils
from ansible.module_utils.hv_logger import Logger

def runPlaybook(module):
    storageSystem = StorageSystem(module.params["storage_serial"])
    data = json.loads(module.params["data"])

    if data.get("id"):
        pools = [storageSystem.getDynamicPool(data["id"])]
    else:
        pools = storageSystem.getDynamicPools()
        if data.get("name"):
            pools = [pool for pool in pools if pool["Name"] == data["name"]]

    Utils.formatPools(pools)
    module.exit_json(pools=pools)

