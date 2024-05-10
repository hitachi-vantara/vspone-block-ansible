#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2020, Hewlett Packard Enterprise Development LP.

__metaclass__ = type

import json
import time

try:
    import requests
except ImportError as error:

    # Output expected ImportErrors.
    # print("enum module not found")

    pass

from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log, \
    HiException
from ansible_collections.hitachi.storage.plugins.module_utils.hv_ucpmanager import UcpManager


class StorageManager:

    def __init__(
        self,
        ucpadvisor_address,
        ucpadvisor_ansible_vault_user,
        ucpadvisor_ansible_vault_secret,
        storage_serial,
        ucp_serial,
        webServicePort=None,
        sessionId=None,
    ):
        funcName = 'hv_storagemanager:init'
        self.logger = Log()
        self.logger.writeEnterSDK(funcName)
        self.dryRun = False

        self.sessionId = sessionId
        self.webServicePort = webServicePort
        self.shouldVerifySslCertification = False
        self.ucpadvisor_address = ucpadvisor_address
        self.ucpadvisor_ansible_vault_user = ucpadvisor_ansible_vault_user
        self.ucpadvisor_ansible_vault_secret = ucpadvisor_ansible_vault_secret
        self.storage_serial = storage_serial
        self.ucp_serial = ucp_serial
        self.basedUrl = 'https://{0}'.format(ucpadvisor_address)

        if ucpadvisor_ansible_vault_user is None or \
           ucpadvisor_ansible_vault_secret is None or \
           ucpadvisor_address is None or \
           ucpadvisor_ansible_vault_user == '' or \
           ucpadvisor_ansible_vault_secret == '' or \
           ucpadvisor_address == '' :
            raise Exception( "UCPA is not configured.")

        if storage_serial is None or \
           storage_serial == '' :
            raise Exception( "Storage system is not configured.")
        
        if self.ucp_serial == '':
            raise Exception( "UCP name is invalid.")
        
        if ucp_serial is None :
            raise Exception( "UCP name is not valid.")
        
        try:
            self.ucpManager = UcpManager(
                self.ucpadvisor_address,
                self.ucpadvisor_ansible_vault_user,
                self.ucpadvisor_ansible_vault_secret
                )
        except Exception as ex:
            raise Exception( "UCPA is not configured.")


    #################################################################
    #################################################################

    def throwException(self, response):
        self.logger.writeInfo('throwException, response={}',response)
        raise Exception('{0}:{1}'.format(response.status_code, response.json().get('error')))

    ## helper func
    def isStorageSystemInUcpSystem(self):
        funcName = 'hv_storagemanager:isStorageSystemInUcpSystem'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeDebug('storage_serial={}',self.storage_serial)
        self.logger.writeDebug('ucp_serial={}',self.ucp_serial)

        theUCP = self.ucpManager.getUcpSystem(self.ucp_serial)
        self.logger.writeInfo('theUCP={}', theUCP)

        if theUCP is None:
            raise Exception('The UCP is not found xxx.')

        for x in theUCP.get('storageDevices'):
                ss = x.get('serialNumber')
                self.logger.writeDebug('ss={}',ss)
                ss = str(ss)
                self.logger.writeDebug('ss={}',ss)
                if ss == str(self.storage_serial):
                    return True
                     
        self.logger.writeExitSDK(funcName)
        return False    

    # returns ss and ucp grid if ss is found
    # else throws exception
    def getStorageSystemResourceId(self):
        """
        docstring
        """

        funcName = 'hv_storagesystem:getStorageSystemResourceId'
        self.logger.writeEnterSDK(funcName)
        headers = self.ucpManager.getAuthToken()
        self.logger.writeParam('headers={}', headers)

        urlPath = 'v2/storage/devices'
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeParam('url={}', url)

        systems = self.getAllStorageSystems()

        self.logger.writeInfo('systems={}', systems)

        system = None
        for x in systems:
            self.logger.writeInfo(int(x['serialNumber']))
            self.logger.writeInfo(self.storage_serial)
            self.logger.writeInfo(int(x['serialNumber'])
                                   == self.storage_serial)

            if str(x['serialNumber']) == str(self.storage_serial):
                system = x
                break
        if system is None:
            raise Exception('Invalid serial = {0}, please check once and try again.'.format(self.storage_serial))

        ucp = system.get('ucpSystems')[0]
        self.logger.writeExitSDK(funcName)
        return (str(system.get('resourceId')), str(ucp))

    def getStorageSystemResourceIdInISP(self):
        """
        docstring
        """

        funcName = 'hv_storagesystem:getStorageSystemResourceIdInISP'
        self.logger.writeEnterSDK(funcName)
        headers = self.ucpManager.getAuthToken()
        # self.logger.writeParam('headers={}', headers)

        urlPath = 'v2/storage/devices'
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeParam('url={}', url)

        systems = self.getAllISPStorageSystems()

        self.logger.writeDebug('systems={}', systems)
        self.logger.writeDebug('20230606 self.storage_serial={}', self.storage_serial)

        system = None
        for x in systems:
            self.logger.writeInfo(int(x['serialNumber']))
            self.logger.writeInfo(self.storage_serial)
            self.logger.writeInfo(int(x['serialNumber'])
                                   == self.storage_serial)
            if str(x['serialNumber']) == str(self.storage_serial):
                system = x
                break
        if system is None:
            raise Exception('Invalid serial = {0}, please check once and try again.'.format(self.storage_serial))

        self.logger.writeExitSDK(funcName)
        return (str(system.get('resourceId')))    

    def getAllISPStorageSystems(self):
        funcName = 'hv_storagemanager:getAllISPStorageSystems'
        self.logger.writeEnterSDK(funcName)

        urlPath = 'v2/systems/default'
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()

        self.logger.writeDebug('url={}', url)
        # self.logger.writeDebug('headers={}', headers)
        response = requests.get(url, headers=headers, verify=self.shouldVerifySslCertification)
        self.logger.writeDebug('response={}', response)

        storage_systems = []
        if response.ok:
            authResponse = response.json()
            # self.logger.writeDebug('ISP response Json={}', authResponse)
            data = authResponse.get('data')
            storage_systems.extend(data.get('storageDevices'))
        else:
            raise Exception(response)
        
        return storage_systems

    def getAllLuns(self):

        funcName = 'hv_storagemanager:getAllLuns'
        self.logger.writeEnterSDK(funcName)
        resourceId = self.getStorageSystemResourceIdInISP()
        # (resourceId, ucp) = self.getStorageSystemResourceId()
        self.logger.writeInfo('Storage_resource_id={0}'.format(resourceId))
        # urlPath = 'v2/storage/devices/{0}/volumes?refresh=false'.format(resourceId)
        urlPath = 'v2/storage/devices/{0}/volumes?fromLdevId=0&toLdevId=64000&refresh=false'.format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeParam('20230620 urlPath={}', url)
        headers = self.ucpManager.getAuthToken()
        response = requests.get(url, headers=headers,
                                verify=self.shouldVerifySslCertification)

        ## too much to dump
        # self.logger.writeDebug('response.json()={}', response.json())
        self.logger.writeDebug('20230620 response.ok={}',response.ok)
        if response.ok:
            respjson = response.json()
            # if respjson.status >= 300 :
            #     self.logger.writeDebug('respjson.status={}', respjson.status)
            #     raise Exception('status={}, error={}', respjson.status, respjson.error)            
            self.logger.writeDebug('get data json')
            respjson = response.json()['data']
            self.logger.writeExitSDK(funcName)
            return respjson
        else:
            raise Exception(response)

    def getLunByID(self, ldevid):

        funcName = 'hv_storagemanager:getLunByID'
        self.logger.writeEnterSDK(funcName)
        resourceId = self.getStorageSystemResourceIdInISP()
        # (resourceId, ucp) = self.getStorageSystemResourceId()
        self.logger.writeDebug('Storage_resource_id={0}'.format(resourceId))
        self.logger.writeDebug('str(ldevid)={0}'.format(str(ldevid)))
        self.logger.writeDebug('str(ldevid+10)={0}'.format(str(int(ldevid)+10)))
        # urlPath = 'v2/storage/devices/{0}/volumes?refresh=false'.format(resourceId)
        urlPath = 'v2/storage/devices/{0}/volumes?fromLdevId={1}&toLdevId={2}&refresh=false'.format(resourceId,str(0),str(int(ldevid)*2))
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeParam('20230620 urlPath={}', url)
        headers = self.ucpManager.getAuthToken()
        response = requests.get(url, headers=headers,
                                verify=self.shouldVerifySslCertification)

        ## too much to dump
        # self.logger.writeDebug('response.json()={}', response.json())
        self.logger.writeDebug('20230620 response.ok={}',response.ok)
        if response.ok:
            self.logger.writeDebug('get data json')
            items = response.json()['data']
            if items is None or len(items) == 0 :
                items = None
            self.logger.writeExitSDK(funcName)
            return items
        else:
            raise Exception(response)

    def getLun(self, lun, doRetry=True):

        funcName = 'hv_storagemanager:getLun'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lun={}', lun)

        self.logger.writeInfo('20230617 looking for lun={}', lun)

        # luns = self.getAllLuns()
        ## getLunByID replaces getAllLuns,
        ## it uses the lun input id for the range to look for the lun
        luns = self.getLunByID(lun)
        foundlun = None
        for item in luns:
            # self.logger.writeDebug('ldevId={}', str(item['ldevId']))
            # self.logger.writeDebug('lun={}', str(lun))
            try:
                if str(item['ldevId']) == str(lun):
                    foundlun = item
                    self.logger.writeInfo('foundlun={}', foundlun)
                    break
            except Exception as e:
                self.logger.writeInfo(str(e))

        self.logger.writeDebug('foundlun={}', foundlun)
        if foundlun == None:
            self.logger.writeInfo('lun {} not found', lun)
            
        self.logger.writeExitSDK(funcName)
        return foundlun

    def getLunByNaa(self, canonicalName):

        funcName = 'hv_storagemanager:getLunByNaa'
        self.logger.writeEnterSDK(funcName)

        canonicalName = str(canonicalName).upper()
        manufacturerCode = "60060"
        if len(canonicalName) == 36 and canonicalName.find("NAA") == 0 and canonicalName.find(manufacturerCode) > 0:
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

            self.storage_serial = int(storageSerial)
            self.logger.writeInfo("storageSerial={0}".format(self.storage_serial))

            lun = int(lunCode, 16)
            self.logger.writeInfo("lun={0}".format(lun))
            self.logger.writeExitSDK(funcName)
            return self.getLun(lun)

    def updateLunInDP(
        self,
        lunResourceId,
        size
    ):
        funcName = 'hv_storagemanager:updateLunInDP'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lunResourceId={}', lunResourceId)
        self.logger.writeParam('size={}', size)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam('resourceId={}', resourceId)
        self.logger.writeParam('lunResourceId={}', lunResourceId)
        self.logger.writeParam('ucp={}', ucp)

        urlPath = 'v2/storage/devices/{0}/volumes/{1}'.format(
            resourceId, lunResourceId)
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeInfo('url={}', url)
        body = {
            # 'capacity': str(size) + 'GB'
            'capacity': size
        }
        self.logger.writeInfo('body={}', body)
        headers = self.ucpManager.getAuthToken()
        self.logger.writeInfo('headers={}', headers)
        response = requests.patch(url, json=body, headers=headers,
                                  verify=self.shouldVerifySslCertification)
        self.logger.writeInfo('response={}', response.json())
        if response.ok:
            # resourceId = response.json()['data']['resourceId']
            # self.logger.writeInfo('resourceId={}', resourceId)
            taskId = response.json()['data'].get('taskId')
            self.ucpManager.checkTaskStatus(taskId)
            time.sleep(10)
            self.logger.writeExitSDK(funcName)
        else:
            self.logger.writeDebug('response not ok={}', response)
            raise Exception(response.text())

    def getAllStorageSystems(self):
        funcName = 'hv_storagesystem:getAllStorageSystems'
        self.logger.writeEnterSDK(funcName)

        # get storage in each UCP
        urlPath = 'v2/storage/devices'
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeInfo('url={}', url)

        ucp_systems = self.ucpManager.getAllUcpSystem()
        self.logger.writeInfo('getAllStorageSystems, loop thru each ucp and get list of storages')

        storage_systems = []
        for ucp in ucp_systems:
            sn = str(ucp.get('serialNumber'))
            self.logger.writeInfo(sn)
            body = {'ucpSystem': sn}
            self.logger.writeInfo('body={}', body)
            headers = self.ucpManager.getAuthToken()

            self.logger.writeInfo('getAllStorageSystems for ucp_serial={}', sn)
            response = requests.get(url, headers=headers, params=body,
                                    verify=self.shouldVerifySslCertification)

            if response.ok:
                authResponse = response.json()
                systems = authResponse.get('data')
                storage_systems.extend(systems)
            elif 'HIJSONFAULT' in response.headers:
                Utils.raiseException( response)
            else:
                self.throwException(response)

        self.logger.writeExitSDK(funcName)
        return storage_systems

    def getStorageSystem(self):
        """
        docstring
        """
        funcName = 'hv_storagesystem:getStorageSystem'
        self.logger.writeEnterSDK(funcName)

        systems = self.fetchStorageSystems()
        # self.logger.writeDebug('systems={}', systems)

        system = None
        for x in systems:
            self.logger.writeInfo(int(x['serialNumber']))
            self.logger.writeInfo(self.storage_serial)
            if str(x['serialNumber']) == str(self.storage_serial):
                system = x
                break
            
        self.logger.writeInfo('system={}', system)
        result = self.formatStorageSystem(system)

        self.logger.writeExitSDK(funcName)
        return result


    #################################################################
    #################################################################

    def createLunInDP(
        self,
        lun,
        pool,
        size,
        dedup,
        name='',
    ):
        funcName = 'hv_storagemanager:createLunInDP'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lun={}', lun)
        self.logger.writeParam('pool={}', pool)
        self.logger.writeParam('sizeInGB={}', size)
        self.logger.writeParam('luName={}', name)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam('resourceId={}', resourceId)
        self.logger.writeParam('ucp={}', ucp)

        urlPath = 'v2/storage/devices/{0}/volumes'.format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeDebug('url={}', url)
        body = {
            'deduplicationCompressionMode': dedup,
            'poolId': pool,
            'name': name,
            'capacity': size,
            'resourceGroupId': 0,
            'ucpSystem': ucp,
        }
        if lun is not None:
            body['lunId'] = lun
        self.logger.writeDebug('body={}', body)
        headers = self.ucpManager.getAuthToken()
        # self.logger.writeInfo('headers={}', headers)
        response = requests.post(url, json=body, headers=headers,
                                 verify=self.shouldVerifySslCertification)
        self.logger.writeDebug('response={}', response.json())
        if response.ok:
            self.logger.writeDebug('resourceId={}', resourceId)
            taskId = response.json()['data'].get('taskId')
            self.logger.writeDebug('taskId={}', taskId)
            self.ucpManager.checkTaskStatus(taskId)
            time.sleep(5)
            if lun is None:
                lun = self.getLunIdFromTaskStatusEvents(taskId)
            self.logger.writeExitSDK(funcName)
            return lun
        else:
            self.logger.writeExitSDK(funcName)
            self.logger.writeDebug('response={}', response)
            if response.status_code == 422:
                raise Exception("The lun name is invalid.")
            else:
                ## this is how to handle porcleain error 400 or 500,
                ## return the error message
                rjson = response.json()
                raise Exception(rjson['error'])

    def createLunInPG(
        self,
        lun,
        parityGroup,
        size,
        stripeSize,
        metaResourceSerial,
        luName,
    ):

        funcName = 'hv_storagemanager:createLunInPG'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lun={}', lun)
        self.logger.writeParam('parityGroupId={}', parityGroup)
        self.logger.writeParam('sizeInGB={}', size)
        self.logger.writeParam('luName={}', luName)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam('resourceId={}', resourceId)
        self.logger.writeParam('ucp={}', ucp)

        urlPath = 'v2/storage/devices/{0}/volumes'.format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeDebug('url={}', url)
        body = {
            'parityGroupId': parityGroup,
            'name': luName,
            'capacity': size,
            'resourceGroupId': 0,
            'ucpSystem': ucp,
        }
        if lun is not None:
            body['lunId'] = lun
        self.logger.writeDebug('body={}', body)
        headers = self.ucpManager.getAuthToken()
        # self.logger.writeInfo('headers={}', headers)
        response = requests.post(url, json=body, headers=headers,
                                 verify=self.shouldVerifySslCertification)
        self.logger.writeDebug('response={}', response.json())
        if response.ok:
            # resourceId = response.json()['data']['resourceId']
            # self.logger.writeInfo('resourceId={}', resourceId)
            taskId = response.json()['data'].get('taskId')
            self.ucpManager.checkTaskStatus(taskId)
            time.sleep(5)

            self.logger.writeDebug('20230617 exiting {} lun={}', funcName, lun)
            if lun is None:
                ## ldevid was not given in the input
                ## get the newly created lun ldevid
                lun = self.getLunIdFromTaskStatusEvents(taskId)
            self.logger.writeDebug('20230617 exiting {} lun={}', funcName, lun)

            self.logger.writeExitSDK(funcName)
            return lun
        else:
            self.logger.writeDebug('response={}', response)
            raise Exception(response)

    ### this func does expand size, change dedup, and lun name
    def updateLunName(self,
        lunResourceId,
        lunName):
        funcName = 'StorageManager:updateLunName'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lunResourceId={}', lunResourceId)
        self.logger.writeParam('sizeInGB={}', lunName)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam('resourceId={}', resourceId)
        self.logger.writeParam('lunResourceId={}', lunResourceId)
        self.logger.writeParam('ucp={}', ucp)

        urlPath = 'v2/storage/devices/{0}/volumes/{1}'.format(
            resourceId, lunResourceId)
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeInfo('url={}', url)
        body = {
            'lunName': lunName
        }
        self.logger.writeInfo('body={}', body)
        headers = self.ucpManager.getAuthToken()
        self.logger.writeInfo('headers={}', headers)
        response = requests.patch(url, json=body, headers=headers,
                                  verify=self.shouldVerifySslCertification)
        self.logger.writeInfo('response={}', response.json())
        if response.ok:
            # resourceId = response.json()['data']['resourceId']
            # self.logger.writeInfo('resourceId={}', resourceId)
            taskId = response.json()['data'].get('taskId')
            self.ucpManager.checkTaskStatus(taskId)
            time.sleep(10)
            self.logger.writeExitSDK(funcName)
        else:
            self.logger.writeDebug('response={}', response)
            if response.status_code == 422:
                raise Exception("The lun name is invalid.")
            else:
                raise Exception(response.status_code)

    def setDedupCompression(self, lunResourceId, dedupMode):
        funcName = 'hv_storagemanager:setDedupCompression'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lunResourceId={}', lunResourceId)
        self.logger.writeParam('dedupMode={}', dedupMode)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam('resourceId={}', resourceId)
        self.logger.writeParam('lunResourceId={}', lunResourceId)
        self.logger.writeParam('ucp={}', ucp)

        urlPath = 'v2/storage/devices/{0}/volumes/{1}'.format(
            resourceId, lunResourceId)
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeInfo('url={}', url)
        body = {
            'deduplicationCompressionMode': dedupMode
        }
        self.logger.writeInfo('body={}', body)
        headers = self.ucpManager.getAuthToken()
        self.logger.writeInfo('headers={}', headers)
        response = requests.patch(url, json=body, headers=headers,
                                  verify=self.shouldVerifySslCertification)
        self.logger.writeInfo('response={}', response.json())
        if response.ok:
            # resourceId = response.json()['data']['resourceId']
            # self.logger.writeInfo('resourceId={}', resourceId)
            taskId = response.json()['data'].get('taskId')
            self.ucpManager.checkTaskStatus(taskId)
            time.sleep(10)
            self.logger.writeExitSDK(funcName)
        else:
            self.logger.writeDebug('response={}', response)
            ## this is how to handle porcleain error 400 or 500,
            ## return the error message
            rjson = response.json()
            raise Exception(rjson['error'])

    def cloneLunInDP(
        self,
        sourceLun,
        pool,
        clonedLunName,
    ):

        funcName = 'hv_storagemanager:cloneLunInDP'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('sourceLun={}', sourceLun)
        self.logger.writeParam('pool={}', pool)
        self.logger.writeParam('clonedLunName={}', clonedLunName)

        urlPath = 'LogicalUnit/LogicalUnit/CloneInDP'
        url = self.ucpManager.getUrl(urlPath)
        body = {
            'sessionId': self.sessionId,
            'serialNumber': self.storage_serial,
            'lun': sourceLun,
            'pool': pool,
            'lunName': clonedLunName,
        }

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            taskId = response.json()['data'].get('taskId')
            return self.ucpManager.checkTaskStatus(taskId)
        else:
            self.logger.writeDebug('response={}', response)
            raise Exception(response)

    def deleteLun(self, lunResourceId):
        funcName = 'hv_storagemanager:deleteLun'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lunResourceId={}', lunResourceId)
        (storageResourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = \
            'v2/storage/devices/{0}/volumes/{1}'.format(storageResourceId,
                                                        lunResourceId)
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        self.logger.writeParam('url={}', url)
        response = requests.delete(url, headers=headers,
                                   verify=self.shouldVerifySslCertification)

        self.logger.writeInfo(response.status_code)
        if response.ok:
            # resourceId = response.json()['data']['resourceId']
            # self.logger.writeInfo('resourceId={}', resourceId)
            taskId = response.json()['data'].get('taskId')
            self.ucpManager.checkTaskStatus(taskId)
            time.sleep(10)
            self.logger.writeExitSDK(funcName)
            return True
        else:
            self.logger.writeDebug('response={}', response)
            raise Exception(response)

    def getLunIdFromTaskStatusEvents(self, taskId):
        funcName = 'hv_storagemanager:getLunIdFromTaskStatusEvents'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('taskId={}', taskId)
        headers = self.ucpManager.getAuthToken()
        urlPath = '/v2/tasks/{0}'.format(taskId)
        url = self.ucpManager.getUrl(urlPath)
        response = requests.get(url, headers=headers,
                                verify=self.shouldVerifySslCertification)
        self.logger.writeDebug('response={}', response)
        status = None
        name = None
        lun = None
        if response.ok:
            status = response.json()['data'].get('status')
            name = response.json()['data'].get('name')

        if status.lower() == 'success':
            events = response.json()['data'].get('events')
            description = events[0].get('description')
            self.logger.writeInfo(description)
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

            parsedLun = '20230617 parsedLun={0}'.format(lun)
            self.logger.writeInfo(parsedLun)
        self.logger.writeExitSDK(funcName)
        return lun.strip()


    @staticmethod
    def formatStorageSystem(storageSystem):
        funcName = 'hv_storagemanager:StorageSystemManager:formatStorageSystem'
        UcpManager.logger.writeEnterSDK(funcName)

        # UcpManager.logger.writeDebug('storageSystem={}',storageSystem)
        if storageSystem is None:
            UcpManager.logger.writeDebug('storageSystem is None')
            return

        storageSystem.pop('resourceId', None)
        storageSystem.pop('storageEfficiencyStat', None)
        storageSystem.pop('storageDeviceLicenses', None)
        storageSystem.pop('isUnified', None)
        storageSystem.pop('tags', None)
        storageSystem.pop('deviceType', None)
        # storageSystem.pop('ucpSystems', None)
        storageSystem.pop('username', None)

        UcpManager.logger.writeExitSDK(funcName)
        return storageSystem

    # fetch the SS CRs
    def fetchStorageSystems(self):
        funcName = 'hv_storagemanager:fetchStorageSystems'
        self.logger.writeEnterSDK(funcName)

        headers = self.ucpManager.getAuthToken()
        urlPath = 'v2/storage/devices'
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeParam('url={}', url)
        response = requests.get(url, headers=headers, verify=self.shouldVerifySslCertification)
        self.logger.writeDebug('response={}', response)

        storage_systems = []
        if response.ok:
            authResponse = response.json()
            # self.logger.writeDebug('ISP response Json={}', authResponse)
            data = authResponse.get('data')
            # storage_systems.extend(data.get('storageDevices'))
            storage_systems = data
            
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException( response)
        else:
            self.throwException(response)

        self.logger.writeExitSDK(funcName)
        return storage_systems

###################################################################
########## Host Groups
###################################################################

    ## this will take time for OOB
    def getAllHostGroups(self):

        funcName = 'hv_storagemanager:getAllHostGroups'
        self.logger.writeEnterSDK(funcName)
      
        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = 'v2/storage/devices/{0}/hostGroups?refresh=false'.format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        response = requests.get(url, headers=headers,
                                verify=self.shouldVerifySslCertification)
        if response.ok:
            # self.logger.writeInfo('response.json()={}',
            #                        response.json())
            self.logger.writeExitSDK(funcName)
            return response.json()['data']
        else:
            self.throwException(response)


    def createHostGroup(
        self,
        hgName,
        port,
        wwnList,
        hostmode,
        hostModeOptions
    ):

        funcName = 'hv_storagemanager:createHostGroup'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('wwnList={}', wwnList)
        self.logger.writeParam('hgName={}', hgName)
        self.logger.writeParam('hostmode={}', hostmode)
        self.logger.writeParam('hostModeOptions={}', hostModeOptions)
        self.logger.writeParam('port={}', port)
        self.logger.writeParam('dryRun={}', self.dryRun)
        if self.dryRun:
            return

        (resourceId, ucp) = self.getStorageSystemResourceId()
        self.logger.writeParam('resourceId={}', resourceId)
        self.logger.writeParam('ucp={}', ucp)

        wwns=[]
        if len(wwnList) >0 :
            for x in list(wwnList):
                wwns.append( {
                        "id": x
                    })
        self.logger.writeParam('wwns={}', wwns)
        
        body = {
            'hostGroupName': str(hgName),
            'port': str(port),
            'ucpSystem': ucp,
            'hostMode': hostmode
            # 'hostModeOptions': list(hostModeOptions)
        }

        if hostModeOptions is not None :
            body['hostModeOptions']=list(hostModeOptions)
        if len(wwns) >0 :
            body['wwns']=wwns

        self.logger.writeParam('body={}', body)
        urlPath = 'v2/storage/devices/{0}/hostGroups'.format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeDebug('url={}', url)
        self.logger.writeDebug('body={}', body)
        headers = self.ucpManager.getAuthToken()
        response = requests.post(url, headers=headers, json=body,
                                 verify=self.shouldVerifySslCertification)
        if not response.ok:
            self.throwException(response)
        else:
            taskId = response.json()['data'].get('taskId')
            self.ucpManager.checkTaskStatus(taskId)

        self.logger.writeExitSDK(funcName)

    def getHostGroup(
        self,
        hgName,
        port,
        doRetry=True,
    ):

        funcName = 'hv_storagemanager:getHostGroup'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('hgName={}', hgName)
        self.logger.writeParam('port={}', port)
        (resourceId, ucp) = self.getStorageSystemResourceId()
        hostgroups = self.getAllHostGroups()

        hostgroup = None
        for x in hostgroups:
            if x.get('hostGroupName') == hgName and x.get('port') \
                    == port:
                hostgroup = x
                self.logger.writeInfo('Found HostGroup')
                break

        self.logger.writeExitSDK(funcName)
        return hostgroup

    def deleteHostGroup(self, hgName, port):

        funcName = 'hv_storagemanager:deleteHostGroup'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('hgName={}', hgName)
        self.logger.writeParam('port={}', port)
        self.logger.writeParam('dryRun={}', self.dryRun)
        if self.dryRun:
            return
        (resourceId, ucp) = self.getStorageSystemResourceId()
        hostgroups = self.getAllHostGroups()
        hostgroup = None
        for x in hostgroups:
            if x.get('hostGroupName') == hgName and x.get('port') == port:
                hostgroup = x
                break

        if hostgroup is None:
            self.logger.writeInfo("Host group is not found.")
            self.logger.writeExitSDK(funcName)
            return                      

        hgResourceId = hostgroup.get('resourceId')
        urlPath = 'v2/storage/devices/{0}/hostGroups/{1}'.format(
            resourceId, hgResourceId)
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        response = requests.delete(url, headers=headers,
                                   verify=self.shouldVerifySslCertification)
        if not response.ok:
            self.throwException(response)
        else:
            self.logger.writeInfo(response)
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

        funcName = 'hv_storagemanager:setHostMode'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('hgName={}', hgName)
        self.logger.writeParam('port={}', port)
        self.logger.writeParam('hostmode={}', hostmode)
        self.logger.writeParam('hostopt={}', hostopt)
        self.logger.writeParam('dryRun={}', self.dryRun)
        if self.dryRun:
            return

        # urlPath = 'HostGroup/HostGroup/SetHostMode'
        (resourceId, ucp) = self.getStorageSystemResourceId()
        
        self.logger.writeParam('storageresourceId={}', resourceId)
        hostgroup = self.getHostGroup(hgName, port)
        hgResourceId = hostgroup.get('resourceId')
        self.logger.writeParam('hgResourceId={}', hgResourceId)
        self.logger.writeParam('ucp={}', ucp)
        urlPath = 'v2/storage/devices/{0}/hostgroups/{1}'.format(resourceId, hgResourceId)
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        body = {
            'hostMode': hostmode,
            'hostModeOptions': list(map(int, hostopt)),
        }

        self.logger.writeInfo(url)
        self.logger.writeInfo(body)
        response = requests.patch(url, json=body, headers=headers,
                                 verify=self.shouldVerifySslCertification)
        self.logger.writeInfo('response={}', response)
     
        if not response.ok:
            self.throwException(response)
        else:
            taskId = response.json()['data'].get('taskId')
            self.ucpManager.checkTaskStatus(taskId)
            time.sleep(5)

        self.logger.writeExitSDK(funcName)


    def presentLun(
        self,
        luns,
        hgName,
        port,
    ):

        funcName = 'hv_storagemanager:presentLun'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lun={}', luns)
        self.logger.writeParam('hgName={}', hgName)
        self.logger.writeParam('port={}', port)
        self.logger.writeParam('dryRun={}', self.dryRun)
        if self.dryRun:
            return
        (resourceId, ucp) = self.getStorageSystemResourceId()
        hostgroups = self.getAllHostGroups()

        # hostgroup = next(x for x in hostgrpups if x.hostGroupName == hgName and x.port == port)

        hostgroup = None
        for x in hostgroups:
            if x.get('hostGroupName') == hgName and x.get('port') == port:
                hostgroup = x
                break

        hgResourceId = hostgroup.get('resourceId')
        urlPath = '/v2/storage/devices/{0}/hostGroups/{1}/volumes'.format(resourceId,
                                                                          hgResourceId)
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        body = {'ldevIds': list(map(int, luns))}

        response = requests.post(url, headers=headers, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)

        if not response.ok:
            self.throwException(response)
        else:
            taskId = response.json()['data'].get('taskId')
            self.ucpManager.checkTaskStatus(taskId)



    def unpresentLun(
        self,
        luns,
        hgName,
        port,
    ):

        funcName = 'hv_storagemanager:UnpresentLun'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lun={}', luns)
        self.logger.writeParam('hgName={}', hgName)
        self.logger.writeParam('port={}', port)
        self.logger.writeParam('dryRun={}', self.dryRun)
        if self.dryRun:
            return
        (resourceId, ucp) = self.getStorageSystemResourceId()
        hostgroups = self.getAllHostGroups()

        # hostgroup = next(x for x in hostgrpups if x.hostGroupName == hgName and x.port == port)

        hostgroup = None
        for x in hostgroups:
            if x.get('hostGroupName') == hgName and x.get('port') == port:
                hostgroup = x
                break

        hgResourceId = hostgroup.get('resourceId')
        urlPath = '/v2/storage/devices/{0}/hostGroups/{1}/volumes'.format(resourceId,
                                                                          hgResourceId)
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        body = {'ldevIds': list(map(int, luns))}

        response = requests.delete(url, headers=headers, json=body,
                                   verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            self.throwException(response)
        else:
            taskId = response.json()['data'].get('taskId')
            self.ucpManager.checkTaskStatus(taskId)


    def addWWN(
        self,
        hgName,
        port,
        wwnList,
    ):

        funcName = 'hv_infra:addWWN'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('hgName={}', hgName)
        self.logger.writeParam('port={}', port)
        self.logger.writeParam('wwnList={}', wwnList)
        self.logger.writeParam('dryRun={}', self.dryRun)
        if self.dryRun:
            return
 
        (resourceId, ucp) = self.getStorageSystemResourceId()
        self.logger.writeParam('storageresourceId={}', resourceId)
        hostgroup = self.getHostGroup(hgName, port)
        hgResourceId = hostgroup.get('resourceId')
        self.logger.writeParam('hgResourceIdresourceId={}', hgResourceId)
        self.logger.writeParam('ucp={}', ucp)
        wwns=[]
        for x in list(wwnList):
           wwns.append( {
                "id": x
            })
        body = {
            'wwns': wwns,
        }
        self.logger.writeParam('body={}', body)
        urlPath = 'v2/storage/devices/{0}/hostGroups/{1}/wwns'.format(resourceId, hgResourceId)
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        response = requests.post(url, headers=headers, json=body,
                                 verify=self.shouldVerifySslCertification)
        self.logger.writeInfo(url)
        self.logger.writeInfo(body)
        if not response.ok:
            self.throwException(response)
        else:
            taskId = response.json()['data'].get('taskId')
            self.ucpManager.checkTaskStatus(taskId)
            ## after success, have to refresh hg, else addl add would not work
            self.refreshHostGroups(resourceId)
        self.logger.writeExitSDK(funcName)

    def removeWWN(
        self,
        hgName,
        port,
        wwnList,
    ):
        funcName = 'hv_infra:removeWWN'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('hgName={}', hgName)
        self.logger.writeParam('port={}', port)
        self.logger.writeParam('wwnList={}', wwnList)
        self.logger.writeParam('dryRun={}', self.dryRun)
        if self.dryRun:
            return
 
        (resourceId, ucp) = self.getStorageSystemResourceId()
        self.logger.writeParam('storageresourceId={}', resourceId)
        hostgroup = self.getHostGroup(hgName, port)
        hgResourceId = hostgroup.get('resourceId')
        self.logger.writeParam('hgResourceIdresourceId={}', hgResourceId)
        self.logger.writeParam('ucp={}', ucp)
        wwns=[]
        for x in list(wwnList):
           wwns.append( {
                "id": x
            })
        
        body = {
            'wwns': wwns,
        }
        self.logger.writeParam('body={}', body)
        urlPath = 'v2/storage/devices/{0}/hostGroups/{1}/wwns'.format(resourceId, hgResourceId)
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        response = requests.delete(url, headers=headers, json=body,
                                 verify=self.shouldVerifySslCertification)
        self.logger.writeInfo(url)
        self.logger.writeInfo(body)
        if not response.ok:
            self.logger.writeDebug('removeWWN not ok response={}',response)
            self.throwException(response)
        else:
            self.logger.writeInfo('response.json()={}', response.json())
            jjson = response.json()
            data = jjson.get('data', None)
            if data is not None:
                taskId = data.get('taskId', None)
                if taskId is not None:
                    self.ucpManager.checkTaskStatus(taskId)
            else:
                ## have to refresh, else the get hg would be wrong
                ## it may be a bug in the porcelain since it is not returning the data/taskId?
                self.refreshHostGroups(resourceId)
                # time.sleep(20)

        self.logger.writeExitSDK(funcName)
        
    def refreshHostGroups(self, resourceId):
        funcName = 'hv_storagemanager:refreshHostGroups'
        self.logger.writeEnterSDK(funcName)

        urlPath = 'v2/storage/devices/{0}/hostGroups?refresh=true'.format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        self.logger.writeDebug('refreshHostGroups url={}', url)
        headers = self.ucpManager.getAuthToken()
        response = requests.get(url, headers=headers,
                                verify=self.shouldVerifySslCertification)
        
        if response.ok:
            ## the response is all the hgs, too verbose
            self.logger.writeDebug('refreshHostGroups sleep')
            time.sleep(90)
            self.logger.writeExitSDK(funcName)
        else:
            self.logger.writeDebug('refreshHostGroups not ok response={}',response)
            self.throwException(response)

    def getAllStoragePoolDetails(self):

        funcName = 'hv_storagemanager:getHostgetAllStoragePoolDetailsGroup'
        self.logger.writeEnterSDK(funcName)
      
        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = 'v2/storage/devices/{0}/pools?refresh=false'.format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        response = requests.get(url, headers=headers,
                                verify=self.shouldVerifySslCertification)
        if response.ok:
            self.logger.writeExitSDK(funcName)
            return response.json()['data']
        else:
            self.throwException(response)
        
    def getAllParityGroups(self):

        funcName = 'hv_storagemanager:getAllParityGroups'
        self.logger.writeEnterSDK(funcName)
      
        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = 'v2/storage/devices/{0}/parityGroups?refresh=false'.format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        response = requests.get(url, headers=headers,
                                verify=self.shouldVerifySslCertification)
        if response.ok:
            self.logger.writeExitSDK(funcName)
            return response.json()['data']
        else:
            self.throwException(response)
                    
    def getAllStoragePorts(self):

        funcName = 'hv_storagemanager:getAllStoragePorts'
        self.logger.writeEnterSDK(funcName)
      
        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = 'v2/storage/devices/{0}/ports?refresh=false'.format(resourceId)
        url = self.ucpManager.getUrl(urlPath)
        headers = self.ucpManager.getAuthToken()
        response = requests.get(url, headers=headers,
                                verify=self.shouldVerifySslCertification)
        if response.ok:
            self.logger.writeExitSDK(funcName)
            return response.json()['data']
        else:
            self.throwException(response)    