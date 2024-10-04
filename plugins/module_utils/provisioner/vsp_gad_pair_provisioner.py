import time


try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes
    from ..common.ansible_common import log_entry_exit, convert_hex_to_dec
    from ..message.vsp_gad_pair_msgs import GADPairValidateMSG
    from ..provisioner.vsp_storage_system_provisioner import VSPStorageSystemProvisioner
    from ..common.hv_constants import CommonConstants
    from ..common.vsp_constants import PairStatus
    from ..provisioner.vsp_host_group_provisioner import VSPHostGroupProvisioner
    from ..model.vsp_gad_pairs_models import (
        GADPairFactSpec,
        HostgroupSpec,
        VspGadPairSpec,
    )

except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes
    from common.ansible_common import log_entry_exit, convert_hex_to_dec
    from message.vsp_gad_pair_msgs import GADPairValidateMSG
    from provisioner.vsp_storage_system_provisioner import VSPStorageSystemProvisioner
    from common.hv_constants import CommonConstants
    from common.vsp_constants import PairStatus
    from provisioner.vsp_host_group_provisioner import VSPHostGroupProvisioner
    from model.vsp_gad_pairs_models import (
        GADPairFactSpec,
        HostgroupSpec,
        VspGadPairSpec,
    )


class GADPairProvisioner:

    def __init__(self, connection_info):
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_GAD_PAIR
        )
        self.storage_prov = VSPStorageSystemProvisioner(connection_info)
        self.connection_info = connection_info
        self.connection_type = connection_info.connection_type
        self.serial = None

    @log_entry_exit
    def create_gad_pair(self, gad_pair_spec):
        secondary_system_serial = self.get_secondary_storage_system_serial(
            gad_pair_spec.secondary_storage_serial_number
        )
        gad_pair_spec.remote_ucp_system = secondary_system_serial
        self.validate_hg_details(gad_pair_spec)
        _ = self.gateway.create_gad_pair(gad_pair_spec)
        self.connection_info.changed = True
        pairs = self.get_gad_pair_by_id(gad_pair_spec.primary_volume_id)
        count = 0
        while not pairs and count < 15:
            time.sleep(5)
            pairs = self.get_gad_pair_by_id(gad_pair_spec.primary_volume_id)
            count += 1
        return pairs

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
                raise ValueError(
                    GADPairValidateMSG.PRIMARY_HG_NOT_FOUND.value.format(names)
                )
            spec.primary_hostgroups = hg_real

        if spec.secondary_hostgroups:
            hgs = hg_prov.get_all_host_groups(spec.secondary_storage_serial_number)
            real_sec_hg = assign_hgs(hgs, spec.secondary_hostgroups)
            if len(spec.secondary_hostgroups) > 0:
                names = [hg.name for hg in spec.secondary_hostgroups]
                raise ValueError(
                    GADPairValidateMSG.SEC_HG_NOT_FOUND.value.format(names)
                )
            spec.secondary_hostgroups = real_sec_hg

    @log_entry_exit
    def get_gad_pair_by_pvol_id(self, volume_id):
        pairs = self.get_all_gad_pairs()
        for pair in pairs.data:
            if pair.primaryVolumeId == volume_id:
                return pair

    @log_entry_exit
    def get_all_gad_pairs(self):
        pairs = self.gateway.get_all_gad_pairs()
        return pairs

    @log_entry_exit
    def get_gad_pair_by_id(self, gad_pair_id):
        pairs = self.get_all_gad_pairs()
        for pair in pairs.data:
            if (pair.resourceId == gad_pair_id) or (
                pair.primaryVolumeId == gad_pair_id
            ):
                return pair

    @log_entry_exit
    def delete_gad_pair(self, gad_pair):

        _ = self.gateway.delete_gad_pair(gad_pair.resourceId)
        self.connection_info.changed = True
        return GADPairValidateMSG.DELETE_GAD_PAIR_SUCCESS.value

    @log_entry_exit
    def split_gad_pair(self, gad_pair):
        if gad_pair.status == PairStatus.PSUS:
            return gad_pair
        _ = self.gateway.split_gad_pair(gad_pair.resourceId)
        self.connection_info.changed = True
        return self.get_gad_pair_by_id(gad_pair.primaryVolumeId)

    @log_entry_exit
    def resync_gad_pair(self, gad_pair):
        if gad_pair.status == PairStatus.PAIR:
            return gad_pair
        _ = self.gateway.resync_gad_pair(gad_pair.resourceId)
        self.connection_info.changed = True
        return self.get_gad_pair_by_id(gad_pair.primaryVolumeId)

    @log_entry_exit
    def gad_pair_facts(self, gad_pair_facts_spec):
        if gad_pair_facts_spec.primary_volume_id is not None:
            return self.get_gad_pair_by_id(gad_pair_facts_spec.primary_volume_id)
        return self.gateway.get_all_gad_pairs()

    @log_entry_exit
    def get_secondary_storage_system_serial(self, serial_number):
        system = self.storage_prov.get_storage_ucp_system(serial_number)
        if not system:
            raise ValueError(GADPairValidateMSG.SECONDARY_SYSTEM_NT_FOUND.value)
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
