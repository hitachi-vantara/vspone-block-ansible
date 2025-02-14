from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_infra import (
    Utils,
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
moduleName = "Storage Parity Group facts"


def writeNameValue(name, value):
    logger.writeInfo(name, value)


def writeMsg(msg):
    logger.writeInfo(msg)


def formatCapacityMB(valueMB, round_digits=4):

    # expected valueMB (from puma):
    # 5120 is 5120MB

    logger.writeDebug("formatCapacityMB, unformatted value={}", valueMB)

    ivalue = float(valueMB)
    if ivalue == 0:
        return "0"

    ivalue = ivalue / 1024 / 1024
    logger.writeDebug("40 formatCapacityMB, ivalue={}", ivalue)
    if ivalue >= 0:
        # drop the fraction
        v = ivalue * 1024 / 1024
        return str(round(v, round_digits)) + "TB"

    ivalue = float(valueMB)
    ivalue = ivalue / 1024
    logger.writeDebug("46 formatCapacityMB, ivalue={}", ivalue)
    if ivalue >= 0:
        # drop the fraction
        v = ivalue * 1024 / 1024
        return str(round(v, round_digits)) + "GB"

    ivalue = float(valueMB)
    logger.writeDebug("52 formatCapacityMB, ivalue={}", ivalue)
    return str(round(ivalue, round_digits)) + "MB"


def formatCapacity(value, round_digits=4, valueInMB=False):

    Utils.logger.writeDebug("formatCapacity, value={}", value)

    ivalue = float(value)
    # Utils.logger.writeParam('formatCapacity, ivalue={}', ivalue)
    if ivalue == 0:
        return "0"

    valueMB = ivalue / 1024 / 1024
    if valueMB > 0 and valueInMB is False:
        logger.writeDebug("41 formatCapacity, valueMB={}", valueMB)
        return formatCapacityMB(valueMB)

    return str(round(valueMB, round_digits)) + "MB"


def formatPg(pgs):
    funcName = "Runner:formatPg"
    logger.writeEnterSDK(funcName)
    try:
        for pg in pgs:
            pg["totalCapacity_mb"] = formatCapacity(pg["totalCapacity"], 4, True)
            pg["freeCapacity_mb"] = formatCapacity(pg["freeCapacity"], 4, True)
            pg["totalCapacity"] = formatCapacity(pg["totalCapacity"])
            pg["freeCapacity"] = formatCapacity(pg["freeCapacity"])
        logger.writeExitSDK(funcName)
    except Exception as ex:
        logger.writeDebug("20230505 Exception={}", ex)


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

    pgid = None
    if module.params.get("spec", None):
        spec = module.params["spec"]
        pgid = spec.get("parity_group_id", None)

    if pgid:
        paritygroup_details = storageSystem.getParityGroup(pgid)
        formatPg([paritygroup_details])
        paritygroup_details = camel_to_snake_case_dict(paritygroup_details)
    else:
        paritygroup_details = storageSystem.getAllParityGroups()
        formatPg(paritygroup_details)
        paritygroup_details = camel_to_snake_case_dict_array(paritygroup_details)
    registration_message = validate_ansible_product_registration()
    data = {
        "parity_group": paritygroup_details,
    }
    if registration_message:
        data["user_consent_required"] = registration_message
    module.exit_json(**data)
