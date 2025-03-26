from typing import Optional
import time

try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes
    from ..common.uaig_utils import UAIGResourceID
    from ..common.hv_constants import ConnectionTypes
    from ..common.hv_log import Log
    from ..common.ansible_common import (
        log_entry_exit,
        camel_dict_to_snake_case,
        convert_block_capacity,
        convert_decimal_size_to_bytes,
    )
    from ..model.vsp_hur_models import VSPHurPairInfoList
    from .vsp_true_copy_provisioner import RemoteReplicationHelperForSVol
    from ..message.vsp_hur_msgs import VSPHurValidateMsg, HurFailedMsg

    from ..model.vsp_copy_groups_models import (
        DirectCopyPairInfo,
        DirectSpecificCopyGroupInfoList,
    )

except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes
    from common.uaig_utils import UAIGResourceID
    from common.hv_constants import ConnectionTypes
    from common.hv_log import Log
    from common.ansible_common import (
        log_entry_exit,
        camel_dict_to_snake_case,
        convert_block_capacity,
        convert_decimal_size_to_bytes,
    )
    from model.vsp_hur_models import VSPHurPairInfoList
    from message.vsp_hur_msgs import VSPHurValidateMsg, HurFailedMsg
    from .vsp_true_copy_provisioner import RemoteReplicationHelperForSVol
    from model.vsp_copy_groups_models import (
        DirectCopyPairInfo,
        DirectSpecificCopyGroupInfoList,
    )

logger = Log()


class VSPHurProvisioner:

    def __init__(self, connection_info, serial):
        self.logger = Log()
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_HUR
        )
        self.vol_gw = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_VOLUME
        )
        self.cg_gw = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_COPY_GROUPS
        )
        self.config_gw = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_CONFIG_MAP
        )
        self.connection_info = connection_info
        self.serial = serial
        self.gateway.set_storage_serial_number(serial)

    @log_entry_exit
    def get_all_replication_pairs(self, serial=None):
        if serial is None:
            serial = self.serial
        return self.gateway.get_all_replication_pairs(serial)

    @log_entry_exit
    def get_replication_pair_info_list(self, serial=None):
        if serial is None:
            serial = self.serial
        all_rep_pairs = self.gateway.get_all_replication_pairs(serial)

        #  20240918 - get hur facts with fetchAll=true
        #  we return all hur pairs un-filtered
        #  filter all hur by the storage serial
        #  in either primary or secondary storage
        ret_list = []
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            for rp in all_rep_pairs.data:
                # self.logger.writeDebug(f"58 rp ={rp}")
                if serial:
                    if str(serial) == str(rp.primaryVolumeStorageId) or str(
                        serial
                    ) == str(rp.secondaryVolumeStorageId):
                        ret_list.append(rp)  # 20240805
        else:
            for rp in all_rep_pairs.data:
                if serial:
                    if str(serial) == str(rp.serialNumber) or str(serial) == str(
                        rp.remoteSerialNumber
                    ):
                        ret_list.append(rp)
        return VSPHurPairInfoList(ret_list)

    @log_entry_exit
    def get_hur_pair_info_list(self, serial=None):
        if serial is None:
            serial = self.serial

        all_rep_pairs = self.gateway.get_all_replication_pairs(serial)
        ret_list = []
        for rp in all_rep_pairs.data:
            ret_list.append(rp)  # 20240805
        return VSPHurPairInfoList(ret_list)

    @log_entry_exit
    def hur_pair_facts_direct(self, spec=None):

        # sng20241115 - hur_pair_facts_direct
        tc_pairs = self.get_all_hur_pairs_direct(spec=spec)
        self.logger.writeDebug(f"PV:: 88 pairs=  {tc_pairs}")
        if tc_pairs is None:
            return tc_pairs
        if spec is None:
            return tc_pairs
        else:
            ret_tc_pairs = self.apply_filters(tc_pairs, spec)
            logger.writeDebug("sng20241115 :ret_tc_pairs={}", ret_tc_pairs)
            # return VSPHurPairInfo(data=ret_tc_pairs)
            return ret_tc_pairs

    # sng20241115 - prov.get_all_hur_pairs_direct
    @log_entry_exit
    def get_all_hur_pairs_direct(self, serial=None, spec=None):
        if serial is None:
            serial = self.serial
        if spec is None:
            ret_list = self.gateway.get_all_replication_pairs(serial)
            self.logger.writeDebug(f"PROV:105:ret_list= {ret_list} serial = {serial}")
            return ret_list
        if self.connection_info.connection_type == ConnectionTypes.DIRECT:
            # First we check if there is a copy group name present in the spec
            spec.secondary_storage_serial_number = self.gateway.get_secondary_serial(
                spec
            )

            if (
                spec.copy_group_name
                and spec.copy_pair_name
                and spec.local_device_group_name
                and spec.remote_device_group_name
            ):
                return self.cg_gw.get_remote_copy_pair_by_id(spec)

            if spec.copy_group_name and spec.copy_pair_name:
                return self.cg_gw.get_remote_pairs_by_copy_group_and_copy_pair_name(
                    spec
                )

            if spec.copy_group_name:
                return self.cg_gw.get_remote_pairs_for_a_copy_group(spec)

            if spec.primary_volume_id:
                return self.cg_gw.get_remote_pairs_by_pvol(spec)

            if spec.secondary_volume_id:
                return self.cg_gw.get_remote_pairs_by_svol(spec)

            # ret_list = self.cg_gw.get_all_copy_pairs(spec)
            ret_list = self.cg_gw.get_all_remote_pairs_from_copy_groups(spec)
            return ret_list
            # return DirectCopyPairInfoList(data=ret_list)

    @log_entry_exit
    def apply_filters(self, tc_pairs, spec):
        result = self.get_hur_copypairs(tc_pairs)
        return result

    # sng20241115 pair: DirectSpecificCopyGroupInfo or list
    @log_entry_exit
    def get_hur_copypairs(self, pair):

        self.logger.writeDebug("sng20241115 :pair={}", pair)

        if isinstance(pair, list):
            return self.get_hur_copypairs_from_list(pair)
        if isinstance(pair, DirectSpecificCopyGroupInfoList):
            return self.get_hur_copypairs_from_list(pair.data_to_list())

        gad_pairs = []

        if isinstance(pair, DirectCopyPairInfo):
            if pair.replicationType == "UR":
                gad_pairs.append(pair)
                return gad_pairs

        copyPairs = pair.copyPairs
        if copyPairs is None:
            return

        for copyPair in copyPairs:
            # sng20241115 change replicationType here to use other types for testing
            if copyPair.replicationType == "UR":
                gad_pairs.append(copyPair)

        return gad_pairs

    @log_entry_exit
    def get_hur_copypairs_from_list(self, cgList):

        gad_pairs = []

        logger.writeDebug("sng20241115 :cg={}", cgList)
        if isinstance(cgList, dict):
            return self.get_hur_copypairs_from_dict(cgList, gad_pairs)

        for cg in cgList:
            if cg is None:
                continue

            logger.writeDebug("sng20241115 :cg={}", cg)

            if isinstance(cg, dict):
                gad_pairs = self.get_hur_copypairs_from_dict(cg, gad_pairs)
                continue

            copyPairs = None
            #  handle cg class object if needed
            if isinstance(cg, DirectCopyPairInfo):
                copyPairs = [cg]
            elif hasattr(cg, "copyPairs"):
                copyPairs = cg.copyPairs

            logger.writeDebug("sng20241115 :copyPairs={}", cg)
            if copyPairs is None:
                continue

            for copyPair in copyPairs:
                if copyPair.replicationType == "UR":
                    gad_pairs.append(copyPair)

        return gad_pairs

    @log_entry_exit
    def get_hur_copypairs_from_dict(self, cgs, gad_pairs):

        if cgs is None:
            return gad_pairs
        if not isinstance(cgs, dict):
            return gad_pairs

        # cgs is a dict, the element of the dict can some time be an array

        for cg in cgs:

            if cg is None:
                continue

            logger.writeDebug("sng20241115 :cg={}", cg)

            if isinstance(cg, str):
                # this element of the dict is not an array,
                # we can now get the copyPairs from the cgs dict
                copyPairs = cgs["copyPairs"]

                if isinstance(copyPairs, dict):
                    for copyPair in copyPairs:
                        if copyPair["replicationType"] == "UR":
                            gad_pairs.append(copyPair)
                else:
                    # handle copyPair class objects
                    for copyPair in copyPairs:
                        if isinstance(copyPair, dict):
                            if copyPair["replicationType"] == "UR":
                                gad_pairs.append(copyPair)
                        else:
                            if copyPair.replicationType == "UR":
                                gad_pairs.append(copyPair)

                return gad_pairs

            #  cg is a list of dict
            items = cg
            if not isinstance(cg, list):
                return gad_pairs

            for cg in items:

                copyPairs = cg["copy_pairs"]
                if copyPairs is None:
                    continue

                for copyPair in copyPairs:
                    if copyPair.replicationType == "UR":
                        gad_pairs.append(copyPair)

        return gad_pairs

    @log_entry_exit
    def get_hur_facts(self, spec=None):
        # primary_volume_id = spec.get('primary_volume_id',None)
        primary_volume_id = spec.primary_volume_id
        if spec is None or (spec and primary_volume_id is None):
            return self.get_all_hurpairs()
        else:
            return self.get_all_hur_for_primary_vol_id(primary_volume_id)

    @log_entry_exit
    def get_all_hurpairs(self, serial=None):
        if serial is None:
            serial = self.serial

        all_rep_pairs = self.gateway.get_all_replication_pairs(serial)

        filtered = [
            ssp.to_dict() for ssp in all_rep_pairs.data
        ]  # 20240805, update - removed if true
        self.logger.writeDebug(f"filtered={filtered}")
        return filtered

    @log_entry_exit
    def get_hur_for_primary_vol_id(self, primary_vol_id):
        all_hurpairs = self.get_replication_pair_info_list()

        # 20240808 - one pvol can have 3 pairs, this only returns the first pair
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            for tc in all_hurpairs.data:
                if tc.primaryVolumeId == primary_vol_id:
                    return tc
        else:
            for tc in all_hurpairs.data:
                if tc.ldevId == primary_vol_id:
                    return tc
        return None

    @log_entry_exit
    def get_hur_for_secondary_vol_id(self, vol_id):
        all_hurpairs = self.get_replication_pair_info_list()

        # 20240808 - one pvol can have 3 pairs, this only returns the first pair
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            for tc in all_hurpairs.data:
                if tc.secondaryVolumeId == vol_id:
                    return tc
        return None

    # 20240808 - get_hur_by_pvol_mirror, mirror id support
    @log_entry_exit
    def get_hur_by_pvol_mirror(self, primary_vol_id, mirror_unit_id):
        all_hurpairs = self.get_replication_pair_info_list()

        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            for tc in all_hurpairs.data:
                if (
                    tc.primaryVolumeId == primary_vol_id
                    and tc.mirrorUnitId == mirror_unit_id
                ):
                    return tc
        else:
            for tc in all_hurpairs.data:
                if tc.ldevId == primary_vol_id and tc.muNumber == mirror_unit_id:
                    return tc

        return None

    #  get_hur_facts_ext
    @log_entry_exit
    def get_hur_facts_ext(
        self,
        pvol: Optional[int] = None,
        svol: Optional[int] = None,
        mirror_unit_id: Optional[int] = None,
    ):
        all_hurpairs = self.get_replication_pair_info_list()
        self.logger.writeDebug(f"all_hurpairs={all_hurpairs}")

        # 20240812 - get_hur_facts_ext
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            result = [
                ssp
                for ssp in all_hurpairs.data
                if (pvol is None or ssp.primaryVolumeId == pvol)
                and (svol is None or ssp.secondaryVolumeId == svol)
                and (mirror_unit_id is None or ssp.mirrorUnitId == mirror_unit_id)
            ]
            self.logger.writeDebug(f"result={result}")
        else:
            result = [
                ssp
                for ssp in all_hurpairs.data
                if (pvol is None or ssp.ldevId == pvol or ssp.remoteLdevId == pvol)
                and (svol is None or ssp.remoteLdevId == svol or ssp.ldevId == svol)
                and (mirror_unit_id is None or ssp.muNumber == mirror_unit_id)
            ]
            self.logger.writeDebug(f"result={result}")

        return VSPHurPairInfoList(data=result)
        # return result

    @log_entry_exit
    def get_all_hur_for_primary_vol_id(self, primary_vol_id):
        all_hurpairs = self.get_replication_pair_info_list()

        # 20240808 - one pvol can have 3 pairs
        result = []
        for tc in all_hurpairs.data:
            if tc.primaryVolumeId == primary_vol_id:
                result.append(tc)

        return result

    @log_entry_exit
    def get_hur_by_pvol_svol(self, pvol, svol):
        all_hurpairs = self.get_replication_pair_info_list()

        # 20240912 - get_hur_by_pvol_svol
        result = None

        for tc in all_hurpairs.data:
            if str(tc.primaryVolumeId) == pvol and str(tc.secondaryVolumeId) == svol:
                self.logger.writeDebug(f"151 tc: {tc}")
                result = tc
                break

        return result

    @log_entry_exit
    def get_replication_pair_by_id(self, pair_id):
        pairs = self.get_all_replication_pairs(self.serial)
        for pair in pairs.data:
            if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
                if pair.resourceId == pair_id:
                    return pair
            else:
                if pair.serialNumber == pair_id:
                    return pair
        return None

    # 20240808 delete_hur_pair
    @log_entry_exit
    def delete_hur_pair(self, primary_volume_id, mirror_unit_id, spec=None):
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            self.connection_info.changed = False
            comment = None
            tc = self.get_hur_by_pvol_mirror(primary_volume_id, mirror_unit_id)
            if tc is None:
                # 20240908 delete_hur_pair Idempotent
                comment = (
                    VSPHurValidateMsg.PRIMARY_VOLUME_ID_DOES_NOT_EXIST.value.format(
                        primary_volume_id
                    )
                )
                return tc, comment
            if primary_volume_id is None:
                err_msg = (
                    HurFailedMsg.PAIR_DELETION_FAILED.value
                    + VSPHurValidateMsg.PRIMARY_VOLUME_ID.value
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)
            if mirror_unit_id is None:
                err_msg = (
                    HurFailedMsg.PAIR_DELETION_FAILED.value
                    + VSPHurValidateMsg.MIRROR_UNIT_ID.value
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)
            device_id = UAIGResourceID().storage_resourceId(self.serial)
            hurpair_id = tc.resourceId
            self.logger.writeDebug(f"device_id: {device_id}")
            self.logger.writeDebug(f"hurpair_id: {hurpair_id}")
            self.connection_info.changed = True
            return self.gateway.delete_hur_pair(device_id, hurpair_id)
        else:
            pair_exiting = self.gateway.get_replication_pair(spec)
            if pair_exiting is None:
                return VSPHurValidateMsg.NO_HUR_PAIR_FOUND.value.format(
                    spec.copy_pair_name
                )
            if spec.copy_group_name and spec.copy_pair_name:
                self.connection_info.changed = True
                return self.gateway.delete_hur_pair_by_pair_id(spec)

    @log_entry_exit
    def resync_hur_pair(self, primary_volume_id, mirror_unit_id, spec=None):
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            tc = self.get_hur_by_pvol_mirror(primary_volume_id, mirror_unit_id)
            self.connection_info.changed = False
            if tc is None:
                err_msg = (
                    HurFailedMsg.PAIR_RESYNC_FAILED.value
                    + VSPHurValidateMsg.PRIMARY_VOLUME_ID_DOES_NOT_EXIST.value.format(
                        primary_volume_id
                    )
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)

            comment = None
            if tc.status == "PAIR":
                comment = VSPHurValidateMsg.NO_RESYNC_NEEDED.value.format(
                    tc.primaryVolumeId,
                    tc.primaryVolumeStorageId,
                    tc.secondaryVolumeId,
                    tc.secondaryVolumeStorageId,
                )
                return camel_dict_to_snake_case(tc.to_dict()), comment

            if primary_volume_id is None:
                err_msg = (
                    HurFailedMsg.PAIR_RESYNC_FAILED.value
                    + VSPHurValidateMsg.PRIMARY_VOLUME_ID.value
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)
            if mirror_unit_id is None:
                err_msg = (
                    HurFailedMsg.PAIR_RESYNC_FAILED.value
                    + VSPHurValidateMsg.MIRROR_UNIT_ID.value
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)
            device_id = UAIGResourceID().storage_resourceId(self.serial)
            tc_pair_id = tc.resourceId
            rep_pair_id = self.gateway.resync_hur_pair(device_id, tc_pair_id)
            self.logger.writeDebug(f"rep_pair_id: {rep_pair_id}")
            self.connection_info.changed = True
            info = self.get_replication_pair_by_id(rep_pair_id)
            self.logger.writeDebug(f"info: {info}")
            info = info.to_dict()
            self.logger.writeDebug(f"info: {info}")
            return camel_dict_to_snake_case(info), comment
            # return info, comment
        else:
            pair_exiting = self.gateway.get_replication_pair(spec)
            if (
                pair_exiting["pvol_status"] == "PAIR"
                and pair_exiting["svol_status"] == "PAIR"
            ):
                return pair_exiting
            pair_id = self.gateway.resync_hur_pair(spec)
            self.logger.writeDebug(f"PV:resync_hur_pair: pair_id=  {pair_id}")
            pair = self.gateway.get_replication_pair(spec)
            self.connection_info.changed = True
            return pair

    @log_entry_exit
    def swap_resync_hur_pair(self, primary_volume_id, spec=None):
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            tc = self.get_hur_for_secondary_vol_id(primary_volume_id)
            if tc is None:
                err_msg = (
                    HurFailedMsg.PAIR_SWAP_RESYNC_FAILED.value
                    + VSPHurValidateMsg.PRIMARY_VOLUME_ID_DOES_NOT_EXIST.value.format(
                        primary_volume_id
                    )
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)

            if primary_volume_id is None:
                err_msg = (
                    HurFailedMsg.PAIR_SWAP_RESYNC_FAILED.value
                    + VSPHurValidateMsg.PRIMARY_VOLUME_ID.value
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)

            # sng20241218 - swap here for now until operator rework is done
            logger.writeDebug(f"PV:sng20241218 507: spec=  {spec}")
            device_id = UAIGResourceID().storage_resourceId(
                spec.secondary_storage_serial_number
            )
            self.gateway.resource_id = device_id
            logger.writeDebug(f"PV:sng20241218 507: device_id=  {device_id}")

            # fetch the pair to get the resourceId
            logger.writeDebug(f"PV:sng20241218 507: pair=  {tc}")
            pair = self.get_hur_for_secondary_vol_id(tc.secondaryVolumeId)
            logger.writeDebug(f"PV:sng20241218 507: pair=  {pair}")
            if pair is None:
                err_msg = (
                    HurFailedMsg.PAIR_SWAP_RESYNC_FAILED.value
                    + VSPHurValidateMsg.HUR_PAIR_NOT_FOUND_SIMPLE.value
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)

            secondaryVolumeId = tc.secondaryVolumeId
            rep_pair_id = self.gateway.swap_resync_hur_pair(device_id, pair.resourceId)
            self.logger.writeDebug(
                f"PV:sng20241218 507: pair.resourceId=  {pair.resourceId}"
            )
            self.logger.writeDebug(
                f"PV:sng20241218 507: secondaryVolumeId=  {secondaryVolumeId}"
            )
            self.logger.writeDebug(f"PV:sng20241218 507: rep_pair_id=  {rep_pair_id}")
            self.connection_info.changed = True
            self.serial = spec.secondary_storage_serial_number
            time.sleep(10)
            # UCA-2411 increase it from 10 to 24 (4 minutes) retries
            retries = 20
            for attempt in range(retries):
                pair = self.get_hur_for_primary_vol_id(secondaryVolumeId)
                if pair is not None:
                    # If pair is not None, break out of the loop
                    break
                time.sleep(10)
            return pair
        else:
            pair_exiting = self.gateway.get_replication_pair(spec)
            if (
                pair_exiting["pvol_status"] == "PAIR"
                and pair_exiting["svol_status"] == "PAIR"
            ):
                return pair_exiting
            pair_id = self.gateway.swap_resync_hur_pair(spec)
            self.logger.writeDebug(f"PV:swap_resync_hur_pair: pair_id=  {pair_id}")
            pair = self.gateway.get_replication_pair(spec)
            self.connection_info.changed = True
            return pair

    @log_entry_exit
    def split_hur_pair(self, primary_volume_id, mirror_unit_id, spec=None):
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            tc = self.get_hur_by_pvol_mirror(primary_volume_id, mirror_unit_id)
            if tc is None:
                err_msg = (
                    HurFailedMsg.PAIR_SPLIT_FAILED.value
                    + VSPHurValidateMsg.PRIMARY_VOLUME_AND_MU_ID_WRONG.value.format(
                        primary_volume_id, mirror_unit_id
                    )
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)

            comment = None
            self.connection_info.changed = False
            if tc.status == "PSUS":
                comment = VSPHurValidateMsg.ALREADY_SPLIT_PAIR.value.format(
                    tc.primaryVolumeId,
                    tc.primaryVolumeStorageId,
                    tc.secondaryVolumeId,
                    tc.secondaryVolumeStorageId,
                )
                return camel_dict_to_snake_case(tc.to_dict()), comment
            if primary_volume_id is None:
                err_msg = (
                    HurFailedMsg.PAIR_SPLIT_FAILED.value
                    + VSPHurValidateMsg.PRIMARY_VOLUME_ID.value.format(
                        primary_volume_id, mirror_unit_id
                    )
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)

            if mirror_unit_id is None:
                err_msg = (
                    HurFailedMsg.PAIR_SPLIT_FAILED.value
                    + VSPHurValidateMsg.MIRROR_UNIT_ID.value.format(
                        primary_volume_id, mirror_unit_id
                    )
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)

            device_id = UAIGResourceID().storage_resourceId(self.serial)
            tc_pair_id = tc.resourceId

            # sng20241220 - support svol readwrite
            self.logger.writeDebug(
                f"is_svol_readwriteable: {spec.is_svol_readwriteable}"
            )
            rep_pair_id = self.gateway.split_hur_pair(
                device_id, tc_pair_id, spec.is_svol_readwriteable
            )

            self.connection_info.changed = True
            self.logger.writeDebug(f"rep_pair_id: {rep_pair_id}")
            tc = self.get_replication_pair_by_id(rep_pair_id)
            return camel_dict_to_snake_case(tc.to_dict()), comment
        else:
            err_msg = ""
            pair_exiting = self.gateway.get_replication_pair(spec)
            if pair_exiting is None:
                err_msg = (
                    HurFailedMsg.PAIR_SPLIT_FAILED.value
                    + VSPHurValidateMsg.NO_HUR_PAIR_FOUND.value.format(
                        spec.copy_pair_name
                    )
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)
            if pair_exiting["remote_mirror_copy_pair_id"] is not None:
                pair_elements = pair_exiting["remote_mirror_copy_pair_id"].split(",")
                if (
                    spec.local_device_group_name is not None
                    or spec.remote_device_group_name is not None
                ):
                    if spec.local_device_group_name != pair_elements[2]:
                        err_msg = (
                            HurFailedMsg.PAIR_SPLIT_FAILED.value
                            + VSPHurValidateMsg.NO_LOCAL_DEVICE_NAME_FOUND.value.format(
                                spec.copy_group_name, pair_elements[2]
                            )
                        )
                        logger.writeError(err_msg)
                        raise ValueError(err_msg)
                    elif spec.remote_device_group_name != pair_elements[3]:
                        err_msg = (
                            HurFailedMsg.PAIR_SPLIT_FAILED.value
                            + VSPHurValidateMsg.NO_REMOTE_DEVICE_NAME_FOUND.value.format(
                                spec.copy_group_name, pair_elements[3]
                            )
                        )
                        logger.writeError(err_msg)
                        raise ValueError(err_msg)
            if (
                pair_exiting["pvol_status"] == "PSUS"
                and pair_exiting["svol_status"] == "SSUS"
            ):
                return pair_exiting
            pair_id = self.gateway.split_hur_pair(spec)
            self.logger.writeDebug(f"PV:split_hur_pair: pair_id=  {pair_id}")
            pair = self.gateway.get_replication_pair(spec)
            self.connection_info.changed = True
            return pair

    @log_entry_exit
    def swap_split_hur_pair(self, primary_volume_id, spec=None):
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            if primary_volume_id is None:
                err_msg = (
                    HurFailedMsg.PAIR_SWAP_SPLIT_FAILED.value
                    + VSPHurValidateMsg.PRIMARY_VOLUME_ID.value
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)

            tc = self.get_hur_for_secondary_vol_id(primary_volume_id)
            if tc is None:
                err_msg = (
                    HurFailedMsg.PAIR_SWAP_SPLIT_FAILED.value
                    + VSPHurValidateMsg.PRIMARY_VOLUME_ID_DOES_NOT_EXIST.value.format(
                        primary_volume_id
                    )
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)

            # sng20241218 - swap here for now until operator rework is done
            logger.writeDebug(f"PV:sng20241218 507: spec=  {spec}")
            device_id = UAIGResourceID().storage_resourceId(
                spec.secondary_storage_serial_number
            )
            self.gateway.resource_id = device_id
            logger.writeDebug(f"PV:sng20241218 507: device_id=  {device_id}")

            # fetch the pair to get the resourceId
            logger.writeDebug(f"PV:sng20241218 507: pair=  {tc}")
            pair = self.get_hur_for_secondary_vol_id(tc.secondaryVolumeId)
            logger.writeDebug(f"PV:sng20241218 507: pair=  {pair}")
            if pair is None:
                err_msg = (
                    HurFailedMsg.PAIR_SWAP_RESYNC_FAILED.value
                    + VSPHurValidateMsg.HUR_PAIR_NOT_FOUND_SIMPLE.value
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)

            self.gateway.swap_split_hur_pair(device_id, pair.resourceId)
            self.connection_info.changed = True
            pair = self.get_hur_for_secondary_vol_id(tc.secondaryVolumeId)
            return pair

        else:
            pair_exiting = self.gateway.get_replication_pair(spec)
            if (
                pair_exiting["pvol_status"] == "PSUS"
                and pair_exiting["svol_status"] == "SSWS"
            ):
                return pair_exiting
            pair_id = self.gateway.swap_split_hur_pair(spec)
            self.logger.writeDebug(f"PV:swap_split_hur_pair: pair_id=  {pair_id}")
            pair = self.gateway.get_replication_pair(spec)
            self.connection_info.changed = True
            return pair

    @log_entry_exit
    def is_resize_needed(self, volume_data, spec):
        size_in_bytes = convert_decimal_size_to_bytes(spec.new_volume_size)
        if volume_data.blockCapacity > size_in_bytes:
            logger.writeDebug(
                "PV:resize_true_copy_copy_pair: Shrink/reduce volume size is not supported."
            )
            return False

        expand_val = size_in_bytes - (
            volume_data.blockCapacity if volume_data.blockCapacity else 0
        )
        if expand_val > 0:
            return True
        return False

    @log_entry_exit
    def resize_hur_copy_pair(self, spec=None):
        hur = None
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            if spec.primary_volume_id:
                primary_volume_id = spec.primary_volume_id
                device_id = UAIGResourceID().storage_resourceId(self.serial)
                ldev_resource_id = UAIGResourceID().ldev_resourceId(
                    self.serial, spec.primary_volume_id
                )
                pvol_data = self.vol_gw.get_volume_by_id_v2(device_id, ldev_resource_id)
                logger.writeDebug("PV:resize_true_copy_copy_pair: zmpvol= ", pvol_data)
                hur = self.get_hur_for_primary_vol_id(primary_volume_id)
                if hur is None:
                    raise ValueError(
                        VSPHurValidateMsg.PRIMARY_VOLUME_ID_DOES_NOT_EXIST.value.format(
                            primary_volume_id
                        )
                    )
                svol_device_id = UAIGResourceID().storage_resourceId(
                    spec.secondary_storage_serial_number
                )
                svol_ldev_resource_id = UAIGResourceID().ldev_resourceId(
                    spec.secondary_storage_serial_number, hur.secondaryVolumeId
                )
                svol_data = self.vol_gw.get_volume_by_id_v2(
                    svol_device_id, svol_ldev_resource_id
                )
                if pvol_data.totalCapacity == convert_decimal_size_to_bytes(
                    spec.new_volume_size, 1
                ):
                    logger.writeDebug(
                        "PV:resize_true_copy_copy_pair: Resize not needed"
                    )
                    pair = camel_dict_to_snake_case(hur.to_dict())
                    pair["primary_volume_size"] = convert_block_capacity(
                        pvol_data.totalCapacity, 1
                    )
                    pair["secondary_volume_size"] = convert_block_capacity(
                        svol_data.totalCapacity, 1
                    )
                    return pair
                elif pvol_data.totalCapacity > convert_decimal_size_to_bytes(
                    spec.new_volume_size, 1
                ):
                    logger.writeDebug(
                        "PV:resize_true_copy_copy_pair: Shrink/reduce volume size is not supported."
                    )
                    raise ValueError("Shrink/reduce volume size is not supported.")

            if hur is not None:
                pair_id = self.gateway.resize_hur_pair(hur, spec)
                logger.writeDebug(f"PV:resize_hur_copy_pair: pair_id=  {pair_id}")
            updated_pvol_data = self.vol_gw.get_volume_by_id_v2(
                device_id, ldev_resource_id
            )
            updated_svol_data = self.vol_gw.get_volume_by_id_v2(
                svol_device_id, svol_ldev_resource_id
            )
            pair = camel_dict_to_snake_case(hur.to_dict())
            pair["primary_volume_size"] = convert_block_capacity(
                updated_pvol_data.totalCapacity, 1
            )
            pair["secondary_volume_size"] = convert_block_capacity(
                updated_svol_data.totalCapacity, 1
            )
            self.connection_info.changed = True
            return pair
            # hur_pair_id = hur.resourceId
            # info = self.get_replication_pair_by_id(hur_pair_id)
            # self.connection_info.changed = True
            # return info
        else:
            pair_id = None
            if spec.copy_group_name and spec.copy_pair_name:
                hur = self.cg_gw.get_remote_pairs_by_copy_group_and_copy_pair_name(spec)
                logger.writeDebug(f"PV:resize_true_copy_copy_pair: hur=  {hur}")
                if hur is not None and len(hur) > 0:
                    pvol_id = hur[0].pvolLdevId
                    pvol_data = self.vol_gw.get_volume_by_id(pvol_id)
                    resize_needed = self.is_resize_needed(pvol_data, spec)
                    if resize_needed is False:
                        err_msg = (
                            HurFailedMsg.PAIR_RESIZE_FAILED.value
                            + VSPHurValidateMsg.REDUCE_VOLUME_SIZE_NOT_SUPPORTED.value
                        )
                        logger.writeError(err_msg)
                        raise ValueError(err_msg)
                    else:
                        pair_id = self.gateway.resize_hur_pair(hur[0], spec)
                        logger.writeDebug(
                            f"PV:resize_hur_copy_pair: pair_id=  {pair_id}"
                        )
                        pair = self.gateway.get_replication_pair(spec)
                        self.connection_info.changed = True
                        return pair
                else:
                    err_msg = (
                        HurFailedMsg.PAIR_RESIZE_FAILED.value
                        + VSPHurValidateMsg.NO_HUR_PAIR_FOUND.value.format(
                            spec.copy_pair_name
                        )
                    )
                    logger.writeError(err_msg)
                    raise ValueError(err_msg)

    #  20240830 convert HostGroupTC to HostGroupHUR
    def convert_secondary_hostgroups(self, secondary_hostgroups):
        hgs = []
        for hg in secondary_hostgroups:
            #  we just take the first one
            #  not expect more than one
            del hg["hostGroupID"]
            del hg["resourceGroupID"]
            hgs.append(hg)
            return hgs

    @log_entry_exit
    def get_copy_group_by_name(self, spec):
        return self.cg_gw.get_copy_group_by_name(spec)

    # 20240808 - prov.create_hur
    @log_entry_exit
    def create_hur_pair(self, spec):
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            # sng20250125 fix UCA-2466
            tc = self.get_hur_by_pvol_mirror(
                spec.primary_volume_id, spec.mirror_unit_id
            )
            if tc:
                comment = VSPHurValidateMsg.HUR_PAIR_ALREADY_EXIST.value.format(
                    spec.primary_volume_id, spec.mirror_unit_id
                )
                # we can return the comment if desired, will need a little bit of work
                self.logger.writeDebug("comment={}", comment)
                self.connection_info.changed = False
                return tc

            return self.create_hur_gateway(spec)
        else:
            return self.create_hur_direct(spec)

    @log_entry_exit
    def create_hur_direct(self, spec):
        pair_exiting = self.gateway.get_replication_pair(spec)
        if spec.begin_secondary_volume_id or spec.end_secondary_volume_id:
            raise ValueError(
                VSPHurValidateMsg.SECONDARY_RANGE_ID_IS_NOT_SUPPORTED.value
            )
        if pair_exiting is not None:
            if pair_exiting["pvol_ldev_id"] != spec.primary_volume_id:
                return "Copy pair name : {} already exits in copy group: {}".format(
                    spec.copy_pair_name, spec.copy_group_name
                )
            else:
                return pair_exiting
        secondary_storage_connection_info = spec.secondary_connection_info
        copy_group = self.get_copy_group_by_name(spec)
        if copy_group is None:
            spec.is_new_group_creation = True
        else:
            spec.is_new_group_creation = False
            if (
                spec.local_device_group_name is not None
                and spec.local_device_group_name != copy_group.localDeviceGroupName
            ):
                err_msg = (
                    HurFailedMsg.PAIR_CREATION_FAILED.value
                    + VSPHurValidateMsg.NO_LOCAL_DEVICE_NAME_FOUND.value.format(
                        spec.copy_group_name, copy_group.localDeviceGroupName
                    )
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)

            if (
                spec.remote_device_group_name is not None
                and spec.remote_device_group_name != copy_group.remoteDeviceGroupName
            ):
                err_msg = (
                    HurFailedMsg.PAIR_CREATION_FAILED.value
                    + VSPHurValidateMsg.NO_REMOTE_DEVICE_NAME_FOUND.value.format(
                        spec.copy_group_name, copy_group.localDeviceGroupName
                    )
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)

        secondary_storage_connection_info.connection_type = ConnectionTypes.DIRECT
        rr_prov = RemoteReplicationHelperForSVol(
            secondary_storage_connection_info, self.gateway.get_secondary_serial(spec)
        )
        pvol = self.get_volume_by_id(spec.primary_volume_id)
        if pvol is None:
            err_msg = (
                HurFailedMsg.PAIR_CREATION_FAILED.value
                + VSPHurValidateMsg.NO_PRIMARY_VOLUME_FOUND.value.format(
                    spec.primary_volume_id
                )
            )
            logger.writeError(err_msg)
            raise ValueError(err_msg)

        secondary_vol_id = None
        try:
            if spec.secondary_nvm_subsystem is not None:
                secondary_vol_id = rr_prov.get_secondary_volume_id_when_nvme(pvol, spec)
            else:
                secondary_vol_id = rr_prov.get_secondary_volume_id(pvol, spec)
            spec.secondary_volume_id = secondary_vol_id
            spec.is_data_reduction_force_copy = pvol.isDataReductionShareEnabled
            result = self.gateway.create_hur_pair(spec)
            self.logger.writeDebug(f"create_hur_direct result: {result}")

            # get immediately after create returning Unable to find the resource. give 5 secs
            time.sleep(5)
            # return self.get_replication_pair_by_id(result)
            pair = self.gateway.get_replication_pair(spec)
            self.connection_info.changed = True
            return pair
        except Exception as ex:
            logger.writeDebug(f"HUR create failed: {ex}")
            # if the HUR creation fails, delete the secondary volume
            err_msg = HurFailedMsg.PAIR_CREATION_FAILED.value + str(ex)
            if secondary_vol_id:
                if spec.secondary_nvm_subsystem is not None:
                    rr_prov.delete_volume_when_nvme(
                        secondary_vol_id,
                        pvol.nvmSubsystemId,
                        spec.secondary_nvm_subsystem,
                        pvol.namespaceId,
                    )
                else:
                    rr_prov.delete_volume(secondary_vol_id, spec)
                logger.writeError(err_msg)
            raise ValueError(err_msg)

    @log_entry_exit
    def create_hur_gateway(self, spec):
        if (
            spec.begin_secondary_volume_id is None
            and spec.end_secondary_volume_id is not None
        ) or (
            spec.begin_secondary_volume_id is not None
            and spec.end_secondary_volume_id is None
        ):
            raise ValueError(VSPHurValidateMsg.SECONDARY_RANGE_ID_INVALID.value)
        consistency_group_id = spec.consistency_group_id or -1
        enable_delta_resync = spec.enable_delta_resync or False
        allocate_new_consistency_group = spec.allocate_new_consistency_group or False

        #  20240808 - get secondary_hostgroups from RemoteReplicationHelperForSVol
        rr_prov = RemoteReplicationHelperForSVol(
            self.connection_info, spec.secondary_storage_serial_number
        )
        # secondary_hostgroups = rr_prov.get_secondary_hg_info()
        secondary_hostgroups = None
        try:
            secondary_hostgroups = rr_prov.get_secondary_hostgroups_payload(
                spec.secondary_hostgroups
            )
        except Exception as ex:
            err_msg = HurFailedMsg.PAIR_CREATION_FAILED.value + str(ex)
            logger.writeError(err_msg)
            raise ValueError(err_msg)
        self.logger.writeDebug(
            f"PV: 199 create_hur: rr_prov=  {rr_prov} secondary_hostgroups = {secondary_hostgroups}"
        )

        secondary_hostgroups = self.convert_secondary_hostgroups(secondary_hostgroups)

        # 20240912 - hur get by pvol svol
        pvol, svol = self.gateway.create_hur(
            spec.primary_volume_id,
            consistency_group_id,
            enable_delta_resync,
            allocate_new_consistency_group,
            spec.secondary_storage_serial_number,
            spec.secondary_pool_id,
            #  20240808 - do we always ignore the spec.secondary_hostgroups?
            # or it will be another option later
            # spec.secondary_hostgroups,
            secondary_hostgroups,
            spec.primary_volume_journal_id,
            spec.secondary_volume_journal_id,
            spec.mirror_unit_id,
            spec.begin_secondary_volume_id,
            spec.end_secondary_volume_id,
        )

        #  id of the newly created pair
        self.logger.writeDebug(f"from create_hur pvol: {pvol}")
        self.logger.writeDebug(f"from create_hur svol: {svol}")
        self.connection_info.changed = True

        if svol is None:
            hurPairResourceId = pvol
            #  20240808 - get_hur_by hurPairResourceId
            return self.get_replication_pair_by_id(hurPairResourceId)
        else:

            # 20240912 - get_hur_by_pvol_svol retry
            response = None
            retryCount = 0
            while response is None and retryCount < 60:
                retryCount = retryCount + 1
                response = self.get_hur_by_pvol_svol(pvol, svol)
                self.logger.writeDebug(f"1055 response: {response}")
                if response:
                    break
                time.sleep(1)
                continue

            return response

    @log_entry_exit
    def check_storage_in_ucpsystem(self) -> bool:
        return self.gateway.check_storage_in_ucpsystem()

    @log_entry_exit
    def get_volume_by_id(self, primary_volume_id):
        volume = self.vol_gw.get_volume_by_id(primary_volume_id)
        # return vol_gw.get_volume_by_id(device_id, primary_volume_id)
        self.logger.writeDebug(f"PROV:get_volume_by_id:volume: {volume}")

        return volume

    @log_entry_exit
    def get_volume_by_id_v2(self, storage_id, volume_id):
        volume = self.vol_gw.get_volume_by_id_v2(storage_id, volume_id)
        # return vol_gw.get_volume_by_id(device_id, primary_volume_id)
        self.logger.writeDebug(f"PROV:get_volume_by_id_v2:volume: {volume}")

        return volume

    @log_entry_exit
    def get_copy_group_list(self):
        return self.cg_gw.get_copy_group_list()

    @log_entry_exit
    def is_out_of_band(self):
        return self.config_gw.is_out_of_band()
