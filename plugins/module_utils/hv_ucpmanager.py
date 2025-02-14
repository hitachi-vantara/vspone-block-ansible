import time

try:
    from .common.hv_log import Log
    from .common.hv_http_client import HTTPClient as requests
    from .common.hv_constants import CommonConstants
except ImportError:
    from common.hv_log import Log
    from common.hv_http_client import HTTPClient as requests
    from common.hv_constants import CommonConstants


class UcpManager:

    logger = Log()

    def __init__(
        self,
        management_address,
        management_username,
        management_password,
        api_token=None,
        partnerId=CommonConstants.PARTNER_ID,
        subscriberId=None,
        serial=None,
        webServicePort=None,
        sessionId=None,
    ):
        funcName = "hv_ucpmanager:init"
        self.logger = Log()
        self.logger.writeEnterSDK(funcName)

        self.sessionId = sessionId
        self.serial = serial
        self.webServicePort = webServicePort
        self.shouldVerifySslCertification = False
        self.management_address = management_address
        self.management_username = management_username
        self.management_password = management_password
        self.api_token = api_token
        self.partnerId = partnerId
        self.subscriberId = subscriberId
        self.basedUrl = "https://{0}".format(management_address)

        if management_address is None or management_address == "":
            raise Exception(
                "Management System is not configured. management address can not be empty."
            )

        # if management_username is None or \
        #    management_password is None or \
        #    management_address is None or \
        #    management_username == '' or \
        #    management_password == '' or \
        #    management_address == '' :
        #     raise Exception(self.sessionId, "Management System is not configured.")

    def getAuthTokenOnly(self):
        # funcName = "hv_ucpmanager:getAuthTokenOnly"
        # self.logger.writeEnterSDK(funcName)

        if self.api_token is not None:
            return self.api_token

        body = {
            "username": self.management_username,
            "password": self.management_password,
        }

        urlPath = "v2/auth/login"
        url = "{0}/porcelain/{1}".format(self.basedUrl, urlPath)

        try:
            response = requests.post(
                url, json=body, verify=self.shouldVerifySslCertification
            )
        except Exception:
            # can be due to wrong address or kong is not ready
            raise Exception(
                "Failed to establish a connection, please check the Management System address or the credentials."
            )

        token = None
        if response.ok:
            authResponse = response.json()
            data = authResponse["data"]
            token = data.get("token")
        else:
            self.logger.writeInfo("Unknown Exception response={}", response)
            raise Exception(
                "Management System login failed, please check the configuration."
            )

        return token

    def getAuthToken(self):
        funcName = "hv_ucpmanager:getAuthToken"
        # self.logger.writeEnterSDK(funcName)

        if self.api_token is not None:
            headers = {"Authorization": "Bearer {0}".format(self.api_token)}
            return headers

        body = {
            "username": self.management_username,
            "password": self.management_password,
        }

        urlPath = "v2/auth/login"
        url = "{0}/porcelain/{1}".format(self.basedUrl, urlPath)

        # self.logger.writeDebug('20230505 username={}',body['username'])
        # self.logger.writeDebug('20230505 url={}',url)

        try:
            response = requests.post(
                url, json=body, verify=self.shouldVerifySslCertification
            )
        except Exception:
            # can be due to wrong address or kong is not ready
            raise Exception(
                "Failed to establish a connection, please check the Management System address or the credentials."
            )

        token = None
        if response.ok:
            authResponse = response.json()
            data = authResponse["data"]
            token = data.get("token")
        elif "HIJSONFAULT" in response.headers:
            # for c-sharp only?
            self.logger.writeInfo("HIJSONFAULT response={}", response)
            raise Exception(response)
        else:
            self.logger.writeInfo("Unknown Exception response={}", response)
            raise Exception(
                "Management System login failed, please check the configuration."
            )

        headers = {"Authorization": "Bearer {0}".format(token)}
        # self.logger.writeExitSDK(funcName)
        return headers

    def getUrl(self, urlPath):
        return "{0}/porcelain/{1}".format(self.basedUrl, urlPath)

    def createUcpSystem(
        self, serial_number, gatewayIp, model, name, region, country, zipcode, zone
    ):
        funcName = "UcpManager:createUcpSystem"
        self.logger.writeEnterSDK(funcName)

        system = self.getUcpSystem(serial_number)
        self.logger.writeInfo("ucpsystem={}", system)

        if system is not None and name != system["name"]:
            raise Exception(
                "UCP serial number is already in use, name change is not supported."
            )

        if system is None:
            body = {
                "gatewayAddress": gatewayIp,
                "model": model,
                "name": name,
                "region": region,
                "serialNumber": serial_number,
                "country": country,
                "zipcode": zipcode,
                "zone": zone,
            }
            # a2.4 20240504 MT createUcpSystem
            urlPath = "v2/systems"
            url = "{0}/porcelain/{1}".format(self.basedUrl, urlPath)

            response = requests.post(
                url,
                headers=self.getAuthToken(),
                json=body,
                verify=self.shouldVerifySslCertification,
            )

            self.logger.writeInfo("132 create ucp response={}", response)
            if response.ok:
                resposeJson = response.json()
                resposeJson["data"]
                self.logger.writeInfo("resposeJson={}", resposeJson)
                taskId = resposeJson["data"].get("taskId")
                self.logger.writeInfo("taskId={}", taskId)
                self.checkTaskStatus(taskId)
                time.sleep(3)
                self.logger.writeExitSDK(funcName)
            # elif "HIJSONFAULT" in response.headers:
            #     self.logger.writeInfo("HIJSONFAULT response={}", response)
            #     Utils.raiseException(self.sessionId, response)
            else:
                self.logger.writeInfo("Response Exception response={}", response)
                str = "{0}".format(response)
                if "400" in str:
                    raise Exception("At least one of the input parameters is invalid.")

                raise Exception("Response error {0}".format(response))
                # raise Exception('Response error {0}'.format(response.status_code + response.message))

        return name, serial_number

    #  helper func
    def getUcpSystemByGateway(self, gatewayIp):
        funcName = "UcpManager:getUcpSystemByGateway"
        self.logger.writeEnterSDK(funcName)

        gatewayLast5 = gatewayIp.replace(".", "")[-5:]
        ucp_name = "ucp-{0}".format(gatewayLast5)
        "Logical-UCP-{0}".format(gatewayLast5)

        systems = self.getAllUcpSystem()
        system = next((x for x in systems if x.get("name") == ucp_name), None)
        self.logger.writeExitSDK(funcName)
        return system

    def getUcpSystemByName(self, ucp_name):
        funcName = "UcpManager:getUcpSystemByName"
        self.logger.writeEnterSDK(funcName)

        systems = self.getAllUcpSystem()
        system = next((x for x in systems if x.get("name") == ucp_name), None)
        self.logger.writeExitSDK(funcName)
        return system

    # 2.4 MT getUcpSystemResourceIdByName
    def getUcpSystemResourceIdByName(self, ucp_name):
        funcName = "UcpManager:getUcpSystemResourceIdByName"
        self.logger.writeEnterSDK(funcName)

        systems = self.getAllUcpSystem()
        system = next((x for x in systems if x.get("name") == ucp_name), None)

        self.logger.writeDebug("system={}", system)
        self.logger.writeDebug("systems={}", systems)

        resourceId = ""
        if system is not None:
            resourceId = system["resourceId"]

        self.logger.writeExitSDK(funcName)
        return resourceId

    #  serial and be ucp.name or ucp.serial
    def getUcpSystem(self, serial):
        funcName = "UcpManager:getUcpSystem"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeDebug("serial={}", serial)

        system = None
        systems = self.getAllUcpSystem()
        # for x in systems:
        #     ss = x.get('serialNumber')
        #     self.logger.writeDebug('ss={}',ss)
        #     ss = str(ss)
        #     self.logger.writeDebug('ss={}',ss)
        #     if ss == serial :
        #         system = x
        #         break

        system = next(
            (x for x in systems if str(x.get("serialNumber")) == serial), None
        )

        if system is None:
            system = next((x for x in systems if str(x.get("name")) == serial), None)

        # self.logger.writeDebug('674 system={}', system)
        self.logger.writeExitSDK(funcName)
        return system

    def getAllUcpSystem(self):
        funcName = "hv_ucpmanager:getAllUcpSystem"
        self.logger.writeEnterSDK(funcName)

        urlPath = "v2/systems"
        url = self.getUrl(urlPath)

        headers = self.getAuthToken()
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        if response.ok:
            authResponse = response.json()
            # self.logger.writeInfo('AllUcpSystem={}', authResponse)
            systems = authResponse.get("data")
            self.logger.writeExitSDK(funcName)
            return systems
        # elif "HIJSONFAULT" in response.headers:
        #     self.logger.writeInfo("raiseException={}", response)
        #     Utils.raiseException(self.sessionId, response)
        else:
            self.logger.writeInfo("throwException={}", response)
            self.throwException(response)

    def getTaskStatus(self, taskId):
        funcName = "UcpManager: getTaskStatus"
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
        return (status, name)

    def getUser(self):
        funcName = "UcpManager: getUser"
        self.logger.writeEnterSDK(funcName)
        headers = self.getAuthToken()
        urlPath = "/v2/rbac/users"
        url = self.getUrl(urlPath)
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        if response.ok:
            users = response.json()["data"].get("users")
            for user in users:
                if user["username"] == "admin":
                    return user
        return {}

    # 20240904 getTaskSubtaskFailedDescription
    # extends getTaskStatusDescription, only to get failed subtask description
    def getTaskSubtaskFailedDescription(self, taskId):
        funcName = "ucpManager: getTaskSubtaskFailedDescription"
        self.logger.writeEnterSDK(funcName)
        headers = self.getAuthToken()
        urlPath = "/v2/tasks/{0}".format(taskId)
        url = self.getUrl(urlPath)
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        description = None
        if response.ok:
            self.logger.writeDebug("TaskResponse={}", response.json())
            response.json()["data"].get("status")
            name = response.json()["data"].get("name")
            events = response.json()["data"].get("events")
            if len(events):
                descriptions = [element.get("description") for element in events]

                self.logger.writeDebug("-".join(descriptions))
                description = events[-1].get("description")
                self.logger.writeDebug(description)
                self.logger.writeExitSDK(funcName)

                description0 = "No descriptions"

                if len(descriptions):
                    description0 = self._get_description(descriptions)

                #  return only the first message
                return description0
            else:
                self.logger.writeExitSDK(funcName)
                return "{} failed".format(name)

    def getTaskStatusDescription(self, taskId):
        funcName = "ucpManager: getTaskStatusDescription"
        self.logger.writeEnterSDK(funcName)
        headers = self.getAuthToken()
        urlPath = "/v2/tasks/{0}".format(taskId)
        url = self.getUrl(urlPath)
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        description = None

        if response.ok:
            self.logger.writeDebug("taskResponse={}", response.json())
            response.json()["data"].get("status")
            name = response.json()["data"].get("name")
            events = response.json()["data"].get("events")
            if len(events):
                descriptions = [element.get("description") for element in events]

                self.logger.writeDebug("-".join(descriptions))
                description = events[-1].get("description")
                self.logger.writeDebug(description)
                self.logger.writeExitSDK(funcName)

                #  return only the first message and see
                return descriptions[0]
            else:
                self.logger.writeExitSDK(funcName)
                return "{} failed".format(name)

    # 20240904 get_task
    def get_task(self, taskId):
        headers = self.getAuthToken()
        urlPath = "/v2/tasks/{0}".format(taskId)
        url = self.getUrl(urlPath)
        return requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

    # 20240904 _get_description
    def _get_description(self, descriptions):
        # find the first subtask in the descriptions
        # get the subtask id
        # fetch it, then return the top most
        # if anything goes wrong, the top of the input descriptions is returned

        subtask = None

        #  caller ensures descriptions is proper
        description0 = descriptions[0]
        for desc in descriptions:
            if "Initiated subtask" in desc:
                ss = desc.replace(".", " ")
                ss = ss.split(" ")
                if len(ss) < 3:
                    #  unexpected error
                    break
                subtask = ss[2]

        if subtask is None:
            return description0

        self.logger.writeDebug("subtask = {}", subtask)
        task_response = self.get_task(subtask)
        self.logger.writeDebug("subtask_response = {}", task_response)

        if task_response.ok:
            # just return the top of the descriptions
            task_events = task_response.json()["data"].get("events")
            if len(task_events):
                descriptions = [element.get("description") for element in task_events]
                self.logger.writeDebug("subtask descriptions = {}", descriptions)
                description0 = "Task event details: " + ", ".join(descriptions)

        self.logger.writeDebug("description0 = {}", description0)
        return description0

    def getTaskStatusDescription_orig(self, taskId):
        funcName = "UcpManager: getTaskStatusDescription"
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
                self.logger.writeInfo("-".join(descriptions))
                description = events[-1].get("description")
                self.logger.writeInfo(description)
                return "-".join(descriptions)
            else:
                return "{} failed".format(name)

    def checkTaskStatus(self, taskId):
        funcName = "UcpManager:checkTaskStatus"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("taskId={}", taskId)
        (status, name) = self.getTaskStatus(taskId)
        self.logger.writeDebug("20230621 status={}", status)
        while status == "Running" or status == "Pending":
            self.logger.writeInfo(
                "{0} task with id {1} status is {2}".format(name, taskId, status)
            )
            time.sleep(5)
            (status, name) = self.getTaskStatus(taskId)

        if status.lower() == "failed":
            description = self.getTaskStatusDescription(taskId)
            self.logger.writeDebug(
                "{0} task with id {1} is failed.".format(name, taskId)
            )
            if "is already part of" in description:
                self.logger.writeDebug(
                    "storage is part of ... already, no exception, idempotent"
                )
            else:
                raise Exception("Operation failed. {0}".format(description))

        description = self.getTaskStatusDescription(taskId)
        self.logger.writeDebug("20230621 description={}", description)

        self.logger.writeExitSDK(funcName)
        return status

    # 20240904 checkTaskSubtaskStatus, extends checkTaskStatus
    def checkTaskSubtaskStatus(self, taskId):
        funcName = "UcpManager:checkTaskStatus"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("taskId={}", taskId)
        (status, name) = self.getTaskStatus(taskId)
        self.logger.writeDebug("20230621 status={}", status)
        while status == "Running" or status == "Pending":
            self.logger.writeInfo(
                "{0} task with id {1} status is {2}".format(name, taskId, status)
            )
            time.sleep(5)
            (status, name) = self.getTaskStatus(taskId)

        if status.lower() == "failed":
            # fail, return subtask info if it is there
            description = self.getTaskSubtaskFailedDescription(taskId)
            self.logger.writeDebug(
                "{0} task with id {1} is failed.".format(name, taskId)
            )
            if "is already part of" in description:
                self.logger.writeDebug(
                    "storage is part of ... already, no exception, idempotent"
                )
            else:
                raise Exception("Operation failed. {0}".format(description))

        # success, no subtask look up
        description = self.getTaskStatusDescription(taskId)
        self.logger.writeDebug("20230621 description={}", description)

        self.logger.writeExitSDK(funcName)
        return status

    def deleteUcpSystem(self, resourceId):
        funcName = "UcpManager:deleteUcpSystem"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("resourceId={}", resourceId)

        urlPath = "v2/systems"
        url = "{0}/porcelain/{1}/{2}".format(self.basedUrl, urlPath, resourceId)

        response = requests.delete(
            url, headers=self.getAuthToken(), verify=self.shouldVerifySslCertification
        )

        if response.ok:
            resposeJson = response.json()
            resposeJson["data"]
            self.logger.writeInfo("resposeJson={}", resposeJson)
            taskId = resposeJson["data"].get("taskId")
            self.logger.writeInfo("taskId={}", taskId)
            self.checkTaskStatus(taskId)
            self.logger.writeExitSDK(funcName)
        # elif "HIJSONFAULT" in response.headers:
        #     self.logger.writeInfo("HIJSONFAULT response={}", response)
        #     Utils.raiseException(self.sessionId, response)
        else:
            self.logger.writeInfo("Unknown Exception response={}", response)
            raise Exception(
                "Unknown error HTTP {0}".format(response.status_code + response.message)
            )

        return

    def updateUcpSystem(
        self,
        resourceId,
        gateway_address,
        region,
        country,
        zipcode,
    ):
        funcName = "UcpManager:updateUcpSystem"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("resourceId={}", resourceId)

        body = {
            "gatewayAddress": str(gateway_address),
            "region": str(region),
            "country": str(country),
            "zipcode": str(zipcode),
        }
        urlPath = "v2/systems"
        url = "{0}/porcelain/{1}/{2}".format(self.basedUrl, urlPath, resourceId)

        response = requests.patch(
            url,
            headers=self.getAuthToken(),
            json=body,
            verify=self.shouldVerifySslCertification,
        )

        if response.ok:
            resposeJson = response.json()
            resposeJson["data"]
            self.logger.writeInfo("resposeJson={}", resposeJson)
            taskId = resposeJson["data"].get("taskId")
            self.logger.writeInfo("taskId={}", taskId)
            self.checkTaskStatus(taskId)
            time.sleep(2)
            self.logger.writeExitSDK(funcName)
        # elif "HIJSONFAULT" in response.headers:
        #     self.logger.writeInfo("HIJSONFAULT response={}", response)
        #     Utils.raiseException(self.sessionId, response)
        else:
            self.logger.writeInfo("Unknown Exception response={}", response)
            raise Exception(
                "Unknown error HTTP {0}".format(response.status_code + response.message)
            )

        return

    def formatUCPs(self, ucps):
        funcName = "UcpManager:formatUCPs"
        self.logger.writeEnterSDK(funcName)
        try:
            for x in ucps:
                self.formatUCP(x)
            self.logger.writeExitSDK(funcName)
        except Exception as ex:
            self.logger.writeDebug("20230505 Exception={}", ex)

    def formatStorages(self, ss):
        funcName = "UcpManager:formatStorages"
        self.logger.writeEnterSDK(funcName)
        try:
            for x in ss:
                self.formatStorage(x)
            self.logger.writeExitSDK(funcName)
        except Exception as ex:
            self.logger.writeDebug("20230505 Exception={}", ex)

    def formatStorage(self, ss):
        del ss["ucpSystems"]

    def formatUCP(self, ucp):
        funcName = "UcpManager:formatUCP"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeDebug("20230505 ucp={}", ucp)
        ucp["status"] = ucp["resultStatus"]
        del ucp["resultStatus"]
        del ucp["computeDevices"]
        del ucp["ethernetSwitches"]
        del ucp["fibreChannelSwitches"]
        del ucp["linked"]
        del ucp["pluginRegistered"]
        del ucp["resourceState"]
        del ucp["resultMessage"]
        del ucp["resourceId"]
        del ucp["workloadType"]
        if ucp.get("zone") is not None:
            del ucp["zone"]
        for x in ucp["storageDevices"]:
            del x["resourceState"]
            del x["resourceId"]
        self.logger.writeExitSDK(funcName)

    def getStorageDevices(self, ucp):
        funcName = "UcpManager:getStorageDevices"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeExitSDK(funcName)
        return ucp["storageDevices"]

    def getStorageDevicesWithRefresh(self, ucp):
        funcName = "UcpManager:getStorageDevicesWithRefresh"
        self.logger.writeEnterSDK(funcName)

        ucp_id = ucp["resourceId"]
        urlPath = "v2/systems/{}?refresh=true".format(ucp_id)

        url = self.getUrl(urlPath)

        headers = self.getAuthToken()

        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        if response.ok:
            authResponse = response.json()
            # self.logger.writeInfo('AllUcpSystem={}', authResponse)
            systems = authResponse.get("data")
            self.logger.writeExitSDK(funcName)
            return systems.get("storageDevices")
        elif "HIJSONFAULT" in response.headers:
            self.logger.writeInfo("raiseException={}", response)
        else:
            self.logger.writeInfo("throwException={}", response)
            self.throwException(response)

    def getAllLuns(self):

        funcName = "UcpManager:getAllLuns"
        self.logger.writeEnterSDK(funcName)
        resourceId = self.getStorageSystemResourceIdInISP()
        # (resourceId, ucp) = self.getStorageSystemResourceId()
        self.logger.writeInfo("Storage_resource_id={0}".format(resourceId))

        # a2.4 MT getAllLuns
        # urlPath = 'v2/storage/devices/{0}/volumes?refresh=false'.format(resourceId)
        urlPath = "v2/storage/devices/{0}/volumes?fromLdevId=0&toLdevId=65000&refresh=false".format(
            resourceId
        )
        urlPath = "v3/storage/{0}/volumes/details?fromLdevId=0&toLdevId=65000&refresh=false".format(
            resourceId
        )

        url = self.getUrl(urlPath)
        self.logger.writeParam("491 url={}", url)

        headers = self.getAuthToken()
        headers["PartnerId"] = self.partnerId
        if self.subscriberId:
            headers["subscriberId"] = self.subscriberId
        # self.logger.writeDebug("497 headers={}", headers)

        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        #  too much to dump
        # self.logger.writeDebug('response.json()={}', response.json())
        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()["data"]
        else:
            raise Exception(response)

    def getStorageSystemResourceIdInISP(self):
        """
        docstring
        """

        funcName = "UcpManager:getStorageSystemResourceIdInISP"
        self.logger.writeEnterSDK(funcName)
        headers = self.getAuthToken()
        # self.logger.writeParam("headers={}", headers)

        urlPath = "v2/storage/devices"
        url = self.getUrl(urlPath)
        self.logger.writeParam("url={}", url)

        systems = self.getAllISPStorageSystems()

        self.logger.writeDebug("systems={}", systems)
        self.logger.writeDebug("20230606 self.serial={}", self.serial)

        system = None
        for x in systems:
            self.logger.writeDebug(int(x["serialNumber"]))
            self.logger.writeDebug(self.serial)
            self.logger.writeDebug(int(x["serialNumber"]) == self.serial)
            if str(x["serialNumber"]) == str(self.serial):
                system = x
                break
        if system is None:
            self.logger.writeError(
                f"Invalid serial = {self.serial}, please check once and try again."
            )
            raise Exception(
                "Invalid serial = {0}, please check once and try again.".format(
                    self.serial
                )
            )

        self.logger.writeExitSDK(funcName)
        return str(system.get("resourceId"))

    def getAllISPStorageSystems(self):
        funcName = "UcpManager:getAllISPStorageSystems"
        self.logger.writeEnterSDK(funcName)

        urlPath = "v2/systems/default"
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()

        self.logger.writeDebug("url={}", url)
        # self.logger.writeDebug("headers={}", headers)
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

    # MT getLunByID V3
    def getLunByID(self, ldevid):

        funcName = "UcpManager:getLunByID"
        self.logger.writeEnterSDK(funcName)
        resourceId = self.getStorageSystemResourceIdInISP()
        # (resourceId, ucp) = self.getStorageSystemResourceId()
        self.logger.writeDebug("537 Storage_resource_id={0}".format(resourceId))
        self.logger.writeDebug("537 ldevid={0}".format(ldevid))
        # self.logger.writeDebug('str(ldevid)={0}'.format(str(ldevid)))
        # self.logger.writeDebug('str(ldevid+10)={0}'.format(str(int(ldevid)+10)))
        # urlPath = 'v2/storage/devices/{0}/volumes?refresh=false'.format(resourceId)

        urlPath = "v2/storage/devices/{0}/volumes?fromLdevId={1}&toLdevId={2}&refresh=false".format(
            resourceId, str(0), str(int(ldevid) * 2)
        )
        headers = self.getAuthToken()
        headers["PartnerId"] = "apiadmin"
        if self.subscriberId:
            headers["subscriberId"] = self.subscriberId
        # self.logger.writeDebug("537 headers={}", headers)

        # urlPath = 'v3/storage/{0}/volumes/details?fromLdevId={1}&toLdevId={2}&refresh=false'.format(resourceId,str(0),str(int(ldevid)*2))
        # MT - the above does not always work with newly created luns, works with the fixed values and it is fast
        # seems like a bug in porcelain
        # a2.4 MT - 20240511 getLunByID
        urlPath = "v3/storage/{0}/volumes/details?fromLdevId=0&toLdevId=65000&refresh=false".format(
            resourceId
        )

        url = self.getUrl(urlPath)
        self.logger.writeParam("594 urlPath={}", url)

        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        #  too much to dump
        # self.logger.writeDebug('response.json()={}', response.json())
        self.logger.writeDebug("20230620 response.ok={}", response.ok)
        if response.ok:
            self.logger.writeDebug("get data json")
            items = response.json()["data"]
            if items is None or len(items) == 0:
                items = None
            # too much to dump
            # self.logger.writeDebug('589 items={}',items)
            self.logger.writeExitSDK(funcName)
            return items
        else:
            raise Exception(response)

    # MT getLunByID V2
    def getLunByID_v2(self, ldevid):

        funcName = "UcpManager:getLunByID_v2"
        self.logger.writeEnterSDK(funcName)
        resourceId = self.getStorageSystemResourceIdInISP()
        # (resourceId, ucp) = self.getStorageSystemResourceId()
        self.logger.writeDebug("537 Storage_resource_id={0}".format(resourceId))
        self.logger.writeDebug("537 ldevid={0}".format(ldevid))
        # self.logger.writeDebug('str(ldevid)={0}'.format(str(ldevid)))
        # self.logger.writeDebug('str(ldevid+10)={0}'.format(str(int(ldevid)+10)))
        # urlPath = 'v2/storage/devices/{0}/volumes?refresh=false'.format(resourceId)

        urlPath = "v2/storage/devices/{0}/volumes?fromLdevId={1}&toLdevId={2}&refresh=false".format(
            resourceId, str(0), str(int(ldevid) * 2)
        )
        headers = self.getAuthToken()

        url = self.getUrl(urlPath)
        self.logger.writeParam("732 urlPath={}", url)

        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        #  too much to dump
        # self.logger.writeDebug('response.json()={}', response.json())
        self.logger.writeDebug("20230620 response.ok={}", response.ok)
        if response.ok:
            self.logger.writeDebug("get data json")
            items = response.json()["data"]
            if items is None or len(items) == 0:
                items = None
            # too much to dump
            # self.logger.writeDebug('589 items={}',items)
            self.logger.writeExitSDK(funcName)
            return items
        else:
            raise Exception(response)

    def getLun(self, lun, doRetry=True):

        funcName = "UcpManager:getLun"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        luns = self.getLunByID(lun)

        if luns is None:
            return None

        foundlun = None
        for item in luns:
            try:
                if str(item["ldevId"]) == str(lun):
                    foundlun = item
                    self.logger.writeInfo(foundlun)
                    break
            except Exception as e:
                self.logger.writeInfo(str(e))

        self.logger.writeExitSDK(funcName)
        return foundlun

    def getLunByNaa(self, canonicalName):

        funcName = "UcpManager:getLunByNaa"
        self.logger.writeEnterSDK(funcName)

        self.logger.writeInfo("566 storageSerial={0}".format(self.serial))

        canonicalName = str(canonicalName).upper()
        manufacturerCode = "60060"
        if (
            len(canonicalName) == 36
            and canonicalName.find("NAA") == 0
            and canonicalName.find(manufacturerCode) > 0
        ):
            lunCode = canonicalName[28:36]
            self.logger.writeInfo("lunCode={0}".format(lunCode))
            modelCode = canonicalName[20:23]
            self.logger.writeInfo("modelCode={0}".format(modelCode))
            serialSubCode = canonicalName[24:28]
            serialCode = serialSubCode

            self.logger.writeInfo("serialCode={0}".format(serialCode))
            storageSerial = int(serialCode, 16)
            if modelCode == "502":
                storageSerial = "2{0}".format(storageSerial)
            elif modelCode == "504":
                storageSerial = "4{0}".format(storageSerial)
            elif modelCode == "506":
                storageSerial = "6{0}".format(storageSerial)
            elif modelCode == "507":
                storageSerial = "7{0}".format(storageSerial)

            # we found issue with naa.60060e80233abb0050603abb000009ae
            # the modelCode = 506 and it yield 615035, but it should be 715035!!
            # self.serial = int(storageSerial)
            # self.logger.writeInfo("storageSerial={0}".format(self.serial))
            #
            # we don't need the storageSerial anyways

            lun = int(lunCode, 16)
            self.logger.writeInfo("lun={0}".format(lun))
            self.logger.writeExitSDK(funcName)
            return self.getLun(lun)

    def updateLunInDP(self, lunResourceId, size):
        funcName = "UcpManager:updateLunInDP"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lunResourceId={}", lunResourceId)
        self.logger.writeParam("sizeInGB={}", size)

        # (resourceId, ucp) = self.getStorageSystemResourceId()
        resourceId = self.getStorageSystemResourceIdInISP()

        self.logger.writeParam("resourceId={}", resourceId)
        self.logger.writeParam("lunResourceId={}", lunResourceId)

        urlPath = "v2/storage/devices/{0}/volumes/{1}".format(resourceId, lunResourceId)
        url = self.getUrl(urlPath)
        self.logger.writeInfo("url={}", url)
        body = {"capacity": size}
        self.logger.writeInfo("body={}", body)
        headers = self.getAuthToken()
        # self.logger.writeInfo("headers={}", headers)
        response = requests.patch(
            url, json=body, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeInfo("response={}", response.json())
        self.logger.writeExitSDK(funcName)
        if response.ok:
            resourceId = response.json()["data"]["resourceId"]
            self.logger.writeInfo("resourceId={}", resourceId)
            taskId = response.json()["data"].get("taskId")
            self.checkTaskStatus(taskId)
            time.sleep(10)
        else:
            self.logger.writeDebug("response={}", response)
            raise Exception(response)

    #  handles attach SS to UCP and
    #  add SS to ISP then UCP, for this you need the SS login info
    def addStorageSystem(
        self,
        storage_serial,
        location,
        pumaGatewayAddress,
        gatewayPort,
        username,
        password,
        useOutOfBandConnection,
        ucpID,
    ):

        self.logger.writeDebug("system serial={}", ucpID)

        funcName = "UcpManager:addStorageSystem"
        self.logger.writeEnterSDK(funcName)
        self.serial = storage_serial

        # a2.4 MT addStorageSystem
        # ucp_serial = CommonConstants.UCP_NAME
        ucp_serial = ucpID
        ucpManager = UcpManager(
            self.management_address,
            self.management_username,
            self.management_password,
            self.api_token,
        )
        theUCP = ucpManager.getUcpSystem(ucpID)
        self.logger.writeDebug("674 serial={}", ucpID)
        # self.logger.writeDebug('674 theUCP={}', theUCP)
        self.registerPartner()

        if theUCP is None:
            self.logger.writeDebug("we should never get here")

            # # need to add UCP if it is not already created
            # # sng,a2.4 - create default UCP
            # theUCP = ucpManager.createUcpSystem(
            #     CommonConstants.UCP_SERIAL,
            #     pumaGatewayAddress, # this is from theUCP, so it will work for remote_gateway_address
            #     "UCP CI",
            #     ucpID,
            #     "AMERICA",
            #     "United States",
            #     "95054",
            #     "",  # zone
            # )

        if theUCP is None:
            #  we don't have a UCP?
            raise Exception("The System is not ready.")

        ucp_model = theUCP["model"]
        if "HC" in ucp_model:
            raise Exception("Adding storage system to model UCP HC is not supported.")
        if "RS" in ucp_model:
            raise Exception("Adding storage system to model UCP RS is not supported.")

        ucp_name = theUCP["name"]
        self.logger.writeInfo("ucp_name={}", ucp_name)
        self.logger.writeInfo("ucp_serial={}", ucp_serial)

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
            # ucpManager = UcpManager(
            #     self.management_address,
            #     self.management_username,
            #     self.management_password)
            # ucpManager.serial = self.serial

            # attach ss to this UCP
            self.logger.writeDebug("20230523 isInUCP={}, do attachSystemToUCP", isInUCP)
            response = self.attachSystemToUCP(
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
                self.api_token,
            )
            # theUCP = ucpManager.getUcpSystem(ucp_serial)

            # raise Exception("WIP3, continue here for add ss to isp")

            self.logger.writeDebug("20230523 username={}", username)
            # self.logger.writeDebug('20230523 password={}', password)
            self.logger.writeDebug("20230523 storage.address={}", location)
            self.logger.writeDebug("20230523 storage.serial={}", self.serial)
            self.logger.writeDebug("20230523 ucp_name={}", ucp_name)
            self.logger.writeDebug("20230523 outOfBand={}", True)
            self.logger.writeDebug("20230523 pumaGatewayAddress={}", pumaGatewayAddress)
            body = {
                "username": username,
                "password": password,
                "managementAddress": location,
                "serialNumber": self.serial,
                "ucpSystem": ucp_name,
                # 2.4 MT
                # "outOfBand": True,
                "gatewayAddress": pumaGatewayAddress,
            }
            # self.logger.writeInfo('body={}', body)

            # addStorageSystem (onboard, first to ISP then UCP)
            # a2.4 MT addStorageSystem
            urlPath = "v2/storage/devices"
            urlPath = "v3/storage/devices"

            url = self.getUrl(urlPath)
            self.logger.writeDebug("20240504 url={}", url)
            headers = self.getAuthToken()
            headers["Content-Type"] = "application/json"
            headers["Accept"] = "application/json"
            headers["PartnerId"] = "apiadmin"
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
            return self.formatStorageSystem(system)

        if response.ok:

            if system is None or True:
                resJson = response.json()
                self.logger.writeInfo("response={}", resJson)
                resourceId = resJson["data"].get("resourceId")
                self.logger.writeInfo("resourceId={}", resourceId)
                taskId = response.json()["data"].get("taskId")
                self.logger.writeInfo("taskId={}", taskId)
                self.checkTaskStatus(taskId)
                time.sleep(5)
                # system = self.checkAndGetStorageInfoByResourceId(resourceId)
                system = self.waitForUCPinSS(ucp_serial)

            self.logger.writeInfo("system={}", system)

            return self.formatStorageSystem(system)
        else:
            self.logger.writeInfo("response err={}", response.json())
            jsonObj = response.json()
            raise Exception(jsonObj["error"]["messages"])

    def attachSystemToUCP(
        self,
        ucp_name,
    ):

        funcName = "UcpManager:attachSystemToUCP"
        self.logger.writeEnterSDK(funcName)

        systems = self.getAllISPStorageSystems()

        # self.logger.writeDebug('systems={}', systems)
        self.logger.writeDebug("self.serial={}", self.serial)
        self.logger.writeDebug("20230523 ucp_name={}", ucp_name)

        system = None
        resourceId = None
        for x in systems:
            self.logger.writeInfo(int(x["serialNumber"]))
            self.logger.writeInfo(int(x["serialNumber"]) == self.serial)

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
        # self.logger.writeParam('headers={}', headers)

        urlPath = "v2/systems/{0}/device/{1}".format(resourceIdUCP, resourceId)
        url = self.getUrl(urlPath)
        self.logger.writeParam("20230523 url={}", url)
        self.logger.writeInfo("system={}", resourceId)
        self.logger.writeInfo("ucp_name={}", ucp_name)
        self.logger.writeInfo("ucp_resource_id={}", resourceIdUCP)

        response = requests.patch(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        # self.logger.writeDebug('20230523 response={}', response)

        if response.ok:
            resJson = response.json()
            self.logger.writeInfo("response={}", resJson)
            resourceId = resJson["data"].get("resourceId")
            self.logger.writeInfo("resourceId={}", resourceId)
            taskId = response.json()["data"].get("taskId")
            self.logger.writeInfo("taskId={}", taskId)
            self.checkTaskStatus(taskId)
            # it is "REFRESHING"
            time.sleep(5)
            self.logger.writeExitSDK(funcName)
            return response
        # elif "HIJSONFAULT" in response.headers:
        #     self.logger.writeInfo("HIJSONFAULT response={}", response)
        #     Utils.raiseException(self.sessionId, response)
        else:
            self.logger.writeInfo("Unknown Exception response={}", response.json())
            self.throwException(response)

    # a2.4 MT support registerPartner
    def registerPartner(self):
        funcName = "UcpManager:registerPartner"
        self.logger.writeEnterSDK(funcName)

        urlPath = "v3/register/partner"
        url = self.getUrl(urlPath)
        self.logger.writeParam("url={}", url)

        headers = self.getAuthToken()
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"
        body = {
            "name": "partnerName",
            "partnerId": "apiadmin",
            "description": "partnerDescription",
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=body,
                verify=self.shouldVerifySslCertification,
            )
            if response.ok:
                self.logger.writeExitSDK(funcName)
            else:
                self.logger.writeDebug("failed response={}", response)
        except (ValueError, TypeError):
            self.logger.writeDebug("registerPartner already")
        except Exception as ex:
            self.logger.writeDebug("type of exception={}", type(ex))
            self.logger.writeDebug("registerPartner already")

    # a2.4 MT support registerSubscriber
    def registerSubscriber(self):
        funcName = "UcpManager:registerSubscriber"
        self.logger.writeEnterSDK(funcName)

        urlPath = "v3/register/subscriber"
        url = self.getUrl(urlPath)
        self.logger.writeParam("url={}", url)

        headers = self.getAuthToken()
        headers["Content-Type"] = "application/json"
        headers["Accept"] = "application/json"
        body = {
            "name": "partnerName",
            "partnerId": self.partnerId,
            "subscriberId": self.subscriberId,
            "softLimit": "80",
            "hardLimit": "90",
            "quotaLimit": "90",
            "description": "partnerDescription",
        }

        try:
            response = requests.post(
                url,
                headers=headers,
                json=body,
                verify=self.shouldVerifySslCertification,
            )
            if response.ok:
                self.logger.writeExitSDK(funcName)
            else:
                self.logger.writeDebug("failed response={}", response)
        except (ValueError, TypeError):
            self.logger.writeDebug("registerSubscriber already")

    # def findStorageSystemMT(self, storage_serial):
    #     funcName = "UcpManager:findStorageSystemMT"
    #     self.logger.writeEnterSDK(funcName)

    #     urlPath = "v3/storage"
    #     url = self.getUrl(urlPath)
    #     self.logger.writeParam("url={}", url)

    #     headers = self.getAuthToken()
    #     headers["PartnerId"] = "apiadmin"
    #     response = requests.get(
    #         url, headers=headers, verify=self.shouldVerifySslCertification
    #     )
    #     if response.ok:
    #         self.logger.writeDebug("response={}", response)
    #         authResponse = response.json()
    #         self.logger.writeDebug("authResponse={}", authResponse)

    #         for ss in authResponse:
    #             storage = ss.get("storage", None)
    #             self.logger.writeDebug("1061 storage={}", storage)
    #             if storage:
    #                 resourceId = storage.get("resourceId", "")
    #                 ucpSystems = storage.get("ucpSystems", None)
    #                 self.logger.writeDebug("1065 resourceId={}", resourceId)
    #                 self.logger.writeDebug("ucpSystems={}", ucpSystems)
    #                 #  its ucp serial not ucp name here
    #                 for ucpSerial in ucpSystems:
    #                     if ucpSerial == CommonConstants.UCP_SERIAL:
    #                         return resourceId

    #         self.logger.writeExitSDK(funcName)
    #         return ""
    #     else:
    #         self.throwException(response)

    def removeStorageSystem_24_notworking(self, storage_serial, ucp_serial):
        funcName = "UcpManager:removeStorageSystem_24_notworking"
        self.logger.writeEnterSDK(funcName)

        self.serial = storage_serial
        self.logger.writeDebug("storage_serial={}", storage_serial)

        # get SS with self.serial of the SS
        # keep getting it until the ucp_serial is not found

        # removeStorageDevice
        self.logger.writeInfo("2.4 removeStorageDevice")

        #  not able to use findStorageSystemMT,
        #  since /v3/storage is not working properly,
        #  at times it does not return all the onboarded ss,
        #  so we will use v2 to get storage_resourceId

        #  find the storage_serial in v3 get SS
        # storage_resourceId = self.findStorageSystemMT(storage_serial)

        #  if ss not in any ucp, this will return NONE
        storage_resourceId, unused = self.getStorageSystemResourceId()
        if storage_resourceId is None:
            self.logger.writeInfo(
                "1102 Idempotent, {} is not in the system, assume it is already deleted.",
                storage_serial,
            )
            return

        mcpResourceId = self.getUcpSystemResourceIdByName(CommonConstants.UCP_NAME)

        headers = self.getAuthToken()
        # self.logger.writeParam('headers={}', headers)

        self.logger.writeDebug("ucp_serial={}", ucp_serial)
        self.logger.writeDebug("storage_resourceId={}", storage_resourceId)
        self.logger.writeDebug("mcpResourceId={}", mcpResourceId)

        # a2.4 20240504 MT removeStorageDevice
        # in 2.3, it supports ss in many ucp
        # in 2.4, only one, so we just delete v3 storage here
        #  need ucp and storage resourceID to delete

        #  this is not working, we get
        #  "message":"Storage not registered with partner"
        #  we also see v3/storage is not working
        #  we have use v2/to delete
        urlPath = "v3/storage/{0}?isDelete=true&ucpSystemId={1}".format(
            storage_resourceId, mcpResourceId
        )
        url = self.getUrl(urlPath)
        self.logger.writeParam("url={}", url)

        # raise Exception("WIP")

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
        else:
            self.logger.writeInfo("Unknown Exception response={}", response.json())
            self.throwException(response)

    def removeStorageSystem23(self, storage_serial, ucp_serial):
        funcName = "UcpManager:removeStorageSystem23"
        self.logger.writeEnterSDK(funcName)

        self.serial = storage_serial

        if ucp_serial is not None:
            # detach from UCP
            if not self.removeStorageSystemFromUCP(ucp_serial):
                # sng,a2.4 already deleted
                self.logger.writeInfo(
                    "Idempotent, Storage system is not in the system, assume it is already deleted."
                )
                return True

        # get SS with self.serial of the SS
        # keep getting it until the ucp_serial is not found
        isInUCP = True
        attached = True
        while isInUCP:
            #  if ss not in any ucp, this will return NONE
            system = self.getStorageSystem()
            if system is None:
                attached = False
                isInUCP = False
                break
            ucps = system["ucpSystems"]
            if ucp_serial not in ucps:
                isInUCP = False
                if len(ucps) == 0:
                    #  this storage is no longer attached to any UCPs
                    #  we can remove it from ISP also
                    attached = False
            self.logger.writeInfo("Storage system is updating ...")

        if attached:
            self.logger.writeInfo(
                "Storage system is still attached to UCP, no removeStorageDevice"
            )
            return

        # removeStorageDevice
        self.logger.writeInfo(
            "Storage system is no lonager attached to any UCPs anymore, removeStorageDevice"
        )
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
        else:
            self.logger.writeInfo("Unknown Exception response={}", response.json())
            self.throwException(response)

    def getUcpSerialForTheStorageSerial(self, storage_serial):

        all_ucp_systems = self.getAllUcpSystem()
        self.logger.writeDebug("all_ucp_suystems={}", all_ucp_systems)

        for ucp in all_ucp_systems:
            if ucp.get("name").startswith(("Storage_System", "REMOTE_STORAGE_SYSTEM_")):
                storage_devices = ucp.get("storageDevices")
                for s in storage_devices:
                    sn = s.get("serialNumber")
                    if str(sn) == str(storage_serial):
                        ucp_systems = s.get("ucpSystems")
                        return ucp_systems

        return None

    # 2.4 MT removeStorageSystem
    # RKD : the function argument ucp_serial is not needed, it finds the ucp serial based on the storage serial number
    def removeStorageSystem(self, storage_serial, ucp_serial):
        funcName = "UcpManager:removeStorageSystem"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeDebug("storage_serial={}", storage_serial)

        self.logger.writeDebug("ucp_serial={}", ucp_serial)
        ucp_serial_list = self.getUcpSerialForTheStorageSerial(storage_serial)
        if ucp_serial_list is None:
            raise Exception(
                f"Could not find UAI gateway for storage serial {storage_serial}."
            )
        ucp_serial = ucp_serial_list[0]
        self.logger.writeDebug("RD ucp_serial={}", ucp_serial)
        self.serial = storage_serial

        if ucp_serial is not None:
            # detach from UCP
            if not self.removeStorageSystemFromUCP(ucp_serial):
                # sng,a2.4 already deleted
                self.logger.writeInfo(
                    "Idempotent, Storage system is not in the system, assume it is already deleted."
                )
                return True

        # get SS with self.serial of the SS
        # keep getting it until the ucp_serial is not found
        isInUCP = True
        attached = True
        while isInUCP:
            #  if ss not in any ucp, this will return NONE
            system = self.getStorageSystem()
            if system is None:
                attached = False
                isInUCP = False
                break
            ucps = system["ucpSystems"]
            if ucp_serial not in ucps:
                isInUCP = False
                if len(ucps) == 0:
                    #  this storage is no longer attached to any UCPs
                    #  we can remove it from ISP also
                    attached = False
            self.logger.writeInfo("Storage system is updating ...")

        if attached:
            self.logger.writeInfo(
                "Not expected, Storage system is still attached to UCP, no removeStorageDevice"
            )
            return

        # removeStorageDevice
        self.logger.writeInfo(
            "Storage system is no lonager attached to any UCPs anymore, removeStorageDevice"
        )
        resourceId = self.getStorageSystemResourceIdInISP()

        headers = self.getAuthToken()
        # self.logger.writeParam('headers={}', headers)

        #  we need to untag then v2 delete
        try:
            self.untag()
        except Exception as e:
            #  ignore exception from untag for now
            self.logger.writeDebug("1256 Exception={}", e)

        self.logger.writeEnterSDK(funcName)

        #  skip delete from isp for now, takes too long

        urlPath = "v2/storage/devices/{0}".format(resourceId)
        url = self.getUrl(urlPath)
        self.logger.writeParam("1396 del ss from isp, url={}", url)
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
        else:
            self.logger.writeInfo("Unknown Exception response={}", response.json())
            self.throwException(response)

        self.logger.writeEnterSDK(funcName)

        return

        # #  we have untag it?
        # urlPath = "v3/storage/{0}?isDelete=true&ucpSystemId={1}".format(
        #     storage_resourceId, mcpResourceId
        # )
        # url = self.getUrl(urlPath)
        # self.logger.writeParam("url={}", url)

        # # raise Exception("WIP")

        # response = requests.delete(
        #     url, headers=headers, verify=self.shouldVerifySslCertification
        # )
        # if response.ok:
        #     resJson = response.json()
        #     self.logger.writeInfo("response={}", resJson)
        #     resourceId = resJson["data"].get("resourceId")
        #     self.logger.writeInfo("resourceId={}", resourceId)
        #     taskId = response.json()["data"].get("taskId")
        #     self.logger.writeInfo("taskId={}", taskId)
        #     self.checkTaskStatus(taskId)
        #     time.sleep(5)
        # else:
        #     self.logger.writeInfo("Unknown Exception response={}", response.json())
        #     self.throwException(response)

    def removeStorageSystemFromUCP(self, ucp_serial):
        funcName = "UcpManager:removeStorageSystemFromUCP"
        self.logger.writeEnterSDK(funcName)
        systems = self.getAllStorageSystems()

        self.logger.writeDebug("systems={}", systems)

        system = None
        for x in systems:
            self.logger.writeInfo(int(x["serialNumber"]))
            self.logger.writeInfo(self.serial)
            self.logger.writeInfo(int(x["serialNumber"]) == self.serial)

            if str(x["serialNumber"]) == str(self.serial):
                system = x
                break

        if system is None:
            self.logger.writeDebug("removeStorageSystemFromUCP, system is None")
            # raise Exception("The storage {} is not found.".format(self.serial))
            # idempotent
            self.logger.writeExitSDK(funcName)
            return False

        resourceId = str(system.get("resourceId"))

        # ensure the ucp is in the ss
        ucps = system.get("ucpSystems", None)
        self.logger.writeInfo("ensure the ucp is in the ss")
        self.logger.writeDebug("ucps={}", ucps)
        self.logger.writeDebug("ucp_serial={}", ucp_serial)
        if ucps is None or ucp_serial not in ucps:
            raise Exception("The storage system is not attached to the UCP.")

        # get the ucp resourceId from ucp
        ucpManager = UcpManager(
            self.management_address,
            self.management_username,
            self.management_password,
            self.api_token,
        )
        theUCP = ucpManager.getUcpSystem(ucp_serial)
        if theUCP is None:
            raise Exception("The System is not found")
        resourceIdUCP = theUCP.get("resourceId")

        # 2.4 MT removeStorageSystemFromUCP
        # urlPath = "v2/systems/{0}/device/{1}".format(resourceIdUCP, resourceId)
        urlPath = "v3/storage/{0}?ucpSystemId={1}&isDelete=true".format(
            resourceId, resourceIdUCP
        )
        url = self.getUrl(urlPath)

        self.logger.writeParam("url={}", url)
        self.logger.writeInfo("resourceId={}", resourceId)
        self.logger.writeInfo("ucp_resource_id={}", resourceIdUCP)

        headers = self.getAuthToken()
        # headers["PartnerId"] = self.partnerId
        # if self.subscriberId:
        #     headers["subscriberId"] = self.subscriberId
        response = requests.delete(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeDebug("0608 response={}", response)
        if response.ok:
            resJson = response.json()
            self.logger.writeDebug("response={}", resJson)
            resourceId = resJson["data"].get("resourceId")
            self.logger.writeDebug("resourceId={}", resourceId)
            taskId = response.json()["data"].get("taskId")
            self.logger.writeDebug("taskId={}", taskId)
            self.checkTaskStatus(taskId)
            time.sleep(5)
            self.logger.writeExitSDK(funcName)
            return True
        else:
            self.logger.writeInfo("Unknown Exception response={}", response.json())
            self.throwException(response)

    def getAllStorageSystems(self):
        funcName = "UcpManager:getAllStorageSystems"
        self.logger.writeEnterSDK(funcName)

        # get storage in each UCP
        urlPath = "v2/storage/devices"
        url = self.getUrl(urlPath)
        self.logger.writeDebug("url={}", url)

        ucp_systems = self.getAllUcpSystem()
        self.logger.writeDebug(
            "getAllStorageSystems, loop thru each ucp and get list of storages"
        )

        storage_systems = []
        for ucp in ucp_systems:
            sn = str(ucp.get("serialNumber"))
            self.logger.writeDebug(sn)
            body = {"ucpSystem": sn}
            self.logger.writeDebug("body={}", body)
            headers = self.getAuthToken()

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
            #     Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)

        self.logger.writeExitSDK(funcName)
        return storage_systems

    def isOnboarding(self):
        funcName = "UcpManager:isOnboarding"
        self.logger.writeEnterSDK(funcName)

        systems = self.getAllStorageSystems()
        system = None
        for x in systems:
            if str(x["serialNumber"]) == str(self.serial):
                system = x
                break

        hs = ""
        self.logger.writeDebug("system={}", system)
        if system is not None:
            hs = system["healthStatus"]

        self.logger.writeDebug("healthStatus={}", hs)
        self.logger.writeExitSDK(funcName)
        return hs == "ONBOARDING"

    def getStorageSystem(self, refresh=False):
        """
        docstring
        """
        funcName = "UcpManager:getStorageSystem"
        self.logger.writeEnterSDK(funcName)

        systems = self.fetchStorageSystems()
        self.logger.writeDebug("1344 systems={}", systems)

        system = None
        for x in systems:
            self.logger.writeDebug(int(x["serialNumber"]))
            self.logger.writeDebug(self.serial)
            if str(x["serialNumber"]) == str(self.serial):
                system = x
                break

        self.logger.writeDebug("zsystem={}", system)

        systems_all = self.fetchStorageSystems(system, refresh)
        self.logger.writeDebug("1344 system={}", systems_all)

        if refresh is True:
            result = self.formatStorageSystem(systems_all)
        else:
            for x in systems_all:
                self.logger.writeDebug(int(x["serialNumber"]))
                self.logger.writeDebug(self.serial)
                if str(x["serialNumber"]) == str(self.serial):
                    system = x
                    break
            result = self.formatStorageSystem(system)

        self.logger.writeExitSDK(funcName)
        return result

    @staticmethod
    def formatStorageSystem(storageSystem):
        funcName = "UcpManager:StorageSystemManager:formatStorageSystem"
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
        # sng,a2.4 - do not pop it here, other part of code needs it
        # storageSystem.pop('ucpSystems', None)
        storageSystem.pop("username", None)

        UcpManager.logger.writeExitSDK(funcName)
        return storageSystem

    # fetch the SS CRs
    def fetchStorageSystems(self, system=None, refresh=False):
        funcName = "UcpManager:fetchStorageSystems"
        self.logger.writeEnterSDK(funcName)

        headers = self.getAuthToken()
        urlPath = "v2/storage/devices"
        if system is not None:
            resourceId = system.get("resourceId", None)
            ucp = system.get("ucpSystems")[0]
            urlPath = "v2/storage/devices?ucpSystem={}".format(ucp)
        if refresh is True:
            urlPath = "v2/storage/devices/{}?ucpSystem={}&refresh=true".format(
                resourceId, ucp
            )

        url = self.getUrl(urlPath)
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
            if refresh is True:
                return data
            else:
                storage_systems = data

        # elif "HIJSONFAULT" in response.headers:
        #     Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

        self.logger.writeExitSDK(funcName)
        return storage_systems

    def throwException(self, response):
        self.logger.writeInfo("throwException, response={}", response)
        raise Exception(
            "{0}:{1}".format(response.status_code, response.json().get("error"))
        )

    # wait until the ucp_serial is in the ssfact CR status
    def waitForUCPinSS(self, ucp_serial):
        funcName = "UcpManager:waitForUCPinSS"
        self.logger.writeEnterSDK(funcName)

        self.logger.writeDebug("looking for ucp_serial={}", ucp_serial)
        notFound = True
        while notFound:
            time.sleep(2)
            self.logger.writeInfo("onboarding in progress ...")
            system = self.getStorageSystem()
            self.logger.writeDebug("in 1201 system={}", system)
            ucps = system.get("ucpSystems", None)
            self.logger.writeDebug("in 1201 ucps={}", ucps)
            if ucps is None:
                continue
            # 2.4, we only have one UCP
            # if ucp_serial in ucps:
            #    notFound = False
            break

        self.logger.writeExitSDK(funcName)
        return system

    # a2.4 MT getPorts
    def getPorts(self):
        funcName = "UcpManager:getPorts"
        self.logger.writeEnterSDK(funcName)
        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeDebug("1554 resourceId={}", resourceId)
        self.logger.writeDebug("1554 resourceId={}", self.partnerId)
        self.logger.writeDebug("1554 resourceId={}", self.subscriberId)

        urlPath = "v2/storage/devices/{0}/ports?refresh={1}".format(resourceId, True)
        urlPath = "v3/storage/{0}/ports?refresh=false".format(resourceId)
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        headers["PartnerId"] = self.partnerId
        if self.subscriberId:
            headers["subscriberId"] = self.subscriberId

        self.logger.writeDebug("1554 headers={}", headers)

        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        self.logger.writeExitSDK(funcName)
        if response.ok:
            self.logger.writeInfo("ports={}", response.json())
            return response.json()["data"]
        else:
            self.throwException(response)

    def getStoragePools(self):

        funcName = "UcpManager:getStoragePools"
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
            self.logger.writeInfo("pools={}", response.json())
            return response.json()["data"]

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        # elif "HIJSONFAULT" in response.headers:
        #     Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def convertJournalPoolsData(self, data):
        self.logger.writeInfo("convertJournalPoolsData={}", data)
        tmp_journal_pools = []

        for x in data:
            tmp_journal_pool = {}

            # Using .get() everywhere to handle missing keys safely
            tmp_journal_pool["dataOverflowWatchSeconds"] = x.get(
                "dataOverflowWatchSeconds"
            )
            tmp_journal_pool["isCacheModeEnabled"] = x.get("isCacheModeEnabled")
            tmp_journal_pool["journalId"] = x.get("journalPoolId")  # Used .get()
            tmp_journal_pool["logicalUnitIds"] = x.get("logicalUnitIds")
            tmp_journal_pool["logicalUnitIdsHexFormat"] = x.get(
                "logicalUnitIdsHexFormat"
            )
            tmp_journal_pool["mirrorUnitId"] = x.get("mirrorUnitId")
            tmp_journal_pool["timerType"] = x.get("timerType")
            tmp_journal_pool["totalCapacity"] = x.get("totalCapacity")
            tmp_journal_pool["type"] = x.get("type")

            # Check for optional fields using .get() with default values
            tmp_journal_pool["mpBladeId"] = x.get("mpBladeId", -1)
            tmp_journal_pool["isInflowControlEnabled"] = x.get(
                "isInflowControlEnabled", False
            )
            tmp_journal_pool["usageRate"] = x.get("usageRate", -1)
            tmp_journal_pool["journalStatus"] = x.get("journalStatus", "")

            tmp_journal_pools.append(tmp_journal_pool)

        return tmp_journal_pools

    def getJournalPools(self):
        funcName = "UcpManager:getJournalPools"
        self.logger.writeEnterSDK(funcName)

        #  2.4 MT getJournalPools
        # the ucpSystem here can be anything,
        # but you have to have something else it will not work
        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = "v2/storage/devices/{0}/journalpool?ucpSystem={1}".format(
            resourceId, "UCP-CI-202404"
        )
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.get(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            self.logger.writeInfo("getJournalPools={}", response.json())
            return self.convertJournalPoolsData(response.json()["data"])
        else:
            self.throwException(response)

    def getQuorumDisks(self):

        funcName = "UcpManager:getQuorumDisks"
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
            self.logger.writeInfo("pools={}", response.json())
            return response.json()["data"]
        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        else:
            self.throwException(response)

    def getDynamicPools(self):

        funcName = "UcpManager:getDynamicPools"
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
        else:
            self.throwException(response)

    def getFreeLUList(self):

        funcName = "UcpManager:getFreeLUList"
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
            self.logger.writeInfo("pools={}", response.json())
            return response.json()["data"]
        else:
            self.throwException(response)

    def getStorageSystemResourceId(self):
        """
        docstring
        """

        funcName = "UcpManager:getStorageSystemResourceId"
        self.logger.writeEnterSDK(funcName)

        systems = self.getAllStorageSystems()
        # self.logger.writeDebug('systems={}', systems)

        system = None
        for x in systems:
            self.logger.writeDebug(int(x["serialNumber"]))
            self.logger.writeDebug(self.serial)
            self.logger.writeDebug(int(x["serialNumber"]) == self.serial)

            if str(x["serialNumber"]) == str(self.serial):
                system = x
                break
        if system is None:
            self.logger.writeDebug(
                f"Invalid serial = {self.serial}, please check once and try again."
            )
            raise Exception(
                "Invalid serial = {0}, please check once and try again.".format(
                    self.serial
                )
            )

        ucp = system.get("ucpSystems")[0]
        self.logger.writeExitSDK(funcName)
        return (str(system.get("resourceId")), str(ucp))

    def untag(self):

        funcName = "UcpManager:untag"
        self.logger.writeEnterSDK(funcName)

        mcpResourceId = self.getUcpSystemResourceIdByName(CommonConstants.UCP_NAME)
        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeInfo("mcpResourceId={}", mcpResourceId)
        self.logger.writeInfo("resourceId={}", resourceId)

        urlPath = "v2/storage/devices/{0}/freeVolumes?count={1}&ucpSystem={2}".format(
            resourceId, 100, ucp
        )
        urlPath = "v3/storage/{0}?isDelete=true&ucpSystemId={1}".format(
            resourceId, mcpResourceId
        )

        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.delete(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        if response.ok:
            pass
        else:
            #  ignore exception from untag for now
            self.logger.writeDebug("1724 failed response={}", response)
            # self.throwException(response)

        self.logger.writeExitSDK(funcName)

    #  a2.4 MT WIP tag
    def tag(self):

        funcName = "UcpManager:tag"
        self.logger.writeEnterSDK(funcName)

        mcpResourceId = self.getUcpSystemResourceIdByName(CommonConstants.UCP_NAME)
        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeInfo("mcpResourceId={}", mcpResourceId)
        self.logger.writeInfo("resourceId={}", resourceId)

        urlPath = "v2/storage/devices/{0}/freeVolumes?count={1}&ucpSystem={2}".format(
            resourceId, 100, ucp
        )
        urlPath = "v3/storage/{0}?isDelete=true&ucpSystemId={1}".format(
            resourceId, mcpResourceId
        )

        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.delete(
            url, headers=headers, verify=self.shouldVerifySslCertification
        )
        if response.ok:
            pass
        else:
            #  ignore exception from untag for now
            self.logger.writeDebug("1724 failed response={}", response)
            # self.throwException(response)

        self.logger.writeExitSDK(funcName)
