import hashlib

try:
    from ..common.vsp_constants import Endpoints
    from ..common.hv_constants import CommonConstants, StateValue
    from ..common.ansible_common import dicts_to_dataclass_list
    from .gateway_manager import UAIGConnectionManager, VSPConnectionManager
    from ..model.vsp_shadow_image_pair_models import (
        VSPShadowImagePairsInfo,
        VSPShadowImagePairInfo,
        UaigResourceMappingInfo,
    )
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..hv_ucpmanager import UcpManager
    from ..message.vsp_shadow_image_pair_msgs import VSPShadowImagePairValidateMsg

except ImportError:
    from common.vsp_constants import Endpoints
    from common.hv_constants import CommonConstants, StateValue
    from common.ansible_common import dicts_to_dataclass_list
    from model.vsp_shadow_image_pair_models import (
        VSPShadowImagePairsInfo,
        VSPShadowImagePairInfo,
        UaigResourceMappingInfo,
    )
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from .gateway_manager import UAIGConnectionManager, VSPConnectionManager
    from hv_ucpmanager import UcpManager
    from message.vsp_shadow_image_pair_msgs import VSPShadowImagePairValidateMsg


class VSPShadowImagePairDirectGateway:

    def __init__(self, connection_info):
        funcName = "VSPShadowImagePairDirectGateway: init"
        self.logger = Log()
        self.logger.writeEnterSDK(funcName)
        self.connectionManager = VSPConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )

    @log_entry_exit
    def get_all_shadow_image_pairs(self, serial):
        funcName = "VSPShadowImagePairDirectGateway: get_all_shadow_image_pairs"
        self.logger.writeEnterSDK(funcName)
        response = self.get_all_shadow_image_pairs_by_copy_group(serial)
        self.logger.writeDebug("{} Response={}", funcName, response)
        shadow_image_list = []
        for shadow_image_item in response["data"]:
            shadow_image = self.parse_shadow_image_data(serial, shadow_image_item)
            if shadow_image is not None:
                shadow_image_list.append(shadow_image)
        self.logger.writeExitSDK(funcName)
        return VSPShadowImagePairsInfo(
            dicts_to_dataclass_list(shadow_image_list, VSPShadowImagePairInfo)
        )

    @log_entry_exit
    def get_shadow_image_pair_by_pvol(self, serial, pvol):
        funcName = "VSPShadowImagePairDirectGateway: get_shadow_image_pair_by_pvol"
        self.logger.writeEnterSDK(funcName)
        response = self.get_all_shadow_image_pairs_by_copy_group(serial)
        self.logger.writeDebug("{} Response={}", funcName, response)
        shadow_image_list = []
        for shadow_image_item in response["data"]:
            if shadow_image_item["pvolLdevId"] == pvol:
                shadow_image = self.parse_shadow_image_data(serial, shadow_image_item)
                if shadow_image is not None:
                    shadow_image_list.append(shadow_image)
        self.logger.writeExitSDK(funcName)
        return VSPShadowImagePairsInfo(
            dicts_to_dataclass_list(shadow_image_list, VSPShadowImagePairInfo)
        )

    @log_entry_exit
    def create_shadow_image_pair(self, serial, createShadowImagePairSpec):
        funcName = "VSPShadowImagePairDirectGateway: create_shadow_image_pair"
        self.logger.writeDebug(f"{funcName}: spec = {createShadowImagePairSpec}")
        end_point = Endpoints.DIRECT_CREATE_SHADOW_IMAGE_PAIR
        self.populateHeader()
        payload = self.generate_create_payload(serial, createShadowImagePairSpec)
        response = self.connectionManager.post(end_point, payload)
        self.logger.writeDebug("{} Response={}", funcName, response)
        self.logger.writeExitSDK(funcName)
        return response

    @log_entry_exit
    def get_shadow_image_pair_by_id(self, serial, pairId):
        funcName = "VSPShadowImagePairDirectGateway: get_shadow_image_pair_by_id"
        self.logger.writeEnterSDK(funcName)
        end_point = Endpoints.DIRECT_GET_SHADOW_IMAGE_PAIR_BY_ID.format(pairId=pairId)
        response = self.connectionManager.read(end_point)
        self.logger.writeDebug("{} Response={}", funcName, response)
        shadow_image_pair = self.parse_shadow_image_data(
            serial=serial, response=response
        )
        self.logger.writeDebug("{} Response={}", funcName, shadow_image_pair)
        self.logger.writeExitSDK(funcName)
        if shadow_image_pair is None:
            raise ValueError(
                VSPShadowImagePairValidateMsg.PAIR_NOT_FOUND.value.format(pairId)
            )
        return VSPShadowImagePairInfo(**shadow_image_pair)

    def split_shadow_image_pair(self, serial, updateShadowImagePairSpec):

        funcName = "VSPShadowImagePairDirectGateway: split_shadow_image_pair"
        self.logger.writeEnterSDK(funcName)
        end_point = Endpoints.DIRECT_SPLIT_SHADOW_IMAGE_PAIR.format(
            pairId=updateShadowImagePairSpec.pair_id
        )
        # headers = self.populateHeader()
        payload = self.generate_update_payload(updateShadowImagePairSpec)
        self.logger.writeDebug(f"GW:split_shadow_image_pair:payload={payload}")
        response = self.connectionManager.post(end_point, payload)
        self.logger.writeDebug("{} Response={}", funcName, response)
        self.logger.writeExitSDK(funcName)
        return response

    def resync_shadow_image_pair(self, serial, updateShadowImagePairSpec):

        funcName = "VSPShadowImagePairDirectGateway: resync_shadow_image_pair"
        self.logger.writeEnterSDK(funcName)
        end_point = Endpoints.DIRECT_RESYNC_SHADOW_IMAGE_PAIR.format(
            pairId=updateShadowImagePairSpec.pair_id
        )
        # headers = self.populateHeader()
        payload = self.generate_update_payload(updateShadowImagePairSpec)
        self.logger.writeDebug(payload)
        response = self.connectionManager.post(end_point, payload)
        self.logger.writeDebug("{} Response={}", funcName, response)
        self.logger.writeExitSDK(funcName)
        return response

    def restore_shadow_image_pair(self, serial, updateShadowImagePairSpec):

        funcName = "VSPShadowImagePairDirectGateway: restore_shadow_image_pair"
        self.logger.writeEnterSDK(funcName)
        end_point = Endpoints.DIRECT_RESTORE_SHADOW_IMAGE_PAIR.format(
            pairId=updateShadowImagePairSpec.pair_id
        )
        # headers = self.populateHeader()
        payload = self.generate_update_payload(updateShadowImagePairSpec)
        self.logger.writeDebug(payload)
        response = self.connectionManager.post(end_point, payload)
        self.logger.writeDebug("{} Response={}", funcName, response)
        self.logger.writeExitSDK(funcName)
        return response

    def delete_shadow_image_pair(self, serial, deleteShadowImagePairSpec):

        funcName = "VSPShadowImagePairDirectGateway: delete_shadow_image_pair"
        self.logger.writeEnterSDK(funcName)
        end_point = Endpoints.DIRECT_DELETE_SHADOW_IMAGE_PAIR.format(
            pairId=deleteShadowImagePairSpec.pair_id
        )
        response = self.connectionManager.delete(end_point)
        self.logger.writeDebug("{} Response={}", funcName, response)
        self.logger.writeExitSDK(funcName)
        return response

    def generate_create_payload(self, serial, createShadowImagePairSpec):
        pvol_mu_number = self.get_pvol_mu_number(serial, createShadowImagePairSpec.pvol)
        copy_group_name = self.generate_copy_group_name(
            createShadowImagePairSpec.pvol, createShadowImagePairSpec.svol
        )
        copy_pair_name = self.generate_copy_pair_name(
            createShadowImagePairSpec.pvol, createShadowImagePairSpec.svol
        )
        copy_pace = self.get_copy_pace_value(
            createShadowImagePairSpec.copy_pace_track_size
        )
        payload = {
            "copyGroupName": copy_group_name,
            "copyPairName": copy_pair_name,
            "replicationType": "SI",
            "pvolLdevId": createShadowImagePairSpec.pvol,
            "pvolMuNumber": pvol_mu_number,
            "svolLdevId": createShadowImagePairSpec.svol,
            "pvolDeviceGroupName": copy_group_name + "P_",
            "svolDeviceGroupName": copy_group_name + "S_",
            "isNewGroupCreation": True,
            "copyPace": copy_pace,
        }
        if createShadowImagePairSpec.auto_split is not None:
            payload["autoSplit"] = bool(createShadowImagePairSpec.auto_split)
        else:
            payload["autoSplit"] = False

        if (
            payload["autoSplit"] is True
            and createShadowImagePairSpec.new_consistency_group is not None
            and createShadowImagePairSpec.new_consistency_group is True
        ):
            raise ValueError(VSPShadowImagePairValidateMsg.AUTO_SPLIT_VALIDATION.value)
        if createShadowImagePairSpec.new_consistency_group is not None:
            payload["isConsistencyGroup"] = bool(
                createShadowImagePairSpec.new_consistency_group
            )
        if createShadowImagePairSpec.consistency_group_id is not None:
            payload["consistencyGroupId"] = int(
                createShadowImagePairSpec.consistency_group_id
            )
            if createShadowImagePairSpec.new_consistency_group is None:
                payload["isConsistencyGroup"] = True

        if (
            payload["autoSplit"] is False
            and createShadowImagePairSpec.enable_quick_mode is not None
            and createShadowImagePairSpec.enable_quick_mode is True
        ):
            raise ValueError(
                VSPShadowImagePairValidateMsg.ENABLE_QUICK_MODE_VALIDATION.value
            )
        if createShadowImagePairSpec.enable_quick_mode is not None:
            payload["quickMode"] = bool(createShadowImagePairSpec.enable_quick_mode)
        if createShadowImagePairSpec.is_data_reduction_force_copy is not None:
            payload["isDataReductionForceCopy"] = bool(
                createShadowImagePairSpec.is_data_reduction_force_copy
            )

        self.logger.writeDebug(payload)
        return payload

    def generate_update_payload(self, updateShadowImagePairSpec):

        copy_pace = self.get_copy_pace_value(
            updateShadowImagePairSpec.copy_pace_track_size
        )
        payload = {}
        parameters = {
            "copyPace": copy_pace,
        }
        if updateShadowImagePairSpec.enable_quick_mode is not None:
            parameters["quickMode"] = bool(updateShadowImagePairSpec.enable_quick_mode)
        else:
            parameters["quickMode"] = False

        payload["parameters"] = parameters

        self.logger.writeDebug(payload)
        return payload

    def populateHeader(self):
        headers = {}
        headers["Job-Mode-Wait-Configuration-Change"] = "NoWait"
        return headers

    def generate_copy_group_name(self, pvol, svol):
        copyGroupName = "CG_" + str(pvol) + "_" + str(svol)
        return copyGroupName

    def generate_copy_pair_name(self, pvol, svol):
        copyPairName = "CP_" + str(pvol) + "_" + str(svol)
        return copyPairName

    def generate_local_clone_copy_pair_id(self, pvol, svol):
        copyGroupName = "CG_" + str(pvol) + "_" + str(svol)
        copyPairName = "CP_" + str(pvol) + "_" + str(svol)
        pvolDeviceGroupName = copyGroupName + "P_"
        svolDeviceGroupName = copyGroupName + "S_"
        local_clone_copy_pair_id = (
            copyGroupName
            + ","
            + pvolDeviceGroupName
            + ","
            + svolDeviceGroupName
            + ","
            + copyPairName
        )
        return local_clone_copy_pair_id

    def get_copy_pace_value(self, copy_pace):
        copy_pace_value = 1
        if copy_pace == "SLOW":
            copy_pace_value = 1
        elif copy_pace == "FAST":
            copy_pace_value = 10
        else:
            copy_pace_value = 3
        return copy_pace_value

    def get_pvol_mu_number(self, serial, pvol):
        pvol_mu_number = None
        shadow_image_pairs = self.get_shadow_image_pair_by_pvol(serial, pvol=pvol)
        if len(shadow_image_pairs.data_to_list()) == 0:
            pvol_mu_number = 0
            return pvol_mu_number
        if len(shadow_image_pairs.data_to_list()) == 3:
            raise SystemError(VSPShadowImagePairValidateMsg.MAX_3_PAIR_EXISTS.value)
        mu_numbers = [0, 1, 2]
        for sip in shadow_image_pairs.data_to_list():
            if sip.get("_VSPShadowImagePairInfo__pvolMuNumber") in mu_numbers:
                mu_numbers.remove(sip.get("_VSPShadowImagePairInfo__pvolMuNumber"))
        pvol_mu_number = mu_numbers[0]
        return pvol_mu_number

    def get_local_replication_id(self, response):
        response = str(response)
        resp_list = response.split(",")
        copy_group_name = resp_list[0]
        copy_group_name = copy_group_name.replace("CG_", "")
        local_replication_id = copy_group_name.replace("_", ",")
        return local_replication_id

    def parse_shadow_image_data(self, serial, response):
        shadow_image_obj = {}

        # This block of code is added to handle situation like described in JIRA
        # https://hv-eng.atlassian.net/browse/UCA-2865?focusedCommentId=2159648
        if response.get("pvolLdevId") is None:
            self.logger.writeInfo(
                "GW:parse_shadow_image_data:Found shadow image pair without pvolLdevId in response={}",
                response,
            )
            return None
        if response.get("svolLdevId") is None:
            self.logger.writeInfo(
                "GW:parse_shadow_image_data:Found shadow image pair without svolLdevId in response={}",
                response,
            )
            return None

        pvol = int(response["pvolLdevId"])
        svol = int(response["svolLdevId"])
        shadow_image_obj["resourceId"] = response["localCloneCopypairId"]

        shadow_image_obj["type"] = (
            "SHADOW_IMAGE" if response["replicationType"] == "SI" else ""
        )
        shadow_image_obj["primaryVolumeId"] = pvol
        shadow_image_obj["secondaryVolumeId"] = svol
        shadow_image_obj["storageSerialNumber"] = serial
        shadow_image_obj["consistencyGroupId"] = (
            response["consistencyGroupId"]
            if response.get("consistencyGroupId") is not None
            else None
        )
        shadow_image_obj["status"] = response["pvolStatus"]
        shadow_image_obj["_VSPShadowImagePairInfo__pvolMuNumber"] = response[
            "pvolMuNumber"
        ]
        shadow_image_obj["mirrorUnitId"] = response["pvolMuNumber"]
        shadow_image_obj["copyRate"] = (
            response["copyProgressRate"]
            if "copyProgressRate" in response
            and response["copyProgressRate"] is not None
            else None
        )
        shadow_image_obj["copyGroupName"] = response.get("copyGroupName", None)
        shadow_image_obj["copyPairName"] = response.get("copyPairName", None)
        return shadow_image_obj

    def get_md5_hash(self, data):
        # nosec: No security issue here as it is does not exploit any security vulnerability only used for generating unique resource id for UAIG
        md5_hash = hashlib.md5()
        md5_hash.update(data.encode("utf-8"))
        return md5_hash.hexdigest()

    @log_entry_exit
    def get_all_shadow_image_pairs_by_copy_group(self, serial):
        funcName = (
            "VSPShadowImagePairDirectGateway: get_all_shadow_image_pairs_by_copy_pair"
        )
        self.logger.writeEnterSDK(funcName)
        end_point = Endpoints.DIRECT_GET_ALL_COPY_PAIR_GROUP
        local_cp_pairs = Endpoints.DIRECT_GET_SI_BY_CPG
        response = self.connectionManager.read(end_point)
        self.logger.writeDebug("{} Copy Group Response={}", funcName, response)
        shadow_image_list = []
        for copy_group_item in response["data"]:
            copy_group_id = copy_group_item["localCloneCopygroupId"]
            uri = local_cp_pairs.format(copy_group_id)
            try:
                resp = self.connectionManager.read(uri)
                for shadow_image_item in resp.get("data"):
                    shadow_image_list.append(shadow_image_item)
            except Exception as e:
                self.logger.writeError(f"An error occurred: {str(e)}")

        self.logger.writeExitSDK(funcName)
        data = {"data": shadow_image_list}
        return data


class VSPShadowImagePairUAIGateway:

    def __init__(self, connection_info):
        funcName = "VSPShadowImagePairUAIGateway: init"
        self.logger = Log()
        self.logger.writeEnterSDK(funcName)
        self.connectionInfo = connection_info
        self.connectionManager = UAIGConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )

    @log_entry_exit
    def get_all_shadow_image_pairs(self, serial):
        funcName = "VSPShadowImagePairUAIGateway: get_all_shadow_image_pairs"
        self.logger.writeEnterSDK(funcName)
        deviceId = self.getStorageResourceId(serial)
        headers = self.populateHeader()
        end_point = Endpoints.UAIG_GET_ALL_SHADOW_IMAGE_PAIR.format(deviceId=deviceId)
        response = self.connectionManager.get(end_point, headers)
        self.logger.writeDebug("{} Response={}", funcName, response)
        self.logger.writeExitSDK(funcName)
        return VSPShadowImagePairsInfo(
            dicts_to_dataclass_list(response["data"], VSPShadowImagePairInfo)
        )

    @log_entry_exit
    def get_shadow_image_pair_by_id(self, serial, pairId):
        funcName = "VSPShadowImagePairUAIGateway: get_shadow_image_pair_by_id"
        self.logger.writeEnterSDK(funcName)
        deviceId = self.getStorageResourceId(serial)
        headers = self.populateHeader()
        end_point = Endpoints.UAIG_GET_SHADOW_IMAGE_PAIR_BY_ID.format(
            deviceId=deviceId, pairId=pairId
        )
        response = self.connectionManager.get(end_point)
        self.logger.writeDebug("{} Response={}", funcName, response)
        self.logger.writeExitSDK(funcName)
        shadow_image_pair = VSPShadowImagePairInfo(**response["data"])
        shadow_image_pair.partnerId = headers.get("partnerId")
        if headers.get("subscriberId") is not None:
            shadow_image_pair.subscriberId = headers.get("subscriberId")
            shadow_image_pair.entitlementStatus = "assigned"
        else:
            shadow_image_pair.subscriberId = None
            shadow_image_pair.entitlementStatus = "unassigned"

        return shadow_image_pair

    @log_entry_exit
    def get_shadow_image_pair_by_pvol(self, serial, pvol):
        funcName = "VSPShadowImagePairUAIGateway: get_shadow_image_pair_by_pvol"
        self.logger.writeEnterSDK(funcName)
        deviceId = self.getStorageResourceId(serial)
        headers = self.populateHeader()
        end_point = Endpoints.UAIG_GET_SHADOW_IMAGE_PAIR_BY_PVOL.format(
            deviceId=deviceId, pvol=pvol
        )
        response = self.connectionManager.get(end_point)
        self.logger.writeDebug("{} Response={}", funcName, response)
        self.logger.writeExitSDK(funcName)
        for sip in response["data"]:
            sip["partnerId"] = headers.get("partnerId")
            if headers.get("subscriberId") is not None:
                sip["subscriberId"] = headers.get("subscriberId")
                sip["entitlementStatus"] = "assigned"
            else:
                sip["subscriberId"] = None
                sip["entitlementStatus"] = "unassigned"

        return VSPShadowImagePairsInfo(
            dicts_to_dataclass_list(response["data"], VSPShadowImagePairInfo)
        )

    @log_entry_exit
    def create_shadow_image_pair(self, serial, createShadowImagePairSpec):
        funcName = "VSPShadowImagePairUAIGateway: create_shadow_image_pair"
        self.logger.writeEnterSDK(funcName)
        deviceId = self.getStorageResourceId(serial)
        end_point = Endpoints.UAIG_CREATE_SHADOW_IMAGE_PAIR.format(deviceId=deviceId)
        headers = self.populateHeader()
        payload = {
            "ucpSystem": CommonConstants.UCP_SERIAL,
            "primaryLunId": int(createShadowImagePairSpec.pvol),
            "secondaryLunId": int(createShadowImagePairSpec.svol),
        }
        if createShadowImagePairSpec.auto_split is not None:
            payload["autoSplit"] = bool(createShadowImagePairSpec.auto_split)
        else:
            payload["autoSplit"] = False
        if createShadowImagePairSpec.new_consistency_group is not None:
            payload["newConsistencyGroup"] = bool(
                createShadowImagePairSpec.new_consistency_group
            )
        if createShadowImagePairSpec.consistency_group_id is not None:
            payload["consistencyGroupID"] = int(
                createShadowImagePairSpec.consistency_group_id
            )
        if createShadowImagePairSpec.copy_pace_track_size is not None:
            payload["copyPaceTrackSize"] = self.get_copy_pace_value(
                createShadowImagePairSpec.copy_pace_track_size
            )

        self.logger.writeDebug(payload)
        response = self.connectionManager.post(
            end_point, payload, headers_input=headers
        )
        self.logger.writeDebug("{} Response={}", funcName, response)
        self.logger.writeExitSDK(funcName)
        return response

    def split_shadow_image_pair(self, serial, updateShadowImagePairSpec):

        funcName = "VSPShadowImagePairUAIGateway: split_shadow_image_pair"
        self.logger.writeEnterSDK(funcName)
        deviceId = self.getStorageResourceId(serial)
        end_point = Endpoints.UAIG_SPLIT_SHADOW_IMAGE_PAIR.format(
            deviceId=deviceId, pairId=updateShadowImagePairSpec.pair_id
        )
        headers = self.populateHeader()
        self.validate_resource_access(
            deviceId,
            updateShadowImagePairSpec.pvol,
            updateShadowImagePairSpec.pair_id,
            headers,
        )
        payload = self.create_payload(updateShadowImagePairSpec, StateValue.SPLIT)
        self.logger.writeDebug(payload)
        response = self.connectionManager.patch(end_point, payload)
        self.logger.writeDebug("{} Response={}", funcName, response)
        self.logger.writeExitSDK(funcName)
        return response

    def resync_shadow_image_pair(self, serial, updateShadowImagePairSpec):

        funcName = "VSPShadowImagePairUAIGateway: resync_shadow_image_pair"
        self.logger.writeEnterSDK(funcName)
        deviceId = self.getStorageResourceId(serial)
        end_point = Endpoints.UAIG_RESYNC_SHADOW_IMAGE_PAIR.format(
            deviceId=deviceId, pairId=updateShadowImagePairSpec.pair_id
        )
        headers = self.populateHeader()
        self.validate_resource_access(
            deviceId,
            updateShadowImagePairSpec.pvol,
            updateShadowImagePairSpec.pair_id,
            headers,
        )
        payload = self.create_payload(updateShadowImagePairSpec, StateValue.SYNC)
        self.logger.writeDebug(payload)
        response = self.connectionManager.patch(end_point, payload)
        self.logger.writeDebug("{} Response={}", funcName, response)
        self.logger.writeExitSDK(funcName)
        return response

    def restore_shadow_image_pair(self, serial, updateShadowImagePairSpec):

        funcName = "VSPShadowImagePairUAIGateway: restore_shadow_image_pair"
        self.logger.writeEnterSDK(funcName)
        deviceId = self.getStorageResourceId(serial)
        end_point = Endpoints.UAIG_RESTORE_SHADOW_IMAGE_PAIR.format(
            deviceId=deviceId, pairId=updateShadowImagePairSpec.pair_id
        )
        headers = self.populateHeader()
        self.validate_resource_access(
            deviceId,
            updateShadowImagePairSpec.pvol,
            updateShadowImagePairSpec.pair_id,
            headers,
        )
        payload = self.create_payload(updateShadowImagePairSpec, StateValue.RESTORE)
        self.logger.writeDebug(payload)
        response = self.connectionManager.patch(end_point, payload)
        self.logger.writeDebug("{} Response={}", funcName, response)
        self.logger.writeExitSDK(funcName)
        return response

    def delete_shadow_image_pair(self, serial, deleteShadowImagePairSpec):

        funcName = "VSPShadowImagePairUAIGateway: delete_shadow_image_pair"
        self.logger.writeEnterSDK(funcName)
        deviceId = self.getStorageResourceId(serial)
        end_point = Endpoints.UAIG_DELETE_SHADOW_IMAGE_PAIR.format(
            deviceId=deviceId, pairId=deleteShadowImagePairSpec.pair_id
        )
        headers = self.populateHeader()
        self.validate_resource_access(
            deviceId,
            deleteShadowImagePairSpec.pvol,
            deleteShadowImagePairSpec.pair_id,
            headers,
        )
        response = self.connectionManager.delete(end_point, headers_input=headers)
        self.logger.writeDebug("{} Response={}", funcName, response)
        self.logger.writeExitSDK(funcName)
        return response

    @log_entry_exit
    def get_resource_mapping_info(self, deviceId, pairId, type, headers):
        funcName = "VSPShadowImagePairUAIGateway: get_resource_mapping_info"
        self.logger.writeEnterSDK(funcName)
        try:
            end_point = Endpoints.UAIG_GET_RESOURCE_MAPPING_INFO.format(
                deviceId=deviceId, pairId=pairId, type=type
            )
            response = self.connectionManager.get(end_point)
            self.logger.writeDebug("{} Response={}", funcName, response)
            self.logger.writeExitSDK(funcName)
            # return VSPShadowImagePairInfo(**response["data"])
            resource_map_info = UaigResourceMappingInfo(**response["data"])
            return resource_map_info
        except Exception:
            return None

    @log_entry_exit
    def getStorageResourceId(self, serial):
        partnerId = CommonConstants.PARTNER_ID
        subscriberId = (
            self.connectionInfo.subscriber_id
            if self.connectionInfo.subscriber_id is not None
            else None
        )
        ucpManager = UcpManager(
            self.connectionInfo.address,
            self.connectionInfo.username,
            self.connectionInfo.password,
            self.connectionInfo.api_token,
            partnerId,
            subscriberId,
            serial,
        )
        (resourceId, ucp) = ucpManager.getStorageSystemResourceId()
        return resourceId

    @log_entry_exit
    def populateHeader(self):
        headers = {}
        headers["partnerId"] = CommonConstants.PARTNER_ID
        if self.connectionInfo.subscriber_id is not None:
            headers["subscriberId"] = self.connectionInfo.subscriber_id
        return headers

    def create_payload(self, updateShadowImagePairSpec, type):
        payload = {}
        if updateShadowImagePairSpec.enable_quick_mode is not None:
            payload["enableQuickMode"] = bool(
                updateShadowImagePairSpec.enable_quick_mode
            )
        else:
            payload["enableQuickMode"] = False

        if type == StateValue.SPLIT:

            if updateShadowImagePairSpec.enable_read_write is not None:
                payload["enableReadWrite"] = bool(
                    updateShadowImagePairSpec.enable_read_write
                )
            else:
                payload["enableReadWrite"] = False
            return payload

        elif type == StateValue.SYNC:

            if updateShadowImagePairSpec.copy_pace_track_size is not None:
                payload["copyPace"] = str(
                    updateShadowImagePairSpec.copy_pace_track_size
                )
            else:
                payload["copyPace"] = "MEDIUM"
            return payload

        elif type == StateValue.RESTORE:

            if updateShadowImagePairSpec.copy_pace_track_size is not None:
                payload["copyPace"] = str(
                    updateShadowImagePairSpec.copy_pace_track_size
                )
            else:
                payload["copyPace"] = "MEDIUM"
            return payload

    def validate_resource_access(self, deviceId, pvol, pairId, headers):
        response = self.get_resource_mapping_info(
            deviceId, pairId, "ShadowImage", headers
        )
        hd_sub_id = (
            str(headers.get("subscriberId")) if headers.get("subscriberId") else None
        )

        if response is None:
            if hd_sub_id is None:
                return True
            else:
                raise Exception(
                    "Subscriber id  is not mapped with Shadow image pair of primary volume: "
                    + str(pvol)
                )
        res_sub_id = response.subscriberId
        if hd_sub_id is not None:
            if res_sub_id and hd_sub_id == res_sub_id:
                return True
            else:
                raise Exception(
                    "Subscriber id is not mapped with Shadow image pair of pvol: "
                    + str(pvol)
                )
        elif hd_sub_id is None and res_sub_id is None:
            return True

    def get_copy_pace_value(self, copy_pace):
        copy_pace_value = 1
        if copy_pace == "SLOW":
            copy_pace_value = 1
        elif copy_pace == "FAST":
            copy_pace_value = 10
        else:
            copy_pace_value = 3
        return copy_pace_value
