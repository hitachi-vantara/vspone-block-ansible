try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes
    from ..common.uaig_utils import UAIGResourceID
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..common.vsp_constants import UnSubscribeResourceTypes
    from .vsp_storage_pool_provisioner import VSPStoragePoolProvisioner
    from .vsp_shadow_image_pair_provisioner import VSPShadowImagePairProvisioner
    from ..provisioner.vsp_iscsi_target_provisioner import VSPIscsiTargetProvisioner
except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes
    from common.uaig_utils import UAIGResourceID
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from .vsp_storage_pool_provisioner import VSPStoragePoolProvisioner
    from .vsp_shadow_image_pair_provisioner import VSPShadowImagePairProvisioner
    from common.vsp_constants import UnSubscribeResourceTypes
    from provisioner.vsp_iscsi_target_provisioner import VSPIscsiTargetProvisioner


logger = Log()


class VSPUnsubscribeProvisioner:

    def __init__(self, connection_info, serial):
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_UNSUBSCRIBE
        )
        self.hg_gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_HOST_GROUP
        )
        self.vol_gw = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_VOLUME
        )
        self.sp_gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.STORAGE_PORT
        )
        # self.pool_gateway = GatewayFactory.get_gateway(
        #     connection_info, GatewayClassTypes.VSP_STORAGE_POOL
        # )
        self.connection_info = connection_info
        self.serial = serial
        self.gateway.set_storage_serial_number(serial)

    @log_entry_exit
    def check_storage_in_ucpsystem(self) -> bool:
        return self.gateway.check_storage_in_ucpsystem()

    @log_entry_exit
    def unsubscribe_hg(self, hg_names):
        err_list = []
        success_list = []

        for hg_info in hg_names:
            ss = hg_info.split(",")
            port = ss[0]
            name = ss[1]
            if port is None or port == "":
                err_list.append("Port name is not provided.")
            if name is None or name == "":
                err_list.append("Host Group name is not provided.")
            if port is None or port == "" or name is None or name == "":
                continue
            hg = self.get_hg_by_port_and_name(port.strip(), name.strip())
            if hg is None:
                err_list.append(f"Did not find Host Group {name} on port {port}.")
            else:
                success_list.append(f"Found Host Group {name} on port {port}.")
                try:
                    result = self.gateway.untag_subscriber_resource(
                        self.serial, hg.resourceId, hg.type
                    )
                    success_list.append(
                        f"Successfully unsubscribed Host Group {name} on port {port}."
                    )
                    logger.writeDebug(f"PV:unsubscribe:result = {result}")
                except Exception as ex:
                    logger.writeDebug(f"PV:unsubscribe:ex = {ex}")
                    err_list.append(str(ex))
        return err_list, success_list

    @log_entry_exit
    def unsubscribe_volume(self, ldev_ids):
        err_list = []
        success_list = []

        for id in ldev_ids:
            volume = self.get_volume_by_ldev_id(id)
            if volume is None:
                err_list.append(f"Did not find Volume with LDEV ID {id}.")
            else:
                success_list.append(f"Found Volume with LDEV ID {id}.")

                logger.writeDebug(
                    f"PV:unsubscribe:serial = {self.serial}  vol = {volume}"
                )
                try:
                    result = self.gateway.untag_subscriber_resource(
                        self.serial, volume.resourceId, volume.type
                    )
                    success_list.append(
                        f"Successfully unsubscribed Volume with LDEV ID {id}. "
                    )
                    logger.writeDebug(f"PV:unsubscribe:result = {result}")
                except Exception as ex:
                    logger.writeDebug(f"PV:unsubscribe:ex = {ex}")
                    err_list.append(str(ex))
        return err_list, success_list

    @log_entry_exit
    def unsubscribe_port(self, port_ids):
        err_list = []
        success_list = []

        for id in port_ids:
            port = self.get_port_by_id(id.strip())
            if port is None:
                err_list.append(f"Did not find Port with ID {id}.")
            else:
                success_list.append(f"Found Port with ID {id}. ")

                logger.writeDebug(
                    f"PV:unsubscribe:serial = {self.serial}  port = {port}"
                )
                try:
                    result = self.gateway.untag_subscriber_resource(
                        self.serial, port.resourceId, port.type
                    )
                    success_list.append(
                        f"Successfully unsubscribed Port with ID {id}. "
                    )
                    logger.writeDebug(f"PV:unsubscribe:result = {result}")
                except Exception as ex:
                    logger.writeDebug(f"PV:unsubscribe:ex = {ex}")
                    err_list.append(str(ex))

        return err_list, success_list

    @log_entry_exit
    def unsubscribe_pool(self, pool_names):
        err_list = []
        success_list = []

        for name in pool_names:
            try:
                pool = self.get_pool_by_name(name)
                if pool is None:
                    err_list.append(f"Did not find Pool with name {name}.")
                else:
                    success_list.append(f"Found Pool with name {name}. ")
                    try:
                        result = self.gateway.untag_subscriber_resource(
                            self.serial,
                            pool.resourceId,
                            UnSubscribeResourceTypes.STORAGE_POOL,
                        )
                        success_list.append(
                            f"Successfully unsubscribed Pool with name {name}. "
                        )
                        logger.writeDebug(f"PV:unsubscribe:result = {result}")
                    except Exception as ex:
                        logger.writeDebug(f"PV:unsubscribe:ex = {ex}")
                        err_list.append(str(ex))
            except Exception as ex:
                logger.writeDebug(f"PV:unsubscribe:ex = {ex}")
                err_list.append(str(ex))

        return err_list, success_list

    @log_entry_exit
    def unsubscribe_iscsi_targets(self, iscsi_targets):
        err_list = []
        success_list = []
        for iscsi_info in iscsi_targets:
            ss = iscsi_info.split(",")
            port = ss[0]
            name = ss[1]
            if port is None or port == "":
                err_list.append("Port name is not provided.")
            if name is None or name == "":
                err_list.append("ISCSI target name is not provided.")
            if port is None or port == "" or name is None or name == "":
                continue
            try:
                iscsi_target = self.get_iscsi_target_by_port_and_name(
                    port.strip(), name.strip()
                )
                if iscsi_target is None:
                    err_list.append(
                        f"Did not find ISCSI Target with name {name} on port {port}."
                    )
                else:
                    success_list.append(
                        f"Found ISCSI Target with name {name} on port {port}."
                    )
                    try:
                        result = self.gateway.untag_subscriber_resource(
                            self.serial,
                            iscsi_target.resourceId,
                            UnSubscribeResourceTypes.ISCSI_TARGET,
                        )
                        success_list.append(
                            f"Successfully unsubscribed ISCSI Target with name {name} on port {port}."
                        )
                        logger.writeDebug(f"PV:unsubscribe:result = {result}")
                    except Exception as ex:
                        logger.writeDebug(f"PV:unsubscribe:ex = {ex}")
                        err_list.append(str(ex))
            except Exception as ex:
                logger.writeDebug(f"PV:unsubscribe:ex = {ex}")
                err_list.append(str(ex))

        return err_list, success_list

    @log_entry_exit
    def unsubscribe_shadow_image(self, localpair_ids):
        err_list = []
        success_list = []

        for id in localpair_ids:
            try:
                si = self.get_shadowimage_by_id(id)
                logger.writeDebug(f"PV:unsubscribe:si = {si}")
                if si is None:
                    err_list.append(f"Did not find shadowimage with ID {id}.")
                else:
                    success_list.append(f"Found shadowimage with ID {id}. ")
                    try:
                        result = self.gateway.untag_subscriber_resource(
                            self.serial, si.resourceId, "shadowimage"
                        )
                        success_list.append(
                            f"Successfully unsubscribed sdadowimage with ID {id}. "
                        )
                        logger.writeDebug(f"PV:unsubscribe:result = {result}")
                    except Exception as ex:
                        logger.writeDebug(f"PV:unsubscribe:ex = {ex}")
                        err_list.append(str(ex))
            except Exception as ex:
                logger.writeDebug(f"PV:unsubscribe:ex = {ex}")
                err_list.append(str(ex) + " " + id + ".")
        return err_list, success_list

    @log_entry_exit
    def unsubscribe(self, spec):

        resources = spec.resources

        err_list = []
        success_list = []

        for x in resources:

            if x["type"].lower() == UnSubscribeResourceTypes.HOST_GROUP.lower():
                e_list, s_list = self.unsubscribe_hg(x["values"])
                err_list.extend(e_list)
                success_list.extend(s_list)

            if x["type"].lower() == UnSubscribeResourceTypes.VOLUME:
                e_list, s_list = self.unsubscribe_volume(x["values"])
                err_list.extend(e_list)
                success_list.extend(s_list)

            if x["type"].lower() == UnSubscribeResourceTypes.STORAGE_POOL.lower():
                e_list, s_list = self.unsubscribe_pool(x["values"])
                err_list.extend(e_list)
                success_list.extend(s_list)

            if x["type"].lower() == UnSubscribeResourceTypes.ISCSI_TARGET.lower():
                e_list, s_list = self.unsubscribe_iscsi_targets(x["values"])
                err_list.extend(e_list)
                success_list.extend(s_list)

            #  Keep port always at the end as it is used by other resources
            if x["type"].lower() == UnSubscribeResourceTypes.PORT:
                e_list, s_list = self.unsubscribe_port(x["values"])
                err_list.extend(e_list)
                success_list.extend(s_list)

            # if x["type"].lower() == UnSubscribeResourceTypes.SHADOW_IMAGE:
            #     e_list, s_list = self.unsubscribe_shadow_image(x["values"])
            #     err_list.extend(e_list)
            #     success_list.extend(s_list)

        return err_list, success_list

    @log_entry_exit
    def get_resource_id(self):
        resource_id = UAIGResourceID().storage_resourceId(self.serial)
        logger.writeDebug(
            "PV:get_resource_id:serial = {}  resourceId = {}", self.serial, resource_id
        )
        return resource_id

    @log_entry_exit
    def get_hg_by_port_and_name(self, port, name):
        hgs = self.hg_gateway.get_host_groups_for_resource_id(self.get_resource_id())
        logger.writeDebug("PROV:get_hg_by_name:hgs = {}", hgs)

        for hg in hgs.data:

            if hg.port == port and hg.hostGroupName == name:
                return hg

        return None

    @log_entry_exit
    def get_volume_by_ldev_id(self, id):
        device_id = UAIGResourceID().storage_resourceId(self.serial)
        volumes = self.vol_gw.get_volumes(device_id)
        # return vol_gw.get_volume_by_id(device_id, primary_volume_id)
        logger.writeDebug(f"PROV:get_volume_by_id:volumes: {volumes}")

        for v in volumes.data:
            logger.writeDebug(
                f"PROV:get_volume_by_id:volumes: {v.storageVolumeInfo['ldevId']} "
            )
            if str(v.storageVolumeInfo["ldevId"]) == str(id):
                return v
        return None

    @log_entry_exit
    def get_port_by_id(self, port_id):
        self.sp_gateway.set_serial(self.serial)
        self.sp_gateway.set_resource_id()
        ports = self.sp_gateway.get_all_storage_ports()
        for port in ports.data:
            if port.resourceId == port_id:
                return port

        return None

    @log_entry_exit
    def get_pool_by_name(self, name):
        pool_prov = VSPStoragePoolProvisioner(self.connection_info)
        pool_prov.check_ucp_system(self.serial)
        storage_pool = pool_prov.get_storage_pool_by_name_or_id(pool_name=name)

        return storage_pool

    @log_entry_exit
    def get_iscsi_target_by_port_and_name(self, port, name):
        iscsi_prov = VSPIscsiTargetProvisioner(self.connection_info)
        iscsi_targets = iscsi_prov.get_all_iscsi_targets(self.serial)
        for iscsi_target in iscsi_targets.data:
            if (
                iscsi_target.iscsiName == name
                and iscsi_target.portId == port
                and iscsi_target.subscriberId == self.connection_info.subscriber_id
            ):
                return iscsi_target
        return None

    @log_entry_exit
    def get_shadowimage_by_id(self, id):
        si_prov = VSPShadowImagePairProvisioner(self.connection_info)
        return si_prov.get_shadow_image_pair_by_id(self.serial, id)
