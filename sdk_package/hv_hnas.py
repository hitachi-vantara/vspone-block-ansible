import json
import requests

from ansible.module_utils.hv_log import Log, HiException

class HNASFileServer:
    connectorPath = "/storage-connectors.json"

    def __init__(self):
        
        try:
            
            HNASFileServer.connectorPath = Log.getHomePath() + HNASFileServer.connectorPath
            
            with open(HNASFileServer.connectorPath) as connectionFile:
                self.connections = json.load(connectionFile)

            if "HNASFileServer" not in self.connections:
                raise Exception("nasStorageSystems is not found, please check the storage.json.")
                
            system = self.connections["HNASFileServer"]
                                    
            self.sessionId = system["sessionId"]
            webServiceIp = system["storageGateway"]
            webServicePort = system["storageGatewayPort"]
        except IOError as ex:
            raise Exception("Storage systems have not been registered. Please run add_storagesystems.yml first.")

        self.logger=Log()
        self.webServiceIp = webServiceIp
        self.webServicePort = webServicePort
        self.basedUrl = "https://{0}:{1}".format(webServiceIp, webServicePort)
        self.shouldVerifySslCertification = False

    def isSessionNotFound(self, exMsg):
        strToMatch = "Session " +self.sessionId+ " is not found"
        if strToMatch in str(exMsg):
            return True
        else:
            return False
        
    def getUrl(self, urlPath):
        return "{0}/HitachiStorageManagementWebServices/{1}".format(self.basedUrl, urlPath)

    def addFileServerIfNotPresent(self, fileServerIP, username, password):
        funcName="hv_hnas.addFileServerIfNotPresent"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("fileServerIP={}",fileServerIP)
        self.logger.writeParam("username={}",username)
        
        fileServers = self.connections.get("fileServers", [])
        if fileServerIP not in fileServers:
            self.addFileServer(fileServerIP, username, password)
            fileServers.append(fileServerIP)
            self.connections["fileServers"] = fileServers
            with open(HNASFileServer.connectorPath, 'w') as connectionFile:
                json.dump(self.connections, connectionFile)
        
        self.logger.writeExitSDK(funcName)

    def addFileServer(self, fileServerIP, username, password):
        funcName="hv_hnas.addFileServer"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("fileServerIP={}",fileServerIP)
        self.logger.writeParam("sessionId={}",self.sessionId)
        self.logger.writeParam("webServiceIp={}",self.webServiceIp)
        self.logger.writeParam("username={}",username)
        
        urlPath = "NAS/StorageManager/AddFileServer"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "fileServer": fileServerIP,
            "userID": username,
            "password": password,
            "gatewayServer": self.webServiceIp,
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

    def getFileServerInfo(self, fileServerIP):
        
        funcName="hv_hnas.getFileServerInfo"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("fileServerIP={}",fileServerIP)
        
        urlPath = "NAS/StorageManager/GetFileServerInfo2"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "fileServer": fileServerIP
        }

        try:
            response = requests.get(url, params=body, verify=self.shouldVerifySslCertification)
    
            if response.ok:
                return response.json()
            elif "HIJSONFAULT" in response.headers:
                ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
                hiex = HiException(ex)
                self.logger.writeHiException(hiex)
                raise hiex
            else:
                raise Exception("Unknown error HTTP {}".format(response.status_code))
        finally:
            self.logger.writeExit(funcName)
            

    def getEnterpriseVirtualServers(self, fileServerIP):
        funcName="hv_hnas.getEnterpriseVirtualServers"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("fileServerIP={}",fileServerIP)

        urlPath = "NAS/FileSystem/GetEnterpriseVirtualSystems"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "fileServer": fileServerIP
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

    def getFileSystems(self, fileServerIP):
        funcName="hv_hnas.getFileSystems"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("fileServerIP={}",fileServerIP)

        urlPath = "NAS/FileSystem/GetAllFileSystems"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "fileServer": fileServerIP
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

    def getFileSystem(self, fileServerIP, fileSystem):
        funcName="hv_hnas.getFileSystem"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("fileServerIP={}",fileServerIP)
        self.logger.writeParam("fileSystem={}",fileSystem)

        urlPath = "NAS/FileSystem/GetFileSystem"
        url = self.getUrl(urlPath)
        body = {
            "sessionId": self.sessionId,
            "fileServer": fileServerIP,
            "fileSystem": fileSystem
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

    def createNFSExport(self, fileServerIP, evs, name, fileSystem, fsPath, accessConfig, 
                        snapshotOption, localReadCacheOption, transferToReplicationTargetSetting):
        funcName="hv_hnas.createNFSExport"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("fileServerIP={}",fileServerIP)
        self.logger.writeParam("evs={}",evs)
        self.logger.writeParam("name={}",name)
        self.logger.writeParam("fileSystem={}",fileSystem)
        self.logger.writeParam("fsPath={}",fsPath)
        self.logger.writeParam("accessConfig={}",accessConfig)
        
        urlPath = "NAS/NFSExport/CreateNFSExport"
        url = self.getUrl(urlPath)
        
        body = {
            "sessionId": self.sessionId,
            "fileServer": fileServerIP,
            "evs": evs,
            "fileSystem": fileSystem
        }
        
        # TODO: Proper enums for snapshot option, local read cache option, transfer to replication setting
        #"snapshotOption": snapshotOption,
        #"localReadCacheOption": localReadCacheOption,
        #"transferToReplicationTargetSetting": transferToReplicationTargetSetting
        if name is not None:
            body["exportName"] = name
        if accessConfig is not None:
            body["accessConfig"] = accessConfig
        if fsPath is not None:
            body["fileSystemPath"] = fsPath
        if snapshotOption is not None:
            body["snapshotOption"] = snapshotOption
        if localReadCacheOption is not None:
            body["localReadCacheOption"] = localReadCacheOption
        if transferToReplicationTargetSetting is not None:
            body["transferToReplicationTargetSetting"] = transferToReplicationTargetSetting
            

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

    def deleteNFSExport(self, fileServerIP, evs, name):
        funcName="hv_hnas.deleteNFSExport"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("fileServerIP={}",fileServerIP)
        self.logger.writeParam("evs={}",evs)
        self.logger.writeParam("name={}",name)

        urlPath = "NAS/NFSExport/DeleteNFSExport"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "fileServer": fileServerIP,
            "evs": evs,
            "exportName": name
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

    def getNFSExports(self, fileServerIP, evs):
        funcName="hv_hnas.getNFSExports"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("fileServerIP={}",fileServerIP)
        self.logger.writeParam("evs={}",evs)

        urlPath = "NAS/NFSExport/GetNFSExports"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "fileServer": fileServerIP,
            "evs": evs
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

    def getNFSExportsByName(self, fileServerIP, evs, namePattern):
        funcName="hv_hnas.getNFSExportsByName"
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam("fileServerIP={}",fileServerIP)
        self.logger.writeParam("evs={}",evs)
        self.logger.writeParam("namePattern={}",namePattern)

        urlPath = "NAS/NFSExport/GetNFSExportByName"
        url = self.getUrl(urlPath)

        body = {
            "sessionId": self.sessionId,
            "fileServer": fileServerIP,
            "evs": evs,
            "exportNamePattern": namePattern
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
