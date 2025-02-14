import json

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_infra import (
    StorageSystem,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)

logger = Log()
moduleName = "VSM facts"


def cleanResult(vsmResult):
    if vsmResult.get("Model") is not None:
        del vsmResult["Model"]
    if vsmResult.get("Type") is not None:
        del vsmResult["Type"]

    ResourceGroups = vsmResult["ResourceGroups"]
    for rg in ResourceGroups:
        if rg.get("VirtualDeviceModel") is not None:
            del rg["VirtualDeviceModel"]
        if rg.get("VirtualDeviceType") is not None:
            del rg["VirtualDeviceType"]
        if rg.get("VirtualStorageMachineType") is not None:
            del rg["VirtualStorageMachineType"]
        if rg.get("VirtualStorageModelType") is not None:
            del rg["VirtualStorageModelType"]


def runPlaybook(module):

    logger.writeEnterModule(moduleName)

    data = json.loads(module.params["data"])
    virtual_storage_serial = data["virtual_storage_serial"]
    storageSystem = StorageSystem(virtual_storage_serial).vsmManager

    storage_serial = module.params.get("storage_serial", None)
    if storage_serial == "":
        storage_serial = None

    logger.writeParam("virtual_storage_serial={}", virtual_storage_serial)
    logger.writeParam("storage_serial={}", storage_serial)

    if storage_serial is None:
        vsmResult = storageSystem.getVSMBySerial(virtual_storage_serial)
    else:
        vsmResult = storageSystem.getVSMBySerial(storage_serial)

    if vsmResult is not None and vsmResult.get("Serial") is not None:
        vserial = vsmResult.get("Serial")
        if str(vserial) == str(0):
            vsmResult = {}
        else:
            cleanResult(vsmResult)
    else:
        vsmResult = {}
    registration_message = validate_ansible_product_registration()
    logger.writeExitModule(moduleName)
    data = {
        "vsm": vsmResult,
    }
    if registration_message:
        data["user_consent_required"] = registration_message

    module.exit_json(**data)
