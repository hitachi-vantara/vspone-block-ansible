from typing import Optional, List, Dict, Any
try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes
    from ..common.uaig_utils import UAIGResourceID
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..model.vsp_hur_models import VSPHurPairInfoList
    from .vsp_true_copy_provisioner import RemoteReplicationHelperForSVol
    from ..message.vsp_hur_msgs import VSPHurValidateMsg
    from .vsp_true_copy_provisioner import RemoteReplicationHelperForSVol

except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes
    from common.uaig_utils import UAIGResourceID
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from model.vsp_storage_port_models import PortInfo, PortsInfo
    from model.vsp_hur_models import VSPHurPairInfoList
    from message.vsp_hur_msgs import VSPHurValidateMsg
    from vsp_true_copy_provisioner import RemoteReplicationHelperForSVol


class VSPVolTierProvisioner:

    def __init__(self, connection_info, serial):
        self.logger = Log()
        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.VSP_VOL_TIER
        )
        self.connection_info = connection_info
        self.serial = serial
        self.gateway.set_storage_serial_number(serial)
        
    ## 20240822 - apply_vol_tiering
    @log_entry_exit
    def apply_vol_tiering(self, spec) -> Dict[str, Any]:
        
        # consistency_group_id = spec.consistency_group_id or -1
        # enable_delta_resync = spec.enable_delta_resync or False
   
        resourceId = self.gateway.apply_vol_tiering(
            spec.ldev_id,
            spec.is_relocation_enabled,
            spec.tier_level_for_new_page_allocation,
            spec.tier_level,
            spec.tier1_allocation_rate_min,
            spec.tier1_allocation_rate_max,
            spec.tier3_allocation_rate_min,
            spec.tier3_allocation_rate_max,
        )
        
        self.logger.writeDebug(f"resourceId: {resourceId}")
        
        return

    @log_entry_exit
    def check_storage_in_ucpsystem(self) -> bool:
        return self.gateway.check_storage_in_ucpsystem()