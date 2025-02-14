import json
import logging
from enum import Enum

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_http_client import (
    HTTPClient as requests,
)


class HtiPairType(Enum):
    UNKNOWN = 0
    SNAPSHOT = 1
    THIN_IMAGE = 2
    SHADOW_IMAGE_L1 = 3
    SHADOW_IMAGE_L2 = 4
    TRUE_COPY = 5
    UNIVERSAL_REPLICATOR = 6
    GLOBAL_ACTIVE_DEVICE = 7

    @classmethod
    def fromValue(cls, value):
        enums = [e for e in cls if e.value == value]
        return enums[0] if enums else None


class LunStatus(Enum):

    UNKNOWN = 0
    NORMAL = 1
    BLOCKED = 2
    PREPARING_QUICKFORMAT = 3
    QUICKFORMAT = 4
    FORMAT = 5
    SHREDDING = 6
    CORRECTION_ACCESS = 7
    CORRECTION_COPY = 8
    REMOVING = 9
    DEFINING = 10
    REGRESSED = 11

    @classmethod
    def fromValue(cls, value):
        enums = [e for e in cls if e.value == value]
        return enums[0] if enums else None


class LunType(Enum):

    SNAPSHOT = 0
    DP = 1
    BASIC = 7

    @classmethod
    def fromValue(cls, value):
        enums = [e for e in cls if e.value == value]
        return enums[0] if enums else None


class PoolStatus(Enum):

    UNKNOWN = 0
    NORMAL = 1
    OVERTHRESHOLD = 2
    SUSPENDED = 3
    FAILURE = 4
    SHRINKING = 5
    RCPY = 6
    REGRESSED = 7
    DETACHED = 8

    @classmethod
    def fromValue(cls, value):
        enums = [e for e in cls if e.value == value]
        return enums[0] if enums else None


class PoolType(Enum):

    UNKNOWN = 0
    HDP = 1
    SNAPSHOT = 2
    HDT = 3
    HTI = 4
    DATAPOOL = 5
    HDT_AF = 6
    PARITYGROUP = 7
    RAIDGROUP = 8
    HRT = 9
    DM = 10

    @classmethod
    def fromValue(cls, value):
        enums = [e for e in cls if e.value == value]
        return enums[0] if enums else None


class HPEPoolType(Enum):

    UNKNOWN = 0
    THP = 1
    FASTSNAP = 2
    HDT = 3
    HTI = 4
    DATAPOOL = 5
    HDT_AF = 6
    PARITYGROUP = 7
    RAIDGROUP = 8
    RTST = 9
    DM = 10

    @classmethod
    def fromValue(cls, value):
        enums = [e for e in cls if e.value == value]
        return enums[0] if enums else None


class ReplicationStatus(Enum):

    UNKNOWN = 0
    COPY = 1
    PAIR = 2
    PSUS = 3
    PSUE = 4
    PDUB = 5
    RCPY = 6
    PFUL = 7
    PFUS = 8
    SSWS = 9

    @classmethod
    def fromValue(cls, value):
        enums = [e for e in cls if e.value == value]
        return enums[0] if enums else None


from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_exceptions import (
    HiException,
)


class HTIManager:
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

    def createHTIPair(
        self,
        lun,
        target_lun,
        dataPool,
        groupName,
        ctgID,
        autoSplit,
        allocateConsistencyGroup,
    ):

        funcName = "hv_htimanager.createHTIPair"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("target_lun={}", target_lun)
        self.logger.writeParam("dataPool={}", dataPool)
        self.logger.writeParam("groupName={}", groupName)
        self.logger.writeParam("ctgID={}", ctgID)
        self.logger.writeParam("autoSplit={}", autoSplit)
        self.logger.writeParam("allocateConsistencyGroup={}", allocateConsistencyGroup)

        if ctgID is not None and ctgID > 0:
            urlPath = "Snapshot/Snapshot/CreateSnapshotPairWithGroupNameAndCTGId"
            url = self.getUrl(urlPath)
            body = {
                "sessionId": self.sessionId,
                "serialNumber": self.serial,
                "pVol": lun,
                "dataPool": dataPool,
                # "groupName": groupName, see SIEAN-85
                "ctgId": ctgID,
                "autoSplit": autoSplit,
            }
            if target_lun is not None:
                body["vVol"] = target_lun

        elif groupName is not None:
            urlPath = "Snapshot/Snapshot/CreateSnapshotPairWithGroupNameAndCTG"
            url = self.getUrl(urlPath)
            body = {
                "sessionId": self.sessionId,
                "serialNumber": self.serial,
                "pVol": lun,
                "dataPool": dataPool,
                "groupName": groupName,
            }

            if target_lun is not None:
                body["vVol"] = target_lun
            if autoSplit is not None:
                body["autoSplit"] = autoSplit
            if allocateConsistencyGroup is not None:
                body["allocateCTG"] = allocateConsistencyGroup
        else:
            urlPath = "Snapshot/Snapshot/CreatePair"
            url = self.getUrl(urlPath)
            body = {
                "sessionId": self.sessionId,
                "serialNumber": self.serial,
                "pVol": lun,
                "vVol": target_lun,
                "dataPool": dataPool,
            }

        response = self.doPost(url, body)

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

    def getHTIPairs(self, lun):
        funcName = "hv_htimanager.getHTIPairs"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)

        urlPath = "Snapshot/Snapshot/GetPairList"
        url = self.getUrl(urlPath)
        body = {"sessionId": self.sessionId, "serial": self.serial, "pVol": lun}

        response = requests.get(
            url, params=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            return []
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def getHTIPair(self, lun, target_lun, mirror_id):
        mess = "mirror_id={0}".format(mirror_id)
        logging.debug(mess)
        if mirror_id is None:
            pairs = [
                pair
                for pair in self.getHTIPairs(lun)
                if str(pair.get("SVol")) == str(target_lun)
            ]
        else:
            pairs = [
                pair
                for pair in self.getHTIPairs(lun)
                if str(pair.get("MirrorId")) == str(mirror_id)
            ]
        return pairs[0] if len(pairs) > 0 else None

    def splitHTIPair(self, lun, target_lun, enable_quick_mode):

        funcName = "hv_htimanager.splitHTIPair"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("target_lun={}", target_lun)
        self.logger.writeParam("enable_quick_mode={}", enable_quick_mode)

        urlPath = "Snapshot/Snapshot/SplitPair"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "vVol": target_lun,
        }

        response = self.doPost(url, body)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            pass
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def splitSnapshotGroup(self, groupName, enableQuickMode=True):

        funcName = "hv_htimanager.splitSnapshotGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("groupName={}", groupName)
        self.logger.writeParam("enableQuickMode={}", enableQuickMode)

        urlPath = "Snapshot/SnapshotGroup/SplitReplicationPairGroupUsingGroupname"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "groupName": groupName,
            "enableQuickMode": enableQuickMode,
        }

        response = self.doPost(url, body)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            pass
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def doPost(self, url, body, returnResponse=True):
        try:
            funcName = "hv_infra:doPost"
            self.logger.writeEnterSDK(funcName)
            self.logger.writeParam("urlPath={}", url)
            self.logger.writeParam("body={}", body)
            response = requests.post(
                url, json=body, verify=self.shouldVerifySslCertification
            )
            self.logger.writeDebug("response={}", response)

            if response.ok:
                self.logger.writeExitSDK(funcName)
                if returnResponse:
                    self.logger.writeDebug("response.json()={}", response.json())
                    return response
                else:
                    return
            elif "HIJSONFAULT" in response.headers:
                ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
            else:
                raise Exception("Unknown error HTTP {0}".format(response.status_code))
        except requests.exceptions.Timeout as t1:
            self.logger.writeException(t1)
            raise Exception(
                " Timeout exception. Perhaps webserivce is not reachable or down ? "
            )
        except requests.exceptions.TooManyRedirects as t2:
            self.logger.writeException(t2)
            raise Exception(
                "Mas retry error. Perhaps webserivce is not reachable or down ?"
            )
        except requests.exceptions.RequestException as e:
            self.logger.writeException(e)
            raise Exception(
                " Connection Error. Perhaps web serivce is not reachable or down ? "
            )

    def doGet(self, url, body, returnJson=True):
        try:
            funcName = "hv_infra:doget"
            self.logger.writeEnterSDK(funcName)
            self.logger.writeParam("url={}", url)
            self.logger.writeParam("body={}", body)
            response = requests.get(
                url, json=body, verify=self.shouldVerifySslCertification
            )
            self.logger.writeDebug("response={}", response)

            if response.ok:
                self.logger.writeExitSDK(funcName)
                if returnJson:
                    self.logger.writeDebug("response.json()={}", response.json())
                    return response
                else:
                    return
            elif "HIJSONFAULT" in response.headers:
                ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
            else:
                raise Exception("Unknown error HTTP {0}".format(response.status_code))
        except requests.exceptions.Timeout as t1:
            self.logger.writeException(t1)
            raise Exception(
                " Timeout exception. Perhaps webserivce is not reachable or down ? "
            )
        except requests.exceptions.TooManyRedirects as t2:
            self.logger.writeException(t2)
            raise Exception(
                "Mas retry error. Perhaps webserivce is not reachable or down ? "
            )
        except requests.exceptions.RequestException as e:
            self.logger.writeException(e)
            raise Exception(
                " Connection Error. Perhaps web serivce is not reachable or down ? "
            )

    def manageSnapshotGroup(self, task, groupName, enableQuickMode=True, dryRun=False):

        funcName = "hv_htimanager.manageSnapshotGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("task={}", task)
        self.logger.writeParam("groupName={}", groupName)
        self.logger.writeParam("enableQuickMode={}", enableQuickMode)

        urlPath = "Snapshot/SnapshotGroup/"
        if task == "split":
            urlPath += "SplitReplicationPairGroupUsingGroupname"
        elif task == "resync":
            urlPath += "ResyncReplicationPairGroupUsingGroupname"
        elif task == "restore":
            urlPath += "RestoreReplicationPairGroupUsingGroupname"
        elif task == "delete":
            urlPath += "DeleteReplicationPairGroupUsingGroupname"
        else:
            raise Exception("SnapshotGroup task not implemented: " + task)

        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "groupName": groupName,
        }

        if task == "split":
            body["enableQuickMode"] = enableQuickMode

        if dryRun:
            self.logger.writeDebug("urlPath={}", urlPath)
            self.logger.writeDebug("body={}", body)
            self.logger.writeDebug("is DRY RUN, exiting")
        else:
            self.doPost(self.getUrl(urlPath), body, False)

        self.logger.writeExitSDK(funcName)
        return

    def deleteConsistencyGroup(self, ctgID, replicationType, dryRun=False):

        funcName = "hv_htimanager.deleteConsistencyGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("ctgID={}", ctgID)
        self.logger.writeParam("replicationType={}", replicationType)

        if dryRun:
            self.logger.writeDebug("is DRY RUN")
        else:
            urlPath = "ConsistencyGroup/Delete"
            body = {
                "sessionId": self.sessionId,
                "serialNumber": self.serial,
                "replicationType": replicationType,
                "ctgID": ctgID,
            }
            self.doPost(urlPath, body)

        self.logger.writeExitSDK(funcName)
        return

    def resyncConsistencyGroup(self, ctgID, replicationType):

        funcName = "hv_htimanager.resyncConsistencyGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("ctgID={}", ctgID)
        self.logger.writeParam("replicationType={}", replicationType)

        urlPath = "ConsistencyGroup/Resync"
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "replicationType": replicationType,
            "ctgID": ctgID,
        }

        self.doPost(urlPath, body)
        self.logger.writeExitSDK(funcName)
        return

    def splitConsistencyGroup(self, ctgID, replicationType, enable_read_write=False):

        funcName = "hv_htimanager.splitConsistencyGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("ctgID={}", ctgID)
        self.logger.writeParam("replicationType={}", replicationType)
        self.logger.writeParam("enable_read_write={}", enable_read_write)

        urlPath = "ConsistencyGroup/Split"
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "replicationType": replicationType,
            "ctgID": ctgID,
        }

        self.doPost(urlPath, body)
        self.logger.writeExitSDK(funcName)
        return

    def splitConsistencyGroup_not_used(self, ctgID, replicationType, enable_read_write):

        funcName = "hv_htimanager.splitConsistencyGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("ctgID={}", ctgID)

        urlPath = "ShadowImage/ShadowImage/SplitShadowImageGroup"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "ctgID": ctgID,
        }

        response = self.doPost(url, body)

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

    def resyncHTIPair(self, lun, target_lun, enable_quick_mode):

        funcName = "hv_htimanager.resyncHTIPair"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("target_lun={}", target_lun)
        self.logger.writeParam("enable_quick_mode={}", enable_quick_mode)

        urlPath = "Snapshot/Snapshot/ResyncPair"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "vVol": target_lun,
        }

        response = self.doPost(url, body)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            pass
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def restoreHTIPair(self, lun, target_lun, enable_quick_mode):

        funcName = "hv_htimanager.restoreHTIPair"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("target_lun={}", target_lun)
        self.logger.writeParam("enable_quick_mode={}", enable_quick_mode)

        urlPath = "Snapshot/Snapshot/RestorePair"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "vVol": target_lun,
        }

        response = self.doPost(url, body)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            pass
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def deleteHTIPair(self, lun, target_lun, delete_target_lun):

        funcName = "hv_htimanager.deleteHTIPair"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("target_lun={}", target_lun)
        self.logger.writeParam("delete_target_lun={}", delete_target_lun)

        urlPath = "Snapshot/Snapshot/DeletePair"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "deleteTargetLun": delete_target_lun,
            "vVol": target_lun,
        }

        response = self.doPost(url, body)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            pass
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def createVVOL(self, lun, target_lun):

        funcName = "hv_htimanager.createVVOL"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("target_lun={}", target_lun)

        urlPath = "Snapshot/Snapshot/CreateVVol"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "vVol": target_lun,
        }

        response = self.doPost(url, body)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            pass
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def createVVOLAutoNum(self, lun):

        funcName = "hv_htimanager.createVVOLAutoNum"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)

        urlPath = "Snapshot/Snapshot/CreateVVolWithAutoVVolNumberGeneration"
        url = self.getUrl(urlPath)
        body = {"sessionId": self.sessionId, "serialNumber": self.serial, "pVol": lun}

        response = self.doPost(url, body)
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
