__metaclass__ = type
import json
import time
import hashlib
import concurrent.futures

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_storagemanager import (
    StorageManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_infra import (
    Utils,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_ucpmanager import (
    UcpManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    CommonConstants,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    camel_to_snake_case_dict_array,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
    generate_random_name_prefix_string,
)

try:
    from .message.vsp_host_group_msgs import VSPHostGroupMessage
except ImportError:
    from message.vsp_host_group_msgs import VSPHostGroupMessage

logger = Log()
moduleName = "Host Group"
dryRun = False


def writeNameValue(name, value):
    logger.writeInfo(name, value)


#     name=name.replace("{}","{0}")
#     logging.debug(name.format(value))


def writeMsg(msg):
    logger.writeDebug(msg)


#     logging.debug(msg)


def delete_volume_with_no_path(storage_system, ldev_id):
    vol_info = storage_system.get_one_lun_by_id_v3(ldev_id)
    if vol_info is not None:
        if vol_info["pathCount"] == 0:
            # Delete the volume
            storage_system.deleteLun(vol_info["resourceId"])


def pre_delete_host_groups(storage_system, host_groups, is_delete_all_luns):
    okToDelete = True
    if is_delete_all_luns is not None and is_delete_all_luns is True:
        ldev_ids = []
        for hg in host_groups:
            writeNameValue("Paths={}", hg["lunPaths"])
            if hg["lunPaths"] is None:
                continue
            lun_paths = hg["lunPaths"]
            if len(lun_paths) > 0:
                for lun_path in lun_paths:
                    ldev_ids.append(lun_path["ldevId"])
                storage_system.unpresentLun(ldev_ids, hg["hostGroupName"], hg["port"])
                with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                    future_tasks = [
                        executor.submit(
                            delete_volume_with_no_path, storage_system, ldev_id
                        )
                        for ldev_id in ldev_ids
                    ]
                # Re-raise exceptions if they occured in the threads
                for future in concurrent.futures.as_completed(future_tasks):
                    future.result()
    else:
        for hg in host_groups:
            writeNameValue("Paths={}", hg["lunPaths"])
            if hg["lunPaths"] is None:
                continue
            if len(hg["lunPaths"]) > 0:
                writeNameValue("Paths={}", hg["lunPaths"][0])
                # hg has presented lun
                okToDelete = False

    return okToDelete


def createHostGroup(
    storageSystem,
    hgName,
    port,
    newWWN,
    newLun,
    hostmodename,
    hostoptlist,
):
    storageSystem.createHostGroup(hgName, port, newWWN)

    # hostmode = HostMode.getHostModeNum(hostmodename or 'LINUX')
    # if hostoptlist is None:
    #     hostoptlist = [41, 51]
    # storageSystem.setHostMode(hgName, port, hostmode, hostoptlist)
    if newLun:
        storageSystem.presentLun(newLun, hgName, port)

    # Load temporary filler data for now

    hg = {"HgName": hgName, "Port": port}


# hostGroups is input/output, input is not none and is not always empty
# knownPortSet are the ports already known to have the hg
# and the hg objects are in the input hostGroups already
# this is to handle the case in which
# the user given only one port to create, we then sync up the hg in all other ports


def getHostGroupsByScanAllPorts(
    storageSystem,
    hgName,
    knownPortSet,
    hostGroups,
):
    logger.writeDebug("Enter getHostGroupsByScanAllPorts")
    hgs = storageSystem.getAllHostGroups()
    for hg in hgs:
        if hg.get("hostGroupName") == hgName:
            hostGroups.append(hg)

    logger.writeDebug(
        "++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++"
    )
    logger.writeDebug(hostGroups)


def runPlaybook(module):
    logger.writeEnterModule(moduleName)

    result = {"changed": False}
    state = module.params["state"]

    connection_info = module.params["connection_info"]
    management_address = connection_info.get("address", None)
    management_username = connection_info.get("username", None)
    management_password = connection_info.get("password", None)
    subscriberId = connection_info.get("subscriber_id", None)
    auth_token = connection_info.get("api_token", None)

    module.params["connection_info"] = json.dumps(connection_info)

    storage_system_info = module.params["storage_system_info"]
    storage_serial = storage_system_info.get("serial", None)
    ucp_serial = CommonConstants.UCP_NAME
    partnerId = CommonConstants.PARTNER_ID

    logger.writeDebug("122 storage_serial={}", storage_serial)
    logger.writeDebug("122 subscriberId={}", subscriberId)

    if storage_serial == "" or storage_serial is None:
        raise Exception("The storage_serial input parameter is required.")

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
        logger.writeInfo("=== End of Host Group operation ===")
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

    subobjState = data.get("state", "present")
    if subobjState == "":
        subobjState = "present"
    if subobjState not in (
        "present",
        "absent",
        "present_ldev",
        "unpresent_ldev",
        "set_host_mode_and_hmo",
        "add_wwn",
        "remove_wwn",
    ):
        raise Exception("The state parameter is invalid.")

    # change the input spec to port instead of ports
    # ports = data.get('ports', None)
    specPort = data.get("port", None)
    ports = []
    ports.append(specPort)
    if specPort is None:
        ports = None

    hgName = data.get("name", None)
    hostmodename = data.get("host_mode", None)
    hostoptlist = data.get("host_mode_options", None)
    logger.writeDebug(hostoptlist)
    wwns = data.get("wwns", None)
    luns = data.get("ldevs")
    is_delete_all_luns = data.get("should_delete_all_ldevs", None)

    logger.writeDebug("2133 ports", ports)

    if ports == "":
        ports = None
    if hostmodename == "":
        hostmodename = None
    if hostoptlist == "":
        hostoptlist = None
    if wwns == "":
        wwns = None
    if luns == "":
        luns = []

    if wwns is not None:
        logger.writeDebug("wwns={}", wwns)
        logger.writeDebug("wwns={}", wwns[0])
        logger.writeDebug("wwns={}", len(wwns))

        if len(wwns[0]) == 1:
            raise Exception("Input wwns is invalid, it needs to be an array.")

    # get all hgs
    # see if all the (hg,port)s are created

    if ports:
        # before the subobjState change
        # make sure all the ports are defined in the storage
        # so we can add comments properly
        sports = storageSystem.getAllStoragePorts()
        for port in ports:
            found = [x for x in sports if x["portId"] == port]
            logger.writeDebug("210found={}", found)
            if found is None or len(found) == 0:
                raise Exception("Port {} is not in the storage system.".format(port))

    logger.writeDebug("subobjState={}", subobjState)
    comments = []
    if (
        subobjState == "present_ldev"
        or subobjState == "unpresent_ldev"
        or subobjState == "set_host_mode_and_hmo"
    ):
        # if hg with given port is not found, we have to ignore
        if wwns is not None:
            wwns = None
            comments.append("The parameter wwns is ignored.")
    if (
        subobjState == "add_wwn"
        or subobjState == "remove_wwn"
        or subobjState == "set_host_mode_and_hmo"
    ):
        # if hg with given port is not found, we have to ignore
        if luns is not None:
            luns = None
            comments.append("The parameter ldevs is ignored.")

    if subobjState == "add_wwn" and (len(ports) > 1 or len(ports) == 0):
        raise Exception("Unable to add WWN to more than one port.")

    if (
        subobjState == "add_wwn"
        or subobjState == "present_ldev"
        or subobjState == "set_host_mode_and_hmo"
    ):
        subobjState = "present"

    if subobjState == "remove_wwn" or subobjState == "unpresent_ldev":
        subobjState = "absent"

    if wwns is not None:

        # upper case the wwns playbook input since the response from services are in upper (SIEAN 280)

        wwns2 = []
        for wwn in wwns:

            # SIEAN 284 - in case wwn is all number

            wwn = str(wwn)
            wwns2.append(wwn.upper())
        newWWN = set(map(str, wwns2))
    else:
        newWWN = set([])

    parsedLuns = []
    if luns:
        for unused, lun in enumerate(luns):
            logger.writeDebug(lun)
            if lun is not None and ":" in str(lun):
                logger.writeDebug(lun)
                lun = Utils.getlunFromHex(lun)
                logger.writeDebug("Hex converted lun={0}".format(lun))
                parsedLuns.append(lun)
            else:
                parsedLuns.append(lun)
    logger.writeDebug(parsedLuns)
    luns = parsedLuns
    logger.writeDebug("LUN Parsing")
    newLun = set(map(int, luns))

    logger.writeParam("state={}", state)
    logger.writeParam("subobjState={}", subobjState)
    logger.writeParam("ports={}", ports)
    logger.writeParam("hgName={}", hgName)
    logger.writeParam("hostmodename={}", hostmodename)
    logger.writeParam("hostoptlist={}", hostoptlist)
    logger.writeParam("newWWN={}", newWWN)
    logger.writeParam("ldevs={}", newLun)

    hostGroups = []

    if ports:

        # make sure all the ports are defined in the storage
        sports = storageSystem.getAllStoragePorts()
        for port in ports:
            found = [x for x in sports if x["portId"] == port]
            logger.writeDebug("210found={}", found)
            if found is None or len(found) == 0:
                raise Exception("Port {} is not in the storage system.".format(port))

        # get hostGroups= get all hgs by ports
        for port in ports:
            writeNameValue("hgName={}", hgName)
            writeNameValue("port{}=", port)
            hg1 = storageSystem.getHostGroup(hgName, port)
            writeNameValue("hg1={}", hg1)

            if subobjState == "absent" and hg1 is None:
                raise Exception("Host group does not exist.")

            if hg1 is not None:
                hostGroups.append(hg1)

        # if hostGroups is None:
        #     comments.append('Hostgroup {} is not found with {}.'.format(hgName, port))

    else:

        # getHostGroup list by name so we will know this is create or modify

        getHostGroupsByScanAllPorts(storageSystem, hgName, None, hostGroups)

    logger.writeDebug("366 hostGroups={}", hostGroups)
    changed = False

    logger.writeDebug("402 hostGroups={}", hostGroups)

    if len(hostGroups) == 0:

        if state == "absent":
            logger.writeInfo("No host groups found, state is absent, no change")
            result["comment"] = (
                "Host group not found. (Perhaps it has already been deleted)"
            )

        if state != "absent":

            writeMsg("Create Mode =========== ")

            if not ports:
                raise Exception(
                    "Host group does not exist; cannot create host groups without ports parameter."
                )
            else:
                for port in ports:
                    if hgName is None:
                        hgName = generate_random_name_prefix_string()
                    writeNameValue("createHostGroup={}", hgName)
                    writeNameValue("port={}", port)
                    writeNameValue("newWWN={}", newWWN)

                    if hostmodename == "" or hostmodename is None:
                        hostmodename = "LINUX"
                    # hostmode = HostMode.getHostModeNum(hostmodename)

                    # if hostoptlist is None:
                    # hostoptlist = [47, 51]
                    if hostoptlist is None:
                        hostoptlist = []
                    writeNameValue("hostoptlist={}", hostoptlist)

                    logger.writeDebug("345 createHostGroup")
                    retry = 0
                    if hgName is None:
                        hgName = generate_random_name_prefix_string()
                    while retry < 5:

                        logger.writeDebug("hgName={}", hgName)

                        try:
                            hg = storageSystem.createHostGroup(
                                hgName, port, newWWN, hostmodename, hostoptlist
                            )
                            break
                        except Exception as ex:
                            logger.writeError(str(ex))
                            if "The hostgroup is already present" in str(ex):
                                retry += 1
                                hgName = generate_random_name_prefix_string()
                                continue
                            else:
                                raise ex

                    logger.writeDebug("345 luns to add {}", luns)

                    if luns:
                        for lun in luns:
                            writeNameValue("presentLun={}", lun)
                            storageSystem.presentLun(newLun, hgName, port)

                    # Load temporary filler data for now

                    hg = {"HgName": hgName, "Port": port}
                    hostGroups.append(hg)
                    changed = True
                    time.sleep(30)
    elif state == "absent":

        # if we want to support the case:
        # the user given one lun, one port to create hg,
        # do sync up the hg in all other ports
        # then we need to call getHostGroupsByScanAllPorts(storageSystem, hgName, ?, hostGroups)

        # Delete mode.

        writeMsg("Delete hgs from the list  =========== ")

        okToDelete = pre_delete_host_groups(
            storageSystem, hostGroups, is_delete_all_luns
        )

        if okToDelete:
            for hg in hostGroups:
                writeNameValue("del hg={}", hg)
                writeNameValue("del HgName={}", hg["hostGroupName"])
                writeNameValue("del Port={}", hg["port"])
                writeNameValue("calling deleteHostGroup, dryRun={}", dryRun)
                if not dryRun:
                    storageSystem.deleteHostGroup(hg["hostGroupName"], hg["port"])
                    changed = True
                    result["comment"] = (
                        VSPHostGroupMessage.DELETE_SUCCESSFULLY.value.format(
                            hg["hostGroupName"]
                        )
                    )
        else:

            result["comment"] = (
                "Hostgroup has ldevs presented. Please make sure to unpresent all ldev prior deleting hostgroup."
            )
            writeMsg("NO Delete with comment")
    else:

        # Modify mode. Certain operations only occur if state is overwrite.

        writeMsg("Update Mode =========== ")

        # check for add/remove hostgroup for each given port

        oldports = [
            hostGroup["port"]
            for hostGroup in hostGroups
            if hostGroup["hostGroupName"] == hgName
        ]
        oldports = set(oldports)

        if ports is not None:
            newports = set(map(str, ports))
        else:

            # ports is not given in the playbook, we will apply the change to all existing ports (SIEAN 281 282)

            writeMsg("apply update to all existing ports")
            newports = set(oldports)

        addPort = newports - oldports
        delPort = oldports & newports

        writeNameValue("oldports={}", oldports)
        writeNameValue("newports={}", newports)
        writeNameValue("addPort={}", addPort)
        writeNameValue("delPort={}", delPort)

        newports = None

        if addPort and subobjState == "present":
            writeMsg("create hg by addPort")
            writeNameValue("hostGroups={}", hostGroups)

            # use the first element in the hostgroup list for cloning

            hg = hostGroups[0]

            newports = addPort

            # get hostoptlist from the existing hg

            writeNameValue("hostModeOptions={}", hg["hostModeOptions"])
            hgHMO = [opt["hostModeOptionNumber"] for opt in hg["hostModeOptions"] or []]
            hmName = hg["hostMode"]
            writeNameValue("hmName={}", hmName)

            # to create hg, you must have a list of ports to add

            for port in addPort:

                # clone an existing host group
                # then add it to the existing hg list
                # then let it go thru the add/remove process below

                writeNameValue("Paths={}", hg.get("lunPaths", None))
                hgLun = set(path["ldevId"] for path in hg.get("lunPaths", None) or [])

                if dryRun:
                    writeMsg("DRYRUN = TRUE")
                    continue

                # update mode subobjState create

                logger.writeDebug("464 createHostGroup")
                storageSystem.createHostGroup(hgName, port, newWWN, hmName, hostoptlist)

                logger.writeDebug("464 getHostGroup")
                hgtmp = storageSystem.getHostGroup(hgName, port)
                if hgtmp is not None:

                    # to help oob performance
                    # add the newly created hg to list instead of getAllHostGroups

                    hostGroups.append(hgtmp)

            changed = True

            # this is incorrect, you del hg not on subobjState, del only on state
        #             if delPort and subobjState == "absent":
        #                 writeMsg("update hg, del port")
        #                 for port in delPort:
        #                     # sss
        #                     preDeleteHostGroup(storageSystem, hostGroups, hgName, port)
        #                     storageSystem.deleteHostGroup(hgName, port)
        #                 changed = True

        # at this point, hostGroups has the list of hg to update
        # whether it is create with 1..n ports or
        # update with 0..n ports in the input
        # update with no ports given mean apply change to all ports

        # process each existing group, check for add/remove hg attributes

        writeMsg("walk thru each host group, check for update ======================")

        oldports = [
            hostGroup["port"]
            for hostGroup in hostGroups
            if hostGroup["hostGroupName"] == hgName
        ]
        oldports = set(oldports)

        if ports is not None:
            newports = set(map(str, ports))
        else:
            writeMsg("apply update to all existing ports")
            newports = set(oldports)

        addPort = newports - oldports
        delPort = oldports & newports

        writeNameValue("oldports={}", oldports)
        writeNameValue("newports={}", newports)
        writeNameValue("addPort={}", addPort)
        writeNameValue("delPort={}", delPort)

        writeNameValue("state={}", state)
        writeNameValue("subobjState={}", subobjState)

        if subobjState == "present":

            # update per the list provided, if new port,
            # it would have been created above

            portsToUpdate = newports
        else:

            logger.writeDebug("remove attributes from list, only if it exists")

            portsToUpdate = delPort

        for hgPort in portsToUpdate:

            hg = [hostGroup for hostGroup in hostGroups if hostGroup["port"] == hgPort]
            writeNameValue("update hg={}", hg)
            if hg is None or len(hg) == 0:
                continue
            hg = hg[0]
            if "port" not in hg:
                continue
            writeNameValue("update HgName={}", hg["hostGroupName"])
            writeNameValue("update Port={}", hg["port"])

            port = hg["port"]
            writeNameValue("processing port={}", port)

            if dryRun:
                writeMsg("DRYRUN = TRUE")
                continue

            writeMsg("check hostmode and hostoptlist for update")
            if hostmodename is not None or hostoptlist is not None:
                if hostmodename is not None:
                    hostmode = hostmodename
                else:
                    hostmode = hg["hostMode"]

                # for hostmode, you can only update, no delete

                writeNameValue("update hostmode={}", hostmode)

                hgHMO = [
                    opt["hostModeOptionNumber"] for opt in hg["hostModeOptions"] or []
                ]
                if hostoptlist is not None:

                    # hostoptlist is the user input

                    oldlist = set(hgHMO)
                    newlist = set(hostoptlist)
                    addlist = newlist - oldlist
                    oldlist & newlist

                    if subobjState == "present":
                        # # add = new - old
                        hostopt = hgHMO + list(addlist)
                    else:
                        # del = old & new
                        hostopt = list(set(hgHMO) - set(hostoptlist))
                else:
                    hostopt = hgHMO
                writeNameValue("update hostopt={}", hostopt)

                if hostmode != hg["hostMode"] or set(hostopt) != set(hgHMO):
                    writeMsg("call setHostMode()")
                    storageSystem.setHostMode(hgName, port, hostmode, hostopt)
                    hgLun = set(
                        path["ldevId"] for path in hg.get("lunPaths", None) or []
                    )
                    changed = True

            writeMsg("check wwns for update")
            if newWWN:  # If newWWN is present,  update wwns
                wwns = (str(path["id"]) for path in hg.get("wwns", None) or [])
                hgWWN = set(wwns)
                addWWN = newWWN - hgWWN
                delWWN = hgWWN.intersection(newWWN)

                writeNameValue("old hgWWN={}", hgWWN)
                writeNameValue("newWWN={}", newWWN)
                writeNameValue("addWWN={}", addWWN)
                writeNameValue("delWWN={}", delWWN)

                if addWWN and subobjState == "present":
                    if len(addWWN) > 0:
                        storageSystem.addWWN(hgName, port, addWWN)
                        changed = True
                if subobjState == "absent":
                    if delWWN:
                        writeNameValue("removeWWN delWWN={0}", delWWN)
                        if len(delWWN) > 0:
                            storageSystem.removeWWN(hgName, port, delWWN)
                            changed = True
                    else:
                        result["comments"] = "WWN(s) are not in the host group."

            writeMsg("532 check luns for update")
            if luns:  # If luns is present, present or overwrite luns
                hgLun = set(
                    path.get("ldevId") for path in hg.get("lunPaths", None) or []
                )
                writeNameValue("newLun={0}", newLun)
                addLun = newLun - hgLun
                # delLun = list(set(hgLun) - set(newLun))
                delLun = hgLun.intersection(newLun)
                writeNameValue("hgLun={0}", hgLun)
                writeNameValue("541 addLun={0}", addLun)
                writeNameValue("542 delLun={0}", delLun)

                if subobjState == "present" and addLun:
                    if len(addLun) > 0:
                        storageSystem.presentLun(addLun, hgName, port)
                        changed = True

                if subobjState == "absent":
                    if delLun:
                        writeNameValue("unpresentLun delLun={0}", delLun)
                        if len(delLun) > 0:
                            storageSystem.unpresentLun(delLun, hgName, port)
                            changed = True
                    else:
                        result["comments"] = "LUN(s) are not in the host group."

                # hg = {'HgName': hgName, 'Port': port}
                # hostGroups.append(hg)

    writeNameValue("20230606 615 changed={}", changed)
    logger.writeDebug("20230606 615 changed={}", changed)
    logger.writeDebug("20230606 615 state={}", state)
    if changed and state != "absent":
        hostGroups = refreshHostGroups(storageSystem, hostGroups)
        # for hg in hostGroups:
        #     hg['hostMode'] = HostMode.getHostModeName(str(hg['hostMode']))

    #         for hg in hostGroups:
    #             hg["HostMode"] = HostMode.getHostModeName(hg["HostMode"])
    #             hg["hostModeOptions"] = [opt["hostModeOptionNumber"] for opt in hg["hostModeOptions"] or []]
    #
    #             hg["luns"] = set(path["lupathID"] for path in hg.get("Paths",None) or [])
    #             del hg["Paths"]

    if state != "absent":
        formatHgs(hostGroups)
        logger.writeDebug("656 hostGroups={}", hostGroups)
        result["hostGroups"] = camel_to_snake_case_dict_array(hostGroups)

    result["changed"] = changed
    if comments:
        result["comments"] = comments
    logger.writeExitModule(moduleName)
    registration_message = validate_ansible_product_registration()
    if registration_message:
        result["user_consent_required"] = registration_message

    logger.writeInfo(f"{result}")
    logger.writeInfo("=== End of Host Group operation ===")
    module.exit_json(**result)


def formatHgs(hostGroups):
    if hostGroups is None:
        return

    writeNameValue("670 formatHgs hostGroups={}", hostGroups)
    for hg in hostGroups:
        writeNameValue("670 formatHgs hg={}", hg)
        if not hg:
            continue
        if hg.get("resourceId"):
            del hg["resourceId"]

        if hg.get("storageId"):
            del hg["storageId"]

        writeNameValue("HostMode={}", hg.get("hostMode"))
        # hg['hostModeOptions'] = [opt['hostModeOptionNumber'] for opt in
        #                          hg['hostModeOptions'] or []]
        if hg.get("hostModeOptions", None) is None:
            hg["hostModeOptions"] = []
        if hg.get("hostModeOptions", None) is not None:
            writeNameValue("hostModeOptions={}", hg["hostModeOptions"])

        #         hg["luns"] = set(path["lupathID"] for path in hg.get("Paths",None) or [])

        # paths = hg.get('lunPaths', None)
        # if paths:
        #     writeNameValue('Paths={}', hg['lunPaths'])
        #     for path in paths:
        #         if 'lupathHostID' in path:
        #             path['hostGroupLunId'] = path['lupathHostID']
        #             del path['lupathHostID']
        #         if 'lupathID' in path:

        #             # path["lunId"] = path["lupathID"]

        #             path['ldevId'] = path['lunId']
        #             del path['lupathID']
        #         if 'hexLupathID' in path:

        #             # path["lunId"] = path["lupathID"]

        #             path['hexldevId'] = path['hexLupathID']
        #             del path['hexLupathID']
        # else:
        #     hg['lunPaths'] = []

        if hg.get("ResourceGroupId") == -1:
            hg["ResourceGroupId"] = ""


#         hg["luns"] = [path["lupathID"] for path in hg["Paths"] or []]
#         if "Paths" in hg:
#             del hg["Paths"]

#     for hostGroup in hostGroups:
#         if "Paths" in hostGroup and hostGroup["Paths"] is None:
#             hostGroup["Paths"] = []
#         if hostGroup["hostModeOptions"] is None:
#             hostGroup["hostModeOptions"] = []
#         if hostGroup["WWNS"] is None:
#             hostGroup["WWNS"] = []

# given the hostGroups list, refresh in hg in the list


def refreshHostGroups(storageSystem, hostGroups):
    if hostGroups is None:
        return

    logger.writeDebug("20230606 715 refreshHostGroups hostGroups={}", hostGroups)

    hgs = []
    for hostGroup in hostGroups:
        hgName = None
        port = None
        if "HgName" not in hostGroup:
            hgName = hostGroup["hostGroupName"]
        else:
            hgName = hostGroup["HgName"]

        if "Port" not in hostGroup:
            port = hostGroup["port"]
        else:
            port = hostGroup["Port"]

        logger.writeDebug("20230606 715 refreshHostGroups hgName={}", hgName)
        logger.writeDebug("20230606 715 refreshHostGroups port={}", port)
        hg = storageSystem.getHostGroup(hgName, port)
        hgs.append(hg)

    return hgs


def get_storage_hostgroup_md5_hash(storage_system_serial_number, hgname, hgport):
    key = f"{storage_system_serial_number}:{hgname.lower()}:{hgport.lower()}"
    return f"hostgroup-{get_md5_hash(key)}"


def get_md5_hash(data):
    # nosec: No security issue here as it is does not exploit any security vulnerability only used for generating unique resource id for UAIG
    md5_hash = hashlib.md5()
    md5_hash.update(data.encode("utf-8"))
    return md5_hash.hexdigest()
