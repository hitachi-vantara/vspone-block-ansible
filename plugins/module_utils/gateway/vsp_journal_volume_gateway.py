from typing import Any, Dict, List


try:
    from ..common.vsp_constants import Endpoints, VSPJournalVolumeReq
    from ..common.uaig_constants import (
        Endpoints as UAIGEndpoints,
        VSPJournalVolumeUAIGReq,
    )
    from .gateway_manager import VSPConnectionManager, UAIGConnectionManager
    from ..common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from ..common.hv_log import Log
    from ..model.vsp_storage_system_models import (
        VSPBasicJournalPoolPfrestList,
        VSPDetailedJournalPoolPfrestList,
        VSPDetailedJournalPoolPfrest,
        VSPBasicJournalPoolPfrest,
    )
    from ..model.vsp_volume_models import VSPVolumesInfo
    from ..model.vsp_journal_models import VSPJournalPools, VSPJournalPool
    from ..common.hv_constants import CommonConstants, HEADER_NAME_CONSTANT
    from ..common.uaig_utils import UAIGResourceID

except ImportError:
    from common.vsp_constants import Endpoints, VSPJournalVolumeReq
    from common.hv_log import Log
    from common.uaig_constants import (
        Endpoints as UAIGEndpoints,
        VSPJournalVolumeUAIGReq,
    )
    from .gateway_manager import VSPConnectionManager, UAIGConnectionManager
    from common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from model.vsp_storage_system_models import (
        VSPBasicJournalPoolPfrestList,
        VSPDetailedJournalPoolPfrestList,
        VSPDetailedJournalPoolPfrest,
        VSPBasicJournalPoolPfrest,
    )
    from model.vsp_volume_models import VSPVolumesInfo

    from common.hv_constants import CommonConstants, HEADER_NAME_CONSTANT
    from model.vsp_journal_models import VSPJournalPools, VSPJournalPool
    from common.uaig_utils import UAIGResourceID


logger = Log()


class VSPSJournalVolumeDirectGateway:

    def __init__(self, connection_info):
        self.logger = Log()
        self.connectionManager = VSPConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )

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
    def get_journal_pool_by_id(self, pool_id):
        """
        Retrieves a journal pool by its ID.

        Args:
            pool_id (str): The ID of the journal pool to retrieve.

        Returns:
            VSPJournalPool: The journal pool data with logical unit IDs populated, or None if not found.
        """
        end_point = f"{Endpoints.GET_JOURNAL_POOLS}?journalInfo=detail"
        pool_dict = self.connectionManager.get(end_point)

        # Use a generator to avoid unnecessary looping
        pool = next(
            (p for p in pool_dict.get("data", []) if p.get("journalId") == pool_id),
            None,
        )
        if not pool:
            return None
        end_point = Endpoints.GET_JOURNAL_POOL.format(pool_id)
        single_pool = self.connectionManager.get(end_point)
        pool.update(single_pool)
        # Initialize and populate the journal pool object
        data = VSPJournalPool(**pool)
        ldevs = self.get_journal_ldevs_info(pool_id)
        data.logicalUnitIds = [ldev.ldevId for ldev in ldevs.data]
        return data

    @log_entry_exit
    def get_journal_ldevs_info(self, pool_id):
        endPoint = Endpoints.LDEVS_JOURNAL_VOLUME.format(pool_id)

        ldevs = self.connectionManager.get(endPoint)
        return VSPVolumesInfo().dump_to_object(ldevs)

    @log_entry_exit
    def get_all_journal_info(self):
        endPoint = Endpoints.GET_JOURNAL_POOLS + "?journalInfo=detail"
        journal_pools_details = self.connectionManager.get(endPoint)
        endPoint = Endpoints.GET_JOURNAL_POOLS + "?journalInfo=basic"
        journal_pools_basic = self.connectionManager.get(endPoint)
        unused = [
            pool.update(basic)
            for pool in journal_pools_details["data"]
            for basic in journal_pools_basic["data"]
            if pool["journalId"] == basic["journalId"]
        ]
        logger.writeDebug(
            f"GW:journal_volume: journal_pools_details =  {journal_pools_details}"
        )
        jp_data = VSPJournalPools().dump_to_object(journal_pools_details)

        for jp in jp_data.data:
            logger.writeDebug(f"GW:journal_volume: jp =  {jp}")
            ldevs = self.get_journal_ldevs_info(jp.journalPoolId)
            if ldevs:
                jp.logicalUnitIds = [ldev.ldevId for ldev in ldevs.data]
        return jp_data

    @log_entry_exit
    def create_journal_volume(self, spec):
        endPoint = Endpoints.POST_JOURNAL_POOLS
        payload = {}
        payload[VSPJournalVolumeReq.journalid] = spec.journal_id
        if spec.startLdevId and spec.endLdevId:
            payload[VSPJournalVolumeReq.startLdevId] = spec.startLdevId
            payload[VSPJournalVolumeReq.endLdevId] = spec.endLdevId
        else:
            payload[VSPJournalVolumeReq.LDEV_IDS] = spec.ldev_ids

        url = self.connectionManager.post(endPoint, payload)
        return url.split("/")[-1]

    @log_entry_exit
    def update_journal_volume(self, pool_id, spec):
        endPoint = Endpoints.GET_JOURNAL_POOL.format(pool_id)
        payload = {}
        url = None
        self.logger.writeDebug(f"GW:journal_volume: spec =  {spec}")
        if spec.data_overflow_watchIn_seconds:
            payload[VSPJournalVolumeReq.dataOverflowWatchInSeconds] = (
                spec.data_overflow_watchIn_seconds
            )
        if spec.is_cache_mode_enabled is not None:
            payload[VSPJournalVolumeReq.isCacheModeEnabled] = spec.is_cache_mode_enabled
        if payload:
            url = self.connectionManager.patch(endPoint, payload)
        if spec.mp_blade_id is not None:
            endPointMPBlade = Endpoints.JOURNAL_POOL_MP_BLADE.format(pool_id)
            payloadMPBlade = {
                VSPJournalVolumeReq.PARAMETERS: {
                    VSPJournalVolumeReq.mpBladeId: spec.mp_blade_id
                }
            }
            url = self.connectionManager.post(endPointMPBlade, payloadMPBlade)
        return url.split("/")[-1]

    @log_entry_exit
    def expand_journal_volume(self, pool_id, spec):
        endPoint = Endpoints.JOURNAL_POOL_EXPAND.format(pool_id)
        payload = {
            VSPJournalVolumeReq.PARAMETERS: {
                VSPJournalVolumeReq.LDEV_IDS: spec.ldev_ids
            }
        }
        url = self.connectionManager.post(endPoint, payload)
        return url.split("/")[-1]

    @log_entry_exit
    def delete_journal_volume(self, pool_id):
        endPoint = Endpoints.GET_JOURNAL_POOL.format(pool_id)
        return self.connectionManager.delete(endPoint)

    @log_entry_exit
    def shrink_journal_volume(self, pool_id, spec):
        endPoint = Endpoints.JOURNAL_POOL_SHRINK.format(pool_id)
        payload = {
            VSPJournalVolumeReq.PARAMETERS: {
                VSPJournalVolumeReq.LDEV_IDS: spec.ldev_ids
            }
        }
        url = self.connectionManager.post(endPoint, payload)
        return url.split("/")[-1]

    def get_all_porcelain_journal_volumes(self):
        pass

    def set_mp_blade_journal_pool(self):
        pass

    def check_storage_in_ucpsystem(self):
        pass


class VSPJournalVolumeUAIGateway:

    def __init__(self, connection_info):
        self.connectionManager = UAIGConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )

        #  Set the resource id
        self.serial_number = None
        self.resource_id = ""

        #  Set the headers
        self.headers = {HEADER_NAME_CONSTANT.PARTNER_ID: CommonConstants.PARTNER_ID}
        if connection_info.subscriber_id is not None:
            self.headers[HEADER_NAME_CONSTANT.SUBSCRIBER_ID] = (
                connection_info.subscriber_id
            )
        self.UCP_SYSTEM = CommonConstants.UCP_SERIAL
        self.generate_id = UAIGResourceID()

    @log_entry_exit
    def set_storage_serial_number(self, serial: str):
        self.storage_serial_number = serial

    @log_entry_exit
    def create_journal_volume(self, spec):

        endPoint = UAIGEndpoints.POST_JOURNAL_VOLUMES.format(self.resource_id)
        payload = {
            VSPJournalVolumeUAIGReq.journalPoolId: spec.journal_id,
            VSPJournalVolumeUAIGReq.logicalUnitIds: spec.ldev_ids,
            VSPJournalVolumeUAIGReq.ucpSystem: self.UCP_SYSTEM,
            VSPJournalVolumeUAIGReq.serialNumber: self.serial_number,
        }
        if spec.data_overflow_watchIn_seconds:
            payload[VSPJournalVolumeUAIGReq.dataOverflowWatchSeconds] = (
                spec.data_overflow_watchIn_seconds
            )
        if spec.is_cache_mode_enabled is not None:
            payload[VSPJournalVolumeUAIGReq.isCacheModeEnabled] = (
                spec.is_cache_mode_enabled
            )

        return self.connectionManager.post(endPoint, payload, self.headers)

    @log_entry_exit
    def expand_journal_volume(self, pool_id, spec):
        res_pool_id = self.generate_id.journal_pool_id(self.serial_number, pool_id)
        endPoint = UAIGEndpoints.JOURNAL_VOLUMES_EXPAND.format(
            self.resource_id, res_pool_id
        )
        payload = {
            VSPJournalVolumeUAIGReq.logicalUnitIds: spec.ldev_ids,
            VSPJournalVolumeUAIGReq.ucpSystem: self.UCP_SYSTEM,
            VSPJournalVolumeUAIGReq.serialNumber: self.serial_number,
            VSPJournalVolumeUAIGReq.journalPoolId: pool_id,
        }
        return self.connectionManager.patch(endPoint, payload, self.headers)

    @log_entry_exit
    def shrink_journal_volume(self, pool_id, spec):
        res_pool_id = self.generate_id.journal_pool_id(self.serial_number, pool_id)

        endPoint = UAIGEndpoints.JOURNAL_VOLUMES_SHRINK.format(
            self.resource_id, res_pool_id
        )
        payload = {
            VSPJournalVolumeUAIGReq.logicalUnitIds: spec.ldev_ids,
            VSPJournalVolumeUAIGReq.ucpSystem: self.UCP_SYSTEM,
            VSPJournalVolumeUAIGReq.serialNumber: self.serial_number,
            VSPJournalVolumeUAIGReq.journalPoolId: pool_id,
        }
        return self.connectionManager.patch(endPoint, payload, self.headers)

    @log_entry_exit
    def set_mp_blade_journal_pool(self, pool_id, spec):
        res_pool_id = self.generate_id.journal_pool_id(self.serial_number, pool_id)

        endPoint = UAIGEndpoints.JOURNAL_VOLUMES_MP_BLADE.format(
            self.resource_id, res_pool_id
        )
        payload = {
            VSPJournalVolumeUAIGReq.mpBladeId: spec.mp_blade_id,
            VSPJournalVolumeUAIGReq.ucpSystem: self.UCP_SYSTEM,
            VSPJournalVolumeUAIGReq.serialNumber: self.serial_number,
            VSPJournalVolumeUAIGReq.journalPoolId: pool_id,
        }

        return self.connectionManager.patch(endPoint, payload, self.headers)

    @log_entry_exit
    def update_journal_volume(self, pool_id, spec):
        res_pool_id = self.generate_id.journal_pool_id(self.serial_number, pool_id)

        endPoint = UAIGEndpoints.UPDATE_JOURNAL_VOLUMES.format(
            self.resource_id, res_pool_id
        )
        response = None
        payload = {
            VSPJournalVolumeUAIGReq.ucpSystem: self.UCP_SYSTEM,
            VSPJournalVolumeUAIGReq.serialNumber: self.serial_number,
            VSPJournalVolumeUAIGReq.journalPoolId: pool_id,
        }
        if spec.data_overflow_watchIn_seconds:
            payload[VSPJournalVolumeUAIGReq.dataOverflowWatchSeconds] = (
                spec.data_overflow_watchIn_seconds
            )
        if spec.is_cache_mode_enabled is not None:
            payload[VSPJournalVolumeUAIGReq.isCacheModeEnabled] = (
                spec.is_cache_mode_enabled
            )

        if len(payload) > 3:
            response = self.connectionManager.put(endPoint, payload, self.headers)

        if spec.mp_blade_id is not None:
            response = self.set_mp_blade_journal_pool(pool_id, spec)
        return response

    @log_entry_exit
    def delete_journal_volume(self, pool_id):
        res_pool_id = self.generate_id.journal_pool_id(self.serial_number, pool_id)

        endPoint = UAIGEndpoints.DELETE_JP.format(self.resource_id, res_pool_id)
        data = {
            VSPJournalVolumeUAIGReq.ucpSystem: self.UCP_SYSTEM,
            VSPJournalVolumeUAIGReq.journalPoolId: pool_id,
        }
        return self.connectionManager.delete(
            endPoint, data=data, headers_input=self.headers
        )

    @log_entry_exit
    def get_all_journal_info(self):
        #  Get the journal volumes
        endPoint = UAIGEndpoints.GET_JOURNAL_VOLUMES.format(
            self.resource_id, self.UCP_SYSTEM
        )
        journalVolumesDict = self.connectionManager.get(endPoint)
        return VSPJournalPools().dump_to_object(journalVolumesDict)

    @log_entry_exit
    def get_all_porcelain_journal_volumes(self):
        #  Get the journal volumes
        endPoint = UAIGEndpoints.GET_JOURNAL_VOLUMES.format(
            self.resource_id, CommonConstants.UCP_SERIAL
        )
        journalVolumesDict = self.connectionManager.get(endPoint)
        return journalVolumesDict

    @log_entry_exit
    def get_ucpsystems(self) -> List[Dict[str, Any]]:
        end_point = UAIGEndpoints.GET_UCPSYSTEMS
        ucpsystems = self.connectionManager.get(end_point)
        return ucpsystems["data"]

    @log_entry_exit
    def check_storage_in_ucpsystem(self, serial) -> bool:

        ucpsystems = self.get_ucpsystems()

        for u in ucpsystems:
            # if u.get("name") == CommonConstants.UCP_NAME:
            for s in u.get("storageDevices"):
                if s.get("serialNumber") == str(serial):
                    if s.get("healthStatus") != CommonConstants.ONBOARDING:
                        for name in s.get("ucpSystems"):
                            if name != CommonConstants.UCP_NAME:
                                self.UCP_SYSTEM = name
                                self.serial_number = serial
                        return True

        return False

    def get_journal_pools(self):
        pass

    def get_journal_pool_by_id(self):
        pass
