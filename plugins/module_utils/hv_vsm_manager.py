import json

try:
    from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_storage_enum import (
        StorageType,
        StorageModel,
        RG_StorageModel,
        RG_StorageType,
    )

    HAS_ENUM = True
except ImportError:
    HAS_ENUM = False
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_exceptions import (
    HiException,
)


from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_http_client import (
    HTTPClient as requests,
)


class VirtualStorageSystem:
    def __init__(self, serial, webServiceIp, webServicePort, sessionId):
        self.serial = serial
        self.sessionId = sessionId
        self.webServiceIp = webServiceIp
        self.webServicePort = webServicePort
        self.basedUrl = "https://{0}:{1}".format(webServiceIp, webServicePort)
        self.shouldVerifySslCertification = False
        self.logger = Log()

    def getUrl(self, urlPath):
        return "{0}/HitachiStorageManagementWebServices/{1}".format(
            self.basedUrl, urlPath
        )

    # get All VSM
    def getVSM(self):

        funcName = "hv_vsm_manager.getVSM"
        self.logger.writeEnterSDK(funcName)

        urlPath = "StorageManager/StorageManager/GetVirtualStorageSystems"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "luns": True,
            "parityGroups": True,
            "hostGroups": True,
            "fcPorts": True,
        }

        response = requests.get(
            url, params=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def getVSMBySerial(self, serialId):

        funcName = "hv_vsm_manager.getVSMBySerial"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("serialId={}", serialId)

        urlPath = "StorageManager/StorageManager/GetVirtualStorageSystem"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serial": serialId,
            "luns": True,
            "parityGroups": True,
            "hostGroups": True,
            "fcPorts": True,
        }

        response = requests.get(
            url, params=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def getResourceGroupDriveGroups(self, rgId):

        funcName = "hv_vsm_manager.getResourceGroupDriveGroups"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}", rgId)

        urlPath = "ResourceGroup/GetResourceGroupDriveGroups"
        url = self.getUrl(urlPath)
        body = {"sessionId": self.sessionId, "serialNumber": self.serial, "rgId": rgId}

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def getResourceGroupHostGroups(self, rgId):

        funcName = "hv_vsm_manager.getResourceGroupHostGroups"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}", rgId)

        urlPath = "ResourceGroup/GetResourceGroupHostGroups"
        url = self.getUrl(urlPath)
        body = {"sessionId": self.sessionId, "serialNumber": self.serial, "rgId": rgId}

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def getResourceGroupLogicalUnits(self, rgId):

        funcName = "hv_vsm_manager.getResourceGroupLogicalUnits"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}", rgId)

        urlPath = "ResourceGroup/GetResourceGroupLogicalUnits"
        url = self.getUrl(urlPath)
        body = {"sessionId": self.sessionId, "serialNumber": self.serial, "rgId": rgId}

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def getResourceGroupPorts(self, rgId):

        funcName = "hv_vsm_manager.getResourceGroupPorts"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}", rgId)

        urlPath = "ResourceGroup/GetResourceGroupPorts"
        url = self.getUrl(urlPath)
        body = {"sessionId": self.sessionId, "serialNumber": self.serial, "rgId": rgId}

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def rediscoverVirtualStorages(self):

        funcName = "hv_vsm_manager.rediscoverVirtualStorages"
        self.logger.writeEnterSDK(funcName)

        url = self.getUrl("StorageManager/StorageManager/DiscoverVirtualStorageSystems")

        body = {
            "sessionId": self.sessionId,
            "luns": True,
            "parityGroups": True,
            "hostGroups": True,
            "fcPorts": True,
        }

        response = requests.get(
            url, params=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def getTypeFromModel(self, model):
        if "VSP" == model:
            return model
        if "VSP_G1000" == model:
            return model
        if "VSP_G1500" == model:
            return model
        if "VSP_F1500" == model:
            return model
        if "VSP_G" in model:
            return "VSP_GX00"
        if "VSP_F" in model:
            return "VSP_FX00"
        if "VSP_N" in model:
            return "VSP_NX00"
        if "00H" in model:
            return "VSP_5X00H"
        if "VSP_5" in model:
            return "VSP_5X00"
        if "VSP_E" in model:
            return "VSP_EX00"
        return "UNKNOWN"

    def createVirtualStorageSystem(self, model, meta_resources):

        funcName = "hv_vsm_manager.createVirtualStorageSystem"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("model={}", model)
        self.logger.writeParam("meta_resources={}", meta_resources)

        url = self.getUrl("StorageManager/StorageManager/CreateVirtualStorageSystem")
        storage_type = RG_StorageType.fromString(self.getTypeFromModel(model))
        storage_model = RG_StorageModel.fromString(model)
        self.logger.writeParam("storage_type={}", storage_type.value)
        self.logger.writeParam("storage_model={}", storage_model.value)
        body = {
            "virtualSerialNumber": self.serial,
            "sessionId": self.sessionId,
            "type": storage_type.value,
            "model": storage_model.value,
            "metaResources": meta_resources,
        }

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def deleteResourceGroup(self, rgId):

        funcName = "hv_vsm_manager.deleteResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}", rgId)

        # if True: return
        urlPath = "ResourceGroup/DeleteResourceGroup"
        url = self.getUrl(urlPath)
        body = {"sessionId": self.sessionId, "serialNumber": self.serial, "rgId": rgId}

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def createVirtualBoxResourceGroup(self, remoteStorageId, model, rgName):

        funcName = "hv_vsm_manager.createVirtualBoxResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("remoteStorageId={}", remoteStorageId)
        self.logger.writeParam("model={}", model)
        self.logger.writeParam("rgName={}", rgName)

        urlPath = "ResourceGroup/CreateVirtualBoxResourceGroup"
        url = self.getUrl(urlPath)
        storage_type = StorageType.fromString(self.getTypeFromModel(model))
        storage_model = StorageModel.fromString(model)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "remoteStorageId": remoteStorageId,
            "type": storage_type.value,
            "model": storage_model.value,
            "rgName": rgName,
        }

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def deleteVirtualStorageSystem(self, physicalSerialNumber=None):

        funcName = "hv_vsm_manager.deleteVirtualStorageSystem"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("physicalSerialNumber={}", physicalSerialNumber)

        url = self.getUrl("StorageManager/StorageManager/DeleteVirtualStorageSystem")

        body = {"virtualSerialNumber": self.serial, "sessionId": self.sessionId}

        if physicalSerialNumber is not None:
            body["physicalSerialNumber"] = physicalSerialNumber

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))
