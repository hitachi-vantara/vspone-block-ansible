import time

try:

    from .gateway_manager import VSPConnectionManager, UAIGConnectionManager
    from ..common.hv_constants import CommonConstants
    from ..common.hv_log import Log
    from ..common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from ..common.uaig_utils import UAIGResourceID
    from ..common.vsp_storage_models import VSPStorageModelsManager
    from ..model.vsp_resource_group_models import (
        VspResourceGroupInfo,
        VspResourceGroupInfoList,
        VirtualStorageMachineInfo,
        VirtualStorageMachineInfoList,
        UaigResourceGroupInfo,
        UaigResourceGroupInfoList,
    )
    from ..message.vsp_resource_group_msgs import VSPResourceGroupValidateMsg
    from ..hv_ucpmanager import UcpManager
except ImportError:
    from .gateway_manager import VSPConnectionManager, UAIGConnectionManager
    from common.hv_constants import CommonConstants
    from common.hv_log import Log
    from common.ansible_common import dicts_to_dataclass_list, log_entry_exit
    from common.vsp_storage_models import VSPStorageModelsManager
    from common.uaig_utils import UAIGResourceID
    from model.vsp_resource_group_models import (
        VspResourceGroupInfo,
        VspResourceGroupInfoList,
        VirtualStorageMachineInfo,
        VirtualStorageMachineInfoList,
        UaigResourceGroupInfo,
        UaigResourceGroupInfoList,
    )
    from message.vsp_resource_group_msgs import VSPResourceGroupValidateMsg
    from hv_ucpmanager import UcpManager

GET_RESOURCE_GROUPS_DIRECT = "v1/objects/resource-groups"
GET_RESOURCE_GROUPS_WITH_PARAM_DIRECT = "v1/objects/resource-groups{}"
GET_RESOURCE_GROUP_BY_ID_DIRECT = (
    "v1/objects/resource-groups/{}?detailInfoType=nvmSubsystemIds"
)
GET_RESOURCE_GROUP_BY_ID_NO_DETAIL_DIRECT = "v1/objects/resource-groups/{}"
CREATE_RESOURCE_GROUP_DIRECT = "v1/objects/resource-groups"
ADD_RESOURCE_TO_RESOURCE_GROUP_DIRECT = (
    "v1/objects/resource-groups/{}/actions/add-resource/invoke"
)
REMOVE_RESOURCE_FROM_RESOURCE_GROUP_DIRECT = (
    "v1/objects/resource-groups/{}/actions/remove-resource/invoke"
)
DELETE_RESOURCE_GROUP_DIRECT = "v1/objects/resource-groups/{}"
GET_LDEVS_BY_POOL_ID_DIRECT = "v1/objects/ldevs?poolId={}"
GET_STORAGE_DEVICE_ID_BY_SERIAL_DIRECT = "v1/objects/storages"
GET_VIRTUAL_STORAGE_DEVICE_ID_DIRECT = "v1/objects/storages/{}/virtual-storages"
GET_DP_POOLS_DIRECT = "v1/objects/storages/{}/pools?poolType=DP"
GET_HTI_POOLS_DIRECT = "v1/objects/storages/{}/pools?poolType=HTI"
GET_LDEV_BY_ID_DIRECT = "v1/objects/storages/{}/ldevs/{}"

CREATE_VSM_RESOURCE_GROUP_DIRECT = "v1/objects/virtual-storages"
GET_VSM_BY_ID_DIRECT = "v1/objects/virtual-storages/{}"
GET_VSM_DIRECT = "v1/objects/virtual-storages"

# UAIGateway V2 API
GET_RESOURCE_GROUPS_UAI_V2 = "v2/storage/devices/{}/resourceGroups?{}"
ADD_ISCSI_TARGETS_TO_RESOURCE_GROUP_UAI_V2 = (
    "v2/storage/devices/{}/resourceGroups/{}/iscsiTargets"
)
ADD_HOST_GROUPS_TO_RESOURCE_GROUP_UAI_V2 = (
    "v2/storage/devices/{}/resourceGroups/{}/hostGroups"
)
ADD_LDEVS_TO_RESOURCE_GROUP_UAI_V2 = "v2/storage/devices/{}/resourceGroups/{}/volumes"
ADD_PORTS_TO_RESOURCE_GROUP_UAI_V2 = "v2/storage/devices/{}/resourceGroups/{}/ports"
ADD_POOLS_TO_RESOURCE_GROUP_UAI_V2 = "v2/storage/devices/{}/resourceGroups/{}/pools"
ADD_PARITY_GROUPS_TO_RESOURCE_GROUP_UAI_V2 = (
    "v2/storage/devices/{}/resourceGroups/{}/parityGroups"
)

REMOVE_ISCSI_TARGETS_FROM_RESOURCE_GROUP_UAI_V2 = (
    "v2/storage/devices/{}/resourceGroups/{}/iscsiTargets"
)
REMOVE_HOST_GROUPS_FROM_RESOURCE_GROUP_UAI_V2 = (
    "v2/storage/devices/{}/resourceGroups/{}/hostGroups"
)
REMOVE_LDEVS_FROM_RESOURCE_GROUP_UAI_V2 = (
    "v2/storage/devices/{}/resourceGroups/{}/volumes"
)
REMOVE_PORTS_FROM_RESOURCE_GROUP_UAI_V2 = (
    "v2/storage/devices/{}/resourceGroups/{}/ports"
)
REMOVE_POOLS_FROM_RESOURCE_GROUP_UAI_V2 = (
    "v2/storage/devices/{}/resourceGroups/{}/pools"
)
REMOVE_PARITY_GROUPS_FROM_RESOURCE_GROUP_UAI_V2 = (
    "v2/storage/devices/{}/resourceGroups/{}/parityGroups"
)
CREATE_RESOURCE_GROUP_UAI_V2 = "v2/storage/devices/{}/resourceGroups"
DELETE_RESOURCE_GROUP_UAI_V2 = "v2/storage/devices/{}/resourceGroups/{}"

logger = Log()

INPUT_TO_REST_MAP = {
    "ldevs": "ldevIds",
    "host_groups": "hostGroupIds",
    "ports": "portIds",
    "parity_groups": "parityGroupIds",
    "nvm_subsystem_ids": "nvmSubsystemIds",
}


class VSPResourceGroupDirectGateway:
    def __init__(self, connection_info):

        self.connection_manager = VSPConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )
        self.connection_info = connection_info
        self.serial = None

    @log_entry_exit
    def set_serial(self, serial=None):
        if serial:
            self.serial = serial
            logger.writeError(f"GW:set_serial={self.serial}")

    @log_entry_exit
    def get_resource_groups(self, spec=None, b_refresh=True):
        if spec is None:
            end_point = GET_RESOURCE_GROUPS_DIRECT
            resource_groups_date = self.connection_manager.get(end_point)
            resource_groups = VspResourceGroupInfoList(
                dicts_to_dataclass_list(
                    resource_groups_date["data"], VspResourceGroupInfo
                )
            )
            return resource_groups
        else:
            params = "?"
            if spec.is_locked is not None:
                if spec.is_locked is True:
                    params += "lockStatus=Locked"
                else:
                    params += "lockStatus=Unlocked"
                if spec.query:
                    my_query = []
                    for x in spec.query:
                        key = x.lower()
                        if key in INPUT_TO_REST_MAP:
                            my_query.append(INPUT_TO_REST_MAP[key])
                        else:
                            continue
                    my_query = ",".join(my_query)
                    if len(my_query) > 0:
                        params += "&attributes={}".format(my_query)
            else:
                if spec.query:
                    my_query = []
                    for x in spec.query:
                        key = x.lower()
                        if key in INPUT_TO_REST_MAP:
                            my_query.append(INPUT_TO_REST_MAP[key])
                        else:
                            continue
                    my_query = ",".join(my_query)
                    if len(my_query) > 0:
                        params += "attributes={}".format(my_query)

            if params == "?":
                end_point = GET_RESOURCE_GROUPS_DIRECT
            else:
                end_point = GET_RESOURCE_GROUPS_WITH_PARAM_DIRECT.format(params)
            resource_groups_date = self.connection_manager.get(end_point)
            resource_groups = VspResourceGroupInfoList(
                dicts_to_dataclass_list(
                    resource_groups_date["data"], VspResourceGroupInfo
                )
            )
            return resource_groups

    @log_entry_exit
    def get_remote_resource_groups(self, spec=None):
        if spec is None:
            raise ValueError("spec is required for remote resource groups")

        if spec.secondary_connection_info is None:
            raise ValueError(
                "secondary_connection_info is required for remote resource groups"
            )

        remote_connection_manager = VSPConnectionManager(
            spec.secondary_connection_info.address,
            spec.secondary_connection_info.username,
            spec.secondary_connection_info.password,
            spec.secondary_connection_info.api_token,
        )
        end_point = GET_RESOURCE_GROUPS_DIRECT
        resource_groups_date = remote_connection_manager.get(end_point)
        resource_groups = VspResourceGroupInfoList(
            dicts_to_dataclass_list(resource_groups_date["data"], VspResourceGroupInfo)
        )
        return resource_groups

    @log_entry_exit
    def get_resource_group_by_id(self, id):
        try:
            end_point = GET_RESOURCE_GROUP_BY_ID_DIRECT.format(id)
            resource_group = self.connection_manager.get(end_point)
            return VspResourceGroupInfo(**resource_group)
        except Exception as err:
            # Older storage models do not support nvm subsystem.
            # So catch the exception and try older method without nvmSubsystem.
            logger.writeError(err)
            API_MSG = (
                "The specified value is not supported for the specified storage system"
            )
            if isinstance(err.args[0], str) and API_MSG in err.args[0]:
                end_point = GET_RESOURCE_GROUP_BY_ID_NO_DETAIL_DIRECT.format(id)
                resource_group = self.connection_manager.get(end_point)
                return VspResourceGroupInfo(**resource_group)
            else:
                raise err

    @log_entry_exit
    def create_vsm_resource_group(self, spec):
        end_point = CREATE_VSM_RESOURCE_GROUP_DIRECT

        payload = {}
        payload["resourceGroupName"] = spec.name
        payload["virtualSerialNumber"] = spec.virtual_storage_serial
        virtual_storage_model = VSPStorageModelsManager.get_direct_storage_model(
            spec.virtual_storage_model
        )
        logger.writeDebug(
            "create_vsm_resource_group: virtual_storage_model= {}",
            virtual_storage_model,
        )
        payload["virtualModel"] = virtual_storage_model

        resource_group = self.connection_manager.post(end_point, payload)
        self.connection_info.changed = True
        return resource_group

    @log_entry_exit
    def create_resource_group(self, spec):
        end_point = CREATE_RESOURCE_GROUP_DIRECT

        payload = {}
        payload["resourceGroupName"] = spec.name

        # if spec.virtual_storage_id and spec.virtual_storage_device_id is None:
        #     payload["virtualStorageId"] = spec.virtual_storage_id
        if spec.virtual_storage_serial:
            virtual_storage_device_id = self.get_vitual_storage_device_id(
                spec.virtual_storage_serial
            )
            if virtual_storage_device_id is None:
                if spec.virtual_storage_model:
                    resource_group = self.create_vsm_resource_group(spec)
                    resource_group_id = self.get_rg_id_by_name(spec.name)
                    self.connection_info.changed = True
                    return resource_group_id

                else:
                    raise ValueError("Virtual Model must be specified to create a VSM.")
            else:
                payload["virtualStorageDeviceId"] = virtual_storage_device_id

        resource_group = self.connection_manager.post(end_point, payload)
        self.connection_info.changed = True
        return resource_group

    @log_entry_exit
    def get_rg_id_by_name(self, name):
        resource_groups = self.get_resource_groups()
        for resource_group in resource_groups.data:
            if resource_group.resourceGroupName == name:
                return resource_group.resourceGroupId
        return None

    @log_entry_exit
    def get_storage_device_id(self):
        end_point = GET_STORAGE_DEVICE_ID_BY_SERIAL_DIRECT
        device = self.connection_manager.get(end_point)
        return device["data"][0]["storageDeviceId"]

    @log_entry_exit
    def get_vitual_storage_device_id(self, virtual_storage_serial):
        storage_device_id = self.get_storage_device_id()
        end_point = GET_VIRTUAL_STORAGE_DEVICE_ID_DIRECT.format(storage_device_id)
        virtual_devices = self.connection_manager.get(end_point)
        for device in virtual_devices["data"]:
            if device["virtualSerialNumber"] == virtual_storage_serial:
                return device["virtualStorageDeviceId"]
        return None

    @log_entry_exit
    def get_vsm_by_id(self, vsm_id):
        end_point = GET_VSM_BY_ID_DIRECT.format(vsm_id)
        vsm = self.connection_manager.get(end_point)
        return VirtualStorageMachineInfo(**vsm)

    @log_entry_exit
    def get_vsm_all(self):
        end_point = GET_VSM_DIRECT
        vsm = self.connection_manager.get(end_point)
        return VirtualStorageMachineInfoList(
            dicts_to_dataclass_list(vsm["data"], VirtualStorageMachineInfo)
        )

    @log_entry_exit
    def get_rg_id_from_ldev_id(self, ldev_id):
        storage_device_id = self.get_storage_device_id()
        end_point = GET_LDEV_BY_ID_DIRECT.format(storage_device_id, ldev_id)
        ldev = self.connection_manager.get(end_point)
        return ldev["resourceGroupId"]

    @log_entry_exit
    def get_dp_pools(self):
        storage_device_id = self.get_storage_device_id()
        end_point = GET_DP_POOLS_DIRECT.format(storage_device_id)
        dp_pools = self.connection_manager.get(end_point)
        return dp_pools["data"]

    @log_entry_exit
    def get_hti_pools(self):
        storage_device_id = self.get_storage_device_id()
        end_point = GET_HTI_POOLS_DIRECT.format(storage_device_id)
        hti_pools = self.connection_manager.get(end_point)
        return hti_pools["data"]

    @log_entry_exit
    def add_resource(self, rg_id, spec):
        parameters = {}
        logger.writeDebug("add_resource spec= {}", spec)
        if spec.ldevs:
            parameters["ldevIds"] = spec.ldevs
        if spec.parity_groups:
            parameters["parityGroupIds"] = spec.parity_groups
        if spec.ports:
            parameters["portIds"] = spec.ports
        if spec.host_groups or spec.iscsi_targets:
            if spec.host_groups_simple and len(spec.host_groups_simple) > 0:
                parameters["hostGroupIds"] = spec.host_groups_simple
        if spec.nvm_subsystem_ids:
            parameters["nvmSubsystemIds"] = spec.nvm_subsystem_ids

        if len(parameters) == 0:
            return

        payload = {"parameters": parameters}
        end_point = ADD_RESOURCE_TO_RESOURCE_GROUP_DIRECT.format(rg_id)
        resource_group = self.connection_manager.post(end_point, payload)
        self.connection_info.changed = True
        return resource_group

    @log_entry_exit
    def remove_resource(self, rg_id, spec):
        parameters = {}

        if spec.ldevs:
            parameters["ldevIds"] = spec.ldevs
        if spec.parity_groups:
            parameters["parityGroupIds"] = spec.parity_groups
        if spec.ports:
            parameters["portIds"] = spec.ports
        if spec.host_groups:
            parameters["hostGroupIds"] = spec.host_groups_simple
        if spec.nvm_subsystem_ids:
            parameters["nvmSubsystemIds"] = spec.nvm_subsystem_ids

        if len(parameters) == 0:
            return

        payload = {"parameters": parameters}
        self.remove_resoure_with_payload(rg_id, payload)
        self.connection_info.changed = True

    @log_entry_exit
    def remove_resoure_with_payload(self, rg_id, payload):
        end_point = REMOVE_RESOURCE_FROM_RESOURCE_GROUP_DIRECT.format(rg_id)
        resource_group = self.connection_manager.post(end_point, payload)
        self.connection_info.changed = True
        return resource_group

    @log_entry_exit
    def delete_resource_group(self, rg_id):
        end_point = DELETE_RESOURCE_GROUP_DIRECT.format(rg_id)
        ret_data = self.connection_manager.delete(end_point)
        self.connection_info.changed = True
        return ret_data

    @log_entry_exit
    def get_pool_ldevs(self, pool_ids):
        pool_ldevs = []
        for pool_id in pool_ids:
            ldevs = self.get_ldevs_by_pool_id(pool_id)
            pool_ldevs += ldevs
        return pool_ldevs

    @log_entry_exit
    def get_ldevs_by_pool_id(self, pool_id):
        end_point = GET_LDEVS_BY_POOL_ID_DIRECT.format(pool_id)
        pool = self.connection_manager.get(end_point)
        ldevs = []
        for x in pool["data"]:
            ldevs.append(x["ldevId"])
        logger.writeDebug("LDEVS: {}", ldevs)
        return ldevs

    @log_entry_exit
    def delete_resource_group_force(self, rg):
        parameters = {}

        if hasattr(rg, "ldevIds") and rg.ldevIds:
            parameters["ldevIds"] = rg.ldevIds
        if hasattr(rg, "parityGroupIds") and rg.parityGroupIds:
            parameters["parityGroupIds"] = rg.parityGroupIds
        if hasattr(rg, "externalParityGroupIds") and rg.externalParityGroupIds:
            parameters["externalParityGroupIds"] = rg.externalParityGroupIds
        if hasattr(rg, "portIds") and rg.portIds:
            parameters["portIds"] = rg.portIds
        if hasattr(rg, "hostGroupIds") and rg.hostGroupIds:
            parameters["hostGroupIds"] = rg.hostGroupIds
        if hasattr(rg, "nvmSubsystemIds") and rg.nvmSubsystemIds:
            parameters["nvmSubsystemIds"] = rg.nvmSubsystemIds

        if bool(parameters):
            payload = {"parameters": parameters}
            self.remove_resoure_with_payload(rg.resourceGroupId, payload)

        self.delete_resource_group(rg.resourceGroupId)
        self.connection_info.changed = True


class VSPResourceGroupUAIGateway:
    def __init__(self, connection_info):

        self.connection_manager = UAIGConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )
        self.connection_info = connection_info
        self.serial = None

    @log_entry_exit
    def set_serial(self, serial=None):
        if serial:
            self.serial = serial
            logger.writeDebug(f"GW:set_serial={self.serial}")

    @log_entry_exit
    def get_resource_groups(self, spec=None, b_refresh=False):
        logger.writeDebug("GW:get_resource_groups:spec={}", spec)
        device_id = UAIGResourceID().storage_resourceId(self.serial)

        refresh = "refresh=false"
        if b_refresh is not None and b_refresh is True:
            refresh = "refresh=true"

        if spec is None:
            end_point = GET_RESOURCE_GROUPS_UAI_V2.format(device_id, refresh)
            resource_groups_date = self.connection_manager.get(end_point)
            resource_groups = UaigResourceGroupInfoList(
                dicts_to_dataclass_list(
                    resource_groups_date["data"], UaigResourceGroupInfo
                )
            )
            return resource_groups
        else:
            logger.writeDebug("GW:get_resource_groups:serial={}", self.serial)
            end_point = GET_RESOURCE_GROUPS_UAI_V2.format(device_id, refresh)
            resource_groups_date = self.connection_manager.get(end_point)
            resource_groups = UaigResourceGroupInfoList(
                dicts_to_dataclass_list(
                    resource_groups_date["data"], UaigResourceGroupInfo
                )
            )
            return resource_groups

    @log_entry_exit
    def add_resource(self, resource_id, spec):
        device_id = UAIGResourceID().storage_resourceId(self.serial)
        changed = False
        resource_group = None
        if spec.ldevs and len(spec.ldevs) > 0:
            end_point = ADD_LDEVS_TO_RESOURCE_GROUP_UAI_V2.format(
                device_id, resource_id
            )
            payload = {"ldevIds": spec.ldevs}
            resource_group = self.connection_manager.post(end_point, payload)
            changed = True
        if spec.parity_groups and len(spec.parity_groups) > 0:
            end_point = ADD_PARITY_GROUPS_TO_RESOURCE_GROUP_UAI_V2.format(
                device_id, resource_id
            )
            payload = {"parityGroupIds": spec.parity_groups}
            resource_group = self.connection_manager.post(end_point, payload)
            changed = True
        if spec.ports and len(spec.ports) > 0:
            end_point = ADD_PORTS_TO_RESOURCE_GROUP_UAI_V2.format(
                device_id, resource_id
            )
            payload = {"ports": spec.ports}
            resource_group = self.connection_manager.post(end_point, payload)
            changed = True
        if spec.host_groups and len(spec.host_groups) > 0:
            end_point = ADD_HOST_GROUPS_TO_RESOURCE_GROUP_UAI_V2.format(
                device_id, resource_id
            )
            host_groups = self.get_host_groups_for_gw_api(spec.host_groups)
            logger.writeDebug("PV:handle_storage_pools:host_groups_api={}", host_groups)
            payload = {"hostGroups": host_groups}
            resource_group = self.connection_manager.post(end_point, payload)
            changed = True
        if spec.iscsi_targets and len(spec.iscsi_targets) > 0:
            end_point = ADD_ISCSI_TARGETS_TO_RESOURCE_GROUP_UAI_V2.format(
                device_id, resource_id
            )
            iscsi_targets = self.get_iscsi_targets_for_gw_api(spec.iscsi_targets)
            payload = {"iscsiTargets": iscsi_targets}
            resource_group = self.connection_manager.post(end_point, payload)
            changed = True
        if spec.storage_pool_ids and len(spec.storage_pool_ids) > 0:
            end_point = ADD_POOLS_TO_RESOURCE_GROUP_UAI_V2.format(
                device_id, resource_id
            )
            payload = {"poolIds": spec.storage_pool_ids}
            resource_group = self.connection_manager.post(end_point, payload)
            changed = True
        self.connection_info.changed = changed
        return resource_group

    @log_entry_exit
    def remove_resource(self, resource_id, spec):
        device_id = UAIGResourceID().storage_resourceId(self.serial)
        changed = False
        response = None
        if spec.ldevs and len(spec.ldevs) > 0:
            end_point = REMOVE_LDEVS_FROM_RESOURCE_GROUP_UAI_V2.format(
                device_id, resource_id
            )
            payload = {"ldevIds": spec.ldevs}
            response = self.connection_manager.delete(end_point, payload)
            changed = True
        if spec.parity_groups and len(spec.parity_groups) > 0:
            end_point = REMOVE_PARITY_GROUPS_FROM_RESOURCE_GROUP_UAI_V2.format(
                device_id, resource_id
            )
            payload = {"parityGroupIds": spec.parity_groups}
            response = self.connection_manager.delete(end_point, payload)
            changed = True
        if spec.ports and len(spec.ports) > 0:
            end_point = REMOVE_PORTS_FROM_RESOURCE_GROUP_UAI_V2.format(
                device_id, resource_id
            )
            payload = {"ports": spec.ports}
            response = self.connection_manager.delete(end_point, payload)
            changed = True
        if spec.host_groups and len(spec.host_groups) > 0:
            end_point = REMOVE_HOST_GROUPS_FROM_RESOURCE_GROUP_UAI_V2.format(
                device_id, resource_id
            )
            host_groups = self.get_host_groups_for_gw_api(spec.host_groups)
            logger.writeDebug("PV:remove_resource:host_groups_api={}", host_groups)
            payload = {"hostGroups": host_groups}
            response = self.connection_manager.delete(end_point, payload)
            changed = True
        if spec.iscsi_targets and len(spec.iscsi_targets) > 0:
            end_point = REMOVE_ISCSI_TARGETS_FROM_RESOURCE_GROUP_UAI_V2.format(
                device_id, resource_id
            )
            iscsi_targets = self.get_iscsi_targets_for_gw_api(spec.iscsi_targets)
            payload = {"iscsiTargets": iscsi_targets}
            response = self.connection_manager.delete(end_point, payload)
            changed = True
        if spec.storage_pool_ids and len(spec.storage_pool_ids) > 0:
            end_point = REMOVE_POOLS_FROM_RESOURCE_GROUP_UAI_V2.format(
                device_id, resource_id
            )
            payload = {"poolIds": spec.storage_pool_ids}
            response = self.connection_manager.delete(end_point, payload)
            changed = True
        self.connection_info.changed = changed
        return response

    @log_entry_exit
    def get_host_groups_for_gw_api(self, host_groups):

        host_groups_api = []
        for host_group in host_groups:
            tmp_dict = {
                "hostGroupName": host_group["name"],
                "port": host_group["port"],
            }
            host_groups_api.append(tmp_dict)
        return host_groups_api

    @log_entry_exit
    def get_iscsi_targets_for_gw_api(self, iscsci_targets):

        iscsci_targets_api = []
        for iscsci_target in iscsci_targets:
            tmp_dict = {
                "iscsiName": iscsci_target["name"],
                "port": iscsci_target["port"],
            }
            iscsci_targets_api.append(tmp_dict)
        return iscsci_targets_api

    @log_entry_exit
    def get_ucp_serial(self):
        partner_id = CommonConstants.PARTNER_ID
        ucp_manager = UcpManager(
            self.connection_info.address,
            self.connection_info.username,
            self.connection_info.password,
            self.connection_info.api_token,
            partner_id,
            self.connection_info.subscriber_id,
            self.serial,
        )
        storage_system_info = ucp_manager.getStorageSystem()
        logger.writeDebug("get_ucp_serial:storage_system_info={}", storage_system_info)
        ucp_serial = storage_system_info.get("ucpSystems")
        logger.writeDebug("get_ucp_serial:ucp_serial={}", ucp_serial)
        return ucp_serial[0]

    @log_entry_exit
    def delete_resource_group(self, rg_id, spec):
        # looks like delete contract is not correct, need to revisit this
        device_id = UAIGResourceID().storage_resourceId(self.serial)
        end_point = DELETE_RESOURCE_GROUP_UAI_V2.format(device_id, rg_id)

        payload = {}
        payload["resourceGroupName"] = spec.name
        payload["serialNumber"] = self.serial
        payload["ucpSystem"] = self.get_ucp_serial()

        ret_data = self.connection_manager.delete(end_point, payload)
        self.connection_info.changed = True
        return ret_data

    @log_entry_exit
    def create_resource_group(self, spec):
        device_id = UAIGResourceID().storage_resourceId(self.serial)
        end_point = CREATE_RESOURCE_GROUP_UAI_V2.format(device_id)

        payload = {}
        payload["resourceGroupName"] = spec.name
        payload["serialNumber"] = self.serial
        payload["ucpSystem"] = self.get_ucp_serial()

        if spec.virtual_storage_serial:
            payload["remoteStorageId"] = spec.virtual_storage_serial
        if spec.virtual_storage_model:
            gw_v_model = VSPStorageModelsManager.get_gw_storage_model(
                spec.virtual_storage_model
            )
            if gw_v_model is None:
                err_msg = VSPResourceGroupValidateMsg.INVALID_VIRTUAL_STORAGE_MODEL.value.format(
                    spec.virtual_storage_model
                )
                raise ValueError(err_msg)
            payload["model"] = gw_v_model
            gw_v_type = VSPStorageModelsManager.get_gw_storage_device_type(
                spec.virtual_storage_model
            )
            if gw_v_type and len(gw_v_type) > 0:
                payload["type"] = gw_v_type

        resource_group = self.connection_manager.post(end_point, payload)
        self.connection_info.changed = True
        return resource_group

    @log_entry_exit
    def delete_resource_group_force(self, rg):

        device_id = UAIGResourceID().storage_resourceId(self.serial)
        resource_id = rg.resourceId

        response = None
        if rg.volumes and len(rg.volumes) > 0:
            end_point = REMOVE_LDEVS_FROM_RESOURCE_GROUP_UAI_V2.format(
                device_id, resource_id
            )
            payload = {"ldevIds": rg.volumes}
            self.connection_manager.delete(end_point, payload)

        if rg.parityGroups and len(rg.parityGroups) > 0:
            end_point = REMOVE_PARITY_GROUPS_FROM_RESOURCE_GROUP_UAI_V2.format(
                device_id, resource_id
            )
            payload = {"parityGroupIds": rg.parityGroups}
            self.connection_manager.delete(end_point, payload)

        if rg.ports and len(rg.ports) > 0:
            end_point = REMOVE_PORTS_FROM_RESOURCE_GROUP_UAI_V2.format(
                device_id, resource_id
            )
            payload = {"ports": rg.ports}
            response = self.connection_manager.delete(end_point, payload)

        if rg.hostGroups and len(rg.hostGroups) > 0:
            end_point = REMOVE_HOST_GROUPS_FROM_RESOURCE_GROUP_UAI_V2.format(
                device_id, resource_id
            )
            payload = {"hostGroups": rg.hostGroups}
            response = self.connection_manager.delete(end_point, payload)

        if rg.iscsiTargets and len(rg.iscsiTargets) > 0:
            end_point = REMOVE_ISCSI_TARGETS_FROM_RESOURCE_GROUP_UAI_V2.format(
                device_id, resource_id
            )
            payload = {"iscsiTargets": rg.iscsiTargets}
            response = self.connection_manager.delete(end_point, payload)

        if rg.pools and len(rg.pools) > 0:
            end_point = REMOVE_POOLS_FROM_RESOURCE_GROUP_UAI_V2.format(
                device_id, resource_id
            )
            payload = {"poolIds": rg.pools}
            response = self.connection_manager.delete(end_point, payload)

        end_point = DELETE_RESOURCE_GROUP_UAI_V2.format(device_id, rg.resourceId)
        payload = {}
        payload["resourceGroupName"] = rg.resourceGroupName
        payload["serialNumber"] = self.serial
        payload["ucpSystem"] = self.get_ucp_serial()

        retry_count = 0
        retry_time = 5
        while retry_count < retry_time:
            try:
                response = self.connection_manager.delete(end_point, payload)
                break
            except Exception as err:
                if "The resource group is currently in use" in str(err):
                    logger.writeError(err)
                    retry_count += 1
                    time.sleep(10)
                else:
                    logger.writeError(err)
                    raise err

        self.connection_info.changed = True
        return response
