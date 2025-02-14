from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_storagemanager import (
    StorageManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_ucpmanager import (
    UcpManager,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    CommonConstants,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    camel_to_snake_case_dict_array,
    camel_to_snake_case_dict,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)

logger = Log()
moduleName = "Storage Pool facts"


def writeNameValue(name, value):
    logger.writeInfo(name, value)


def writeMsg(msg):
    logger.writeInfo(msg)


def formatPools(pools):

    if pools is None:
        return

    for pool in pools:
        if pool is None:
            continue
        for key in list(pool.keys()):
            if pool.get(key) is not None:
                if str(pool[key]) == str(-1):
                    pool[key] = ""


def runPlaybook(module):

    logger.writeEnterModule(moduleName)

    connection_info = module.params["connection_info"]
    management_address = connection_info.get("address", None)
    management_username = connection_info.get("username", None)
    management_password = connection_info.get("password", None)
    api_token = connection_info.get("api_token", None)
    subscriberId = connection_info.get("subscriber_id", None)

    storage_system_info = module.params["storage_system_info"]
    storage_serial = storage_system_info.get("serial", None)
    ucp_serial = CommonConstants.UCP_NAME

    logger.writeDebug("20230606 storage_serial={}", storage_serial)
    logger.writeDebug("20230606 ucp_name={}", ucp_serial)

    partnerId = CommonConstants.PARTNER_ID

    # True: test the rest of the module using api_token

    # if False:
    #     ucpManager = UcpManager(
    #         management_address,
    #         management_username,
    #         management_password,
    #         api_token,
    #         partnerId,
    #         subscriberId,
    #         storage_serial,
    #     )
    #     api_token = ucpManager.getAuthTokenOnly()
    #     management_username = ""

    storageSystem = None
    try:
        storageSystem = StorageManager(
            management_address,
            management_username,
            management_password,
            api_token,
            storage_serial,
            ucp_serial,
            partnerId,
            subscriberId,
        )
    except Exception as ex:
        module.fail_json(msg=str(ex))

    if not storageSystem.isStorageSystemInUcpSystem():
        raise Exception("Storage system is not under the management system.")

    partnerId = CommonConstants.PARTNER_ID
    subscriberId = CommonConstants.SUBSCRIBER_ID
    #  check the healthStatus=onboarding
    ucpManager = UcpManager(
        management_address,
        management_username,
        management_password,
        api_token,
        partnerId,
        subscriberId,
        storage_serial,
    )
    if ucpManager.isOnboarding():
        raise Exception("Storage system is onboarding, please try again later.")

    poolId = None
    if module.params.get("spec", None):
        data = module.params["spec"]
        poolId = data.get("pool_id", None)
    if poolId:
        storage_pool_details = storageSystem.getStoragePoolDetails(poolId)
        formatPools([storage_pool_details])
        storage_pool_details = camel_to_snake_case_dict(storage_pool_details)
    else:
        storage_pool_details = storageSystem.getAllStoragePoolDetails()
        formatPools(storage_pool_details)
        storage_pool_details = camel_to_snake_case_dict_array(storage_pool_details)

    # formatPools(storage_pool_details)
    # storage_pool_details = camel_to_snake_case_dict_array(storage_pool_details)
    registration_message = validate_ansible_product_registration()
    data = {
        "storage_pool": storage_pool_details,
    }
    if registration_message:
        data["user_consent_required"] = registration_message
    module.exit_json(**data)
    # return storage_pool_details
