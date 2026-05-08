from ..model.vsp_one_gad_models import VspOneGadFactSpec, VspOneGadList
from ..gateway.vsp_one_gad_gateway import VspOneGadGateway
from ..model.vsp_gad_pairs_models import VspGadCtgInfoList
from ..common.ansible_common import log_entry_exit
from ..common.hv_log import (
    Log,
)
from ..gateway.vsp_one_gad_ctg_gateway import VspOneGadCtgGateway
from ..common.vsp_errors import (
    VspFeatureNotSupportedError,
    VspPortNotFoundError,
)
from ..message.vsp_storage_system_msgs import VspStorageSystemMsg
from ..message.vsp_gad_pair_msgs import VspOneGadValidationMsg
from ..model.vsp_volume_models import (
    CreateVolumeSpecwithDeatilsSetting,
    VolumeDetailItemSpec,
)
from ..model.vsp_gad_pairs_models import (
    VspGadCtgCreateSpec,
    RemoteVolumeActiveActiveMirroringInfo,
)
from ..gateway.vsp_volume_simple_api_gateway import VspSimpleApiGateway
from ..gateway.vsp_remote_connection_gateway import VSPRemoteConnectionDirectGateway

logger = Log()


class VspOneGadCtgProvisioner:

    def __init__(self, connection_info, secondary_connection_info):
        self.gateway = VspOneGadCtgGateway(connection_info, secondary_connection_info)
        self.connection_info = connection_info
        self.secondary_connection_info = secondary_connection_info
        self.volume_gateway = VspSimpleApiGateway(connection_info)
        self.secondary_vol_gateway = VspSimpleApiGateway(secondary_connection_info)
        self.remote_storage_gateway = VSPRemoteConnectionDirectGateway(connection_info)
        self.secondary_volume_list = []
        self.ctg_group_data = None
        self.gad_gateway = VspOneGadGateway(connection_info)

        if not self.gateway.is_block_high_end:
            raise VspFeatureNotSupportedError(
                VspStorageSystemMsg.ONLY_SUPPORTED_ON_BHE.value
            )

    @log_entry_exit
    def get_gad_ctgs(self, spec=None):
        """
        Get GAD consistency groups
        :return: GAD consistency groups
        """
        if spec and spec.consistency_group_id is not None:
            return self.get_gad_ctg_by_id(spec.consistency_group_id)
        return self.gateway.get_gad_ctgs()

    @log_entry_exit
    def get_gad_ctg_by_id(self, ctg_id):
        """
        Get GAD consistency group information by ID
        :param ctg_id: GAD consistency group ID
        :return: GAD consistency group information
        """
        return self.gateway.get_gad_ctg_by_id(ctg_id)

    @log_entry_exit
    def get_gad_pairs_by_ctg_id(self, ctg_ids):
        """
        Get multiple GAD consistency group information by IDs
        :param ctg_ids: List of GAD consistency group IDs
        :return: List of GAD consistency group information
        """
        gad_pair_list = []
        for ctg_id in ctg_ids:
            spec = VspOneGadFactSpec(consistency_group_id=ctg_id)
            gad_pairs = self.gad_gateway.get_gad_pairs_facts(spec)
            if gad_pairs:
                gad_pair_list.extend(gad_pairs.data)
        return VspOneGadList(data=gad_pair_list)

    @log_entry_exit
    def get_multi_gad_ctg_by_id(self, ctg_ids):
        """
        Get multiple GAD consistency group information by IDs
        :param ctg_ids: List of GAD consistency group IDs
        :return: List of GAD consistency group information
        """
        ctg_info_list = []
        for ctg_id in ctg_ids:
            ctg_info = self.get_gad_ctg_by_id(ctg_id)
            if ctg_info:
                ctg_info_list.append(ctg_info)
        return VspGadCtgInfoList(data=ctg_info_list)

    @log_entry_exit
    def suspend_gad_pairs(self, spec=None):

        return self.gateway.suspend_gad_pairs(
            spec.consistency_group_ids, spec.continue_io_volume
        )

    @log_entry_exit
    def resync_gad_pairs(self, spec=None):

        return self.gateway.resync_gad_pairs(
            spec.consistency_group_ids,
            spec.is_swap_resynced,
            spec.io_preference_mode,
            spec.copy_pace,
        )

    @log_entry_exit
    def create_gad_using_ctg(self, spec: VspGadCtgCreateSpec):

        # validate the spec before proceeding with provisioning
        self._validate_gad_spec(spec)
        self._handle_ctg_group_data(spec)
        # Get the primary volumes information
        primary_volume_dict = self._get_primary_volumes_info(spec)

        # Handle the provisioning of secondary volumes for GAD pairs
        self._handle_secondary_volumes(spec, primary_volume_dict)
        # After provisioning secondary volumes, call the gateway method to create GAD CTG with the updated spec
        try:
            unused = self.gateway.create_gad_pairs(spec)
        except Exception as e:
            logger.writeError(
                VspOneGadValidationMsg.FAILED_TO_CREATE_GAD_CTG.value.format(
                    spec.consistency_group_id, e
                )
            )
            # Consider rolling back created secondary volumes here if necessary
            self._cleanup_secondary_volumes(spec)
            raise e

        return None

    def _handle_secondary_volumes(self, spec: VspGadCtgCreateSpec, primary_volume_dict):
        """
        Handle the provisioning of secondary volumes for GAD (Global Active Device) pairs.
        This method creates secondary volumes in the specified storage pool that correspond to
        primary volumes in a GAD configuration. For each GAD pair without an already provisioned
        secondary volume, a secondary volume is created with matching capacity and settings as
        the primary volume.
        Args:
            spec (VspGadCtgCreateSpec): The GAD CTG (Consistency Target Group) specification containing
                GAD pairs and secondary storage pool configuration.
            primary_volume_dict (dict): A dictionary mapping primary volume IDs to their volume information objects,
                containing details like name, capacity, and saving settings.
        Returns:
            None: The method updates the spec.gad_pairs in-place, populating the
                provisioned_secondary_volume_id for each GAD pair that did not already have one.
        Raises:
            Potentially raises exceptions from gateway operations if volume creation fails.
        Note:
            - Secondary volumes are only created for GAD pairs where provisioned_secondary_volume_id is None.
            - The secondary volumes inherit capacity and data reduction settings from their corresponding primary volumes.
            - There is a TODO comment indicating potential future enhancement to validate existing secondary volumes before provisioning.
        """

        volume_spec = CreateVolumeSpecwithDeatilsSetting(
            pool_id=spec.secondary_storage_pool_id,
            capacity_unit="block",
            virtualization_active_active_mirroring_pair_reserved="RESERVED",
        )
        volume_spec.create_volume_details = []

        # Collect primary volumes that need secondary volumes created
        primary_volumes = []
        for gad_pair in spec.gad_pairs:
            # Only process GAD pairs without an existing secondary volume
            if (
                gad_pair.provisioned_secondary_volume_id is None
                and gad_pair.already_exists is False
            ):
                # Get primary volume details from the dictionary
                volume_info = primary_volume_dict.get(gad_pair.primary_volume_id)

                # Create a volume spec for the secondary volume with same properties
                internal_spec = VolumeDetailItemSpec(
                    nickname=volume_info.nickname,
                    capacity=volume_info.totalCapacity,
                    saving_setting=volume_info.savingSetting,
                    is_data_reduction_share_enabled=volume_info.isDataReductionShareEnabled,
                    resource_id=volume_info.id,
                )
                # Add to batch creation list
                volume_spec.create_volume_details.append(internal_spec)
                primary_volumes.append(gad_pair.primary_volume_id)
            elif (
                gad_pair.provisioned_secondary_volume_id is not None
                and gad_pair.already_exists is False
            ):
                volume_info = self.secondary_vol_gateway.get_volume_by_id_with_mirroring_n_virtualization(
                    gad_pair.provisioned_secondary_volume_id
                )
                if not volume_info:
                    raise VspPortNotFoundError(
                        VspOneGadValidationMsg.SECONDARY_VOLUME_NOT_FOUND.value.format(
                            gad_pair.provisioned_secondary_volume_id
                        )
                    )
                if volume_info.luns is None or len(volume_info.luns) == 0:
                    raise ValueError(
                        VspOneGadValidationMsg.SECONDARY_VOLUME_NOT_MAPPED.value.format(
                            gad_pair.provisioned_secondary_volume_id
                        )
                    )
                remote_info = RemoteVolumeActiveActiveMirroringInfo(
                    ssid=volume_info.activeActiveMirroringInfo.ssid,
                    port_number=volume_info.activeActiveMirroringInfo.portNumber,
                    absolute_lun=volume_info.activeActiveMirroringInfo.absoluteLun,
                    storage_type_number=volume_info.activeActiveMirroringInfo.storageTypeNumber,
                )
                gad_pair.remote_volume_active_active_mirroring_info = remote_info

        if len(primary_volumes) < 1:
            return
        # Create all secondary volumes in batch
        try:
            secondary_volumes_ids = (
                self.secondary_vol_gateway.create_volume_with_details(volume_spec)
            )
            self.secondary_volume_list.extend(secondary_volumes_ids)
        except Exception as e:
            logger.writeError(
                VspOneGadValidationMsg.FAILED_TO_CREATE_SECONDARY_VOLUMES.value.format(
                    e
                )
            )
            # Consider rolling back created secondary volumes here if necessary
            self._cleanup_secondary_volumes(spec)
            raise e

        try:
            self.secondary_vol_gateway.attach_servers_to_volumes(
                secondary_volumes_ids, spec.secondary_servers
            )
        except Exception as e:
            logger.writeError(
                VspOneGadValidationMsg.FAILED_TO_ATTACH_SERVERS_TO_VOLUMES.value.format(
                    e
                )
            )
            # Consider rolling back created secondary volumes here if necessary
            self._cleanup_secondary_volumes(spec)
            raise e
        # Map created secondary volumes back to their GAD pairs
        for primary_volume_id, secondary_volume_id in zip(
            primary_volumes, secondary_volumes_ids
        ):
            for gad_pair in spec.gad_pairs:
                if gad_pair.primary_volume_id == primary_volume_id:
                    gad_pair.provisioned_secondary_volume_id = secondary_volume_id
                    volume_info = self.secondary_vol_gateway.get_volume_by_id_with_mirroring_n_virtualization(
                        secondary_volume_id
                    )
                    remote_info = RemoteVolumeActiveActiveMirroringInfo(
                        ssid=volume_info.activeActiveMirroringInfo.ssid,
                        port_number=volume_info.activeActiveMirroringInfo.portNumber,
                        absolute_lun=volume_info.activeActiveMirroringInfo.absoluteLun,
                        storage_type_number=volume_info.activeActiveMirroringInfo.storageTypeNumber,
                    )
                    gad_pair.remote_volume_active_active_mirroring_info = remote_info
                    break

    def _get_primary_volumes_info(self, spec: VspGadCtgCreateSpec):
        primary_volume_dict = {}
        for gad_config in spec.gad_pairs:
            volume_info = (
                self.volume_gateway.get_volume_by_id_with_mirroring_n_virtualization(
                    gad_config.primary_volume_id
                )
            )
            if not volume_info:
                raise VspPortNotFoundError(
                    VspOneGadValidationMsg.PRIMARY_VOLUME_NOT_FOUND.value.format(
                        gad_config.primary_volume_id
                    )
                )

            if volume_info.luns is None or len(volume_info.luns) == 0:
                raise ValueError(
                    VspOneGadValidationMsg.PRIMARY_VOLUME_NOT_MAPPED.value.format(
                        gad_config.primary_volume_id
                    )
                )
            primary_volume_dict[volume_info.id] = volume_info
        return primary_volume_dict

    @log_entry_exit
    def filter_gad_pairs_by_primary_volume_ids(
        self, consistency_group_id, primary_volume_ids
    ):
        filtered_gad_pairs = []
        gad_pairs = self.gateway.get_all_gad_pairs_by_ctg_id(consistency_group_id)
        for gad_pair in gad_pairs.data:
            if gad_pair.localVolumeId in primary_volume_ids:
                filtered_gad_pairs.append(gad_pair)
        return filtered_gad_pairs

    def _validate_gad_spec(self, spec: VspGadCtgCreateSpec):
        # validate the remote connection
        should_check_server = True
        if spec.consistency_group_id is None:
            raise ValueError(VspOneGadValidationMsg.CONSISTENCY_GROUP_ID_REQUIRED.value)

        if not spec.gad_pairs or len(spec.gad_pairs) == 0:
            raise ValueError(VspOneGadValidationMsg.GAD_PAIR_DEFINITION_REQUIRED.value)
        if spec.secondary_storage_pool_id is None:
            sec_prov_vols = [
                gad_pair.provisioned_secondary_volume_id
                for gad_pair in spec.gad_pairs
                if gad_pair.provisioned_secondary_volume_id is not None
            ]
            if len(spec.gad_pairs) != len(sec_prov_vols):
                raise ValueError(
                    VspOneGadValidationMsg.SECONDARY_STORAGE_POOL_ID_REQUIRED.value
                )
            should_check_server = False
        if (
            spec.secondary_servers is None
            or len(spec.secondary_servers) == 0
            and should_check_server
        ):
            raise ValueError(VspOneGadValidationMsg.SECONDARY_SERVER_REQUIRED.value)

        remote_storages = self.remote_storage_gateway.get_all_remote_storages()
        secondary_storage = None
        for remote_connection in remote_storages.data:
            if remote_connection.restServerIp == self.secondary_connection_info.address:
                secondary_storage = remote_connection
                break
        if not secondary_storage:
            raise VspPortNotFoundError(
                VspOneGadValidationMsg.SECONDARY_STORAGE_NOT_FOUND.value.format(
                    self.secondary_connection_info.address
                )
            )
        # Validate the path group and quorum group exist in the secondary storage
        remote_path_groups = self.remote_storage_gateway.get_all_remote_connections()
        for remote_connection in remote_path_groups.data:
            if int(remote_connection.remoteSerialNumber) == int(
                secondary_storage.serialNumber
            ):
                if (
                    spec.path_group_id is not None
                    and remote_connection.pathGroupId != spec.path_group_id
                ):
                    continue
                spec.remote_storage_serial_number = secondary_storage.serialNumber
                spec.remote_storage_model = remote_connection.remoteStorageTypeId
                spec.path_group_id = remote_connection.pathGroupId

        if spec.remote_storage_serial_number is None:
            raise VspPortNotFoundError(
                VspOneGadValidationMsg.PATH_GROUP_NOT_FOUND.value.format(
                    self.secondary_connection_info.address
                )
            )

        self._validate_quorum_disk(spec)

    def _handle_ctg_group_data(self, spec: VspGadCtgCreateSpec):
        ctg_group_data = self.gateway.get_all_gad_pairs_by_ctg_id(
            spec.consistency_group_id
        )

        for group in ctg_group_data.data:
            for gad_pair in spec.gad_pairs:
                if gad_pair.primary_volume_id == group.localVolumeId:
                    gad_pair.already_exists = True
                    break
        original_mirror_unit_number = None
        if len(ctg_group_data.data) > 0:
            original_mirror_unit_number = ctg_group_data.data[0].muNumber

        if (
            spec.mirror_unit_number is not None
            and original_mirror_unit_number is not None
            and spec.mirror_unit_number != original_mirror_unit_number
        ):
            raise ValueError(
                VspOneGadValidationMsg.MIRROR_UNIT_NUMBER_MISMATCH.value.format(
                    spec.mirror_unit_number,
                    spec.consistency_group_id,
                    original_mirror_unit_number,
                )
            )
        if original_mirror_unit_number is not None:
            spec.mirror_unit_number = original_mirror_unit_number
        else:
            spec.mirror_unit_number = (
                spec.mirror_unit_number if spec.mirror_unit_number is not None else 0
            )

    def _cleanup_secondary_volumes(self, spec: VspGadCtgCreateSpec):
        for volume in self.secondary_volume_list:
            for server in spec.secondary_servers:
                try:
                    self.secondary_vol_gateway.detach_server_from_volume(volume, server)
                except Exception as e:
                    logger.writeError(
                        VspOneGadValidationMsg.FAILED_TO_DETACH_SECONDARY_VOLUME.value.format(
                            volume, server, e
                        )
                    )
        try:
            self.secondary_vol_gateway.salamander_delete_volumes(
                self.secondary_volume_list
            )
        except Exception as e:
            logger.writeError(
                VspOneGadValidationMsg.FAILED_TO_DELETE_SECONDARY_VOLUMES.value.format(
                    e
                )
            )

    def _validate_quorum_disk(self, spec: VspGadCtgCreateSpec):
        primary_disks = self.gateway.get_primary_vsp_one_quorum_disk()
        secondary_disks = self.gateway.get_secondary_vsp_one_quorum_disk()

        available_quorum_ids = []

        for disk in primary_disks.data:
            if int(disk.pairedStorageSerial) == int(spec.remote_storage_serial_number):
                if (
                    disk.externalVolumeStatus
                    and disk.externalVolumeStatus.lower() == "blockade"
                ):
                    continue
                available_quorum_ids.append(disk.quorumId)

        if len(available_quorum_ids) == 0:
            raise ValueError(
                " No available quorum disks found for the specified primary storage."
            )
        if spec.quorum_id is not None and spec.quorum_id not in available_quorum_ids:
            raise ValueError(
                "The specified quorum ID is not available on the primary storage. Available quorum IDs for the specified secondary storage are: {}".format(
                    available_quorum_ids
                )
            )

        spec.quorum_id = available_quorum_ids[0]
        secondary_disk_ids = [disk.quorumId for disk in secondary_disks.data]
        if spec.quorum_id is not None and spec.quorum_id not in secondary_disk_ids:
            raise ValueError(
                "The specified quorum ID is not available on the secondary storage. "
                "It must match the quorum ID on the primary storage. "
                f"Available quorum IDs on secondary storage are: {secondary_disk_ids}"
            )
