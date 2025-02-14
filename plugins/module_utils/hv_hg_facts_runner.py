from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_infra import (
    Utils,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_storagemanager import (
    StorageManager,
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
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    camel_to_snake_case_dict_array,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)

logger = Log()
moduleName = "Host Group facts"


def writeNameValue(name, value):
    logger.writeDebug(name, value)


def runPlaybook(module):

    logger.writeEnterModule(moduleName)

    connection_info = module.params["connection_info"]
    management_address = connection_info.get("address", None)
    management_username = connection_info.get("username", None)
    management_password = connection_info.get("password", None)
    subscriberId = connection_info.get("subscriber_id", None)
    auth_token = connection_info.get("api_token", None)
    result = {}

    storage_system_info = module.params["storage_system_info"]
    storage_serial = storage_system_info.get("serial", None)
    ucp_serial = CommonConstants.UCP_NAME
    partnerId = CommonConstants.PARTNER_ID

    logger.writeDebug("40 storage_serial={}", storage_serial)
    logger.writeDebug("40 subscriberId={}", subscriberId)

    # True: test the rest of the module using api_token

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
        logger.writeError(str(ex))
        logger.writeInfo("=== End of Host Group Facts ===")
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

    data = module.params["spec"]
    if data is None:
        data = {}

    options = data.get("query", [])

    hostGroups = []
    ports = data.get("ports")
    name = data.get("name")
    if name == "":
        name = None

    lun = data.get("lun")
    if lun is not None and ":" in str(lun):
        lun = Utils.getlunFromHex(lun)
        logger.writeDebug("Hex converted lun={0}".format(lun))
    if lun == "":
        lun = None

    logger.writeDebug("data={0}".format(data))
    logger.writeDebug("Ports={0}".format(ports))
    logger.writeDebug("name={0}".format(name))
    logger.writeDebug("lun={0}".format(lun))

    hostGroups = storageSystem.getAllHostGroups()
    logger.writeDebug("88 hostGroups={}", hostGroups)

    if hostGroups:
        hostGroups2 = []
        for hh in hostGroups:
            hhp = hh.get("port", None)
            if hhp is None:
                continue
            hostGroups2.append(hh)
        hostGroups = hostGroups2

    if ports:
        #  apply port filter
        portSet = set(ports)
        hostGroups = [group for group in hostGroups if group["port"] in portSet]
        if len(hostGroups) == 0:
            result["comment"] = "No hostgroup is found with the given ports"

    if name is not None:
        #  apply name filter
        logger.writeParam("name={}", data["name"])
        # hostGroups = [group for group in hostGroups if group['hostGroupName'] == name]
        logger.writeDebug(hostGroups)
        hostGroups = [x for x in hostGroups if x["hostGroupName"] == name]
        if len(hostGroups) == 0:
            result["comment"] = "No hostgroup is found by name " + name
        logger.writeDebug(hostGroups)

    if lun is not None:
        #  apply lun filter
        logger.writeParam("apply filter, lun={}", data["lun"])
        hostGroupsNew = []
        for hg in hostGroups:
            lunPaths = hg.get("lunPaths", None)
            if lunPaths:
                # logger.writeDebug('Paths={}', hg['lunPaths'])
                for lunPath in lunPaths:
                    if "ldevId" in lunPath:
                        # logger.writeDebug('lunPath[ldevId]={}', lunPath['ldevId'])
                        if lun == str(lunPath["ldevId"]):
                            #  found the lun in the lunPaths, return the whole lunPaths,
                            #  if you only want to return the matching lun instead of the whole list,
                            #  then you need to add more code here
                            logger.writeDebug(
                                "found lun in lunPaths={}", hg["lunPaths"]
                            )
                            hostGroupsNew.append(hg)
                            break
        hostGroups = hostGroupsNew
        # hostGroups = storageSystem.getHostGroupsForLU(data['lun'])
        # if ports:
        #     portSet = set(ports)
        #     hostGroups = [group for group in hostGroups if group['Port'
        #                                                          ] in portSet]
        # else:
        #     hostGroups = storageSystem.getAllHostGroups()
        #     if ports:
        #         portSet = set(ports)
        #         hostGroups = [group for group in hostGroups if group['port'
        #                                                              ] in portSet]

    #  prepare output, apply filters
    for hg in hostGroups:

        if hg.get("hostModeOptions", None) is None:
            hg["hostModeOptions"] = []

        del hg["resourceId"]

        # if not options or 'ldevs' in options:
        #     paths = hg.get('lunPaths', None)
        #     if paths:
        #         writeNameValue('Paths={}', hg['lunPaths'])
        #         for path in paths:
        #             if 'lupathHostID' in path:
        #                 path['hostGroupLunId'] = path['lupathHostID']
        #                 del path['lupathHostID']
        #             if 'lupathID' in path:

        #                 #                             path["lunId"] = path["lupathID"]

        #                 path['ldevId'] = path['lupathID']
        #                 del path['lupathID']
        #             if 'hexLupathID' in path:

        #                 # path["lunId"] = path["lupathID"]

        #                 path['hexLdevId'] = path['hexLupathID']
        #                 del path['hexLupathID']
        #     else:
        #         hg['Paths'] = []
        # else:
        #     del hg['Paths']

        if options:
            if "wwns" not in options:
                del hg["wwns"]
            if "ldevs" not in options and lun is None:
                del hg["lunPaths"]

            # if hg.get("hostModeOptions", None):

        # writeNameValue('hostModeOptions={}', hg['hostModeOptions'])
        # del hg['hostModeOptions']

        if hg.get("ResourceGroupId") == -1:
            hg["ResourceGroupId"] = ""

    result["hostGroups"] = camel_to_snake_case_dict_array(hostGroups)
    logger.writeExitModule(moduleName)
    registration_message = validate_ansible_product_registration()
    if registration_message:
        result["user_consent_required"] = registration_message

    logger.writeInfo(f"{result}")
    logger.writeInfo("=== End of Host Group Facts ===")
    module.exit_json(**result)
