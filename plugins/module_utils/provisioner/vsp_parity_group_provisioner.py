try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes
    from ..common.ansible_common import log_entry_exit, convert_block_capacity
    from ..model.vsp_parity_group_models import *
except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes
    from common.ansible_common import log_entry_exit, convert_block_capacity
    from model.vsp_parity_group_models import *


class VSPParityGroupProvisioner:

    def __init__(self, connection_info):
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_PARITY_GROUP
        )

    @log_entry_exit
    def format_parity_group(self, parity_group):
        pg_dict = {}
        pg_dict["parityGroupId"] = parity_group.parityGroupId
        if parity_group.availableVolumeCapacity is not None:
            pg_dict["freeCapacity"] = (
                convert_block_capacity(
                    parity_group.availableVolumeCapacity * 1024 * 1024 * 1024, 1
                )
                if parity_group.availableVolumeCapacity != 0
                else "0"
            )
        else:
            None
        if parity_group.physicalCapacity is not None:
            pg_dict["totalCapacity"] = (
                convert_block_capacity(
                    parity_group.physicalCapacity * 1024 * 1024 * 1024, 1
                )
                if parity_group.physicalCapacity != 0
                else "0"
            )
        else:
            if parity_group.totalCapacity is not None:
                pg_dict["totalCapacity"] = (
                    convert_block_capacity(
                        parity_group.totalCapacity * 1024 * 1024 * 1024, 1
                    )
                    if parity_group.totalCapacity != 0
                    else "0"
                )
            else:
                None
        pg_dict["ldevIds"] = []
        count_query = "count={}".format(16384)
        pg_query = "parityGroupId={}".format(parity_group.parityGroupId)
        pg_vol_query = "?" + count_query + "&" + pg_query
        ldevs = self.gateway.get_ldevs(pg_vol_query)
        for ldev in ldevs.data:
            pg_dict["ldevIds"].append(ldev.ldevId)
        pg_dict["raidLevel"] = parity_group.raidLevel
        pg_dict["driveType"] = parity_group.driveTypeName
        pg_dict["copybackMode"] = parity_group.isCopyBackModeEnabled
        pg_dict["isAcceleratedCompression"] = (
            parity_group.isAcceleratedCompressionEnabled
        )
        pg_dict["isEncryptionEnabled"] = parity_group.isEncryptionEnabled
        return pg_dict

    @log_entry_exit
    def format_external_parity_group(self, external_parity_group):
        pg_dict = {}
        pg_dict["parityGroupId"] = "E" + external_parity_group.externalParityGroupId
        if external_parity_group.availableVolumeCapacity is not None:
            if external_parity_group.availableVolumeCapacity != 0:
                pg_dict["freeCapacity"] = convert_block_capacity(
                    external_parity_group.availableVolumeCapacity * 1024 * 1024 * 1024,
                    1,
                )
            else:
                pg_dict["freeCapacity"] = "0"
        else:
            pg_dict["freeCapacity"] = None
        total_capacity = 0
        if external_parity_group.spaces is not None:
            if len(external_parity_group.spaces) > 0:
                for space in external_parity_group.spaces:
                    if space.lbaSize is not None:
                        if space.lbaSize.startswith("0x"):
                            total_capacity += int(space.lbaSize[2:], 16) * 512
                        else:
                            total_capacity += int(space.lbaSize, 16) * 512
                    else:
                        total_capacity = -1
            else:
                total_capacity = 0
        else:
            if external_parity_group.availableVolumeCapacity is not None:
                if (
                    external_parity_group.availableVolumeCapacity != 0
                    and external_parity_group.usedCapacityRate != 100
                ):
                    total_capacity = (
                        external_parity_group.availableVolumeCapacity
                        * 1024
                        * 1024
                        * 1024
                        * 100
                    ) / (100 - external_parity_group.usedCapacityRate)
                else:
                    total_capacity = 0
            else:
                total_capacity = -1
        if total_capacity != 0:
            pg_dict["totalCapacity"] = (
                convert_block_capacity(total_capacity, 1)
                if total_capacity != -1
                else None
            )
        else:
            pg_dict["totalCapacity"] = "0"
        return pg_dict

    @log_entry_exit
    def get_all_parity_groups(self):
        tmp_parity_groups = []
        # Get a list of parity groups
        parity_groups = self.gateway.get_all_parity_groups()
        for parity_group in parity_groups.data:
            tmp_parity_groups.append(
                VSPParityGroup(**self.format_parity_group(parity_group))
            )
        # Get a list of external parity groups
        external_parity_groups = self.gateway.get_all_external_parity_groups()
        for external_parity_group in external_parity_groups.data:
            tmp_parity_groups.append(
                VSPParityGroup(
                    **self.format_external_parity_group(external_parity_group)
                )
            )

        return VSPParityGroups(tmp_parity_groups)

    @log_entry_exit
    def get_parity_group(self, pg_id):
        if pg_id.strip().startswith("E"):
            external_parity_group = self.gateway.get_external_parity_group(pg_id[1:])
            return VSPParityGroup(
                **self.format_external_parity_group(external_parity_group)
            )
        else:
            parity_group = self.gateway.get_parity_group(pg_id)
            return VSPParityGroup(**self.format_parity_group(parity_group))
