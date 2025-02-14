import json

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_infra import (
    StorageSystem,
    Utils,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)

logger = Log()
moduleName = "VSM facts"


def writeNameValue(name, value):
    logger.writeInfo(name, value)


def writeMsg(msg):
    logger.writeInfo(msg)


def mockGetVSM():

    vsms = []
    resourceGroups = []

    vsm = {"Serial": 411223, "Type": 7}

    resourceGroup = {
        "MetaResourceSerial": 415056,
        "ResourceGroupId": 9,
        "ResourceGroupName": "ansible-11223",
        "VirtualDeviceId": 411223,
        "VirtualDeviceType": 7,
    }
    resourceGroups.append(resourceGroup)
    vsm["ResourceGroups"] = resourceGroups

    vsms.append(vsm)

    # return vsms
    return vsm


def getVSM(storage_serial, virtual_storage_serial):
    writeMsg("================================================================")
    writeMsg("enter getVSM")
    writeNameValue("storage_serial={}", storage_serial)
    writeNameValue("virtual_storage_serial={}", virtual_storage_serial)

    writeMsg("call getVSMBySerial")

    storageSystem = StorageSystem(virtual_storage_serial).vsmManager
    vsms = storageSystem.getVSMBySerial(virtual_storage_serial)

    writeMsg("return from getVSMBySerial")

    if vsms is None:
        writeMsg("getVSMBySerial returns None")
    else:
        writeMsg("check for empty returns means vsm does not exist")
        if vsms.get("Serial") is not None:
            vserial = vsms.get("Serial")
            writeNameValue("found Serial in getVSM output={}", vserial)
            if str(vserial) == str(0):
                writeMsg("getVSMBySerial returns empty response")
                vsms = None

    vsmResult = []
    if vsms is not None:
        vsmResult = vsms
    return vsmResult


def validateMS(meta_resources):
    resource_groups = []
    for resource in meta_resources:
        if "serial" not in resource:
            raise Exception(
                "Meta Resource object must include a serial number!! (Error at index {0})".format(
                    len(resource_groups)
                )
            )
        resource_groups.append(resource)


def getResourceGroup(vsm, storage_serial, virtual_storage_serial, name):

    writeMsg("Enter getResourceGroup from getVSM -------------------")
    writeNameValue("storage_serial={}", storage_serial)
    writeNameValue("virtual_storage_serial={}", virtual_storage_serial)
    writeNameValue("name={}", name)

    # find the resource in the get vsm output
    # for vsm in vsms:
    ResourceGroups = vsm["ResourceGroups"]

    found = False
    rgs = []
    for rsrc in ResourceGroups:
        writeNameValue(
            "getResourceGroup.MetaResourceSerial={}", rsrc["MetaResourceSerial"]
        )
        writeNameValue("getResourceGroup.VirtualDeviceId={}", rsrc["VirtualDeviceId"])
        writeNameValue(
            "getResourceGroup.ResourceGroupName={}", rsrc["ResourceGroupName"]
        )
        if (
            str(rsrc["MetaResourceSerial"]) == str(storage_serial)
            and str(rsrc["VirtualDeviceId"]) == str(virtual_storage_serial)
            and rsrc["ResourceGroupName"] == name
        ):
            rgs.append(rsrc)
            found = True

    if found:
        writeMsg("getResourceGroup.found")
        return rgs
    else:
        writeMsg("getResourceGroup.not.found")
        return None


def handleDriveGroups(old, new, doAdd, storage, rgId):

    writeMsg("Enter handleDriveGroups-------------------")
    writeNameValue("old={}", old)
    writeNameValue("new={}", new)
    writeNameValue("doAdd={}", doAdd)

    pgs = []
    if old is not None:
        writeMsg("walking the old items ===")
        for item in old:
            writeNameValue("old item={}", item)
            if "ParityGroup" in item:
                pg = item["ParityGroup"]
                pgs.append(pg)

    old = pgs
    writeNameValue("old={}", old)

    if old is None:
        old = set()
    else:
        old = set(old)

    if new is None:
        new = set()
    else:
        new = set(new)

    toAdd = new - old
    toDel = old & new

    if doAdd:
        writeNameValue("toAdd={}", toAdd)
        if len(toAdd) == 0:
            writeMsg("nothing to add")
        else:
            for luId in toAdd:
                writeNameValue("addDriveGroupToResourceGroup={}", luId)
                storage.addDriveGroupToResourceGroup(rgId, luId)
    else:
        writeNameValue("toDel={}", toDel)
        if len(toDel) == 0:
            writeMsg("nothing toDel")
        else:
            for luId in toDel:
                writeNameValue("removeDriveGroupFromResourceGroup={}", luId)
                storage.removeDriveGroupFromResourceGroup(rgId, luId)


def handleHostGroupsInSamePort(hgPort, old, new, doAdd, storage, rgId):

    writeMsg("Enter handleHostGroupsInPort-------------------")
    writeNameValue("old={}", old)
    writeNameValue("new={}", new)
    writeNameValue("doAdd={}", doAdd)

    if old is None:
        old = set()
    else:
        old = set(old)

    if new is None:
        new = set()
    else:
        new = set(new)

    toAdd = new - old
    toDel = old & new

    if doAdd:
        writeNameValue("toAdd={}", toAdd)
        if len(toAdd) == 0:
            writeMsg("nothing to add")
        else:
            for hgName in toAdd:
                writeNameValue("addHostGroupToResourceGroup, hgName={}", hgName)
                writeNameValue("addHostGroupToResourceGroup, hgPort={}", hgPort)
                storage.addHostGroupToResourceGroup(rgId, hgName, hgPort)
    else:
        writeNameValue("toDel={}", toDel)
        if len(toDel) == 0:
            writeMsg("nothing toDel")
        else:
            for hgName in toDel:
                writeNameValue("removeHostGroupFromResourceGroup, rgId={}", rgId)
                writeNameValue("removeHostGroupFromResourceGroup, hgName={}", hgName)
                writeNameValue("removeHostGroupFromResourceGroup, hgPort={}", hgPort)
                storage.removeHostGroupFromResourceGroup(rgId, hgName, hgPort)


def handleHostGroups(old, new, doAdd, storage, rgId):

    writeMsg("Enter handleHostGroups-------------------")
    writeNameValue("old={}", old)
    writeNameValue("new={}", new)
    writeNameValue("doAdd={}", doAdd)

    hgNamesNew = []  # array of hgNamesArray
    hgPortsNew = []  # array of port
    hgPortsOld = []

    hgMapNew = {}  # key=port, value=hgNamesArray
    hgMapOld = {}

    if new is not None:
        writeMsg("walking the new items ===")
        for item in new:
            # from the playbook, each item is
            # hgNames[] and hgPort
            writeNameValue("new item={}", item)
            hgNames = item.get("host_group_names", None)
            hgPort = item.get("port", None)
            hgMapNew[hgPort] = hgNames
            hgPortsNew.append(hgPort)

    writeNameValue("hgMapNew={}", hgMapNew)
    writeNameValue("keys of the map={}", hgPortsNew)

    hgNamesArrInValue = []
    hgNames = []
    if old is not None:
        writeMsg("walking the old items ===")
        for item in old:
            writeNameValue("old item={}", item)
            hgName = None
            if "HgName" in item:
                hgName = item["HgName"]
            if "Port" in item:
                hgPort = item["Port"]
                if hgPort not in hgMapOld:
                    hgNamesArrInValue = []
                    hgMapOld[hgPort] = hgNamesArrInValue
                    hgPortsOld.append(hgPort)
                else:
                    hgNamesArrInValue = hgMapOld[hgPort]
                hgNamesArrInValue.append(hgName)

    writeNameValue("hgMapOld={}", hgMapOld)
    writeNameValue("hgNamesArrInValue={}", hgNamesArrInValue)
    writeNameValue("keys of the map={}", hgPortsOld)

    # do delta on ports
    # add/remove on port of hgs
    # then for each port do delta on the hgs
    # and add/remove hg

    # DEBUG
    # if True : return

    new = hgPortsNew
    old = hgPortsOld

    if old is None:
        old = set()
    else:
        old = set(old)

    if new is None:
        new = set()
    else:
        new = set(new)

    toAdd = new - old
    toDel = old & new

    if doAdd:
        writeNameValue("ports toAdd={}", toAdd)
        if len(toAdd) == 0:
            writeMsg("nothing to add, continue with case #2")
        else:

            # for add, there are two cases

            # case #1, a new port specified in the playbook
            # we need to add each hg
            for hgPort in toAdd:
                writeNameValue("add hgs in port={}", hgPort)
                hgNames = hgMapNew[hgPort]
                writeNameValue("add hgs in hgNames={}", hgNames)
                for hgName in hgNames:
                    writeNameValue("addHostGroupToResourceGroup, hgName={}", hgName)
                    writeNameValue("addHostGroupToResourceGroup, hgPort={}", hgPort)
                    storage.addHostGroupToResourceGroup(rgId, hgName, hgPort)
                # remove this port from the playbook port list for the phase 2 processing
                new.remove(hgPort)

        # case #2, for the ports which are already exist
        # we need to handle any delta in the hg list for each port
        # need to do that whether toAdd is empty or not
        for hgPort in new:
            handleHostGroupsInSamePort(
                hgPort, hgMapOld[hgPort], hgMapNew[hgPort], doAdd, storage, rgId
            )
    else:
        writeNameValue("ports toDel={}", toDel)
        if len(toDel) == 0:
            writeMsg("new/old ports are the same, now handle changes in the hg")
            writeNameValue("old={}", old)
            # del hg in the port
            for hgPort in old:
                handleHostGroupsInSamePort(
                    hgPort, hgMapOld[hgPort], hgMapNew[hgPort], doAdd, storage, rgId
                )
        else:
            for hgName in hgNamesArrInValue:
                writeNameValue("removeHostGroupFromResourceGroup, rgId={}", rgId)
                writeNameValue("removeHostGroupFromResourceGroup, hgName={}", hgName)
                writeNameValue("removeHostGroupFromResourceGroup, hgPort={}", hgPort)
                storage.removeHostGroupFromResourceGroup(rgId, hgName, hgPort)


def handleLogicalUnits(unDefinedLuns, old, new, doAdd, storage, rgId):

    writeMsg("Enter handleLogicalUnits-------------------")
    writeNameValue("old={}", old)
    writeNameValue("new={}", new)
    writeNameValue("doAdd={}", doAdd)

    luns = []
    parsedLuns = []
    if new:
        logger.writeDebug("luns count={0}".format(len(new)))
        for lun in new:
            logger.writeDebug(lun)
            if lun is not None and ":" in str(lun):
                logger.writeDebug(lun)
                lun = Utils.getlunFromHex(lun)
                logger.writeDebug("Hex converted lun={0}".format(lun))
                parsedLuns.append(lun)
            else:
                parsedLuns.append(lun)
    logger.writeDebug(parsedLuns)
    new = parsedLuns

    if unDefinedLuns is not None:
        # unDefinedLuns can be None or an empty list
        luns = unDefinedLuns

    if old is not None:
        writeMsg("walking the old items ===")
        for item in old:
            writeNameValue("old item={}", item)
            # if "LunNumber" in item:
            if "PhysicalLunNumber" in item:
                LunNumber = item["PhysicalLunNumber"]
                luns.append(LunNumber)

    old = luns
    writeNameValue("old={}", old)
    if old is None:
        old = set()
    else:
        old = set(old)

    if new is None:
        new = set()
    else:
        new = set(new)

    toAdd = new - old
    toDel = old & new

    if doAdd:
        writeNameValue("toAdd={}", toAdd)
        if len(toAdd) == 0:
            writeMsg("nothing to add")
        else:
            for luId in toAdd:
                writeNameValue("addLogicalUnitToResourceGroup={}", luId)
                storage.addLogicalUnitToResourceGroup(rgId, luId)
    else:
        writeNameValue("toDel={}", toDel)
        if len(toDel) == 0:
            writeMsg("nothing toDel")
        else:
            for luId in toDel:
                writeNameValue("removeLogicalUnitFromResourceGroup={}", luId)
                storage.removeLogicalUnitFromResourceGroup(rgId, luId)


def handlePorts(old, new, doAdd, storage, rgId):

    writeMsg("Enter handlePorts-------------------")
    writeNameValue("old={}", old)
    writeNameValue("new={}", new)
    writeNameValue("doAdd={}", doAdd)

    # DEBUG
    # if True : return

    ports = []
    if old is not None:
        writeMsg("walking the old items ===")
        for item in old:
            writeNameValue("old item={}", item)
            if "Name" in item:
                port = item["Name"]
                ports.append(port)

    old = ports
    writeNameValue("old={}", old)

    if old is None:
        old = set()
    else:
        old = set(old)

    if new is None:
        new = set()
    else:
        new = set(new)

    toAdd = new - old
    toDel = old & new

    if doAdd:
        writeNameValue("toAdd={}", toAdd)
        if len(toAdd) == 0:
            writeMsg("nothing to add")
        else:
            for luId in toAdd:
                writeNameValue("addPortToResourceGroup={}", luId)
                storage.addPortToResourceGroup(rgId, luId)
    else:
        writeNameValue("toDel={}", toDel)
        if len(toDel) == 0:
            writeMsg("nothing toDel")
        else:
            for luId in toDel:
                writeNameValue("removePortFromResourceGroup={}", luId)
                storage.removePortFromResourceGroup(rgId, luId)


def getResourceGroupInPlayBook(playbook_meta_resources, storage_serial, name):
    for rsrc in playbook_meta_resources:
        rg_storage_serial = rsrc["serial"]
        rg_name = rsrc["name"]
        if str(rg_storage_serial) == str(storage_serial) and name == rg_name:
            return rsrc

    return None


def doAddResourceGroup(storageSystem, serial, model, rgName):
    writeMsg("enter doAddResourceGroup")
    writeMsg("call CreateVirtualBoxResourceGroup")

    result = storageSystem.createVirtualBoxResourceGroup(serial, model, rgName)
    writeNameValue("result={}", result)


def doDeleteResourceGroup(storageSystem, storage_serial, rgId):
    writeMsg("enter doDeleteResourceGroup")
    writeMsg("call DeleteResourceGroup")
    storageSystem.deleteResourceGroup(rgId)


# walk thru the getVSM and see if any of the resource group
# is not in the playbook, if so remove it


def handleRemoveResourceGroup(
    vsms, playbook_meta_resources, playbook_virtual_storage_serial
):
    writeMsg("Enter handleRemoveResourceGroup-------------------")

    # see getResourceGroup
    changed = False
    # for vsms in vsms_array:
    for vsm in vsms:
        writeNameValue("vsm={}", vsm)
        ResourceGroups = vsm["ResourceGroups"]
        for rsrc in ResourceGroups:
            virtual_storage_serial = rsrc["VirtualDeviceId"]
            if str(virtual_storage_serial) != str(playbook_virtual_storage_serial):
                # there is only one virtual_storage_serial in the playbook
                continue

            storage_serial = rsrc["MetaResourceSerial"]
            name = rsrc["ResourceGroupName"]

            writeMsg("looking for existing RG in the playbook")
            writeNameValue("storage_serial={}", storage_serial)
            writeNameValue("name={}", name)
            rg = getResourceGroupInPlayBook(
                playbook_meta_resources, storage_serial, name
            )
            if rg is None:
                writeMsg(
                    "sub.state=absent, ResourceGroup exists but not in playbook, doDelete"
                )
                writeNameValue("call doDeleteResourceGroup={}", rsrc)
                # this is fixed by anisble sanity test , not tested
                rgId = rsrc["ResourceGroupId"]
                doDeleteResourceGroup(storage_serial, rgId)
                changed = True
            else:
                writeMsg("not found, no change")

    writeNameValue("handleRemoveResourceGroup.changed={}", changed)


# this is called for each resource group under playbook.meta_resources


def doUpdate(
    vsm, virtual_storage_serial, resource, resource_groups, doAdd, storageSystem, model
):
    writeMsg("enter doUpdate")
    writeNameValue("doUpdate:resource={}", resource)
    writeNameValue("doUpdate:doAdd={}", doAdd)

    # vsm is the response from get.one.VSM
    # resource is the each resource obj in the resource groups of the playbook
    #
    # resource_groups is the to be returned used to update the vsm, same obj use to create
    # (we may not need this, since we are to call the each api to add/remove)
    #
    # first get the delta between the vsm and this resource
    # looks like we need a map with the key so we can logic the resource in the vsm then compare
    #
    # or use MetaResourceSerial, VirtualDeviceId and ResourceGroupName in the vsm to match the
    # serial, virtual_storage_serial and name in the yml respectively
    storage_serial = resource["serial"]
    name = resource.get("name", None)
    resource.get("luns", None)

    rgs = getResourceGroup(vsm, storage_serial, virtual_storage_serial, name)
    if rgs is None:
        if doAdd:
            writeMsg(
                "no old resource, we need to add new resource group specified in the playbook"
            )
            doAddResourceGroup(storageSystem, virtual_storage_serial, model, name)
            vsm = getVSM(None, virtual_storage_serial)
            rgs = getResourceGroup(vsm, storage_serial, virtual_storage_serial, name)
            for rsrc in rgs:
                writeMsg("add resources to the newly added rg")
                writeNameValue("rsrc={}", rsrc)
                writeNameValue("resource={}", resource)
                rgId = rsrc["ResourceGroupId"]
                writeNameValue("rgId={}", rgId)

                # playbook vars are optional
                item = resource.get("parity_groups", None)
                handleDriveGroups(None, item, doAdd, storageSystem, rgId)
                item = resource.get("host_groups", None)
                handleHostGroups(None, item, doAdd, storageSystem, rgId)
                item = resource.get("luns", None)
                handleLogicalUnits(None, None, item, doAdd, storageSystem, rgId)
                item = resource.get("ports", None)
                handlePorts(None, item, doAdd, storageSystem, rgId)

    else:
        writeMsg("doUpdate:after getResourceGroup")
        for rsrc in rgs:
            writeMsg("doUpdate:found the targeted resource")
            writeNameValue("rsrc={}", rsrc)
            writeNameValue("resource={}", resource)
            rgId = rsrc["ResourceGroupId"]
            writeNameValue("rgId={}", rgId)
            item = resource.get("luns", None)
            writeNameValue("luns={}", item)
            handleLogicalUnits(
                getUnDefinedLuns(rsrc),
                rsrc["LogicalUnits"],
                item,
                doAdd,
                storageSystem,
                rgId,
            )

            item = resource.get("parity_groups", None)
            writeNameValue("parity_groups={}", item)
            handleDriveGroups(rsrc["ParityGroups"], item, doAdd, storageSystem, rgId)

            item = resource.get("host_groups", None)
            writeNameValue("host_groups={}", item)
            handleHostGroups(rsrc["HostGroups"], item, doAdd, storageSystem, rgId)

            item = resource.get("ports", None)
            writeNameValue("ports={}", item)
            handlePorts(rsrc["Ports"], item, doAdd, storageSystem, rgId)

    return vsm


def getUnDefinedLuns(rsrc):
    udluns = rsrc.get("UnDefinedLuns", None)
    if udluns is None:
        udluns = rsrc.get("UndefinedLuns", None)
    writeNameValue("getUnDefinedLuns returns udluns={}", udluns)
    return udluns


def doCreateRGsForVsmCreate(resource, resource_groups):
    writeMsg("enter doCreate")

    host_groups = []
    for hg in resource.get("host_groups", []):
        if "port" not in hg:
            raise Exception(
                "Host Group object must include the port!! (Error at index {0})".format(
                    len(host_groups)
                )
            )
        host_groups.append(
            {"hostgroupIds": hg.get("host_group_names", []), "port": hg["port"]}
        )

    luns = resource.get("luns", [])
    logger.writeDebug("luns={0}".format(luns))
    parsedLuns = []
    if luns:
        logger.writeDebug("luns count={0}".format(len(luns)))
        for lun in luns:
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
    new_resource = {
        "physicalSerialNumber": resource["serial"],
        "resourceGroupName": resource.get("name", resource["serial"]),
        "logicalUnits": luns,
        "ports": resource.get("ports", []),
        "parityGroups": resource.get("parity_groups", []),
        "hostGroups": host_groups,
    }
    resource_groups.append(new_resource)


def getTypeFromModel(model):
    if "VSP" == model:
        return model
    if "VSP_G1000" == model:
        return model
    if "VSP_G1500" == model:
        return model
    if "VSP_F1500" == model:
        return model
    if "VSP_G" in model:
        return "VSP_GX00"
    if "VSP_F" in model:
        return "VSP_FX00"
    if "VSP_N" in model:
        return "VSP_NX00"
    if "00H" in model:
        return "VSP_5X00H"
    if "VSP_5" in model:
        return "VSP_5X00"
    return "UNKNOWN"


def runPlaybook(module):
    logger.writeEnterModule(moduleName)
    virtual_storage_serial = module.params["virtual_storage_serial"]
    physical_storage_serial = module.params.get("physical_storage_serial")
    if physical_storage_serial == "":
        physical_storage_serial = None
    storageSystem = StorageSystem(virtual_storage_serial).vsmManager
    state = module.params["state"]
    result = None

    logger.writeParam("virtual_storage_serial={}", virtual_storage_serial)
    logger.writeParam("physical_storage_serial={}", physical_storage_serial)

    if state != "absent":
        data = json.loads(module.params["data"])

        subobjState = data.get("state", "present")
        if subobjState not in ("present", "absent"):
            raise Exception(
                "Subobject state is neither present nor absent. Please set it to a valid value."
            )

        model = data.get("model")
        if not model:
            raise Exception("No model supplied!")

        # in the case of update/remove
        # we will take action on each ms object
        # hence we will do a validateMS first here
        # we don't want to take some action then raise an exception
        # then it is not clear weather we have change anything or not
        meta_resources = data.get("meta_resources")
        validateMS(meta_resources)

        isCreate = True
        resource_groups = []

        if subobjState == "absent":
            # we are in update mode, vsm must exist
            isCreate = False

        # walk thru the meta_resources from the input
        # and see for each meta rsrc obj (ms obj)
        # if we need to do create, updateAdd or updateRemove
        # tasks include:
        # - create VSM
        # - add/remove resources in new/old ms objs
        # - resources include name?, hg.ports, hg.ids, luns, pgs, ports for a VSM resource
        # the serial is the key to the ms obj
        result = {}
        result["vsm"] = []
        vsm = []
        vsm = getVSM(None, virtual_storage_serial)

        if len(vsm) != 0:
            isCreate = False

        if isCreate is False and len(vsm) == 0:
            msg = "task.state=present and data.state=absent and VSM does not exist, no change."
            writeMsg(msg)
            result = {}
            result["comment"] = msg
            module.exit_json(changed=False, comment=msg)

        for resource in meta_resources:
            # do a get to see if this is a create or update
            physicalSerialNumber = resource["serial"]
            physicalStorageSystem = StorageSystem(physicalSerialNumber)
            if isCreate or vsm is None or len(vsm) == 0:
                writeMsg("doCreateRGs For vsm Create")
                # generate the resource_groups for createVirtualStorageSystem
                doCreateRGsForVsmCreate(resource, resource_groups)
                isCreate = True
            else:
                writeMsg("do update")
                vsm = doUpdate(
                    vsm,
                    virtual_storage_serial,
                    resource,
                    resource_groups,
                    subobjState != "absent",
                    physicalStorageSystem,
                    model,
                )
                isCreate = False

        if isCreate is False:
            # we might want to getVSM again or just return a comment
            # so user don't have to wait for the getVSM, they might not care
            result["vsm"].append(vsm)

        if subobjState == "absent":
            # walk thru the getVSM and see if any of the resource group
            # is not in the playbook, if so remove it
            handleRemoveResourceGroup(
                result["vsm"], meta_resources, virtual_storage_serial
            )

        if isCreate:
            writeMsg("call createVirtualStorageSystem")
            # DEBUG disable for debugging
            result = storageSystem.createVirtualStorageSystem(model, resource_groups)

            # it's incomplete without re-discovery, so no point to show it
            result = {}
        else:
            writeMsg("Update VSM operation is successful")
            result = {}
            result["comment"] = "Update VSM operation is successful"
    else:
        # state:absent doDelete
        writeMsg("call deleteVirtualStorageSystem")
        storageSystem.deleteVirtualStorageSystem(physical_storage_serial)
        module.exit_json(changed=True)

    # do we need this?
    # storageSystem.rediscoverVirtualStorages()

    data = {
        "storage_system": result,
        "changed": True,
    }
    registration_message = validate_ansible_product_registration()
    if registration_message:
        data["user_consent_required"] = registration_message
    logger.writeExitModule(moduleName)
    module.exit_json(**data)
