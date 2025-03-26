import concurrent.futures

try:
    from ..common.vsp_constants import Endpoints
    from .gateway_manager import VSPConnectionManager, UAIGConnectionManager
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..common.ansible_common import dicts_to_dataclass_list
    from ..model.vsp_host_group_models import (
        VSPHostGroupUAIG,
        VSPHostGroupsUAIG,
        VSPOneHostGroupInfo,
        VSPHostGroupInfo,
        VSPHostGroupsInfo,
        VSPLunResponse,
        VSPPortResponse,
        VSPWwnResponse,
    )
    from ..common.hv_constants import CommonConstants, VSPHostGroupConstant
    from ..message.vsp_host_group_msgs import VSPHostGroupMessage
    from ..common.uaig_constants import Endpoints as UAIGEndpoints
    from ..common.uaig_utils import UAIGResourceID
except ImportError:
    from common.vsp_constants import Endpoints
    from .gateway_manager import VSPConnectionManager, UAIGConnectionManager
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from common.ansible_common import dicts_to_dataclass_list
    from model.vsp_host_group_models import (
        VSPHostGroupUAIG,
        VSPHostGroupsUAIG,
        VSPOneHostGroupInfo,
        VSPHostGroupInfo,
        VSPHostGroupsInfo,
        VSPLunResponse,
        VSPPortResponse,
        VSPWwnResponse,
    )
    from common.hv_constants import CommonConstants, VSPHostGroupConstant
    from message.vsp_host_group_msgs import VSPHostGroupMessage
    from common.uaig_constants import Endpoints as UAIGEndpoints
    from common.uaig_utils import UAIGResourceID

g_raidHostModeOptions = {
    2: "VERITAS_DB_EDITION_ADV_CLUSTER",
    6: "TPRLO",
    7: "AUTO_LUN_RECOGNITION",
    12: "NO_DISPLAY_FOR_GHOST_LUN",
    13: "SIM_REPORT_AT_LINK_FAILURE",
    14: "HP_TRUCLUSTER_WITH_TRUECOPY",
    15: "HACMP",
    22: "VERITAS_CLUSTER_SERVER",
    23: "REC_COMMAND_SUPPORT",
    25: "SUPPORT_SPC_3_PERSISTENT_RESERVATION",
    33: "SET_REPORT_DEVICE_ID_ENABLE",
    39: "CHANGE_NEXUS_SPECIFIED_IN_SCSI_TARGET_RESET",
    40: "VVOL_EXPANSION",
    41: "PRIORITIZED_DEVICE_RECOGNITION",
    42: "PREVENT_OHUB_PCI_RETRY",
    43: "QUEUE_FULL_RESPONSE",
    48: "HAM_SVOL_READ",
    49: "BB_CREDIT_SETUP_1",
    50: "BB_CREDIT_SETUP_2",
    51: "ROUND_TRIP_SETUP",
    52: "HAM_AND_CLUSTER_SW_FOR_SCSI_2",
    54: "EXTENDED_COPY",
    57: "HAM_RESPONSE_CHANGE",
    60: "LUN0_CHANGE_GUARD",
    61: "EXPANDED_PERSISTENT_RESERVE_KEY",
    63: "VSTORAGE_APIS_ON_T10_STANDARDS",
    65: "ROUND_TRIP_EXTENDED_SETUP",
    67: "CHANGE_OF_ED_TOV_VALUE",
    68: "PAGE_RECLAMATION_LINUX",
    69: "ONLINE_LUSE_EXPANSION",
    71: "CHANGE_UNIT_ATTENTION_FOR_BLOCKED_POOL_VOLS",
    72: "AIX_GPFS",
    73: "WS2012",
    78: "NON_PREFERRED_PATH",
    80: "MULTITEXT_OFF",
    81: "NOP_IN_SUPPRESS",
    82: "DISCOVERY_CHAP",
    83: "REPORT_ISCSI_FULL_PORTAL_LIST",
    88: "PORT_CONSOLIDATION",
    91: "DISABLE_IO_WAIT_FOR_OPEN_STACK",
    95: "CHANGE_SCSI_LU_RESET_NEXUS_VSP_HUS_VM",
    96: "CHANGE_SCSI_LU_RESET_NEXUS",
    97: "PROPRIETARY_ANCHOR_COMMAND_SUPPORT",
    100: "HITACHI_HBA_EMULATION_CONNECTION_OPTION",
    102: "GAD_STANDARD_INQUIRY_EXPANSION_HCS",
    105: "TASK_SET_FULL_RESPONSE_FOR_IO_OVERLOAD",
    110: "ODX_SUPPORT_WIN2012",
    113: "ISCSI_CHAP_AUTH_LOG",
    114: "AUTO_ASYNC_RECLAMATION_ESXI_6_5",
    122: "TASK_SET_FULL_RESPONSE_AFTER_QOS_UPPER_LIMIT",
    124: "GUARANTEED_RESPONSE_DURING_CONTROLLER_FAILURE",
    131: "WCE_BIT_OFF_MODE",
}

gHostMode = {
    "LINUX": "LINUX/IRIX",
    "VMWARE": "VMWARE",
    "HP": "HP-UX",
    "OPEN_VMS": "OVMS",
    "TRU64": "TRU64",
    "SOLARIS": "SOLARIS",
    "NETWARE": "NETWARE",
    "WINDOWS": "WIN",
    "AIX": "AIX",
    "VMWARE_EXTENSION": "VMWARE_EX",
    "WINDOWS_EXTENSION": "WIN_EX",
}


class VSPHostGroupDirectGateway:
    def __init__(self, connection_info):
        self.rest_api = VSPConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )
        self.end_points = Endpoints
        self.serial = None

    @log_entry_exit
    def set_serial(self, serial):
        self.serial = serial

    @log_entry_exit
    def get_ports(self):
        Log()
        end_point = self.end_points.GET_PORTS
        resp = self.rest_api.read(end_point)
        return dicts_to_dataclass_list(resp["data"], VSPPortResponse)

    @log_entry_exit
    def get_one_port(self, port_id):
        Log()
        end_point = self.end_points.GET_ONE_PORT.format(port_id)
        resp = self.rest_api.read(end_point)
        return VSPPortResponse(**resp)

    @log_entry_exit
    def check_valid_port(self, port_id):
        is_valid = True
        port = self.get_one_port(port_id)
        port_type = port.portType
        if (
            port_type != VSPHostGroupConstant.PORT_TYPE_FIBRE
            and port_type != VSPHostGroupConstant.PORT_TYPE_FCOE
            and port_type != VSPHostGroupConstant.PORT_TYPE_HNASS
            and port_type != VSPHostGroupConstant.PORT_TYPE_HNASU
        ):
            is_valid = False
        return is_valid

    @log_entry_exit
    def get_wwns(self, port_id, hg_number):
        end_point = "{}?portId={}&hostGroupNumber={}".format(
            self.end_points.GET_WWNS, port_id, hg_number
        )
        end_point = self.end_points.GET_WWNS.format(
            "?portId={}&hostGroupNumber={}".format(port_id, hg_number)
        )
        resp = self.rest_api.read(end_point)
        return dicts_to_dataclass_list(resp["data"], VSPWwnResponse)

    @log_entry_exit
    def get_luns(self, port_id, hg_number):
        end_point = self.end_points.GET_LUNS.format(
            "?portId={}&hostGroupNumber={}".format(port_id, hg_number)
        )
        resp = self.rest_api.read(end_point)
        return dicts_to_dataclass_list(resp["data"], VSPLunResponse)

    @log_entry_exit
    def parse_host_group(self, hg, is_get_wwns, is_get_luns):
        tmpHg = {}
        port_id = hg["portId"]
        hg_name = hg["hostGroupName"]
        tmpHg["hostGroupName"] = hg_name
        hg_number = hg["hostGroupNumber"]
        tmpHg["hostGroupId"] = hg_number
        for hm in gHostMode:
            if gHostMode[hm] == hg["hostMode"]:
                tmpHg["hostMode"] = hm
                break
        tmpHg["resourceGroupId"] = hg.get("resourceGroupId", "")
        tmpHg["port"] = hg["portId"]

        if is_get_wwns:
            wwns = self.get_wwns(port_id, hg_number)
            tmpHg["wwns"] = []
            for wwn in wwns:
                tmpHg["wwns"].append(
                    {"id": wwn.hostWwn.upper(), "name": wwn.wwnNickname}
                )

        if is_get_luns:
            luns = self.get_luns(port_id, hg_number)
            tmpHg["lunPaths"] = []
            for lun in luns:
                tmpHg["lunPaths"].append({"lunId": lun.lun, "ldevId": lun.ldevId})

        host_mode_options = hg.get("hostModeOptions", None)
        tmpHg["hostModeOptions"] = []
        if host_mode_options:
            for option in host_mode_options:

                option_txt = ""
                if option in g_raidHostModeOptions:
                    option_txt = g_raidHostModeOptions[option]

                tmpHg["hostModeOptions"].append(
                    {
                        "hostModeOption": option_txt,
                        "hostModeOptionNumber": option,
                    }
                )

        return tmpHg

    @log_entry_exit
    def get_all_hgs(self):
        logger = Log()

        end_points = self.end_points.POST_HOST_GROUPS
        retry = 0
        resp = None
        max_retry = 20
        while retry < max_retry:
            try:
                resp = self.rest_api.read(end_points)
                if resp:
                    return VSPHostGroupsInfo(
                        dicts_to_dataclass_list(resp["data"], VSPHostGroupInfo)
                    )
            except Exception as e:
                if retry == max_retry - 1:
                    logger.writeError(f"Failed to get all host groups: {e}")
            finally:
                retry += 1
        return

    @log_entry_exit
    def get_host_groups(self, ports_input, name_input, is_get_wwns, is_get_luns):
        logger = Log()
        lstHg = []
        port_set = None
        if ports_input:
            port_set = set(ports_input)
        logger.writeInfo("port_set={0}".format(port_set))
        ports = self.get_ports()
        for port in ports:
            port_id = port.portId
            if port_set and port_id not in port_set:
                continue

            port_type = port.portType
            logger.writeInfo("port_type = {}", port_type)
            if (
                port_type != VSPHostGroupConstant.PORT_TYPE_FIBRE
                and port_type != VSPHostGroupConstant.PORT_TYPE_FCOE
                and port_type != VSPHostGroupConstant.PORT_TYPE_HNASS
                and port_type != VSPHostGroupConstant.PORT_TYPE_HNASU
            ):
                continue

            end_point = self.end_points.GET_HOST_GROUPS.format(
                "?portId={}&detailInfoType=resourceGroup".format(port_id)
            )
            resp = self.rest_api.read(end_point)
            for hg in resp["data"]:
                if name_input and hg["hostGroupName"] != name_input:
                    continue
                tmpHg = self.parse_host_group(hg, is_get_wwns, is_get_luns)
                lstHg.append(tmpHg)

        return VSPHostGroupsInfo(dicts_to_dataclass_list(lstHg, VSPHostGroupInfo))

    @log_entry_exit
    def get_host_groups_from_meta_resource(self, port):
        logger = Log()
        freeHgNumlst = []

        end_point = self.end_points.GET_HOST_GROUPS.format(
            "?portId={}&isUndefined=true&detailInfoType=resourceGroup".format(port)
        )
        resp = self.rest_api.read(end_point)

        for hg in resp["data"]:
            if hg["resourceGroupId"] == 0 and hg["isDefined"] is False:
                freeHgNumlst.append(hg["hostGroupNumber"])
        logger.writeDebug("free Hostgroup list = {}", freeHgNumlst)
        return freeHgNumlst

    @log_entry_exit
    def get_host_groups_of_a_port(self, port_id):
        Log()
        lstHg = []
        end_point = self.end_points.GET_HOST_GROUPS.format(
            "?portId={}&detailInfoType=resourceGroup".format(port_id)
        )
        resp = self.rest_api.read(end_point)
        for hg in resp["data"]:
            tmpHg = self.parse_host_group(hg, None, None)
            lstHg.append(tmpHg)

            return VSPHostGroupsInfo(dicts_to_dataclass_list(lstHg, VSPHostGroupInfo))
        return None

    @log_entry_exit
    def get_hg_by_id(self, object_id):
        Log()
        end_point = self.end_points.GET_HOST_GROUP_BY_ID.format(object_id)
        resp = self.rest_api.read(end_point)
        return resp
        # retHg = self.parse_host_group(resp, True, True)
        # return VSPOneHostGroupInfo(VSPHostGroupInfo(**retHg))

    @log_entry_exit
    def get_one_host_group(self, port_id, name):
        if not self.check_valid_port(port_id):
            return VSPOneHostGroupInfo(**{"data": None})

        retHg = {}
        end_point = self.end_points.GET_HOST_GROUPS.format(
            "?portId={}&detailInfoType=resourceGroup".format(port_id)
        )
        resp = self.rest_api.read(end_point)

        for hg in resp["data"]:
            if name == hg["hostGroupName"]:
                retHg = self.parse_host_group(hg, True, True)
                return VSPOneHostGroupInfo(VSPHostGroupInfo(**retHg))

        return VSPOneHostGroupInfo(**{"data": None})

    @log_entry_exit
    def create_host_group(self, port, name, wwns, luns, host_mode, host_mode_options):
        if not self.check_valid_port(port):
            raise Exception(VSPHostGroupMessage.PORT_TYPE_INVALID.value)

        logger = Log()
        hostGroupNumber = self.get_host_groups_from_meta_resource(port)
        logger.writeDebug("HostGroup List = {}", hostGroupNumber)
        if len(hostGroupNumber) == 0:
            raise Exception(VSPHostGroupMessage.HG_IN_META_NOT_AVAILABLE.value)

        end_point = self.end_points.POST_HOST_GROUPS
        data = {}
        data["hostGroupNumber"] = hostGroupNumber[0]
        data["portId"] = port
        data["hostGroupName"] = name
        if host_mode in gHostMode:
            data["hostMode"] = gHostMode[host_mode]
        if len(host_mode_options) > 0:
            data["hostModeOptions"] = host_mode_options
        logger.writeInfo(data)
        resp = self.rest_api.post(end_point, data)
        logger.writeInfo(resp)
        if resp is not None:
            number = 0
            split_arr = resp.split(",")
            if len(split_arr) > 1:
                port = split_arr[0]
                number = split_arr[1]
            end_point = self.end_points.GET_HOST_GROUP_ONE.format(port, number)
            read_resp = self.rest_api.read(end_point)
            logger.writeInfo(read_resp)
            ret_hg = self.parse_host_group(read_resp, False, False)
            hg_info = VSPHostGroupInfo(**ret_hg)
            if wwns:
                self.add_wwns_to_host_group(hg_info, wwns)
            if luns:
                self.add_luns_to_host_group(hg_info, luns)

    @log_entry_exit
    def add_wwns_to_host_group(self, hg, wwns):
        logger = Log()
        for wwn in wwns:
            end_point = self.end_points.POST_WWNS
            data = {}
            data["hostWwn"] = wwn
            data["portId"] = hg.port
            data["hostGroupNumber"] = hg.hostGroupId
            resp = self.rest_api.post(end_point, data)
            logger.writeInfo(resp)

    @log_entry_exit
    def add_luns_to_host_group(self, hg, luns):
        logger = Log()
        for lun in luns:
            end_point = self.end_points.POST_LUNS
            data = {}
            data["ldevId"] = lun
            data["portId"] = hg.port
            data["hostGroupNumber"] = hg.hostGroupId
            resp = self.rest_api.post(end_point, data)
            logger.writeInfo(resp)

    @log_entry_exit
    def delete_one_lun_from_host_group(self, host_group: VSPHostGroupInfo, lun_id):
        logger = Log()
        end_point = self.end_points.DELETE_LUNS.format(
            host_group.port, host_group.hostGroupId, lun_id
        )
        resp = self.rest_api.delete(end_point)
        logger.writeInfo(resp)

    @log_entry_exit
    def is_volume_not_associated_with_hgs(self, ldev_id):
        logger = Log()
        end_point = self.end_points.LDEVS_ONE.format(ldev_id)
        resp = self.rest_api.get(end_point)
        logger.writeInfo("resp = {}", resp)
        if "numOfPorts" not in resp or resp["numOfPorts"] == 0:
            return True
        return False

    @log_entry_exit
    def delete_one_volume(self, ldev_id):
        logger = Log()
        end_point = self.end_points.DELETE_LDEVS.format(ldev_id)
        resp = self.rest_api.delete(end_point)
        logger.writeInfo(resp)

    @log_entry_exit
    def unpresent_lun_from_hg_and_delete_lun(self, hg, lun):
        self.delete_one_lun_from_host_group(hg, lun.lunId)
        if self.is_volume_not_associated_with_hgs(lun.ldevId):
            self.delete_one_volume(lun.ldevId)

    @log_entry_exit
    def delete_host_group(self, hg, is_delete_all_luns):
        logger = Log()
        if is_delete_all_luns:
            with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
                future_tasks = [
                    executor.submit(
                        self.unpresent_lun_from_hg_and_delete_lun, hg, logical_unit
                    )
                    for logical_unit in hg.lunPaths
                ]
            # Re-raise exceptions if they occured in the threads
            for future in concurrent.futures.as_completed(future_tasks):
                future.result()

        end_point = self.end_points.DELETE_HOST_GROUPS.format(hg.port, hg.hostGroupId)
        resp = self.rest_api.delete(end_point)
        logger.writeInfo(resp)

    @log_entry_exit
    def delete_wwns_from_host_group(self, hg, wwns):
        logger = Log()
        for wwn in wwns:
            end_point = self.end_points.DELETE_WWNS.format(hg.port, hg.hostGroupId, wwn)
            resp = self.rest_api.delete(end_point)
            logger.writeInfo(resp)

    @log_entry_exit
    def delete_luns_from_host_group(self, hg, luns):
        logger = Log()
        for lun in luns:
            for lunPath in hg.lunPaths:
                if lun == lunPath.ldevId:
                    lunId = lunPath.lunId
                    end_point = self.end_points.DELETE_LUNS.format(
                        hg.port, hg.hostGroupId, lunId
                    )
                    resp = self.rest_api.delete(end_point)
                    logger.writeInfo(resp)
                    break

    @log_entry_exit
    def set_host_mode(self, hg, host_mode, host_mode_options):
        logger = Log()
        end_point = self.end_points.PATCH_HOST_GROUPS.format(hg.port, hg.hostGroupId)
        data = {}
        if host_mode and host_mode in gHostMode:
            data["hostMode"] = gHostMode[host_mode]
        else:
            data["hostMode"] = host_mode
        if host_mode_options is not None:
            if len(host_mode_options) > 0:
                data["hostModeOptions"] = host_mode_options
            else:
                data["hostModeOptions"] = [-1]
        resp = self.rest_api.patch(end_point, data)
        logger.writeInfo(resp)


class VSPHostGroupUAIGateway:
    def __init__(self, connection_info):
        self.logger = Log()
        self.connection_manager = UAIGConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )
        self.connection_info = connection_info
        self.serial = None
        self.resource_id = None

    @log_entry_exit
    def populate_header(self):
        headers = {}
        headers["partnerId"] = CommonConstants.PARTNER_ID
        if self.connection_info.subscriber_id is not None:
            headers["subscriberId"] = self.connection_info.subscriber_id
        return headers

    @log_entry_exit
    def set_serial(self, serial):
        self.serial = serial
        self.set_resource_id()

    @log_entry_exit
    def set_resource_id(self, serial=None):
        logger = Log()
        serial = serial if serial else self.serial
        self.resource_id = UAIGResourceID().storage_resourceId(self.serial)
        logger.writeDebug(
            "GW:set_resource_id:serial = {}  resourceId = {}",
            self.serial,
            self.resource_id,
        )

    @log_entry_exit
    def get_host_groups(self, ports_input, name_input, is_get_wwns, is_get_luns):
        self.set_resource_id()
        end_point = UAIGEndpoints.UAIG_GET_HOST_GROUPS.format(self.resource_id)
        headers = self.populate_header()
        host_grps = self.connection_manager.get(end_point, headers)
        hg_info = VSPHostGroupsUAIG().dump_to_object(host_grps)
        return hg_info

    @log_entry_exit
    def get_host_groups_for_resource_id(self, resource_id):
        end_point = UAIGEndpoints.UAIG_GET_HOST_GROUPS.format(resource_id)
        headers = self.populate_header()
        host_grps = self.connection_manager.get(end_point, headers)
        hg_info = VSPHostGroupsUAIG().dump_to_object(host_grps)
        return hg_info

    @log_entry_exit
    def get_host_group_by_id(self, hg_id):
        end_point = UAIGEndpoints.GET_HOST_GROUP_BY_ID.format(self.resource_id, hg_id)
        headers = None
        # headers = self.populate_header()
        host_grp = self.connection_manager.get(end_point, headers)
        return VSPHostGroupUAIG(**host_grp["data"])

    @log_entry_exit
    def create_default_host_group(self, payload):
        end_point = UAIGEndpoints.UAIG_CREATE_HOST_GROUP.format(self.resource_id)
        headers = self.populate_header()
        host_grp_id = self.connection_manager.post(end_point, payload, headers)
        return host_grp_id
