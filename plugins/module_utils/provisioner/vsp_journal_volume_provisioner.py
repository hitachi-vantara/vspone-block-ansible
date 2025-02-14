import re
import time

try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..common.hv_constants import ConnectionTypes
    from ..common.uaig_utils import UAIGResourceID
    from ..message.vsp_journal_volume_msgs import VSPSJournalVolumeValidateMsg
    from ..gateway.vsp_journal_volume_gateway import (
        VSPSJournalVolumeDirectGateway,
        VSPJournalVolumeUAIGateway,
    )
    from ..common.vsp_constants import StoragePoolLimits
    from ..message.common_msgs import CommonMessage


except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes
    from common.ansible_common import log_entry_exit
    from common.hv_log import Log
    from common.hv_constants import ConnectionTypes
    from common.uaig_utils import UAIGResourceID
    from message.vsp_journal_volume_msgs import VSPSJournalVolumeValidateMsg
    from gateway.vsp_journal_volume_gateway import (
        VSPSJournalVolumeDirectGateway,
        VSPJournalVolumeUAIGateway,
    )
    from common.vsp_constants import StoragePoolLimits
    from message.common_msgs import CommonMessage


class VSPJournalVolumeProvisioner:

    def __init__(self, connection_info, serial=None):
        self.logger = Log()
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_JOURNAL_VOLUME
        )
        self.connection_info = connection_info
        self.connection_type = connection_info.connection_type
        self.resource_id = None
        self.serial = None
        self.pg_info = None

        if self.connection_info.connection_type == ConnectionTypes.DIRECT:
            self.gateway = VSPSJournalVolumeDirectGateway(self.connection_info)
        if connection_info.connection_type == ConnectionTypes.GATEWAY:
            self.gateway = VSPJournalVolumeUAIGateway(connection_info)
            self.gateway.set_storage_serial_number(serial)

    # Helper function to convert camelCase to snake_case
    def camel_to_snake(self, name: str) -> str:
        # Insert underscores before uppercase letters and convert to lowercase
        return re.sub(r"([a-z])([A-Z])", r"\1_\2", name).lower()

    # @log_entry_exit
    # def get_journal_pools(self):
    #     if self.connection_info.connection_type == ConnectionTypes.DIRECT:
    #         detailed_journal_pools = self.gateway.get_journal_pools("detail")
    #         basic_journal_pools = self.gateway.get_journal_pools("basic")
    #         tmp_journal_pools = []
    #         for detailed_journal in detailed_journal_pools.data:
    #             for basic_journal in basic_journal_pools.data:
    #                 if detailed_journal.journalId == basic_journal.journalId:
    #                     tmp_journal_pool = {}

    #                     tmp_journal_pool["journal_id"] = detailed_journal.journalId
    #                     tmp_journal_pool["journal_status"] = basic_journal.journalStatus

    #                     tmp_journal_pool["data_overflow_watch_seconds"] = (
    #                         detailed_journal.dataOverflowWatchInSeconds
    #                     )
    #                     tmp_journal_pool["is_cache_mode_enabled"] = (
    #                         detailed_journal.isCacheModeEnabled
    #                     )

    #                     tmp_journal_pool["is_inflow_control_enabled"] = (
    #                         detailed_journal.isInflowControlEnabled
    #                     )
    #                     tmp_journal_pool["mp_blade_id"] = detailed_journal.mpBladeId
    #                     tmp_journal_pool["capacity"] = convert_block_capacity(
    #                         basic_journal.blockCapacity
    #                     )
    #                     if basic_journal.usageRate is not None:
    #                         tmp_journal_pool["usage_rate"] = basic_journal.usageRate
    #                     tmp_journal_pool["first_ldev_id"] = basic_journal.firstLdevId
    #                     tmp_journal_pool["num_of_ldevs"] = basic_journal.numOfLdevs
    #                     tmp_journal_pool["capacity_in_unit"] = (
    #                         basic_journal.byteFormatCapacity.replace(" G", " GB")
    #                     )
    #                     tmp_journal_pool["mirror_unit_ids"] = []
    #                     # Convert the list of VSPMirrorUnit to snake_case
    #                     for mirror_unit in detailed_journal.mirrorUnits:
    #                         # mirror_unit_dict = asdict(mirror_unit)
    #                         # Convert all keys in the mirror_unit dict to snake_case
    #                         snake_case_mirror_unit = {
    #                             self.camel_to_snake(k): v
    #                             for k, v in mirror_unit.items()
    #                         }
    #                         tmp_journal_pool["mirror_unit_ids"].append(
    #                             snake_case_mirror_unit
    #                         )
    #                     if basic_journal.numOfActivePaths is not None:
    #                         tmp_journal_pool["num_of_active_paths"] = (
    #                             basic_journal.numOfActivePaths
    #                         )
    #                     if basic_journal.qMarker is not None:
    #                         tmp_journal_pool["q_marker"] = basic_journal.qMarker
    #                     if basic_journal.qCount is not None:
    #                         tmp_journal_pool["q_count"] = basic_journal.qCount

    #                     tmp_journal_pools.append(tmp_journal_pool)
    #                     break
    #         return tmp_journal_pools
    #     else:
    #         resp = self.gateway.get_all_porcelain_journal_volumes()
    #         if "data" in resp:
    #             for item in resp["data"]:
    #                 # Modify the 'totalCapacity' field to MB
    #                 if "totalCapacity" in item:
    #                     item["capacity"] = convert_block_capacity(
    #                         int(item["totalCapacity"]), 1
    #                     )
    #                     del item[
    #                         "totalCapacity"
    #                     ]  # Remove the original 'totalCapacity' field
    #                 if "dataOverflowWatchSeconds" in item:
    #                     item["data_overflow_watch_seconds"] = item[
    #                         "dataOverflowWatchSeconds"
    #                     ]
    #                     del item["dataOverflowWatchSeconds"]
    #                 if "isCacheModeEnabled" in item:
    #                     item["is_cache_mode_enabled"] = item["isCacheModeEnabled"]
    #                     del item["isCacheModeEnabled"]
    #                 if "journalPoolId" in item:
    #                     item["journal_id"] = item["journalPoolId"]
    #                     del item["journalPoolId"]
    #                 if "logicalUnitIds" in item:
    #                     item["logical_unit_ids"] = item["logicalUnitIds"]
    #                     del item["logicalUnitIds"]
    #                 if "logicalUnitIdsHexFormat" in item:
    #                     item["logical_unit_ids_hex_format"] = item[
    #                         "logicalUnitIdsHexFormat"
    #                     ]
    #                     del item["logicalUnitIdsHexFormat"]
    #                 if "mirrorUnitId" in item:
    #                     item["mirror_unit_id"] = 0
    #                     del item["mirrorUnitId"]
    #                 if "mpBladeId" in item:
    #                     item["mp_blade_id"] = item["mpBladeId"]
    #                     del item["mpBladeId"]
    #                 if "timerType" in item:
    #                     item["timer_type"] = item["timerType"]
    #                     del item["timerType"]
    #                 # item = {self.camel_to_snake(item.items())}
    #         return resp

    @log_entry_exit
    def get_journal_pool_by_id(self, pool_id):
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            journal_pools = self.gateway.get_all_journal_info()
            self.logger.writeDebug(
                f"PV:journal_volume: pool_id to be feteched =  {pool_id}"
            )
            return next(
                (pool for pool in journal_pools.data if pool.journalPoolId == pool_id),
                None,
            )
        else:
            return self.gateway.get_journal_pool_by_id(pool_id)

    @log_entry_exit
    def journal_pool_facts(self, spec=None):

        if spec and spec.is_free_journal_pool_id and spec.is_mirror_not_used:
            err_msg = (
                VSPSJournalVolumeValidateMsg.BOTH__FREE_POOL_ID_AND_USED_PARAM.value
            )
            self.logger.writeError(err_msg)
            raise ValueError(err_msg)

        if spec and spec.is_free_journal_pool_id:
            data = {
                "free_journal_pool_ids": self.get_free_journal_pool_ids(
                    spec.free_journal_pool_id_count
                )
            }
            return data
        elif spec and spec.is_mirror_not_used:
            return self.get_unused_journal_pools()

        if spec and spec.journal_id is not None:
            pools = self.get_journal_pool_by_id(spec.journal_id)
            if pools:
                return pools.camel_to_snake_dict()
        else:
            pools = self.gateway.get_all_journal_info().data_to_snake_case_list()
        return None if not pools else pools

    @log_entry_exit
    def create_journal_pool(self, pool_spec):

        if pool_spec.journal_id is not None:
            pool_exits = self.get_journal_pool_by_id(pool_spec.journal_id)
            if pool_exits:
                return pool_exits.camel_to_snake_dict(), None
        self.logger.writeDebug(f"PV:journal_volume: spec =  {pool_spec.startLdevId}")
        if (
            # pool_spec.startLdevId is None
            # and pool_spec.endLdevId is None
            # and
            pool_spec.ldev_ids
            is None
        ):
            err_msg = VSPSJournalVolumeValidateMsg.JOURNAL_VOLUME_REQUIRED.value
            self.logger.writeError(err_msg)
            raise ValueError(err_msg)
        elif pool_spec.startLdevId is not None and pool_spec.endLdevId is not None:
            pass
        if pool_spec.journal_id is None or pool_spec.journal_id == "":
            free_journal_id = self.get_free_journal_pool_ids()
            self.logger.writeDebug(
                f"PV:journal_volume: free_journal_id =  {free_journal_id}"
            )
            if len(free_journal_id) == 0:
                err_msg = VSPSJournalVolumeValidateMsg.NO_FREE_JOURNAL_POOL_ID.value
                self.logger.writeError(err_msg)
                raise ValueError(err_msg)
            pool_spec.journal_id = free_journal_id[0]
        pool_id = self.gateway.create_journal_volume(pool_spec)
        self.connection_info.changed = True

        if self.connection_info.connection_type == ConnectionTypes.DIRECT:
            pool = {}
            if (
                pool_spec.data_overflow_watchIn_seconds is not None
                or pool_spec.is_cache_mode_enabled is not None
                or pool_spec.mp_blade_id is not None
            ):
                pool = self.gateway.update_journal_volume(
                    pool_spec.journal_id, pool_spec
                )
        else:
            if pool_spec.mp_blade_id is not None:
                pool = self.gateway.set_mp_blade_journal_pool(
                    pool_spec.journal_id, pool_spec
                )
        pool = None
        retry = 0
        while pool is None and retry < 5:
            pool = self.get_journal_pool_by_id(pool_spec.journal_id)
            retry += 1
            time.sleep(10)
        if pool is None:
            err_msg = VSPSJournalVolumeValidateMsg.JOURNAL_VOLUME_CREATE_FAILED.value
            self.logger.writeError(err_msg)
            raise ValueError(err_msg)

        self.logger.writeDebug(f"PV:journal_volume: pool =  {pool}")
        return pool.camel_to_snake_dict(), None

    @log_entry_exit
    def update_journal_pool(self, spec, pool_id):
        pool_exits = self.get_journal_pool_by_id(pool_id)
        if pool_exits is None:
            return (
                None,
                VSPSJournalVolumeValidateMsg.NO_JOURNAL_VOLUME_FOR_ID.value.format(
                    pool_id
                ),
            )
        self.logger.writeDebug(f"PV:journal_volume: spec =  {spec}")
        if (
            spec.data_overflow_watchIn_seconds != pool_exits.dataOverflowWatchSeconds
            or spec.is_cache_mode_enabled != pool_exits.isCacheModeEnabled
            or spec.mp_blade_id != pool_exits.mpBladeId
        ):
            if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
                spec.is_cache_mode_enabled = (
                    pool_exits.isCacheModeEnabled
                    if spec.is_cache_mode_enabled is None
                    else spec.is_cache_mode_enabled
                )
                spec.data_overflow_watchIn_seconds = (
                    pool_exits.dataOverflowWatchSeconds
                    if spec.data_overflow_watchIn_seconds is None
                    else spec.data_overflow_watchIn_seconds
                )
            # If any of the conditions do not match, perform the update
            unused = self.gateway.update_journal_volume(pool_id, spec)
        else:
            return (
                pool_exits.camel_to_snake_dict(),
                None,
            )  # Everything is already updated.
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            time.sleep(30)
        pool = self.get_journal_pool_by_id(pool_id).camel_to_snake_dict()
        self.connection_info.changed = True
        return pool, None

    @log_entry_exit
    def expand_journal_pool(self, spec, pool_id):
        pool_exits = self.get_journal_pool_by_id(pool_id)
        if pool_exits is None:
            return (
                None,
                VSPSJournalVolumeValidateMsg.NO_JOURNAL_VOLUME_FOR_ID.value.format(
                    pool_id
                ),
            )
        self.logger.writeDebug(f"PV:journal_volume: pool_exits =  {pool_exits}")
        if len(pool_exits.logicalUnitIds) == 2:
            return (
                pool_exits.camel_to_snake_dict(),
                VSPSJournalVolumeValidateMsg.JP_POOL_LDEV_LIMIT_MAX.value,
            )
        unused = self.gateway.expand_journal_volume(pool_id, spec)
        self.connection_info.changed = True
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            time.sleep(30)
        pool = self.get_journal_pool_by_id(pool_id).camel_to_snake_dict()
        return pool, None

    @log_entry_exit
    def delete_journal_pool(self, pool_id):
        pool = self.get_journal_pool_by_id(pool_id)
        if pool is None:
            return (
                None,
                VSPSJournalVolumeValidateMsg.NO_JOURNAL_VOLUME_FOR_ID.value.format(
                    pool_id
                ),
            )

        unused = self.gateway.delete_journal_volume(pool_id)
        self.connection_info.changed = True
        return None, VSPSJournalVolumeValidateMsg.JOURNAL_POOL_DELETE.value

    @log_entry_exit
    def shrink_journal_pool(self, spec, pool_id):
        pool_exits = self.get_journal_pool_by_id(pool_id)
        if pool_exits is None:
            return (
                None,
                VSPSJournalVolumeValidateMsg.NO_JOURNAL_VOLUME_FOR_ID.value.format(
                    pool_id
                ),
            )
        self.logger.writeDebug(f"PV:journal_volume: pool_exits =  {pool_exits}")
        if len(pool_exits.logicalUnitIds) == 1:
            return (
                pool_exits.camel_to_snake_dict(),
                VSPSJournalVolumeValidateMsg.JP_POOL_LDEV_LIMIT_MIN.value,
            )

        unused = self.gateway.shrink_journal_volume(pool_id, spec)
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            time.sleep(30)
        pool = self.get_journal_pool_by_id(pool_id).camel_to_snake_dict()
        self.connection_info.changed = True
        return pool, None

    @log_entry_exit
    def get_free_journal_pool_ids(self, count=1):
        pools = self.gateway.get_all_journal_info()
        pool_ids = set(jp.journalPoolId for jp in pools.data)
        available_pool = [
            id
            for id in range(StoragePoolLimits.JOURNAL_POOL_ID_LIMIT)
            if id and id not in pool_ids
        ]
        self.logger.writeDebug(f"PV:journal_volume: available_pool =  {available_pool}")
        return (
            available_pool[:count] if count <= len(available_pool) else available_pool
        )

    @log_entry_exit
    def get_unused_journal_pools(self):
        all_pools = self.gateway.get_all_journal_info()
        free_pools = [
            pool.camel_to_snake_dict()
            for pool in all_pools.data
            if pool.journalStatus and pool.journalStatus.upper() == "SMPL"
        ]
        return free_pools

    @log_entry_exit
    def check_ucp_system(self, serial):
        if self.connection_info.connection_type == ConnectionTypes.DIRECT:
            return serial
        if not self.gateway.check_storage_in_ucpsystem(serial):
            err_msg = CommonMessage.SERIAL_NUMBER_NOT_FOUND.value.format(serial)
            self.logger.writeError(err_msg)
            raise ValueError(err_msg)
        else:
            self.serial = serial
            self.resource_id = UAIGResourceID().storage_resourceId(self.serial)
            self.gateway.resource_id = self.resource_id
            return serial
