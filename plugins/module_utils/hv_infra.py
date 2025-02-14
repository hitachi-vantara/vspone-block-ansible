import json
import os
import re
import time

# import urllib3
from enum import Enum

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_http_client import (
    HTTPClient as requests,
)


class SNAPSHOT_OPTION(Enum):

    SSOPTION_HIDE_AND_DISABLE_ACCESS = 0
    SSOPTION_HIDE_AND_ALLOW_ACCESS = 1
    SSOPTION_SHOW_AND_ALLOW_ACCESS = 3
    UNKNOWN = None

    @classmethod
    def fromValue(cls, value):
        enums = [e for e in cls if e.value == value]
        return enums[0] if enums else None

    @classmethod
    def fromString(cls, value):
        if value.upper() in cls.__members__:
            return cls[value.upper()]
        else:
            return cls.UNKNOWN

    @classmethod
    def parse(cls, value):
        try:
            model = cls(value)
        except ValueError:
            model = cls.UNKNOWN
        return model


from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_htimanager import (
    HTIManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_remotemanager import (
    RemoteManager,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_htimanager import (
    PoolType,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_htimanager import (
    ReplicationStatus,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_storage_enum import (
    PoolCreateType,
    StorageType,
    StorageModel,
    PoolStatus,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_ucpmanager import (
    UcpManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_vsm_manager import (
    VirtualStorageSystem,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_exceptions import (
    HiException,
)


class StorageSystemManager:

    logger = Log()

    @staticmethod
    def getHostWWNs(
        hitachiAPIGatewayService,
        vcip,
        user,
        pword,
        esxiIP,
    ):

        funcName = "hv_infra:getHostWWNs"
        StorageSystemManager.logger.writeEnterSDK(funcName)
        url = "http://localhost:2030/getHostWWN"
        body = {"vcip": vcip, "user": user, "hostIp": esxiIP}
        StorageSystemManager.logger.writeInfo(" url= {}", url)
        StorageSystemManager.logger.writeInfo(" body= {}", body)
        body["pwd"] = pword

        response = requests.post(url, json=body, verify=False)
        StorageSystemManager.logger.writeExitSDK(funcName)
        if response.ok:
            commandOutJson = response.json()
            StorageSystemManager.logger.writeInfo(" response= {}", commandOutJson)

            # return is a string
            # commandOutJson = json.loads(commandOut)

            return commandOutJson
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            StorageSystemManager.logger.writeHiException(hiex)
            raise hiex
        else:
            r = json.loads(response.text)
            StorageSystemManager.logger.writeInfo(r)
            Utils.raiseException(None, response)

    @staticmethod
    def reScanHostStorage(
        hitachiAPIGatewayService,
        vcip,
        user,
        pword,
        esxiIP,
    ):

        funcName = "hv_infra:reScanHostStorage"
        StorageSystemManager.logger.writeEnterSDK(funcName)
        url = "http://localhost:2030/scanHostStorage"
        body = {"vcip": vcip, "user": user, "hostIp": esxiIP}
        StorageSystemManager.logger.writeInfo(" url= {}", url)
        StorageSystemManager.logger.writeInfo(" body= {}", body)
        body["pwd"] = pword

        StorageSystemManager.logger.writeExitSDK(funcName)
        response = requests.post(url, json=body, verify=False)
        if response.ok:
            StorageSystemManager.logger.writeInfo(" response= {}", response)
            return response
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            StorageSystemManager.logger.writeHiException(hiex)
            raise hiex
        else:
            r = json.loads(response.text)
            StorageSystemManager.logger.writeInfo(r)
            Utils.raiseException(None, response)

    @staticmethod
    def reScanVMFS(
        hitachiAPIGatewayService,
        vcip,
        user,
        pword,
        esxiIP,
    ):

        funcName = "hv_infra:reScanHostStorage"
        StorageSystemManager.logger.writeEnterSDK(funcName)
        url = "http://localhost:2030/scanVMFS"
        body = {"vcip": vcip, "user": user, "hostIp": esxiIP}
        StorageSystemManager.logger.writeInfo(" url= {}", url)
        StorageSystemManager.logger.writeInfo(" body= {}", body)
        body["pwd"] = pword

        StorageSystemManager.logger.writeExitSDK(funcName)
        response = requests.post(url, json=body, verify=False)
        if response.ok:
            StorageSystemManager.logger.writeInfo(" response= {}", response)
            return response
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            StorageSystemManager.logger.writeHiException(hiex)
            raise hiex
        else:
            r = json.loads(response.text)
            StorageSystemManager.logger.writeInfo(r)
            Utils.raiseException(None, response)

    @staticmethod
    def isOOB(isPhysicalServer):
        if isPhysicalServer is None:
            useOutOfBandConnection = False
        else:
            if isPhysicalServer.upper() == "FALSE":
                useOutOfBandConnection = False
            else:
                useOutOfBandConnection = True

        return useOutOfBandConnection

    @staticmethod
    def removeStorageSystems(
        management_address,
        management_username,
        management_password,
        ucp_serial,
        hitachiAPIGatewayService,
        hitachiAPIGatewayServicePort,
        storagesystems,
    ):
        funcName = "hv_infra:StorageSystemManager:removeStorageSystems"
        StorageSystemManager.logger.writeEnterSDK(funcName)

        serials = set()
        results = {}

        if storagesystems is None:
            storagesystems = []

        # do we need this
        # results['comment'] = 'No change.'

        for systemInfo in storagesystems:
            if not systemInfo:
                continue

            gatewayServer = systemInfo.get(
                "hitachiPeerService", hitachiAPIGatewayService
            )
            gatewayServerPort = systemInfo.get(
                "hitachiPeerServicePort", hitachiAPIGatewayServicePort
            )

            if gatewayServer is None:
                raise Exception("Gateway Server is required.")

            if hitachiAPIGatewayService is None:
                hitachiAPIGatewayService = gatewayServer
                hitachiAPIGatewayServicePort = gatewayServerPort

            if "svpIP" not in systemInfo:
                raise Exception("svpIP (location) is required.")

            serviceIP = systemInfo.get("storageGateway", hitachiAPIGatewayService)
            serial = systemInfo["serialNumber"]
            gateway = StorageSystem(
                serial,
                management_address,
                management_username,
                management_password,
                serviceIP,
            )

            #  if ucp is in the ss fact then do remove
            results["changed"] = False
            ss = gateway.getStorageSystem()

            if ss is None:
                raise Exception("The storage system {} is not found.".format(serial))

            if ucp_serial in ss["ucpSystems"]:
                gateway.removeStorageSystem(ucp_serial)
                results["changed"] = True
                serials.add(str(serial))
                results["comment"] = "Storage serial {} unregistered.".format(
                    ",".join(serials)
                )

                # operate on the matching ss serial only then exit
                # revisit this for detach all from ucp
                break
            else:
                raise Exception(
                    "The storage is not attached to the UCP {}".format(ucp_serial)
                )

        StorageSystemManager.logger.writeExitSDK(funcName)
        return results

    @staticmethod
    def formatStorageSystem(storageSystem):
        funcName = "hv_infra:StorageSystemManager:formatStorageSystem"
        StorageSystemManager.logger.writeEnterSDK(funcName)

        StorageSystemManager.logger.writeDebug("storageSystem={}", storageSystem)
        if storageSystem is None:
            return

        storageSystem.pop("resourceId", None)
        storageSystem.pop("storageEfficiencyStat", None)
        storageSystem.pop("storageDeviceLicenses", None)
        storageSystem.pop("isUnified", None)
        storageSystem.pop("tags", None)
        storageSystem.pop("deviceType", None)
        # storageSystem.pop('ucpSystems', None)
        storageSystem.pop("username", None)

        StorageSystemManager.logger.writeExitSDK(funcName)
        return storageSystem


class Utils:

    logger = Log()

    @staticmethod
    def is_hex(lun):
        try:
            int(lun, 16)
            return True
        except ValueError:
            return False

    @staticmethod
    def getlunFromHex(lun):
        if ":" in lun:
            lun = lun.replace(":", "")
        try:
            return int(lun, 16)
        except ValueError:
            return None

    @staticmethod
    def requestsPost_notused(url, json, verify):
        try:
            return requests.post(url, json=json, verify=verify)
        except Exception:

            # note: exception thrown by requests is caught by ansible module
            # it will not be caught here

            raise Exception("requests exception caught")

    @staticmethod
    def raiseException(sessionid, response, throwException=True):
        jsonStr = json.loads(response.headers["HIJSONFAULT"])
        if (
            "You need to re-initaite ADD STORAGE operation to create a new session"
            in str(jsonStr["ErrorMessage"])
        ):
            if sessionid is None:
                raise Exception(
                    "Session expired. You need to re-initiate session with add_storagesystem playbook to create a new session"
                )
            else:
                raise Exception(
                    "Session {0} is not found or expired. You need to re-initiate session with add_storagesystem \
                    playbook to create a new session".format(
                        sessionid
                    )
                )

        ex = Exception(jsonStr)
        hiex = HiException(ex)
        Utils.logger.writeHiException(hiex)
        if throwException:
            raise hiex

    @staticmethod
    def requestsGet_notused(url, params, verify):
        try:
            return requests.get(url, params=params, verify=verify)
        except Exception:

            # let's try to add storage again

            raise Exception("foo:w")

    @staticmethod
    def formatCapacity(valueMB, round_digits=4, valueInMB=False):

        # expected valueMB (from puma):
        # 5120 is 5120MB

        Utils.logger.writeDebug("formatCapacity, value={}", valueMB)
        oneK = 1024

        ivalue = float(valueMB)
        # Utils.logger.writeParam('formatCapacity, ivalue={}', ivalue)
        if ivalue == 0:
            return "0"

        ivalue = ivalue / 1024 / 1024
        # Utils.logger.writeParam('formatCapacity, ivalue={}', ivalue)
        if ivalue >= oneK * oneK and valueInMB is False:
            divfrac = oneK * oneK
            v = ivalue / divfrac
            # Utils.logger.writeDebug('TB Section, v={}', v)
            return str(round(v, round_digits)) + "TB"
        elif ivalue >= oneK and valueInMB is False:
            v = ivalue / oneK
            return str(round(v, round_digits)) + "GB"
        else:
            return str(round(ivalue, round_digits)) + "MB"

    @staticmethod
    def formatLun(lun):

        # Utils.logger.writeDebug('enter formatLun, lun={}', lun)

        if lun is None:
            return
        if lun.get("ports") is not None:
            del lun["ports"]
        if lun.get("resourceId") is not None:
            del lun["resourceId"]
        if lun.get("isDRS") is not None:
            lun["isDataReductionShareEnabled"] = lun["isDRS"]
            del lun["isDRS"]
        if lun.get("virtualLogicalUnitId") is not None:
            lun["virtualLdevId"] = lun["virtualLogicalUnitId"]
            del lun["virtualLogicalUnitId"]
        if lun.get("naaId") is not None:
            lun["canonicalName"] = lun["naaId"]
            del lun["naaId"]
        if lun.get("poolId") == -1:
            del lun["poolId"]
        if lun.get("parityGroupId") == "":
            del lun["parityGroupId"]
        # if lun.get('ldevId') is not None:
        #    lun['Lun'] = lun['ldevId']
        #    del lun['ldevId']
        # if lun.get('poolId') is not None:
        #    del lun['DynamicPool']
        if lun.get("totalCapacity") is not None:
            lun["totalCapacity_mb"] = Utils.formatCapacity(
                lun["totalCapacity"], 4, True
            )
            lun["totalCapacity"] = Utils.formatCapacity(lun["totalCapacity"])
        if lun.get("usedCapacity") is not None:
            lun["usedCapacity_mb"] = Utils.formatCapacity(lun["usedCapacity"], 4, True)
            lun["usedCapacity"] = Utils.formatCapacity(lun["usedCapacity"])
        # if HAS_ENUM and lun.get('Status') is not None:
        #    lun['Status'] = LunStatus.fromValue(lun.get('Status',
        #            0)).name
        # if HAS_ENUM and lun.get('Type') is not None:
        #    lun['Type'] = LunType.fromValue(lun.get('Type', 0)).name
        # if HAS_ENUM and lun.get('PoolType') is not None:
        #    lun['PoolType'] = PoolType.fromValue(lun.get('PoolType',
        #            0)).name
        # if lun.get('DedupCompressionProgress') == -1:
        #    lun['DedupCompressionProgress'] = ''
        # if lun.get('VirtualStorageDeviceId') == -1:
        #    lun['VirtualStorageDeviceId'] = ''
        # if lun.get('TotalCapacityInString') is not None:
        #    del lun['TotalCapacityInString']
        # if lun.get('FreeCapacityInString') is not None:
        #    del lun['FreeCapacityInString']

        # Utils.logger.writeDebug('exit formatLun, lun={}', lun)

    @staticmethod
    def formatLuns(luns):
        Utils.logger.writeDebug("752 formatLuns")
        for lun in luns:
            Utils.formatLun(lun)

    @staticmethod
    def formatGadPair(pair):
        pair["Status"] = ReplicationStatus.fromValue(pair.get("Status", 0)).name
        pair["Type"] = "GAD"
        if pair.get("FenceLevel") is not None:
            del pair["FenceLevel"]
        if pair.get("ManagementPoolId") is not None:
            del pair["ManagementPoolId"]
        if pair.get("JournalPoolId") is not None:
            del pair["JournalPoolId"]
        if pair.get("ReplicationPoolId") is not None:
            del pair["ReplicationPoolId"]
        if pair.get("DataPoolId") is not None:
            del pair["DataPoolId"]
        if pair.get("MirrorId") is not None:
            del pair["MirrorId"]
        if pair.get("SplitTime") is not None:
            del pair["SplitTime"]
        if pair.get("PairName") is not None:
            del pair["PairName"]
        if pair.get("VirtualDeviceId") is not None:
            pair["VSMSerial"] = pair["VirtualDeviceId"]
            del pair["VirtualDeviceId"]
        if pair.get("ConsistencyGroupId") is not None:
            if str(pair["ConsistencyGroupId"]) == str(-1):
                pair["ConsistencyGroupId"] = ""
        return pair

    @staticmethod
    def formatPool(pool):
        pool["Status"] = PoolStatus.getName(pool.get("Status", 0))
        pool["Type"] = PoolType.parse(pool.get("Type", 0)).name

        return pool

    @staticmethod
    def formatPools(pools):
        for pool in pools:
            Utils.formatPool(pool)

    @staticmethod
    def isStorageOOB(ip_address):
        Utils.logger.writeInfo(ip_address)
        Utils.logger.writeInfo(os.path.realpath("storage.json"))
        if os.path.isfile("./storage.json"):
            storageJson = os.path.realpath("storage.json")
        else:
            storageJson = os.getenv("HV_STORAGE_ANSIBLE_PROFILE")
        with open(storageJson) as connectionFile:
            connections = json.load(connectionFile)

        storagesystems = connections.get("sanStorageSystems", None)
        isOBB = connections.get("useOutOfBandConnection", None)

        for sysinfo in storagesystems:
            serial = sysinfo.get("serialNumber", None)
            if str(serial) == str(ip_address):
                isOBB = sysinfo.get("useOutOfBandConnection", None)
                break
        return str(isOBB).upper()

    @staticmethod
    def isGivenValidSerial(serial):

        if serial is None:
            raise Exception(
                "Storage systems have not been registered. Please run add_storagesystems.yml first."
            )

        Utils.logger.writeInfo(serial)
        Utils.logger.writeInfo(os.path.realpath("storage.json"))
        if os.path.isfile("./storage.json"):
            storageJson = os.path.realpath("storage.json")
        else:
            storageJson = os.getenv("HV_STORAGE_ANSIBLE_PROFILE")
        with open(storageJson) as connectionFile:
            connections = json.load(connectionFile)

        storagesystems = connections.get("sanStorageSystems", None)
        isfound = False

        for sysinfo in storagesystems:
            sysserial = sysinfo.get("serialNumber", None)
            if str(serial) == str(sysserial):
                isfound = True
                break
        return isfound

    @staticmethod
    def isGivenValidFileServerIp(ip_address):
        if ip_address is None:
            raise Exception("The fileServerIP is missing.")
        Utils.logger.writeInfo(ip_address)
        Utils.logger.writeInfo(os.path.realpath("storage.json"))
        if os.path.isfile("./storage.json"):
            storageJson = os.path.realpath("storage.json")
        else:
            storageJson = os.getenv("HV_STORAGE_ANSIBLE_PROFILE")
        with open(storageJson) as connectionFile:
            connections = json.load(connectionFile)
        nasStoragesystems = connections.get("nasStorageSystems", None)
        isfound = False

        for sysinfo in nasStoragesystems:
            fileServerIP = sysinfo.get("fileServerIP", None)
            if str(fileServerIP) == str(ip_address):
                isfound = True
                break
        return isfound

    @staticmethod
    def getSerialByNaa(naa):
        naa = str(naa)
        modelString = naa[20:23]
        if modelString == "502":
            subsytemModel = "HUS-VM"
        elif modelString == "003":
            subsytemModel = "VSP G-1000"
        elif modelString == "000":
            subsytemModel = "VSP"
        elif modelString == "504":
            subsytemModel = "VSP Gx00"
        elif modelString == "502":
            subsytemModel = "HM700"
        else:
            subsytemModel = "Other"

        serial = naa[23:28]

        # naa.substring(23, 28)

        serialNum1 = int(serial, 16)
        serialNum = str(serialNum1)
        if subsytemModel == "VSP Gx00":
            serialNum = "4" + serialNum
        elif subsytemModel == "HM700":
            serialNum = "2" + serialNum
        return serialNum


class StorageSystem:

    #     slogger = Log()

    def setDryRun(self, flag):

        # StorageSystem.slogger.writeEnterSDK("slogger: StorageSystem.setDryRun")

        funcName = "StorageSystem:setDryRun"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("dryRun={}", flag)

        # StorageSystem.slogger.writeEnterSDK("slogger: StorageSystem.setDryRun")

        funcName = "StorageSystem:setDryRun"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("dryRun={}", flag)
        self.dryRun = flag
        self.logger.writeExitSDK(funcName)

    def __init__(
        self,
        serial,
        management_address,
        management_username,
        management_password,
        api_token,
        webServiceIp=None,
        webServicePort=None,
        sessionId=None,
    ):

        self.logger = Log()
        self.dryRun = False
        self.serial = serial
        self.sessionId = sessionId
        self.isVirtualSerial = False

        self.management_address = management_address
        self.management_username = management_username
        self.management_password = management_password
        self.api_token = api_token
        self.basedUrl = "https://{0}".format(management_address)

        if (
            management_username is None
            or management_password is None
            or management_address is None
            or management_username == ""
            or management_password == ""
            or management_address == ""
        ):
            raise Exception(self.sessionId, "Management System is not configured.")

        if not webServiceIp:
            try:
                with open(
                    Log.getHomePath() + "/storage-connectors.json"
                ) as connectionFile:
                    connections = json.load(connectionFile)
                system = connections.get(str(serial))

                if system is None:
                    system = connections["hitachiAPIGatewayService"]
                    self.isVirtualSerial = True

                self.sessionId = None
                webServiceIp = system["storageGateway"]
                # webServicePort = system['storageGatewayPort']
            except IOError:
                raise Exception(
                    "Storage systems have not been registered. Please run add_storagesystems.yml first."
                )

        self.webServiceIp = webServiceIp
        self.webServicePort = webServicePort
        # self.basedUrl = 'https://{0}:{1}'.format(webServiceIp, webServicePort)
        # self.basedUrl = 'https://{0}'.format(webServiceIp)
        self.shouldVerifySslCertification = False

        self.htiManager = HTIManager(
            self.serial, self.webServiceIp, self.webServicePort, self.sessionId
        )
        self.remoteManager = RemoteManager(
            self.serial, self.webServiceIp, self.webServicePort, self.sessionId
        )
        self.vsmManager = VirtualStorageSystem(
            self.serial, self.webServiceIp, self.webServicePort, self.sessionId
        )

    def isSessionNotFound(self, exMsg):
        strToMatch = "Session is not found"
        if strToMatch in str(exMsg):
            return True
        else:
            return False

    def removeLogicalUnitFromResourceGroup(self, rgId, id):

        funcName = "hv_infra:removeLogicalUnitFromResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}", rgId)
        self.logger.writeParam("id={}", id)

        urlPath = "ResourceGroup/RemoveLogicalUnitFromResourceGroup"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "luId": id,
            "rgId": rgId,
        }

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def addLogicalUnitToResourceGroup(self, rgId, id):

        funcName = "hv_infra:addLogicalUnitToResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}", rgId)
        self.logger.writeParam("id={}", id)

        funcName = "hv_infra:addLogicalUnitToResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}", rgId)
        self.logger.writeParam("id={}", id)

        urlPath = "ResourceGroup/AddLogicalUnitToResourceGroup"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "luId": id,
            "rgId": rgId,
        }

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def deleteResourceGroup(self, rgId):

        funcName = "hv_infra:deleteResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}", rgId)

        urlPath = "ResourceGroup/DeleteResourceGroup"
        url = self.getUrl(urlPath)
        body = {"sessionId": self.sessionId, "serialNumber": self.serial, "rgId": rgId}

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def removeDriveGroupFromResourceGroup(self, rgId, parityGroupId):

        funcName = "hv_infra:removeDriveGroupFromResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}", rgId)
        self.logger.writeParam("parityGroupId={}", parityGroupId)

        urlPath = "ResourceGroup/RemoveDriveGroupFromResourceGroup"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "parityGroupId": parityGroupId,
            "rgId": rgId,
        }

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def addDriveGroupToResourceGroup(self, rgId, parityGroupId):

        funcName = "hv_infra:addDriveGroupToResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}", rgId)
        self.logger.writeParam("parityGroupId={}", parityGroupId)

        urlPath = "ResourceGroup/AddDriveGroupToResourceGroup"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "parityGroupId": parityGroupId,
            "rgId": rgId,
        }

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def removeHostGroupFromResourceGroup(
        self,
        rgId,
        hostGroupName,
        portId,
    ):

        funcName = "hv_infra:removeHostGroupFromResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}", rgId)
        self.logger.writeParam("hostGroupName={}", hostGroupName)
        self.logger.writeParam("portId={}", portId)

        urlPath = "ResourceGroup/RemoveHostGroupFromResourceGroup"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "hostGroupName": hostGroupName,
            "portId": portId,
            "rgId": rgId,
        }

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:

            # return response.json()

            return response
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def addHostGroupToResourceGroup(
        self,
        rgId,
        hostGroupName,
        portId,
    ):

        funcName = "hv_infra:addHostGroupToResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}", rgId)
        self.logger.writeParam("hostGroupName={}", hostGroupName)
        self.logger.writeParam("portId={}", portId)

        urlPath = "ResourceGroup/AddHostGroupToResourceGroup"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "hostGroupName": hostGroupName,
            "portId": portId,
            "rgId": rgId,
        }

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def removePortFromResourceGroup(self, rgId, id):

        funcName = "hv_infra:removePortFromResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}", rgId)
        self.logger.writeParam("id={}", id)

        urlPath = "ResourceGroup/RemovePortFromResourceGroup"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "portId": id,
            "rgId": rgId,
        }

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getTypeFromModel(self, model):
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

    def createVirtualBoxResourceGroup(
        self,
        remoteStorageId,
        model,
        rgName,
    ):

        funcName = "hv_infra:createVirtualBoxResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("remoteStorageId={}", remoteStorageId)
        self.logger.writeParam("model={}", model)
        self.logger.writeParam("rgName={}", rgName)

        funcName = "hv_infra:createVirtualBoxResourceGroup"
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

            return response
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def addPortToResourceGroup(self, rgId, id):

        funcName = "hv_infra:addPortToResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}", rgId)
        self.logger.writeParam("id={}", id)

        urlPath = "ResourceGroup/AddPortToResourceGroup"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "portId": id,
            "rgId": rgId,
        }

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def isVirtualSerialInUse(self):
        return self.isVirtualSerial

    def getUrl(self, urlPath):
        return "{0}/porcelain/{1}".format(self.basedUrl, urlPath)

    def addStorageSystemToISP(
        self, location, gatewayIP, gatewayPort, username, password
    ):

        funcName = "hv_infra:addStorageSystemToISP"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("location={}", location)
        self.logger.writeParam("gatewayIP={}", gatewayIP)
        self.logger.writeParam("gatewayPort={}", gatewayPort)
        self.logger.writeParam("username={}", username)

        headers = self.getAuthToken()
        self.logger.writeParam("headers={}", headers)

        urlPath = "v2/storage/devices"
        url = self.getUrl(urlPath)
        self.logger.writeParam("url={}", url)
        systems = self.getAllISPStorageSystems()
        self.logger.writeDebug("systems={}", systems)
        system = None
        for x in systems:
            self.logger.writeInfo(
                "int(x[serialNumber]) == self.serial={}",
                int(x["serialNumber"]) == self.serial,
            )
            if int(x["serialNumber"]) == self.serial:
                system = x
                break
        self.logger.writeInfo("system={}", system)

        if system is None:
            if system is None:
                body = {
                    "managementAddress": location,
                    "password": password,
                    "serialNumber": self.serial,
                    "username": username,
                }
                self.logger.writeInfo("body={}", body)
                response = requests.post(
                    url,
                    json=body,
                    headers=headers,
                    verify=self.shouldVerifySslCertification,
                )
        else:
            return StorageSystemManager.formatStorageSystem(system)

        if response.ok:
            if system is None:
                resJson = response.json()
                self.logger.writeInfo("response={}", resJson)
                resourceId = resJson["data"].get("resourceId")
                self.logger.writeInfo("resourceId={}", resourceId)
                taskId = response.json()["data"].get("taskId")
                self.logger.writeInfo("taskId={}", taskId)
                self.checkTaskStatus(taskId)
                time.sleep(10)
                systems = self.getAllISPStorageSystems()
                self.logger.writeDebug("systems={}", systems)
                system = None
                for x in systems:
                    self.logger.writeInfo(
                        "int(x[serialNumber]) == self.serial={}",
                        int(x["serialNumber"]) == self.serial,
                    )
                    if int(x["serialNumber"]) == self.serial:
                        system = x
                        break
            self.logger.writeInfo("system={}", system)
            return system
        elif "HIJSONFAULT" in response.headers:
            self.logger.writeInfo("HIJSONFAULT response={}", response)
            Utils.raiseException(self.sessionId, response)
        else:
            self.logger.writeInfo("Unknown Exception response={}", response.json())
            self.throwException(response)

    def addStorageSystem(
        self,
        location,
        gatewayIP,
        gatewayPort,
        username,
        password,
        useOutOfBandConnection,
        ucpID,
    ):

        funcName = "hv_infra:addStorageSystem"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("location={}", location)
        self.logger.writeParam("gatewayIP={}", gatewayIP)
        self.logger.writeParam("gatewayPort={}", gatewayPort)
        self.logger.writeParam("username={}", username)
        # self.logger.writeParam('password={}', password)

        # ucp_name = "ucp-21-25"
        # ucp_serial = "UCP-CI-12135"
        # ucp_name = "ucp-20-35"
        # ucp_serial = "UCP-CI-12035"
        ucp_serial = ucpID
        ucpManager = UcpManager(
            self.management_address, self.management_username, self.management_password
        )
        theUCP = ucpManager.getUcpSystem(ucp_serial)
        if theUCP is None:
            raise Exception("The System is not found")
        ucp_name = theUCP["name"]
        pumaGatewayAddress = theUCP["gatewayAddress"]
        if pumaGatewayAddress is None:
            raise Exception("The UCP gatewayAddress is not found")

        self.logger.writeInfo("ucp_name={}", ucp_name)
        self.logger.writeInfo("ucp_serial={}", ucp_serial)

        headers = self.getAuthToken()
        self.logger.writeParam("headers={}", headers)

        # systems = self.getAllStorageSystems()
        systems = self.getAllISPStorageSystems()
        self.logger.writeDebug("systems={}", systems)

        # use cases: SS is
        # in this UCP, return
        # in other UCP, do attach
        # in ISP only,  do attach
        # not in ISP, do addSS

        isInThisUCP = False
        isInUCP = False
        system = None
        for x in systems:

            if str(x["serialNumber"]) != str(self.serial):
                continue

            system = x
            ucpSerials = x["ucpSystems"]
            self.logger.writeInfo("20230523 ucpSerials={}", ucpSerials)

            # 'unicode' object has no attribute 'get'
            # ucpSerial = next((x for x in ucpSerials if x.get('ucpSystems')
            #             == ucp_serial), None)

            # isInThisUCP = [ele for ele in ucpSerials if(str(ele) in ucp_serial)]
            for y in ucpSerials:
                self.logger.writeInfo("20230523 y={}", str(y))
                isInUCP = True
                if str(y) == ucp_serial:
                    isInThisUCP = True
                    break

            break

        self.logger.writeInfo("20230523 system={}", system)
        self.logger.writeInfo("20230523 isInUCP={}", isInUCP)
        self.logger.writeInfo("20230523 isInThisUCP={}", isInThisUCP)

        if system is not None and not isInThisUCP:
            # attach ss to this UCP
            self.logger.writeDebug("20230523 attachSystemToUCP={}", isInUCP)
            response = self.attachSystemToUCP(
                location,
                gatewayIP,
                gatewayPort,
                username,
                password,
                useOutOfBandConnection,
                ucp_name,
            )
            system = self.getStorageSystem()

        elif system is None:

            # ss is not in the system, add ss (ucp must be added already)
            # operator will add to isp (this needs the puma gatewayAddress)
            # then ucp, then we have to wait for the facts to finish
            # we can print to the log file, that's about it?

            # get the puma gatewayAddress from UCP
            ucpManager = UcpManager(
                self.management_address,
                self.management_username,
                self.management_password,
            )
            theUCP = ucpManager.getUcpSystem(ucp_serial)

            self.logger.writeDebug("20230523 username={}", username)
            self.logger.writeDebug("20230523 password={}", password)
            self.logger.writeDebug("20230523 location={}", location)
            self.logger.writeDebug("20230523 self.serial={}", self.serial)
            self.logger.writeDebug("20230523 ucp_name={}", ucp_name)
            self.logger.writeDebug("20230523 pumaGatewayAddress={}", pumaGatewayAddress)
            body = {
                "username": username,
                "password": password,
                "managementAddress": location,
                "serialNumber": self.serial,
                "ucpSystem": ucp_name,
                "gatewayAddress": pumaGatewayAddress,
            }
            # self.logger.writeInfo('body={}', body)

            # addStorageSystem (first to ISP then UCP)
            urlPath = "v2/storage/devices"
            url = self.getUrl(urlPath)
            self.logger.writeDebug("20230523 url={}", url)
            response = requests.post(
                url,
                json=body,
                headers=headers,
                verify=self.shouldVerifySslCertification,
            )
            self.logger.writeDebug("20230523 response={}", response)

        else:
            # ss is already in thisUCP
            # we should show the ss from UCP so user can see which UCP this ss belongs to!!
            return StorageSystemManager.formatStorageSystem(system)

        if response.ok:

            if system is not None:
                resJson = response.json()
                self.logger.writeInfo("response={}", resJson)
                resourceId = resJson["data"].get("resourceId")
                self.logger.writeInfo("resourceId={}", resourceId)
                taskId = response.json()["data"].get("taskId")
                self.logger.writeInfo("taskId={}", taskId)
                self.checkTaskStatus(taskId)
                time.sleep(5)
                system = self.waitForUCPinSS(ucp_serial)

            self.logger.writeInfo("system={}", system)
            # system['webServiceIp'] = self.webServiceIp
            # system['webServicePort'] = self.webServicePort
            return StorageSystemManager.formatStorageSystem(system)
        elif "HIJSONFAULT" in response.headers:
            self.logger.writeInfo("HIJSONFAULT response={}", response)
            Utils.raiseException(self.sessionId, response)
        else:
            self.logger.writeInfo("Unknown Exception response={}", response.json())
            self.throwException(response)

    # wait until the ucp_serial is in the ssfact CR status
    def waitForUCPinSS(self, ucp_serial):
        funcName = "hv_infra:waitForUCPinSS"
        self.logger.writeEnterSDK(funcName)

        self.logger.writeDebug("looking for ucp_serial={}", ucp_serial)
        notFound = True
        while notFound:
            time.sleep(2)
            self.logger.writeInfo("onboarding in progress ...")
            system = self.getStorageSystem()
            ucps = system.get("ucpSystems", None)
            if ucps is None:
                continue
            self.logger.writeDebug("in ucps={}", ucps)
            if ucp_serial in ucps:
                notFound = False

        self.logger.writeExitSDK(funcName)
        return system

    # called after detach from UCP,
    # monitor the ucp_serial in the ISP.ss.ucpsystems list,
    # expect to find ss_serial in ISP
    def waitForUCPnotInSS(self, ucp_serial):
        funcName = "hv_infra:waitForUCPnotInSS"
        self.logger.writeEnterSDK(funcName)

        self.logger.writeDebug("ucp_serial={}", ucp_serial)
        self.logger.writeDebug("self.serial={}", self.serial)

        system = None
        found = True
        while found:
            time.sleep(2)
            found = False

            # get from ISP
            systems = self.getAllISPStorageSystems()
            for x in systems:

                if str(x["serialNumber"]) != str(self.serial):
                    continue

                system = x
                ucps = x.get("ucpSystems", None)
                if ucps is None:
                    raise Exception(
                        "UCP system list is not found in the storage system."
                    )

                self.logger.writeDebug("in ucps={}", ucps)
                if ucp_serial in ucps:
                    found = True

        self.logger.writeExitSDK(funcName)
        return system

    def removeStorageSystem(self, ucp_serial):
        funcName = "hv_infra:removeStorageSystem"
        self.logger.writeEnterSDK(funcName)

        # this is done in the caller? or check for none here

        if ucp_serial is not None:
            # detach from UCP
            self.removeStorageSystemFromUCP(ucp_serial)

        # get SS with self.serial of the SS
        # keep getting it until the ucp_serial is not found
        found = True
        attached = True
        while found:
            system = self.getStorageSystem()
            if system is None:
                # we may have to take a look at getStorageSystem for this case,
                # we want it to return something so we can go delete ss from isp
                return
            ucps = system["ucpSystems"]
            if ucp_serial not in ucps:
                found = False
                if len(ucps) == 0:
                    attached = False
            self.logger.writeInfo("Storage system is updating ...")

        if attached:
            self.logger.writeDebug("no removeStorageDevice")
            return

        # removeStorageDevice
        self.logger.writeDebug("removeStorageDevice")
        resourceId = self.getStorageSystemResourceIdInISP()

        headers = self.getAuthToken()
        # self.logger.writeParam('headers={}', headers)

        urlPath = "v2/storage/devices/{0}".format(resourceId)
        url = self.getUrl(urlPath)
        self.logger.writeParam("url={}", url)
        self.logger.writeInfo("ss GRID={}", resourceId)

        response = requests.delete(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        if response.ok:
            resJson = response.json()
            self.logger.writeInfo("response={}", resJson)
            resourceId = resJson["data"].get("resourceId")
            self.logger.writeInfo("resourceId={}", resourceId)
            taskId = response.json()["data"].get("taskId")
            self.logger.writeInfo("taskId={}", taskId)
            self.checkTaskStatus(taskId)
            time.sleep(5)
        elif "HIJSONFAULT" in response.headers:
            self.logger.writeInfo("HIJSONFAULT response={}", response)
            Utils.raiseException(self.sessionId, response)
        else:
            self.logger.writeInfo("Unknown Exception response={}", response.json())
            self.throwException(response)

    # this version uses waitForUCPnotInSS,
    # if we are deleting the last ucp from the system, then this can be fast,
    # problem is we need the details for the get storage yml, and that needs the fact to finish,
    # in general, we have to check the fact, so it has to wait for the fact to finish refreshing,
    # save this for reviewing the design
    def removeStorageSystem2(self, ucp_serial):
        funcName = "hv_infra:removeStorageSystem2"
        self.logger.writeEnterSDK(funcName)

        if ucp_serial is not None:
            # detach from UCP
            self.removeStorageSystemFromUCP(ucp_serial)

        # i.e. the ucp list in ss is not empty
        # revisit this later
        attached = True

        self.waitForUCPnotInSS(ucp_serial)

        if attached:
            self.logger.writeDebug("no removeStorageDevice")
            return

        # removeStorageDevice
        self.logger.writeDebug("removeStorageDevice")
        resourceId = self.getStorageSystemResourceIdInISP()

        headers = self.getAuthToken()
        # self.logger.writeParam('headers={}', headers)

        urlPath = "v2/storage/devices/{0}".format(resourceId)
        url = self.getUrl(urlPath)
        self.logger.writeParam("url={}", url)
        self.logger.writeInfo("ss GRID={}", resourceId)

        response = requests.delete(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        if response.ok:
            resJson = response.json()
            self.logger.writeInfo("response={}", resJson)
            resourceId = resJson["data"].get("resourceId")
            self.logger.writeInfo("resourceId={}", resourceId)
            taskId = response.json()["data"].get("taskId")
            self.logger.writeInfo("taskId={}", taskId)
            self.checkTaskStatus(taskId)
            time.sleep(5)
        elif "HIJSONFAULT" in response.headers:
            self.logger.writeInfo("HIJSONFAULT response={}", response)
            Utils.raiseException(self.sessionId, response)
        else:
            self.logger.writeInfo("Unknown Exception response={}", response.json())
            self.throwException(response)

    def removeStorageSystemFromUCP(self, ucp_serial):
        funcName = "hv_infra:removeStorageSystemFromUCP"
        self.logger.writeEnterSDK(funcName)
        systems = self.getAllStorageSystems()

        self.logger.writeDebug("systems={}", systems)

        system = None
        for x in systems:
            self.logger.writeDebug(int(x["serialNumber"]))
            self.logger.writeDebug(self.serial)
            self.logger.writeDebug(int(x["serialNumber"]) == self.serial)

            if str(x["serialNumber"]) == str(self.serial):
                system = x
                break

        if system is None:
            return

        resourceId = str(system.get("resourceId"))

        # ensure the ucp is in the ss
        ucps = system.get("ucpSystems", None)
        self.logger.writeDebug("ucps={}", ucps)
        self.logger.writeDebug("ucp_serial={}", ucp_serial)
        if ucps is None or ucp_serial not in ucps:
            self.throwException("The storage system is not attached to the UCP.")

        # get the ucp resourceId from ucp
        ucpManager = UcpManager(
            self.management_address, self.management_username, self.management_password
        )
        theUCP = ucpManager.getUcpSystem(ucp_serial)
        if theUCP is None:
            raise Exception("The System is not found")
        resourceIdUCP = theUCP.get("resourceId")

        urlPath = "v2/systems/{0}/device/{1}".format(resourceIdUCP, resourceId)
        url = self.getUrl(urlPath)

        self.logger.writeParam("url={}", url)
        self.logger.writeInfo("resourceId={}", resourceId)
        self.logger.writeInfo("ucp_resource_id={}", resourceIdUCP)

        headers = self.getAuthToken()
        self.logger.writeInfo("0608 headers={}", headers)
        response = requests.delete(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeInfo("0608 response={}", response)
        if response.ok:
            resJson = response.json()
            self.logger.writeInfo("response={}", resJson)
            resourceId = resJson["data"].get("resourceId")
            self.logger.writeInfo("resourceId={}", resourceId)
            taskId = response.json()["data"].get("taskId")
            self.logger.writeInfo("taskId={}", taskId)
            self.checkTaskStatus(taskId)
            time.sleep(5)
        elif "HIJSONFAULT" in response.headers:
            self.logger.writeInfo("HIJSONFAULT response={}", response)
            Utils.raiseException(self.sessionId, response)
        else:
            self.logger.writeInfo("Unknown Exception response={}", response.json())
            self.throwException(response)

    # only name the ucp_name to attach
    def attachSystemToUCP(
        self,
        location,
        gatewayIP,
        gatewayPort,
        username,
        password,
        useOutOfBandConnection,
        ucp_name,
    ):

        funcName = "hv_infra:attachSystemToUCP"
        self.logger.writeEnterSDK(funcName)

        systems = self.getAllISPStorageSystems()

        # self.logger.writeDebug('systems={}', systems)
        self.logger.writeDebug("self.serial={}", self.serial)
        self.logger.writeDebug("20230523 ucp_name={}", ucp_name)

        system = None
        resourceId = None
        for x in systems:
            self.logger.writeDebug(int(x["serialNumber"]))
            self.logger.writeDebug(int(x["serialNumber"]) == self.serial)

            if str(x["serialNumber"]) == str(self.serial):
                system = x
                resourceId = str(x["resourceId"])
                self.logger.writeDebug("20230523 resourceId={}", resourceId)
                break

        if system is None:
            self.logger.writeDebug("StorageSystem not found")
            return

        ucpsystem = self.getUcpSystemByName(ucp_name)
        self.logger.writeDebug("20230523 ucpsystem={}", ucpsystem)
        resourceIdUCP = str(ucpsystem["resourceId"])
        self.logger.writeDebug("20230523 resourceId={}", resourceId)
        self.logger.writeDebug("20230523 resourceIdUCP={}", resourceIdUCP)

        headers = self.getAuthToken()
        # self.logger.writeParam("headers={}", headers)

        urlPath = "v2/systems/{0}/device/{1}".format(resourceIdUCP, resourceId)
        url = self.getUrl(urlPath)
        self.logger.writeDebug("20230523 url={}", url)
        self.logger.writeInfo("system={}", resourceId)
        self.logger.writeDebug("ucp_name={}", ucp_name)
        self.logger.writeDebug("ucp_resource_id={}", resourceIdUCP)

        response = requests.patch(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        # self.logger.writeDebug('20230523 response={}', response)

        if response.ok:
            resJson = response.json()
            self.logger.writeDebug("response={}", resJson)
            resourceId = resJson["data"].get("resourceId")
            self.logger.writeDebug("resourceId={}", resourceId)
            taskId = response.json()["data"].get("taskId")
            self.logger.writeDebug("taskId={}", taskId)
            self.checkTaskStatus(taskId)
            # it is "REFRESHING"
            time.sleep(5)
            self.logger.writeExitSDK(funcName)
            return response
        elif "HIJSONFAULT" in response.headers:
            self.logger.writeError("HIJSONFAULT response={}", response)
            Utils.raiseException(self.sessionId, response)
        else:
            self.logger.writeError("Unknown Exception response={}", response.json())
            self.throwException(response)

    # returns ss and ucp grid if ss is found
    # else throws exception
    def getStorageSystemResourceId(self):
        """
        docstring
        """

        funcName = "hv_infra:getStorageSystemResourceId"
        self.logger.writeEnterSDK(funcName)
        headers = self.getAuthToken()
        self.logger.writeParam("headers={}", headers)

        urlPath = "v2/storage/devices"
        url = self.getUrl(urlPath)
        self.logger.writeParam("url={}", url)

        systems = self.getAllStorageSystems()

        self.logger.writeDebug("systems={}", systems)

        system = None
        for x in systems:
            self.logger.writeDebug(int(x["serialNumber"]))
            self.logger.writeDebug(self.serial)
            self.logger.writeDebug(int(x["serialNumber"]) == self.serial)

            if str(x["serialNumber"]) == str(self.serial):
                system = x
                break
        if system is None:
            raise Exception(
                "Invalid serial = {0}, please check once and try again.".format(
                    self.serial
                )
            )

        ucp = system.get("ucpSystems")[0]
        self.logger.writeExitSDK(funcName)
        return (str(system.get("resourceId")), str(ucp))

    def getStorageSystemResourceIdInISP(self):
        """
        docstring
        """

        funcName = "hv_infra:getStorageSystemResourceIdInISP"
        self.logger.writeEnterSDK(funcName)
        headers = self.getAuthToken()
        # self.logger.writeParam("headers={}", headers)

        urlPath = "v2/storage/devices"
        url = self.getUrl(urlPath)
        self.logger.writeParam("url={}", url)

        systems = self.getAllISPStorageSystems()

        self.logger.writeDebug("systems={}", systems)

        system = None
        for x in systems:
            self.logger.writeDebug(int(x["serialNumber"]))
            self.logger.writeDebug(self.serial)
            self.logger.writeDebug(int(x["serialNumber"]) == self.serial)
            if str(x["serialNumber"]) == str(self.serial):
                system = x
                break
        if system is None:
            raise Exception(
                "Invalid serial = {0}, please check once and try again.".format(
                    self.serial
                )
            )

        self.logger.writeExitSDK(funcName)
        return str(system.get("resourceId"))

    # fetch the SS CRs
    def fetchStorageSystems(self):
        funcName = "hv_infra:fetchStorageSystems"
        self.logger.writeEnterSDK(funcName)

        headers = self.getAuthToken()
        urlPath = "v2/storage/devices"
        url = self.getUrl(urlPath)
        self.logger.writeParam("url={}", url)
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug("response={}", response)

        storage_systems = []
        if response.ok:
            authResponse = response.json()
            self.logger.writeDebug("ISP response Json={}", authResponse)
            data = authResponse.get("data")
            # storage_systems.extend(data.get('storageDevices'))
            storage_systems = data

        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

        self.logger.writeExitSDK(funcName)
        return storage_systems

    def getStorageSystem(self):
        """
        docstring
        """
        funcName = "hv_infra:getStorageSystem"
        self.logger.writeEnterSDK(funcName)

        systems = self.fetchStorageSystems()
        self.logger.writeDebug("systems={}", systems)

        system = None
        for x in systems:
            self.logger.writeDebug(int(x["serialNumber"]))
            self.logger.writeDebug(self.serial)
            if str(x["serialNumber"]) == str(self.serial):
                system = x
                break

        self.logger.writeDebug("system={}", system)
        result = StorageSystemManager.formatStorageSystem(system)

        self.logger.writeExitSDK(funcName)
        return result

    def getAuthToken(self):
        funcName = "hv_infra:getAuthToken"
        self.logger.writeEnterSDK(funcName)

        body = {
            "username": self.management_username,
            "password": self.management_password,
        }

        urlPath = "v2/auth/login"
        url = "{0}/porcelain/{1}".format(self.basedUrl, urlPath)

        self.logger.writeDebug("20230505 username={}", body["username"])
        self.logger.writeDebug("20230505 url={}", url)

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        token = None
        if response.ok:
            authResponse = response.json()
            data = authResponse["data"]
            token = data.get("token")
        elif "HIJSONFAULT" in response.headers:
            self.logger.writeError("HIJSONFAULT response={}", response)
            Utils.raiseException(self.sessionId, response)
        else:
            self.logger.writeError("Unknown Exception response={}", response)
            self.throwException(response)

        headers = {"Authorization": "Bearer {0}".format(token)}

        return headers

    def createUcpSystem(self, gatewayIp):
        funcName = "hv_infra:createUcpSystem"
        self.logger.writeEnterSDK(funcName)

        gatewayLast5 = gatewayIp.replace(".", "")[-5:]
        ucp_name = "ucp-{0}".format(gatewayLast5)
        ucp_serial = "Logical-UCP-{0}".format(gatewayLast5)
        system = self.getUcpSystem(gatewayIp)
        self.logger.writeDebug("ucpsystem={}", system)
        if system is None:
            body = {
                "gatewayAddress": gatewayIp,
                "model": "Logical UCP",
                "name": ucp_name,
                "region": "EMEA",
                "serialNumber": ucp_serial,
                "country": "Belgium",
                "zipcode": 1020,
                "zone": "zone",
            }
            urlPath = "v2/systems"
            url = "{0}/porcelain/{1}".format(self.basedUrl, urlPath)

            response = requests.post(
                url,
                headers=self.getAuthToken(),
                json=body,
                verify=self.shouldVerifySslCertification,
            )
            self.logger.writeExitSDK(funcName)

            if response.ok:
                resposeJson = response.json()
                resposeJson["data"]
                self.logger.writeError("resposeJson={}", resposeJson)
                taskId = resposeJson["data"].get("taskId")
                self.checkTaskStatus(taskId)
                time.sleep(10)
            elif "HIJSONFAULT" in response.headers:
                self.logger.writeError("HIJSONFAULT response={}", response)
                Utils.raiseException(self.sessionId, response)
            else:
                self.logger.writeError("Unknown Exception response={}", response)
                raise Exception(
                    "Unknown error HTTP {0}".format(
                        response.status_code + response.message
                    )
                )
        return ucp_name, ucp_serial

    def updateUcpSystem(self, gatewayIp):
        funcName = "hv_infra:updateUcpSystem"
        self.logger.writeEnterSDK(funcName)

        gatewayLast5 = gatewayIp.replace(".", "")[-5:]
        ucp_name = "ucp-{0}".format(gatewayLast5)
        ucp_serial = "Logical-UCP-{0}".format(gatewayLast5)
        system = self.getUcpSystem(gatewayIp)
        self.logger.writeDebug("ucpsystem={}", system)
        if system:
            body = {
                "gatewayAddress": gatewayIp,
                "model": "Logical UCP",
                "name": ucp_name,
                "region": "EMEA",
                "serialNumber": ucp_serial,
                "country": "Belgium",
                "zipcode": 1020,
                "zone": "zone",
            }
            urlPath = "v2/systems"
            url = "{0}/porcelain/{1}".format(self.basedUrl, urlPath)

            response = requests.post(
                url,
                headers=self.getAuthToken(),
                json=body,
                verify=self.shouldVerifySslCertification,
            )
            self.logger.writeExitSDK(funcName)

            if response.ok:
                resposeJson = response.json()
                resposeJson["data"]
                self.logger.writeDebug("resposeJson={}", resposeJson)
                taskId = resposeJson["data"].get("taskId")
                self.checkTaskStatus(taskId)
            elif "HIJSONFAULT" in response.headers:
                self.logger.writeError("HIJSONFAULT response={}", response)
                Utils.raiseException(self.sessionId, response)
            else:
                self.logger.writeError("Unknown Exception response={}", response)
                raise Exception(
                    "Unknown error HTTP {0}".format(
                        response.status_code + response.message
                    )
                )
        return ucp_name

    # old obselete helper func
    def getUcpSystem(self, gatewayIp):
        funcName = "hv_infra:getUcpSystem"
        self.logger.writeEnterSDK(funcName)

        gatewayLast5 = gatewayIp.replace(".", "")[-5:]
        ucp_name = "ucp-{0}".format(gatewayLast5)
        "Logical-UCP-{0}".format(gatewayLast5)

        systems = self.getAllUcpSystem()
        system = next((x for x in systems if x.get("name") == ucp_name), None)
        self.logger.writeExitSDK(funcName)
        return system

    def getUcpSystemByName(self, ucpname):
        funcName = "hv_infra:getUcpSystemByName"
        self.logger.writeEnterSDK(funcName)

        systems = self.getAllUcpSystem()
        # self.logger.writeDebug('20230523 systems={}', systems)

        # system = next((x for x in systems if str(x['serialNumber'])
        #                 == ucpSerial), None)

        self.logger.writeDebug("20230523 systems={}", ucpname)
        system = next((x for x in systems if str(x["name"]) == ucpname), None)
        self.logger.writeDebug("20230523 system={}", system)
        # system = None
        # for x in systems:
        #     self.logger.writeDebug('20230523 ucp={}', x)
        #     self.logger.writeDebug('20230523 serialNumber={}', x['serialNumber'])
        #     if str(x['serialNumber']) == ucpname:
        #         system = x
        #         break

        self.logger.writeExitSDK(funcName)
        return system

    def getAllUcpSystem(self):
        funcName = "hv_infra:getAllUcpSystem"
        self.logger.writeEnterSDK(funcName)

        urlPath = "v2/systems"
        url = self.getUrl(urlPath)

        headers = self.getAuthToken()
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            authResponse = response.json()
            self.logger.writeDebug("AllUcpSystem={}", authResponse)
            systems = authResponse.get("data")
            return systems
        elif "HIJSONFAULT" in response.headers:
            self.logger.writeError("raiseException={}", response)
            Utils.raiseException(self.sessionId, response)
        else:
            self.logger.writeError("throwException={}", response)
            self.throwException(response)

    def getvCenter(self, vcip):
        funcName = "hv_infra:getvCenter"
        self.logger.writeEnterSDK(funcName)
        vCenters = self.getAllvCenter()
        vCenter = next((x for x in vCenters if x.get("vcenterAddress") == vcip), None)
        self.logger.writeExitSDK(funcName)
        return vCenter

    def getAllvCenter(self):
        funcName = "hv_infra:getAllvCenter"
        self.logger.writeEnterSDK(funcName)

        urlPath = "v2/virtualization/vcenters"
        url = self.getUrl(urlPath)

        headers = self.getAuthToken()
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            authResponse = response.json()
            self.logger.writeDebug("vcenters={}", authResponse)
            systems = authResponse.get("data")
            return systems
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def addvCenter(self, vcip, user, password, ucpname):
        funcName = "hv_infra:addvCenter"
        self.logger.writeEnterSDK(funcName)
        vCenter = self.getvCenter(vcip)
        self.logger.writeDebug("vCenter={}", vCenter)
        if vCenter is None:
            body = {
                "vcenterAddress": vcip,
                "username": user,
                "password": password,
                "ucpSystem": ucpname,
            }
            urlPath = "v2/virtualization/vcenters"
            url = "{0}/porcelain/{1}".format(self.basedUrl, urlPath)
            self.logger.writeDebug("url={}", url)
            self.logger.writeDebug("body={}", body)
            response = requests.post(
                url,
                headers=self.getAuthToken(),
                json=body,
                verify=self.shouldVerifySslCertification,
            )
            self.logger.writeExitSDK(funcName)

            if response.ok:
                resposeJson = response.json()
                resposeJson["data"]
                self.logger.writeDebug("resposeJson={}", resposeJson)
                taskId = resposeJson["data"].get("taskId")
                self.checkTaskStatus(taskId)
                vCenter = self.getvCenter(vcip)
                time.sleep(10)
            elif "HIJSONFAULT" in response.headers:
                self.logger.writeError("HIJSONFAULT response={}", response)
                Utils.raiseException(self.sessionId, response)
            else:
                self.logger.writeError("Unknown Exception response={}", response)
                raise Exception("Unknown error HTTP {0}".format(response.status_code))

    # this old function only getAllStorageSystems from the first ucp,
    # it assume there is only one ucp
    def getAllStorageSystems(self):
        funcName = "hv_infra:getAllStorageSystems"
        self.logger.writeEnterSDK(funcName)

        urlPath = "v2/storage/devices"
        url = self.getUrl(urlPath)

        ucp_systems = self.getAllUcpSystem()
        storage_systems = []
        for ucp in ucp_systems:
            sn = str(ucp.get("serialNumber"))
            self.logger.writeDebug(sn)
            body = {"ucpSystem": sn}
            self.logger.writeDebug("body={}", body)
            headers = self.getAuthToken()

            response = requests.get(
                url,
                headers=headers,
                params=body,
                verify=self.shouldVerifySslCertification,
            )

            if response.ok:
                authResponse = response.json()
                systems = authResponse.get("data")
                storage_systems.extend(systems)
            elif "HIJSONFAULT" in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)
        return storage_systems

    def getAllISPStorageSystems(self):
        funcName = "hv_infra:getAllISPStorageSystems"
        self.logger.writeEnterSDK(funcName)

        urlPath = "v2/systems/default"
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()

        self.logger.writeDebug("url={}", url)
        self.logger.writeDebug("headers={}", headers)
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug("response={}", response)

        storage_systems = []
        if response.ok:
            authResponse = response.json()
            self.logger.writeDebug("ISP response Json={}", authResponse)
            data = authResponse.get("data")
            storage_systems.extend(data.get("storageDevices"))
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)
        return storage_systems

    def getStorageInfoByResourceId(self, resourceId):

        funcName = "hv_infra:getStorageInfoByResourceId"

        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("resourceId={}", resourceId)
        urlPath = "v2/storage/devices/{0}".format(resourceId)
        url = self.getUrl(urlPath)

        # body = {'id': resourceId}

        headers = self.getAuthToken()
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        self.logger.writeDebug("parse the response")
        if response.ok:
            authResponse = response.json()
            system = authResponse["data"]
            self.logger.writeDebug("system={}", system)
            system["StorageDeviceType"] = StorageType.parse(
                system.get("deviceType")
            ).name
            system["StorageDeviceModel"] = StorageModel.parse(system.get("model")).name

            # del system['model']
            # del system['deviceType']
            self.logger.writeExitSDK(funcName)
            return system
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def checkAndGetStorageInfoByResourceId(self, resourceId):
        funcName = "hv_infra:checkAndGetStorageInfoByResourceId"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("resourceId={}", resourceId)
        system = self.getStorageInfoByResourceId(resourceId)
        self.logger.writeDebug("system={}", system)
        while (
            system["operationalStatus"] == "Running"
            or system["operationalStatus"] == "Processing"
        ):
            self.logger.writeDebug(
                "system[operationalStatus]={}", system["operationalStatus"]
            )
            self.logger.writeInfo(
                "storage system with resource {0} resource state is onboarding".format(
                    resourceId
                )
            )
            time.sleep(5)
            system = self.getStorageInfoByResourceId(resourceId)

        self.logger.writeExitSDK(funcName)
        return system

    def createCommandDevice(self, poolId, vcip, user, pword, vmName, ucp_serial):
        funcName = "hv_infra:createCommandDevice"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("poolId={}", poolId)
        self.logger.writeParam("vcip={}", vcip)
        self.logger.writeParam("user={}", user)
        self.logger.writeParam("pword={}", pword)
        self.logger.writeParam("vmName={}", vmName)

        resourceId = self.getStorageSystemResourceIdInISP()

        self.logger.writeParam("resourceId={}", resourceId)
        self.logger.writeParam("ucp={}", ucp_serial)
        urlPath = "v2/storage/devices/storage/command/device"
        url = self.getUrl(urlPath)
        self.logger.writeDebug("url={}", url)

        body = {
            "poolId": poolId,
            "vmName": vmName,
            "size": "50MB",
            "resourceGroupId": 0,
            "ucpSystem": ucp_serial,
            "serialNumber": self.serial,
        }

        self.logger.writeDebug("body={}", body)
        headers = self.getAuthToken()
        # self.logger.writeDebug("headers={}", headers)
        response = requests.post(
            url, json=body, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug("response={}", response.json())
        self.logger.writeExitSDK(funcName)
        if response.ok:
            resourceId = response.json()["data"]["resourceId"]
            self.logger.writeDebug("resourceId={}", resourceId)
            taskId = response.json()["data"].get("taskId")
            self.checkTaskStatus(taskId)
            time.sleep(5)
            return self.getCommandDeviceEvents(taskId)
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def createLunInDP(
        self,
        lun,
        pool,
        size,
        dedup,
        name="",
    ):
        funcName = "hv_infra:createLunInDP"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("pool={}", pool)
        self.logger.writeParam("sizeInGB={}", size)
        self.logger.writeParam("luName={}", name)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam("resourceId={}", resourceId)
        self.logger.writeParam("ucp={}", ucp)

        urlPath = "v2/storage/devices/{0}/volumes".format(resourceId)
        url = self.getUrl(urlPath)
        self.logger.writeDebug("url={}", url)
        body = {
            "deduplicationCompressionMode": dedup,
            "poolId": pool,
            "name": name,
            "capacity": size,
            "resourceGroupId": 0,
            "ucpSystem": ucp,
        }
        if lun is not None:
            body["lunId"] = lun
        self.logger.writeDebug("body={}", body)
        headers = self.getAuthToken()
        self.logger.writeDebug("headers={}", headers)
        response = requests.post(
            url, json=body, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug("response={}", response.json())
        self.logger.writeExitSDK(funcName)
        if response.ok:
            resourceId = response.json()["data"]["resourceId"]
            self.logger.writeDebug("resourceId={}", resourceId)
            taskId = response.json()["data"].get("taskId")
            self.checkTaskStatus(taskId)
            time.sleep(5)
            if lun is None:
                lun = self.getLunIdFromTaskStatusEvents(taskId)
            return lun
        elif "HIJSONFAULT" in response.headers:

            # return self.getLunByResourceId1(resourceId)

            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def updateLunInDP(self, lunResourceId, size):
        funcName = "hv_infra:updateLunInDP"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lunResourceId={}", lunResourceId)
        self.logger.writeParam("sizeInGB={}", size)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam("resourceId={}", resourceId)
        self.logger.writeParam("lunResourceId={}", lunResourceId)
        self.logger.writeParam("ucp={}", ucp)

        urlPath = "v2/storage/devices/{0}/volumes/{1}".format(resourceId, lunResourceId)
        url = self.getUrl(urlPath)
        self.logger.writeDebug("url={}", url)
        body = {"capacity": size}
        self.logger.writeDebug("body={}", body)
        headers = self.getAuthToken()
        self.logger.writeDebug("headers={}", headers)
        response = requests.patch(
            url, json=body, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug("response={}", response.json())
        self.logger.writeExitSDK(funcName)
        if response.ok:
            resourceId = response.json()["data"]["resourceId"]
            self.logger.writeDebug("resourceId={}", resourceId)
            taskId = response.json()["data"].get("taskId")
            self.checkTaskStatus(taskId)
            time.sleep(10)
        elif "HIJSONFAULT" in response.headers:

            # return self.getLunByResourceId1(resourceId)

            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def createLunInPG(
        self,
        lun,
        parityGroup,
        size,
        stripeSize,
        metaResourceSerial,
        luName,
    ):

        funcName = "hv_infra:createLunInPG"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("parityGroupId={}", parityGroup)
        self.logger.writeParam("sizeInGB={}", size)
        self.logger.writeParam("luName={}", luName)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam("resourceId={}", resourceId)
        self.logger.writeParam("ucp={}", ucp)

        urlPath = "v2/storage/devices/{0}/volumes".format(resourceId)
        url = self.getUrl(urlPath)
        self.logger.writeDebug("url={}", url)
        body = {
            "parityGroupId": parityGroup,
            "name": luName,
            "capacity": size,
            "resourceGroupId": 0,
            "ucpSystem": ucp,
        }
        if lun is not None:
            body["lunId"] = lun
        self.logger.writeDebug("body={}", body)
        headers = self.getAuthToken()
        self.logger.writeDebug("headers={}", headers)
        response = requests.post(
            url, json=body, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug("response={}", response.json())
        self.logger.writeExitSDK(funcName)
        if response.ok:
            resourceId = response.json()["data"]["resourceId"]
            self.logger.writeDebug("resourceId={}", resourceId)
            taskId = response.json()["data"].get("taskId")
            self.checkTaskStatus(taskId)
            time.sleep(5)
            if lun is None:
                lun = self.getLunIdFromTaskStatusEvents(taskId)
            return lun
        elif "HIJSONFAULT" in response.headers:

            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def updateLunName(self, lunResourceId, lunName):
        funcName = "hpe_infra:updateLunInDP"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lunResourceId={}", lunResourceId)
        self.logger.writeParam("sizeInGB={}", lunName)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam("resourceId={}", resourceId)
        self.logger.writeParam("lunResourceId={}", lunResourceId)
        self.logger.writeParam("ucp={}", ucp)

        urlPath = "v2/storage/devices/{0}/volumes/{1}".format(resourceId, lunResourceId)
        url = self.getUrl(urlPath)
        self.logger.writeDebug("url={}", url)
        body = {"lunName": lunName}
        self.logger.writeDebug("body={}", body)
        headers = self.getAuthToken()
        # self.logger.writeDebug("headers={}", headers)
        response = requests.patch(
            url, json=body, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug("response={}", response.json())
        self.logger.writeExitSDK(funcName)
        if response.ok:
            resourceId = response.json()["data"]["resourceId"]
            self.logger.writeDebug("resourceId={}", resourceId)
            taskId = response.json()["data"].get("taskId")
            self.checkTaskStatus(taskId)
            time.sleep(10)
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def setDedupCompression(self, lunResourceId, dedupMode):
        funcName = "hv_infra:setDedupCompression"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lunResourceId={}", lunResourceId)
        self.logger.writeParam("dedupMode={}", dedupMode)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam("resourceId={}", resourceId)
        self.logger.writeParam("lunResourceId={}", lunResourceId)
        self.logger.writeParam("ucp={}", ucp)

        urlPath = "v2/storage/devices/{0}/volumes/{1}".format(resourceId, lunResourceId)
        url = self.getUrl(urlPath)
        self.logger.writeDebug("url={}", url)
        body = {"deduplicationCompressionMode": dedupMode}
        self.logger.writeDebug("body={}", body)
        headers = self.getAuthToken()
        self.logger.writeDebug("headers={}", headers)
        response = requests.patch(
            url, json=body, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug("response={}", response.json())
        self.logger.writeExitSDK(funcName)
        if response.ok:
            resourceId = response.json()["data"]["resourceId"]
            self.logger.writeDebug("resourceId={}", resourceId)
            taskId = response.json()["data"].get("taskId")
            self.checkTaskStatus(taskId)
            time.sleep(10)
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def cloneLunInDP(
        self,
        sourceLun,
        pool,
        clonedLunName,
    ):

        funcName = "hv_infra:cloneLunInDP"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("sourceLun={}", sourceLun)
        self.logger.writeParam("pool={}", pool)
        self.logger.writeParam("clonedLunName={}", clonedLunName)

        urlPath = "LogicalUnit/LogicalUnit/CloneInDP"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "lun": sourceLun,
            "pool": pool,
            "lunName": clonedLunName,
        }

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            taskId = response.json()["data"].get("taskId")
            return self.checkTaskStatus(taskId)
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def createPresentedVolume(
        self,
        lun,
        pool,
        resourceGroupId,
        hostGroupName,
        port,
        sizeInMB,
        stripeSize,
        luName,
    ):

        funcName = "hv_infra:createPresentedVolume"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("pool={}", pool)
        self.logger.writeParam("resourceGroupId={}", resourceGroupId)

        urlPath = "LogicalUnit/LogicalUnit/CreatePresentedVolume"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "lun": lun or -1,
            "resourceGroupId": resourceGroupId,
            "hostGroupName": hostGroupName or "",
            "port": port or "",
            "pool": pool,
            "sizeInMB": sizeInMB,
            "stripeSize": stripeSize or 0,
            "luName": luName or "",
        }

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def expandLun(self, lun, sizeInGB):

        funcName = "hv_infra:expandLun"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("sizeInGB={}", sizeInGB)
        self.logger.writeParam("dryRun={}", self.dryRun)
        if self.dryRun:
            return

        urlPath = "LogicalUnit/LogicalUnit/Expand"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "lun": lun,
            "expandSizeInGB": sizeInGB,
        }

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            if "HIJSONFAULT" in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)

    def expandLunInBytes(self, lun, sizeInBytes):

        funcName = "hv_infra:expandLun"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("sizeInBytes={}", sizeInBytes)
        self.logger.writeParam("dryRun={}", self.dryRun)
        if self.dryRun:
            return

        urlPath = "LogicalUnit/LogicalUnit/ExpandInBytes"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "lun": lun,
            "expandSize": sizeInBytes,
        }

        response = RequestsUtils.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            if "HIJSONFAULT" in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)

    def deleteLun(self, lunResourceId):
        funcName = "hv_infra:deleteLun"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lunResourceId={}", lunResourceId)
        (storageResourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = "v2/storage/devices/{0}/volumes/{1}".format(
            storageResourceId, lunResourceId
        )
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        self.logger.writeParam("url={}", url)
        response = requests.delete(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        self.logger.writeDebug(response.status_code)
        if response.ok:
            resourceId = response.json()["data"]["resourceId"]
            self.logger.writeDebug("resourceId={}", resourceId)
            taskId = response.json()["data"].get("taskId")
            self.checkTaskStatus(taskId)
            time.sleep(10)
            return True
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            if "HIJSONFAULT" in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)

    def getLun(self, lun, doRetry=True):

        funcName = "hv_infra:getLun"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        luns = self.getAllLuns()
        foundlun = None
        for item in luns:
            try:
                if str(item["ldevId"]) == str(lun):
                    foundlun = item
                    self.logger.writeDebug(foundlun)
                    break
            except Exception as e:
                self.logger.writeException(e)

        self.logger.writeExitSDK(funcName)
        return foundlun

    def getLunByResourceId(self, lunResourceId, doRetry=True):

        funcName = "hv_infra:getLunByResourceId"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lunResourceId={}", lunResourceId)
        (storageResourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = "v2/storage/devices/{0}/volumes/{1}".format(
            storageResourceId, lunResourceId
        )
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        self.logger.writeParam("url={}", url)
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        self.logger.writeDebug(response.status_code)
        if response.ok:
            return response.json()["data"]
        elif "HIJSONFAULT" in response.headers:
            if doRetry:
                self.logger.writeDebug(funcName + ":{}", "retry once")
                return self.getLunByResourceId(lunResourceId, False)
            else:
                Utils.raiseException(self.sessionId, response, False)
        else:
            self.throwException(response)

    def getLunByResourceId1(self, lunResourceId, doRetry=True):

        funcName = "hv_infra:getLunByResourceId1"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lunResourceId={}", lunResourceId)

        luns = self.getAllLuns()
        foundlun = None
        for item in luns:
            try:
                if str(item["resourceId"]) == str(lunResourceId):
                    foundlun = item
                    break
            except Exception as e:
                self.logger.writeException(e)

        self.logger.writeExitSDK(funcName)
        return foundlun

    def throwException(self, response):
        raise Exception(
            "{0}:{1}".format(response.status_code, response.json().get("error"))
        )

    def getLunByNaa(self, canonicalName):

        funcName = "hv_infra:getLunByNaa"
        self.logger.writeEnterSDK(funcName)

        canonicalName = str(canonicalName).upper()
        manufacturerCode = "60060"
        if (
            len(canonicalName) == 36
            and canonicalName.find("NAA") == 0
            and canonicalName.find(manufacturerCode) > 0
        ):
            lunCode = canonicalName[28:36]
            self.logger.writeDebug("lunCode={0}".format(lunCode))
            modelCode = canonicalName[20:23]
            self.logger.writeInfo("modelCode={0}".format(modelCode))
            serialSubCode = canonicalName[24:28]
            serialCode = serialSubCode

            self.logger.writeDebug("serialCode={0}".format(serialCode))
            storageSerial = int(serialCode, 16)
            if modelCode == "502":
                storageSerial = "2{0}".format(storageSerial)
            elif modelCode == "504":
                storageSerial = "4{0}".format(storageSerial)

            self.serial = int(storageSerial)
            self.logger.writeDebug("storageSerial={0}".format(self.serial))

            lun = int(lunCode, 16)
            self.logger.writeDebug("lun={0}".format(lun))
            self.logger.writeExitSDK(funcName)
            return self.getLun(lun)

    def getLunByCountByNaa(self, lunCanonicalName, maxCount):

        funcName = "hv_infra:getLunByCountByNaa"
        self.logger.writeEnterSDK(funcName)

        urlPath = "LogicalUnit/LogicalUnit/GetListByCountByCanonicalName"
        url = self.getUrl(urlPath)
        params = {
            "sessionId": self.sessionId,
            "canonicalName": lunCanonicalName,
            "maxCount": maxCount,
        }

        self.logger.writeParam("url={}", url)
        self.logger.writeParam("params={}", params)

        response = requests.get(
            url, params=params, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getLunsByCount(self, startLDev, maxCount):

        funcName = "hv_infra:getLunsByCount"
        self.logger.writeEnterSDK(funcName)

        urlPath = "LogicalUnit/LogicalUnit/GetListByCount"
        url = self.getUrl(urlPath)
        params = {
            "sessionId": self.sessionId,
            "serial": self.serial,
            "startLDev": startLDev,
            "maxCount": maxCount,
        }

        self.logger.writeParam("url={}", url)
        self.logger.writeParam("params={}", params)

        response = requests.get(
            url, params=params, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getLunsByRange(self, beginLDev, endLDev):

        funcName = "hv_infra:getLunsByRange"
        self.logger.writeEnterSDK(funcName)

        urlPath = "LogicalUnit/LogicalUnit/GetListByRange"
        url = self.getUrl(urlPath)
        params = {
            "sessionId": self.sessionId,
            "serial": self.serial,
            "beginLDev": beginLDev,
            "endLDev": endLDev,
        }

        self.logger.writeParam("url={}", url)
        self.logger.writeParam("params={}", params)

        response = requests.get(
            url, params=params, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getAllLuns(self):

        funcName = "hv_infra:getAllLuns"
        self.logger.writeEnterSDK(funcName)
        (resourceId, ucp) = self.getStorageSystemResourceId()
        self.logger.writeDebug("Storage_resource_id={0}".format(resourceId))
        # urlPath = 'v2/storage/devices/{0}/volumes?refresh=false'.format(resourceId)
        urlPath = "v2/storage/devices/{0}/volumes?fromLdevId=1000&toLdevId=1100&refresh=false".format(
            resourceId
        )
        url = self.getUrl(urlPath)
        self.logger.writeParam("url={}", url)
        headers = self.getAuthToken()
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        # self.logger.writeDebug('response.json()={}', response.json())

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()["data"]
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def presentLun(
        self,
        luns,
        hgName,
        port,
    ):

        funcName = "hv_infra:presentLun"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", luns)
        self.logger.writeParam("hgName={}", hgName)
        self.logger.writeParam("port={}", port)
        self.logger.writeParam("dryRun={}", self.dryRun)
        if self.dryRun:
            return
        (resourceId, ucp) = self.getStorageSystemResourceId()
        hostgroups = self.getAllHostGroups()

        # hostgroup = next(x for x in hostgrpups if x.hostGroupName == hgName and x.port == port)

        hostgroup = None
        for x in hostgroups:
            if x.get("hostGroupName") == hgName and x.get("port") == port:
                hostgroup = x
                break

        hgResourceId = hostgroup.get("resourceId")
        urlPath = "/v2/storage/devices/{0}/hostGroups/{1}/volumes".format(
            resourceId, hgResourceId
        )
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        body = {"ldevIds": list(map(int, luns))}

        response = requests.post(
            url, headers=headers, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)

        if not response.ok:
            if "HIJSONFAULT" in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)
        else:
            taskId = response.json()["data"].get("taskId")
            self.checkTaskStatus(taskId)

    def checkTaskStatus(self, taskId):
        funcName = "hv_infra:checkTaskStatus"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("taskId={}", taskId)
        (status, name) = self.getTaskStatus(taskId)
        count = 0
        while status == "Running":
            if count % 5 == 0:
                self.logger.writeInfo(
                    "{0} task with id {1} status is Running".format(name, taskId)
                )
            time.sleep(5)
            count += 1
            (status, name) = self.getTaskStatus(taskId)

        if status.lower() == "failed":
            description = self.getTaskStatusDescription(taskId)
            self.logger.writeError(
                "{0} task with id {1} is failed.".format(name, taskId)
            )
            raise Exception("Operation failed. {0}".format(description))

        self.logger.writeExitSDK(funcName)
        return status

    def getLunIdFromTaskStatusEvents(self, taskId):
        funcName = "hv_infra:getLunIdFromTaskStatusEvents"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("taskId={}", taskId)
        headers = self.getAuthToken()
        urlPath = "/v2/tasks/{0}".format(taskId)
        url = self.getUrl(urlPath)
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        status = None
        lun = None
        if response.ok:
            status = response.json()["data"].get("status")
            response.json()["data"].get("name")

        if status.lower() == "success":
            events = response.json()["data"].get("events")
            description = events[1].get("description")
            self.logger.writeDebug(description)
            # start = description.find("Created logical Unit") + len("Created logical Unit")
            # end = description. find("in")
            # lun = description[start:end]
            # parsedLun = 'parsedLun={0}'.format(lun)
            start = description.find("Successfully created Volume [") + len(
                "Successfully created volume ["
            )
            end = description.find("] for")
            lun = description[start:end]
            parsedLun = "parsedLun={0}".format(lun)
            self.logger.writeDebug(parsedLun)
        self.logger.writeExitSDK(funcName)
        return lun.strip()

    def getTaskStatus(self, taskId):
        funcName = "hv_infra: getTaskStatus"
        self.logger.writeEnterSDK(funcName)
        headers = self.getAuthToken()
        urlPath = "/v2/tasks/{0}".format(taskId)
        url = self.getUrl(urlPath)
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        status = None
        name = None
        if response.ok:
            status = response.json()["data"].get("status")
            name = response.json()["data"].get("name")

        self.logger.writeExitSDK(funcName)
        return (status, name)

    def getTaskStatusDescription(self, taskId):
        funcName = "hv_infra: getTaskStatusDescription"
        self.logger.writeEnterSDK(funcName)
        headers = self.getAuthToken()
        urlPath = "/v2/tasks/{0}".format(taskId)
        url = self.getUrl(urlPath)
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        description = None
        if response.ok:
            self.logger.writeDebug("getFailedTaskResponse={}", response.json())
            response.json()["data"].get("status")
            name = response.json()["data"].get("name")
            events = response.json()["data"].get("events")
            if len(events):
                descriptions = [element.get("description") for element in events]
                self.logger.writeDebug("-".join(descriptions))
                description = events[-1].get("description")
                self.logger.writeDebug(description)
                return "-".join(descriptions)
            else:
                return "{} failed".format(name)

    def getCommandDeviceEvents(self, taskId):
        funcName = "hv_infra: getCommandDeviceEvents"
        self.logger.writeEnterSDK(funcName)
        headers = self.getAuthToken()
        urlPath = "/v2/tasks/{0}".format(taskId)
        url = self.getUrl(urlPath)
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        if response.ok:
            self.logger.writeDebug("getFailedTaskResponse={}", response.json())
            response.json()["data"].get("status")
            name = response.json()["data"].get("name")
            events = response.json()["data"].get("events")
            if len(events):
                descriptions = [element.get("description") for element in events]
                # self.logger.writeDebug('-'.join(descriptions))
                # description = events[-1].get('description')
                # self.logger.writeDebug(description)
                return descriptions
            else:
                return "{} failed".format(name)

    def unpresentLun(
        self,
        luns,
        hgName,
        port,
    ):

        funcName = "hv_infra:UnpresentLun"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", luns)
        self.logger.writeParam("hgName={}", hgName)
        self.logger.writeParam("port={}", port)
        self.logger.writeParam("dryRun={}", self.dryRun)
        if self.dryRun:
            return
        (resourceId, ucp) = self.getStorageSystemResourceId()
        hostgroups = self.getAllHostGroups()

        # hostgroup = next(x for x in hostgrpups if x.hostGroupName == hgName and x.port == port)

        hostgroup = None
        for x in hostgroups:
            if x.get("hostGroupName") == hgName and x.get("port") == port:
                hostgroup = x
                break

        hgResourceId = hostgroup.get("resourceId")
        urlPath = "/v2/storage/devices/{0}/hostGroups/{1}/volumes".format(
            resourceId, hgResourceId
        )
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        body = {"ldevIds": list(map(int, luns))}

        response = requests.delete(
            url, headers=headers, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            if "HIJSONFAULT" in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)
        else:
            taskId = response.json()["data"].get("taskId")
            self.checkTaskStatus(taskId)

    def createHostGroup(self, hgName, port, wwnList, hostmode, hostModeOptions):

        funcName = "hv_infra:createHostGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("wwnList={}", wwnList)
        self.logger.writeParam("hgName={}", hgName)
        self.logger.writeParam("port={}", port)
        self.logger.writeParam("dryRun={}", self.dryRun)
        if self.dryRun:
            return

        (resourceId, ucp) = self.getStorageSystemResourceId()
        self.logger.writeParam("resourceId={}", resourceId)
        self.logger.writeParam("ucp={}", ucp)
        wwns = []
        for x in list(wwnList):
            wwns.append({"id": x})
        body = {
            "hostGroupName": str(hgName),
            "port": str(port),
            "ucpSystem": ucp,
            "hostMode": hostmode,
            "hostModeOptions": list(hostModeOptions),
        }

        if len(wwns) > 0:
            body["wwns"] = wwns

        self.logger.writeParam("body={}", body)
        urlPath = "v2/storage/devices/{0}/hostGroups".format(resourceId)
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.post(
            url, headers=headers, json=body, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug(url)
        self.logger.writeDebug(body)
        if not response.ok:
            if "HIJSONFAULT" in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)
        else:
            taskId = response.json()["data"].get("taskId")
            self.checkTaskStatus(taskId)

        self.logger.writeExitSDK(funcName)

    def deleteHostGroup(self, hgName, port):

        funcName = "hv_infra:deleteHostGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("hgName={}", hgName)
        self.logger.writeParam("port={}", port)
        self.logger.writeParam("dryRun={}", self.dryRun)
        if self.dryRun:
            return
        (resourceId, ucp) = self.getStorageSystemResourceId()
        hostgroups = self.getAllHostGroups()
        hostgroup = None
        for x in hostgroups:
            if x.get("hostGroupName") == hgName and x.get("port") == port:
                hostgroup = x
                break
        hgResourceId = hostgroup.get("resourceId")
        urlPath = "v2/storage/devices/{0}/hostGroups/{1}".format(
            resourceId, hgResourceId
        )
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.delete(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        if not response.ok:
            if "HIJSONFAULT" in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)
        else:
            self.logger.writeDebug(response)
            # taskId = response.json()['data'].get('taskId')
            # self.checkTaskStatus(taskId)
            self.logger.writeExitSDK(funcName)

    def getHostGroup(
        self,
        hgName,
        port,
        doRetry=True,
    ):

        funcName = "hv_infra:getHostGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("hgName={}", hgName)
        self.logger.writeParam("port={}", port)
        (resourceId, ucp) = self.getStorageSystemResourceId()
        hostgroups = self.getAllHostGroups()

        hostgroup = None
        for x in hostgroups:
            if x.get("hostGroupName") == hgName and x.get("port") == port:
                hostgroup = x
                break
        return hostgroup

    def getVSM(self):

        funcName = "hv_infra:getVSM"
        self.logger.writeEnterSDK(funcName)

        urlPath = "StorageManager/StorageManager/GetVirtualStorageSystems"
        url = self.getUrl(urlPath)
        body = {"sessionId": self.sessionId}

        response = requests.get(
            url, params=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getAllHostGroups(self):

        funcName = "hv_infra:getAllHostGroups"
        self.logger.writeEnterSDK(funcName)

        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = "v2/storage/devices/{0}/hostGroups?refresh=false".format(resourceId)
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeExitSDK(funcName)
        if response.ok:
            # self.logger.writeDebug('response.json()={}',
            #                        response.json())
            return response.json()["data"]
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    # def getAllHostgroups(self):
    #     funcName = 'hv_infra:getAllHostgroups'
    #     self.logger.writeEnterSDK(funcName)
    #     resourceId = self.getStorageSystemResourceId()
    #     urlPath = 'v2/storage/devices/{0}/hostGroups'.format(resourceId)
    #     url = self.getUrl(urlPath)
    #     headers = self.getAuthToken()
    #     response = requests.get(url, headers=headers,
    #                             verify=self.shouldVerifySslCertification)

    #     self.logger.writeExitSDK(funcName)
    #     if response.ok:
    #         self.logger.writeDebug('response.json()={}',
    #                                response.json())
    #         return response.json()['data']
    #     elif 'HIJSONFAULT' in response.headers:
    #         Utils.raiseException(self.sessionId, response)
    #     else:
    #         raise Exception(
    #            self.throwException(response)

    def getHostGroupsForLU(self, lun):

        funcName = "hv_infra:getHostGroupsForLU"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)

        urlPath = "HostGroup/HostGroup/GetHostGroupsForLU"
        url = self.getUrl(urlPath)
        body = {"sessionId": self.sessionId, "serialNumber": self.serial, "lu": lun}

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def setHostMode(
        self,
        hgName,
        port,
        hostmode,
        hostopt,
    ):

        funcName = "hv_infra:setHostMode"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("hgName={}", hgName)
        self.logger.writeParam("port={}", port)
        self.logger.writeParam("hostmode={}", hostmode)
        self.logger.writeParam("hostopt={}", hostopt)
        self.logger.writeParam("dryRun={}", self.dryRun)
        if self.dryRun:
            return

        # urlPath = 'HostGroup/HostGroup/SetHostMode'
        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam("storageresourceId={}", resourceId)
        hostgroup = self.getHostGroup(hgName, port)
        hgResourceId = hostgroup.get("resourceId")
        self.logger.writeParam("hgResourceId={}", hgResourceId)
        self.logger.writeParam("ucp={}", ucp)
        urlPath = "v2/storage/devices/{0}/hostgroups/{1}".format(
            resourceId, hgResourceId
        )
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        body = {
            "hostMode": hostmode,
            "hostModeOptions": list(map(int, hostopt)),
        }

        self.logger.writeDebug(url)
        self.logger.writeDebug(body)
        response = requests.patch(
            url, json=body, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug("response={}", response)

        if not response.ok:
            if "HIJSONFAULT" in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)
        else:
            taskId = response.json()["data"].get("taskId")
            self.checkTaskStatus(taskId)
            time.sleep(5)

        self.logger.writeExitSDK(funcName)

    def addWWN(
        self,
        hgName,
        port,
        wwnList,
    ):

        funcName = "hv_infra:addWWN"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("hgName={}", hgName)
        self.logger.writeParam("port={}", port)
        self.logger.writeParam("wwnList={}", wwnList)
        self.logger.writeParam("dryRun={}", self.dryRun)
        if self.dryRun:
            return

        (resourceId, ucp) = self.getStorageSystemResourceId()
        self.logger.writeParam("storageresourceId={}", resourceId)
        hostgroup = self.getHostGroup(hgName, port)
        hgResourceId = hostgroup.get("resourceId")
        self.logger.writeParam("hgResourceIdresourceId={}", hgResourceId)
        self.logger.writeParam("ucp={}", ucp)
        wwns = []
        for x in list(wwnList):
            wwns.append({"id": x})
        body = {
            "wwns": wwns,
        }
        self.logger.writeParam("body={}", body)
        urlPath = "v2/storage/devices/{0}/hostGroups/{1}/wwns".format(
            resourceId, hgResourceId
        )
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.post(
            url, headers=headers, json=body, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug(url)
        self.logger.writeDebug(body)
        if not response.ok:
            if "HIJSONFAULT" in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)
        else:
            taskId = response.json()["data"].get("taskId")
            self.checkTaskStatus(taskId)
        self.logger.writeExitSDK(funcName)

    def removeWWN(
        self,
        hgName,
        port,
        wwnList,
    ):
        funcName = "hv_infra:removeWWN"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("hgName={}", hgName)
        self.logger.writeParam("port={}", port)
        self.logger.writeParam("wwnList={}", wwnList)
        self.logger.writeParam("dryRun={}", self.dryRun)
        if self.dryRun:
            return

        (resourceId, ucp) = self.getStorageSystemResourceId()
        self.logger.writeParam("storageresourceId={}", resourceId)
        hostgroup = self.getHostGroup(hgName, port)
        hgResourceId = hostgroup.get("resourceId")
        self.logger.writeParam("hgResourceIdresourceId={}", hgResourceId)
        self.logger.writeParam("ucp={}", ucp)
        wwns = []
        for x in list(wwnList):
            wwns.append({"id": x})

        body = {
            "wwns": wwns,
        }
        self.logger.writeParam("body={}", body)
        urlPath = "v2/storage/devices/{0}/hostGroups/{1}/wwns".format(
            resourceId, hgResourceId
        )
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.delete(
            url, headers=headers, json=body, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug(url)
        self.logger.writeDebug(body)
        if not response.ok:
            if "HIJSONFAULT" in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)
        else:
            self.logger.writeDebug("response.json()={}", response.json())
            # taskId = response.json()['data'].get('taskId')
            # self.checkTaskStatus(taskId)
            time.sleep(5)

        self.logger.writeExitSDK(funcName)

    def getPorts(self):
        funcName = "hv_infra:getPorts"
        self.logger.writeEnterSDK(funcName)
        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = "v2/storage/devices/{0}/ports?refresh={1}".format(resourceId, True)
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeExitSDK(funcName)
        if response.ok:
            self.logger.writeDebug("ports={}", response.json())
            return response.json()["data"]
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getStoragePools(self):

        funcName = "hv_infra:getStoragePools"
        self.logger.writeEnterSDK(funcName)
        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = "v2/storage/devices/{0}/pools".format(resourceId)
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeExitSDK(funcName)
        if response.ok:
            self.logger.writeDebug("pools={}", response.json())
            return response.json()["data"]

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getJournalPools(self):
        funcName = "hv_infra:getJournalPools"
        self.logger.writeEnterSDK(funcName)

        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = "v2/storage/devices/{0}/journalpool?ucpSystem={1}".format(
            resourceId, "UCP-CI-12035"
        )
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            self.logger.writeDebug("getJournalPools={}", response.json())
            return response.json()["data"]
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getFreeLUList(self):

        funcName = "hv_infra:getFreeLUList"
        self.logger.writeEnterSDK(funcName)

        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = "v2/storage/devices/{0}/freeVolumes?count={1}&ucpSystem={2}".format(
            resourceId, 100, ucp
        )
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeExitSDK(funcName)
        if response.ok:
            self.logger.writeDebug("pools={}", response.json())
            return response.json()["data"]
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getFreeGADConsistencyGroupId(self):

        funcName = "hv_infra:getFreeGADConsistencyGroupId"
        self.logger.writeEnterSDK(funcName)

        urlPath = "TrueCopy/GetFreeGADConsistencyGroupId"
        url = self.getUrl(urlPath)

        body = {"sessionId": self.sessionId, "serial": self.serial}

        response = requests.get(
            url, params=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getFreeHTIConsistencyGroupId(self):

        funcName = "hv_infra:getFreeHTIConsistencyGroupId"
        self.logger.writeEnterSDK(funcName)

        urlPath = "TrueCopy/GetFreeLocalConsistencyGroupId"
        url = self.getUrl(urlPath)

        body = {"sessionId": self.sessionId, "serial": self.serial}

        response = requests.get(
            url, params=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getFreeTCConsistencyGroupId(self):

        funcName = "hv_infra:getFreeTCConsistencyGroupId"
        self.logger.writeEnterSDK(funcName)

        urlPath = "TrueCopy/GetFreeRemoteConsistencyGroup"
        url = self.getUrl(urlPath)

        body = {"sessionId": self.sessionId, "serial": self.serial}

        response = requests.get(
            url, params=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getFreeURConsistencyGroupId(self):

        funcName = "hv_infra:getFreeURConsistencyGroupId"
        self.logger.writeEnterSDK(funcName)

        urlPath = "TrueCopy/GetFreeUniversalReplicatorConsistencyGroup"
        url = self.getUrl(urlPath)

        body = {"sessionId": self.sessionId, "serial": self.serial}

        response = requests.get(
            url, params=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getQuorumDisks(self):

        funcName = "hv_infra:getQuorumDisks"
        self.logger.writeEnterSDK(funcName)
        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = "v2/storage/devices/{0}/quorum/disks".format(resourceId)
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeExitSDK(funcName)
        if response.ok:
            self.logger.writeDebug("pools={}", response.json())
            return response.json()["data"]
        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getResourceGroups(self):

        funcName = "hv_infra:getResourceGroups"
        self.logger.writeEnterSDK(funcName)

        urlPath = "ResourceGroup/GetList"
        url = self.getUrl(urlPath)

        body = {"sessionId": self.sessionId, "serial": self.serial}

        response = requests.get(
            url, params=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getDynamicPools(self):

        funcName = "hv_infra:getDynamicPools"
        self.logger.writeEnterSDK(funcName)

        urlPath = "StoragePool/GetStoragePools"
        url = self.getUrl(urlPath)

        body = {"sessionId": self.sessionId, "serialNumber": self.serial}

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def createDynamicPool(
        self,
        name,
        luns,
        poolType,
    ):

        funcName = "hv_infra:createDynamicPool"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("name={}", name)
        self.logger.writeParam("luns={}", luns)
        self.logger.writeParam("poolType={}", poolType)

        urlPath = "StoragePool/CreateDynamicPool"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "poolName": name,
            "luList": ",".join(map(str, luns)),
            "poolType": PoolCreateType.fromString(poolType),
        }

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def expandDynamicPool(self, poolId, luns):

        funcName = "hv_infra:expandDynamicPool"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("luns={}", luns)
        self.logger.writeParam("poolId={}", poolId)

        urlPath = "StoragePool/ExpandDynamicPool"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "poolId": poolId,
            "ldevList": ",".join(map(str, luns)),
        }

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def shrinkDynamicPool(self, poolId, luns):

        funcName = "hv_infra:shrinkDynamicPool"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("luns={}", luns)
        self.logger.writeParam("poolId={}", poolId)

        urlPath = "StoragePool/ShrinkDynamicPoolUsingPoolID"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "poolId": poolId,
            "ldevList": ",".join(map(str, luns)),
        }

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def doPost(
        self,
        urlPath,
        body,
        returnJson=False,
    ):

        funcName = "hv_infra:doPost"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("urlPath={}", urlPath)
        self.logger.writeParam("body={}", body)
        url = self.getUrl(urlPath)
        self.logger.writeParam("url={}", url)
        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug("response={}", response)

        if response.ok:
            self.logger.writeExitSDK(funcName)
            if returnJson:
                self.logger.writeDebug("response.json()={}", response.json())
                return response.json()
            else:
                return
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def deleteDynamicPool(self, poolId):

        funcName = "hv_infra:deleteDynamicPool"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("poolId={}", poolId)

        urlPath = "StoragePool/DeleteDynamicPool"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "poolId": poolId,
        }

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return
        elif "HIJSONFAULT" in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def setDynamicPoolCapacityThreshold(
        self,
        poolId,
        warningRate,
        depletionRate,
        enableNotification,
    ):

        urlPath = "StoragePool/SetDynamicPoolCapacityThreshold"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "poolId": poolId,
            "warningRate": warningRate,
            "depletionRate": depletionRate,
            "enableNotification": enableNotification,
        }

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        if response.ok:
            return
        elif "HIJSONFAULT" in response.headers:
            raise Exception(json.loads(response.headers["HIJSONFAULT"]))
        else:
            self.throwException(response)


class HostMode:

    modes = [  # 0
        # 1
        # 2
        # 3
        # 4
        # 5
        # 6
        # 7
        # 8
        # 9
        # 10
        # 11
        # 12
        # 13
        # 14
        # 15
        # 16
        # 17
        "UNKNOWN",
        "NOT_SPECIFIED",
        "RESERVED",
        "LINUX",
        "VMWARE",
        "HP",
        "OPEN_VMS",
        "TRU64",
        "SOLARIS",
        "NETWARE",
        "WINDOWS",
        "HI_UX",
        "AIX",
        "VMWARE_EXTENSION",
        "WINDOWS_EXTENSION",
        "UVM",
        "HP_XP",
        "DYNIX",
    ]

    @staticmethod
    def getHostModeNum(hm):
        hostmode = hm.upper()

        if hostmode == "STANDARD":
            hostmode = "LINUX"
        hostmode = re.sub(r"WIN($|_)", r"WINDOWS\1", hostmode)
        hostmode = re.sub(r"EXT?$", "EXTENSION", hostmode)

        if hostmode not in HostMode.modes:
            raise Exception("Invalid host mode: '{0}'".format(hm))

        return HostMode.modes.index(hostmode)

    @staticmethod
    def getHostModeName(hostmode):
        if isinstance(hostmode, str):
            return hostmode
        return HostMode.modes[hostmode]


class DedupMode:

    modes = ["DISABLED", "COMPRESSION", "COMPRESSION_DEDUPLICATION"]


class RequestsUtils:

    @staticmethod
    def get(url, params, verify):
        try:
            return requests.get(url, params=params, verify=verify)
        except requests.exceptions.Timeout:
            raise Exception(
                " Timeout exception. Perhaps webserivce is not reachable or down ? "
            )
        except requests.exceptions.TooManyRedirects:
            raise Exception(
                "Mas retry error. Perhaps webserivce is not reachable or down ?"
            )
        except requests.exceptions.RequestException:
            raise Exception(
                " Connection Error. Perhaps web serivce is not reachable is down ? "
            )

    @staticmethod
    def post(url, json, verify):
        try:
            return requests.post(url, json=json, verify=verify)
        except requests.exceptions.Timeout:
            raise Exception(
                " Timeout exc Hi Adaeption. Perhaps webserivce is not reachable or down ? "
            )
        except requests.exceptions.TooManyRedirects:
            raise Exception(
                "Mas retry error. Perhaps webserivce is not reachable or down ?"
            )
        except requests.exceptions.RequestException:
            raise Exception(
                " Connection Error. Perhaps web serivce is not reachable is down ? "
            )
