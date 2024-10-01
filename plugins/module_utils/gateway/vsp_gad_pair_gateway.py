try:
    from .gateway_manager import UAIGConnectionManager
    from ..common.hv_constants import CommonConstants, HEADER_NAME_CONSTANT
    from ..common.uaig_constants import Endpoints as UAIGEndpoints
    from ..model.vsp_gad_pairs_models import (
        VspGadPairSpec,
        VspGadPairInfo,
        VspGadPairsInfo,
    )
    from ..common.uaig_constants import GADPairConst
    from ..common.ansible_common import log_entry_exit, convert_hex_to_dec

except ImportError:
    from .gateway_manager import UAIGConnectionManager
    from common.hv_constants import CommonConstants, HEADER_NAME_CONSTANT
    from common.uaig_constants import Endpoints as UAIGEndpoints
    from model.vsp_gad_pairs_models import (
        VspGadPairSpec,
        VspGadPairInfo,
        VspGadPairsInfo,
    )
    from common.uaig_constants import GADPairConst
    from common.ansible_common import log_entry_exit, convert_hex_to_dec


class GADPairUAIGateway:

    def __init__(self, connection_info):
        self.connectionManager = UAIGConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )

        ## Set the resource id
        self.serial_number = None
        self.resource_id = None

        ## Set the headers
        self.headers = {HEADER_NAME_CONSTANT.PARTNER_ID: CommonConstants.PARTNER_ID}
        if connection_info.subscriber_id is not None:
            self.headers[HEADER_NAME_CONSTANT.SUBSCRIBER_ID] = (
                connection_info.subscriber_id
            )
        self.UCP_SYSTEM = CommonConstants.UCP_SERIAL

    @log_entry_exit
    def get_all_gad_pairs_v2(self):
        ## Get the storage pools
        endPoint = UAIGEndpoints.GET_REPLICATION_PAIRS.format(self.resource_id)
        gadPairsDict = self.connectionManager.get(endPoint)
        return VspGadPairsInfo().dump_to_object(gadPairsDict)

    @log_entry_exit
    def get_all_gad_pairs(self):
        ## Get the storage pools
        endPoint = UAIGEndpoints.GET_GAD_PAIRS_V3.format(self.resource_id)
        gadPairsDict = self.connectionManager.get(endPoint, headers_input=self.headers)
        return VspGadPairsInfo().dump_to_object(gadPairsDict)

    @log_entry_exit
    def delete_gad_pair(self, gad_pair_id):
        ## delete_gad_pair
        endPoint = (
            UAIGEndpoints.GAD_SINGLE_PAIR_V3.format(self.resource_id, gad_pair_id)
            + "?isDelete=true"
        )
        return self.connectionManager.delete(endPoint, headers_input=self.headers)

    @log_entry_exit
    def split_gad_pair(self, gad_pair_id):
        ## split_gad_pair
        endPoint = UAIGEndpoints.SPLIT_GAD_PAIR_V3.format(self.resource_id, gad_pair_id)
        return self.connectionManager.patch(endPoint, headers_input=self.headers)

    @log_entry_exit
    def resync_gad_pair(self, gad_pair_id):
        ## resync_gad_pair
        endPoint = UAIGEndpoints.RESYNC_GAD_PAIR_V3.format(
            self.resource_id, gad_pair_id
        )
        return self.connectionManager.patch(endPoint, headers_input=self.headers)

    @log_entry_exit
    def create_gad_pair(self, spec: VspGadPairSpec):
        payload = {
            GADPairConst.PRIMARY_SERIAL_NUMBER: spec.primary_storage_serial_number,
            GADPairConst.PRIMARY_LUN_ID: spec.primary_volume_id,
            GADPairConst.SECONDARY_SERIAL_NUMBER: spec.secondary_storage_serial_number,
            GADPairConst.SECONDARY_POOL_ID: spec.secondary_pool_id,
            GADPairConst.UCP_SYSTEM: self.UCP_SYSTEM,
        }
        if spec.remote_ucp_system:
            payload[GADPairConst.REMOTE_UCP_SYSTEM] = spec.remote_ucp_system

        if spec.consistency_group_id:
            payload[GADPairConst.CONSISTENCY_GROUP_ID] = spec.consistency_group_id
        else:
            payload[GADPairConst.CONSISTENCY_GROUP_ID] = -1
        if spec.primary_hostgroups:
            payload[GADPairConst.PRIMARY_HOSTGROUP_PAYLOADS] = self._append_hg_payload(
                spec.primary_hostgroups
            )

        if spec.secondary_hostgroups:
            payload[GADPairConst.SECONDARY_HOSTGROUP_PAYLOADS] = (
                self._append_hg_payload(spec.secondary_hostgroups)
            )

        if spec.allocate_new_consistency_group:
            payload[GADPairConst.NEW_CONSISTENCY_GROUP] = (
                spec.allocate_new_consistency_group
            )

        if spec.set_alua_mode:
            payload[GADPairConst.SET_ALUA_MODE] = spec.set_alua_mode
        if spec.primary_resource_group_name:
            payload[GADPairConst.PRIMARY_RESOURCE_GROUP_PAYLOAD] = {
                GADPairConst.NAME: spec.primary_resource_group_name
            }
        if spec.secondary_resource_group_name:
            payload[GADPairConst.VIRTUAL_RESOURCE_GROUP_PAYLOAD] = {
                GADPairConst.NAME: spec.secondary_resource_group_name
            }
        if spec.quorum_disk_id:
            payload[GADPairConst.QUORUM_DISK_ID] = spec.quorum_disk_id

        endPoint = UAIGEndpoints.POST_GAD_PAIR
        return self.connectionManager.post_subtask_ext(
            endPoint, data=payload, headers_input=self.headers
        )

    def _append_hg_payload(self, input_data):
        list_hgs = []
        for hg in input_data:
            dict_hg = {}
            dict_hg[GADPairConst.HOST_GROUP_ID] = hg.id
            dict_hg[GADPairConst.NAME] = hg.name
            dict_hg[GADPairConst.PORT] = hg.port
            dict_hg[GADPairConst.RESOURCE_GROUP_ID] = hg.resource_group_id
            if hg.enable_preferred_path:
                dict_hg[GADPairConst.ENABLE_PREFERRED_PATH] = hg.enable_preferred_path
            list_hgs.append(dict_hg)
        return list_hgs
