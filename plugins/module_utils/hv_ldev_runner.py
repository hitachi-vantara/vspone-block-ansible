import json
import re
import collections
import time
import hashlib


from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_storagemanager import (
    StorageManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_infra import (
    Utils,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_ucpmanager import (
    UcpManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    CommonConstants,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_constants import (
    DEFAULT_NAME_PREFIX,
)

logger = Log()
moduleName = "LUN"


def loggingInfo(msg):
    logger.writeInfo(msg)


def handleResizeInDP(
    storageSystem,
    logicalUnit,
    size,
    storagePool,
    cap_saving_setting,
    lun_name,
    result,
):
    loggingInfo("handleResizeInDP, size={0}".format(size))

    sizeInBytes = getSizeInbytes(size)
    loggingInfo("handleResizeInDP, size={0}".format(size))

    loggingInfo(" entered handleResizeInDP, size={0}".format(sizeInBytes))
    if logicalUnit.get("parityGroup"):
        raise Exception(
            "Cannot resize ({0}) logical units in a parity group.".format(
                logicalUnit.get("TotalCapacity")
            )
        )
    elif float(sizeInBytes) < float(logicalUnit.get("totalCapacity")):
        raise Exception(
            "Cannot resize logical unit to a size less than its current total capacity."
        )
    elif float(sizeInBytes) > float(logicalUnit.get("totalCapacity")):
        lun = logicalUnit["ldevId"]
        lunResourceId = logicalUnit["resourceId"]
        # size = (size * 1024 - logicalUnit.get('totalCapacity')) / 1024
        loggingInfo("expandLun lun={0}".format(lun))
        # sizeInBlock = size * 1024 * 1024 * 1024 / 512
        # sizeInBytes = long(sizeInBlock) * 512
        # storageSystem.expandLunInBytes(lun, sizeInBytes)
        logger.writeInfo("updateLunInDP sizeInBytes={0}".format(sizeInBytes))
        # storageSystem.updateLunInDP(lunResourceId, sizeInBytes)
        storageSystem.updateLunInDP(lunResourceId, size)
        result["changed"] = True
        loggingInfo("after expandLun")
        logicalUnit = storageSystem.getLun(lun)
    return logicalUnit


def handleResize(
    storageSystem,
    logicalUnit,
    size,
    result,
):
    size = getSizeInbytes(size)
    loggingInfo(" enter handleResizeInDP, size={0}".format(size))
    if logicalUnit.get("parityGroup"):
        raise Exception(
            "Cannot resize ({0}) logical units in a parity group.".format(
                logicalUnit.get("TotalCapacity")
            )
        )
    elif float(size) < logicalUnit.get("totalCapacity"):
        raise Exception(
            "Cannot resize logical unit to a size less than its current total capacity."
        )
    elif float(size) > logicalUnit.get("totalCapacity"):
        lun = logicalUnit["ldevId"]
        size = (size * 1024 - logicalUnit.get("totalCapacity")) / 1024
        loggingInfo("expandLun lun={0}".format(lun))
        # sizeInBlock = size * 1024 * 1024 * 1024 / 512
        # sizeInBytes = long(sizeInBlock) * 512
        # storageSystem.expandLunInBytes(lun, sizeInBytes)
        if lun.get("totalCapacity") is not None:
            lun["totalCapacity"] = Utils.formatCapacity(lun["totalCapacity"])
        # uca-2306
        # result["changed"] = True
        loggingInfo("after expandLun")
        # logicalUnit = storageSystem.getLun(lun)

    return logicalUnit


def getSizeInbytes(size):
    logger.writeInfo("getSizeInbytes size={}", size)
    match = re.match(r"(^\d*[.]?\d*)(\D*)", str(size))
    if match:
        sizetype = match.group(2).upper().strip() or "MB"
        logger.writeInfo("getSizeInbytes sizetype={}", sizetype)
        if sizetype not in ("GB", "TB", "MB"):
            raise Exception("This module only accepts MB, GB or TB sizes.")
        else:
            size = float(match.group(1))
            if sizetype == "TB":
                size = size * 1024 * 1024
            if sizetype == "GB":
                size *= 1024
        sizeInBlock = size * 1024 * 1024 / 512
        sizeInBytes = int(sizeInBlock) * 512
        return sizeInBytes


def getLogicalUnit(ucpManager, lun):
    loggingInfo("Enter local getLogicalUnit lun={0}".format(lun))

    if lun is None:
        return None
    logicalUnit = None
    lunInfo = ucpManager.getLunByID(lun)
    logger.writeInfo("335 getLunByID={}", lunInfo)
    if lunInfo:
        for item in lunInfo:
            if str(item.get("ldevId")) == str(lun):
                logicalUnit = item
                # lunIsExisting = True
                break

    # logicalUnit = storageSystem.getLun(lun)

    return logicalUnit


def generate_lun_name_from_spec(lun_name):
    if lun_name is None or lun_name == "":
        return lun_name
    do_not_need_prefix = lun_name.lower().startswith("ansible")
    if do_not_need_prefix:
        pass
    else:
        lun_name = f"ansible-{lun_name}"
    return lun_name


def generate_lun_name(ldev_id):
    label = f"{DEFAULT_NAME_PREFIX}-{ldev_id}"
    return label


def getLogicalUnitsByName(storageSystem, lun_name):
    loggingInfo("Enter getLogicalUnitsByName lun_name={0}".format(lun_name))

    if lun_name is None:
        return None

    logicalUnits = []

    # # SIEAN-201
    # # for idempotent, we cannot getLun this way,
    # # it will error out with exception in the main(),
    # # have to get all then search
    # # logicalUnit = storageSystem.getLun(lun)

    luns = storageSystem.getAllLuns()

    # loggingInfo("luns={0}".format(luns))

    for item in luns:
        if str(item["Name"]) == str(lun_name):
            logicalUnits.append(item)
            break

    return logicalUnits


def isExistingLun(storageSystem, lun):
    try:
        lun_resourceId = get_storage_volume_md5_hash(storageSystem.storage_serial, lun)
        logger.writeDebug("20230617 lun_resourceId={}", lun_resourceId)
        lunInfo = storageSystem.getOneLunByResourceID(lun_resourceId)
        logger.writeDebug("isExistingLun, lunInfo={}", lunInfo)
        return lunInfo
    except Exception as ex:
        loggingInfo("is NOT ExistingLun, ex={0}".format(ex))
        return None


def isValidParityGroup(parity_group):
    try:
        pg = parity_group.replace("-", "")
        loggingInfo("isValidaParityGroup, pg={0}".format(pg))
        int(pg)
        return True
    except Exception:
        return False


def get_storage_volume_md5_hash(storage_system_serial_number, ldev):
    ldev_id = f"{storage_system_serial_number}:{ldev}"
    return f"storagevolume-{get_md5_hash(ldev_id)}"


def get_md5_hash(data):
    # nosec: No security issue here as it is does not exploit any security vulnerability only used for generating unique resource id for UAIG
    md5_hash = hashlib.md5()
    md5_hash.update(data.encode("utf-8"))
    return md5_hash.hexdigest()


def runPlaybook(module):
    logger.writeEnterModule(moduleName)

    storage_system_info = module.params["storage_system_info"]
    storage_serial = storage_system_info.get("serial")
    ucp_serial = CommonConstants.UCP_NAME

    connection_info = module.params["connection_info"]
    management_address = connection_info.get("address")
    management_username = connection_info.get("username")
    management_password = connection_info.get("password")
    subscriberId = connection_info.get("subscriber_id", None)
    auth_token = connection_info.get("api_token", None)

    state = module.params.get("state", "present")
    if state not in ["present", "absent"]:
        raise Exception("State must only be either present or absent.")

    module.params["connection_info"] = json.dumps(connection_info)

    if storage_serial is None:
        raise Exception("The input parameter storage_serial is required.")
    if ucp_serial is None:
        raise Exception("The input parameter ucp_name is required.")

    logger.writeParam("storage_serial={}", storage_serial)
    logger.writeParam("ucp_serial={}", ucp_serial)
    logger.writeParam("management_address={}", management_address)
    logger.writeParam("management_username={}", management_username)

    partnerId = CommonConstants.PARTNER_ID
    # subscriberId=CommonConstants.SUBSCRIBER_ID

    # True: test the rest of the module using api_token

    ucpManager = UcpManager(
        management_address,
        management_username,
        management_password,
        auth_token,
        partnerId,
        subscriberId,
        storage_serial,
    )
    auth_token = ucpManager.getAuthTokenOnly()
    management_username = ""

    storageSystem = None
    try:
        storageSystem = StorageManager(
            management_address,
            management_username,
            management_password,
            auth_token,
            storage_serial,
            ucp_serial,
            partnerId,
            subscriberId,
        )
    except Exception as ex:
        module.fail_json(msg=str(ex))

    if not storageSystem.isStorageSystemInUcpSystem():
        raise Exception("Storage system is not under the management system.")

    #  check the healthStatus=onboarding
    ucpManager = UcpManager(
        management_address,
        management_username,
        management_password,
        auth_token,
        partnerId,
        subscriberId,
        storage_serial,
    )
    if ucpManager.isOnboarding():
        raise Exception("Storage system is onboarding, please try again later.")

    lun_info = module.params["spec"]
    # lun = lun_info.get("luns", None)  # # note, it is using 'luns'
    lun = lun_info.get("ldev_id", None)
    force = lun_info.get("force", None)
    enableDRS = lun_info.get("data_reduction_share", False)

    # 20250103 - vldev_id
    vldev_id = lun_info.get("vldev_id", None)

    # 20240824 - vol tiering validations

    is_relocation_enabled = lun_info.get("is_relocation_enabled", None)
    tier_level_for_new_page_allocation = lun_info.get(
        "tier_level_for_new_page_allocation", None
    )
    tiering_policy = lun_info.get("tiering_policy", None)

    # flatten tiering_policy
    tier_level = None
    tier1_allocation_rate_min = None
    tier1_allocation_rate_max = None
    tier3_allocation_rate_min = None
    tier3_allocation_rate_max = None
    doApplyVolTiering = False

    if tiering_policy:
        tier_level = tiering_policy.get("tier_level", None)
        tier1_allocation_rate_min = tiering_policy.get(
            "tier1_allocation_rate_min", None
        )
        tier1_allocation_rate_max = tiering_policy.get(
            "tier1_allocation_rate_max", None
        )
        tier3_allocation_rate_min = tiering_policy.get(
            "tier3_allocation_rate_min", None
        )
        tier3_allocation_rate_max = tiering_policy.get(
            "tier3_allocation_rate_max", None
        )

    if (
        is_relocation_enabled
        or tier_level_for_new_page_allocation
        or tier_level
        or tier1_allocation_rate_min
        or tier1_allocation_rate_max
        or tier3_allocation_rate_min
        or tier3_allocation_rate_max
    ):
        doApplyVolTiering = True

    if tier_level_for_new_page_allocation:
        if (
            tier_level_for_new_page_allocation != "High"
            and tier_level_for_new_page_allocation != "Middle"
            and tier_level_for_new_page_allocation != "Low"
        ):
            raise Exception(
                "tier_level_for_new_page_allocation must be High, Middle or Low"
            )

    if tier_level:
        if tier_level < 0 or tier_level > 31:
            raise Exception("tier_level must be a value from 0 to 31")

    if tier1_allocation_rate_min:
        if tier1_allocation_rate_min < 1 or tier1_allocation_rate_min > 100:
            raise Exception("tier1_allocation_rate_min must be a value from 1 to 100")

    if tier1_allocation_rate_max:
        if tier1_allocation_rate_max < 1 or tier1_allocation_rate_max > 100:
            raise Exception("tier1_allocation_rate_max must be a value from 1 to 100")

    if tier3_allocation_rate_min:
        if tier3_allocation_rate_min < 1 or tier3_allocation_rate_min > 100:
            raise Exception("tier3_allocation_rate_min must be a value from 1 to 100")

    if tier3_allocation_rate_max:
        if tier3_allocation_rate_max < 1 or tier3_allocation_rate_max > 100:
            raise Exception("tier3_allocation_rate_max must be a value from 1 to 100")

    parity_group = lun_info.get("parity_group", None)
    if parity_group == "":
        parity_group = None
    # if parity_group is not None and not isValidParityGroup(parity_group):
    #     raise Exception('Not a valid Parity group: {0}, please check once and try again.'.format(parity_group))

    if lun is not None and lun == "":
        lun = None

    if lun is None:
        lun = lun_info.get("ldev_id", None)
        if lun == "":
            lun = None
    else:
        if isinstance(lun, list) and len(lun) == 0:
            lun = None
    clonedLunName = lun_info.get("cloned_lun_name", None)
    if clonedLunName == "":
        clonedLunName = None

    result = {"changed": False}

    stripeSizes = ["0", "64", "256", "512"]
    stripeSize = lun_info.get("stripe_size", 512)
    if str(stripeSize) not in stripeSizes:
        raise Exception("Valid value for stripe size is 0, 64, 256 or 512 KB")

    logger.writeParam("lun={}", lun)
    logger.writeParam("clonedLunName={}", clonedLunName)
    logger.writeParam("stripeSizes={}", stripeSizes)
    logger.writeParam("state={}", module.params["state"])

    loggingInfo("luns={0}".format(lun))
    logicalUnit = None
    lunName = lun_info.get("name", None)
    if lunName is None or lunName == "":
        lunName = None

    if lunName and len(lunName) > 32:
        raise Exception("Name cannot be more than 32 characters.")

    def compare(x, y):
        return collections.Counter(x) == collections.Counter(y)

    c_d_setting = ["compression", "compression_deduplication"]
    cap_saving_setting = lun_info.get("capacity_saving", None)
    loggingInfo("20230621 cap_saving_setting={0}".format(cap_saving_setting))

    if cap_saving_setting is not None:
        if isinstance(cap_saving_setting, list):
            c_list = [str(c).strip() for c in cap_saving_setting]
            logger.writeInfo(c_list)
            if compare(c_d_setting, sorted(c_list)):
                cap_saving_setting = "COMPRESSION_DEDUPLICATION"
            elif compare(["compression"], c_list):
                cap_saving_setting = "COMPRESSION"
            elif compare(["disable"], c_list):
                cap_saving_setting = "DISABLED"
            else:
                raise Exception(
                    "Entered {0} is not a valid cap save setting.".format(
                        cap_saving_setting
                    )
                )
        elif cap_saving_setting == "":
            cap_saving_setting = None
        else:
            cap_saving_setting = cap_saving_setting.lower()
            if cap_saving_setting == "compression":
                cap_saving_setting = "COMPRESSION"
            elif cap_saving_setting == "compression_deduplication":
                cap_saving_setting = "COMPRESSION_DEDUPLICATION"
            elif cap_saving_setting == "disabled":
                cap_saving_setting = "DISABLED"
            elif state != "absent":
                raise Exception(
                    "Possible values for capacity_saving are ['compression', 'compression_deduplication', 'disabled']"
                )

    loggingInfo("lunName={0}".format(lunName))
    loggingInfo("382 cap_saving_setting={0}".format(cap_saving_setting))
    lunNameMatch = []

    if lun is not None and ":" in str(lun):
        lun = Utils.getlunFromHex(lun)
        loggingInfo("Hex converted lun={0}".format(lun))

    if lun is not None:
        try:
            lun = int(lun)
        except ValueError:
            raise Exception("Entered {0} is not valid.".format(lun))

    # # lun can be an empty array

    if lun is not None:

        logger.writeDebug("handle existing lun, id={0}".format(lun))

        if lun > 65535:
            raise Exception("Entered ldevid {0} is not valid.".format(lun))

        lunIsExisting = False

        #  a2.4 MT this returns all the luns for this subscriber
        lunInfo = ucpManager.getLunByID(lun)
        logger.writeInfo("RD_0903 getLunByID={}", lunInfo)
        if lunInfo:
            logger.writeInfo("RD_0903 getLunByID len={}", len(lunInfo))
            for item in lunInfo:
                if str(item.get("ldevId")) == str(lun):
                    lunInfo = item
                    lunIsExisting = True
                    break

        logger.writeInfo("lunIsExisting={}", lunIsExisting)
        if not lunIsExisting:
            lunInfo = None

        if state == "absent" and not lunIsExisting:
            loggingInfo(
                "419 lun already deleted or lun is not tagged to this subscriber"
            )
            lunInfo = None
        elif subscriberId and not lunIsExisting:

            #  see if we need to auto-tag to allow lun update

            # the provided lun is not found in the subscriber
            # let's check entitlement using v3
            lun_resourceId = get_storage_volume_md5_hash(storage_serial, lun)
            logger.writeDebug("413 lun_resourceId={}", lun_resourceId)
            lunInfo2 = storageSystem.getOneLunByResourceIDV3(lun)
            logger.writeDebug("416 lunInfo2={}", lunInfo2)

            if lunInfo2:
                #  check entitlement
                for lun2 in lunInfo2:

                    #  assume we only have to check the first one
                    entitlementStatus = lun2.get("entitlementStatus", None)
                    if entitlementStatus is None or entitlementStatus != "assigned":
                        #  not assigned, we can tag this existing volume
                        logger.writeDebug(
                            "416 this volume is unassigned, tag this volume={}", lun
                        )
                        s_resourceId, unused = (
                            storageSystem.getStorageSystemResourceId()
                        )
                        storageSystem.tagV2Volume(s_resourceId, lun_resourceId)

                        #  after tagging, we need the v2 luninfo to continue the processing
                        lunInfo = ucpManager.getLunByID_v2(lun)
                        lunIsExisting = False
                        if lunInfo:
                            logger.writeInfo("454 getLunByID len={}", len(lunInfo))
                            for item in lunInfo:
                                if str(item.get("ldevId")) == str(lun):
                                    lunInfo = item
                                    lunIsExisting = True
                                    break
                        if lunIsExisting:
                            break

                    #  assume we only have to check the first one
                    raise Exception(
                        "This existing volume does not belong to the current subscriber."
                    )

                    # storageVolumeInfo = lun2.get('storageVolumeInfo',None)
                    # if storageVolumeInfo:
                    #     ldevId = storageVolumeInfo.get('ldevId',None)
                    #     if ldevId:
                    #         if str(ldevId) == str(lun):
                    #             # we need to tag this

                    # check v2 existence
                    # logger.writeDebug("349 is v2 ExistingLun?")
                    # lunInfo = isExistingLun(storageSystem, lun)
                    # logger.writeInfo("335 isExistingLun={}", lunInfo)
                    # if lunInfo:
                    #     raise Exception(
                    #         "This existing volume does not belong to this subscriber."
                    #     )

        if not lunInfo and state == "absent":
            logicalUnit = None
        else:
            logicalUnit = lunInfo
    elif lunName is not None:

        #  this is incorrect, we cannot allow update a lun by name only
        #  ldev.id must be given also
        # 20240911 you can have luns with the same name
        pass

        # loggingInfo("312 lunName={0}".format(lunName))

        # lunNameMatch = [
        #     unit
        #     for unit in storageSystem.getAllLuns()
        #     if str(unit.get("name", None)) == lunName
        # ]
        # loggingInfo("lunNameMatch={0}".format(lunNameMatch))
        # if len(lunNameMatch) > 0:
        #     logicalUnits = lunNameMatch
        # if len(lunNameMatch) == 1:
        #     logicalUnit = lunNameMatch[0]

    # loggingInfo("logicalUnit={0}".format(logicalUnit))

    # logger.writeDebug("335 logicalUnit={}", logicalUnit)
    logger.writeDebug("335 state={}", module.params["state"])

    if state == "present":
        existing_pool_id = None
        size = lun_info.get("size", None)
        if size == "":
            size = None

        # match = re.match(r'(\d+)(\D*)', str(size))

        logger.writeParam("size={}", size)
        if size is not None:
            match = re.match(r"(^\d*[.]?\d*)(\D*)", str(size))
            if match:
                sizetype = match.group(2).upper().strip() or "MB"
                logger.writeInfo("L333 sizetype={}", sizetype)
                if sizetype not in ("GB", "TB", "MB"):
                    raise Exception("This module only accepts MB, GB or TB sizes.")
                # else:
                #     size = float(match.group(1))
                #     if sizetype == 'TB':
                #         size = size * 1024 * 1024
                #     if sizetype == 'GB':
                #         size *= 1024
        elif logicalUnit is None and size is None:
            raise Exception(
                "Size is required. This module only accepts MB, GB or TB sizes."
            )

        loggingInfo("state={0}".format(state))

        # Update Lun Name

        logger.writeDebug("335 lun={}", lun)
        logger.writeDebug("335 lunName={}", lunName)
        logger.writeDebug("335 logicalUnit={}", logicalUnit)

        if lunName is not None and lun is not None and logicalUnit is not None:

            # # LUN exists, idempotent
            existing_pool_id = logicalUnit["poolId"]

            if lunName != logicalUnit.get("name"):
                loggingInfo("update the lunName")
                result["changed"] = True
                lunResourceId = logicalUnit["resourceId"]
                storageSystem.updateLunName(lunResourceId, lunName)
                logicalUnit["name"] = lunName

        if cap_saving_setting is not None and logicalUnit is not None:
            loggingInfo(cap_saving_setting)
            # loggingInfo(DedupMode.modes.index(str(logicalUnit.get('dedupCompressionMode'
            #                                                        ))))

            # logger.writeDebug("552 deduplicationCompressionMode={}", logicalUnit.get("deduplicationCompressionMode"))

            if str(logicalUnit.get("deduplicationCompressionMode")) != str(
                cap_saving_setting
            ):
                loggingInfo("update the cap_saving_setting")
                result["changed"] = True
                lunResourceId = logicalUnit["resourceId"]
                storageSystem.setDedupCompression(lunResourceId, cap_saving_setting)
                logicalUnit = getLogicalUnit(ucpManager, lun)

        parity_group = lun_info.get("parity_group", None)
        if parity_group == "":
            parity_group = None

        storagePool = None
        if existing_pool_id:
            storage_pool_id = existing_pool_id
            storagePool = int(storage_pool_id)
            loggingInfo("existing_storage_pool_id={0}".format(existing_pool_id))
        else:
            storage_pool_id = lun_info.get("pool_id", None)
            if storage_pool_id == "":
                storage_pool_id = None

        loggingInfo("20230617 parity_group={0}".format(parity_group))
        loggingInfo("20230617 storage_pool_id={0}".format(storage_pool_id))

        if parity_group is not None and storage_pool_id is not None:
            raise Exception(
                "Cannot create LUN with both storage pool and parity group!"
            )

        if lun is None:
            if parity_group is None and storage_pool_id is None:
                # for create lun only
                raise Exception("Either pool_id or parity_group is required.")

        if parity_group is not None:
            if cap_saving_setting is not None:
                raise Exception(
                    "The capacity_saving parameter is in conflict with parity_group."
                )
            if parity_group.count("-") > 1:
                raise Exception("The parity_group value is not valid.")
            if parity_group[0] == "E":
                x = re.search(
                    r"^E([1-9]|[1-9][0-9])-([1-9]|[1-9][0-9])\b", parity_group
                )
            else:
                x = re.search(r"^([1-9]|[1-9][0-9])-([1-9]|[1-9][0-9])\b", parity_group)
            if not x:
                raise Exception("The parity_group value is not valid.")

        if storage_pool_id is not None:
            storagePool = int(storage_pool_id)
            loggingInfo("storage_pool_id={0}".format(storage_pool_id))

        loggingInfo("check clonedLunName")
        loggingInfo(size)
        loggingInfo(parity_group)
        loggingInfo(storagePool)
        loggingInfo(logicalUnit)

        #  reconciling begins here

        if clonedLunName is not None:
            loggingInfo("Clone mode")
            if not logicalUnit:
                reason = (
                    "More than 1 LUN found with the given name"
                    if len(lunNameMatch) > 1
                    else "No LUN found with the given lun/name"
                )
                raise Exception("Cannot clone logical unit. {0}.".format(reason))
            elif storagePool is not None:
                new_lun = storageSystem.cloneLunInDP(
                    logicalUnit["ldevId"], storagePool, clonedLunName
                )
                lunInfo = None
                i = 0
                while i < 100 and lunInfo is None:
                    lunInfo = storageSystem.getLun(new_lun)
                    i += 1
                    time.sleep(3)
                logger.writeInfo("lunInfo={}", lunInfo)
                result["lun"] = lunInfo
                result["changed"] = True
                Utils.formatLun(result["lun"])
            else:
                raise Exception("Cannot clone logical unit without a storage pool.")
        elif logicalUnit is not None:

            #  20250103 - updateLunVldevId
            if vldev_id is not None and logicalUnit["virtualLogicalUnitId"] != vldev_id:
                result["changed"] = True
                logger.writeDebug("lun={}", lun)
                logger.writeDebug("vldev_id={}", vldev_id)
                s_resourceId, unused = storageSystem.getStorageSystemResourceId()
                lun_resourceId = get_storage_volume_md5_hash(storage_serial, lun)
                storageSystem.updateLunVldevId(
                    s_resourceId,
                    lun_resourceId,
                    lun,
                    logicalUnit["virtualLogicalUnitId"],
                    -1,
                )
                storageSystem.updateLunVldevId(
                    s_resourceId,
                    lun_resourceId,
                    lun,
                    -1,
                    vldev_id,
                )
                logicalUnit["virtualLogicalUnitId"] = vldev_id

            #  20240824 - vol tiering, update lun
            if doApplyVolTiering:
                storageSystem.applyVolTiering(
                    lun,
                    is_relocation_enabled,
                    tier_level_for_new_page_allocation,
                    tier_level,
                    tier1_allocation_rate_min,
                    tier1_allocation_rate_max,
                    tier3_allocation_rate_min,
                    tier3_allocation_rate_max,
                )

                #  after the apply, need to update the local lunInfo
                lunInfotmp = ucpManager.getLunByID(lun)
                if lunInfotmp:
                    for item in lunInfotmp:
                        if str(item.get("ldevId")) == str(lun):
                            logicalUnit = item
                            logger.writeDebug("743 logicalUnit={}", logicalUnit)
                            break

            if size is not None:

                # if lun is None, consider create only, no idempotent,
                # even if logicalUnit is not None, since it is found by lun_name

                loggingInfo("Expand mode, lun={0}".format(logicalUnit["ldevId"]))
                loggingInfo("Expand mode, name={0}".format(logicalUnit["name"]))
                loggingInfo("Expand mode, storagePool={0}".format(storagePool))
                loggingInfo("Expand mode, parity_group={0}".format(parity_group))
                loggingInfo("Expand mode, poolId={0}".format(logicalUnit["poolId"]))

                parity_group = logicalUnit["parityGroupId"]
                storagePool = logicalUnit["poolId"]

                # Expand mode. Only if logical unit was found.

                if len(lunNameMatch) > 1:
                    raise Exception(
                        "Cannot expand logical unit. More than 1 LUN found with the given name. Use lun parameter instead."
                    )
                elif logicalUnit:

                    if storagePool is None and parity_group:
                        raise Exception(
                            "Cannot expand logical unit which is in a parity group."
                        )

                    if storagePool is None:
                        raise Exception(
                            "Cannot expand logical unit, storage pool is not provided."
                        )

                    # uca-2306
                    # result["changed"] = True
                    logicalUnit = handleResizeInDP(
                        storageSystem,
                        logicalUnit,
                        size,
                        storagePool,
                        cap_saving_setting,
                        lunName,
                        result,
                    )
                    result["lun"] = logicalUnit
                    # Utils.formatLun(result["lun"])

        elif logicalUnit is None and (
            storagePool is not None or parity_group is not None
        ):

            loggingInfo("Create mode, parity_group.id={0}".format(parity_group))
            if lun is None:
                logicalUnit = None

            loggingInfo("lun={0}".format(lun))
            loggingInfo("logicalUnit={0}".format(logicalUnit))

            if not size:
                raise Exception(
                    "Cannot create logical unit. No size given (or size was set to 0)."
                )
            elif storagePool is not None:
                loggingInfo("storagePool={0}".format(storagePool))
                loggingInfo("logicalUnit={0}".format(logicalUnit))
                if logicalUnit is not None:

                    # idempotency

                    result["comment"] = "Logical unit already exist."

                    # check for invalid pool id

                    if str(storagePool) != str(logicalUnit["poolId"]):
                        loggingInfo("storagePool={0}".format(logicalUnit["poolId"]))
                        result["comment"] = (
                            "Logical unit {0} is already created with PoolId {1}".format(
                                logicalUnit["ldevId"], logicalUnit["poolId"]
                            )
                        )
                    stripeSize = lun_info.get("stripeSize")
                    if stripeSize is not None and str(stripeSize) != str(
                        logicalUnit["stripeSize"]
                    ):
                        result["comment"] = (
                            "Logical unit {0} is already created with stripeSize {1}".format(
                                logicalUnit["ldevId"], logicalUnit["stripeSize"]
                            )
                        )
                    result["changed"] = False
                    new_lun = None

                    # handleResize idempotent

                    logicalUnit = handleResize(storageSystem, logicalUnit, size, result)
                    logger.writeDebug("LogicalUnit={0}".format(logicalUnit))

                else:
                    logger.writeInfo("createLunInDP size={0}".format(size))
                    logger.writeInfo("createLunInDP sizetype={0}".format(sizetype))

                    logger.writeDebug(
                        "20240824 is_relocation_enabled ={}", is_relocation_enabled
                    )
                    logger.writeDebug(
                        "20240824 tier_level_for_new_page_allocation ={}",
                        tier_level_for_new_page_allocation,
                    )
                    logger.writeDebug("20240824 tiering_policy ={}", tiering_policy)
                    # if lunName is not None:
                    #     if len(lunName) > 31:
                    #         raise Exception(
                    #             "Cannot create logical unit. Invalid lunName {}. Lun name cannot have more than 31 characters .".format(lunName)
                    #             )
                    #     else:
                    #     lunName = lunName  # generate_lun_name_from_spec(lunName)

                    # createLunInDP
                    new_lun, addl_comment = storageSystem.createLunInDP(
                        lun,
                        storagePool,
                        # getSizeInbytes(size),
                        size,
                        cap_saving_setting,
                        enableDRS,
                        lunName,
                    )
                    # UCA-2317
                    time.sleep(5)
                    if (lunName is None or lunName == "") and new_lun is not None:
                        lunName = generate_lun_name(new_lun)
                        logger.writeDebug(
                            "20241211 new_lun ={} lunName = {}", new_lun, lunName
                        )
                        logicalUnit2 = getLogicalUnit(ucpManager, new_lun)
                        lunResourceId = logicalUnit2["resourceId"]
                        storageSystem.updateLunName(lunResourceId, lunName)

                    if addl_comment:
                        result["comment"] = addl_comment

                    # if len(lunNameMatch) > 0:
                    #     lunName = lunName + "_" + hex(int(new_lun))
                    # else:
                    # lunName = lun_info.get("name", "")
                    lunName
                    logger.writeDebug("659 createLunInDP result={}", result)
                    logger.writeDebug("lunName={0}".format(lunName))
                    logger.writeDebug("new_lun={0}".format(new_lun))

                    # 20250103 - updateLunVldevId after createLun
                    if vldev_id is not None:
                        logger.writeDebug("vldev_id={}", vldev_id)
                        s_resourceId, unused = (
                            storageSystem.getStorageSystemResourceId()
                        )
                        lun_resourceId = get_storage_volume_md5_hash(
                            storage_serial, new_lun
                        )
                        # always first unmap
                        storageSystem.updateLunVldevId(
                            s_resourceId,
                            lun_resourceId,
                            new_lun,
                            new_lun,
                            -1,
                        )
                        # then map
                        storageSystem.updateLunVldevId(
                            s_resourceId,
                            lun_resourceId,
                            new_lun,
                            -1,
                            vldev_id,
                        )

                    #  20240824 - vol tiering, create lun
                    if doApplyVolTiering:
                        storageSystem.applyVolTiering(
                            new_lun,
                            is_relocation_enabled,
                            tier_level_for_new_page_allocation,
                            tier_level,
                            tier1_allocation_rate_min,
                            tier1_allocation_rate_max,
                            tier3_allocation_rate_min,
                            tier3_allocation_rate_max,
                        )

                    # a2.4 MT post createLunInDP, need refresh
                    # need to refresh luns for v3 get vol to work??
                    # if so we can to add the code here
                    # the get lun MT playbook would tell us when it is done
                    # do we need to wait for it to be done?
                    # its done in the runner for now, move to here if needed

                    # if lunName != '':
                    #     storageSystem.updateLunName(new_lun, lunName)
                # if cap_saving_setting is not None:

                # # LUN exists, idempotent

                # loggingInfo('update the cap_saving_setting')
                # storageSystem.setDedupCompression(new_lun, cap_saving_setting)
            elif parity_group is not None:
                logger.writeDebug("parity_group={0}".format(parity_group))
                logger.writeDebug("logicalUnit={0}".format(logicalUnit))
                if logicalUnit is not None:

                    # idempotency
                    result["comment"] = "Logical unit already exist."

                    # check for invalid pool id

                    if parity_group != logicalUnit["poolId"]:
                        raise Exception(
                            "Logical unit {0} is already created with PoolId {1}".format(
                                logicalUnit["ldevId"], logicalUnit["poolId"]
                            )
                        )
                    stripeSize = lun_info.get("stripeSize")
                    if stripeSize is not None and str(stripeSize) != str(
                        logicalUnit["stripeSize"]
                    ):
                        raise Exception(
                            "Logical unit {0} is already created with stripeSize {1}".format(
                                logicalUnit["ldevId"], logicalUnit["stripeSize"]
                            )
                        )
                    result["changed"] = False
                    new_lun = None
                else:

                    # resize lun in parity group is not supported?
                    # logicalUnit = handleResize(storageSystem, logicalUnit, size, result)

                    new_lun = storageSystem.createLunInPG(
                        lun,
                        parity_group,
                        getSizeInbytes(size),
                        lun_info.get("stripe_size", 0),
                        lun_info.get("meta_serial", -1),
                        lun_info.get("name", ""),
                    )
                    # UCA-2317
                    time.sleep(5)

                    # 20250103 - updateLunVldevId after createLunInPG
                    if vldev_id is not None:
                        logger.writeDebug("vldev_id={}", vldev_id)
                        s_resourceId, unused = (
                            storageSystem.getStorageSystemResourceId()
                        )
                        lun_resourceId = get_storage_volume_md5_hash(
                            storage_serial, new_lun
                        )
                        # always first unmap
                        storageSystem.updateLunVldevId(
                            s_resourceId,
                            lun_resourceId,
                            new_lun,
                            new_lun,
                            -1,
                        )
                        # then map
                        storageSystem.updateLunVldevId(
                            s_resourceId,
                            lun_resourceId,
                            new_lun,
                            -1,
                            vldev_id,
                        )

                    lunName = lun_info.get("name", "")
                    if lunName is not None or lunName != "":
                        pass
                        # lunName = lunName  # generate_lun_name_from_spec(lunName)
                    else:
                        lunName = generate_lun_name(new_lun)

                    if lunName and new_lun:
                        logger.writeDebug(
                            "20241211 new_lun ={} lunName = {}", new_lun, lunName
                        )
                        logicalUnit2 = getLogicalUnit(ucpManager, new_lun)
                        lunResourceId = logicalUnit2["resourceId"]
                        storageSystem.updateLunName(lunResourceId, lunName)
                    # if lunName != '':
                    # storageSystem.updateLunName(new_lun, lunName)
                    # if cap_saving_setting is not None:

                    # LUN exists, idempotent

                    # loggingInfo('update the cap_saving_setting')
                    # storageSystem.setDedupCompression(new_lun,
                    # cap_saving_setting)
            else:
                raise Exception(
                    "Cannot create logical unit. No storage pool or parity group given."
                )

            if new_lun is None:
                result["lun"] = logicalUnit
                result["comment"] = "Logical unit already exist."
            else:
                lunInfo = None
                logger.writeDebug("20230617 validate new_lun={}", new_lun)

                # i = 0
                # while i < 100 and lunInfo is None:
                # #   lunInfo = storageSystem.getLun(new_lun)
                #   lunInfo = storageSystem.getOneLunByID(new_lun)
                #   i += 1
                #   time.sleep(10)

                lun_resourceId = get_storage_volume_md5_hash(storage_serial, new_lun)
                logger.writeDebug("20230617 lun_resourceId={}", lun_resourceId)

                lunInfo = storageSystem.getOneLunByResourceID(lun_resourceId)
                logger.writeDebug("20230617 lunInfo={}", lunInfo)
                # logger.writeDebug('lunInfo={}', lunInfo)
                logger.writeDebug("753 result={}", result)
                if lunInfo is None:
                    logger.writeDebug(
                        "20230617 volume {} is created, but timed out looking for it.",
                        new_lun,
                    )
                    result["comment"] = (
                        "Volume {} is created, but timed out looking for it.".format(
                            new_lun
                        )
                    )
                else:
                    #  post create
                    #  inject the subscriber info
                    logger.writeDebug("865 subscribe_id={}", subscriberId)
                    lunInfo["entitlementStatus"] = "unassigned"
                    if subscriberId and subscriberId != "":
                        lunInfo["entitlementStatus"] = "assigned"
                        lunInfo["partnerId"] = CommonConstants.PARTNER_ID
                        lunInfo["subscriberId"] = subscriberId
                    Utils.formatLun(lunInfo)
                result["lun"] = lunInfo
                result["changed"] = True

        if logicalUnit:
            logger.writeDebug(logicalUnit)
            result["lun"] = logicalUnit
            Utils.formatLun(result["lun"])
    else:

        # state == absent

        loggingInfo("delete mode")
        if logicalUnit is not None:
            logger.writeDebug("841 logicalUnit={}", logicalUnit)
            logger.writeDebug("841 force={}", force)
            logger.writeDebug("841 logicalUnitId={}", logicalUnit["ldevId"])
            logger.writeDebug(int(logicalUnit["pathCount"]))

            if lunName is not None:
                raise Exception("The name parameter is not supported for delete.")

            #  we should not get here if lun is tagged to other subscriber,
            #  should have been validated already

            if force:
                storageSystem.detachLun(logicalUnit["ldevId"])
            elif int(logicalUnit["pathCount"]) >= 1:
                raise Exception("Cannot delete LUN: Lun is mapped to a hostgroup!")

            storageSystem.deleteLun(logicalUnit["resourceId"])
            result["comment"] = "Ldev is deleted"
            result["lun"] = logicalUnit
            result["changed"] = True
            Utils.formatLun(result["lun"])

        elif lun is None and lunName is None:
            raise Exception("Cannot delete LUN: No lun or name was specified!")
        elif lunName is not None and len(lunNameMatch) > 1:
            raise Exception(
                "Cannot delete LUN: More than 1 LUN with matching name found! Use lun parameter instead."
            )
        else:
            result["lun"] = None
            result["comment"] = "Ldev not found. (Perhaps it has already been deleted?)"
            result["skipped"] = True

    logger.writeExit(moduleName)
    return result
    # module.exit_json(**result)
