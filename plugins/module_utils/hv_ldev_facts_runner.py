from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_storagemanager import (
    StorageManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_ucpmanager import (
    UcpManager,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_infra import (
    Utils,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
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
moduleName = "LUN facts"


def runPlaybook(module):
    logger.writeEnterModule(moduleName)

    lun = None
    count = None
    lun_end = None
    name = None
    is_detailed = None
    data = module.params.get("spec")
    if data:
        name = data.get("name")
        lun = data.get("ldev_id")
        count = data.get("max_count")
        lun_end = data.get("lun_end")
        is_detailed = data.get("is_detailed")

    connection_info = module.params["connection_info"]
    management_address = connection_info.get("address", None)
    management_username = connection_info.get("username", None)
    management_password = connection_info.get("password", None)
    subscriberId = connection_info.get("subscriber_id", None)
    auth_token = connection_info.get("api_token", None)

    storage_system_info = module.params["storage_system_info"]
    storage_serial = storage_system_info.get("serial", None)
    ucp_serial = CommonConstants.UCP_NAME

    logger.writeParam("20230606 storage_serial={}", storage_serial)
    logger.writeParam("lun={}", lun)
    logger.writeParam("name={}", name)
    logger.writeParam("count={}", count)
    logger.writeParam("lun_end={}", lun_end)
    logger.writeParam("is_detailed={}", is_detailed)

    if storage_serial == "":
        storage_serial = None
    if lun == "":
        lun = None
    if count == "":
        count = None
    if lun_end == "":
        lun_end = None
    if name == "":
        name = None

    if ucp_serial == "":
        ucp_serial = None

    if ucp_serial is None:
        raise Exception("The ucp_name is invalid.")

    # x = re.search("^(UCP-CI|UCP-HC|UCP-RS|Logical-UCP)-\d{5,10}$", ucp_serial)
    # if not x:
    #     raise Exception('The ucp_serial is invalid.')

    partnerId = CommonConstants.PARTNER_ID
    # subscriberId=CommonConstants.SUBSCRIBER_ID

    # True: test the rest of the module using api_token

    # if False:
    #     ucpManager = UcpManager(
    #         management_address,
    #         management_username,
    #         management_password,
    #         auth_token,
    #         partnerId,
    #         subscriberId,
    #         storage_serial,
    #     )
    #     auth_token = ucpManager.getAuthTokenOnly()
    #     management_username = ""

    # #  check the healthStatus=onboarding
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

    # lun is a int?
    logger.writeDebug("82 lun={}", lun)
    logger.writeDebug(isinstance(lun, int))

    if lun is not None and ":" in str(lun):
        lun = Utils.getlunFromHex(lun)
        logger.writeDebug("Hex converted lun={0}".format(lun))
        if lun is None:
            raise Exception("The LUN is not found.")

    # if lun is not None:
    #     if not isinstance(lun, int) and lun.startswith('naa.'):
    #         logger.writeDebug('Parsing Naa lun={0}'.format(lun))
    #         storage_serial = Utils.getSerialByNaa(lun)
    #         logger.writeDebug('storage_serial={0}'.format(storage_serial))

    if storage_serial is None:
        if lun is not None and lun.startswith("naa."):
            storage_serial = "get.lun.naa"
        else:
            raise Exception("The storage_serial is missing.")
    # logger.writeDebug('Utils.isGivenValidSerial(storage_serial)={0}'.format(
    #     Utils.isGivenValidSerial(storage_serial)))
    # if not Utils.isGivenValidSerial(storage_serial):
    #     raise Exception(
    #         'Storage system {0} is not registered. Double-check the serial number or run the hv_storagesystem \
    #         module with this storage system.'.format(storage_serial))

    # storageSystem = StorageSystem(storage_serial)
    logger.writeDebug("108 storage_serial={}", storage_serial)
    storageSystem = UcpManager(
        management_address,
        management_username,
        management_password,
        auth_token,
        partnerId,
        subscriberId,
        storage_serial,
    )

    storageManager = None
    try:
        storageManager = StorageManager(
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
        logger.writeException(ex)
        logger.writeInfo("=== End of LDEV Facts ===")
        module.fail_json(msg=str(ex))

    if lun is None and count is not None:
        raise Exception("The ldev_id parameter is required along with max_count.")

    luns = None
    if lun is not None:
        luns = []
        logger.writeDebug("121 lun={}", lun)
        if not isinstance(lun, int) and lun.startswith("naa."):

            # get lun by NAA

            logger.writeDebug("20230606 count={}", count)
            if count is None or count == 0:
                lun = storageSystem.getLunByNaa(lun)
                if lun:
                    luns.append(lun)
            else:
                raise Exception(
                    "The parameter 'count' must be zero if lun starts with 'naa'."
                )
            logger.writeDebug("luns={}", luns)
        elif count is not None:
            if int(count) < 1:
                raise Exception(
                    "The parameter 'count' must be a whole number greater than zero."
                )
            if lun_end is not None:
                raise Exception(
                    "Ambiguous parameters, max_count and lun_end cannot co-exist."
                )

            # get lun with count

            logger.writeDebug("168 getLunByID count={}", count)
            # luns = storageSystem.getAllLuns()
            luns = storageSystem.getLunByID(lun)
            # logger.writeDebug('157 luns={}', luns)
            # g = (i for i, e in enumerate([1, 2, 1]) if e == 1)

            # logger.writeDebug(luns)
            # index = [index for index, item in luns if item.get(
            #     'ldevId') == str(lun)]
            lunswithcount = []
            logger.writeDebug("deduce the output starting at lun={}", lun)
            if luns:
                for index, item in enumerate(luns):
                    # logger.writeDebug('165 item={}', item)
                    item_ldevId = str(item.get("ldevId"))
                    if (
                        (item_ldevId == str(lun))
                        or (str(lun) == "1")
                        or int(item_ldevId) > int(lun)
                    ):
                        logger.writeDebug("20230606 found index={}", index)
                        logger.writeDebug("20230606 count={}", count)
                        lunswithcount = luns[index : index + int(count)]
                        break
            # logger.writeDebug('173 lunswithcount={}', lunswithcount)
            luns = lunswithcount
            # luns = storageSystem.getLunsByCount(lun, count)
        elif lun_end is not None:
            lunswithcount = []
            logger.writeDebug("192 getLunByID lun_end={}", lun_end)
            # luns = storageSystem.getAllLuns()
            luns = storageSystem.getLunByID(lun)
            logger.writeDebug("179 luns={}", luns)
            # luns = storageSystem.getLunsByRange(lun, lun_end)

            # Ensure lun and lun_end are integers (assuming they're not already)
            lun = int(lun)
            lun_end = int(lun_end)

            for item in luns:
                # Safely retrieve ldevId and convert it to an integer, assuming it's numeric
                ldev_id = int(
                    item.get("ldevId", 0)
                )  # Default to 0 if ldevId is not found

                # Check if the current LUN is within the range [lun, lun_end]
                if lun <= ldev_id <= lun_end:
                    lunswithcount.append(item)
                    logger.writeParam("lunswithcount={}".format(lunswithcount))

                # Break the loop if ldev_id reaches or exceeds lun_end
                if ldev_id >= lun_end:
                    break

            luns = lunswithcount

        else:
            lun = storageSystem.getLun(lun)
            if lun:
                luns.append(lun)
        if luns:
            logger.writeDebug("response: luns={}", luns)
    elif luns is not None:

        # # terraform only

        logger.writeDebug("getAllLuns luns={}", luns)
        luns = [unit for unit in storageSystem.getAllLuns() if unit["ldevId"] in luns]
    elif name is not None:
        logger.writeDebug("getAllLuns name={}", name)
        luns = [unit for unit in storageSystem.getAllLuns() if unit["name"] == name]
    else:
        logger.writeDebug("214 getAllLuns")
        luns = storageSystem.getAllLuns()

    logger.writeDebug("223 luns={}", luns)

    registration_message = validate_ansible_product_registration()
    data = {"data": []}

    if registration_message:
        data["user_consent_required"] = registration_message

    if luns is None:
        logger.writeExitModule(moduleName)
        logger.writeInfo("data=[]")
        logger.writeInfo("=== End of LDEV Facts ===")
        module.exit_json(data=[])

    #  for the final luns,
    #  need to get is_encrypted from the parity group as needed
    if is_detailed:
        luns = addDetails(storageManager, storageSystem, luns)

    Utils.formatLuns(luns)
    if luns:
        luns = camel_to_snake_case_dict_array_ext(luns)

    logger.writeExitModule(moduleName)
    # return luns
    logger.writeInfo(f"{luns}")
    logger.writeInfo("=== End of LDEV Facts ===")
    module.exit_json(volumes=luns)


# end of runPlaybook #


# 20240819 "tiering_properties" camel_to_snake_case_dict_array_ext
def camel_to_snake_case_dict_array_ext(items):
    new_items = []
    if items:
        for item in items:
            new_dict = camel_to_snake_case_dict(item)
            # logger.writeDebug("214 new_dict={}", new_dict)
            tiering_properties = new_dict.get("tiering_properties_dto", None)
            if tiering_properties:
                new_dict["tiering_policy"] = camel_to_snake_case_dict(
                    tiering_properties
                )
                new_dict["tiering_policy"]["tier1_used_capacity_mb"] = new_dict[
                    "tiering_policy"
                ]["tier1_used_capacity_m_b"]
                new_dict["tiering_policy"]["tier2_used_capacity_mb"] = new_dict[
                    "tiering_policy"
                ]["tier2_used_capacity_m_b"]
                new_dict["tiering_policy"]["tier3_used_capacity_mb"] = new_dict[
                    "tiering_policy"
                ]["tier3_used_capacity_m_b"]
                new_dict["tiering_policy"]["policy"] = camel_to_snake_case_dict(
                    new_dict["tiering_properties_dto"]["policy"]
                )
                del new_dict["tiering_properties_dto"]
                del new_dict["tiering_policy"]["tier1_used_capacity_m_b"]
                del new_dict["tiering_policy"]["tier2_used_capacity_m_b"]
                del new_dict["tiering_policy"]["tier3_used_capacity_m_b"]
            new_items.append(new_dict)
    return new_items


#  this is only for better performance
#  would not work for OOB if IT does not return luns
def getIscsiTargetsLunMap(storageManager, sresourceId, its):
    logger.writeDebug("Enter")
    # logger.writeDebug("its={}",its)
    ret = {}

    #  given the ITs
    #  get the objectID, get the IT, get logicalUnits, add entry to the ret dict
    for it in its:

        if it is None:
            continue

        # logger.writeDebug("it={}",it)
        resourceId = it.get("resourceId")
        resp = storageManager.getIscsiTarget(sresourceId, resourceId)
        if resp is None:
            continue

        # logger.writeDebug("resp={}",resp)
        logicalUnits = resp.get("logicalUnits")
        logger.writeDebug("logicalUnits={}", logicalUnits)
        if logicalUnits is None:
            continue
        for logicalUnit in logicalUnits:
            lun = str(logicalUnit.get("logicalUnitId"))
            # logger.writeDebug("logicalUnitId={}",lun)
            lunITs = ret.get(lun)
            if lunITs is None:
                lunITs = []
                ret[lun] = lunITs

            #  append this IT to the ret<lun, []IT>
            dto = {}
            dto["id"] = resp["iSCSIId"]
            dto["name"] = resp["iSCSIName"]
            dto["port_id"] = resp["portId"]
            lunITs.append(dto)

    logger.writeDebug("Exit")
    return ret


def getIscsiTargetById(its, id):
    logger.writeDebug("Enter")
    # logger.writeDebug("its={}",its)
    ret = None

    #  given the ITs
    for it in its:

        logger.writeDebug("it={}", it)
        if it is None:
            continue

        itid = it.get("iSCSIId")
        if id is None:
            continue

        if str(itid) == str(itid):
            ret = it
            break

    logger.writeDebug("ret={}", ret)
    logger.writeDebug("Exit")
    return ret


def addDetails(storageManager, storageSystem, luns):
    logger.writeDebug("Enter")

    parityGroups = storageManager.getAllParityGroups()
    hostGroups = storageManager.getAllHostGroups()
    iscsiTargets = storageManager.getIscsiTargets()
    nvmSubsystems, sresourceId = storageManager.getNvmSubsystems()

    logger.writeDebug("len.parityGroups={}", len(parityGroups))
    logger.writeDebug("len.hostGroups={}", len(hostGroups))
    logger.writeDebug("len.iscsiTargets={}", len(iscsiTargets))
    logger.writeDebug("len.nvmSubsystems={}", len(nvmSubsystems))

    for lun in luns:

        logger.writeDebug("lun={}", lun["ldevId"])
        lun["isEncryptionEnabled"] = False

        ret = getAllHostGroupsByLun(hostGroups, lun["ldevId"])
        lun["hostGroups"] = camel_to_snake_case_dict_array(ret)

        ret = getIscsiTargetsByLun(iscsiTargets, lun)
        # ret = getIscsiTargetsByLun_old(iscsiTargets, lun['ldevId'])
        logger.writeDebug("getIscsiTargetsByLun ret={}", len(ret))
        lun["iscsiTargets"] = camel_to_snake_case_dict_array(ret)

        lun["nvmSubsystem"] = camel_to_snake_case_dict(
            getNvmSubsystemByLun(nvmSubsystems, lun["ldevId"])
        )

        pgId = lun["parityGroupId"]
        if pgId != "":
            pg = getParityGroup(parityGroups, pgId)
            lun["isEncryptionEnabled"] = pg["isEncryptionEnabled"]

    logger.writeDebug("Exit")
    # logger.writeDebug("337 luns={}",luns)
    return luns


#  the new way is to get the nvmss.id from the lun
#  then it still has to loop thru the nvmss,
#  so it does not help much,
#  just use this unless there is an issue
def getNvmSubsystemByLun(nvmss, lun):
    logger.writeParam("lun={}", lun)
    ret = {}

    for hg in nvmss:
        if hg is None:
            continue
        namespaces = hg.get("namespaces")
        # logger.writeDebug("namespaces={}",namespaces)
        if namespaces is None:
            continue
        for ns in namespaces:
            if str(ns.get("lun")) == str(lun):
                # logger.writeDebug("nvmss={}",hg)
                ret["id"] = hg["nvmSubsystemId"]
                ret["name"] = hg["nvmSubsystemName"]
                ret["port_id"] = hg["ports"]
                # lun can only be in one nvmss
                logger.writeDebug("ret={}", ret)
                return ret

    # found empty
    logger.writeDebug("ret={}", ret)
    return {}


def getAllHostGroupsByLun(hostGroups, lun):
    funcName = "getAllHostGroupsByLun"
    logger.writeEnterModule(funcName)
    ret = []

    for hg in hostGroups:
        if hg is None:
            continue
        logicalUnits = hg.get("lunPaths")
        if logicalUnits is None:
            continue
        for logicalUnit in logicalUnits:
            # logger.writeDebug("logicalUnit={}",logicalUnit)
            # logger.writeDebug("hg={}",hg)
            if int(logicalUnit.get("ldevId")) == int(lun):
                dto = {}
                dto["id"] = hg["hostGroupId"]
                dto["name"] = hg["hostGroupName"]
                dto["port_id"] = hg["port"]
                ret.append(dto)
                # one lun to many hg
                continue

    logger.writeExitModule(funcName)
    return ret


#  this will work for both inband and OOB
def getIscsiTargetsByLun(its, lun):
    funcName = "getIscsiTargetsByLun"
    logger.writeEnterModule(funcName)
    # logger.writeParam("its={}",its)
    logger.writeParam("lun={}", lun)
    ret = []

    #  get the port list in the lunfact
    ports = lun.get("ports", None)
    if ports is None:
        return []

    for hg in ports:
        if hg is None:
            continue
        id = hg.get("group")
        logger.writeDebug("groupid={}", id)
        if id is None:
            continue
        it = getIscsiTargetById(its, id)
        if it:
            # logger.writeDebug("IscsiTarget={}",it)
            dto = {}
            dto["id"] = it["iSCSIId"]
            dto["name"] = it["iSCSIName"]
            dto["port_id"] = it["portId"]
            ret.append(dto)
            # lun can be in many IscsiTargets
            continue

    logger.writeExitModule(funcName)
    return ret


#  not used anymore - this will only work for inband
def getIscsiTargetsByLun_inband_only(its, lun):
    # logger.writeParam("its={}",its)
    logger.writeParam("lun={}", lun)
    ret = []

    for hg in its:
        if hg is None:
            continue
        logicalUnits = hg.get("logicalUnits")
        # logger.writeDebug("logicalUnits={}",logicalUnits)
        if logicalUnits is None:
            continue
        for logicalUnit in logicalUnits:
            if str(logicalUnit.get("logicalUnitId")) == str(lun):
                # logger.writeDebug("IscsiTarget={}",hg)
                dto = {}
                dto["id"] = hg["iSCSIId"]
                dto["name"] = hg["iSCSIName"]
                dto["port_id"] = hg["portId"]
                ret.append(dto)
                # lun can be in many IscsiTargets
                continue

    logger.writeDebug("Exit")
    return ret


def getParityGroup(parityGroups, pgid):
    for p in parityGroups:
        if p["parityGroupId"] == pgid:
            return p
