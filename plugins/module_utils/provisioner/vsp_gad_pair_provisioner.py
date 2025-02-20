import time

try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes
    from ..message.vsp_gad_pair_msgs import GADPairValidateMSG
    from ..provisioner.vsp_storage_system_provisioner import VSPStorageSystemProvisioner
    from ..common.hv_constants import CommonConstants
    from ..common.vsp_constants import PairStatus, DEFAULT_NAME_PREFIX
    from ..provisioner.vsp_host_group_provisioner import VSPHostGroupProvisioner
    from ..message.vsp_true_copy_msgs import VSPTrueCopyValidateMsg
    from ..message.vsp_gad_pair_msgs import GADFailedMsg
    from ..common.vsp_constants import VolumePayloadConst
    from ..common.hv_constants import ConnectionTypes
    from ..common.hv_log import Log
    from ..model.vsp_volume_models import CreateVolumeSpec
    from ..model.vsp_resource_group_models import VSPResourceGroupSpec
    from ..common.uaig_utils import UAIGResourceID
    from ..model.vsp_copy_groups_models import (
        DirectCopyPairInfo,
        DirectSpecificCopyGroupInfo,
        DirectSpecificCopyGroupInfoList,
    )
    from ..model.vsp_gad_pairs_models import (
        HostgroupSpec,
        VspGadPairsInfo,
    )
    from ..common.ansible_common import (
        log_entry_exit,
        convert_decimal_size_to_bytes,
        camel_dict_to_snake_case,
        convert_block_capacity,
    )

except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes
    from message.vsp_gad_pair_msgs import GADPairValidateMSG
    from provisioner.vsp_storage_system_provisioner import VSPStorageSystemProvisioner
    from common.hv_constants import CommonConstants
    from common.vsp_constants import PairStatus, DEFAULT_NAME_PREFIX
    from provisioner.vsp_host_group_provisioner import VSPHostGroupProvisioner
    from message.vsp_true_copy_msgs import VSPTrueCopyValidateMsg
    from message.vsp_gad_pair_msgs import GADFailedMsg
    from common.vsp_constants import VolumePayloadConst
    from common.hv_constants import ConnectionTypes
    from common.hv_log import Log
    from model.vsp_volume_models import CreateVolumeSpec
    from model.vsp_resource_group_models import VSPResourceGroupSpec
    from common.uaig_utils import UAIGResourceID
    from model.vsp_copy_groups_models import (
        DirectCopyPairInfo,
        DirectSpecificCopyGroupInfo,
        DirectSpecificCopyGroupInfoList,
    )
    from model.vsp_gad_pairs_models import (
        HostgroupSpec,
        VspGadPairsInfo,
    )
    from common.ansible_common import (
        log_entry_exit,
        convert_decimal_size_to_bytes,
        convert_block_capacity,
    )

logger = Log()


class GADPairProvisioner:

    def __init__(self, connection_info, serial):
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_GAD_PAIR
        )
        self.vol_gw = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_VOLUME
        )
        self.config_gw = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_CONFIG_MAP
        )
        if connection_info.connection_type == ConnectionTypes.DIRECT:
            # sng1104 get VSPRemoteCopyGroupsDirectGateway
            self.cg_gw = GatewayFactory.get_gateway(
                connection_info, GatewayClassTypes.VSP_COPY_GROUPS
            )
            self.rg_gateway = GatewayFactory.get_gateway(
                connection_info, GatewayClassTypes.VSP_RESOURCE_GROUP
            )

        self.storage_prov = VSPStorageSystemProvisioner(connection_info)
        self.connection_info = connection_info
        self.connection_type = connection_info.connection_type
        self.serial = serial

        #  sng1104 check_ucp_system?
        self.check_ucp_system(serial)
        self.gateway.set_storage_serial_number(serial)

    @log_entry_exit
    def create_gad_pair(self, gad_pair_spec):
        # UCA-2455 - typo? this is blocking direct create
        # 'VspGadPairSpec' object has no attribute 'begin_secondary_volume_id'"
        if (
            gad_pair_spec.begin_secondary_volume_id
            or gad_pair_spec.end_secondary_volume_id
        ):
            raise ValueError(
                GADPairValidateMSG.SECONDARY_RANGE_ID_IS_NOT_SUPPORTED.value
            )
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            return self.create_gad_pair_gateway(gad_pair_spec)
        else:
            return self.create_gad_pair_direct(gad_pair_spec)

    @log_entry_exit
    def get_resource_group_by_id_remote(self, spec, resourceGroupId):
        secondary_storage_connection_info = spec.secondary_storage_connection_info
        secondary_storage_connection_info.connection_type = ConnectionTypes.DIRECT
        rr_prov = RemoteReplicationHelperForSVol(
            secondary_storage_connection_info, spec.secondary_storage_serial_number
        )
        vol = rr_prov.get_resource_group_by_id(resourceGroupId)
        return vol

    @log_entry_exit
    def get_vsm_all(self):
        return self.rg_gateway.get_vsm_all()

    @log_entry_exit
    def get_secondary_serial_direct(self, spec):
        return self.gateway.get_secondary_serial(spec)

    @log_entry_exit
    def get_vsm_all_remote(self, spec):
        secondary_storage_connection_info = spec.secondary_storage_connection_info
        secondary_storage_connection_info.connection_type = ConnectionTypes.DIRECT
        rr_prov = RemoteReplicationHelperForSVol(
            secondary_storage_connection_info, spec.secondary_storage_serial_number
        )
        vsms = rr_prov.get_vsm_all()
        return vsms

    @log_entry_exit
    def get_vol_remote(self, spec, ldev):
        secondary_storage_connection_info = spec.secondary_storage_connection_info
        secondary_storage_connection_info.connection_type = ConnectionTypes.DIRECT
        rr_prov = RemoteReplicationHelperForSVol(
            secondary_storage_connection_info, spec.secondary_storage_serial_number
        )
        vol = rr_prov.get_volume_by_id(ldev)
        return vol

    @log_entry_exit
    def create_gad_pair_direct(self, spec):

        #  sng20241123 auto config the is_new_group_creation
        copy_group = self.cg_gw.get_copy_group_by_name(spec)
        logger.writeDebug(f"copy_group result: {copy_group}")
        if copy_group is None:
            spec.is_new_group_creation = True
        else:
            spec.is_new_group_creation = False
            spec.muNumber = copy_group.muNumber

        pvol = self.get_volume_by_id(spec.primary_volume_id)
        if pvol is None:
            err_msg = (
                GADFailedMsg.PAIR_CREATION_FAILED.value
                + VSPTrueCopyValidateMsg.NO_PRIMARY_VOLUME_FOUND.value.format(
                    spec.primary_volume_id
                )
            )
            logger.writeError(err_msg)
            raise ValueError(err_msg)

        # sng20241127 - pvol set_alua_mode
        if spec.set_alua_mode:
            self.vol_gw.change_volume_settings(
                spec.primary_volume_id, None, spec.set_alua_mode
            )

        # verify the pvol isAluaEnabled
        pvol = self.get_volume_by_id(spec.primary_volume_id)
        logger.writeDebug("PROV:813:pvol.isAluaEnabled = {}", pvol.isAluaEnabled)

        secondary_storage_connection_info = spec.secondary_storage_connection_info
        secondary_storage_connection_info.connection_type = ConnectionTypes.DIRECT
        rr_prov = RemoteReplicationHelperForSVol(
            secondary_storage_connection_info, spec.secondary_storage_serial_number
        )
        secondary_vol_id = None
        try:
            secondary_vol_id = rr_prov.get_secondary_volume_id(pvol, spec)
            spec.secondary_volume_id = secondary_vol_id
            result = self.gateway.create_gad_pair(spec)
            logger.writeDebug(f"create_gad_pair result: {result}")
            pair = self.cg_gw.get_one_copy_pair_by_id(
                result, spec.secondary_connection_info
            )
            # get immediately after create returning Unable to find the resource. give 5 secs
            # time.sleep(5)
            # return self.get_replication_pair_by_id(result)
            # pair = self.get_gad_pair_by_pvol_id(spec, spec.primary_volume_id)
            self.connection_info.changed = True
            return pair
        except Exception as ex:
            # if the GAD creation fails, delete the secondary volume
            err_msg = GADFailedMsg.PAIR_CREATION_FAILED.value + str(ex)
            if "0C1B" in str(ex):
                err_msg = GADFailedMsg.PAIR_CREATION_FAILED.value + "The specified port is in the NVMe mode. This feature is not supported."
            try:
                if secondary_vol_id:
                    rr_prov.delete_volume(secondary_vol_id, spec)
            except Exception as del_err:
                err_msg = err_msg + str(del_err)
            logger.writeError(err_msg)
            raise ValueError(err_msg)

    @log_entry_exit
    def create_gad_pair_gateway(self, gad_pair_spec):
        try:
            secondary_system_serial = self.get_secondary_storage_system_serial(
                gad_pair_spec.secondary_storage_serial_number
            )
            gad_pair_spec.remote_ucp_system = secondary_system_serial
            self.validate_hg_details(gad_pair_spec)
            unused = self.gateway.create_gad_pair(gad_pair_spec)
            self.connection_info.changed = True
            pairs = self.get_gad_pair_by_id(gad_pair_spec.primary_volume_id)
            count = 0
            while not pairs and count < 15:
                time.sleep(5)
                pairs = self.get_gad_pair_by_id(gad_pair_spec.primary_volume_id)
                count += 1
            return pairs
        except Exception as ex:
            err_msg = GADFailedMsg.PAIR_CREATION_FAILED.value + str(ex)
            logger.writeError(err_msg)
            raise ValueError(err_msg)

    @log_entry_exit
    def validate_hg_details(self, spec):
        hg_prov = VSPHostGroupProvisioner(self.connection_info)

        def assign_hgs(hgs, input_hgs):
            hg_objects = []
            input_hgs_copy = input_hgs[:]
            for input_hg in input_hgs_copy:
                for hg in hgs.data:
                    if hg.hostGroupName == input_hg.name and hg.port == input_hg.port:
                        input_hgs.remove(input_hg)
                        hg_spec = HostgroupSpec(
                            id=hg.hostGroupId,
                            name=hg.hostGroupName,
                            port=hg.port,
                            resource_group_id=hg.resourceGroupId,
                        )
                        if input_hg.enable_preferred_path:
                            hg_spec.enable_preferred_path = (
                                input_hg.enable_preferred_path
                            )
                        hg_objects.append(hg_spec)
                        break
            return hg_objects

        if spec.primary_hostgroups:
            hgs = hg_prov.get_all_host_groups(spec.primary_storage_serial_number)
            hg_real = assign_hgs(hgs, spec.primary_hostgroups)
            if len(spec.primary_hostgroups) > 0:
                names = [hg.name for hg in spec.primary_hostgroups]
                err_msg = GADPairValidateMSG.PRIMARY_HG_NOT_FOUND.value.format(names)
                logger.writeError(err_msg)
                raise ValueError(err_msg)
            spec.primary_hostgroups = hg_real

        if spec.secondary_hostgroups:
            hgs = hg_prov.get_all_host_groups(spec.secondary_storage_serial_number)
            real_sec_hg = assign_hgs(hgs, spec.secondary_hostgroups)
            if len(spec.secondary_hostgroups) > 0:
                names = [hg.name for hg in spec.secondary_hostgroups]
                err_msg = GADPairValidateMSG.SEC_HG_NOT_FOUND.value.format(names)
                logger.writeError(err_msg)
                raise ValueError(err_msg)
            spec.secondary_hostgroups = real_sec_hg

    def get_copypair_dict_one(self, pairs, volume_id):
        logger.writeDebug("PROV::pairs={}", pairs)
        for pair in pairs:
            logger.writeDebug("PROV::pair={}", pair)
            copyPairs = pair.get("copyPairs", None)
            if copyPairs and len(copyPairs) > 0:
                for copyPair in copyPairs:
                    if copyPair["pvolLdevId"] == volume_id:
                        # just return the first one for now
                        logger.writeDebug("PROV::copyPair={}", copyPair)
                        return copyPair

    def get_copypair_one(self, pairs, volume_id):
        logger.writeDebug("PROV::pairs={}", pairs)
        logger.writeDebug("PROV::volume_id={}", volume_id)
        if pairs is None:
            return

        if isinstance(pairs, list):
            for copyPair in pairs:
                # expect DirectCopyPairInfo here
                if copyPair.pvolLdevId == volume_id:
                    # just return the first one for now
                    return copyPair.to_dict()

        if isinstance(pairs, DirectSpecificCopyGroupInfo):
            copyPairs = pairs.copyPairs
            if copyPairs and len(copyPairs) > 0:
                for copyPair in copyPairs:
                    if copyPair.pvolLdevId == volume_id:
                        # just return the first one for now
                        logger.writeDebug("PROV::copyPair={}", copyPair)
                        return copyPair.to_dict()

    def get_copypair_one_data(self, pairs, volume_id):
        logger.writeDebug("PROV::pairs={}", pairs)
        if pairs is None:
            return
        for pair in pairs.data:
            logger.writeDebug("PROV::pair={}", pair)
            copyPairs = pair.copyPairs
            if copyPairs and len(copyPairs) > 0:
                for copyPair in copyPairs:
                    if copyPair.pvolLdevId == volume_id:
                        # just return the first one for now
                        logger.writeDebug("PROV::copyPair={}", copyPair)
                        return copyPair.to_dict()

    @log_entry_exit
    def get_copy_group_list(self):
        return self.cg_gw.get_copy_group_list()

    @log_entry_exit
    def get_gad_pair_by_pvol_id(self, spec, volume_id):
        logger.writeDebug("PROV:215 self.connection_type={}", self.connection_type)
        if self.connection_type == "direct":
            #  sng1104 - use copy group, get_all_copy_pairs_by_copygroup_name
            # pairs = self.cg_gw.get_all_copy_pairs_by_copygroup_name(spec)
            pairs = self.cg_gw.get_all_copy_pairs(spec)
            return self.get_copypair_one(pairs, volume_id)
        else:
            pairs = self.get_all_gad_pairs(spec)
            for pair in pairs.data:
                if pair.primaryVolumeId == volume_id:
                    return pair

    @log_entry_exit
    def get_gad_pair_by_svol_id(self, spec, volume_id):
        logger.writeDebug("PROV:215 self.connection_type={}", self.connection_type)
        if self.connection_type == "direct":
            return
        else:
            pairs = self.get_all_gad_pairs(spec)
            for pair in pairs.data:
                logger.writeDebug("PROV:215 pair={}", pair)
                if int(pair.secondaryVolumeId) == int(volume_id):
                    return pair

    @log_entry_exit
    def get_all_gad_pairs(self, spec):
        # DIRECT should use gad_pair_facts cg_gw
        pairs = self.gateway.get_all_gad_pairs(spec)
        return pairs

    @log_entry_exit
    def get_gad_pair_by_id(self, gad_pair_id):

        #  don't expect DIRECT to call this one, it goes thru CG

        # TODO - spec is not needed for gateway, clean up the gateway layer later
        spec = None
        pairs = self.get_all_gad_pairs(spec)
        for pair in pairs.data:
            if self.connection_type == "direct":
                if pair.ldevId == gad_pair_id:
                    return pair
            else:
                if (pair.resourceId == gad_pair_id) or (
                    pair.primaryVolumeId == gad_pair_id
                ):
                    return pair

    @log_entry_exit
    def get_gad_pair_by_svol_id_gw(self, gad_pair_id):

        #  don't expect DIRECT to call this one, it goes thru CG

        # TODO - spec is not needed for gateway, clean up the gateway layer later
        spec = None
        pairs = self.get_all_gad_pairs(spec)
        for pair in pairs.data:
            if self.connection_type == "direct":
                if pair.ldevId == gad_pair_id:
                    return pair
            else:
                if (pair.resourceId == gad_pair_id) or (
                    pair.secondaryVolumeId == gad_pair_id
                ):
                    return pair

    @log_entry_exit
    def delete_gad_pair(self, spec, gad_pair):
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            if gad_pair.status == PairStatus.PAIR:
                self.gateway.delete_gad_pair(None, gad_pair.resourceId)
            else:
                return GADPairValidateMSG.DELETE_GAD_FAIL_SPLIT_GW.value
        else:
            logger.writeDebug(f"PROV:gad_pair:gad_pair: {gad_pair}")
            # logger.writeDebug(f"PROV:gad_pair:pvolStatus: {gad_pair["pvolStatus"]}")
            if gad_pair["pvolStatus"] == PairStatus.PSUS:
                self.gateway.delete_gad_pair(spec, gad_pair["remoteMirrorCopyPairId"])
            else:
                return GADPairValidateMSG.DELETE_GAD_FAIL_SPLIT_DIRECT.value

        self.connection_info.changed = True
        return GADPairValidateMSG.DELETE_GAD_PAIR_SUCCESS.value

    @log_entry_exit
    def swap_resync_gad_pair(self, spec=None, gad_pair=None):
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            if gad_pair.status == PairStatus.PAIR:
                # already
                return gad_pair
            if gad_pair.consistencyGroupId != -1:
                msg = (
                    GADFailedMsg.PAIR_SWAP_RESYNC_FAILED.value
                    + GADPairValidateMSG.NO_SWAP_SPLIT_WITH_CTG.value
                )
                return msg

            # sng20241218 - swap here for now until operator rework is done

            logger.writeDebug(f"PV:sng20241218 507: spec=  {spec}")
            device_id = UAIGResourceID().storage_resourceId(
                spec.secondary_storage_serial_number
            )
            self.gateway.resource_id = device_id
            logger.writeDebug(f"PV:sng20241218 507: device_id=  {device_id}")

            # fetch the pair to get the resourceId
            logger.writeDebug(f"PV:sng20241218 507: gad_pair=  {gad_pair}")
            gad_pair = self.get_gad_pair_by_svol_id(spec, gad_pair.secondaryVolumeId)
            logger.writeDebug(f"PV:sng20241218 507: gad_pair=  {gad_pair}")
            if gad_pair is None:
                err_msg = (
                    GADFailedMsg.PAIR_SWAP_RESYNC_FAILED.value
                    + GADPairValidateMSG.GAD_PAIR_NOT_FOUND_SIMPLE.value
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)

            resourceId = self.gateway.swap_resync_gad_pair(gad_pair.resourceId)
            logger.writeDebug(f"PV:sng20241218 507: resourceId=  {resourceId}")
            self.connection_info.changed = True
            # if you don't wait long enough, you may not see the swapped pair
            time.sleep(10)

            svol = gad_pair.secondaryVolumeId
            pair = self.get_gad_pair_by_pvol_id(spec, svol)
            logger.writeDebug(f"PV:sng20241218 507: gad_pair=  {pair}")

            if pair is None:
                pair = gad_pair

            # the resourceId from the call is the old one,
            # after the swap, there will be a new resourceId
            # so this call would fail
            # gad_pair = self.get_gad_pair_by_id(resourceId)
            # logger.writeDebug(f"PV:sng20241218 507: gad_pair=  {gad_pair}")

            return pair

        else:
            spec.secondary_storage_serial_number = self.gateway.get_secondary_serial(
                spec
            )
            swap_pair_id = self.gateway.swap_resync_gad_pair(spec)
            pair_id = swap_pair_id
            #  don't swap for GAD
            # pair_id = self.gateway.get_pair_id_from_swap_pair_id(swap_pair_id, spec.secondary_connection_info)
            # logger.writeDebug(f"PV: swap_pair_id = {swap_pair_id} pair_id = {pair_id}")
            pair = self.cg_gw.get_one_copy_pair_by_id(
                pair_id, spec.secondary_connection_info
            )

            #  sng20241123 make the call so the copy group is save to global
            #  we need it for get_other_attributes()
            cg = self.cg_gw.get_copy_group_by_name(spec)
            logger.writeDebug(f"PV: 362 cg = {cg}")

            self.connection_info.changed = True
            return pair

    @log_entry_exit
    def swap_split_gad_pair(self, spec=None, gad_pair=None):
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            if gad_pair.status == PairStatus.SSWS:
                # already
                return gad_pair
            if gad_pair.consistencyGroupId != -1:
                return GADPairValidateMSG.NO_SWAP_SPLIT_WITH_CTG.value

            # sng20241218 - swap here for now until operator rework is done
            logger.writeDebug(f"PV:sng20241218 507: spec=  {spec}")
            device_id = UAIGResourceID().storage_resourceId(
                spec.secondary_storage_serial_number
            )
            self.gateway.resource_id = device_id
            logger.writeDebug(f"PV:sng20241218 507: device_id=  {device_id}")

            # fetch the pair to get the resourceId
            logger.writeDebug(f"PV:sng20241218 507: gad_pair=  {gad_pair}")
            gad_pair = self.get_gad_pair_by_svol_id(spec, gad_pair.secondaryVolumeId)
            logger.writeDebug(f"PV:sng20241218 507: gad_pair=  {gad_pair}")
            if gad_pair is None:
                err_msg = (
                    GADFailedMsg.PAIR_SWAP_SPLIT_FAILED.value
                    + GADPairValidateMSG.GAD_PAIR_NOT_FOUND_SIMPLE.value
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)

            self.gateway.swap_split_gad_pair(gad_pair.resourceId)
            self.connection_info.changed = True
            time.sleep(5)

            pvol = gad_pair.primaryVolumeId

            # svol = gad_pair.secondaryVolumeId
            # gad_pair = self.get_gad_pair_by_pvol_id(spec, svol)
            # logger.writeDebug(f"PV:sng20241218 507: gad_pair=  {gad_pair}")
            # gad_pair = self.get_gad_pair_by_svol_id(spec, pvol)
            # logger.writeDebug(f"PV:sng20241218 507: gad_pair=  {gad_pair}")
            # gad_pair = self.get_gad_pair_by_svol_id(spec, svol)
            # logger.writeDebug(f"PV:sng20241218 507: gad_pair=  {gad_pair}")

            gad_pair = self.get_gad_pair_by_pvol_id(spec, pvol)
            logger.writeDebug(f"PV:sng20241218 507: gad_pair=  {gad_pair}")
            return gad_pair
        else:
            spec.secondary_storage_serial_number = self.gateway.get_secondary_serial(
                spec
            )
            tc = self.cg_gw.get_gad_pair_by_copy_group_and_copy_pair_name(spec)
            logger.writeDebug(f"PV: 362 tc = {tc}")

            if tc is None:
                return "GAD pair is not found"

            # sng20241126 swap_split_gad_pair consistencyGroupId check
            if tc.consistencyGroupId is not None:
                if (
                    isinstance(tc.consistencyGroupId, int)
                    and tc.consistencyGroupId != "-1"
                ):
                    return GADPairValidateMSG.NO_SWAP_SPLIT_WITH_CTG.value
                if tc.consistencyGroupId != "-1" and tc.consistencyGroupId != "":
                    return GADPairValidateMSG.NO_SWAP_SPLIT_WITH_CTG.value

            swap_pair_id = self.gateway.swap_split_gad_pair(spec)
            pair_id = swap_pair_id
            #  don't swap for GAD
            # pair_id = self.gateway.get_pair_id_from_swap_pair_id(swap_pair_id, spec.secondary_connection_info)

            pair = self.cg_gw.get_one_copy_pair_by_id(
                pair_id, spec.secondary_connection_info
            )
            logger.writeDebug(f"PV: 362 pair = {pair}")
            #  here the pair is DirectCopyPairInfo with
            #   remoteMirrorCopyPairId='A34000810050,test_GAD2,test_GAD2S_,test_GAD2P_,test_GAD_pair1'

            #  sng20241123 make the call so the copy group is save to global
            #  we need it for get_other_attributes()
            cg = self.cg_gw.get_copy_group_by_name(spec)
            logger.writeDebug(f"PV: 362 cg = {cg}")

            self.connection_info.changed = True
            return pair

    #  sng20241115 split_gad_pair
    @log_entry_exit
    def split_gad_pair(self, spec=None, gad_pair=None):

        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            if gad_pair.status == PairStatus.PSUS:
                # already in split state
                return gad_pair
            unused = self.gateway.split_gad_pair(gad_pair.resourceId)
            self.connection_info.changed = True
            time.sleep(5)
            return self.get_gad_pair_by_id(gad_pair.primaryVolumeId)

        #  connection_type is DIRECT

        # common code is checking it?
        # if gad_pair["pvolStatus"] == PairStatus.PSUS:
        #     # already in split state
        #     return gad_pair

        # tc = None
        # if spec.primary_volume_id:
        #     primary_volume_id = spec.primary_volume_id
        #     tc = self.get_gad_for_primary_vol_id(spec, primary_volume_id)
        #     if tc is None:
        #         raise ValueError(GADPairValidateMSG.NO_PAIR_FOR_PRIMARY_VOLUME_ID.value.format(primary_volume_id))
        #     if tc.pvolStatus == 'PSUE' :
        #         return tc

        spec.secondary_storage_serial_number = self.gateway.get_secondary_serial(spec)
        tc = self.cg_gw.get_gad_pair_by_copy_group_and_copy_pair_name(spec)
        logger.writeDebug(f"PV:: 331 tc=  {tc}")
        if tc.pvolStatus == PairStatus.PSUS:
            # already in split state
            return tc

        if tc is not None and tc.svolStatus == "SSWS":
            swap_pair_id = self.gateway.swap_split_gad_pair(spec, "PSUS")
            pair_id = self.gateway.get_pair_id_from_swap_pair_id(
                swap_pair_id, spec.secondary_connection_info
            )
            logger.writeDebug(f"PV: swap_pair_id = {swap_pair_id} pair_id = {pair_id}")
            pair = self.cg_gw.get_one_copy_pair_by_id(
                pair_id, spec.secondary_connection_info
            )
            self.connection_info.changed = True
            return pair
        else:
            pair_id = self.gateway.split_gad_pair(spec)
            logger.writeDebug(f"PV:: pair_id=  {pair_id}")
            pair = self.cg_gw.get_one_copy_pair_by_id(
                pair_id, spec.secondary_connection_info
            )
            self.connection_info.changed = True
            return pair

    @log_entry_exit
    def get_gad_for_primary_vol_id(self, spec, primary_vol_id):
        all_tc_pairs = self.get_all_gad_pairs_direct(spec=spec)
        logger.writeDebug(
            f"PV:: get_gad_for_primary_vol_id all_tc_pairs=  {all_tc_pairs}"
        )

        #  sng20241115 isinstance DirectCopyPairInfo
        if isinstance(all_tc_pairs, DirectCopyPairInfo):
            tc = all_tc_pairs
            if tc.pvolLdevId == primary_vol_id:
                return tc

        for tc in all_tc_pairs.data:
            if hasattr(tc, "ldevId"):
                if tc.ldevId == primary_vol_id:
                    return tc
            if hasattr(tc, "primaryVolumeId"):
                if tc.primaryVolumeId == primary_vol_id:
                    return tc

        return None

    #  sng20241115 resync_gad_pair
    @log_entry_exit
    def resync_gad_pair(self, spec=None, gad_pair=None):
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            if gad_pair.status == PairStatus.PAIR:
                # already in resync state
                return gad_pair
            unused = self.gateway.resync_gad_pair(gad_pair.resourceId)
            self.connection_info.changed = True
            return self.get_gad_pair_by_id(gad_pair.primaryVolumeId)

        #  connection_type is DIRECT

        # common code is checking it?
        # if gad_pair["pvolStatus"] == PairStatus.PAIR:
        #     # already in resync state
        #     return gad_pair

        # tc = None
        # if spec.primary_volume_id:
        #     primary_volume_id = spec.primary_volume_id
        #     tc = self.get_gad_for_primary_vol_id(spec, primary_volume_id)
        #     if tc is None:
        #         raise ValueError(GADPairValidateMSG.NO_PAIR_FOR_PRIMARY_VOLUME_ID.value.format(primary_volume_id))
        #     logger.writeDebug(f"PROV:resync_gad_pair:tc : {tc}")
        #     if tc.pvolStatus == 'PAIR' :
        #         #  sng20241115 resync_gad_pair already in PAIR, tc is a CG
        #         return tc

        spec.secondary_storage_serial_number = self.gateway.get_secondary_serial(spec)
        tc = self.cg_gw.get_gad_pair_by_copy_group_and_copy_pair_name(spec)
        if tc.pvolStatus == PairStatus.PAIR:
            # already in pair state
            return tc

        pair_id = self.gateway.resync_gad_pair(spec)
        logger.writeDebug(f"PV: pair_id=  {pair_id}")
        pair = self.cg_gw.get_one_copy_pair_by_id(
            pair_id, spec.secondary_connection_info
        )
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
    def resize_gad_pair(self, spec=None):
        gad = None
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            if spec.primary_volume_id:
                primary_volume_id = spec.primary_volume_id
                device_id = UAIGResourceID().storage_resourceId(self.serial)
                ldev_resource_id = UAIGResourceID().ldev_resourceId(
                    self.serial, spec.primary_volume_id
                )
                pvol_data = self.vol_gw.get_volume_by_id_v2(device_id, ldev_resource_id)
                logger.writeDebug("PV:resize_gad_pair: zmpvol= ", pvol_data)
                gad = self.get_gad_pair_by_pvol_id(spec, primary_volume_id)
                if gad is None:
                    err_msg = (
                        GADFailedMsg.PAIR_RESIZE_FAILED.value
                        + VSPTrueCopyValidateMsg.PRIMARY_VOLUME_ID_DOES_NOT_EXIST.value.format(
                            primary_volume_id
                        )
                    )
                    logger.writeError(err_msg)
                    raise ValueError(err_msg)
                svol_device_id = UAIGResourceID().storage_resourceId(
                    spec.secondary_storage_serial_number
                )
                svol_ldev_resource_id = UAIGResourceID().ldev_resourceId(
                    spec.secondary_storage_serial_number, gad.secondaryVolumeId
                )
                svol_data = self.vol_gw.get_volume_by_id_v2(
                    svol_device_id, svol_ldev_resource_id
                )
                # svol_data = self.vol_gw.get_volume_by_id_v2(svol_device_id, svol_ldev_resource_id)
                if pvol_data.totalCapacity == convert_decimal_size_to_bytes(
                    spec.new_volume_size, 1
                ):
                    logger.writeDebug("PV:resize_gad_pair: Resize not needed")
                    pair = camel_dict_to_snake_case(gad.to_dict())
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
                    err_msg = (
                        GADFailedMsg.PAIR_RESIZE_FAILED.value
                        + VSPTrueCopyValidateMsg.REDUCE_VOLUME_SIZE_NOT_SUPPORTED.value
                    )
                    logger.writeError(f"Exception in resize_gad_pair. {err_msg}")
                    raise ValueError(err_msg)

                if gad is not None:
                    pair_id = self.gateway.resize_gad_pair(gad, spec)
                    logger.writeDebug(f"PV:resize_gad_pair: pair_id=  {pair_id}")
                updated_pvol_data = self.vol_gw.get_volume_by_id_v2(
                    device_id, ldev_resource_id
                )
                updated_svol_data = self.vol_gw.get_volume_by_id_v2(
                    svol_device_id, svol_ldev_resource_id
                )
                pair = camel_dict_to_snake_case(gad.to_dict())
                pair["primary_volume_size"] = convert_block_capacity(
                    updated_pvol_data.totalCapacity, 1
                )
                pair["secondary_volume_size"] = convert_block_capacity(
                    updated_svol_data.totalCapacity, 1
                )
                self.connection_info.changed = True
                return pair
        else:
            pair_id = None
            if spec.copy_group_name and spec.copy_pair_name:
                tc = self.cg_gw.get_remote_pairs_by_copy_group_and_copy_pair_name(spec)
                logger.writeDebug(f"PV:resize_gad_pair: tc=  {tc}")
                if tc is not None and len(tc) > 0:
                    pvol_id = tc[0].pvolLdevId
                    svol_id = tc[0].svolLdevId
                    pvol_data = self.vol_gw.get_volume_by_id(pvol_id)
                    svol_data = self.vol_gw.get_volume_by_id(svol_id)
                    resize_needed = self.is_resize_needed(pvol_data, spec)
                    if resize_needed is False:
                        err_msg = (
                            GADFailedMsg.PAIR_RESIZE_FAILED.value
                            + VSPTrueCopyValidateMsg.REDUCE_VOLUME_SIZE_NOT_SUPPORTED.value
                        )
                        logger.writeError(err_msg)
                        raise ValueError(err_msg)
                    else:
                        pair_id = self.gateway.resize_gad_pair(tc[0], spec)
                        logger.writeDebug(
                            f"resize_true_copy_copy_pair: pair_id=  {pair_id}"
                        )
                        pair = self.cg_gw.get_one_copy_pair_by_id(
                            tc[0].remoteMirrorCopyPairId, spec.secondary_connection_info
                        )
                        self.connection_info.changed = True
                        return pair
                else:
                    err_msg = (
                        GADFailedMsg.PAIR_RESIZE_FAILED.value
                        + GADPairValidateMSG.GAD_PAIR_NOT_FOUND.value.format(
                            spec.copy_pair_name
                        )
                    )
                    logger.writeError(err_msg)
                    raise ValueError(err_msg)

    @log_entry_exit
    def gad_pair_facts(self, gad_pair_facts_spec=None):
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            if (
                gad_pair_facts_spec is not None
                and gad_pair_facts_spec.primary_volume_id is not None
            ):
                return self.get_gad_pair_by_id(gad_pair_facts_spec.primary_volume_id)
            return self.gateway.get_all_gad_pairs(gad_pair_facts_spec)
        else:
            # sng20241115 - prov.gad_pair_facts.direct
            spec = gad_pair_facts_spec
            # logger.writeDebug("sng20241115 get_all_gad_pairs_direct.secondary_connection_info ={}", spec.secondary_connection_info)

            tc_pairs = self.get_all_gad_pairs_direct(spec=spec)

            logger.writeDebug(f"PV:: pairs=  {tc_pairs}")
            if tc_pairs is None:
                return tc_pairs
            if spec is None:
                return tc_pairs
            else:
                ret_tc_pairs = self.apply_filters(tc_pairs, spec)
                return VspGadPairsInfo(data=ret_tc_pairs)

    # sng20241115 - prov.get_all_gad_pairs_direct
    @log_entry_exit
    def get_all_gad_pairs_direct(self, serial=None, spec=None):
        if serial is None:
            serial = self.serial
        if spec is None:
            ret_list = self.gateway.get_all_gad_pairs(serial)
            logger.writeDebug(
                f"PROV:get_all_gad_pairs_direct:ret_list= {ret_list} serial = {serial}"
            )
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
        pairs = self.get_gad_copypairs(tc_pairs)

        logger.writeDebug("sng20241115 spec={}", spec)
        result = pairs
        if not spec.primary_volume_id and not spec.secondary_volume_id:
            return result

        if pairs and spec.primary_volume_id:
            result = []
            for pair in pairs:
                logger.writeDebug("sng20241115 pair={}", pair)
                if pair.pvolLdevId != spec.primary_volume_id:
                    continue
                result.append(pair)
            return result

        if pairs and spec.secondary_volume_id:
            result = []
            for pair in pairs:
                logger.writeDebug("sng20241115 pair={}", pair)
                if pair.svolLdevId != spec.secondary_volume_id:
                    continue
                result.append(pair)
            return result

        return result

    @log_entry_exit
    def apply_filter_pvol(self, tc_pairs, primary_vol_id):

        if not isinstance(tc_pairs, list):
            tc_pairs = [tc_pairs]

        ret_val = []
        for tc in tc_pairs:
            if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
                if (
                    tc.primaryVolumeId == primary_vol_id
                    or tc.secondaryVolumeId == primary_vol_id
                ):
                    ret_val.append(tc)
            else:
                logger.writeDebug("sng20241115 pair={}", tc)
                tc = self.get_gad_pair_by_pvol_new(
                    self.get_gad_copypairs(tc), primary_vol_id
                )
                # if tc.ldevId == primary_vol_id or tc.remoteLdevId == primary_vol_id:
                if tc:
                    ret_val.append(tc)
        return ret_val

    # sng20241115 pair: DirectSpecificCopyGroupInfo or list
    @log_entry_exit
    def get_gad_copypairs(self, pair):

        logger.writeDebug("sng20241115 :pair={}", pair)

        if isinstance(pair, list):
            return self.get_gad_copypairs_from_list(pair)
        if isinstance(pair, DirectSpecificCopyGroupInfoList):
            return self.get_gad_copypairs_from_list(pair.data_to_list())

        gad_pairs = []

        if isinstance(pair, DirectCopyPairInfo):
            if (
                pair.replicationType == "GAD"
                and pair.svolStatus != "SMPL"
                # commented by ansible sanity test
                # and copyPair.pvolStatus != "SMPL"
            ):
                gad_pairs.append(pair)
                return gad_pairs

        copyPairs = pair.copyPairs
        if copyPairs is None:
            return

        for copyPair in copyPairs:
            # sng20241115 change replicationType here to use other types for testing
            if (
                copyPair.replicationType == "GAD"
                and copyPair.svolStatus != "SMPL"
                and copyPair.pvolStatus != "SMPL"
            ):
                gad_pairs.append(copyPair)

        return gad_pairs

    @log_entry_exit
    def get_gad_copypairs_from_list(self, cgList):

        gad_pairs = []

        logger.writeDebug("sng20241115 :cg={}", cgList)
        if isinstance(cgList, dict):
            return self.get_gad_copypairs_from_dict(cgList, gad_pairs)

        for cg in cgList:
            if cg is None:
                continue

            logger.writeDebug("sng20241115 :cg={}", cg)

            if isinstance(cg, dict):
                gad_pairs = self.get_gad_copypairs_from_dict(cg, gad_pairs)
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
                if (
                    copyPair.replicationType == "GAD"
                    and copyPair.svolStatus != "SMPL"
                    and copyPair.pvolStatus != "SMPL"
                ):
                    gad_pairs.append(copyPair)

        return gad_pairs

    @log_entry_exit
    def get_gad_copypairs_from_dict(self, cgs, gad_pairs):

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
                        if (
                            copyPair["replicationType"] == "GAD"
                            and copyPair["svolStatus"] != "SMPL"
                            and copyPair.pvolStatus != "SMPL"
                        ):
                            gad_pairs.append(copyPair)
                else:
                    # handle copyPair class objects
                    for copyPair in copyPairs:
                        if isinstance(copyPair, dict):
                            if (
                                copyPair["replicationType"] == "GAD"
                                and copyPair["svolStatus"] != "SMPL"
                                and copyPair.pvolStatus != "SMPL"
                            ):
                                gad_pairs.append(copyPair)
                        else:
                            if (
                                copyPair.replicationType == "GAD"
                                and copyPair.svolStatus != "SMPL"
                                and copyPair.pvolStatus != "SMPL"
                            ):
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
                    if (
                        copyPair.replicationType == "GAD"
                        and copyPair.svolStatus != "SMPL"
                        and copyPair.pvolStatus != "SMPL"
                    ):
                        gad_pairs.append(copyPair)

        return gad_pairs

    # sng20241115 pairs: []DirectCopyPairInfo
    def get_gad_pair_by_pvol_new(self, copyPairs, volume_id):
        logger.writeDebug("sng20241115 :copyPairs={}", copyPairs)
        if copyPairs is None:
            return
        if not isinstance(copyPairs, list):
            copyPairs = [copyPairs]
        for copyPair in copyPairs:
            if isinstance(copyPair, dict):
                if copyPair["pvolLdevId"] == volume_id:
                    # just return the first one for now
                    logger.writeDebug("sng20241115 found copyPair={}", copyPair)
                    return copyPair
            else:
                if copyPair.pvolLdevId == volume_id:
                    # just return the first one for now
                    logger.writeDebug("sng20241115 found copyPair={}", copyPair)
                    return copyPair

    @log_entry_exit
    def apply_filter_svol(self, tc_pairs, secondary_vol_id):
        ret_val = []

        for tc in tc_pairs:
            if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
                if (
                    tc.secondaryVolumeId == secondary_vol_id
                    or tc.primaryVolumeId == secondary_vol_id
                ):
                    ret_val.append(tc)
            else:
                if tc.remoteLdevId == secondary_vol_id or tc.ldevId == secondary_vol_id:
                    ret_val.append(tc)
        return ret_val

    @log_entry_exit
    def gad_pair_facts_v1(self, gad_pair_facts_spec):
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            if (
                gad_pair_facts_spec is not None
                and gad_pair_facts_spec.primary_volume_id is not None
            ):
                return self.get_gad_pair_by_id(gad_pair_facts_spec.primary_volume_id)
            return self.gateway.get_all_gad_pairs(gad_pair_facts_spec)
        else:
            # sng1104 - GET FACTS, formatting is in the reconciler layer
            # do pegasus switch here
            # invalid code , commented by ansible sanity test
            # if False:
            #     # faster but missing some info and not for pegasus
            #     pairs = self.gateway.get_all_gad_pairs(gad_pair_facts_spec)
            # else:
            #     # pegasus has to use copy group, slower
            pairs = self.cg_gw.get_all_copy_pairs(gad_pair_facts_spec)
            return pairs

    @log_entry_exit
    def get_secondary_storage_system_serial(self, serial_number):
        system = self.storage_prov.get_storage_ucp_system(serial_number)
        if not system:
            err_msg = GADPairValidateMSG.SECONDARY_SYSTEM_NT_FOUND.value
            logger.writeError(err_msg)
            raise ValueError(err_msg)
        elif system.ucpSystems[0] == CommonConstants.UCP_SERIAL:
            pass
            # raise ValueError(GADPairValidateMSG.SECONDARy_SYSTEM_CANNOT_BE_SAME.value)
        return system.ucpSystems[0]

    @log_entry_exit
    def check_ucp_system(self, serial):
        serial, resource_id = self.storage_prov.check_ucp_system(serial)
        self.serial = serial
        self.gateway.resource_id = resource_id
        self.gateway.serial = serial
        return serial

    @log_entry_exit
    def check_storage_in_ucpsystem(self) -> bool:
        return self.gateway.check_storage_in_ucpsystem()

    @log_entry_exit
    def is_out_of_band(self):
        return self.config_gw.is_out_of_band()

    @log_entry_exit
    def get_resource_group_by_id(self, resourceGroupId):
        return self.rg_gateway.get_resource_group_by_id(resourceGroupId)

    @log_entry_exit
    def get_volume_by_id(self, primary_volume_id):

        volume = self.vol_gw.get_volume_by_id(primary_volume_id)
        # return vol_gw.get_volume_by_id(device_id, primary_volume_id)
        logger.writeDebug(f"PROV:get_volume_by_id:volume: {volume}")

        return volume

    @log_entry_exit
    def get_volume_by_id_v2(self, storage_id, volume_id):
        volume = self.vol_gw.get_volume_by_id_v2(storage_id, volume_id)
        # return vol_gw.get_volume_by_id(device_id, primary_volume_id)
        logger.writeDebug(f"PROV:get_volume_by_id_v2:volume: {volume}")

        return volume


class RemoteReplicationHelperForSVol:

    DEFAULT_HOSTGROUP_NAME = "ANSIBLE_DEFAULT_HOSTGROUP"
    DEFAULT_HOST_MODE = "VMWARE_EXTENSION"  # "STANDARD"

    #  sng1104 - RemoteReplicationHelperForSVol
    def __init__(self, connection_info, serial):
        self.rg_gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_RESOURCE_GROUP
        )
        self.hg_gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_HOST_GROUP
        )
        self.sp_gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.STORAGE_PORT
        )
        self.vol_gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_VOLUME
        )
        self.connection_info = connection_info
        self.serial = serial
        self.hg_gateway.set_serial(serial)
        self.sp_gateway.set_serial(serial)
        self.vol_gateway.set_serial(serial)

    @log_entry_exit
    def get_resource_group_by_id(self, resourceGroupId):
        return self.rg_gateway.get_resource_group_by_id(resourceGroupId)

    @log_entry_exit
    def get_vsm_all(self):
        return self.rg_gateway.get_vsm_all()

    @log_entry_exit
    def get_volume_by_id(self, id):
        vol = self.vol_gateway.get_volume_by_id(id)
        return vol

    @log_entry_exit
    def delete_volume(self, secondary_vol_id, spec):
        port_id = spec.secondary_hostgroups[0].port
        hg_name = spec.secondary_hostgroups[0].name
        host_group_info = self.hg_gateway.get_one_host_group(port_id, hg_name)
        if host_group_info.data is not None:
            logger.writeDebug(
                "PROV:delete_volume:host_group_info = {}", host_group_info
            )
            hg_number = host_group_info.data.hostGroupId
            lun_paths = host_group_info.data.lunPaths
            lun_id = None
            for lun_path in lun_paths:
                if int(lun_path.ldevId) == int(secondary_vol_id):
                    lun_id = int(lun_path.lunId)
                    logger.writeDebug("PROV:delete_volume:found lun_id = {}", lun_id)
                    break
            if lun_id is not None:
                port = {
                    "portId": port_id,
                    "hostGroupNumber": hg_number,
                    "lun": lun_id,
                }
                logger.writeDebug("PROV:delete_volume:port = {}", port)
                self.vol_gateway.delete_lun_path(port)

        volume = self.vol_gateway.get_volume_by_id(secondary_vol_id)
        force_execute = (
            True
            if volume.dataReductionMode
            and volume.dataReductionMode.lower() != VolumePayloadConst.DISABLED
            else None
        )
        try:
            self.vol_gateway.delete_volume(secondary_vol_id, force_execute)
            self.connection_info.changed = False
            return
        except Exception as e:
            err_msg = GADFailedMsg.SEC_VOLUME_DELETE_FAILED.value + str(e)
            logger.writeError(err_msg)
            raise ValueError(err_msg)

    @log_entry_exit
    def select_secondary_volume_id(self, pvol_id):
        free_vol_info = self.vol_gateway.get_free_ldev_matching_pvol(pvol_id)
        logger.writeDebug(
            "PROV:select_secondary_volume_id:free_vol_info = {}", free_vol_info
        )
        return free_vol_info.data[0].ldevId

    @log_entry_exit
    def get_secondary_volume_id(self, vol_info, spec):

        # sng1104 GAD Work Flow: provisioning svol for GAD pair creation

        logger.writeDebug("PROV:813:primary_volume = {}", vol_info)

        # Fail early, save time
        # Before creating the secondary volume check if secondary hostgroup exists
        host_group = self.get_secondary_hostgroup(spec.secondary_hostgroups)
        if host_group is None:
            err_msg = VSPTrueCopyValidateMsg.NO_REMOTE_HG_FOUND.value.format(
                spec.secondary_hostgroups[0].name, spec.secondary_hostgroups[0].port
            )
            logger.writeError(err_msg)
            raise ValueError(err_msg)

        svol_id = self.select_secondary_volume_id(vol_info.ldevId)
        secondary_pool_id = spec.secondary_pool_id
        sec_vol_spec = CreateVolumeSpec()
        sec_vol_spec.pool_id = secondary_pool_id

        sec_vol_spec.size = self.get_size_from_byte_format_capacity(
            vol_info.byteFormatCapacity
        )
        sec_vol_spec.capacity_saving = vol_info.dataReductionMode
        sec_vol_spec.ldev_id = svol_id

        sec_vol_id = self.vol_gateway.create_volume(sec_vol_spec)

        # per UCA-2281
        if vol_info.label is not None and vol_info.label != "":
            sec_vol_name = vol_info.label
        else:
            sec_vol_name = f"{DEFAULT_NAME_PREFIX}-{vol_info.ldevId}"

        # the name change is done in the update_volume method
        logger.writeDebug("PROV:1221:sec_vol_name = {}", sec_vol_name)

        # sng20241127 - set svol label/name and set_alua_mode
        set_alua_mode = None
        if spec.set_alua_mode:
            set_alua_mode = spec.set_alua_mode

        try:
            logger.writeDebug("PROV:813:sec_vol_name = {}", sec_vol_name)
            logger.writeDebug("PROV:813:set_alua_mode = {}", set_alua_mode)
            self.vol_gateway.change_volume_settings(
                sec_vol_id, sec_vol_name, set_alua_mode
            )

            # verify the svol set label and set_alua_mode
            vol_info = self.vol_gateway.get_volume_by_id(sec_vol_id)
            logger.writeDebug("PROV:813:sec_vol_id = {}", sec_vol_id)
            logger.writeDebug("PROV:813:sec_vol = {}", vol_info)
            logger.writeDebug(
                "PROV:813:sec_vol isAluaEnabled= {}", vol_info.isAluaEnabled
            )

            self.vol_gateway.unassign_vldev(sec_vol_id, sec_vol_id)
            logger.writeDebug(
                "PROV:get_secondary_volume_id:sec_vol_id = {}", sec_vol_id
            )
            logger.writeDebug(
                "PROV:get_secondary_volume_id:sec_vol_spec = {}", sec_vol_spec
            )

            #  sng1104 - TODO enable_preferred_path goes here if needed?
            # hg_info = self.parse_hostgroup(host_group)
            # logger.writeDebug("PROV:get_secondary_volume_id:hg_info = {}", hg_info)

            #  sng1104 - on the 2nd storage, find the hg.RG, move lun to RG
            add_resource_spec = VSPResourceGroupSpec()
            add_resource_spec.ldevs = [int(sec_vol_id)]
            resourceGroupId = host_group.resourceGroupId
            logger.writeDebug(
                "PROV:get_secondary_volume_id:resourceGroupId = {}", resourceGroupId
            )
            self.rg_gateway.add_resource(resourceGroupId, add_resource_spec)

            # GAD reserved
            self.vol_gateway.assign_vldev(sec_vol_id, 65535)

            self.hg_gateway.add_luns_to_host_group(host_group, [sec_vol_id])
        except Exception as ex:
            err_msg = GADFailedMsg.SEC_VOLUME_OPERATION_FAILED.value + str(ex)
            logger.writeError(err_msg)
            # if setting the volume name fails, delete the secondary volume
            # if attaching the volume to the host group fails, delete the secondary volume
            self.delete_volume(sec_vol_id, spec)
            raise Exception(err_msg)
        return sec_vol_id

    def get_secondary_hostgroup(self, secondary_hostgroup):
        hostgroups_list = self.validate_secondary_hostgroups(secondary_hostgroup)
        logger.writeDebug(
            "PROV:get_secondary_hostgroup:hostgroups_list = {}", hostgroups_list
        )
        return hostgroups_list[0]

    @log_entry_exit
    def parse_hostgroup(self, hostgroup):
        hostgroup.port = hostgroup.portId
        return hostgroup

    @log_entry_exit
    def get_size_from_byte_format_capacity(self, byte_format):
        value = byte_format.split(" ")[0]
        unit = byte_format.split(" ")[1]
        int_value = value.split(".")[0]
        return f"{int_value}{unit}"

    def get_secondary_hostgroups_payload(self, secondary_hostgroups):
        hostgroups_list = self.validate_secondary_hostgroups(secondary_hostgroups)
        payload = self.create_secondary_hgs_payload(hostgroups_list)
        return payload

    def validate_secondary_hostgroups(self, secondary_hgs):
        logger.writeDebug("PROV:validate_secondary_hostgroups:hgs = {}", secondary_hgs)
        logger.writeDebug(
            "PROV:validate_secondary_hostgroups:connection_info = {}",
            self.connection_info,
        )

        hostgroup_list = []
        for hg in secondary_hgs:
            hostgroup = self.get_hg_by_name_port(hg.name, hg.port)
            if hostgroup is None:
                err_msg = VSPTrueCopyValidateMsg.NO_REMOTE_HG_FOUND.value.format(
                    hg.name, hg.port
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)

            if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
                if self.connection_info.subscriber_id is not None:
                    if self.connection_info.subscriber_id != hostgroup.subscriberId:
                        err_msg = VSPTrueCopyValidateMsg.HG_SUBSCRIBER_ID_MISMATCH.value.format(
                            self.connection_info.subscriber_id, hostgroup.subscriberId
                        )
                        logger.writeError(err_msg)
                        raise ValueError(err_msg)
                else:
                    if hostgroup.subscriberId is not None:
                        err_msg = (
                            VSPTrueCopyValidateMsg.NO_SUB_PROVIDED_HG_HAS_SUB.value
                        )
                        logger.writeError(err_msg)
                        raise ValueError(err_msg)

            hostgroup_list.append(hostgroup)

        logger.writeDebug(
            f"PROV:validate_secondary_hostgroups:hostgroup_list = {hostgroup_list}"
        )

        for hg in secondary_hgs:
            port = self.get_port_by_name(hg.port)
            if port is None:
                err_msg = VSPTrueCopyValidateMsg.SEC_PORT_NOT_FOUND.value.format(
                    hg.port
                )
                logger.writeError(err_msg)
                raise ValueError(err_msg)

            # if port.portInfo["portType"] != "FIBRE" or port.portInfo["mode"] != "SCSI":
            #     raise ValueError(VSPTrueCopyValidateMsg.WRONG_PORT_PROVIDED.value.format(port.resourceId, port.portInfo["portType"], port.portInfo["mode"]))
            if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
                if self.connection_info.subscriber_id is not None:
                    if self.connection_info.subscriber_id != port.subscriberId:
                        err_msg = VSPTrueCopyValidateMsg.PORT_SUBSCRIBER_ID_MISMATCH.value.format(
                            self.connection_info.subscriber_id, port.subscriberId
                        )
                        logger.writeError(err_msg)
                        raise ValueError(err_msg)
                else:
                    if port.subscriberId is not None:
                        err_msg = (
                            VSPTrueCopyValidateMsg.NO_SUB_PROVIDED_PORT_HAS_SUB.value
                        )
                        logger.writeError(err_msg)
                        raise ValueError(err_msg)

        return hostgroup_list

    @log_entry_exit
    def get_hg_by_name_port(self, name, port):
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            hgs = self.hg_gateway.get_host_groups_for_resource_id(
                UAIGResourceID().storage_resourceId(self.serial)
            )
            logger.writeDebug("PROV:get_hg_by_name_port:hgs = {}", hgs)

            for hg in hgs.data:
                if (
                    hg.hostGroupInfo["hostGroupName"] == name
                    and hg.hostGroupInfo["port"] == port
                ):
                    return hg

            return None
        else:
            hg = self.hg_gateway.get_one_host_group(port, name)
            logger.writeDebug("PROV:get_hg_by_name_port:hgs = {}", hg)
            if hg is None:
                return None
            return hg.data

    @log_entry_exit
    def get_port_by_name(self, port):
        return self.sp_gateway.get_single_storage_port(port)

    @log_entry_exit
    def create_secondary_hgs_payload(self, hgs):
        ret_list = []
        for hg in hgs:
            item = {}
            item["hostGroupID"] = hg.hostGroupInfo["hostGroupId"]
            item["name"] = hg.hostGroupInfo["hostGroupName"]
            item["port"] = hg.hostGroupInfo["port"]
            item["resourceGroupID"] = hg.hostGroupInfo["resourceGroupId"] or 0
            ret_list.append(item)
        return ret_list

    @log_entry_exit
    def get_secondary_hg_payload(self, hg):
        ret_list = []
        item = {}
        item["hostGroupID"] = hg.hostGroupInfo["hostGroupId"]
        item["name"] = hg.hostGroupInfo["hostGroupName"]
        item["port"] = hg.hostGroupInfo["port"]
        item["resourceGroupID"] = hg.hostGroupInfo["resourceGroupId"] or 0
        ret_list.append(item)
        return ret_list
