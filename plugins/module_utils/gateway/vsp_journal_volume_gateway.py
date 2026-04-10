try:
    from ..common.vsp_constants import Endpoints, VSPJournalVolumeReq
    from .gateway_manager import VSPConnectionManager
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
except ImportError:
    from common.vsp_constants import Endpoints, VSPJournalVolumeReq
    from common.hv_log import Log
    from .gateway_manager import VSPConnectionManager
    from common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from model.vsp_storage_system_models import (
        VSPBasicJournalPoolPfrestList,
        VSPDetailedJournalPoolPfrestList,
        VSPDetailedJournalPoolPfrest,
        VSPBasicJournalPoolPfrest,
    )
    from model.vsp_volume_models import VSPVolumesInfo
    from model.vsp_journal_models import VSPJournalPools, VSPJournalPool


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
        single_pool = None
        try:
            end_point = Endpoints.GET_JOURNAL_POOL.format(pool_id)
            single_pool = self.connectionManager.get(end_point)
        except Exception as e:
            self.logger.writeError(f"Error retrieving journal pool by ID: {e}")
            return None

        end_point = f"{Endpoints.GET_JOURNAL_POOLS}?journalInfo=detail"
        pool_dict = self.connectionManager.get(end_point)

        # Use a generator to avoid unnecessary looping
        pool = next(
            (p for p in pool_dict.get("data", []) if p.get("journalId") == pool_id),
            None,
        )
        if not pool:
            return None

        pool.update(
            single_pool
        )  # Update the pool dictionary with the single pool details
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
    def get_all_journal_basic_info(self):
        endPoint = Endpoints.GET_JOURNAL_POOLS + "?journalInfo=basic"
        journal_pools_basic = self.connectionManager.get(endPoint)
        return VSPJournalPools().dump_to_object(journal_pools_basic)

    @log_entry_exit
    def get_all_journal_info(self):
        from concurrent.futures import ThreadPoolExecutor, as_completed

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

        try:
            with ThreadPoolExecutor(
                max_workers=min(8, len(jp_data.data) or 1)
            ) as executor:
                future_to_jp = {
                    executor.submit(self.get_journal_ldevs_info, jp.journalPoolId): jp
                    for jp in jp_data.data
                }
                for future in as_completed(future_to_jp):
                    jp = future_to_jp[future]
                    logger.writeDebug(f"GW:journal_volume: jp =  {jp}")
                    ldevs = future.result()
                    if ldevs:
                        jp.logicalUnitIds = [ldev.ldevId for ldev in ldevs.data]
        except KeyboardInterrupt:
            logger.writeError(
                "GW:journal_volume: get_all_journal_info interrupted by user"
            )
            executor.shutdown(wait=False, cancel_futures=True)
            raise

        return jp_data

    @log_entry_exit
    def create_journal_volume(self, spec):
        endPoint = Endpoints.POST_JOURNAL_POOLS
        payload = {}
        payload[VSPJournalVolumeReq.journalid] = spec.journal_id
        if spec.start_ldev_id and spec.end_ldev_id:
            payload[VSPJournalVolumeReq.startLdevId] = spec.start_ldev_id
            payload[VSPJournalVolumeReq.endLdevId] = spec.end_ldev_id
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
        if spec.data_overflow_watch_in_seconds:
            payload[VSPJournalVolumeReq.dataOverflowWatchInSeconds] = (
                spec.data_overflow_watch_in_seconds
            )
        if spec.is_cache_mode_enabled is not None:
            payload[VSPJournalVolumeReq.isCacheModeEnabled] = spec.is_cache_mode_enabled
        if (
            spec.copy_pace is not None
            or spec.path_blockade_watch_in_minutes is not None
        ):
            if spec.mirror_unit_number is None:
                # raise ValueError(
                #     "Mirror unit number is required when copy pace or path blockade watch is specified."
                # )
                spec.mirror_unit_number = (
                    1  # default mirror unit number to 1 if not provided
                )
        payload[VSPJournalVolumeReq.mirrorUnit] = {
            VSPJournalVolumeReq.muNumber: spec.mirror_unit_number,
            VSPJournalVolumeReq.copyPace: self.convert_copy_pace_to_api_value(
                spec.copy_pace
            ),
            VSPJournalVolumeReq.pathBlockadeWatchInMinutes: (
                spec.path_blockade_watch_in_minutes
                if spec.path_blockade_watch_in_minutes
                else 0
            ),
        }
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

    def convert_copy_pace_to_api_value(self, copy_pace):
        if copy_pace is None:
            return "L"
        if copy_pace < 3:
            return "L"
        elif 3 <= copy_pace <= 7:
            return "M"
        else:
            return "H"

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
