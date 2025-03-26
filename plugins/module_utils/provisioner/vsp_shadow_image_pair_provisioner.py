import time

try:
    from ..common.ansible_common import (
        log_entry_exit,
        get_size_from_byte_format_capacity,
        dicts_to_dataclass_list,
    )
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes, ConnectionTypes
    from ..common.hv_log import Log
    from ..common.vsp_constants import DEFAULT_NAME_PREFIX
    from ..model.vsp_shadow_image_pair_models import (
        VSPShadowImagePairsInfo,
        VSPShadowImagePairInfo,
    )
    from ..common.vsp_constants import VolumePayloadConst, PairStatus
    from .vsp_volume_prov import VSPVolumeProvisioner
    from .vsp_nvme_provisioner import VSPNvmeProvisioner
    from .vsp_host_group_provisioner import VSPHostGroupProvisioner
    from ..message.vsp_shadow_image_pair_msgs import VSPShadowImagePairValidateMsg
    from ..model.vsp_volume_models import CreateVolumeSpec
    from ..model.vsp_host_group_models import VSPHostGroupInfo

except ImportError:
    from common.ansible_common import (
        log_entry_exit,
        get_size_from_byte_format_capacity,
        dicts_to_dataclass_list,
    )
    from common.hv_constants import GatewayClassTypes, ConnectionTypes
    from common.hv_log import Log
    from common.vsp_constants import DEFAULT_NAME_PREFIX
    from gateway.gateway_factory import GatewayFactory
    from model.vsp_shadow_image_pair_models import (
        VSPShadowImagePairsInfo,
        VSPShadowImagePairInfo,
    )
    from .vsp_volume_prov import VSPVolumeProvisioner
    from .vsp_nvme_provisioner import VSPNvmeProvisioner
    from .vsp_host_group_provisioner import VSPHostGroupProvisioner
    from common.vsp_constants import VolumePayloadConst, PairStatus
    from message.vsp_shadow_image_pair_msgs import VSPShadowImagePairValidateMsg
    from model.vsp_volume_models import CreateVolumeSpec
    from model.vsp_host_group_models import VSPHostGroupInfo

logger = Log()


class VSPShadowImagePairProvisioner:

    def __init__(self, connection_info):
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_SHADOW_IMAGE_PAIR
        )
        self.connection_info = connection_info
        self.config_gw = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_CONFIG_MAP
        )
        if self.connection_info.connection_type == ConnectionTypes.DIRECT:
            #  20240820 for direct only
            self.vol_provisioner = VSPVolumeProvisioner(connection_info)
            self.hg_prov = VSPHostGroupProvisioner(self.connection_info)

    @log_entry_exit
    def get_all_shadow_image_pairs(self, serial, pvol):
        if pvol is not None:
            shadow_image_pairs = self.get_shadow_image_pair_by_pvol_and_svol(
                serial, pvol
            )
        else:
            shadow_image_pairs = self.gateway.get_all_shadow_image_pairs(serial)
            shadow_image_pairs = shadow_image_pairs.data_to_list()

        if self.connection_info.connection_type == ConnectionTypes.DIRECT:
            shadow_image_pairs = self.fill_nvm_subsystem_info_for_si_pairs(
                shadow_image_pairs
            )

        return shadow_image_pairs

    @log_entry_exit
    def fill_nvm_subsystem_info_for_si_pairs(self, shadow_image_pairs):
        logger.writeDebug(
            f"fill_nvm_subsystem_info_for_si_pairs:shadow_image_pairs= {shadow_image_pairs}"
        )
        new_shadow_image_pairs = []
        for si in shadow_image_pairs:
            new_si_pair = self.fill_nvm_subsystem_info_for_one_si_pair(si)
            new_shadow_image_pairs.append(new_si_pair)
        return new_shadow_image_pairs

    @log_entry_exit
    def fill_nvm_subsystem_info_for_one_si_pair(self, shadow_image_pair):
        logger.writeDebug(
            f"fill_nvm_subsystem_info_for_one_si_pair:shadow_image_pair= {shadow_image_pair}"
        )
        if isinstance(shadow_image_pair, dict):
            pvol = shadow_image_pair["primaryVolumeId"]
            svol = shadow_image_pair["secondaryVolumeId"]
            shadow_image_pair["pvolNvmSubsystemName"] = (
                self.nvm_subsystem_name_for_ldev_id(pvol)
            )
            shadow_image_pair["svolNvmSubsystemName"] = (
                self.nvm_subsystem_name_for_ldev_id(svol)
            )
        else:
            pvol = shadow_image_pair.primaryVolumeId
            svol = shadow_image_pair.secondaryVolumeId
            shadow_image_pair.pvolNvmSubsystemName = (
                self.nvm_subsystem_name_for_ldev_id(pvol)
            )
            shadow_image_pair.svolNvmSubsystemName = (
                self.nvm_subsystem_name_for_ldev_id(svol)
            )

        return shadow_image_pair

    @log_entry_exit
    def nvm_subsystem_name_for_ldev_id(self, ldev_id):
        volume = self.vol_provisioner.get_volume_by_ldev(ldev_id)
        if volume.nvmSubsystemId:
            nvm_subsystem_name = self.get_nvm_subsystem_name(volume)
            logger.writeDebug(
                "PROV:nvm_subsystem_name_for_ldev_id:nvm_subsystem_name = {}",
                nvm_subsystem_name,
            )
            return nvm_subsystem_name
        else:
            return None

    @log_entry_exit
    def get_nvm_subsystem_name(self, volume):
        nvm_provisioner = VSPNvmeProvisioner(self.connection_info)
        nvm_ss = nvm_provisioner.get_nvme_subsystem_by_id(volume.nvmSubsystemId)
        logger.writeDebug("PROV:get_nvm_subsystem_info:nvm_subsystem = {}", nvm_ss)

        return nvm_ss.nvmSubsystemName

    @log_entry_exit
    def create_secondary_volume(self, pvol, svol_pool_id):
        sec_vol_spec = CreateVolumeSpec()
        sec_vol_spec.pool_id = svol_pool_id
        sec_vol_spec.size = get_size_from_byte_format_capacity(pvol.byteFormatCapacity)
        sec_vol_spec.capacity_saving = pvol.dataReductionMode
        if pvol.label is not None and pvol.label != "":
            sec_vol_name = pvol.label
        else:
            sec_vol_name = f"{DEFAULT_NAME_PREFIX}-{pvol.ldevId}"
        sec_vol_spec.name = sec_vol_name

        sec_vol_id = self.vol_provisioner.create_volume(sec_vol_spec)
        return sec_vol_id

    @log_entry_exit
    def create_shadow_image_pair(self, serial, createShadowImagePairSpec):

        if self.connection_info.connection_type == ConnectionTypes.DIRECT:
            #  20240820 for direct only
            pvol = self.vol_provisioner.get_volume_by_ldev(
                createShadowImagePairSpec.pvol
            )
            if pvol.emulationType == VolumePayloadConst.NOT_DEFINED:
                err_msg = VSPShadowImagePairValidateMsg.PVOL_NOT_FOUND.value
                logger.writeError(err_msg)
                raise ValueError(err_msg)

            if createShadowImagePairSpec.svol is None:
                if createShadowImagePairSpec.secondary_pool_id is None:
                    err_msg = VSPShadowImagePairValidateMsg.SVOL_POOL_ID_NEEDED.value
                    raise ValueError(err_msg)
                svol_pool_id = createShadowImagePairSpec.secondary_pool_id
                svol_id = self.create_secondary_volume(pvol, svol_pool_id)
                createShadowImagePairSpec.svol = svol_id
                if pvol.nvmSubsystemId:
                    ns_id = self.create_name_space_for_svol(
                        pvol.nvmSubsystemId, svol_id
                    )

                if pvol.ports is not None and len(pvol.ports) > 0:
                    hg_info = pvol.ports[0]
                    hg = VSPHostGroupInfo(
                        port=hg_info["portId"], hostGroupId=hg_info["hostGroupNumber"]
                    )
                    self.hg_prov.add_luns_to_host_group(hg, luns=[svol_id])
                    svol = self.vol_provisioner.get_volume_by_ldev(svol_id)
                    if svol.ports:
                        hg_info = svol.ports[0]
            else:
                svol = self.vol_provisioner.get_volume_by_ldev(
                    createShadowImagePairSpec.svol
                )
                if svol.emulationType == VolumePayloadConst.NOT_DEFINED:
                    err_msg = VSPShadowImagePairValidateMsg.SVOL_NOT_FOUND.value
                    logger.writeError(err_msg)
                    raise ValueError(err_msg)
                if pvol.byteFormatCapacity != svol.byteFormatCapacity:
                    err_msg = (
                        VSPShadowImagePairValidateMsg.PVOL_SVOL_SIZE_MISMATCH.value
                    )
                    logger.writeError(err_msg)
                    raise ValueError(err_msg)
            logger.writeDebug(
                f"PV:create_shadow_image_pair:spec= {createShadowImagePairSpec}"
            )
            if createShadowImagePairSpec.is_data_reduction_force_copy is None:
                createShadowImagePairSpec.is_data_reduction_force_copy = (
                    True
                    if pvol.dataReductionMode
                    and pvol.dataReductionMode != VolumePayloadConst.DISABLED
                    else False
                )

        pairId = self.gateway.create_shadow_image_pair(
            serial, createShadowImagePairSpec
        )
        time.sleep(20)
        shadow_image_pair = self.gateway.get_shadow_image_pair_by_id(serial, pairId)
        shadow_image_pair = self.fill_nvm_subsystem_info_for_one_si_pair(
            shadow_image_pair
        )
        logger.writeDebug(
            "PROV:create_shadow_image_pair:create_shadow_image_pair = {} type = {}",
            shadow_image_pair,
            type(shadow_image_pair),
        )
        if isinstance(shadow_image_pair, dict):
            return shadow_image_pair
        return shadow_image_pair.to_dict()

    @log_entry_exit
    def create_name_space_for_svol(self, nvm_subsystem_id, ldev_id):
        nvm_provisioner = VSPNvmeProvisioner(self.connection_info)
        return nvm_provisioner.create_namespace(nvm_subsystem_id, ldev_id)

    @log_entry_exit
    def get_shadow_image_pair_by_id(self, serial, pairId):

        return self.gateway.get_shadow_image_pair_by_id(serial, pairId)

    @log_entry_exit
    def get_shadow_image_pair_by_pvol_and_svol(self, serial, pvol, svol=None):
        shadow_image_pairs = None
        if pvol is None:
            shadow_image_pairs = self.gateway.get_all_shadow_image_pairs(serial)
        else:
            shadow_image_pairs = self.gateway.get_shadow_image_pair_by_pvol(
                serial, pvol
            )
        shadow_image_list = []
        shadow_image_pair = None
        for sip in shadow_image_pairs.data_to_list():
            if sip.get("primaryVolumeId") == pvol:
                shadow_image_list.append(sip)
            if svol is not None:
                if sip.get("secondaryVolumeId") == svol:
                    shadow_image_pair = sip
                    return shadow_image_pair

        if svol is not None:
            return None

        data = VSPShadowImagePairsInfo(
            dicts_to_dataclass_list(shadow_image_list, VSPShadowImagePairInfo)
        )
        return data.data_to_list()

    @log_entry_exit
    def is_out_of_band(self):
        return self.config_gw.is_out_of_band()

    @log_entry_exit
    def split_shadow_image_pair(self, serial, updateShadowImagePairSpec):
        unused = self.gateway.split_shadow_image_pair(serial, updateShadowImagePairSpec)
        return self.get_si_pair_with_latest_data(
            serial, updateShadowImagePairSpec.pair_id, PairStatus.PSUS
        )

    @log_entry_exit
    def resync_shadow_image_pair(self, serial, updateShadowImagePairSpec):
        unused = self.gateway.resync_shadow_image_pair(
            serial, updateShadowImagePairSpec
        )
        return self.get_si_pair_with_latest_data(
            serial, updateShadowImagePairSpec.pair_id, PairStatus.PAIR
        )

    @log_entry_exit
    def restore_shadow_image_pair(self, serial, updateShadowImagePairSpec):
        unused = self.gateway.restore_shadow_image_pair(
            serial, updateShadowImagePairSpec
        )

        return self.get_si_pair_with_latest_data(
            serial, updateShadowImagePairSpec.pair_id, PairStatus.PAIR
        )

    @log_entry_exit
    def get_si_pair_with_latest_data(self, serial, pair_id, type):
        pair = None
        count = 0

        while count < 10:
            pair = self.gateway.get_shadow_image_pair_by_id(serial, pair_id)

            if (
                isinstance(pair, dict)
                and pair.get("status") == type
                or pair.status == type
            ):
                return pair.to_dict()
            time.sleep(10)
            count += 1
        return pair

    @log_entry_exit
    def delete_shadow_image_pair(self, serial, deleteShadowImagePairSpec):
        unused = self.gateway.delete_shadow_image_pair(
            serial, deleteShadowImagePairSpec
        )
        return "Shadow image pair is deleted."
