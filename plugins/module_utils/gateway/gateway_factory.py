

try:
    from ..common.hv_constants import ConnectionTypes, GatewayClassTypes
except ImportError:
    # created a soft link from the current directory to avoid import error
    from common.hv_constants import ConnectionTypes, GatewayClassTypes

from .sdsb_compute_node_gateway import SDSBComputeNodeUAIGateway, SDSBComputeNodeDirectGateway
from .sdsb_volume_gateway import SDSBVolumeUAIGateway,SDSBVolumeDirectGateway
from .sdsb_chap_user_gateway import SDSBChapUsereUAIGateway,SDSBChapUserDirectGateway
from .sdsb_pool_gateway import SDSBPoolDirectGateway
from .sdsb_port_auth_gateway import SDSBPortAuthDirectGateway
from .sdsb_port_gateway import SDSBPortDirectGateway
from .sdsb_vps_gateway import SDSBVpsDirectGateway

from .vsp_snapshot_gateway import VSPHtiSnapshotDirectGateway,VSPHtiSnapshotUaiGateway

from .vsp_volume import VSPVolumeDirectGateway,VSPVolumeUAIGateway
from .vsp_host_group_gateway import VSPHostGroupDirectGateway, VSPHostGroupUAIGateway
from .vsp_shadow_image_pair_gateway import VSPShadowImagePairDirectGateway,VSPShadowImagePairUAIGateway
from .uaig_subscriber_gateway import SubscriberUAIGateway
from .uaig_subscriber_resource_gateway import SubscriberResourceUAIGateway
from .uaig_password_gateway import PasswordUAIGateway
from .vsp_storage_system_gateway import VSPStorageSystemDirectGateway, UAIGStorageSystemGateway
from .sdsb_storage_system_gateway import SDSBStorageSystemDirectGateway
from .vsp_iscsi_target_gateway import VSPIscsiTargetDirectGateway,VSPIscsiTargetUAIGateway
from .vsp_storage_pool_gateway import VSPStoragePoolDirectGateway, VSPStoragePoolUAIGateway
from .vsp_parity_group_gateway import VSPParityGroupDirectGateway, VSPParityGroupUAIGateway
from .vsp_storage_port_gateway import VSPStoragePortDirectGateway, VSPStoragePortUAIGateway
from .vsp_true_copy_gateway import  VSPTrueCopyUAIGateway
from .vsp_hur_gateway import  VSPHurUAIGateway
from .vsp_volume_tiering_gateway import  VSPVolTieringUAIGateway
from .vsp_nvme_gateway import VSPOneNvmeSubsystemDirectGateway
from .vsp_unsubscribe_gateway import VSPUnsubscribeUAIGateway

from .vsp_gad_pair_gateway import GADPairUAIGateway

GATEWAY_MAP = {
    ConnectionTypes.DIRECT: {
        GatewayClassTypes.VSP_VOLUME: VSPVolumeDirectGateway,
        GatewayClassTypes.VSP_HOST_GROUP: VSPHostGroupDirectGateway,
        GatewayClassTypes.VSP_SHADOW_IMAGE_PAIR: VSPShadowImagePairDirectGateway,
        GatewayClassTypes.VSP_STORAGE_SYSTEM: VSPStorageSystemDirectGateway,
        GatewayClassTypes.VSP_ISCSI_TARGET: VSPIscsiTargetDirectGateway,
        GatewayClassTypes.VSP_STORAGE_POOL: VSPStoragePoolDirectGateway,
        GatewayClassTypes.VSP_SNAPSHOT: VSPHtiSnapshotDirectGateway,
        GatewayClassTypes.VSP_PARITY_GROUP: VSPParityGroupDirectGateway,
        GatewayClassTypes.VSP_NVME_SUBSYSTEM: VSPOneNvmeSubsystemDirectGateway,
        # Add more mappings for direct connection types here
        GatewayClassTypes.SDSB_CHAP_USER: SDSBChapUserDirectGateway,
        GatewayClassTypes.SDSB_COMPUTE_NODE: SDSBComputeNodeDirectGateway,
        GatewayClassTypes.SDSB_STORAGE_SYSTEM: SDSBStorageSystemDirectGateway,
        GatewayClassTypes.SDSB_VOLUME: SDSBVolumeDirectGateway,
        GatewayClassTypes.SDSB_POOL: SDSBPoolDirectGateway,
        GatewayClassTypes.SDSB_PORT_AUTH:SDSBPortAuthDirectGateway,
        GatewayClassTypes.SDSB_PORT:SDSBPortDirectGateway,
        GatewayClassTypes.SDSB_VPS:SDSBVpsDirectGateway,
        GatewayClassTypes.STORAGE_PORT: VSPStoragePortDirectGateway,
    },
    ConnectionTypes.GATEWAY: {
        GatewayClassTypes.VSP_VOLUME: VSPVolumeUAIGateway,
        GatewayClassTypes.VSP_HOST_GROUP: VSPHostGroupUAIGateway,
        GatewayClassTypes.VSP_SNAPSHOT: VSPHtiSnapshotUaiGateway,
        GatewayClassTypes.VSP_SHADOW_IMAGE_PAIR: VSPShadowImagePairUAIGateway,
        GatewayClassTypes.VSP_ISCSI_TARGET: VSPIscsiTargetUAIGateway,
        # Add more mappings for uaig connection types here
        GatewayClassTypes.SDSB_CHAP_USER: SDSBChapUsereUAIGateway,
        GatewayClassTypes.SDSB_VOLUME: SDSBVolumeUAIGateway,
        GatewayClassTypes.SDSB_COMPUTE_NODE: SDSBComputeNodeUAIGateway,
        GatewayClassTypes.UAIG_SUBSCRIBER: SubscriberUAIGateway,
        GatewayClassTypes.UAIG_PASSWORD: PasswordUAIGateway,
        GatewayClassTypes.VSP_TRUE_COPY: VSPTrueCopyUAIGateway,
        GatewayClassTypes.VSP_HUR: VSPHurUAIGateway,
        GatewayClassTypes.VSP_VOL_TIER: VSPVolTieringUAIGateway,
        GatewayClassTypes.VSP_STORAGE_POOL:VSPStoragePoolUAIGateway,
        GatewayClassTypes.VSP_PARITY_GROUP: VSPParityGroupUAIGateway,
        GatewayClassTypes.STORAGE_PORT: VSPStoragePortUAIGateway,
        GatewayClassTypes.VSP_GAD_PAIR: GADPairUAIGateway,
        GatewayClassTypes.VSP_STORAGE_SYSTEM: UAIGStorageSystemGateway,
        GatewayClassTypes.UAIG_SUBSCRIBER_RESOURCE: SubscriberResourceUAIGateway,
        GatewayClassTypes.VSP_UNSUBSCRIBE:  VSPUnsubscribeUAIGateway      
    },
}


class GatewayFactory:
    """Factory class to get the gateway object"""

    @staticmethod
    def get_gateway(connection_info, gateway_type):
        """
        it takes the connection_info and the gateway_type argument and returns the gateway object
        """
        connection_map = GATEWAY_MAP.get(connection_info.connection_type.lower())
        if not connection_map:
            raise ValueError(
                f"Unsupported connection type: {connection_info.connection_type}"
            )

        gateway_class = connection_map.get(gateway_type)
        if not gateway_class:
            raise ValueError(f"Unsupported gateway type: {gateway_type}")

        return gateway_class(connection_info)
