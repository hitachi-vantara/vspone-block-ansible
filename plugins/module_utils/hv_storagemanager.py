import time
import hashlib

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_ucpmanager import (
    UcpManager,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_http_client import (
    HTTPClient as requests,
)


class StorageManager:

    def __init__(
        self,
        management_address,
        management_username,
        management_password,
        api_token,
        storage_serial,
        ucp_serial,
        partnerId=None,
        subscriberId=None,
        webServicePort=None,
        sessionId=None,
    ):
        funcName = "hv_storagemanager:init"
        self.logger = Log()
        self.logger.writeEnterSDK(funcName)
        self.dryRun = False

        self.sessionId = sessionId
        self.webServicePort = webServicePort
        self.shouldVerifySslCertification = False
        self.management_address = management_address
        self.management_username = management_username
        self.management_password = management_password
        self.api_token = api_token
        self.storage_serial = storage_serial
        self.ucp_serial = ucp_serial
        self.partnerId = partnerId
        self.subscriberId = subscriberId
        self.basedUrl = "https://{0}".format(management_address)

        # if management_username is None or \
        #    management_password is None or \
        #    management_address is None or \
        #    management_username == '' or \
        #    management_password == '' or \
        #    management_address == '' :
        #     raise Exception( "Management System is not configured.")
        if management_address is None or management_address == "":
            raise Exception(
                "Management System is not configured. management address can not be empty."
            )

        if storage_serial is None or storage_serial == "":
            raise Exception("Storage system is not configured.")

        if self.ucp_serial == "":
            raise Exception("UCP name is invalid.")

        if ucp_serial is None:
            raise Exception("UCP name is not valid.")

        try:
            self.ucpManager = UcpManager(
                self.management_address,
                self.management_username,
                self.management_password,
                self.api_token,
            )
        except Exception:
            raise Exception("Management System is not configured.")

    def throwException(self, response):
        self.logger.writeInfo("throwException, response={}", response)
        raise Exception(
            "{0}:{1}".format(response.status_code, response.json().get("error"))
        )

    #  helper func
    def isStorageSystemInUcpSystem(self):
        funcName = "hv_storagemanager:isStorageSystemInUcpSystem"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeDebug("storage_serial={}", self.storage_serial)
        self.logger.writeDebug("ucp_serial={}", self.ucp_serial)

        theUCP = self.ucpManager.getUcpSystem(self.ucp_serial)
        self.logger.writeDebug("theUCP={}", theUCP)

        if theUCP is None:
            raise Exception("The System is not found.")

        for x in theUCP.get("storageDevices"):
            ss = x.get("serialNumber")
            self.logger.writeDebug("ss={}", ss)
            ss = str(ss)
            self.logger.writeDebug("ss={}", ss)

            # Removed the restriction of having the storage system in the UCP system
            return True
            # if ss == str(self.storage_serial):
            #     return True

        self.logger.writeExitSDK(funcName)
        return False

    # returns ss and ucp grid if ss is found
    # else throws exception
    def getStorageSystemResourceId(self):
        """
        docstring
        """

        funcName = "hv_storagesystem:getStorageSystemResourceId"
        self.logger.writeEnterSDK(funcName)
        headers = self.ucpManager.getAuthToken()
        # self.logger.writeParam("headers={}", headers)

        urlPath = "v2/storage/devices"
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeParam("url={}", url)

        systems = self.getAllStorageSystems()

        self.logger.writeDebug("systems={}", systems)

        system = None
        for x in systems:
            self.logger.writeDebug(int(x["serialNumber"]))
            self.logger.writeDebug(self.storage_serial)
            self.logger.writeDebug(int(x["serialNumber"]) == self.storage_serial)

            if str(x["serialNumber"]) == str(self.storage_serial):
                system = x
                break
        if system is None:
            raise Exception(
                "Invalid serial = {0}, please check once and try again.".format(
                    self.storage_serial
                )
            )

        ucp = system.get("ucpSystems")[0]
        self.logger.writeExitSDK(funcName)
        return (str(system.get("resourceId")), str(ucp))

    def getStorageSystemResourceIdInISP(self):
        """
        docstring
        """

        funcName = "hv_storagesystem:getStorageSystemResourceIdInISP"
        self.logger.writeEnterSDK(funcName)
        self.ucpManager.getAuthToken()
        # self.logger.writeParam('headers={}', headers)

        urlPath = "v2/storage/devices"
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeParam("url={}", url)

        systems = self.getAllISPStorageSystems()

        self.logger.writeDebug("systems={}", systems)
        self.logger.writeDebug("20230606 self.storage_serial={}", self.storage_serial)

        system = None
        for x in systems:
            self.logger.writeDebug(int(x["serialNumber"]))
            self.logger.writeDebug(self.storage_serial)
            self.logger.writeDebug(int(x["serialNumber"]) == self.storage_serial)
            if str(x["serialNumber"]) == str(self.storage_serial):
                system = x
                break
        if system is None:
            raise Exception(
                "Invalid serial = {0}, please check once and try again.".format(
                    self.storage_serial
                )
            )

        self.logger.writeExitSDK(funcName)
        return str(system.get("resourceId"))

    def getAllISPStorageSystems(self):
        funcName = "hv_storagemanager:getAllISPStorageSystems"
        self.logger.writeEnterSDK(funcName)

        urlPath = "v2/systems/default"
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()

        self.logger.writeDebug("url={}", url)
        # self.logger.writeDebug('headers={}', headers)
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug("response={}", response)

        storage_systems = []
        if response.ok:
            authResponse = response.json()
            # self.logger.writeDebug('ISP response Json={}', authResponse)
            data = authResponse.get("data")
            storage_systems.extend(data.get("storageDevices"))
        else:
            raise Exception(response)

        return storage_systems

    def getAllLuns(self):

        funcName = "hv_storagemanager:getAllLuns"
        self.logger.writeEnterSDK(funcName)
        resourceId = self.getStorageSystemResourceIdInISP()
        # (resourceId, ucp) = self.getStorageSystemResourceId()
        self.logger.writeDebug("Storage_resource_id={0}".format(resourceId))
        # urlPath = 'v2/storage/devices/{0}/volumes?refresh=false'.format(resourceId)
        urlPath = "v2/storage/devices/{0}/volumes?fromLdevId=0&toLdevId=64000&refresh=false".format(
            resourceId
        )
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeParam("20230620 urlPath={}", url)
        headers = self.ucpManager.getAuthToken()
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        #  too much to dump
        # self.logger.writeDebug('response.json()={}', response.json())
        self.logger.writeDebug("20230620 response.ok={}", response.ok)
        if response.ok:
            respjson = response.json()
            # if respjson.status >= 300 :
            #     self.logger.writeDebug('respjson.status={}', respjson.status)
            #     raise Exception('status={}, error={}', respjson.status, respjson.error)
            self.logger.writeDebug("get data json")
            respjson = response.json()["data"]
            self.logger.writeExitSDK(funcName)
            return respjson
        else:
            raise Exception(response)

    # a2.4 MT refreshVolumesMT
    def refreshVolumesMT(self, resourceId, ldevid):
        funcName = "hv_storagemanager:refreshVolumesMT"
        self.logger.writeEnterSDK(funcName)

        urlPath = "v2/storage/devices/{0}/volumes?fromLdevId={1}&toLdevId={2}&refresh=false".format(
            resourceId, str(0), str(int(ldevid) * 2)
        )
        urlPath = "v3/storage/{0}/volumes/details?fromLdevId={1}&toLdevId={2}&refresh=true".format(
            resourceId, str(0), str(int(ldevid) * 2)
        )
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeParam("urlPath={}", url)

        headers = self.ucpManager.getAuthToken()
        headers["PartnerId"] = self.partnerId
        if self.subscriberId:
            headers["subscriberId"] = self.subscriberId

        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        self.logger.writeDebug("response.ok={}", response.ok)
        if response.ok:
            self.logger.writeDebug("get data json")

        else:
            raise Exception(response)

    # a2.4 MT tagResource
    def tagResource(self, storageResourceId, resourceId, resourceType):
        funcName = "hv_storagemanager:tagResource"
        self.logger.writeEnterSDK(funcName)

        if self.subscriberId is None:
            #  NOP
            self.logger.writeDebug("295 subscriberId is required to tagResource")
            return

        urlPath = "v3/storage/{0}/resource".format(storageResourceId)
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeParam("urlPath={}", url)

        headers = self.ucpManager.getAuthToken()
        body = {
            "resourceId": resourceId,
            "partnerId": self.partnerId,
            "type": resourceType,
        }
        if self.subscriberId:
            body["subscriberId"] = self.subscriberId
        self.logger.writeParam("310 body={}", body)

        response = requests.post(
            url, headers=headers, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeDebug("response.ok={}", response.ok)
        if response.ok:
            taskId = response.json()["data"].get("taskId")
            self.ucpManager.checkTaskStatus(taskId)
            comment = self.getSoftLimitMessageFromTaskStatusEvents(taskId)
            self.logger.writeExitSDK(funcName)
            return comment
        else:
            raise Exception(response)

    # a2.4 MT tagV2Volume
    def tagV2Volume(self, resourceId, volumeResourceId):
        funcName = "hv_storagemanager:tagV2Volume"
        self.logger.writeEnterSDK(funcName)

        if self.subscriberId is None:
            #  NOP
            self.logger.writeDebug("294 subscriberId is required to tag")
            return

        urlPath = "v3/storage/{0}/resource".format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeParam("urlPath={}", url)

        headers = self.ucpManager.getAuthToken()
        body = {
            "resourceId": volumeResourceId,
            "partnerId": self.partnerId,
            "type": "Volume",
        }
        if self.subscriberId:
            body["subscriberId"] = self.subscriberId
        self.logger.writeParam("276 body={}", body)

        response = requests.post(
            url, headers=headers, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeDebug("response.ok={}", response.ok)
        if response.ok:
            taskId = response.json()["data"].get("taskId")
            self.ucpManager.checkTaskStatus(taskId)
            comment = self.getSoftLimitMessageFromTaskStatusEvents(taskId)
            self.logger.writeExitSDK(funcName)
            return comment
        else:
            raise Exception(response)

    # a2.4 MT tagPort
    def tagPort(self, resourceId, port):
        funcName = "hv_storagemanager:tagPort"
        self.logger.writeEnterSDK(funcName)

        # portId = "CL2-A"
        portId = str(port)

        urlPath = "v3/storage/{0}/resource".format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeParam("urlPath={}", url)

        headers = self.ucpManager.getAuthToken()
        headers["PartnerId"] = self.partnerId
        if self.subscriberId:
            headers["subscriberId"] = self.subscriberId

        body = {"resourceId": portId, "partnerId": self.partnerId, "type": "Port"}
        if self.subscriberId:
            body["subscriberId"] = self.subscriberId

        try:
            response = requests.post(
                url,
                headers=headers,
                json=body,
                verify=self.shouldVerifySslCertification,
            )
            if response.ok:
                self.logger.writeDebug("ok")
                time.sleep(5)
            else:
                self.logger.writeDebug("failed: {}", response)
        except (ValueError, TypeError):
            self.logger.writeDebug("except")

        self.logger.writeExitSDK(funcName)

    #  may not be used anymore
    def getLunByID(self, ldevid):

        funcName = "hv_storagemanager:getLunByID"
        self.logger.writeEnterSDK(funcName)
        resourceId = self.getStorageSystemResourceIdInISP()
        # (resourceId, ucp) = self.getStorageSystemResourceId()
        self.logger.writeDebug("Storage_resource_id={0}".format(resourceId))
        self.logger.writeDebug("str(ldevid)={0}".format(str(ldevid)))
        self.logger.writeDebug("str(ldevid+10)={0}".format(str(int(ldevid) + 10)))
        # urlPath = 'v2/storage/devices/{0}/volumes?refresh=false'.format(resourceId)
        urlPath = "v2/storage/devices/{0}/volumes?fromLdevId={1}&toLdevId={2}&refresh=false".format(
            resourceId, str(0), str(int(ldevid) * 2)
        )
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeParam("378 urlPath={}", url)
        headers = self.ucpManager.getAuthToken()
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        #  too much to dump
        # self.logger.writeDebug('response.json()={}', response.json())
        self.logger.writeDebug("386 response.ok={}", response.ok)
        if response.ok:
            self.logger.writeDebug("get data json")
            items = response.json()["data"]
            if items is None or len(items) == 0:
                items = None
            self.logger.writeExitSDK(funcName)
            return items
        else:
            raise Exception(response)

    def get_one_lun_by_id_v3(self, ldevid):
        funcName = "hv_storagemanager:get_one_lun_by_id_v3"
        self.logger.writeEnterSDK(funcName)
        resourceId = self.getStorageSystemResourceIdInISP()
        urlPath = "v3/storage/{resource_id}/volumes/details?fromLdevId={from_ldev}&toLdevId={to_ldev}&refresh=false".format(
            resource_id=resourceId, from_ldev=ldevid, to_ldev=ldevid
        )

        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeParam("urlPath={}", url)

        headers = self.ucpManager.getAuthToken()
        headers["PartnerId"] = self.partnerId
        if self.subscriberId:
            headers["subscriberId"] = self.subscriberId

        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        self.logger.writeDebug("response.ok={}", response.ok)
        if response.ok:
            self.logger.writeDebug("get data json")
            items = response.json()["data"]
            if items is None or len(items) == 0:
                self.logger.writeExitSDK(funcName)
                return None
            else:
                self.logger.writeExitSDK(funcName)
                return items[0]
        else:
            raise Exception(response)

    def getOneLunByResourceID(self, lun_resourceId):

        funcName = "hv_storagemanager:getOneLunByResourceID"
        self.logger.writeEnterSDK(funcName)
        storage_resourceId = self.getStorageSystemResourceIdInISP()
        # (resourceId, ucp) = self.getStorageSystemResourceId()
        self.logger.writeDebug(f"lun type ??????? {type(lun_resourceId)}")
        try:
            lun_resourceId = int(lun_resourceId)
            lun_resourceId = self.get_storage_volume_md5_hash(lun_resourceId)
        except Exception as ex:
            self.logger.writeDebug(f"exception in getOneLunByResourceID {ex}")

        self.logger.writeDebug("Storage_resource_id={0}".format(storage_resourceId))
        self.logger.writeDebug("330 lun_resourceId={0}".format(lun_resourceId))

        # urlPath = 'v2/storage/devices/{0}/volumes?refresh=false'.format(resourceId)
        urlPath = "v2/storage/devices/{0}/volumes/{1}".format(
            storage_resourceId, lun_resourceId
        )
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeParam("20230620 urlPath={}", url)
        headers = self.ucpManager.getAuthToken()
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        #  only one lun
        self.logger.writeDebug("response.json()={}", response.json())
        self.logger.writeDebug("20230620 response.ok={}", response.ok)
        if response.ok:
            self.logger.writeDebug("get data json")
            item = response.json()["data"]
            self.logger.writeExitSDK(funcName)
            # if items is None or len(items) == 0 :
            #     return None
            return item
        else:
            raise Exception(response)

    # 2.4 MT getOneLunByResourceID v3 partner only, no subs
    # expect it to return entitlement info
    def getOneLunByResourceIDV3(self, lun):

        funcName = "hv_storagemanager:getOneLunByResourceIDV3"
        self.logger.writeEnterSDK(funcName)
        storage_resourceId = self.getStorageSystemResourceIdInISP()
        # (resourceId, ucp) = self.getStorageSystemResourceId()
        self.logger.writeDebug("Storage_resource_id={0}".format(storage_resourceId))
        self.logger.writeDebug("437 lun={0}".format(lun))
        # urlPath = 'v2/storage/devices/{0}/volumes?refresh=false'.format(resourceId)
        urlPath = "v3/storage/{storage_id}/volume?fromLdevId={from_lun}&toLdevId={to_lun}".format(
            storage_id=storage_resourceId, from_lun=lun, to_lun=lun
        )

        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeParam("443 urlPath={}", url)
        headers = self.ucpManager.getAuthToken()
        headers["PartnerId"] = self.partnerId
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        #  only one lun
        self.logger.writeDebug("response.json()={}", response.json())
        self.logger.writeDebug("451 response.ok={}", response.ok)
        if response.ok:
            self.logger.writeDebug("get data json")
            item = response.json()["data"]
            self.logger.writeExitSDK(funcName)
            # if items is None or len(items) == 0 :
            #     return None
            return item
        else:
            raise Exception(response)

    def getLun(self, lun, doRetry=True):

        funcName = "hv_storagemanager:getLun"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)

        self.logger.writeDebug("20230617 looking for lun={}", lun)

        # luns = self.getAllLuns()
        #  getLunByID replaces getAllLuns,
        #  it uses the lun input id for the range to look for the lun
        luns = self.getLunByID(lun)
        foundlun = None
        for item in luns:
            # self.logger.writeDebug('ldevId={}', str(item['ldevId']))
            # self.logger.writeDebug('lun={}', str(lun))
            try:
                if str(item["ldevId"]) == str(lun):
                    foundlun = item
                    self.logger.writeDebug("foundlun={}", foundlun)
                    break
            except Exception as e:
                self.logger.writeDebug("403 e={}", e)
                self.logger.writeError(str(e))

        self.logger.writeDebug("405 foundlun={}", foundlun)
        if foundlun is None:
            self.logger.writeDebug("lun {} not found", lun)

        self.logger.writeExitSDK(funcName)
        return foundlun

    def getLunByNaa(self, canonicalName):

        funcName = "hv_storagemanager:getLunByNaa"
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
            self.logger.writeDebug("modelCode={0}".format(modelCode))
            serialSubCode = canonicalName[24:28]
            serialCode = serialSubCode

            self.logger.writeDebug("serialCode={0}".format(serialCode))
            storageSerial = int(serialCode, 16)
            if modelCode == "502":
                storageSerial = "2{0}".format(storageSerial)
            elif modelCode == "504":
                storageSerial = "4{0}".format(storageSerial)
            elif modelCode == "506":
                storageSerial = "6{0}".format(storageSerial)
            elif modelCode == "507":
                storageSerial = "7{0}".format(storageSerial)

            self.storage_serial = int(storageSerial)
            self.logger.writeDebug("storageSerial={0}".format(self.storage_serial))

            lun = int(lunCode, 16)
            self.logger.writeDebug("lun={0}".format(lun))
            self.logger.writeExitSDK(funcName)
            return self.getLun(lun)

    def updateLunInDP(self, lunResourceId, size):
        funcName = "hv_storagemanager:updateLunInDP"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lunResourceId={}", lunResourceId)
        self.logger.writeParam("size={}", size)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam("resourceId={}", resourceId)
        self.logger.writeParam("lunResourceId={}", lunResourceId)
        self.logger.writeParam("ucp={}", ucp)

        # urlPath = "v2/storage/devices/{0}/volumes/{1}".format(resourceId, lunResourceId)
        urlPath = "v3/storage/{0}/volumes/{1}".format(resourceId, lunResourceId)
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeDebug("url={}", url)
        body = {
            # 'capacity': str(size) + 'GB'
            "capacity": size.upper() if size else None
        }
        self.logger.writeDebug("body={}", body)
        headers = self.ucpManager.getAuthToken()
        headers["PartnerId"] = self.partnerId
        if self.subscriberId:
            headers["subscriberId"] = self.subscriberId
        self.logger.writeDebug("headers={}", headers)

        response = requests.patch(
            url, json=body, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug("response={}", response.json())
        if response.ok:
            # resourceId = response.json()['data']['resourceId']
            # self.logger.writeDebug('resourceId={}', resourceId)
            taskId = response.json()["data"].get("taskId")
            self.ucpManager.checkTaskStatus(taskId)
            time.sleep(10)
            self.logger.writeExitSDK(funcName)
        else:
            self.logger.writeDebug("response not ok={}", response)
            raise Exception(response.text())

    def getAllStorageSystems(self):
        funcName = "hv_storagesystem:getAllStorageSystems"
        self.logger.writeEnterSDK(funcName)

        # get storage in each UCP
        urlPath = "v2/storage/devices"
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeDebug("url={}", url)

        ucp_systems = self.ucpManager.getAllUcpSystem()
        self.logger.writeDebug(
            "getAllStorageSystems, loop thru each ucp and get list of storages"
        )

        storage_systems = []
        for ucp in ucp_systems:
            sn = str(ucp.get("serialNumber"))
            self.logger.writeDebug(sn)
            body = {"ucpSystem": sn}
            self.logger.writeDebug("body={}", body)
            headers = self.ucpManager.getAuthToken()

            self.logger.writeDebug("getAllStorageSystems for ucp_serial={}", sn)
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
            # elif "HIJSONFAULT" in response.headers:
            #     Utils.raiseException(response)
            else:
                self.throwException(response)

        self.logger.writeExitSDK(funcName)
        return storage_systems

    def getStorageSystem(self):
        """
        docstring
        """
        funcName = "hv_storagesystem:getStorageSystem"
        self.logger.writeEnterSDK(funcName)

        systems = self.fetchStorageSystems()
        # self.logger.writeDebug('systems={}', systems)

        system = None
        for x in systems:
            self.logger.writeDebug(int(x["serialNumber"]))
            self.logger.writeDebug(self.storage_serial)
            if str(x["serialNumber"]) == str(self.storage_serial):
                system = x
                break

        self.logger.writeDebug("system={}", system)
        result = self.formatStorageSystem(system)

        self.logger.writeExitSDK(funcName)
        return result

    # 2.4 MT updateLunVldevId
    def updateLunVldevId(
        self,
        storage_resourceId: str,
        lun_resourceId: str,
        lunId: int,
        vldev_id_old: int,
        vldev_id: int,
    ):
        funcName = "hv_storagemanager:updateLunVldevId"
        self.logger.writeEnterSDK(funcName)

        self.logger.writeParam("storage_resourceId={}", storage_resourceId)
        self.logger.writeParam("lun_resourceId={}", lun_resourceId)
        self.logger.writeParam("lunId={}", lunId)
        self.logger.writeParam("vldev_id_old={}", vldev_id_old)
        self.logger.writeParam("vldev_id={}", vldev_id)

        if vldev_id_old == vldev_id:
            return

        headers = self.ucpManager.getAuthToken()
        headers["PartnerId"] = self.partnerId
        if self.subscriberId:
            headers["subscriberId"] = self.subscriberId
        self.logger.writeDebug("752 headers={}", headers)

        urlPath = "v2/storage/devices/{0}/volumes/{1}".format(
            storage_resourceId, lun_resourceId
        )
        url = self.ucpManager.getUrl(urlPath)

        body = {
            "virtualLdevId": vldev_id,
        }

        self.logger.writeDebug("565 url={}", url)
        self.logger.writeDebug("body={}", body)
        self.logger.writeDebug("headers={}", headers)

        try:
            response = requests.patch(
                url,
                json=body,
                headers=headers,
                verify=self.shouldVerifySslCertification,
            )
            self.logger.writeDebug("568 response={}", response.json())

            if not response.ok:
                self.throwException(response)
            else:
                taskId = response.json()["data"].get("taskId")
                self.ucpManager.checkTaskStatus(taskId)
                #  20240831 after this is done, there is a delay for the facts to get updated
                # time.sleep(20)
        except Exception as e:
            self.logger.writeDebug("773 err:{}", e)
            raise Exception(e)

        self.logger.writeExitSDK(funcName)

    # 2.4 MT applyVolTiering
    def applyVolTiering(
        self,
        lunId: int,
        is_relocation_enabled: bool,
        tier_level_for_new_page_allocation: str,
        tier_level: int,
        tier1_allocation_rate_min: int,
        tier1_allocation_rate_max: int,
        tier3_allocation_rate_min: int,
        tier3_allocation_rate_max: int,
        name="",
    ):
        funcName = "hv_storagemanager:applyVolTiering"
        self.logger.writeEnterSDK(funcName)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam("resourceId={}", resourceId)
        self.logger.writeParam("ucp={}", ucp)

        body = {
            "name": "volume-policy-1",
            "lunId": int(lunId),
            "serialNumber": str(self.storage_serial),
            "ucpSystem": "UCP-CI-202404",
            # "ucpSystem": CommonConstants.UCP_SERIAL,
            # "tierLevelForNewPageAlloc": tierLevelForNewPageAlloc,
            # "tierLevel": tier_level,
            # "enableRelocation": is_relocation_enabled,
            # "tier1AllocRateMax": tier1_allocation_rate_max,
            # "tier1AllocRateMin": tier1_allocation_rate_min,
            # "tier3AllocRateMax": tier3_allocation_rate_max,
            # "tier3AllocRateMin": tier3_allocation_rate_min,
            "shouldAllowDelete": False,
        }

        if tier_level_for_new_page_allocation:
            tierLevelForNewPageAlloc = "M"
            if tier_level_for_new_page_allocation.lower() == "high":
                tierLevelForNewPageAlloc = "H"
            if tier_level_for_new_page_allocation.lower() == "low":
                tierLevelForNewPageAlloc = "L"
            body["tierLevelForNewPageAlloc"] = tierLevelForNewPageAlloc

        if is_relocation_enabled is not None:
            body["enableRelocation"] = is_relocation_enabled
        if tier_level is not None:
            body["tierLevel"] = tier_level
        if tier1_allocation_rate_max:
            body["tier1AllocRateMax"] = tier1_allocation_rate_max
        if tier1_allocation_rate_min:
            body["tier1AllocRateMin"] = tier1_allocation_rate_min
        if tier3_allocation_rate_max:
            body["tier3AllocRateMax"] = tier3_allocation_rate_max
        if tier3_allocation_rate_min:
            body["tier3AllocRateMin"] = tier3_allocation_rate_min

        self.logger.writeDebug("body={}", body)
        headers = self.ucpManager.getAuthToken()
        headers["PartnerId"] = self.partnerId
        if self.subscriberId:
            headers["subscriberId"] = self.subscriberId
        self.logger.writeDebug("752 headers={}", headers)

        urlPath = "v3/luntiering/addPolicy"
        urlPath = "v2/policies/luntiering"
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeDebug("565 url={}", url)

        try:
            response = requests.post(
                url,
                json=body,
                headers=headers,
                verify=self.shouldVerifySslCertification,
            )
            self.logger.writeDebug("568 response={}", response.json())

            if not response.ok:
                self.throwException(response)
            else:
                taskId = response.json()["data"].get("taskId")
                self.ucpManager.checkTaskStatus(taskId)
                #  20240831 after this is done, there is a delay for the facts to get updated
                time.sleep(20)
        except Exception as e:
            self.logger.writeDebug("773 err:{}", e)
            raise Exception(e)

        self.logger.writeExitSDK(funcName)

    def createLunInDP(
        self,
        lun,
        pool,
        size,
        dedup,
        enableDRS,
        name="",
    ):
        funcName = "hv_storagemanager:createLunInDP"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("pool={}", pool)
        self.logger.writeParam("sizeInGB={}", size)
        self.logger.writeParam("luName={}", name)
        self.logger.writeParam("dedup={}", dedup)
        self.logger.writeParam("enableDRS={}", enableDRS)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam("resourceId={}", resourceId)
        self.logger.writeParam("ucp={}", ucp)

        body = {
            "deduplicationCompressionMode": dedup,
            "enableDRS": enableDRS,
            "poolId": pool,
            "name": name,
            "capacity": size.upper() if size else None,
            "resourceGroupId": 0,
            "ucpSystem": ucp,
        }
        if lun is not None:
            body["lunId"] = lun
        self.logger.writeDebug("body={}", body)
        headers = self.ucpManager.getAuthToken()

        # a2.4 MT create lun
        urlPath = "v3/storage/{0}/volumes".format(resourceId)
        headers = self.ucpManager.getAuthToken()
        headers["partnerId"] = self.partnerId
        if self.subscriberId:
            headers["subscriberId"] = self.subscriberId
        # urlPath = "v2/storage/devices/{0}/volumes".format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeDebug("565 url={}", url)
        response = requests.post(
            url, json=body, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug("568 response={}", response.json())
        if response.ok:
            self.logger.writeDebug("resourceId={}", resourceId)
            taskId = response.json()["data"].get("taskId")
            self.logger.writeDebug("572 taskId={}", taskId)

            # 20240904 subtask
            self.ucpManager.checkTaskSubtaskStatus(taskId)
            time.sleep(5)

            self.logger.writeDebug(" 575 lun={}", lun)
            if lun is None:

                # with subscriber, the taskid is for:
                #   Successfully tagged Volume xxx to subscriber
                # which is diff without subscriber where the new lun is given
                lun = self.getLunIdFromTaskStatusEvents(taskId)
                self.logger.writeDebug("578 lun={}", lun)

                # a2.4 MT, post creat lun need to parse return if subscriber is given
                # we are getting the grid
                # have to look up the ldevid
                try:
                    int(lun)
                except (ValueError, TypeError):
                    ss = lun.split(" ")
                    lun_resourceId = ""
                    if ss:
                        lun_resourceId = ss[0]
                        lunInfo = self.getOneLunByResourceID(lun_resourceId)
                        self.logger.writeDebug(" 544 lunInfo={}", lunInfo)
                        lun = lunInfo["ldevId"]

            # a2.4 MT post createLunInDP, need refresh
            # need to refresh luns for v3 get vol to return the result
            # the get lun MT playbook would show the id when it is done
            # can take a few minutes
            self.logger.writeDebug(" 596 lun={}", lun)
            if lun:
                self.logger.writeDebug(type(lun))
                # self.refreshVolumesMT(resourceId,lun)

                # self.getLun has problem, only works after facts refresh,
                # since operator only appends the latest when patching the facts
                #
                # logicalUnit = self.getLun(lun)
                # volumeResourceId = logicalUnit.get('resourceId')

                self.logger.writeDebug(" 596 storage_serial={}", self.storage_serial)
                volumeResourceId = self.get_storage_volume_md5_hash(lun)

                #  20240831 tagV2Volume volumeResourceId
                self.logger.writeDebug(" 596 volumeResourceId={}", volumeResourceId)

                # Removed the volume tag as already tagged using the v3 api
                # try:
                #     comment = self.tagV2Volume(resourceId, volumeResourceId)
                # except Exception as e:
                #     self.deleteLunV2(volumeResourceId)
                #     self.logger.writeDebug(" failed to tagV2Volume={}", volumeResourceId)
                #     self.logger.writeExitSDK(funcName)
                #     raise e

            # 20240824 - should we apply vol tiering here? it maybe easier to make a sep call in the runner

            self.logger.writeExitSDK(funcName)
            return lun, ""
        else:
            self.logger.writeExitSDK(funcName)
            self.logger.writeDebug("response={}", response)
            if response.status_code == 422:
                raise Exception("The lun name is invalid.")
            else:
                #  this is how to handle porcleain error 400 or 500,
                #  return the error message
                rjson = response.json()
                raise Exception(rjson["error"])

    def createLunInPG(
        self,
        lun,
        parityGroup,
        size,
        stripeSize,
        metaResourceSerial,
        luName,
    ):

        funcName = "hv_storagemanager:createLunInPG"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("parityGroupId={}", parityGroup)
        self.logger.writeParam("sizeInGB={}", size)
        self.logger.writeParam("luName={}", luName)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam("resourceId={}", resourceId)
        self.logger.writeParam("ucp={}", ucp)

        urlPath = "v2/storage/devices/{0}/volumes".format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeDebug("url={}", url)
        body = {
            "parityGroupId": parityGroup,
            "name": luName,
            "capacity": str(size).upper() if size else None,
            "resourceGroupId": 0,
            "ucpSystem": ucp,
        }
        if lun is not None:
            body["lunId"] = lun
        self.logger.writeDebug("body={}", body)
        headers = self.ucpManager.getAuthToken()
        # self.logger.writeDebug('headers={}', headers)
        response = requests.post(
            url, json=body, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug("response={}", response.json())
        if response.ok:
            # resourceId = response.json()['data']['resourceId']
            # self.logger.writeDebug('resourceId={}', resourceId)
            taskId = response.json()["data"].get("taskId")
            self.ucpManager.checkTaskStatus(taskId)
            time.sleep(5)

            self.logger.writeDebug("20230617 exiting {} lun={}", funcName, lun)
            if lun is None:
                #  ldevid was not given in the input
                #  get the newly created lun ldevid
                lun = self.getLunIdFromTaskStatusEvents(taskId)
            self.logger.writeDebug("20230617 exiting {} lun={}", funcName, lun)

            self.logger.writeExitSDK(funcName)
            return lun
        else:
            self.logger.writeDebug("response={}", response)
            raise Exception(response)

    # a2.4 MT updateLunName
    # # this func does expand size, change dedup, and lun name
    def updateLunName(self, lunResourceId, lunName):
        funcName = "StorageManager:updateLunName"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lunResourceId={}", lunResourceId)
        self.logger.writeParam("sizeInGB={}", lunName)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam("resourceId={}", resourceId)
        self.logger.writeParam("lunResourceId={}", lunResourceId)
        self.logger.writeParam("ucp={}", ucp)

        urlPath = "v2/storage/devices/{0}/volumes/{1}".format(resourceId, lunResourceId)
        urlPath = "v3/storage/{0}/volumes/{1}".format(resourceId, lunResourceId)
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeDebug("url={}", url)
        body = {"lunName": lunName}
        self.logger.writeDebug("body={}", body)

        headers = self.ucpManager.getAuthToken()
        headers["PartnerId"] = self.partnerId
        if self.subscriberId:
            headers["subscriberId"] = self.subscriberId
        self.logger.writeDebug("752 headers={}", headers)

        response = requests.patch(
            url, json=body, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug("response={}", response.json())
        if response.ok:
            # resourceId = response.json()['data']['resourceId']
            # self.logger.writeDebug('resourceId={}', resourceId)
            taskId = response.json()["data"].get("taskId")
            self.ucpManager.checkTaskStatus(taskId)
            time.sleep(10)
            self.logger.writeExitSDK(funcName)
        else:
            self.logger.writeDebug("response={}", response)
            if response.status_code == 422:
                raise Exception("The lun name is invalid.")
            else:
                raise Exception(response.status_code)

    def setDedupCompression(self, lunResourceId, dedupMode):
        funcName = "hv_storagemanager:setDedupCompression"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lunResourceId={}", lunResourceId)
        self.logger.writeParam("dedupMode={}", dedupMode)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam("resourceId={}", resourceId)
        self.logger.writeParam("lunResourceId={}", lunResourceId)
        self.logger.writeParam("ucp={}", ucp)

        urlPath = "v2/storage/devices/{0}/volumes/{1}".format(resourceId, lunResourceId)
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeDebug("url={}", url)
        body = {"deduplicationCompressionMode": dedupMode}
        self.logger.writeDebug("body={}", body)
        headers = self.ucpManager.getAuthToken()
        self.logger.writeDebug("headers={}", headers)
        response = requests.patch(
            url, json=body, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug("response={}", response.json())
        if response.ok:
            # resourceId = response.json()['data']['resourceId']
            # self.logger.writeDebug('resourceId={}', resourceId)
            taskId = response.json()["data"].get("taskId")
            self.ucpManager.checkTaskStatus(taskId)
            time.sleep(10)
            self.logger.writeExitSDK(funcName)
        else:
            self.logger.writeDebug("response={}", response)
            #  this is how to handle porcleain error 400 or 500,
            #  return the error message
            rjson = response.json()
            raise Exception(rjson["error"])

    def cloneLunInDP(
        self,
        sourceLun,
        pool,
        clonedLunName,
    ):

        funcName = "hv_storagemanager:cloneLunInDP"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("sourceLun={}", sourceLun)
        self.logger.writeParam("pool={}", pool)
        self.logger.writeParam("clonedLunName={}", clonedLunName)

        urlPath = "LogicalUnit/LogicalUnit/CloneInDP"
        url = self.ucpManager.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.storage_serial,
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
            return self.ucpManager.checkTaskStatus(taskId)
        else:
            self.logger.writeDebug("response={}", response)
            raise Exception(response)

    # a2.4 MT deleteLun
    def deleteLun(self, lunResourceId):
        funcName = "hv_storagemanager:deleteLun"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lunResourceId={}", lunResourceId)
        (storageResourceId, ucp) = self.getStorageSystemResourceId()

        urlPath = "v2/storage/devices/{0}/volumes/{1}".format(
            storageResourceId, lunResourceId
        )
        urlPath = "v3/storage/{0}/volumes/{1}".format(storageResourceId, lunResourceId)

        url = self.ucpManager.getUrl(urlPath)
        url = url + "?isDelete=true"
        headers = self.ucpManager.getAuthToken()
        headers["PartnerId"] = self.partnerId
        if self.subscriberId:
            headers["subscriberId"] = self.subscriberId

        self.logger.writeParam("url={}", url)
        response = requests.delete(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        self.logger.writeDebug(response.status_code)
        if response.ok:
            # resourceId = response.json()['data']['resourceId']
            # self.logger.writeDebug('resourceId={}', resourceId)
            taskId = response.json()["data"].get("taskId")
            self.ucpManager.checkTaskStatus(taskId)
            time.sleep(10)
            self.logger.writeExitSDK(funcName)
            return True
        else:
            self.logger.writeDebug("response={}", response)
            raise Exception(response)

    # a2.4 MT removeNamespace
    def removeNamespace(self, storageResourceId, nvmSubsystemId, namespaceId):

        funcName = "hv_storagemanager:removeNamespace"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("nvmSubsystemId={}", nvmSubsystemId)
        self.logger.writeParam("namespaceId={}", namespaceId)

        urlPath = "v2/storage/devices/{0}/nvmSubsystems/{1}/namespaces".format(
            storageResourceId, nvmSubsystemId
        )

        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()

        namespaceIds = []
        namespaceIds.append(int(namespaceId))

        body = {}
        body["namespaceIds"] = namespaceIds
        self.logger.writeDebug("body={}", body)

        self.logger.writeParam("url={}", url)
        response = requests.delete(
            url, headers=headers, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeDebug(response.status_code)
        if response.ok:
            # resourceId = response.json()['data']['resourceId']
            # self.logger.writeDebug('resourceId={}', resourceId)
            taskId = response.json()["data"].get("taskId")
            self.ucpManager.checkTaskStatus(taskId)
            time.sleep(10)
            self.logger.writeExitSDK(funcName)
        else:
            self.logger.writeDebug("response={}", response)
            raise Exception(response)

    def deleteLunV2(self, lunResourceId):
        funcName = "hv_storagemanager:deleteLunV2"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lunResourceId={}", lunResourceId)
        (storageResourceId, ucp) = self.getStorageSystemResourceId()

        urlPath = "v2/storage/devices/{0}/volumes/{1}".format(
            storageResourceId, lunResourceId
        )

        url = self.ucpManager.getUrl(urlPath)
        url = url + "?isDelete=true"
        headers = self.ucpManager.getAuthToken()

        self.logger.writeParam("url={}", url)
        response = requests.delete(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        self.logger.writeDebug(response.status_code)
        if response.ok:
            # resourceId = response.json()['data']['resourceId']
            # self.logger.writeDebug('resourceId={}', resourceId)
            taskId = response.json()["data"].get("taskId")
            self.ucpManager.checkTaskStatus(taskId)
            time.sleep(5)
            self.logger.writeExitSDK(funcName)
            return True
        else:
            self.logger.writeDebug("response={}", response)
            raise Exception(response)

    def getSoftLimitMessageFromTaskStatusEvents(self, taskId):
        funcName = "hv_storagemanager:getSoftLimitMessageFromTaskStatusEvents"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("taskId={}", taskId)
        headers = self.ucpManager.getAuthToken()
        urlPath = "/v2/tasks/{0}".format(taskId)
        url = self.ucpManager.getUrl(urlPath)
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug("response={}", response)
        status = None
        if response.ok:
            status = response.json()["data"].get("status")
            response.json()["data"].get("name")

        returnMsg = None
        if status.lower() == "success":
            events = response.json()["data"].get("events")
            description = events[1].get("description")
            self.logger.writeDebug(description)
            returnMsg = "Please increase quota"
            start = description.find(returnMsg)
            returnMsg = description
            if start < 0:
                self.logger.writeDebug("Not found")
                return None

        self.logger.writeExitSDK(funcName)
        return returnMsg

    def getLunIdFromTaskStatusEvents(self, taskId):
        funcName = "hv_storagemanager:getLunIdFromTaskStatusEvents"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("taskId={}", taskId)
        headers = self.ucpManager.getAuthToken()
        urlPath = "/v2/tasks/{0}".format(taskId)
        url = self.ucpManager.getUrl(urlPath)
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug("response={}", response)
        status = None
        lun = None
        if response.ok:
            status = response.json()["data"].get("status")
            response.json()["data"].get("name")

        if status.lower() == "success":
            events = response.json()["data"].get("events")
            description = events[0].get("description")
            self.logger.writeDebug(description)
            # start = description.find("Created logical Unit") + len("Created logical Unit")
            # end = description. find("in")
            # lun = description[start:end]
            # parsedLun = 'parsedLun={0}'.format(lun)

            # some has the "Successfully formatted volume" before the "Successfully created volume"
            msg = "Successfully formatted volume "
            start = description.find(msg)
            if start < 0:
                msg = "Successfully created volume "
                start = description.find(msg)

            start = start + len(msg)
            end = description.find(" on storage system")
            lun = description[start:end]

            parsedLun = "20230617 parsedLun={0}".format(lun)
            self.logger.writeDebug(parsedLun)
        self.logger.writeExitSDK(funcName)
        return lun.strip()

    @staticmethod
    def formatStorageSystem(storageSystem):
        funcName = "hv_storagemanager:StorageSystemManager:formatStorageSystem"
        UcpManager.logger.writeEnterSDK(funcName)

        # UcpManager.logger.writeDebug('storageSystem={}',storageSystem)
        if storageSystem is None:
            UcpManager.logger.writeDebug("storageSystem is None")
            return

        storageSystem.pop("resourceId", None)
        storageSystem.pop("storageEfficiencyStat", None)
        storageSystem.pop("storageDeviceLicenses", None)
        storageSystem.pop("isUnified", None)
        storageSystem.pop("tags", None)
        storageSystem.pop("deviceType", None)
        # storageSystem.pop('ucpSystems', None)
        storageSystem.pop("username", None)

        UcpManager.logger.writeExitSDK(funcName)
        return storageSystem

    # fetch the SS CRs
    def fetchStorageSystems(self):
        funcName = "hv_storagemanager:fetchStorageSystems"
        self.logger.writeEnterSDK(funcName)

        headers = self.ucpManager.getAuthToken()
        urlPath = "v2/storage/devices"
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeParam("url={}", url)
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug("response={}", response)

        storage_systems = []
        if response.ok:
            authResponse = response.json()
            # self.logger.writeDebug('ISP response Json={}', authResponse)
            data = authResponse.get("data")
            # storage_systems.extend(data.get('storageDevices'))
            storage_systems = data

        # elif "HIJSONFAULT" in response.headers:
        #     Utils.raiseException(response)
        else:
            self.throwException(response)

        self.logger.writeExitSDK(funcName)
        return storage_systems

    def getV3HostGroup(self, hgName, hgPort):

        funcName = "hv_storagemanager:getV3HostGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeDebug("1162 hgName={}", hgName)
        self.logger.writeDebug("1162 hgPort={}", hgPort)

        # a2.4 MT getV3HostGroup
        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = "v2/storage/devices/{0}/hostGroups?refresh=false".format(resourceId)
        urlPath = "v3/storage/{0}/resource?type=HostGroup".format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        headers["PartnerId"] = self.partnerId

        # do not consider the subscriberId
        # since the caller wants to know if this hg is assigned (tagged already)
        #
        # if self.subscriberId:
        #     headers["subscriberId"] = self.subscriberId

        self.logger.writeDebug("1155 headers={}", headers)

        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        if response.ok:
            hgs1 = response.json()["data"]
            self.logger.writeDebug("1162 len={}", len(hgs1))

            hgs2 = []
            #  find the hg
            for hg in hgs1:
                hostGroupInfo = hg.get("hostGroupInfo", None)
                if hostGroupInfo:
                    hostGroupName = hostGroupInfo.get("hostGroupName", None)
                    port = hostGroupInfo.get("port", None)
                    if hgName == hostGroupName and hgPort == port:
                        hgs2.append(hg)
                        break

            self.logger.writeExitSDK(funcName)
            return hgs2
        else:
            self.throwException(response)

    #  this will take time for OOB
    def getAllHostGroups(self):

        funcName = "hv_storagemanager:getAllHostGroups"
        self.logger.writeEnterSDK(funcName)

        # a2.4 MT getAllHostGroups
        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = "v2/storage/devices/{0}/hostGroups?refresh=false".format(resourceId)
        urlPath = "v3/storage/devices/{0}/hostGroups/details?refresh=false".format(
            resourceId
        )
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        headers["PartnerId"] = self.partnerId
        if self.subscriberId:
            headers["subscriberId"] = self.subscriberId

        self.logger.writeDebug("989 headers={}", headers)

        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        if response.ok:
            # self.logger.writeDebug('response.json()={}',
            #                        response.json())
            self.logger.writeExitSDK(funcName)
            return response.json()["data"]
        else:
            self.throwException(response)

    # a2.4 MT getIscsiTargets
    def getIscsiTargets(self):

        funcName = "hv_storagemanager:getIscsiTargets"
        self.logger.writeEnterSDK(funcName)

        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = "v3/storage/{0}/iscsiTargets/details".format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        headers["PartnerId"] = self.partnerId
        if self.subscriberId:
            headers["subscriberId"] = self.subscriberId

        self.logger.writeDebug("1300 headers={}", headers)

        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        if response.ok:
            self.logger.writeExitSDK(funcName)
            return response.json()["data"]
        else:
            self.throwException(response)

    # a2.4 MT getIscsiTarget
    def getIscsiTarget(self, sresourceId, resourceId):

        funcName = "hv_storagemanager:getIscsiTarget"
        self.logger.writeEnterSDK(funcName)

        urlPath = "v2/storage/devices/{0}/iscsiTargets/{1}".format(
            sresourceId, resourceId
        )

        headers = self.ucpManager.getAuthToken()
        if self.subscriberId:
            urlPath = "v3/storage/{0}/iscsiTargets/{1}".format(sresourceId, resourceId)
            headers["PartnerId"] = self.partnerId
            headers["subscriberId"] = self.subscriberId

        self.logger.writeDebug("1300 headers={}", headers)

        url = self.ucpManager.getUrl(urlPath)
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        if response.ok:
            self.logger.writeExitSDK(funcName)
            return response.json()["data"]
        else:
            self.throwException(response)

    # a2.4 MT detachLun
    def detachLun(self, logicalUnitId):

        funcName = "hv_storagemanager:detachLun"
        self.logger.writeEnterSDK(funcName)

        # get all nvme
        items, resourceId = self.getNvmSubsystems()
        if items:
            for item in items:
                self.logger.writeDebug("item={}", item)
                nvmSubsystemId = item["grid"]
                for lu in item["namespaces"]:
                    self.logger.writeDebug("namespace={}", lu)
                    logicalUnitIdIT = lu["lun"]
                    if str(logicalUnitId) == str(logicalUnitIdIT):
                        # found
                        # removeNamespace
                        luns = []
                        luns.append(int(logicalUnitIdIT))
                        namespaceId = lu["id"]
                        self.removeNamespace(resourceId, nvmSubsystemId, namespaceId)
                        self.logger.writeDebug(
                            "done removeNamespace, logicalUnitIdIT={}", logicalUnitIdIT
                        )
                        return True

        # get all hgs
        items = self.getAllHostGroups()
        if items:
            for item in items:
                # self.logger.writeDebug("1328 item={}", item)
                for lu in item["lunPaths"]:
                    logicalUnitIdIT = lu["ldevId"]
                    if str(logicalUnitId) == str(logicalUnitIdIT):
                        # found lun in hg
                        # unpresent from hg
                        luns = []
                        luns.append(int(logicalUnitIdIT))
                        self.unpresentLun2(luns, item["resourceId"])
                        self.logger.writeDebug(
                            "done detachLun hg, logicalUnitIdIT={}", logicalUnitIdIT
                        )
                        return True

        # get all iscsi targets (IT)
        items = self.getIscsiTargets()
        if items:
            for item in items:
                for lu in item["logicalUnits"]:
                    logicalUnitIdIT = lu["logicalUnitId"]
                    if str(logicalUnitId) == str(logicalUnitIdIT):
                        # found lun in IT
                        # unpresent from IT
                        self.unpresentLunFromIT(logicalUnitIdIT, item)
                        self.logger.writeDebug(
                            "done detachLun IT, logicalUnitIdIT={}", logicalUnitIdIT
                        )
                        return True

        return False

    def createHostGroup(self, hgName, port, wwnList, hostmode, hostModeOptions):

        funcName = "hv_storagemanager:createHostGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("wwnList={}", wwnList)
        self.logger.writeParam("hgName={}", hgName)
        self.logger.writeParam("hostmode={}", hostmode)
        self.logger.writeParam("hostModeOptions={}", hostModeOptions)
        self.logger.writeParam("port={}", port)
        self.logger.writeParam("dryRun={}", self.dryRun)
        if self.dryRun:
            return

        (resourceId, ucp) = self.getStorageSystemResourceId()
        self.logger.writeParam("resourceId={}", resourceId)
        self.logger.writeParam("ucp={}", ucp)

        wwns = []
        if len(wwnList) > 0:
            for x in list(wwnList):
                wwns.append({"id": x})
        self.logger.writeParam("wwns={}", wwns)

        body = {
            "hostGroupName": str(hgName),
            "port": str(port),
            "ucpSystem": ucp,
            "hostMode": hostmode,
            # 'hostModeOptions': list(hostModeOptions)
        }

        if hostModeOptions is not None:
            body["hostModeOptions"] = list(hostModeOptions)
        if len(wwns) > 0:
            body["wwns"] = wwns

        #  we do not have a playbook to tag a port,
        #  so we do it here, if the port belongs to other subs already,
        #  the create would fail
        try:
            # a2.4 MT tagPort to createHostGroup
            self.tagPort(resourceId, port)
        except Exception:
            self.logger.writeDebug("common case is already tagged")
            pass

        # a2.4 MT createHostGroup
        self.logger.writeParam("body={}", body)
        urlPath = "v2/storage/devices/{0}/hostGroups".format(resourceId)
        urlPath = "v3/storage/devices/{0}/hostGroups".format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeDebug("955 url={}", url)
        self.logger.writeDebug("body={}", body)
        headers = self.ucpManager.getAuthToken()
        headers["PartnerId"] = self.partnerId
        if self.subscriberId:
            headers["subscriberId"] = self.subscriberId

        self.logger.writeDebug("1057 headers:{}", headers)

        try:
            response = requests.post(
                url,
                headers=headers,
                json=body,
                verify=self.shouldVerifySslCertification,
            )
            if not response.ok:
                self.throwException(response)
            else:
                taskId = response.json()["data"].get("taskId")
                self.ucpManager.checkTaskStatus(taskId)
        except Exception as e:

            self.logger.writeDebug("1025 err:{}", e)
            self.logger.writeDebug(
                "1025 The hostgroup is already present, but not for this subscriber."
            )

            raise Exception(e)

        self.logger.writeExitSDK(funcName)

    def getHostGroup_24flat(
        self,
        hgName,
        port,
        doRetry=True,
    ):

        funcName = "hv_storagemanager:getHostGroup_24flat"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("hgName={}", hgName)
        self.logger.writeParam("port={}", port)
        (resourceId, ucp) = self.getStorageSystemResourceId()
        hostgroups = self.getAllHostGroups()

        hostgroup = None
        for x in hostgroups:
            if x.get("hostGroupName") == hgName and x.get("port") == port:
                hostgroup = x
                self.logger.writeDebug("Found HostGroup")
                break

        self.logger.writeExitSDK(funcName)
        return hostgroup

    def getHostGroup(
        self,
        hgName,
        port,
        doRetry=True,
    ):

        funcName = "hv_storagemanager:getHostGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("hgName={}", hgName)
        self.logger.writeParam("port={}", port)
        (resourceId, ucp) = self.getStorageSystemResourceId()
        hostgroups = self.getAllHostGroups()
        self.logger.writeDebug("1048 hostgroups={}", hostgroups)

        hostgroup = None
        for x in hostgroups:
            # a2.4 MT getHostGroup
            # x = hg.get('hostGroupInfo',None)
            if x is None:
                continue
            if x.get("hostGroupName") == hgName and x.get("port") == port:
                hostgroup = x
                self.logger.writeDebug("Found HostGroup")
                break

        self.logger.writeExitSDK(funcName)
        return hostgroup

    def deleteHostGroup(self, hgName, port):

        funcName = "hv_storagemanager:deleteHostGroup"
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

        if hostgroup is None:
            self.logger.writeInfo("Host group is not found.")
            self.logger.writeExitSDK(funcName)
            return

        # "subscriber_id" check
        self.logger.writeDebug("1162 Host group: {}", hostgroup)
        subscriber_id = hostgroup.get("subscriberId", "")
        self.logger.writeDebug("1162 Host group is tagged to: {}", subscriber_id)
        if subscriber_id != self.subscriberId:
            raise Exception("The hostgroup is tagged to " + subscriber_id)

        # a2.4 MT deleteHostGroup
        hgResourceId = hostgroup.get("resourceId")
        urlPath = "v2/storage/devices/{0}/hostGroups/{1}".format(
            resourceId, hgResourceId
        )
        urlPath = "v2/storage/devices/{0}/hostGroups/{1}".format(
            resourceId, hgResourceId
        )
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        headers["PartnerId"] = self.partnerId
        if self.subscriberId:
            headers["subscriberId"] = self.subscriberId

        response = requests.delete(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        if not response.ok:
            self.throwException(response)
        else:
            self.logger.writeDebug(response)
            # taskId = response.json()['data'].get('taskId')
            # self.checkTaskStatus(taskId)
            self.logger.writeExitSDK(funcName)

    def setHostMode(
        self,
        hgName,
        port,
        hostmode,
        hostopt,
    ):

        funcName = "hv_storagemanager:setHostMode"
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
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        body = {
            "hostMode": hostmode,
            "hostModeOptions": list(map(int, hostopt)),
        }

        self.logger.writeDebug(url)
        self.logger.writeDebug(body)
        retry_times = 5
        retry_count = 0
        while retry_count < retry_times:
            response = requests.patch(
                url,
                json=body,
                headers=headers,
                verify=self.shouldVerifySslCertification,
            )
            self.logger.writeDebug("response={}", response)

            if not response.ok:
                self.throwException(response)
            else:
                taskId = response.json()["data"].get("taskId")
                try:
                    self.ucpManager.checkTaskStatus(taskId)
                    break
                except Exception as e:
                    if "Operation failed. Updating host group failed" in str(e):
                        self.logger.writeDebug("Updating host group retrying")
                        retry_count += 1
                        time.sleep(10)
                        continue
                    else:
                        raise e

        else:
            raise Exception(
                "This issue may be intermittent. Please re-run the task after a while."
            )

        self.logger.writeExitSDK(funcName)

    def presentLun(
        self,
        luns,
        hgName,
        port,
    ):

        funcName = "hv_storagemanager:presentLun"
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

        # a2.4 MT presentLun
        hgResourceId = hostgroup.get("resourceId")
        urlPath = "/v2/storage/devices/{0}/hostGroups/{1}/volumes".format(
            resourceId, hgResourceId
        )
        urlPath = "/v3/storage/devices/{0}/hostGroups/{1}/volumes".format(
            resourceId, hgResourceId
        )
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        headers["PartnerId"] = self.partnerId
        if self.subscriberId:
            headers["subscriberId"] = self.subscriberId
        body = {"ldevIds": list(map(int, luns))}

        response = requests.post(
            url, headers=headers, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)

        if not response.ok:
            self.throwException(response)
        else:
            taskId = response.json()["data"].get("taskId")
            self.ucpManager.checkTaskStatus(taskId)

    # a2.4 MT unpresent Lun from iscsi target
    def unpresentLunFromIT(
        self,
        lun,
        iscsiTarget,
    ):

        funcName = "hv_storagemanager:unpresentLunFromIT"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("dryRun={}", self.dryRun)
        if self.dryRun:
            return

        (resourceId, unused) = self.getStorageSystemResourceId()
        resourceIdIT = iscsiTarget.get("resourceId")
        urlPath = "/v3/storage/{0}/iscsiTargets/{1}/volumes".format(
            resourceId, resourceIdIT
        )
        url = self.ucpManager.getUrl(urlPath)

        headers = self.ucpManager.getAuthToken()
        headers["PartnerId"] = self.partnerId
        if self.subscriberId:
            headers["subscriberId"] = self.subscriberId

        luns = []
        luns.append(int(lun))
        body = {"ldevIds": luns}
        self.logger.writeDebug("1665 body={}", body)

        response = requests.delete(
            url, headers=headers, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            self.throwException(response)
        else:
            taskId = response.json()["data"].get("taskId")
            self.ucpManager.checkTaskStatus(taskId)

    def unpresentLun(
        self,
        luns,
        hgName,
        port,
    ):

        funcName = "hv_storagemanager:UnpresentLun"
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

        # a2.4 MT unpresentLun
        hgResourceId = hostgroup.get("resourceId")
        urlPath = "/v2/storage/devices/{0}/hostGroups/{1}/volumes".format(
            resourceId, hgResourceId
        )
        urlPath = "/v3/storage/devices/{0}/hostGroups/{1}/volumes".format(
            resourceId, hgResourceId
        )
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        headers["PartnerId"] = self.partnerId
        if self.subscriberId:
            headers["subscriberId"] = self.subscriberId
        body = {"ldevIds": list(map(int, luns))}

        response = requests.delete(
            url, headers=headers, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            self.throwException(response)
        else:
            taskId = response.json()["data"].get("taskId")
            self.ucpManager.checkTaskStatus(taskId)

    # a2.4 MT unpresentLun2
    # this version is for caller already has the hgResourceId
    def unpresentLun2(
        self,
        luns,
        hgResourceId,
    ):

        funcName = "hv_storagemanager:UnpresentLun2"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", luns)
        self.logger.writeParam("dryRun={}", self.dryRun)
        if self.dryRun:
            return

        (resourceId, unused) = self.getStorageSystemResourceId()
        urlPath = "/v3/storage/devices/{0}/hostGroups/{1}/volumes".format(
            resourceId, hgResourceId
        )
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        headers["PartnerId"] = self.partnerId
        if self.subscriberId:
            headers["subscriberId"] = self.subscriberId
        body = {"ldevIds": list(map(int, luns))}

        response = requests.delete(
            url, headers=headers, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            self.throwException(response)
        else:
            taskId = response.json()["data"].get("taskId")
            self.ucpManager.checkTaskStatus(taskId)

    def addWWN(
        self,
        hgName,
        port,
        wwnList,
    ):

        funcName = "hv_storagemanager:addWWN"
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
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        response = requests.post(
            url, headers=headers, json=body, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug(url)
        self.logger.writeDebug(body)
        if not response.ok:
            self.throwException(response)
        else:
            taskId = response.json()["data"].get("taskId")
            self.ucpManager.checkTaskStatus(taskId)
            #  after success, have to refresh hg, else addl add would not work
            self.refreshHostGroups(resourceId)
        self.logger.writeExitSDK(funcName)

    def removeWWN(
        self,
        hgName,
        port,
        wwnList,
    ):
        funcName = "hv_storagemanager:removeWWN"
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
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        response = requests.delete(
            url, headers=headers, json=body, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug(url)
        self.logger.writeDebug(body)
        if not response.ok:
            self.logger.writeDebug("removeWWN not ok response={}", response)
            self.throwException(response)
        else:
            self.logger.writeDebug("response.json()={}", response.json())
            jjson = response.json()
            data = jjson.get("data", None)
            if data is not None:
                taskId = data.get("taskId", None)
                if taskId is not None:
                    self.ucpManager.checkTaskStatus(taskId)
            else:
                #  have to refresh, else the get hg would be wrong
                #  it may be a bug in the porcelain since it is not returning the data/taskId?
                self.refreshHostGroups(resourceId)
                # time.sleep(20)

        self.logger.writeExitSDK(funcName)

    def refreshHostGroups(self, resourceId):
        funcName = "hv_storagemanager:refreshHostGroups"
        self.logger.writeEnterSDK(funcName)

        urlPath = "v2/storage/devices/{0}/hostGroups?refresh=false".format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeDebug("refreshHostGroups url={}", url)
        headers = self.ucpManager.getAuthToken()
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        if response.ok:
            # time.sleep(90)
            self.logger.writeExitSDK(funcName)
        else:
            self.logger.writeDebug("refreshHostGroups not ok response={}", response)
            self.throwException(response)

    def getAllStoragePoolDetails(self):

        funcName = "hv_storagemanager:getHostgetAllStoragePoolDetailsGroup"
        self.logger.writeEnterSDK(funcName)

        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = "v2/storage/devices/{0}/pools?refresh=false".format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        if response.ok:
            self.logger.writeExitSDK(funcName)
            return response.json()["data"]
        else:
            self.throwException(response)

    def getStoragePoolDetails(self, poolId):
        data = self.getAllStoragePoolDetails()
        for p in data:
            if p["poolId"] == poolId:
                return p

    def getAllParityGroups(self):

        funcName = "hv_storagemanager:getAllParityGroups"
        self.logger.writeEnterSDK(funcName)

        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = "v2/storage/devices/{0}/parityGroups?refresh=false".format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        if response.ok:
            self.logger.writeExitSDK(funcName)
            return response.json()["data"]
        else:
            self.throwException(response)

    def getParityGroup(self, pgid):
        data = self.getAllParityGroups()
        for p in data:
            if p["parityGroupId"] == pgid:
                return p

    def getAllStoragePorts(self):

        funcName = "hv_storagemanager:getAllStoragePorts"
        self.logger.writeEnterSDK(funcName)

        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = "v2/storage/devices/{0}/ports?refresh=false".format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        if response.ok:
            self.logger.writeExitSDK(funcName)
            return response.json()["data"]
        else:
            self.throwException(response)

    def getNvmSubsystems(self):

        funcName = "hv_storagemanager:getNvmSubsystems"
        self.logger.writeEnterSDK(funcName)

        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = "v2/storage/devices/{0}/nvmSubsystems".format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        if response.ok:
            self.logger.writeExitSDK(funcName)
            return response.json()["data"], resourceId
        else:
            self.throwException(response)

    def get_storage_volume_md5_hash(self, ldev):
        storage_system_serial_number = self.storage_serial
        ldev_id = f"{storage_system_serial_number}:{ldev}"
        return f"storagevolume-{self.get_md5_hash(ldev_id)}"

    def get_md5_hash(self, data):
        # nosec: No security issue here as it is does not exploit any security vulnerability only used for generating unique resource id for UAIG
        md5_hash = hashlib.md5()
        md5_hash.update(data.encode("utf-8"))
        return md5_hash.hexdigest()
