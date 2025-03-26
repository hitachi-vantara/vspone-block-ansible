try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes
    from ..provisioner.vsp_storage_system_provisioner import VSPStorageSystemProvisioner
    from ..common.hv_log import Log
    from ..model.vsp_volume_models import VSPVolumesInfo
    from ..model.vsp_external_volume_models import ExternalVolumeSpec
    from ..common.ansible_common import (
        log_entry_exit,
    )
    from ..message.vsp_external_volume_msgs import VSPSExternalVolumeValidateMsg

except ImportError:
    from message.vsp_external_volume_msgs import VSPSExternalVolumeValidateMsg
    from model.vsp_external_volume_models import ExternalVolumeSpec
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes
    from provisioner.vsp_storage_system_provisioner import VSPStorageSystemProvisioner
    from common.hv_log import Log
    from model.vsp_volume_models import VSPVolumesInfo
    from common.ansible_common import (
        log_entry_exit,
    )

logger = Log()


class VSPExternalVolumeProvisioner:

    def __init__(self, connection_info, serial):
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_EXT_VOLUME
        )
        self.pg_gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_PARITY_GROUP
        )
        self.vol_gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_VOLUME
        )

        self.storage_prov = VSPStorageSystemProvisioner(connection_info)
        self.connection_info = connection_info
        self.connection_type = connection_info.connection_type
        self.serial = serial

        self.check_ucp_system(serial)
        self.gateway.set_storage_serial_number(serial)

    @log_entry_exit
    def check_ucp_system(self, serial):
        serial, resource_id = self.storage_prov.check_ucp_system(serial)
        self.serial = serial
        self.gateway.resource_id = resource_id
        self.gateway.serial = serial
        return serial

    @log_entry_exit
    def get_external_path_groups(self):
        resp = self.gateway.get_external_path_groups()
        return resp

    @log_entry_exit
    def get_free_ldev_from_meta(self):
        items = self.vol_gateway.get_free_ldev_from_meta()
        for item in items.data:
            return item.ldevId

    @log_entry_exit
    def get_next_external_parity_group(self, get_external_path_group):
        epgs = self.pg_gateway.get_all_external_parity_groups()
        pgids = []
        for epg in epgs.data:
            pgids.append(epg.externalParityGroupId)

        ii = 1
        pgid = "1-" + str(ii)
        while pgid in pgids:
            ii += 1
            pgid = "1-" + str(ii)

        return pgid

    @log_entry_exit
    def select_external_path_group(self, extvol):
        portId = extvol.portId
        externalWwn = extvol.externalWwn
        logger.writeDebug("20250228 portId={}", portId)
        logger.writeDebug("20250228 externalWwn={}", externalWwn)

        external_path_groups = self.gateway.get_external_path_groups()
        if external_path_groups is None:
            return

        for external_path_group in external_path_groups.data:
            externalPaths = external_path_group.externalPaths
            logger.writeDebug("20250228 externalPaths={}", externalPaths)
            if externalPaths is None:
                continue
            for externalPath in externalPaths.data:
                if portId != externalPath.portId:
                    continue
                if externalWwn != externalPath.externalWwn:
                    continue
                return external_path_group

    @log_entry_exit
    # find the external_parity_group in the external_path_group, then get the ldevids from it
    def get_ldev_ids_in_external_path_group(
        self, external_path_group, externalLun, portId, externalWwn
    ):
        for epg in external_path_group.externalParityGroups:
            externalLuns = epg.get("externalLuns")
            if externalLuns is None:
                continue
            for extlun in externalLuns:
                if extlun is None:
                    continue
                pid = extlun.get("portId")
                wwn = extlun.get("externalWwn")
                lun = extlun.get("externalLun")
                if pid is None or pid != portId:
                    continue
                if wwn is None or wwn != externalWwn:
                    continue
                if lun is None or lun != externalLun:
                    continue
                externalParityGroupId = epg.get("externalParityGroupId")
                if externalParityGroupId is None:
                    continue
                eprg = self.pg_gateway.get_external_parity_group(externalParityGroupId)
                ldevIds = []
                for space in eprg.spaces:
                    ldevId = space.ldevId
                    if ldevId is not None:
                        ldevIds.append(ldevId)
                return ldevIds
        return []

    @log_entry_exit
    # find the external_parity_group in the external_path_group
    def get_external_parity_group(
        self, external_path_group, externalLun, portId, externalWwn
    ):
        for epg in external_path_group.externalParityGroups:
            externalLuns = epg.get("externalLuns")
            if externalLuns is None:
                continue
            for extlun in externalLuns:
                if extlun is None:
                    continue
                pid = extlun.get("portId")
                wwn = extlun.get("externalWwn")
                lun = extlun.get("externalLun")
                if pid is None or pid != portId:
                    continue
                if wwn is None or wwn != externalWwn:
                    continue
                if lun is None or lun != externalLun:
                    continue
                return epg

        return

    @log_entry_exit
    def get_all_external_volumes(self):
        allExtvols = []
        allExtvolsObj = []
        external_path_groups = self.gateway.get_external_path_groups()
        if external_path_groups is None:
            return

        for external_path_group in external_path_groups.data:
            externalPaths = external_path_group.externalPaths
            logger.writeDebug("20250228 externalPaths={}", externalPaths)
            if externalPaths is None:
                continue
            for externalPath in externalPaths.data:
                extvols = self.gateway.get_external_volumes_with_extpath(
                    externalPath.portId, externalPath.externalWwn
                )
                for extvol in extvols.data:
                    externalVolumeInfo = extvol.externalVolumeInfo
                    extvol.externalLdevId = int(externalVolumeInfo[-4:], 16)
                    extvol.externalVolumeCapacityInMb = (
                        extvol.externalVolumeCapacity * 512
                    ) / (1024 * 1024)
                    extvol.externalProductId = external_path_group.externalProductId
                    extvol.externalSerialNumber = (
                        external_path_group.externalSerialNumber
                    )
                    extvol.externalPathGroupId = external_path_group.externalPathGroupId

                    # look for the external volume from the external_parity_group in the external_path_group
                    extvol.ldevIds = self.get_ldev_ids_in_external_path_group(
                        external_path_group,
                        extvol.externalLun,
                        extvol.portId,
                        extvol.externalWwn,
                    )

                    item = extvol.camel_to_snake_dict()
                    allExtvols.append(item)
                    allExtvolsObj.append(extvol)

                logger.writeDebug("20250228 extvols={}", allExtvols)
                return allExtvols, allExtvolsObj

    @log_entry_exit
    def get_one_external_volume(
        self, all_external_volumes, external_storage_serial, external_ldev_id
    ):

        if all_external_volumes is None:
            return None, None

        logger.writeDebug("20250228 ext_serial={}", external_storage_serial)
        logger.writeDebug("20250228 external_ldev_id={}", external_ldev_id)

        for extvol in all_external_volumes:
            if extvol.externalSerialNumber == external_storage_serial:
                if extvol.externalLdevId == external_ldev_id:
                    return extvol.camel_to_snake_dict(), extvol

        return None, None

    @log_entry_exit
    def external_volume_facts(self, spec):

        rsp, objs = self.get_all_external_volumes()
        if spec is None:
            return None if not rsp else rsp

        ext_serial = spec.external_storage_serial
        external_ldev_id = spec.external_ldev_id

        rsp, notused = self.get_one_external_volume(
            objs,
            ext_serial,
            external_ldev_id,
        )
        logger.writeDebug("20250228 notused={}", notused)
        return rsp

    @log_entry_exit
    def find_ext_volume_by_external_ldev_id(
        self, hex_ldev, externalPathsList, epg=None
    ):
        # for eplist in externalPathsList:
        for ep in externalPathsList.data:
            extvols = self.gateway.get_external_volumes_with_extpath(
                ep.portId, ep.externalWwn
            )
            for extvol in extvols.data:
                externalVolumeInfo = extvol.externalVolumeInfo
                ldev = externalVolumeInfo[-4:]
                logger.writeDebug("20250228 externalVolumeInfo={}", externalVolumeInfo)
                if hex_ldev != ldev:
                    continue
                extvol.externalLdevId = int(externalVolumeInfo[-4:], 16)
                extvol.externalVolumeCapacityInMb = (
                    extvol.externalVolumeCapacity * 512
                ) / (1024 * 1024)
                extvol.externalProductId = epg.externalProductId
                extvol.externalSerialNumber = epg.externalSerialNumber
                extvol.externalPathGroupId = epg.externalPathGroupId
                return extvol

    @log_entry_exit
    def get_extern_paths(self, ext_serial):
        resp = self.gateway.get_external_path_groups()
        if resp is None:
            return

        for epg in resp.data:
            if epg.externalSerialNumber != ext_serial:
                continue

        return None

    @log_entry_exit
    def select_external_volume(self, ext_serial, ext_ldev_id):

        # get the hex format of the volume
        # 1345 -> 0541
        hex_ldev = format(ext_ldev_id, "04x")
        hex_ldev = hex_ldev.upper()
        # get the storage serial encoding
        # 410109 -> 40277D
        model = ext_serial[0]
        serial = ext_serial[-5:]
        hex_serial = format(int(serial), "04x")
        hex_serial = hex_serial.upper()
        hex_serial = model + "0" + hex_serial
        logger.writeDebug("20250228 hex_ldev={}", hex_ldev)
        logger.writeDebug("20250228 hex_serial={}", hex_serial)

        # need the portID and externalWWN
        # get_extern_paths from get_extern_path_groups by ext_serial
        # list<portID, externalWWN> = self.get_extern_paths(ext_serial)
        externalPathGroup = self.get_extern_paths(ext_serial)
        if externalPathGroup is not None:
            rsp = self.find_ext_volume_by_external_ldev_id(
                hex_ldev, externalPathGroup.externalPaths, externalPathGroup
            )
        else:
            return
        return rsp

    @log_entry_exit
    def get_external_path_groups(self):
        resp = self.gateway.get_external_path_groups()
        return resp

    @log_entry_exit
    def delete_volume(self, connection_info, ldev):
        gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_VOLUME
        )

        gateway.delete_volume(ldev, False)
        return

    @log_entry_exit
    def create_external_volume_by_spec(self, spec: ExternalVolumeSpec):
        return self.create_external_volume(
            spec.ldev_id,
            spec.external_storage_serial,
            spec.external_ldev_id,
        )

    @log_entry_exit
    def delete_external_volume_by_spec(self, spec: ExternalVolumeSpec):
        return self.delete_external_volume(
            spec.ldev_id,
            spec.external_storage_serial,
            spec.external_ldev_id,
        )

    @log_entry_exit
    def delete_external_volume(self, ldev_id, ext_serial, external_ldev_id):
        # the external volume to delete
        if ldev_id is None:
            return None, VSPSExternalVolumeValidateMsg.LDEV_REQUIRED.value
            # return None, "External Volume ldev_id parameter is mandatory."

        rsp, objs = self.get_all_external_volumes()
        if rsp is None:
            return None, VSPSExternalVolumeValidateMsg.NO_EXT_VOL.value
            # return None, "No External Storage Volumes in the system."
        notused, rsp = self.get_one_external_volume(
            objs,
            ext_serial,
            external_ldev_id,
        )
        logger.writeDebug("20250228 notused={}", notused)
        if rsp is None:
            return None, VSPSExternalVolumeValidateMsg.EXT_VOL_NOT_FOUND.value
            # return None, "External Storage Volume is not found."
        portId = rsp.portId
        externalWwn = rsp.externalWwn
        lunId = rsp.externalLun

        # found the exteranl storage volume
        # now deduce the external_parity_group
        # delete the external_parity_group to delete the exteranl volume(s)
        portId = rsp.portId
        externalWwn = rsp.externalWwn
        lunId = rsp.externalLun
        # found = False
        vol = self.vol_gateway.get_volume_by_id_external_volume(ldev_id)
        logger.writeDebug("20250228 vol={}", vol)
        if vol and vol.emulationType != "NOT DEFINED":
            external_ports = vol.externalPorts
            if external_ports:
                if self.ldev_in_external_ports(
                    external_ports, portId, externalWwn, lunId
                ):
                    # vol = vol.camel_to_snake_dict()
                    vol = VSPVolumesInfo(data=[vol])
                    # found = True
                    # return (
                    #     vol,
                    #     "ldev_id is already associated with the external volume.",
                    # )
                else:
                    vol = vol.camel_to_snake_dict()
                    # vol = VSPVolumesInfo(data=[vol])
                    return (
                        vol,
                        VSPSExternalVolumeValidateMsg.ASSOCIATED_ANOTHER.value,
                        # "ldev_id is already associated with another external volume.",
                    )
            else:
                return [], VSPSExternalVolumeValidateMsg.PROVISIONED.value
                # return [], "ldev_id is already provisioned with an internal ldev."
        else:
            return [], VSPSExternalVolumeValidateMsg.NOT_FOUND.value
            # return [], "ldev_id is not found, may have been deleted."

        external_path_group = self.select_external_path_group(rsp)
        if external_path_group is None:
            return [], VSPSExternalVolumeValidateMsg.NO_PATHGRP.value
            # return None, "Unable to find the external path group."

        # now we have the external path group,
        # find the external parity group
        epg = self.get_external_parity_group(
            external_path_group,
            lunId,
            portId,
            externalWwn,
        )
        if epg is None:
            return [], VSPSExternalVolumeValidateMsg.NO_PARITYGRP.value
            # return None, "Unable to find the external parity group."

        # delete epg, force=true
        logger.writeDebug("20250228 epg={}", epg.get("externalParityGroupId"))
        self.pg_gateway.delete_external_parity_group_force(
            epg.get("externalParityGroupId")
        )

        return [], None

    @log_entry_exit
    def ldev_in_external_ports(self, external_ports, portId, externalWwn, lunId):
        logger.writeDebug("20250228 external_ports={}", external_ports)
        logger.writeDebug("20250228 lunId={}", lunId)
        logger.writeDebug("20250228 portId={}", portId)
        logger.writeDebug("20250228 externalWwn={}", externalWwn)

        if not external_ports:
            return False
        for ep in external_ports:
            logger.writeDebug("20250228 ep={}", ep)
            pid = ep.get("portId")
            wwn = ep.get("wwn")
            lun = ep.get("lun")
            if not pid or pid != portId:
                continue
            if not wwn or wwn != externalWwn:
                continue
            if lun is None or lun != lunId:
                continue
            return True

        return False

    @log_entry_exit
    def create_external_volume(self, ldev_id, ext_serial, external_ldev_id):

        # 20250303 creates an external volume from external parity group
        ldev = external_ldev_id

        # select ext-volume by ldev and serial
        rsp = self.select_external_volume(ext_serial, ldev)
        if rsp is None:
            return None, "Unable to find the external volume."

        portId = rsp.portId
        externalWwn = rsp.externalWwn
        lunId = rsp.externalLun
        externalVolumeCapacity = rsp.externalVolumeCapacity

        if ldev_id:
            vol = self.vol_gateway.get_volume_by_id_external_volume(ldev_id)
            logger.writeDebug("20250228 vol={}", vol)
            if vol and vol.emulationType != "NOT DEFINED":
                external_ports = vol.externalPorts
                if external_ports:
                    if self.ldev_in_external_ports(
                        external_ports, portId, externalWwn, lunId
                    ):
                        # vol = vol.camel_to_snake_dict()
                        vol = VSPVolumesInfo(data=[vol])
                        return (
                            vol,
                            "ldev_id is already associated with the external volume.",
                        )
                    else:
                        # vol = vol.camel_to_snake_dict()
                        vol = VSPVolumesInfo(data=[vol])
                        return (
                            vol,
                            "ldev_id is already associated with another external volume.",
                        )
                else:
                    return None, "ldev_id is already provisioned with an internal ldev."

        rsp = self.select_external_path_group(rsp)
        externalPathGroupId = rsp.externalPathGroupId
        if rsp is None:
            return None, "Unable to find the external path group."

        rsp = self.get_next_external_parity_group(rsp)
        externalParityGroupId = rsp

        logger.writeDebug("20250228 externalPathGroupId={}", externalPathGroupId)
        logger.writeDebug("20250228 externalParityGroupId={}", externalParityGroupId)
        logger.writeDebug("20250228 lunId={}", lunId)
        logger.writeDebug("20250228 portId={}", portId)
        logger.writeDebug("20250228 externalWwn={}", externalWwn)
        rsp = self.pg_gateway.create_external_parity_group(
            externalPathGroupId,
            externalParityGroupId,
            portId,
            externalWwn,
            lunId,
        )
        # if it fails, check the lunId, which is the externalLun
        # loop thru the externalParityGroups in the externalPathGroups
        # get the externalParityGroupId which has this externalLun
        # and report it (or offer to delete it)
        # this can be a pre-check
        logger.writeDebug("20250228 rsp={}", rsp)

        # map ext volume: create volume by parity group
        if not ldev_id:
            ldev_id = self.get_free_ldev_from_meta()
        logger.writeDebug("20250228 ldev_id={}", ldev_id)
        logger.writeDebug("20250228 externalVolumeCapacity={}", externalVolumeCapacity)
        rsp = self.vol_gateway.map_ext_volume(
            ldev_id, externalParityGroupId, externalVolumeCapacity
        )

        if rsp:
            vol = self.vol_gateway.get_volume_by_id_external_volume(rsp)
            # return vol.camel_to_snake_dict(), None
            return VSPVolumesInfo(data=[vol]), None

        return None, "Failed to create external volume."
