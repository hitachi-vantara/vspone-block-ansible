try:
    from .gateway_manager import SDSBConnectionManager
    from ..common.hv_log import Log
    from ..common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from ..model.sdsb_storage_node_models import (
        SDSBStorageNodeInfo,
        SDSBStorageNodeInfoList,
    )
except ImportError:
    from .gateway_manager import SDSBConnectionManager
    from common.hv_log import Log
    from common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from model.sdsb_storage_node_models import (
        SDSBStorageNodeInfo,
        SDSBStorageNodeInfoList,
    )

GET_STORAGE_NODES = "v1/objects/storage-nodes"
GET_STORAGE_NODES_WITH_QUERY = "v1/objects/storage-nodes{}"
GET_STORAGE_NODE_BY_ID = "v1/objects/storage-nodes/{}"
BLOCK_FOR_MAINTENANCE = (
    "v1/objects/storage-nodes/{}/actions/block-for-maintenance/invoke"
)
RESTORE_FROM_MAINTENANCE = "v1/objects/storage-nodes/{}/actions/recover/invoke"


logger = Log()


class SDSBStorageNodeDirectGateway:

    def __init__(self, connection_info):
        self.connection_manager = SDSBConnectionManager(
            connection_info.address, connection_info.username, connection_info.password
        )

    @log_entry_exit
    def get_query_parameters(
        self,
        fault_domain_id=None,
        name=None,
        cluster_role=None,
        protection_domain_id=None,
    ):
        # logger.writeDebug(f"fault_domain_id={fault_domain_id}, name={name}, cluster_role={cluster_role}, protection_domain_id={protection_domain_id}")
        first = True
        query = ""
        if fault_domain_id:
            query = query + f"?faultDomainId={fault_domain_id}"
            first = False
        if name:
            if first:
                query = query + f"?name={name}"
                first = False
            else:
                query = query + f"&name={name}"
        if cluster_role:
            if first:
                query = query + f"?clusterRole={cluster_role}"
                first = False
            else:
                query = query + f"&clusterRole={cluster_role}"
        if protection_domain_id:
            if first:
                query = query + f"?protectionDomainId={protection_domain_id}"
                first = False
            else:
                query = query + f"&protectionDomainId={protection_domain_id}"
        return query

    @log_entry_exit
    def get_storage_nodes(
        self,
        fault_domain_id=None,
        name=None,
        cluster_role=None,
        protection_domain_id=None,
    ):
        if (
            fault_domain_id is None
            and name is None
            and cluster_role is None
            and protection_domain_id is None
        ):
            end_point = GET_STORAGE_NODES
        else:
            query = self.get_query_parameters(
                fault_domain_id, name, cluster_role, protection_domain_id
            )
            end_point = GET_STORAGE_NODES_WITH_QUERY.format(query)

        storage_node_data = self.connection_manager.get(end_point)

        return SDSBStorageNodeInfoList(
            dicts_to_dataclass_list(storage_node_data["data"], SDSBStorageNodeInfo)
        )

    @log_entry_exit
    def block_node_for_maintenance(self, id):
        end_point = BLOCK_FOR_MAINTENANCE.format(id)
        resp = self.connection_manager.post(end_point, data=None)
        logger.writeDebug(f"GW:block_node_for_maintenance:resp={resp}")
        return resp

    @log_entry_exit
    def restore_from_maintenance(self, id):
        end_point = RESTORE_FROM_MAINTENANCE.format(id)
        resp = self.connection_manager.post(end_point, data=None)
        logger.writeDebug(f"GW:restore_from_maintenance:resp={resp}")
        return resp

    @log_entry_exit
    def get_storage_node_by_id(self, id):
        end_point = GET_STORAGE_NODE_BY_ID.format(id)
        storage_node_data = self.connection_manager.get(end_point)
        return SDSBStorageNodeInfo(**storage_node_data)
