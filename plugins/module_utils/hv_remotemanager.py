import json

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_http_client import (
    HTTPClient as requests,
)

try:
    from enum import Enum

    class REPLICATION_PAIR_TYPE(Enum):

        UNKNOWN = 0
        SS = 1
        THIN_IMAGE = 2
        SI_L1 = 3
        SI_L2 = 4
        TRUE_COPY = 5
        UR = 6
        GAD = 7

        @classmethod
        def fromValue(cls, value):
            enums = [e for e in cls if e.value == value]
            return enums[0] if enums else None

    class FENCE_LEVEL(Enum):

        UNKNOWN = 0
        NEVER = 1
        DATA = 2
        STATUS = 3

        @classmethod
        def fromValue(cls, value):
            enums = [e for e in cls if e.value == value]
            return enums[0] if enums else None

except ImportError:

    # Output expected ImportErrors.

    pass

try:
    from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_htimanager import (
        ReplicationStatus,
    )

    HAS_REPLICATION_STATUS = True
except ImportError:
    HAS_REPLICATION_STATUS = False

try:
    from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_htimanager import (
        HtiPairType,
    )

    HAS_HTI_PAIR_TYPE = True
except ImportError:
    HAS_HTI_PAIR_TYPE = False

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_exceptions import (
    HiException,
)


class RemoteManager:

    def __init__(
        self,
        serial,
        webServiceIp,
        webServicePort,
        sessionId,
    ):
        self.serial = serial
        self.sessionId = sessionId
        self.webServiceIp = webServiceIp
        self.webServicePort = webServicePort
        self.basedUrl = "https://{0}:{1}".format(webServiceIp, webServicePort)
        self.shouldVerifySslCertification = False
        self.logger = Log()

    def formatPair(self, pair):
        if pair.get("PVolSerial") is not None:
            if str(pair["PVolSerial"]) == str(-1):
                del pair["PVolSerial"]
        if pair.get("ConsistencyGroupId") is not None:
            if str(pair["ConsistencyGroupId"]) == str(-1):
                del pair["ConsistencyGroupId"]
        if pair.get("DataPoolId") is not None:
            pair["PoolId"] = pair["DataPoolId"]
            del pair["DataPoolId"]
        if pair.get("Type") is not None:
            pair["Type"] = REPLICATION_PAIR_TYPE.fromValue(pair.get("Type", 0)).name
            self.logger.writeDebug(pair["Type"])
        if HAS_REPLICATION_STATUS and pair.get("Status") is not None:
            pair["Status"] = ReplicationStatus.fromValue(pair.get("Status", 0)).name
        if pair.get("FenceLevel") is not None:
            pair["FenceLevel"] = FENCE_LEVEL.fromValue(pair.get("FenceLevel", 0)).name
            if pair["FenceLevel"] == "UNKNOWN":
                pair["FenceLevel"] = "NEVER"
        if pair.get("Fence_Level") is not None:
            pair["FenceLevel"] = FENCE_LEVEL.fromValue(pair.get("Fence_Level", 0)).name
            if pair["FenceLevel"] == "UNKNOWN":
                pair["FenceLevel"] = "NEVER"

    def formatPairHTI(self, pair):
        self.logger.writeDebug("Entered formatHTI")
        if HAS_REPLICATION_STATUS:
            pair["Status"] = ReplicationStatus.fromValue(pair.get("Status", 0)).name
        if HAS_HTI_PAIR_TYPE:
            pair["Type"] = HtiPairType.fromValue(pair.get("Type", 0)).name
        if pair.get("FenceLevel") is not None:
            del pair["FenceLevel"]
        if pair.get("ManagementPoolId") is not None:
            del pair["ManagementPoolId"]
        if pair.get("JournalPoolId") is not None:
            del pair["JournalPoolId"]
        if pair.get("ReplicationPoolId") is not None:
            del pair["ReplicationPoolId"]
        if pair.get("SplitTime") is not None:
            del pair["SplitTime"]
        if pair.get("PairName") is not None:
            del pair["PairName"]
        if pair.get("SVolSerial") is not None:
            del pair["SVolSerial"]
        pvol = pair["PVol"]
        if pvol is not None and pvol < 0:
            del pair["PVol"]
            del pair["HexPVOL"]
        svol = pair["SVol"]
        if svol is not None and svol < 0:
            del pair["SVol"]
            del pair["HexSVOL"]
        cpid = pair["ConsistencyGroupId"]
        if cpid is not None and cpid < 0:
            del pair["ConsistencyGroupId"]

    def formatPairTC(self, pair):
        self.formatPair(pair)
        newpair = {}
        if pair.get("Type") is not None:
            newpair["Type"] = pair["Type"]
        if pair["Type"] == "TRUE_COPY" or pair["Type"] == "UR" or pair["Type"] == "GAD":
            if pair.get("Fence_Level") is not None and pair["Fence_Level"] != "UNKNOWN":
                newpair["FenceLevel"] = pair["Fence_Level"]
        if pair.get("FenceLevel") is not None and pair["FenceLevel"] != "UNKNOWN":
            newpair["FenceLevel"] = pair["FenceLevel"]
        if pair.get("PVol") is not None:
            newpair["PVol"] = pair["PVol"]
        if pair.get("HexPVOL") is not None:
            newpair["HexPVOL"] = pair["HexPVOL"]
        if pair.get("HexSVOL") is not None:
            newpair["HexSVOL"] = pair["HexSVOL"]
        if pair.get("SVol") is not None:
            if str(pair["SVol"]) == str(-1):
                newpair["SVol"] = ""
            else:
                newpair["SVol"] = pair["SVol"]
        if str(pair["Serial"]) != str(-1):
            newpair["PVolSerial"] = pair["Serial"]
        if str(pair["SVolSerial"]) != str(-1):
            newpair["SVolSerial"] = pair["SVolSerial"]
        if pair.get("Status") is not None:
            newpair["Status"] = pair["Status"]
        if pair.get("ConsistencyGroupId") is not None:
            newpair["ConsistencyGroupId"] = pair["ConsistencyGroupId"]
        return newpair

    def formatPairUR(self, pair):
        self.formatPair(pair)
        newpair = {}

        if pair.get("JournalPoolId") is not None:
            newpair["PrimaryJournalPoolId"] = pair["JournalPoolId"]

        if pair.get("ConsistencyGroupId") is not None:
            newpair["ConsistencyGroupId"] = pair["ConsistencyGroupId"]
        if pair.get("MirrorId") is not None:
            newpair["MirrorId"] = pair["MirrorId"]

        if pair.get("Type") is not None:
            newpair["Type"] = pair["Type"]
        if pair.get("PVol") is not None:
            newpair["PVol"] = pair["PVol"]
        if pair.get("SVol") is not None:
            newpair["SVol"] = pair["SVol"]
        if pair.get("HexPVOL") is not None:
            newpair["HexPVOL"] = pair["HexPVOL"]
        if pair.get("HexSVOL") is not None:
            newpair["HexSVOL"] = pair["HexSVOL"]

        # if str(pair["Serial"]) != str(-1):
        #     newpair["PVolSerial"] = pair["Serial"]
        # if str(pair["SVolSerial"]) != str(-1):
        #     newpair["SVolSerial"] = pair["SVolSerial"]

        if pair.get("Status") is not None:
            newpair["Status"] = pair["Status"]
        return newpair

    def formatGadPair(self, pair):
        # if REPLICATION_PAIR_TYPE:
        #     pair["Status"] = ReplicationStatus.fromValue(pair.get("Status", 0)).name
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

        return pair

    def formatReplicationPair(self, pair):
        pair = self.formatPairTC(pair)
        if pair["Type"] != "TRUE_COPY":
            del pair["FenceLevel"]
        return pair

    def getUrl(self, urlPath):
        return "{0}/HitachiStorageManagementWebServices/{1}".format(
            self.basedUrl, urlPath
        )

    def getTCPairsFromAll(self, rclist, lun):
        if lun is None or lun == -1:
            pairs = [self.formatPairTC(pair) for pair in rclist if pair["Type"] == 5]
        else:
            pairs = [
                self.formatPairTC(pair)
                for pair in rclist
                if pair["Type"] == 5 and str(pair["PVol"]) == str(lun)
            ]
        return pairs

    def formatTCPairs(self, rclist):
        pairs = [self.formatPairTC(pair) for pair in rclist]
        return pairs

    def formatReplicationPairs(self, rclist):
        pairs = [self.formatReplicationPair(pair) for pair in rclist]
        return pairs

    def getURPairsFromAll(self, rclist, lun):
        if lun is None or lun == -1:
            pairs = [self.formatPairUR(pair) for pair in rclist if pair["Type"] == 6]
        else:
            pairs = [
                self.formatPairUR(pair)
                for pair in rclist
                if pair["Type"] == 6 and str(pair["PVol"]) == str(lun)
            ]
        return pairs

    def getURPairByPVol(
        self,
        lun,
        remote_serial,
        target_lun,
    ):
        obj = self.getRemoteClone(lun, remote_serial, None)

        # if type(obj) is not list:
        #     return obj

        if not isinstance(obj, list):
            return obj

        rclist = obj
        pair = [
            pair
            for pair in rclist
            if str(pair["Type"]) == str(6)
            and str(pair["PVol"]) == str(lun)
            and (
                str(pair["SVolSerial"]) == str(remote_serial)
                or str(pair["SVolSerial"]) == str(0)
            )
        ]

        if pair is None or len(pair) == 0:
            pair = {}
            return pair
        else:
            return pair[0]

    # given pvol, svol return UR

    def getURPair(
        self,
        lun,
        remote_serial,
        target_lun,
    ):
        obj = self.getRemoteClone(lun, remote_serial, target_lun)

        # if type(obj) is not list:
        #     return obj
        if not isinstance(obj, list):
            return obj

        rclist = obj
        pair = [
            pair
            for pair in rclist
            if pair["Type"] == 6
            and str(pair["PVol"]) == str(lun)
            and (
                str(pair["SVolSerial"]) == str(remote_serial)
                or str(pair["SVolSerial"]) == str(0)
            )
            and str(pair["SVol"]) == str(target_lun)
        ]
        return pair[0]

    def getRemoteClone(
        self,
        lun,
        remote_serial,
        target_lun,
    ):

        funcName = "hv_remotemanager:getRemoteClone"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("target_lun={}", target_lun)

        url = self.getUrl("TrueCopy/GetRemoteCloneList")

        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "remoteDeviceSerial": remote_serial,
            "remoteSVol": target_lun,
        }

        response = requests.get(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            return []
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    # SIEAN-188
    # looks the GetTrueCopyPairs needs the remoteDeviceSerial input

    def getTrueCopyPair(
        self,
        lun,
        remote_serial,
        target_lun,
    ):
        url = self.getUrl("TrueCopy/GetTrueCopyPairs")

        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "remoteDeviceSerial": remote_serial,
        }

        response = requests.get(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        if response.ok:
            return self.formatTCPairs(response.json())
        elif "HIJSONFAULT" in response.headers:
            return []
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def getTCPairs(
        self,
        lun=-1,
        remote_serial=None,
        target_lun=None,
    ):

        funcName = "hv_remotemanager:getTCPairs"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("target_lun={}", target_lun)

        url = self.getUrl("TrueCopy/GetRemoteCloneList")

        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "remoteDeviceSerial": None,
            "remoteSVol": None,
        }

        body = {"sessionId": self.sessionId, "serialNumber": self.serial}

        response = requests.post(
            url, params=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            pairs = self.getTCPairsFromAll(response, lun)
            return pairs
        elif "HIJSONFAULT" in response.headers:

            # return response.json()

            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def getTrueCopyPairsList(
        self,
        lun=-1,
        remote_serial=None,
        target_lun=None,
    ):

        funcName = "hv_remotemanager:getTrueCopyPairsList"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("target_lun={}", target_lun)

        url = self.getUrl("TrueCopy/GetTrueCopyPairsList")

        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "remoteDeviceSerial": None,
            "remoteSVol": None,
        }

        body = {"sessionId": self.sessionId, "serialNumber": self.serial}

        response = requests.get(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            pairs = self.formatTCPairs(response.json())

            #             pairs = (response.json())

            return pairs
        elif "HIJSONFAULT" in response.headers:

            # return response.json()

            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def getRemoteClones(
        self,
        lun,
        remote_serial,
        target_lun,
    ):

        funcName = "hv_remotemanager:getRemoteClones"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("target_lun={}", target_lun)

        url = self.getUrl("TrueCopy/GetRemoteCloneList")

        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "remoteDeviceSerial": None,
            "remoteSVol": None,
        }

        body = {"sessionId": self.sessionId, "serialNumber": self.serial}

        response = requests.get(
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

    def getSnapshotGroups(self, group_name=None):
        funcName = "hv_remotemanager:getSnapshotGroups"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("group_name={}", group_name)

        url = self.getUrl("ConsistencyGroup/SnapshotGroupAll")

        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "snapshotGroupName": group_name,
        }
        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:

            # pairs = self.formatTCPairs(response.json())

            pairs = response.json()
            return pairs
        elif "HIJSONFAULT" in response.headers:

            # return response.json()

            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def getConsistencyPairGroups(self, consistency_group_id=None):
        funcName = "hv_remotemanager:getConsistencyPairGroups"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("consistency_group_id={}", consistency_group_id)

        url = self.getUrl("ConsistencyGroup/GetReplicationPairGroup")

        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "ctgId": consistency_group_id,
        }
        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            pairs = self.formatReplicationPairs(response.json())

            # pairs = response.json()

            return pairs
        elif "HIJSONFAULT" in response.headers:

            # return response.json()

            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def createUR(
        self,
        lun,
        remote_serial,
        target_lun,
        ctgId=None,
        allocateCtg=False,
        copyPace=3,
        enable_delta_resync=False,
        lun_journal_id=None,
        target_lun_journal_id=None,
    ):

        funcName = "hv_remotemanager:createUR"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("target_lun={}", target_lun)

        url = self.getUrl("TrueCopy/CreateUniversalReplicatorPair")
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "remoteDeviceSerial": remote_serial,
            "pvolJournalPool": lun_journal_id,
            "svolJournalPool": target_lun_journal_id,
            "allocateCtg": allocateCtg,
            "enableDeltaResync": enable_delta_resync,
        }

        if target_lun is not None:
            body["remoteSVol"] = target_lun

        if ctgId is not None:
            body["ctgID"] = ctgId

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return "OK"
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def createUR_tpi(
        self,
        lun,
        remote_serial,
        target_pool_id,
        ctgId=None,
        allocateCtg=False,
        copyPace=3,
        enable_delta_resync=False,
        lun_journal_id=None,
        target_lun_journal_id=None,
    ):

        funcName = "hv_remotemanager:createUR_tpi"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("target_pool_id={}", target_pool_id)

        url = self.getUrl("TrueCopy/CreateUniversalReplicatorPairWithRemotePoolId")
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "remoteDeviceSerial": remote_serial,
            "pvolJournalPool": lun_journal_id,
            "svolJournalPool": target_lun_journal_id,
            "allocateCtg": allocateCtg,
            "enableDeltaResync": enable_delta_resync,
        }

        if ctgId is not None:
            body["ctgID"] = ctgId
        else:
            body["ctgID"] = -1

        if target_pool_id is not None:
            body["remotePoolId"] = target_pool_id

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:

            return "OK"
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def createTC(
        self,
        lun,
        remote_serial,
        target_lun,
        fence_level,
        ctgId=None,
        allocateCtg=False,
        copyPace=3,
    ):

        funcName = "hv_remotemanager:createTC"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("target_lun={}", target_lun)

        url = self.getUrl("TrueCopy/CreateRemoteClone")

        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "fenceLevel": fence_level or 1,
            "pVol": lun,
        }

        if ctgId is not None:
            url += "WithConsistencyGroupId"
            body["ctgId"] = ctgId

        if remote_serial is not None:
            body["remoteDeviceSerial"] = remote_serial
        if target_lun is not None:
            body["remoteSVol"] = target_lun
        if copyPace is not None:
            body["copyPace"] = copyPace
        if allocateCtg is not None:
            body["allocateCTG"] = allocateCtg
        if fence_level is not None:
            body["fenceLevel"] = fence_level

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

    def createTC_tpi(
        self,
        lun,
        remote_serial,
        target_pool_id,
        fence_level,
        ctgId=None,
        allocateCtg=False,
        copyPace=3,
    ):

        funcName = "hv_remotemanager:createTC_tpi"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("target_pool_id={}", target_pool_id)

        url = self.getUrl("TrueCopy/CreateRemoteCloneWithRemotePoolId")
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "fenceLevel": fence_level or 1,
            "pVol": lun,
        }

        if ctgId is not None:
            url = self.getUrl("TrueCopy/CreateRemoteCloneWithCTGIdAndRemotePoolId")
            body["ctgId"] = ctgId

        if target_pool_id is not None:
            body["remotePoolId"] = target_pool_id
        if remote_serial is not None:
            body["remoteDeviceSerial"] = remote_serial
        if copyPace is not None:
            body["copyPace"] = copyPace
        if allocateCtg is not None:
            body["allocateCTG"] = allocateCtg
        if fence_level is not None:
            body["fenceLevel"] = fence_level

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

    def splitTC(
        self,
        lun,
        remote_serial,
        target_lun,
        enable_read_write,
    ):

        funcName = "hv_remotemanager:splitTC"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("target_lun={}", target_lun)

        url = self.getUrl("TrueCopy/SplitRemoteClone")
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "enableReadWrite": enable_read_write,
            "remoteDeviceSerial": remote_serial,
        }

        if target_lun is not None:
            body["remoteSVol"] = target_lun

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return "OK"
        elif "HIJSONFAULT" in response.headers:

            jfault = json.loads(response.headers["HIJSONFAULT"])
            msg = jfault["ErrorMessage"]
            if "The pair is already split" in msg:
                return None
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def splitUR(
        self,
        lun,
        remote_serial,
        target_lun,
        enable_read_write,
    ):

        funcName = "hv_remotemanager:splitUR"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("target_lun={}", target_lun)

        url = self.getUrl("TrueCopy/SplitURRemoteClone")
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "remoteDeviceSerial": remote_serial,
        }

        if target_lun is not None:
            body["remoteSVol"] = target_lun
        if enable_read_write is not None:
            body["enableReadWrite"] = enable_read_write

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return "OK"
        elif "HIJSONFAULT" in response.headers:

            jfault = json.loads(response.headers["HIJSONFAULT"])
            msg = jfault["ErrorMessage"]
            if "The pair is already split" in msg:
                return None
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def splitRemoteClone(
        self,
        lun,
        remote_serial,
        target_lun,
    ):

        funcName = "hv_remotemanager:splitRemoteClone"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("target_lun={}", target_lun)

        url = self.getUrl("TrueCopy/SplitRemoteClone")
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "remoteDeviceSerial": remote_serial,
            "remoteSVol": target_lun,
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

    def resyncRemoteClone(
        self,
        lun,
        remote_serial,
        target_lun,
    ):

        funcName = "hv_remotemanager:resyncRemoteClone"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("target_lun={}", target_lun)

        url = self.getUrl("TrueCopy/ResyncRemoteClone")
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "remoteDeviceSerial": remote_serial,
            "remoteSVol": target_lun,
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

    def resyncTC(
        self,
        lun,
        remote_serial,
        target_lun,
        copy_pace,
    ):

        funcName = "hv_remotemanager:resyncTC"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("target_lun={}", target_lun)

        url = self.getUrl("TrueCopy/ResyncRemoteClone")
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "copyPace": copy_pace,
            "remoteDeviceSerial": remote_serial,
        }

        if target_lun is not None:
            body["remoteSVol"] = target_lun

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return "OK"
        elif "HIJSONFAULT" in response.headers:

            # return response.json()

            jfault = json.loads(response.headers["HIJSONFAULT"])
            msg = jfault["ErrorMessage"]
            if "The pair is already in PAIR status" in msg:
                return None
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def resyncUR(
        self,
        lun,
        remote_serial,
        target_lun,
        copy_pace,
    ):

        funcName = "hv_remotemanager:resyncUR"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("target_lun={}", target_lun)

        url = self.getUrl("TrueCopy/ResyncURRemoteClone")
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "remoteDeviceSerial": remote_serial,
        }

        if target_lun is not None:
            body["remoteSVol"] = target_lun
        if copy_pace is not None:
            body["copyPace"] = copy_pace

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return "OK"
        elif "HIJSONFAULT" in response.headers:

            # return response.json()

            jfault = json.loads(response.headers["HIJSONFAULT"])
            msg = jfault["ErrorMessage"]
            if "The pair is already in PAIR status" in msg:
                return None
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def restoreRemoteClone(
        self,
        lun,
        remote_serial,
        target_lun,
    ):

        funcName = "hv_remotemanager:restoreRemoteClone"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("target_lun={}", target_lun)

        url = self.getUrl("TrueCopy/RestoreRemoteClone")
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "remoteDeviceSerial": remote_serial,
            "remoteSVol": target_lun,
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

    def getFreeCTGId(self):

        funcName = "hv_remotemanager:getFreeCTGId"
        self.logger.writeEnterSDK(funcName)

        url = self.getUrl("TrueCopy/GetFreeLocalConsistencyGroupId")
        body = {"sessionId": self.sessionId, "serial": self.serial}

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

    def createGADPairVbox(
        self,
        pVol,
        remote_serial,
        targetResourceId,
        quorum_id,
        targetPoolId,
        targetHostGroup,
        allocateCtg,
    ):

        funcName = "hv_remotemanager:createGADPairVbox"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("pVol={}", pVol)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("targetPoolId={}", targetPoolId)

        url = self.getUrl("TrueCopy/CreateVBOXGlobalActiveDevicePairWithCTG")
        body = {
            "sessionId": self.sessionId,
            "pVol": pVol,
            "serialNumber": self.serial,
            "quorumDiskId": quorum_id,
            "targetPoolId": targetPoolId,
        }

        if remote_serial is not None:
            body["targetDeviceSerial"] = remote_serial
        if targetResourceId is not None:
            body["targetResourceId"] = targetResourceId
        if targetHostGroup is not None:
            body["targetHostGroup"] = targetHostGroup
        if allocateCtg is not None:
            body["allocateCtg"] = allocateCtg

        #         Logger().writeInfo(json.dumps(body))

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

    def createGADPairVboxCtgid(
        self,
        pVol,
        remote_serial,
        targetResourceId,
        quorum_id,
        targetPoolId,
        targetHostGroup,
        ctgID,
    ):

        funcName = "hv_remotemanager:createGADPairVboxCtgid"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("pVol={}", pVol)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("targetPoolId={}", targetPoolId)

        url = self.getUrl("TrueCopy/CreateVBOXGlobalActiveDevicePairWithCTGId")

        body = {
            "sessionId": self.sessionId,
            "pVol": pVol,
            "serialNumber": self.serial,
            "quorumDiskId": quorum_id,
            "targetPoolId": targetPoolId,
        }

        if remote_serial is not None:
            body["targetDeviceSerial"] = remote_serial
        if targetResourceId is not None:
            body["targetResourceId"] = targetResourceId
        if targetHostGroup is not None:
            body["targetHostGroup"] = targetHostGroup
        if ctgID is not None:
            body["ctgID"] = ctgID

        #         Logger().writeInfo(json.dumps(body))

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

    def createGADPair(
        self,
        pVol,
        remote_serial,
        sVol,
        quorum_id,
        ctgID,
    ):

        funcName = "hv_remotemanager:createGADPair"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("pVol={}", pVol)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("sVol={}", sVol)

        url = self.getUrl("TrueCopy/CreateGlobalActiveDevicePair")
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": pVol,
            "remoteDeviceSerial": remote_serial,
            "quorumDiskId": quorum_id,
            "copyPace": 3,
        }

        if ctgID is not None:
            body["ctgID"] = ctgID
        if sVol is not None:
            body["remoteSVol"] = sVol

        #         Logger().writeInfo(json.dumps(body))

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

    def createGADPair_tpid(
        self,
        pVol,
        remote_serial,
        target_pool_id,
        quorum_id,
        ctgID,
    ):

        funcName = "hv_remotemanager:createGADPair_tpid"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("pVol={}", pVol)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("target_pool_id={}", target_pool_id)

        url = self.getUrl("TrueCopy/CreateGlobalActiveDevicePairWithRemotePoolId")
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": pVol,
            "remotePoolId": target_pool_id,
            "quorumDiskId": quorum_id,
        }

        # removed from the func spec
        # if remote_serial is not None:
        #  body["remoteDeviceSerial"] = remote_serial

        if ctgID is not None:
            body["ctgID"] = ctgID

        #         Logger().writeInfo(json.dumps(body))

        response = requests.post(
            url, json=body, verify=self.shouldVerifySslCertification
        )

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return
        else:

            # elif "HIJSONFAULT" in response.headers:
            # The given key '0' was not present in the dictionary
            # raise Exception(json.loads(response.headers["HIJSONFAULT"]))

            raise Exception("HTTP error {0}".format(response.status_code))

    def getGADPairs(self, pVol=-1):

        funcName = "hv_remotemanager:getGADPairs"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("pVol={}", pVol)

        body = {"sessionId": self.sessionId, "serial": self.serial}

        if pVol is not None and pVol > 0:
            url = self.getUrl("TrueCopy/GetGlobalActiveDevicePairs")
            body["pVol"] = pVol
        else:
            url = self.getUrl("TrueCopy/GetGlobalActiveDevicePairsList")

        #         Logger().writeInfo("ENTER getGADPairs, pVol={}", pVol)

        response = requests.get(
            url, params=body, verify=self.shouldVerifySslCertification
        )

        if response.ok:
            self.logger.writeDebug("response.json()={}", response.json())
            self.logger.writeExitSDK(funcName)
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex = Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {0}".format(response.status_code))

    def splitGADPair(self, lun):

        funcName = "hv_remotemanager:splitGADPair"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)

        url = self.getUrl("TrueCopy/SplitGlobalActiveDevicePair")
        body = {"sessionId": self.sessionId, "serialNumber": self.serial, "pVol": lun}

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

    def resyncGADPair(self, lun):

        funcName = "hv_remotemanager:resyncGADPair"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)

        url = self.getUrl("TrueCopy/ResyncGlobalActiveDevicePair")
        body = {"sessionId": self.sessionId, "serialNumber": self.serial, "pVol": lun}

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

    def deleteGADPair(self, lun):

        funcName = "hv_remotemanager:deleteGADPair"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)

        url = self.getUrl("TrueCopy/DeleteGlobalActiveDevicePair")
        body = {"sessionId": self.sessionId, "serialNumber": self.serial, "pVol": lun}

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

    def deleteTCPair(
        self,
        lun,
        remote_serial,
        target_lun,
    ):

        funcName = "hv_remotemanager:deleteTCPair"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("target_lun={}", target_lun)

        url = self.getUrl("TrueCopy/DeleteRemoteClone")
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "remoteDeviceSerial": remote_serial,
        }

        if target_lun is not None:
            body["remoteSVol"] = target_lun

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

    def deleteURPair(
        self,
        lun,
        remote_serial,
        target_lun,
    ):

        funcName = "hv_remotemanager:deleteURPair"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("target_lun={}", target_lun)

        url = self.getUrl("TrueCopy/DeleteURRemoteClone")
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "remoteDeviceSerial": remote_serial,
        }

        if target_lun is not None:
            body["remoteSVol"] = target_lun

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

    def getErrorMessage(self, response):
        jfault = json.loads(response.headers["HIJSONFAULT"])
        msg = jfault["ErrorMessage"]
        resp = {}
        resp["comment"] = msg
        resp["failed"] = True
        return resp

    # deleteUR

    def deleteRemoteClone(
        self,
        lun,
        remote_serial,
        target_lun,
    ):

        funcName = "hv_remotemanager:deleteRemoteClone"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}", lun)
        self.logger.writeParam("remote_serial={}", remote_serial)
        self.logger.writeParam("target_lun={}", target_lun)

        url = self.getUrl("TrueCopy/DeleteRemoteClone")
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "pVol": lun,
            "remoteDeviceSerial": remote_serial,
            "remoteSVol": target_lun,
        }

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
