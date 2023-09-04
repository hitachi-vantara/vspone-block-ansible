import datetime
import json
import sys
#import os
import requests
import urllib
import urllib2
import urllib3
import base64
import os
import re
import logging
import subprocess

from enum import Enum

from ansible.module_utils.hv_htimanager import HTIManager
from ansible.module_utils.hv_remotemanager import RemoteManager
from ansible.module_utils.hv_htimanager import LunStatus
from ansible.module_utils.hv_htimanager import LunType
from ansible.module_utils.hv_htimanager import PoolType
from ansible.module_utils.hv_htimanager import ReplicationStatus
from ansible.module_utils.hv_vsm_manager import VirtualStorageSystem
from ansible.module_utils.hv_storage_enum import PoolCreateType, StorageType, StorageModel, PoolType, PoolStatus
from ansible.module_utils.hv_logger import Logger, MessageID
from ansible.module_utils.hv_log import Log, HiException

class StorageSystemManager:
    
    logger = Log()

    @staticmethod
    def getHostWWNs(hitachiAPIGatewayService, vcip, user, pword, esxiIP):
        funcName = "hv_infra:getHostWWNs"
        StorageSystemManager.logger.writeEnterSDK(funcName)    
        url = "https://{0}:2023/HitachiStorageManagementWebServices/StorageManager/StorageManager/HostWWN".format(hitachiAPIGatewayService)
        body = {
            "vcip": vcip,
            "user": user,
            "hostIp": esxiIP
        }            
        StorageSystemManager.logger.writeInfo(" url= {}", url)
        StorageSystemManager.logger.writeInfo(" body= {}", body)
        body["pwd"] = pword
        
        StorageSystemManager.logger.writeExitSDK(funcName)    
        response = requests.get(url, params=body, verify=False)
        if response.ok:
            commandOutJson = response.json()
            StorageSystemManager.logger.writeInfo(" response= {}", commandOutJson)
            #return is a string
            #commandOutJson = json.loads(commandOut)
            return commandOutJson
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            StorageSystemManager.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))
    
    @staticmethod
    def reScanHostStorage(hitachiAPIGatewayService, vcip, user, pword, esxiIP):
        funcName = "hv_infra:reScanHostStorage"
        StorageSystemManager.logger.writeEnterSDK(funcName)    
        url = "https://{0}:2023/HitachiStorageManagementWebServices/StorageManager/StorageManager/ReScanHostStorage".format(hitachiAPIGatewayService)
        body = {
            "vcip": vcip,
            "user": user,
            "hostIp": esxiIP
        }            
        StorageSystemManager.logger.writeInfo(" url= {}", url)
        StorageSystemManager.logger.writeInfo(" body= {}", body)
        body["pwd"] = pword
        
        StorageSystemManager.logger.writeExitSDK(funcName)    
        response = requests.post(url, params=body,  json={}, verify=False)
        if response.ok:
            StorageSystemManager.logger.writeInfo(" response= {}", response)
            return response
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            StorageSystemManager.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))
    
    @staticmethod
    def reScanVMFS(hitachiAPIGatewayService, vcip, user, pword, esxiIP):
        funcName = "hv_infra:reScanHostStorage"
        StorageSystemManager.logger.writeEnterSDK(funcName)    
        url = "https://{0}:2023/HitachiStorageManagementWebServices/StorageManager/StorageManager/ReScanVMFS".format(hitachiAPIGatewayService)
        body = {
            "vcip": vcip,
            "user": user,
            "hostIp": esxiIP
        }            
        StorageSystemManager.logger.writeInfo(" url= {}", url)
        StorageSystemManager.logger.writeInfo(" body= {}", body)
        body["pwd"] = pword
        
        StorageSystemManager.logger.writeExitSDK(funcName)    
        response = requests.post(url, params=body, json={}, verify=False)
        if response.ok:
            StorageSystemManager.logger.writeInfo(" response= {}", response)
            return response
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            StorageSystemManager.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    @staticmethod
    def addStorgeSystemByJson():
        
        funcName = "hv_infra:addStorgeSystemByJson"
        StorageSystemManager.logger.writeEnterSDK(funcName)    
        connections = {}
        
        try:  
            storageJson = os.getenv('HV_STORAGE_ANSIBLE_PROFILE', "./storage.json")
            with open(storageJson) as connectionFile:
                connections = json.load(connectionFile)
                
            storagesystems = connections.get("sanStorageSystems", None)           
            fileServers = connections.get("nasStorageSystems", None)
            if storagesystems is None and fileServers is None:
                raise Exception("Both sanStorageSystems and nasStorageSystems are not specified.")
            
            hitachiAPIGatewayService = connections.get("hitachiAPIGatewayService", None)
            hitachiAPIGatewayServicePort = connections.get("hitachiAPIGatewayServicePort", None)
            
            isPhysicalServer = connections.get("useOutOfBandConnection", None)
            if isPhysicalServer is None:
                useOutOfBandConnection = False
            else:
                if isPhysicalServer.upper() == "FALSE":
                    useOutOfBandConnection = False
                else:
                    useOutOfBandConnection = True        
                        
            StorageSystemManager.addStorgeSystem(
                        hitachiAPIGatewayService, hitachiAPIGatewayServicePort,
                        storagesystems, fileServers, useOutOfBandConnection
                        )        
            
            StorageSystemManager.logger.writeExitSDK(funcName)    
        except:
            raise Exception("Failed to add StorgeSystem again")  
        
    @staticmethod
    def addFileServers( hitachiAPIGatewayService, hitachiAPIGatewayServicePort,
            fileServers, sessionIds, connectors, serials): 
        
        funcName = "hv_infra:StorageSystemManager:addFileServers"
        StorageSystemManager.logger.writeEnterSDK(funcName)    
                               
        for systemInfo in fileServers:
            
            #check for empty map
            if not systemInfo:
                continue
            
            gatewayServer = systemInfo.get("hitachiPeerService", hitachiAPIGatewayService)
            gatewayServerPort = systemInfo.get("hitachiPeerServicePort", hitachiAPIGatewayServicePort)
            
            if gatewayServer is None or gatewayServerPort is None:
                raise Exception("Gateway Server and Port are required.")
            
            if "fileServerIP" not in systemInfo:
                raise Exception("fileServerIP is required.")
            
            fileServerIP = systemInfo["fileServerIP"]
            
            StorageSystemManager.logger.writeParam("fileServerIP={}",fileServerIP)    
            #StorageSystemManager.self.logger.writeInfo("pwd",
            #            Utils.doGrains(systemInfo["fileServerIP"])
            #            )

            ## hitachiAPIGatewayService is the one and only c# service
            ## the local var serviceIP = "storageGateway" also the c# service
            ## gatewayServer = puma server
            serviceIP = systemInfo.get("storageGateway", hitachiAPIGatewayService)
            servicePort = gatewayServerPort
            
            ##for fileServer, there is no serial
            #serial = systemInfo["serialNumber"]
            
            ## use the hitachiAPIGatewayService to add nas storage,
            ## and gatewayServer is the puma server if differ from hitachiAPIGatewayService
            serial = 0
#             self.logger.writeInfo("serial={}", serial)

            gateway = StorageSystem(serial, serviceIP, servicePort, sessionIds.get(serviceIP, ""))
#             self.logger.writeInfo("gateway={}", gateway)
            username = systemInfo.get("username", None)

            # terraform provides the password as a parameter, but ansible reads it from encrypted storage.json
            password = systemInfo.get("password", None)
            if password is None:
                password = Utils.doGrains(systemInfo["fileServerIP"])

            storageSystem = gateway.addFileServer( gatewayServer,
                systemInfo["fileServerIP"], username,
                password)
            
            if storageSystem is None:
                raise Exception("Failed to add the storage system : {0}.{1}".format(serviceIP,servicePort))

            sessionIds[serviceIP] = storageSystem["GroupIdentifier"]
            serial = fileServerIP
            connectors[serial] = {
                "storageGatewayServer": gatewayServer,
                "storageGateway": serviceIP,
                "storageGatewayPort": servicePort,
                "sessionId": storageSystem["GroupIdentifier"]
            }
            serials.add(serial)
            
            connectors["hitachiAPIGatewayService"] = {
                "storageGatewayServer": gatewayServer,
                "storageGatewayServer": gatewayServer,
                "storageGateway": serviceIP,
                "storageGatewayPort": servicePort,
                "sessionId": storageSystem["GroupIdentifier"]
            }

            connectors["HNASFileServer"] = {
                "storageGatewayServer": gatewayServer,
                "storageGateway": hitachiAPIGatewayService,
                "storageGatewayPort": hitachiAPIGatewayServicePort,
                "sessionId": storageSystem["GroupIdentifier"]
            }
        
        ##done with looping thru the file servers, exit                
        StorageSystemManager.logger.writeExitSDK(funcName)    

    @staticmethod
    def isOOB( isPhysicalServer ):
        if isPhysicalServer is None:
            useOutOfBandConnection = False
        else:
            if isPhysicalServer.upper() == "FALSE":
                useOutOfBandConnection = False
            else:
                useOutOfBandConnection = True
                
        return useOutOfBandConnection
    
    @staticmethod
    def addStorgeSystem( 
            hitachiAPIGatewayService, hitachiAPIGatewayServicePort,
            storagesystems, fileServers, useOutOfBandConnection
            ):
        
        funcName = "hv_infra:StorageSystemManager:addStorgeSystem"
        StorageSystemManager.logger.writeEnterSDK(funcName)
        StorageSystemManager.logger.writeParam("useOutOfBandConnection={}",useOutOfBandConnection)
        
        sessionIds = {}
        connectors = {}
        serials = set()
        results = {} 
        ssDetails = {} 
        
        if storagesystems is None:
            storagesystems = []
        if fileServers is None:
            fileServers = []
        
        ## process nasStorageSystems in storage.json
        StorageSystemManager.addFileServers(hitachiAPIGatewayService, hitachiAPIGatewayServicePort,
                                            fileServers, sessionIds, connectors, serials)       
        
        ## process sanStorageSystems in storage.json
        for systemInfo in storagesystems:
            
            #check for empty map
            if not systemInfo:
                continue
                        
            gatewayServer = systemInfo.get("hitachiPeerService", hitachiAPIGatewayService)
            gatewayServerPort = systemInfo.get("hitachiPeerServicePort", hitachiAPIGatewayServicePort)
            
            ## each storage can have the option to overwrite the global useOutOfBandConnection option
            isOutOfBand = useOutOfBandConnection
            isPhysicalServer = systemInfo.get("useOutOfBandConnection", None)
            if isPhysicalServer is not None:
                isOutOfBand = StorageSystemManager.isOOB( isPhysicalServer )
            
            
#             self.logger.writeInfo("gatewayServer={}", gatewayServer)
            if gatewayServer is None or gatewayServerPort is None:
                raise Exception("Gateway Server and Port are required.")
            
            if hitachiAPIGatewayService is None:
                # to be backward compatible, just use the first setting for primary(default)
                hitachiAPIGatewayService = gatewayServer
                hitachiAPIGatewayServicePort = gatewayServerPort
            
            if "svpIP" not in systemInfo:
                raise Exception("svpIP (location) is required.")
            
            ## hitachiAPIGatewayService is the one and only c# service
            ## the local var serviceIP = "storageGateway" also the c# service
            ## gatewayServer = puma server
            serviceIP = systemInfo.get("storageGateway", hitachiAPIGatewayService)
            servicePort = gatewayServerPort
            
            
            serial = systemInfo["serialNumber"]
#             self.logger.writeInfo("serial={}", serial)

            gateway = StorageSystem(serial, serviceIP, servicePort, sessionIds.get(serviceIP, ""))
#             self.logger.writeInfo("gateway={}", gateway)
            username = systemInfo.get("username", None)


            # terraform provides the password as a parameter, but ansible reads it from encrypted storage.json
            password = systemInfo.get("password", None)
            if password is None:
                password = Utils.doGrains(systemInfo["svpIP"])

            storageSystem = gateway.addStorageSystem(systemInfo["svpIP"], gatewayServer,
                                                    8444, username,
                                                    password, isOutOfBand)

            if storageSystem is None:
                raise Exception("Failed to add the storage system : {0}.{1}".format(serviceIP,servicePort))

            ## FIXME - SIEAN-268 was raise due to the names are confusing
            ## and a incorrect fix was committed now it is reverted
            ## we need to rename storageGateway to storageMgmtServer
            ##
            ## storageGateway = StorageManagementServer C# service
            ## storageGatewayPort is typical 2023
            ## storageGatewayServer is the puma
            ## 

            sessionIds[serviceIP] = storageSystem["SessionId"]
            connectors[serial] = {
                "storageGatewayServer": gatewayServer,
                "storageGateway": serviceIP,
                "storageGatewayPort": servicePort,
                "sessionId": storageSystem["SessionId"]
            }
            serials.add(serial)
            
            connectors["hitachiAPIGatewayService"] = {
                "storageGatewayServer": gatewayServer,
                "storageGatewayServer": gatewayServer,
                "storageGateway": serviceIP,
                "storageGatewayPort": servicePort,
                "sessionId": storageSystem["SessionId"]
            }
            ssDetails[serial] = storageSystem

        with open(Log.getHomePath()+"/storage-connectors.json", 'w') as connectorFile:
            json.dump(connectors, connectorFile)
            
        results["storageSystems"] = list(serials)        
        results["sessionIds"] = sessionIds
        results["details"] = ssDetails
        
        StorageSystemManager.logger.writeExitSDK(funcName)    
        return results        

class Utils:
    
    logger = Log()
    
    @staticmethod
    def doGrains(ipaddress):
        
        funcName = "hv_infra:doGrains"
        Utils.logger.writeEnterSDK(funcName)
        
        try:
                storageJson = os.getenv('HV_STORAGE_ANSIBLE_PROFILE', "./storage.json")
                
                Utils.logger.writeInfo("storageJson={}",storageJson)
                Utils.logger.writeInfo("Log.getHomePath()={}",Log.getHomePath())
                
                command = Log.getHomePath()+'/bin/.grains {} '+storageJson+' '
                command = command.format( ipaddress )
#                 Utils.logger.writeInfo("command={}",command)
                
                commandOutStr = subprocess.check_output(command, shell=False)
                commandOutStr = commandOutStr.replace("\n","")
#                 Utils.logger.writeInfo("the password is={}",commandOutStr)
                
                Utils.logger.writeExitSDK(funcName)
                return commandOutStr
        except:
            raise Exception("Invalid password, please check password for {}".format(ipaddress))
    
    @staticmethod
    def requestsPost_notused(url, json, verify):
        try:
            return requests.post( url, json=json, verify=verify)        
        except:
            # note: exception thrown by requests is caught by ansible module
            # it will not be caught here
            raise Exception("requests exception caught")
    
    @staticmethod
    def requestsGet_notused(url, params, verify):
        try:
            return requests.get( url, params=params, verify=verify)        
        except:
            # let's try to add storage again
            raise Exception("foo:w")
    
    @staticmethod
    def formatCapacity(valueMB):
        
        # expected valueMB (from puma):
        # 5120 is 5120MB
        
        Utils.logger.writeParam("formatCapacity, value={}", valueMB)
        oneK = 1024
        
        ivalue = int(valueMB)
        if ivalue == 0:
            return "0"
        elif ivalue >= oneK*oneK:
            v = ivalue / oneK*oneK
            return str(v) + "TB"
        elif ivalue >= oneK:
            v = ivalue / oneK
            return str(v) + "GB"
        else:
            return str(valueMB) + "MB"
        
    @staticmethod
    def formatLun(lun):
        if lun.get("VirtualLunNumber") is not None: 
            lun["VirtualLun"] = lun["VirtualLunNumber"] 
            del lun["VirtualLunNumber"]
        if lun.get("LunNumber") is not None: 
            lun["Lun"] = lun["LunNumber"] 
            del lun["LunNumber"]
        if lun.get("IsVirtualLogicalUnit") is not None: 
            del lun["IsVirtualLogicalUnit"]
        if lun.get("DynamicPool") is not None: 
            del lun["DynamicPool"]
        if lun.get("TotalCapacity") is not None: 
            lun["TotalCapacity"] = Utils.formatCapacity(lun["TotalCapacity"])
        if lun.get("UsedCapacity") is not None: 
            lun["UsedCapacity"] = Utils.formatCapacity(lun["UsedCapacity"]) 
        if lun.get("Status") is not None: 
            lun["Status"] = LunStatus.fromValue(lun.get("Status", 0)).name
        if lun.get("Type") is not None: 
            lun["Type"] = LunType.fromValue(lun.get("Type", 0)).name
        if lun.get("PoolType") is not None: 
            lun["PoolType"] = PoolType.fromValue(lun.get("PoolType", 0)).name
        
    @staticmethod
    def formatLuns(luns):
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
        
class StorageSystem():
    
#     slogger = Log()
    
    def setDryRun(self, flag):        
        #StorageSystem.slogger.writeEnterSDK("slogger: StorageSystem.setDryRun")
        funcName="StorageSystem:setDryRun"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("dryRun={}",flag)
        #StorageSystem.slogger.writeEnterSDK("slogger: StorageSystem.setDryRun")
        funcName="StorageSystem:setDryRun"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("dryRun={}",flag)
        self.dryRun=flag
        self.logger.writeExitSDK(funcName)
            
    def __init__(self, serial, webServiceIp=None, webServicePort=None, sessionId=None):
        self.logger=Log()
        self.dryRun=False
        self.serial = serial
        self.sessionId = sessionId
        self.isVirtualSerial = False

        if not webServiceIp:
            try:
                with open(Log.getHomePath()+"/storage-connectors.json") as connectionFile:
                    connections = json.load(connectionFile)
                system = connections.get(str(serial))
                
                if system is None:
                    #raise Exception("Storage system {0} is not registered. Double-check the serial number or run the hv_storagesystem module with this storage system.".format(serial))
                    # to support virutal serial ids, we just use the first one,                    
                    # since all have the same session.id
                    system = connections["hitachiAPIGatewayService"]
                    self.isVirtualSerial = True
                                        
                self.sessionId = system["sessionId"]
                webServiceIp = system["storageGateway"]
                webServicePort = system["storageGatewayPort"]
            except IOError as ex:
                raise Exception("Storage systems have not been registered. Please run add_storagesystems.yml first.")

        self.webServiceIp = webServiceIp
        self.webServicePort = webServicePort
        self.basedUrl = "https://{0}:{1}".format(webServiceIp, webServicePort)
        self.shouldVerifySslCertification = False

        self.htiManager = HTIManager(self.serial, self.webServiceIp, self.webServicePort, self.sessionId)
        self.remoteManager = RemoteManager(self.serial, self.webServiceIp, self.webServicePort, self.sessionId)
        self.vsmManager = VirtualStorageSystem(self.serial, self.webServiceIp, self.webServicePort, self.sessionId)

    def isSessionNotFound(self, exMsg):
        strToMatch = "Session " +self.sessionId+ " is not found"
        if strToMatch in str(exMsg):
            return True
        else:
            return False
        
    def removeLogicalUnitFromResourceGroup(self, rgId, id ):
                
        funcName="hv_infra:removeLogicalUnitFromResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}",rgId)
        self.logger.writeParam("id={}",id)
                
        urlPath = "ResourceGroup/RemoveLogicalUnitFromResourceGroup"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "luId": id,
            "rgId": rgId
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))


    def addLogicalUnitToResourceGroup(self, rgId, id ):
                
        funcName="hv_infra:addLogicalUnitToResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}",rgId)
        self.logger.writeParam("id={}",id)
        
        funcName="hv_infra:addLogicalUnitToResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}",rgId)
        self.logger.writeParam("id={}",id)
        
        urlPath = "ResourceGroup/AddLogicalUnitToResourceGroup"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "luId": id,
            "rgId": rgId
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def deleteResourceGroup(self, rgId ):
                
        funcName="hv_infra:deleteResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}",rgId)

        urlPath = "ResourceGroup/DeleteResourceGroup"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "rgId": rgId
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def removeDriveGroupFromResourceGroup(self, rgId, parityGroupId ):
                
        funcName="hv_infra:removeDriveGroupFromResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}",rgId)
        self.logger.writeParam("parityGroupId={}",parityGroupId)

        urlPath = "ResourceGroup/RemoveDriveGroupFromResourceGroup"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "parityGroupId": parityGroupId,
            "rgId": rgId
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))
 
    def addFileServer(self, gatewayServer, fileServerIP, username, password):
                
        funcName="hv_infra:StorageSystem:addFileServer"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("gatewayServer={}",gatewayServer)
        self.logger.writeParam("fileServerIP={}",fileServerIP)
        self.logger.writeParam("username={}",username)

        urlPath = "NAS/StorageManager/AddFileServer"
        url = self.getUrl(urlPath)
        self.logger.writeInfo("url={}",url)
        body = {
            "sessionId": self.sessionId,
            "fileServer": fileServerIP,
            "userID": username,
            "password": password,
            #"gatewayServer": self.webServiceIp,
            "gatewayServer": gatewayServer,
            "gatewayServerPort": 8444,
            "forceReinitialize": False
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))
               
    def addDriveGroupToResourceGroup(self, rgId, parityGroupId ):
        
        funcName="hv_infra:addDriveGroupToResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}",rgId)
        self.logger.writeParam("parityGroupId={}",parityGroupId)
        
        urlPath = "ResourceGroup/AddDriveGroupToResourceGroup"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "parityGroupId": parityGroupId,
            "rgId": rgId
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def removeHostGroupFromResourceGroup(self, rgId, hostGroupName, portId  ):
                
        funcName="hv_infra:removeHostGroupFromResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}",rgId)
        self.logger.writeParam("hostGroupName={}",hostGroupName)
        self.logger.writeParam("portId={}",portId)

        urlPath = "ResourceGroup/RemoveHostGroupFromResourceGroup"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "hostGroupName": hostGroupName,
            "portId": portId,
            "rgId": rgId
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            #return response.json()
            return response
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def addHostGroupToResourceGroup(self, rgId, hostGroupName, portId  ):
                
        funcName="hv_infra:addHostGroupToResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}",rgId)
        self.logger.writeParam("hostGroupName={}",hostGroupName)
        self.logger.writeParam("portId={}",portId)

        urlPath = "ResourceGroup/AddHostGroupToResourceGroup"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "hostGroupName": hostGroupName,
            "portId": portId,
            "rgId": rgId
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def removePortFromResourceGroup(self, rgId, id ):
                
        funcName="hv_infra:removePortFromResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}",rgId)
        self.logger.writeParam("id={}",id)

        urlPath = "ResourceGroup/RemovePortFromResourceGroup"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "portId": id,
            "rgId": rgId
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

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
    
    def createVirtualBoxResourceGroup(self, remoteStorageId, model, rgName ):
                
        funcName="hv_infra:createVirtualBoxResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("remoteStorageId={}",remoteStorageId)
        self.logger.writeParam("model={}",model)
        self.logger.writeParam("rgName={}",rgName)
        
        funcName="hv_infra:createVirtualBoxResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("remoteStorageId={}",remoteStorageId)
        self.logger.writeParam("model={}",model)
        self.logger.writeParam("rgName={}",rgName)
        
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
            "rgName": rgName
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            #return response.json()
            return response
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def addPortToResourceGroup(self, rgId, id ):
                
        funcName="hv_infra:addPortToResourceGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("rgId={}",rgId)
        self.logger.writeParam("id={}",id)

        urlPath = "ResourceGroup/AddPortToResourceGroup"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "portId": id,
            "rgId": rgId
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def isVirtualSerialInUse(self):
        return self.isVirtualSerial
    
    def getUrl(self, urlPath):
        return "{0}/HitachiStorageManagementWebServices/{1}".format(self.basedUrl, urlPath)

    def addStorageSystem(self, location, gatewayIP, gatewayPort, username, password, useOutOfBandConnection):
                
        funcName="hv_infra:StorageSystem:addStorageSystem"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("location={}",location)
        self.logger.writeParam("gatewayIP={}",gatewayIP)
        self.logger.writeParam("gatewayPort={}",gatewayPort)
        self.logger.writeParam("username={}",username)
        self.logger.writeParam("useOutOfBandConnection={}",useOutOfBandConnection)

                
        funcName="hv_infra:addStorageSystem"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("location={}",location)
        self.logger.writeParam("gatewayIP={}",gatewayIP)
        self.logger.writeParam("gatewayPort={}",gatewayPort)
        self.logger.writeParam("username={}",username)

        urlPath = "StorageManager/StorageManager/AddRAID"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId or "",
            "serialNumber": self.serial,
            "location": location,
            "gatewayServer": gatewayIP,
            "gatewayServerPort": gatewayPort,
            "userID": username,
            "useOutOfBand": useOutOfBandConnection,
            "password": password
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            system = response.json()
            system["webServiceIp"] = self.webServiceIp
            system["webServicePort"] = self.webServicePort
            system["StorageDeviceType"] = StorageType.parse(system.get("StorageDeviceType")).name

            return system
        elif "HIJSONFAULT" in response.headers:
            self.logger.writeDebug("HIJSONFAULT response={}",response)
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            self.logger.writeDebug("Unknown Exception response={}",response)
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def getInfo(self):
                
        funcName="hv_infra:getInfo"
        self.logger.writeEnterSDK(funcName)

        urlPath = "StorageManager/StorageManager/GetRAIDStorageInfo"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serial": self.serial
        }

        response = requests.get(url, params=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            system = response.json()
            system["StorageDeviceType"] = StorageType.parse(system.get("StorageDeviceType")).name

            return system
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def createLunInDP(self, lun, pool, sizeInGB, stripeSize, metaResourceSerial, luName):
                
        funcName="hv_infra:createLunInDP"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}",lun)
        self.logger.writeParam("pool={}",pool)
        self.logger.writeParam("sizeInGB={}",sizeInGB)
        self.logger.writeParam("stripeSize={}",stripeSize)
        self.logger.writeParam("metaResourceSerial={}",metaResourceSerial)
        self.logger.writeParam("luName={}",luName)

        urlPath = "LogicalUnit/LogicalUnit/CreateInDPLite"
        url = self.getUrl(urlPath)
        self.logger.writeDebug("url={}",url)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "lun": lun or -1,
            "pool": pool,
            "sizeInGB": sizeInGB,
            "stripeSize": stripeSize or 0,
            "metaResourceSerial": metaResourceSerial or -1,
            "luName": luName or ''
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def createLunInPG(self, lun, parityGroup, sizeInGB, stripeSize, metaResourceSerial, luName):
                
        funcName="hv_infra:createLunInPG"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}",lun)
        self.logger.writeParam("parityGroup={}",parityGroup)
        self.logger.writeParam("sizeInGB={}",sizeInGB)
        self.logger.writeParam("stripeSize={}",stripeSize)
        self.logger.writeParam("metaResourceSerial={}",metaResourceSerial)
        self.logger.writeParam("luName={}",luName)

        urlPath = "LogicalUnit/LogicalUnit/CreateInPGLite"
        url = self.getUrl(urlPath)
        self.logger.writeDebug("url={}",url)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "lun": lun or -1,
            "pg": parityGroup,
            "sizeInGB": sizeInGB,
            "stripeSize": stripeSize,
            "metaResourceSerial": metaResourceSerial or -1,
            "luName": luName or ''
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def updateLunName(self, lun, luName):
        
        funcName="hv_infra:updateLunName"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}",lun)
        self.logger.writeParam("luName={}",luName)
        self.logger.writeParam("dryRun={}",self.dryRun)
        if self.dryRun:
            return
        
        urlPath = "LogicalUnit/LogicalUnit/UpdateLogicalUnitName"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "lun": lun,
            "lunName": luName
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def cloneLunInDP(self, sourceLun, pool, clonedLunName):
                
        funcName="hv_infra:cloneLunInDP"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("sourceLun={}",sourceLun)
        self.logger.writeParam("pool={}",pool)
        self.logger.writeParam("clonedLunName={}",clonedLunName)

        urlPath = "LogicalUnit/LogicalUnit/CloneInDP"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "lun": sourceLun,
            "pool": pool,
            "lunName": clonedLunName
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def createPresentedVolume(self, lun, pool, resourceGroupId, hostGroupName, port, sizeInMB, stripeSize, luName):
                
        funcName="hv_infra:createPresentedVolume"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}",lun)
        self.logger.writeParam("pool={}",pool)
        self.logger.writeParam("resourceGroupId={}",resourceGroupId)

        urlPath = "LogicalUnit/LogicalUnit/CreatePresentedVolume"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "lun": lun or -1,
            "resourceGroupId": resourceGroupId,
            "hostGroupName": hostGroupName or '',
            "port": port or '',
            "pool": pool,
            "sizeInMB": sizeInMB,
            "stripeSize": stripeSize or 0,
            "luName": luName or ''
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def expandLun(self, lun, sizeInGB):
        
        funcName="hv_infra:expandLun"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}",lun)
        self.logger.writeParam("sizeInGB={}",sizeInGB)
        self.logger.writeParam("dryRun={}",self.dryRun)
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

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            if "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
            else:
                raise Exception("Unknown error HTTP {}".format(response.status_code))

    def deleteLun(self, lun):
                
        funcName="hv_infra:deleteLun"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}",lun)

        urlPath = "LogicalUnit/LogicalUnit/Delete"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "lun": lun,
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            if "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
            else:
                raise Exception("Unknown error HTTP {}".format(response.status_code))

    def getLun(self, lun, doRetry=True):
                
        funcName="hv_infra:getLun"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}",lun)
        
                
        funcName="hv_infra:getLun"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}",lun)

        urlPath = "LogicalUnit/LogicalUnit/Get"
        url = self.getUrl(urlPath)
        params = {
            "sessionId": self.sessionId,
            "serial": self.serial,
            "lun": lun,
        }

        self.logger.writeParam("url={}",url)
        self.logger.writeParam("params={}",params)
        response = requests.get(url, params=params, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            if doRetry:
                ##retry once
#             self.logger.writeDebug(funcName+":HIJSONFAULT={}",response.headers)
                self.logger.writeDebug(funcName+":{}","retry once")
                return self.getLun(lun, False)
            else:
                return None
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def getLunByNaa(self, lunCanonicalName):
                
        funcName="hv_infra:getLunByNaa"
        self.logger.writeEnterSDK(funcName)

        urlPath = "LogicalUnit/LogicalUnit/GetByCanonicalName"
        url = self.getUrl(urlPath)
        params = {
            "sessionId": self.sessionId,
            "canonicalName": lunCanonicalName,
        }

        self.logger.writeParam("url={}",url)
        self.logger.writeParam("params={}",params)
        
        response = requests.get(url, params=params, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def getLunByCountByNaa(self, lunCanonicalName, maxCount):
                
        funcName="hv_infra:getLunByCountByNaa"
        self.logger.writeEnterSDK(funcName)

        urlPath = "LogicalUnit/LogicalUnit/GetListByCountByCanonicalName"
        url = self.getUrl(urlPath)
        params = {
            "sessionId": self.sessionId,
            "canonicalName": lunCanonicalName,
            "maxCount": maxCount,
        }

        self.logger.writeParam("url={}",url)
        self.logger.writeParam("params={}",params)
        
        response = requests.get(url, params=params, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def getLunsByCount(self, startLDev, maxCount):
                
        funcName="hv_infra:getLunsByCount"
        self.logger.writeEnterSDK(funcName)

        urlPath = "LogicalUnit/LogicalUnit/GetListByCount"
        url = self.getUrl(urlPath)
        params = {
            "sessionId": self.sessionId,
            "serial": self.serial,
            "startLDev": startLDev,
            "maxCount": maxCount,
        }

        self.logger.writeParam("url={}",url)
        self.logger.writeParam("params={}",params)
        
        response = requests.get(url, params=params, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def getLunsByRange(self, beginLDev, endLDev):
                
        funcName="hv_infra:getLunsByRange"
        self.logger.writeEnterSDK(funcName)

        urlPath = "LogicalUnit/LogicalUnit/GetListByRange"
        url = self.getUrl(urlPath)
        params = {
            "sessionId": self.sessionId,
            "serial": self.serial,
            "beginLDev": beginLDev,
            "endLDev": endLDev,
        }

        self.logger.writeParam("url={}",url)
        self.logger.writeParam("params={}",params)
        
        response = requests.get(url, params=params, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))


    def getAllLuns(self):
                
        funcName="hv_infra:getAllLuns"
        self.logger.writeEnterSDK(funcName)

        urlPath = "LogicalUnit/LogicalUnit/GetList"
        url = self.getUrl(urlPath)
        params = {
            "sessionId": self.sessionId,
            "serial": self.serial
        }

        self.logger.writeParam("url={}",url)
        self.logger.writeParam("params={}",params)
        
        response = requests.get(url, params=params, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))
    def presentLun(self, lun, hgName, port):
        
        funcName="hv_infra:presentLun"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}",lun)
        self.logger.writeParam("hgName={}",hgName)
        self.logger.writeParam("port={}",port)
        self.logger.writeParam("dryRun={}",self.dryRun)
        if self.dryRun:
            return
        
        urlPath = "HostGroup/HostGroup/AddHostGroupLogicalUnitWithHostGroupLUNID"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "ldevid": lun,
            "hostGroupName": hgName,
            "port": port
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            if "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
            else:
                raise Exception("Unknown error HTTP {}".format(response.status_code))

    def unpresentLun(self, lun, hgName, port):
        
        funcName="hv_infra:unpresentLun"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}",lun)
        self.logger.writeParam("hgName={}",hgName)
        self.logger.writeParam("port={}",port)
        self.logger.writeParam("dryRun={}",self.dryRun)
        if self.dryRun:
            return
        
        urlPath = "HostGroup/HostGroup/RemoveLogicalUnit"
        url = self.getUrl(urlPath)
               
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "lun": lun,
            "hostGroupName": hgName,
            "port": port
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            if "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
            else:
                raise Exception("Unknown error HTTP {}".format(response.status_code))

    def createHostGroup(self, hgName, port, wwnList):
        
        funcName="hv_infra:createHostGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("wwnList={}",wwnList)
        self.logger.writeParam("hgName={}",hgName)
        self.logger.writeParam("port={}",port)
        self.logger.writeParam("dryRun={}",self.dryRun)
        if self.dryRun:
            return
        
        urlPath = "HostGroup/HostGroup/Create"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "wwns": ",".join(wwnList),
            "hostGroupName": hgName,
            "port": port
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            if "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
            else:
                raise Exception("Unknown error HTTP {}".format(response.status_code))

    def deleteHostGroup(self, hgName, port):
        
        funcName="hv_infra:deleteHostGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("hgName={}",hgName)
        self.logger.writeParam("port={}",port)
        self.logger.writeParam("dryRun={}",self.dryRun)
        if self.dryRun:
            return
        
        urlPath = "HostGroup/HostGroup/Delete"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "hostGroupName": hgName,
            "port": port
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            if "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
            else:
                raise Exception("Unknown error HTTP {}".format(response.status_code))

    def getHostGroup(self, hgName, port, doRetry=True):
                
        
        funcName="hv_infra:getHostGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("hgName={}",hgName)
        self.logger.writeParam("port={}",port)

                
        funcName="hv_infra:getHostGroup"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("hgName={}",hgName)
        self.logger.writeParam("port={}",port)

        urlPath = "HostGroup/HostGroup/Get"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serial": self.serial,
            "hostGroupName": hgName,
            "port": port
        }

        response = requests.get(url, params=body, verify=self.shouldVerifySslCertification)
        self.logger.writeExitSDK(funcName)
                
        self.logger.writeExitSDK(funcName)
        if response.ok:
            self.logger.writeDebug(funcName+":response={}",response)
            self.logger.writeDebug(funcName+":response={}",response.json())
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            if doRetry:
                ##retry once
#             self.logger.writeDebug(funcName+":HIJSONFAULT={}",response.headers)
                self.logger.writeDebug(funcName+":{}","retry once")
                return self.getHostGroup(hgName, port, False)
            else:
                return None
            #raise Exception(json.loads(response.headers["HIJSONFAULT"]))
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def getVSM(self):
                
        funcName="hv_infra:getVSM"
        self.logger.writeEnterSDK(funcName)

        urlPath = "StorageManager/StorageManager/GetVirtualStorageSystems"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId
        }

        response = requests.get(url, params=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
            ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
            hiex = HiException(ex)
            self.logger.writeHiException(hiex)
            raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))
        
    def getAllHostGroups(self):
                
        funcName="hv_infra:getAllHostGroups"
        self.logger.writeEnterSDK(funcName)

        urlPath = "HostGroup/HostGroup/GetList"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serial": self.serial
        }

        response = requests.get(url, params=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def getHostGroupsForLU(self, lun):
                
        funcName="hv_infra:getHostGroupsForLU"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("lun={}",lun)

        urlPath = "HostGroup/HostGroup/GetHostGroupsForLU"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "lu": lun
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def setHostMode(self, hgName, port, hostmode, hostopt):
        
        funcName="hv_infra:setHostMode"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("hgName={}",hgName)
        self.logger.writeParam("port={}",port)
        self.logger.writeParam("hostmode={}",hostmode)
        self.logger.writeParam("hostopt={}",hostopt)
        self.logger.writeParam("dryRun={}",self.dryRun)
        if self.dryRun:
            return

        urlPath = "HostGroup/HostGroup/SetHostMode"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "hostGroupName": hgName,
            "port": port,
            "mode": hostmode,
            "hostModeOptions": list(map(int, hostopt))
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            if "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
            else:
                raise Exception("Unknown error HTTP {}".format(response.status_code))

    def addWWN(self, hgName, port, wwnList):
        
        funcName="hv_infra:addWWN"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("hgName={}",hgName)
        self.logger.writeParam("port={}",port)
        self.logger.writeParam("wwnList={}",wwnList)
        self.logger.writeParam("dryRun={}",self.dryRun)
        if self.dryRun:
            return

        urlPath = "HostGroup/HostGroup/AddWWN"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "hostGroupName": hgName,
            "port": port,
            "wwns": ",".join(wwnList)
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            if "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
            else:
                raise Exception("Unknown error HTTP {}".format(response.status_code))

    def removeWWN(self, hgName, port, wwnList):
        
        funcName="hv_infra:removeWWN"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("hgName={}",hgName)
        self.logger.writeParam("port={}",port)
        self.logger.writeParam("wwnList={}",wwnList)
        self.logger.writeParam("dryRun={}",self.dryRun)
        if self.dryRun:
            return

        urlPath = "HostGroup/HostGroup/RemoveWWN"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "hostGroupName": hgName,
            "port": port,
            "wwns": ",".join(wwnList)
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            if "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
            else:
                raise Exception("Unknown error HTTP {}".format(response.status_code))

    def getPorts(self):
                
        funcName="hv_infra:getPorts"
        self.logger.writeEnterSDK(funcName)

        urlPath = "StorageDevice/StorageDevice/GetPorts"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serial": self.serial
        }

        response = requests.get(url, params=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def getStoragePools(self):
                
        funcName="hv_infra:getStoragePools"
        self.logger.writeEnterSDK(funcName)

        urlPath = "StoragePool/GetStoragePools"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def getJournalPools(self):
                
        funcName="hv_infra:getJournalPools"
        self.logger.writeEnterSDK(funcName)

        urlPath = "StorageDevice/StorageDevice/GetJournalPools"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "serial": self.serial
        }

        response = requests.get(url, params=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def getFreeLUList(self):
                
        funcName="hv_infra:getFreeLUList"
        self.logger.writeEnterSDK(funcName)

        urlPath = "LogicalUnit/LogicalUnit/GetFreeLUList"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "serial": self.serial,
            "minResults": 100
        }

        response = requests.get(url, params=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def getFreeGADConsistencyGroupId(self):
                
        funcName="hv_infra:getFreeGADConsistencyGroupId"
        self.logger.writeEnterSDK(funcName)

        urlPath = "TrueCopy/GetFreeGADConsistencyGroupId"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "serial": self.serial
        }

        response = requests.get(url, params=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def getFreeHTIConsistencyGroupId(self):
                
        funcName="hv_infra:getFreeHTIConsistencyGroupId"
        self.logger.writeEnterSDK(funcName)

        urlPath = "TrueCopy/GetFreeLocalConsistencyGroupId"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "serial": self.serial
        }

        response = requests.get(url, params=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def getFreeTCConsistencyGroupId(self):
                
        funcName="hv_infra:getFreeTCConsistencyGroupId"
        self.logger.writeEnterSDK(funcName)

        urlPath = "TrueCopy/GetFreeRemoteConsistencyGroup"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "serial": self.serial
        }

        response = requests.get(url, params=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def getFreeURConsistencyGroupId(self):
                
        funcName="hv_infra:getFreeURConsistencyGroupId"
        self.logger.writeEnterSDK(funcName)

        urlPath = "TrueCopy/GetFreeUniversalReplicatorConsistencyGroup"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "serial": self.serial
        }

        response = requests.get(url, params=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def getQuorumDisks(self):
                
        funcName="hv_infra:getQuorumDisks"
        self.logger.writeEnterSDK(funcName)

        urlPath = "TrueCopy/GetQuorumDisks"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "serial": self.serial
        }

        response = requests.get(url, params=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def getResourceGroups(self):
                
        funcName="hv_infra:getResourceGroups"
        self.logger.writeEnterSDK(funcName)

        urlPath = "ResourceGroup/GetList"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "serial": self.serial
        }

        response = requests.get(url, params=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def getDynamicPools(self):
                
        funcName="hv_infra:getDynamicPools"
        self.logger.writeEnterSDK(funcName)

        urlPath = "StoragePool/GetStoragePools"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def createDynamicPool(self, name, luns, poolType):
                
        funcName="hv_infra:createDynamicPool"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("name={}",name)
        self.logger.writeParam("luns={}",luns)
        self.logger.writeParam("poolType={}",poolType)

        urlPath = "StoragePool/CreateDynamicPool"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "poolName": name,
            "luList": ','.join(map(str, luns)),
            "poolType": PoolCreateType.fromString(poolType)
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def expandDynamicPool(self, poolId, luns):
                
        funcName="hv_infra:expandDynamicPool"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("luns={}",luns)
        self.logger.writeParam("poolId={}",poolId)

        urlPath = "StoragePool/ExpandDynamicPool"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "poolId": poolId,
            "ldevList": ','.join(map(str, luns))
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return
        elif "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def shrinkDynamicPool(self, poolId, luns):
                
        funcName="hv_infra:shrinkDynamicPool"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("luns={}",luns)
        self.logger.writeParam("poolId={}",poolId)

        urlPath = "StoragePool/ShrinkDynamicPoolUsingPoolID"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "poolId": poolId,
            "ldevList": ','.join(map(str, luns))
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return
        elif "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def doPost(self, urlPath, body, returnJson=False):
                
        funcName="hv_infra:doPost"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("urlPath={}",urlPath)
        self.logger.writeParam("body={}",body)
        url = self.getUrl(urlPath)
        self.logger.writeParam("url={}",url)
        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)
        self.logger.writeDebug("response={}",response)
        
        if response.ok:
            self.logger.writeExitSDK(funcName)
            if returnJson:
                self.logger.writeDebug("response.json()={}",response.json())
                return response.json()
            else:
                return
        elif "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def deleteDynamicPool(self, poolId):
                
        funcName="hv_infra:deleteDynamicPool"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("poolId={}",poolId)

        urlPath = "StoragePool/DeleteDynamicPool"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "poolId": poolId
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return
        elif "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

    def setDynamicPoolCapacityThreshold(self, poolId, warningRate, depletionRate, enableNotification):
        urlPath = "StoragePool/SetDynamicPoolCapacityThreshold"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "serialNumber": self.serial,
            "poolId": poolId,
            "warningRate": warningRate,
            "depletionRate": depletionRate,
            "enableNotification": enableNotification
        }

        response = requests.post(url, json=body, verify=self.shouldVerifySslCertification)

        if response.ok:
            return
        elif "HIJSONFAULT" in response.headers:
            raise Exception(json.loads(response.headers["HIJSONFAULT"]))
        else:
            raise Exception("Unknown error HTTP {}".format(response.status_code))

class HostMode:
    modes = [
        "UNKNOWN",          # 0
        "NOT_SPECIFIED",    # 1
        "RESERVED",         # 2
        "LINUX",            # 3
        "VMWARE",           # 4
        "HP",               # 5
        "OPEN_VMS",         # 6
        "TRU64",            # 7
        "SOLARIS",          # 8
        "NETWARE",          # 9
        "WINDOWS",          # 10
        "HI_UX",            # 11
        "AIX",              # 12
        "VMWARE_EXTENSION", # 13
        "WINDOWS_EXTENSION",# 14
        "UVM",              # 15
        "HP_XP",            # 16
        "DYNIX",            # 17
    ]

    @staticmethod
    def getHostModeNum(hm):
        hostmode = hm.upper()

        if hostmode == "STANDARD":
            hostmode = "LINUX"
        hostmode = re.sub(r"WIN($|_)", r"WINDOWS\1", hostmode)
        hostmode = re.sub(r"EXT?$", "EXTENSION", hostmode)

        if hostmode not in HostMode.modes:
            raise Exception("Invalid host mode: '{}'".format(hm))

        return HostMode.modes.index(hostmode)

    @staticmethod
    def getHostModeName(hostmode):
        if isinstance(hostmode, str):
            return hostmode
        return HostMode.modes[hostmode]


class SNAPSHOT_OPTION(Enum):
    SSOPTION_HIDE_AND_DISABLE_ACCESS = 0
    SSOPTION_HIDE_AND_ALLOW_ACCESS   = 1
    SSOPTION_SHOW_AND_ALLOW_ACCESS   = 3

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

