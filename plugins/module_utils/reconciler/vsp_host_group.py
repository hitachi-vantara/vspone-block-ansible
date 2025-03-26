try:
    from ..provisioner.vsp_host_group_provisioner import VSPHostGroupProvisioner
    from ..common.ansible_common import (
        camel_to_snake_case,
        camel_array_to_snake_case,
        camel_dict_to_snake_case,
        generate_random_name_prefix_string,
        convert_hex_to_dec,
        get_default_value,
    )
    from ..common.hv_log import Log
    from ..model.vsp_host_group_models import VSPModifyHostGroupProvResponse
    from ..common.hv_constants import VSPHostGroupConstant, StateValue
    from ..message.vsp_host_group_msgs import VSPHostGroupMessage
except ImportError:
    from provisioner.vsp_host_group_provisioner import VSPHostGroupProvisioner
    from common.ansible_common import (
        camel_to_snake_case,
        camel_array_to_snake_case,
        camel_dict_to_snake_case,
        generate_random_name_prefix_string,
        convert_hex_to_dec,
        get_default_value,
    )
    from common.hv_log import Log
    from model.vsp_host_group_models import VSPModifyHostGroupProvResponse
    from common.hv_constants import VSPHostGroupConstant, StateValue
    from message.vsp_host_group_msgs import VSPHostGroupMessage


class VSPHostGroupReconciler:

    def __init__(self, connectionInfo, serial, hostGroupSpec=None):
        self.connectionInfo = connectionInfo
        self.serial = serial
        self.hostGroupSpec = hostGroupSpec
        self.provisioner = VSPHostGroupProvisioner(self.connectionInfo)
        self.provisioner.serial = serial

    def pre_check_port(self, port):
        logger = Log()
        logger.writeInfo("port = {}", port)
        if not port:
            raise Exception(VSPHostGroupMessage.PORT_NOT_IN_SYSTEM.value.format(port))
        if port:
            # before the subobjState change
            # make sure all the ports are defined in the storage
            # so we can add comments properly
            sports = self.provisioner.get_ports()
            found = [x for x in sports if x.portId == port]
            logger.writeDebug("210found={}", found)
            if found is None or len(found) == 0:
                raise Exception(
                    VSPHostGroupMessage.PORT_NOT_IN_SYSTEM.value.format(port)
                )

    def pre_check_wwns(self, subobjState, wwns, result):
        logger = Log()
        newWWN = set()
        if wwns == "":
            wwns = None
        if wwns is not None:
            logger.writeDebug("wwns={}", wwns)
            logger.writeDebug("wwns={}", wwns[0])
            logger.writeDebug("wwns={}", len(wwns))

            if len(wwns[0]) == 1:
                raise Exception(VSPHostGroupMessage.WWNS_INVALID.value)
        if (
            subobjState == VSPHostGroupConstant.STATE_PRESENT_LDEV
            or subobjState == VSPHostGroupConstant.STATE_UNPRESENT_LDEV
            or subobjState == VSPHostGroupConstant.STATE_SET_HOST_MODE
        ):
            # if hg with given port is not found, we have to ignore
            if wwns is not None:
                wwns = None
                result["comments"].append(VSPHostGroupMessage.IGNORE_WWNS.value)

        if wwns:
            # Convert WWNs to uppercase and ensure they are strings, removing duplicates
            newWWN = {str(wwn).upper() for wwn in wwns}

        return newWWN

    def pre_check_luns(self, subobjState, luns, result):
        logger = Log()
        if luns == "":
            luns = []
        if (
            subobjState == VSPHostGroupConstant.STATE_ADD_WWN
            or subobjState == VSPHostGroupConstant.STATE_REMOVE_WWN
            or subobjState == VSPHostGroupConstant.STATE_SET_HOST_MODE
        ):
            # if hg with given port is not found, we have to ignore
            if luns is not None:
                luns = None
                result["comments"].append(VSPHostGroupMessage.IGNORE_LUNS.value)

        parsedLuns = []
        if luns:
            for unused, lun in enumerate(luns):
                logger.writeDebug(lun)
                if lun is not None and ":" in str(lun):
                    logger.writeDebug(lun)
                    lun = convert_hex_to_dec(lun)
                    logger.writeDebug("Hex converted lun={0}".format(lun))
                    parsedLuns.append(lun)
                else:
                    parsedLuns.append(lun)
        logger.writeDebug(parsedLuns)
        luns = parsedLuns
        logger.writeDebug("LUN Parsing")
        newLun = list(map(int, luns))
        return newLun

    def pre_check_sub_state(self, subobjState):
        logger = Log()

        if subobjState == "":
            subobjState = StateValue.PRESENT
        if subobjState not in (
            StateValue.PRESENT,
            StateValue.ABSENT,
            VSPHostGroupConstant.STATE_PRESENT_LDEV,
            VSPHostGroupConstant.STATE_UNPRESENT_LDEV,
            VSPHostGroupConstant.STATE_SET_HOST_MODE,
            VSPHostGroupConstant.STATE_ADD_WWN,
            VSPHostGroupConstant.STATE_REMOVE_WWN,
        ):
            raise Exception(VSPHostGroupMessage.SPEC_STATE_INVALID.value)

        # support the new subobjState keywords
        logger.writeDebug("subobjState={}", subobjState)
        if (
            subobjState == VSPHostGroupConstant.STATE_ADD_WWN
            or subobjState == VSPHostGroupConstant.STATE_PRESENT_LDEV
            or subobjState == VSPHostGroupConstant.STATE_SET_HOST_MODE
        ):
            subobjState = StateValue.PRESENT

        if (
            subobjState == VSPHostGroupConstant.STATE_REMOVE_WWN
            or subobjState == VSPHostGroupConstant.STATE_UNPRESENT_LDEV
        ):
            subobjState = StateValue.ABSENT

        return subobjState

    def create_host_group(
        self, port, hgName, hostmodename, hostoptlist, newWWN, newLun
    ):
        logger = Log()

        logger.writeDebug("create_host_group={}", hgName)
        logger.writeDebug("port={}", port)
        logger.writeDebug("newWWN={}", newWWN)

        if hostmodename == "" or hostmodename is None:
            hostmodename = "LINUX/IRIX"
        if hostoptlist is None:
            hostoptlist = []
        logger.writeDebug("hostoptlist={}", hostoptlist)

        self.provisioner.create_host_group(
            port, hgName, newWWN, newLun, hostmodename, hostoptlist
        )

        hostGroup = self.provisioner.get_one_host_group(port, hgName).data
        return hostGroup

    def delete_host_group(self, spec, hg, result):
        self.provisioner.delete_host_group(hg, spec.delete_all_luns)
        result["changed"] = True
        result["hostGroup"] = None
        result["comment"] = VSPHostGroupMessage.DELETE_SUCCESSFULLY.value.format(
            hg.hostGroupName
        )

    def handle_set_host_mode(self, subobjState, hg, hostmodename, hostoptlist, result):
        logger = Log()
        if hostmodename is not None:
            hostmode = hostmodename
        else:
            hostmode = hg.hostMode

        # for hostmode, you can only update, no delete

        logger.writeDebug("update hostmode={}", hostmode)

        hgHMO = [opt.hostModeOptionNumber for opt in hg.hostModeOptions or []]
        if hostoptlist is not None:

            # hostoptlist is the user input

            oldlist = set(hgHMO)
            newlist = set(hostoptlist)
            addlist = newlist - oldlist
            oldlist & newlist

            if subobjState == StateValue.PRESENT:
                # # add = new - old
                hostopt = hgHMO + list(addlist)
            else:
                # del = old & new
                hostopt = list(set(hgHMO) - set(hostoptlist))
        else:
            hostopt = hgHMO
        logger.writeDebug("update hostopt={}", hostopt)

        if hostmode != hg.hostMode or set(hostopt) != set(hgHMO):
            logger.writeDebug("call set_host_mode()")
            self.provisioner.set_host_mode(hg, hostmode, hostopt)
            result["changed"] = True

    def handle_update_wwns(self, subobjState, hg, newWWN, result):
        logger = Log()
        wwns = (str(path.id) for path in hg.wwns or [])
        hgWWN = set(wwns)
        addWWN = newWWN - hgWWN
        delWWN = hgWWN.intersection(newWWN)

        logger.writeDebug("old hgWWN={}", hgWWN)
        logger.writeDebug("newWWN={}", newWWN)
        logger.writeDebug("addWWN={}", addWWN)
        logger.writeDebug("delWWN={}", delWWN)

        if addWWN and subobjState == StateValue.PRESENT:
            if len(addWWN) > 0:
                self.provisioner.add_wwns_to_host_group(hg, addWWN)
                result["changed"] = True
        if delWWN and subobjState == StateValue.ABSENT:
            if len(delWWN) > 0:
                self.provisioner.delete_wwns_from_host_group(hg, delWWN)
                result["changed"] = True

    def luns_to_add(self, new_lun: list, hg_lun: set):
        luns_to_add = []
        for lun in new_lun:
            if lun not in hg_lun:
                luns_to_add.append(lun)
        return luns_to_add

    def luns_to_delete(self, new_lun: list, hg_lun: set):
        luns_to_delete = []
        for lun in new_lun:
            if lun in hg_lun:
                luns_to_delete.append(lun)
        return luns_to_delete

    def handle_update_luns(self, subobjState, hg, newLun, result):
        logger = Log()
        hgLun = set(path.ldevId for path in hg.lunPaths or [])
        logger.writeDebug("newLun={0}", newLun)
        addLun = self.luns_to_add(newLun, hgLun)
        # delLun = list(set(hgLun) - set(newLun))
        delLun = self.luns_to_delete(newLun, hgLun)
        logger.writeDebug("hgLun={0}", hgLun)
        logger.writeDebug("541 addLun={0}", addLun)
        logger.writeDebug("542 delLun={0}", delLun)

        if subobjState == StateValue.PRESENT and addLun:
            if len(addLun) > 0:
                self.provisioner.add_luns_to_host_group(hg, addLun)
                result["changed"] = True

        if subobjState == StateValue.ABSENT:
            if delLun:
                logger.writeDebug("delete_luns_from_host_group delLun={0}", delLun)
                if len(delLun) > 0:
                    self.provisioner.delete_luns_from_host_group(hg, delLun)
                    result["changed"] = True
            else:
                result["comment"] = VSPHostGroupMessage.LUN_IS_NOT_IN_HG.value

    def handle_update_host_group(self, hg, data, result):
        logger = Log()
        # check for add/remove hostgroup for each given port
        subobjState = data["subobjState"]
        newWWN = data["newWWN"]
        newLun = data["newLun"]
        hostoptlist = data["hostoptlist"]
        hostmodename = data["hostmodename"]

        logger.writeDebug("subobjState={}", subobjState)

        if hg.port is None:
            return
        logger.writeDebug("update HgName={}", hg.hostGroupName)
        logger.writeDebug("update Port={}", hg.port)

        port = hg.port
        logger.writeDebug("processing port={}", port)

        logger.writeDebug("check hostmode and hostoptlist for update")
        if hostmodename is not None or hostoptlist is not None:
            self.handle_set_host_mode(
                subobjState, hg, hostmodename, hostoptlist, result
            )

        logger.writeDebug("check wwns for update")
        if newWWN:  # If newWWN is present,  update wwns
            self.handle_update_wwns(subobjState, hg, newWWN, result)

        logger.writeDebug("532 check luns for update")
        if newLun:  # If luns is present, present or overwrite luns
            self.handle_update_luns(subobjState, hg, newLun, result)

    def host_group_reconcile(self, state, spec):
        logger = Log()
        result = {"changed": False}
        data = spec
        subobjState = data.state
        port = data.port
        hgName = data.name
        hostmodename = data.host_mode
        hostoptlist = data.host_mode_options
        logger.writeDebug(hostoptlist)
        if hostmodename == "":
            hostmodename = None
        if hostoptlist == "":
            hostoptlist = None
        result["comments"] = []
        self.pre_check_port(port)
        newWWN = self.pre_check_wwns(subobjState, data.wwns, result)
        newLun = self.pre_check_luns(subobjState, data.ldevs, result)
        subobjState = self.pre_check_sub_state(subobjState)
        logger.writeParam("state={}", state)
        logger.writeParam("subobjState={}", subobjState)
        logger.writeParam("port={}", port)
        logger.writeParam("hgName={}", hgName)
        logger.writeParam("hostmodename={}", hostmodename)
        logger.writeParam("hostoptlist={}", hostoptlist)
        logger.writeParam("newWWN={}", newWWN)
        logger.writeParam("ldevs={}", newLun)
        # get all hgs
        # see if all the (hg,port)s are created
        hostGroup = None
        if hgName:
            hostGroup = self.provisioner.get_one_host_group(port, hgName).data
        logger.writeInfo("hostGroup = {}", hostGroup)
        result["changed"] = False
        if hgName is None and state != StateValue.ABSENT:
            hgName = generate_random_name_prefix_string()
        if not hostGroup:

            # No host groups found
            # Enter create mode
            # In this case, if state is absent, we do nothing.

            if state == StateValue.ABSENT:
                if hgName is None:
                    raise Exception(VSPHostGroupMessage.HG_NAME_EMPTY.value)
                logger.writeInfo("No host groups found, state is absent, no change")
                result["comment"] = VSPHostGroupMessage.HG_HAS_BEEN_DELETED.value

            if state != StateValue.ABSENT:
                logger.writeDebug("Create Mode =========== ")

                if not port:
                    raise Exception(VSPHostGroupMessage.PORTS_PARAMETER_INVALID.value)
                else:
                    hostGroup = self.create_host_group(
                        port, hgName, hostmodename, hostoptlist, newWWN, newLun
                    )
                    result["changed"] = True
        elif state == StateValue.ABSENT:

            # if we want to support the case:
            # the user given one lun, one port to create hg,
            # do sync up the hg in all other ports
            # then we need to call get_host_groups_by_scan_all_ports(self.provisioner, hgName, ?, hostGroups)

            # Delete mode.
            logger.writeDebug("Delete hgs from the list  =========== ")
            if hostGroup is None:
                logger.writeInfo("No host group found, state is absent, no change")
                result["comment"] = VSPHostGroupMessage.HG_HAS_BEEN_DELETED.value
            else:
                if len(hostGroup.lunPaths) > 0 and not spec.delete_all_luns:
                    # result["comment"] = VSPHostGroupMessage.LDEVS_PRESENT.value
                    raise Exception(VSPHostGroupMessage.LDEVS_PRESENT.value)
                else:
                    # Handle delete host group
                    self.delete_host_group(spec, hostGroup, result)

        else:

            # Modify mode. Certain operations only occur if state is overwrite.

            logger.writeDebug("Update Mode =========== ")
            data = {
                "subobjState": subobjState,
                "port": port,
                "hgName": hgName,
                "hostmodename": hostmodename,
                "hostoptlist": hostoptlist,
                "newWWN": newWWN,
                "newLun": newLun,
            }
            self.handle_update_host_group(hostGroup, data, result)

        logger.writeDebug("changed={}", result["changed"])
        logger.writeDebug("state={}", state)
        if result["changed"] and state != StateValue.ABSENT:
            result["hostGroup"] = self.provisioner.get_one_host_group(
                hostGroup.port, hostGroup.hostGroupName
            ).data

        if state != StateValue.ABSENT and "hostGroup" not in result:
            result["hostGroup"] = hostGroup
        return VSPModifyHostGroupProvResponse(**result)

    def get_host_groups(self, spec):
        return self.provisioner.get_host_groups(
            spec.ports, spec.name, spec.lun, spec.query
        )


class VSPHostGroupCommonPropertiesExtractor:
    def __init__(self, serial):
        self.common_properties = {
            "hostGroupName": str,
            "hostGroupId": int,
            "resourceGroupId": int,
            "port": str,
            "lunPaths": list,
            "hostMode": str,
            "wwns": list,
            "hostModeOptions": list,
        }

        self.modification_properties = {
            "changed": bool,
            "comment": str,
            "comments": list,
            "hostGroup": dict,
        }

    def extract(self, responses):
        new_items = []
        for response in responses:
            new_dict = {}
            for key, value_type in self.common_properties.items():
                # Get the corresponding key from the response or its mapped key
                response_key = None
                if key in response:
                    response_key = response.get(key)
                # Assign the value based on the response key and its data type
                cased_key = camel_to_snake_case(key)
                if response_key is not None:
                    new_dict[cased_key] = value_type(response_key)
                else:
                    # Handle missing keys by assigning default values
                    if (
                        key != "wwns" and key != "lunPaths"
                    ):  # Do not add default value for wwns and lunPaths because they are in query
                        default_value = get_default_value(value_type)
                        new_dict[cased_key] = default_value
            new_items.append(new_dict)
        new_items = camel_array_to_snake_case(new_items)
        return new_items

    def extract_dict(self, response):
        new_dict = {}
        for key, value_type in self.modification_properties.items():
            # Get the corresponding key from the response or its mapped key
            response_key = None
            if key in response:
                response_key = response.get(key)
            # Assign the value based on the response key and its data type
            cased_key = camel_to_snake_case(key)
            if response_key:
                new_dict[cased_key] = value_type(response_key)
        new_dict = camel_dict_to_snake_case(new_dict)
        return new_dict
