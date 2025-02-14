try:
    from ..common.vsp_constants import Endpoints
    from ..common.ansible_common import dicts_to_dataclass_list
    from ..model.vsp_storage_system_models import (
        VSPStorageSystemsInfoPfrestList,
        VSPStorageSystemsInfoPfrest,
        VSPStorageSystemInfoPfrest,
        VSPDetailedJournalPoolPfrestList,
        VSPDetailedJournalPoolPfrest,
        VSPBasicJournalPoolPfrestList,
        VSPBasicJournalPoolPfrest,
        VSPPortPfrestList,
        VSPPortPfrest,
        VSPPoolPfrestList,
        VSPPoolPfrest,
        VSPQuorumDiskPfrestList,
        VSPQuorumDiskPfrest,
        VSPFreeLunPfrestList,
        VSPFreeLunPfrest,
        VSPSyslogServerPfrest,
        VSPStorageCapacitiesPfrest,
    )
    from .gateway_manager import VSPConnectionManager, UAIGConnectionManager
    from ..common.ansible_common import log_entry_exit
    from ..common.hv_constants import CommonConstants, HEADER_NAME_CONSTANT
    from ..common.uaig_constants import Endpoints as UAIGEndpoints
    from ..model.vsp_storage_system_models import UCPStorageSystemsInfo
except ImportError:
    from common.vsp_constants import Endpoints
    from common.ansible_common import dicts_to_dataclass_list
    from model.vsp_storage_system_models import (
        VSPStorageSystemsInfoPfrestList,
        VSPStorageSystemsInfoPfrest,
        VSPStorageSystemInfoPfrest,
        VSPDetailedJournalPoolPfrestList,
        VSPDetailedJournalPoolPfrest,
        VSPBasicJournalPoolPfrestList,
        VSPBasicJournalPoolPfrest,
        VSPPortPfrestList,
        VSPPortPfrest,
        VSPPoolPfrestList,
        VSPPoolPfrest,
        VSPQuorumDiskPfrestList,
        VSPQuorumDiskPfrest,
        VSPFreeLunPfrestList,
        VSPFreeLunPfrest,
        VSPSyslogServerPfrest,
        VSPStorageCapacitiesPfrest,
    )
    from common.ansible_common import log_entry_exit
    from common.hv_constants import CommonConstants, HEADER_NAME_CONSTANT
    from common.uaig_constants import Endpoints as UAIGEndpoints
    from .gateway_manager import VSPConnectionManager, UAIGConnectionManager
    from model.vsp_storage_system_models import UCPStorageSystemsInfo


class VSPStorageSystemDirectGateway:

    def __init__(self, connection_info):
        self.connectionManager = VSPConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )

    @log_entry_exit
    def get_storage_systems(self):
        endPoint = Endpoints.GET_STORAGE_SYSTEMS
        storageSystemsDict = self.connectionManager.get(endPoint)
        return VSPStorageSystemsInfoPfrestList(
            dicts_to_dataclass_list(
                storageSystemsDict["data"], VSPStorageSystemsInfoPfrest
            )
        )

    @log_entry_exit
    def get_storage_system(self, instance):
        # logger = Log()
        path = instance + "?detailInfoType=version"
        endPoint = Endpoints.GET_STORAGE_SYSTEM.format(path)
        storageSystemInfo = self.connectionManager.get(endPoint)
        return VSPStorageSystemInfoPfrest(**storageSystemInfo)

    @log_entry_exit
    def get_current_storage_system_info(self):
        # logger = Log()
        endPoint = Endpoints.GET_STORAGE_INFO
        storageSystemInfo = self.connectionManager.get(endPoint)
        return VSPStorageSystemInfoPfrest(**storageSystemInfo)

    @log_entry_exit
    def get_journal_pools(self, journal_info_query):
        endPoint = Endpoints.GET_JOURNAL_POOLS
        if journal_info_query is not None:
            endPoint += "?journalInfo=" + journal_info_query
        journal_pools = self.connectionManager.get(endPoint)
        if journal_info_query == "detail":
            return VSPDetailedJournalPoolPfrestList(
                dicts_to_dataclass_list(
                    journal_pools["data"], VSPDetailedJournalPoolPfrest
                )
            )
        elif journal_info_query == "basic":
            return VSPBasicJournalPoolPfrestList(
                dicts_to_dataclass_list(
                    journal_pools["data"], VSPBasicJournalPoolPfrest
                )
            )

    @log_entry_exit
    def get_ports(self):
        endPoint = Endpoints.GET_PORTS + "?detailInfoType=portMode"
        ports = self.connectionManager.get(endPoint)
        return VSPPortPfrestList(dicts_to_dataclass_list(ports["data"], VSPPortPfrest))

    @log_entry_exit
    def get_pools(self):
        endPoint = Endpoints.GET_POOLS
        pools = self.connectionManager.get(endPoint)
        return VSPPoolPfrestList(dicts_to_dataclass_list(pools["data"], VSPPoolPfrest))

    @log_entry_exit
    def get_quorum_disks(self):
        endPoint = Endpoints.GET_QUORUM_DISKS
        quorum_disks = self.connectionManager.get(endPoint)
        return VSPQuorumDiskPfrestList(
            dicts_to_dataclass_list(quorum_disks["data"], VSPQuorumDiskPfrest)
        )

    @log_entry_exit
    def get_free_luns(self):
        # endPoint = Endpoints.GET_LDEVS.format("?count=16384&ldevOption=undefined")
        endPoint = Endpoints.GET_LDEVS.format(
            "?count=100&resourceGroupId=0&ldevOption=undefined"
        )
        free_luns = self.connectionManager.get(endPoint)
        return VSPFreeLunPfrestList(
            dicts_to_dataclass_list(free_luns["data"], VSPFreeLunPfrest)
        )

    @log_entry_exit
    def get_syslog_servers(self):
        endPoint = Endpoints.GET_SYSLOG_SERVERS
        syslog_servers = self.connectionManager.get(endPoint)
        return VSPSyslogServerPfrest(**syslog_servers)

    @log_entry_exit
    def get_storage_capacity(self):
        endPoint = Endpoints.GET_STORAGE_CAPACITY
        capacity = self.connectionManager.get(endPoint)
        return VSPStorageCapacitiesPfrest(**capacity)


class UAIGStorageSystemGateway:

    def __init__(self, connection_info):
        self.connectionManager = UAIGConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )

        #  Set the resource id
        self.serial_number = None
        self.resource_id = None

        #  Set the headers
        self.headers = {HEADER_NAME_CONSTANT.PARTNER_ID: CommonConstants.PARTNER_ID}
        if connection_info.subscriber_id is not None:
            self.headers[HEADER_NAME_CONSTANT.SUBSCRIBER_ID] = (
                connection_info.subscriber_id
            )
        self.UCP_SYSTEM = CommonConstants.UCP_SERIAL

    @log_entry_exit
    def get_ucpsystems(self):
        end_point = UAIGEndpoints.GET_UCPSYSTEMS
        ucpsystems = self.connectionManager.get(end_point)
        return ucpsystems["data"]

    @log_entry_exit
    def get_ucp_systems(self):
        end_point = UAIGEndpoints.GET_UCPSYSTEMS
        ucpsystems = self.connectionManager.get(end_point)
        return UCPStorageSystemsInfo().dump_to_object(ucpsystems)

    def check_storage_in_ucpsystem(self, serial) -> bool:

        ucpsystems = self.get_ucpsystems()
        for u in ucpsystems:
            # if u.get("name") == CommonConstants.UCP_NAME:
            for s in u.get("storageDevices"):
                if s.get("serialNumber") == str(serial):
                    if s.get("healthStatus") != CommonConstants.ONBOARDING:
                        return True

        return False
