#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
import os
import re
import subprocess
import time
import requests
import urllib3
from enum import Enum


class SNAPSHOT_OPTION(Enum):

    SSOPTION_HIDE_AND_DISABLE_ACCESS = 0
    SSOPTION_HIDE_AND_ALLOW_ACCESS = 1
    SSOPTION_SHOW_AND_ALLOW_ACCESS = 3

    @classmethod
    def fromValue(cls, value):
        enums = [e for e in cls if e.value == value]
        return (enums[0] if enums else None)

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


from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_htimanager import HTIManager
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_remotemanager import RemoteManager
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_htimanager import LunStatus
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_htimanager import LunType
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_htimanager import PoolType
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_htimanager import ReplicationStatus
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_storage_enum import PoolCreateType, \
    StorageType, StorageModel, PoolStatus

from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_vsm_manager import VirtualStorageSystem

from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_log import Log, \
    HiException


class StorageSystemManager:

    logger = Log()

    @staticmethod
    def getHostWWNs(
        hpeAPIGatewayService,
        vcip,
        user,
        pword,
        esxiIP,
    ):

        funcName = 'hpe_infra:getHostWWNs'
        StorageSystemManager.logger.writeEnterSDK(funcName)
        url = 'http://localhost:2030/getHostWWN'
        body = {'vcip': vcip, 'user': user, 'hostIp': esxiIP}
        StorageSystemManager.logger.writeInfo(' url= {}', url)
        StorageSystemManager.logger.writeInfo(' body= {}', body)
        body['pwd'] = pword

        response = requests.post(url, json=body, verify=False)
        StorageSystemManager.logger.writeExitSDK(funcName)
        if response.ok:
            commandOutJson = response.json()
            StorageSystemManager.logger.writeInfo(' response= {}',
                                                  commandOutJson)

            # return is a string
            # commandOutJson = json.loads(commandOut)

            return commandOutJson
        elif 'HIJSONFAULT' in response.headers:
            ex = Exception(json.loads(response.headers['HIJSONFAULT']))
            hiex = HiException(ex)
            StorageSystemManager.logger.writeHiException(hiex)
            raise hiex
        else:
            r = json.loads(response.text)
            StorageSystemManager.logger.writeInfo(r)
            Utils.raiseException(None, response)

    @staticmethod
    def reScanHostStorage(
        hpeAPIGatewayService,
        vcip,
        user,
        pword,
        esxiIP,
    ):

        funcName = 'hpe_infra:reScanHostStorage'
        StorageSystemManager.logger.writeEnterSDK(funcName)
        url = 'http://localhost:2030/scanHostStorage'
        body = {'vcip': vcip, 'user': user, 'hostIp': esxiIP}
        StorageSystemManager.logger.writeInfo(' url= {}', url)
        StorageSystemManager.logger.writeInfo(' body= {}', body)
        body['pwd'] = pword

        StorageSystemManager.logger.writeExitSDK(funcName)
        response = requests.post(url, json=body, verify=False)
        if response.ok:
            StorageSystemManager.logger.writeInfo(' response= {}',
                                                  response)
            return response
        elif 'HIJSONFAULT' in response.headers:
            ex = Exception(json.loads(response.headers['HIJSONFAULT']))
            hiex = HiException(ex)
            StorageSystemManager.logger.writeHiException(hiex)
            raise hiex
        else:
            r = json.loads(response.text)
            StorageSystemManager.logger.writeInfo(r)
            Utils.raiseException(None, response)

    @staticmethod
    def reScanVMFS(
        hpeAPIGatewayService,
        vcip,
        user,
        pword,
        esxiIP,
    ):

        funcName = 'hpe_infra:reScanHostStorage'
        StorageSystemManager.logger.writeEnterSDK(funcName)
        url = 'http://localhost:2030/scanVMFS'
        body = {'vcip': vcip, 'user': user, 'hostIp': esxiIP}
        StorageSystemManager.logger.writeInfo(' url= {}', url)
        StorageSystemManager.logger.writeInfo(' body= {}', body)
        body['pwd'] = pword

        StorageSystemManager.logger.writeExitSDK(funcName)
        response = requests.post(url, json=body, verify=False)
        if response.ok:
            StorageSystemManager.logger.writeInfo(' response= {}',
                                                  response)
            return response
        elif 'HIJSONFAULT' in response.headers:
            ex = Exception(json.loads(response.headers['HIJSONFAULT']))
            hiex = HiException(ex)
            StorageSystemManager.logger.writeHiException(hiex)
            raise hiex
        else:
            r = json.loads(response.text)
            StorageSystemManager.logger.writeInfo(r)
            Utils.raiseException(None, response)

    @staticmethod
    def addStorgeSystemByJson():

        funcName = 'hpe_infra:addStorgeSystemByJson'
        StorageSystemManager.logger.writeEnterSDK(funcName)
        connections = {}

        try:

            # storageJson = os.getenv('HV_STORAGE_ANSIBLE_PROFILE', "./storage.json")

            if os.path.isfile('./storage.json'):
                storageJson = os.path.realpath('storage.json')
            else:
                storageJson = os.getenv('HV_STORAGE_ANSIBLE_PROFILE')

            StorageSystemManager.logger.writeInfo(storageJson)
            with open(storageJson) as connectionFile:
                connections = json.load(connectionFile)
            storagesystems = connections.get('sanStorageSystems', None)
            fileServers = connections.get('nasStorageSystems', None)

            StorageSystemManager.logger.writeInfo(storagesystems)
            StorageSystemManager.logger.writeInfo(fileServers)

            if storagesystems is None and fileServers is None:
                raise Exception('Both sanStorageSystems and nasStorageSystems are not specified.'
                                )

            hpeAPIGatewayService = \
                connections.get('hpeAPIGatewayService', None)
            hpeAPIGatewayServicePort = \
                connections.get('hpeAPIGatewayServicePort', None)

            isPhysicalServer = connections.get('useOutOfBandConnection', None)
            if isPhysicalServer is None:
                useOutOfBandConnection = False
            else:
                if isPhysicalServer.upper() == 'FALSE':
                    useOutOfBandConnection = False
                else:
                    useOutOfBandConnection = True
            StorageSystemManager.addStorgeSystem(hpeAPIGatewayService,
                                                 hpeAPIGatewayServicePort, storagesystems,
                                                 fileServers, useOutOfBandConnection)

            StorageSystemManager.logger.writeExitSDK(funcName)
        except Exception:
            raise Exception('Failed to add StorgeSystem again')

    @staticmethod
    def addFileServers(
        hpeAPIGatewayService,
        hpeAPIGatewayServicePort,
        fileServers,
        sessionIds,
        connectors,
        serials,
    ):

        funcName = 'hpe_infra:StorageSystemManager:addFileServers'
        StorageSystemManager.logger.writeEnterSDK(funcName)
        for systemInfo in fileServers:

            # check for empty map

            if not systemInfo:
                continue

            gatewayServer = systemInfo.get('hpePeerService',
                                           hpeAPIGatewayService)
            gatewayServerPort = systemInfo.get(
                'hpePeerServicePort', hpeAPIGatewayServicePort)

            if gatewayServer is None or gatewayServerPort is None:
                raise Exception('Gateway Server and Port are required.')

            if 'fileServerIP' not in systemInfo:
                raise Exception('fileServerIP is required.')

            fileServerIP = systemInfo['fileServerIP']

            StorageSystemManager.logger.writeParam('fileServerIP={}',
                                                   fileServerIP)

            # StorageSystemManager.self.logger.writeInfo("pwd",
            #            Utils.doGrains(systemInfo["fileServerIP"])
            #            )

            # hpeAPIGatewayService is the one and only c# service
            # the local var serviceIP = "storageGateway" also the c# service
            # gatewayServer = puma server

            serviceIP = systemInfo.get('storageGateway',
                                       hpeAPIGatewayService)
            servicePort = gatewayServerPort

            # for fileServer, there is no serial
            # serial = systemInfo["serialNumber"]

            # use the hpeAPIGatewayService to add nas storage,
            # and gatewayServer is the puma server if differ from hpeAPIGatewayService

            serial = 0

            #             self.logger.writeInfo("serial={}", serial)

            gateway = StorageSystem(serial, serviceIP, servicePort,
                                    sessionIds.get(serviceIP, ''))

            #             self.logger.writeInfo("gateway={}", gateway)

            username = systemInfo.get('username', None)

            # terraform provides the password as a parameter, but ansible reads it from encrypted storage.json

            password = systemInfo.get('password', None)
            if password is None:
                password = Utils.doGrains(systemInfo['fileServerIP'])

            storageSystem = gateway.addFileServer(gatewayServer,
                                                  systemInfo['fileServerIP'], username, password)

            if storageSystem is None:
                raise Exception('Failed to add the storage system : {0}.{1}'.format(serviceIP,
                                                                                    servicePort))

            sessionIds[serviceIP] = storageSystem['GroupIdentifier']
            serial = fileServerIP
            connectors[serial] = {
                'storageGatewayServer': gatewayServer,
                'storageGateway': serviceIP,
                'storageGatewayPort': servicePort,
                'sessionId': storageSystem['GroupIdentifier'],
            }
            serials.add(serial)

            connectors['hpeAPIGatewayService'] = {
                'storageGatewayServer': gatewayServer,
                'storageGateway': serviceIP,
                'storageGatewayPort': servicePort,
                'sessionId': storageSystem['GroupIdentifier'],
            }

            connectors['HNASFileServer'] = {
                'storageGatewayServer': gatewayServer,
                'storageGateway': hpeAPIGatewayService,
                'storageGatewayPort': hpeAPIGatewayServicePort,
                'sessionId': storageSystem['GroupIdentifier'],
            }

        # done with looping thru the file servers, exit

        StorageSystemManager.logger.writeExitSDK(funcName)

    @staticmethod
    def isOOB(isPhysicalServer):
        if isPhysicalServer is None:
            useOutOfBandConnection = False
        else:
            if isPhysicalServer.upper() == 'FALSE':
                useOutOfBandConnection = False
            else:
                useOutOfBandConnection = True

        return useOutOfBandConnection

    @staticmethod
    def removeStorageSystems(
        hpeAPIGatewayService,
        hpeAPIGatewayServicePort,
        storagesystems
    ):
        funcName = 'hpe_infra:StorageSystemManager:removeStorageSystems'
        StorageSystemManager.logger.writeEnterSDK(funcName)

        serials = set()
        results = {}

        if storagesystems is None:
            storagesystems = []
      
        for systemInfo in storagesystems:
            if not systemInfo:
                continue

            gatewayServer = systemInfo.get('hpePeerService', hpeAPIGatewayService)
            gatewayServerPort = systemInfo.get('hpePeerServicePort', hpeAPIGatewayServicePort)

            if gatewayServer is None:
                raise Exception('Gateway Server is required.')

            if hpeAPIGatewayService is None:
                hpeAPIGatewayService = gatewayServer
                hpeAPIGatewayServicePort = gatewayServerPort

            if 'svpIP' not in systemInfo:
                raise Exception('svpIP (location) is required.')

            serviceIP = systemInfo.get('storageGateway',
                                       hpeAPIGatewayService)
            serial = systemInfo['serialNumber']
            gateway = StorageSystem(serial, serviceIP)

            gateway.removeStorageSystem()
            serials.add(str(serial))
        results['comment'] = 'Storage serial(s) {} unregistered successfully.'.format(",".join(serials))
        results['changed'] = True
        StorageSystemManager.logger.writeExitSDK(funcName)
        return results    

    @staticmethod
    def addStorgeSystem(
        hpeAPIGatewayService,
        hpeAPIGatewayServicePort,
        storagesystems,
        fileServers,
        useOutOfBandConnection,
    ):

        funcName = 'hpe_infra:StorageSystemManager:addStorgeSystem'
        StorageSystemManager.logger.writeEnterSDK(funcName)
        StorageSystemManager.logger.writeParam(
            'useOutOfBandConnection={}', useOutOfBandConnection)

        sessionIds = {}
        connectors = {}
        serials = set()
        results = {}
        ssDetails = {}

        if storagesystems is None:
            storagesystems = []
        if fileServers is None:
            fileServers = []

        # process nasStorageSystems in storage.json

        # StorageSystemManager.addFileServers(
        #     hpeAPIGatewayService,
        #     hpeAPIGatewayServicePort,
        #     fileServers,
        #     sessionIds,
        #     connectors,
        #     serials,
        #     )

        # process sanStorageSystems in storage.json

        for systemInfo in storagesystems:

            # check for empty map

            if not systemInfo:
                continue

            gatewayServer = systemInfo.get('hpePeerService',
                                           hpeAPIGatewayService)
            gatewayServerPort = systemInfo.get(
                'hpePeerServicePort', hpeAPIGatewayServicePort)

            storageGatewayServer = systemInfo['hpeAPIStorageGatewayService']
            # each storage can have the option to overwrite the global useOutOfBandConnection option

            isOutOfBand = useOutOfBandConnection
            isPhysicalServer = systemInfo.get('useOutOfBandConnection',
                                              None)
            if isPhysicalServer is not None:
                isOutOfBand = \
                    StorageSystemManager.isOOB(isPhysicalServer)

            #             self.logger.writeInfo("gatewayServer={}", gatewayServer)

            if gatewayServer is None:
                raise Exception('Gateway Server is required.')

            if hpeAPIGatewayService is None:

                # to be backward compatible, just use the first setting for primary(default)

                hpeAPIGatewayService = gatewayServer
                hpeAPIGatewayServicePort = gatewayServerPort

            if 'svpIP' not in systemInfo:
                raise Exception('svpIP (location) is required.')

            serviceIP = systemInfo.get('storageGateway',
                                       hpeAPIGatewayService)
            servicePort = gatewayServerPort

            serial = systemInfo['serialNumber']
            gateway = StorageSystem(serial, serviceIP, servicePort,
                                    sessionIds.get(serviceIP, ''))
            username = systemInfo.get('username', None)
            password = systemInfo.get('password', None)

            if password is None:
                password = Utils.doGrains(systemInfo['svpIP'])

            storageSystem = gateway.addStorageSystem(
                systemInfo['svpIP'],
                gatewayServer,
                8444,
                username,
                password,
                False,
                storageGatewayServer
            )

            if storageSystem is None:
                raise Exception('Failed to add the storage system : {0}.{1}'.format(serviceIP,
                                                                                    servicePort))

            connectors[serial] = \
                {'storageGatewayServer': gatewayServer,
                 'storageGateway': serviceIP,
                 'storageGatewayPort': servicePort}

            serials.add(serial)

            connectors['hpeAPIGatewayService'] = {
                'storageGatewayServer': gatewayServer,
                'storageGateway': serviceIP,
                'storageGatewayPort': servicePort,
            }

            ssDetails[serial] = \
                StorageSystemManager.formatStorageSystem(storageSystem)

        with open(Log.getHomePath() + '/storage-connectors.json', 'w'
                  ) as connectorFile:
            json.dump(connectors, connectorFile)

        results['storageSystems'] = list(serials)
        results['sessionIds'] = sessionIds
        results['details'] = ssDetails

        StorageSystemManager.logger.writeExitSDK(funcName)
        return results

    @staticmethod
    def formatStorageSystem(storageSystem):
        funcName = 'hpe_infra:StorageSystemManager:formatStorageSystem'
        StorageSystemManager.logger.writeEnterSDK(funcName)
        storageSystem.pop('resourceId', None)
        storageSystem.pop('storageEfficiencyStat', None)
        storageSystem.pop('storageDeviceLicenses', None)
        storageSystem.pop('isUnified', None)
        storageSystem.pop('tags', None)
        storageSystem.pop('deviceType', None)
        storageSystem.pop('ucpSystems', None)
        storageSystem.pop('username', None)
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
        if ':' in lun:
            lun = lun.replace(':', '')
        try:
            return int(lun, 16)
        except ValueError:
            return None

    @staticmethod
    def doGrains(ipaddress):

        funcName = 'hpe_infra:doGrains'
        Utils.logger.writeEnterSDK(funcName)

        try:

            # dir_path = os.path.dirname(os.path.realpath("storage.json"))
            # Utils.logger.writeInfo("dir_path={}", dir_path)
            # storageJson = os.getenv('HV_STORAGE_ANSIBLE_PROFILE', "./storage.json")
            # storageJson = dir_path + r"/storage.json"

            if os.path.isfile('./storage.json'):
                storageJson = os.path.realpath('storage.json')
            else:
                storageJson = os.getenv('HV_STORAGE_ANSIBLE_PROFILE')
            Utils.logger.writeInfo('storageJson={}', storageJson)
            Utils.logger.writeInfo('Log.getHomePath()={}',
                                   Log.getHomePath())

            command = Log.getHomePath() + '/bin/.grains {} ' \
                + storageJson + ' '
            command = command.format(ipaddress)

            # Utils.logger.writeInfo("command={}",command)
            # Utils.logger.writeInfo("subprocess.check_output(command, shell=True)={}", subprocess.check_output(command, shell=True))

            commandOutStr = subprocess.check_output(command, shell=True)
            commandOutStr = commandOutStr.replace('\n', '')

            # Utils.logger.writeInfo("the password is={}",commandOutStr)

            Utils.logger.writeExitSDK(funcName)
            return commandOutStr
        except Exception:
            raise Exception(
                'Invalid password, please check password for {0}'.format(ipaddress))

    @staticmethod
    def requestsPost_notused(url, json, verify):
        try:
            return requests.post(url, json=json, verify=verify)
        except Exception:

            # note: exception thrown by requests is caught by ansible module
            # it will not be caught here

            raise Exception('requests exception caught')

    @staticmethod
    def raiseException(sessionid, response, throwException=True):
        jsonStr = json.loads(response.headers['HIJSONFAULT'])
        if 'You need to re-initaite ADD STORAGE operation to create a new session' \
                in str(jsonStr['ErrorMessage']):
            if sessionid is None:
                raise Exception('Session expired. You need to re-initiate session with add_storagesystem playbook to create a new session'
                                )
            else:
                raise Exception(
                    'Session {0} is not found or expired. You need to re-initiate session with add_storagesystem \
                    playbook to create a new session'.format(sessionid))

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

            raise Exception('foo:w')

    @staticmethod
    def formatCapacity(valueMB, round_digits=4):

        # expected valueMB (from puma):
        # 5120 is 5120MB

        Utils.logger.writeParam('formatCapacity, value={}', valueMB)
        oneK = 1024

        ivalue = float(valueMB)
        Utils.logger.writeParam('formatCapacity, ivalue={}', ivalue)
        if ivalue == 0:
            return '0'

        ivalue = ivalue / 1024 / 1024
        Utils.logger.writeParam('formatCapacity, ivalue={}', ivalue)
        if ivalue >= oneK * oneK:
            divfrac = oneK * oneK
            v = ivalue / divfrac
            Utils.logger.writeParam('TB Section, v={}', v)
            return str(round(v, round_digits)) + 'TB'
        elif ivalue >= oneK:
            v = ivalue / oneK
            return str(round(v, round_digits)) + 'GB'
        else:
            return str(round(ivalue, round_digits)) + 'MB'

    @staticmethod
    def formatLun(lun):
        # if lun.get('VirtualLunNumber') is not None:
        # lun['VirtualLun'] = lun['VirtualLunNumber']
        # del lun['VirtualLunNumber']
        # if lun.get('ldevId') is not None:
        #    lun['Lun'] = lun['ldevId']
        #    del lun['ldevId']
        # if lun.get('poolId') is not None:
        #    del lun['DynamicPool']
        if lun.get('provisionType') == "DP":
            lun['provisionType'] = 'THP'
        if lun.get('resourceId') is -1:
            del lun['resourceId']
        if lun.get('poolId') is -1:
            del lun['poolId']
        if lun.get('parityGroupId') == "":
            del lun['parityGroupId']
        if lun.get('naaId') is not None:
            lun['canonicalName'] = lun['naaId']
            del lun['naaId']
        if lun.get('totalCapacity') is not None:
            lun['totalCapacity'] = \
                Utils.formatCapacity(lun['totalCapacity'])
        if lun.get('usedCapacity') is not None:
            lun['usedCapacity'] = \
                Utils.formatCapacity(lun['usedCapacity'])
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

    @staticmethod
    def formatLuns(luns):
        for lun in luns:
            Utils.formatLun(lun)

    @staticmethod
    def formatGadPair(pair):
        pair['Status'] = ReplicationStatus.fromValue(pair.get('Status', 0)).name
        pair['Type'] = 'GAD'
        if pair.get('FenceLevel') is not None:
            del pair['FenceLevel']
        if pair.get('ManagementPoolId') is not None:
            del pair['ManagementPoolId']
        if pair.get('JournalPoolId') is not None:
            del pair['JournalPoolId']
        if pair.get('ReplicationPoolId') is not None:
            del pair['ReplicationPoolId']
        if pair.get('DataPoolId') is not None:
            del pair['DataPoolId']
        if pair.get('MirrorId') is not None:
            del pair['MirrorId']
        if pair.get('SplitTime') is not None:
            del pair['SplitTime']
        if pair.get('PairName') is not None:
            del pair['PairName']
        if pair.get('VirtualDeviceId') is not None:
            pair['VSMSerial'] = pair['VirtualDeviceId']
            del pair['VirtualDeviceId']
        if pair.get('ConsistencyGroupId') is not None:
            if str(pair['ConsistencyGroupId']) == str(-1):
                pair['ConsistencyGroupId'] = ''
        return pair

    @staticmethod
    def formatPool(pool):
        pool['Status'] = PoolStatus.getName(pool.get('Status', 0))
        pool['Type'] = PoolType.parse(pool.get('Type', 0)).name

        return pool

    @staticmethod
    def formatPools(pools):
        for pool in pools:
            Utils.formatPool(pool)

    @staticmethod
    def isStorageOOB(ip_address):
        Utils.logger.writeInfo(ip_address)
        Utils.logger.writeInfo(os.path.realpath('storage.json'))
        if os.path.isfile('./storage.json'):
            storageJson = os.path.realpath('storage.json')
        else:
            storageJson = os.getenv('HV_STORAGE_ANSIBLE_PROFILE')
        with open(storageJson) as connectionFile:
            connections = json.load(connectionFile)

        storagesystems = connections.get('sanStorageSystems', None)
        isOBB = connections.get('useOutOfBandConnection', None)

        for sysinfo in storagesystems:
            serial = sysinfo.get('serialNumber', None)
            if str(serial) == str(ip_address):
                isOBB = sysinfo.get('useOutOfBandConnection', None)
                break
        return str(isOBB).upper()

    @staticmethod
    def isGivenValidSerial(serial):

        if serial is None:
            raise Exception('Storage systems have not been registered. Please run add_storagesystems.yml first.'
                            )

        Utils.logger.writeInfo(serial)
        Utils.logger.writeInfo(os.path.realpath('storage.json'))
        if os.path.isfile('./storage.json'):
            storageJson = os.path.realpath('storage.json')
        else:
            storageJson = os.getenv('HV_STORAGE_ANSIBLE_PROFILE')
        with open(storageJson) as connectionFile:
            connections = json.load(connectionFile)

        storagesystems = connections.get('sanStorageSystems', None)
        isfound = False

        for sysinfo in storagesystems:
            sysserial = sysinfo.get('serialNumber', None)
            if str(serial) == str(sysserial):
                isfound = True
                break
        return isfound

    @staticmethod
    def isGivenValidFileServerIp(ip_address):
        if ip_address is None:
            raise Exception('The fileServerIP is missing.')
        Utils.logger.writeInfo(ip_address)
        Utils.logger.writeInfo(os.path.realpath('storage.json'))
        if os.path.isfile('./storage.json'):
            storageJson = os.path.realpath('storage.json')
        else:
            storageJson = os.getenv('HV_STORAGE_ANSIBLE_PROFILE')
        with open(storageJson) as connectionFile:
            connections = json.load(connectionFile)
        nasStoragesystems = connections.get('nasStorageSystems', None)
        isfound = False

        for sysinfo in nasStoragesystems:
            fileServerIP = sysinfo.get('fileServerIP', None)
            if str(fileServerIP) == str(ip_address):
                isfound = True
                break
        return isfound

    @staticmethod
    def getSerialByNaa(naa):
        naa = str(naa)
        modelString = naa[20:23]
        if modelString == '502':
            subsytemModel = 'HUS-VM'
        elif modelString == '003':
            subsytemModel = 'VSP G-1000'
        elif modelString == '000':
            subsytemModel = 'VSP'
        elif modelString == '504':
            subsytemModel = 'VSP Gx00'
        elif modelString == '502':
            subsytemModel = 'HM700'
        else:
            subsytemModel = 'Other'

        serial = naa[23:28]

        # naa.substring(23, 28)

        serialNum1 = int(serial, 16)
        serialNum = str(serialNum1)
        if subsytemModel == 'VSP Gx00':
            serialNum = '4' + serialNum
        elif subsytemModel == 'HM700':
            serialNum = '2' + serialNum
        return serialNum


class StorageSystem:

    #     slogger = Log()

    def setDryRun(self, flag):

        # StorageSystem.slogger.writeEnterSDK("slogger: StorageSystem.setDryRun")

        funcName = 'StorageSystem:setDryRun'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('dryRun={}', flag)

        # StorageSystem.slogger.writeEnterSDK("slogger: StorageSystem.setDryRun")

        funcName = 'StorageSystem:setDryRun'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('dryRun={}', flag)
        self.dryRun = flag
        self.logger.writeExitSDK(funcName)

    def __init__(
        self,
        serial,
        webServiceIp=None,
        webServicePort=None,
        sessionId=None,
    ):

        self.logger = Log()
        self.dryRun = False
        self.serial = serial
        self.sessionId = sessionId
        self.isVirtualSerial = False

        if not webServiceIp:
            try:
                with open(Log.getHomePath() + '/storage-connectors.json'
                          ) as connectionFile:
                    connections = json.load(connectionFile)
                system = connections.get(str(serial))

                if system is None:
                    system = connections['hpeAPIGatewayService']
                    self.isVirtualSerial = True

                self.sessionId = None
                webServiceIp = system['storageGateway']
                webServicePort = system['storageGatewayPort']
            except IOError as ex:
                raise Exception('Storage systems have not been registered. Please run add_storagesystems.yml first.'
                                )

        self.webServiceIp = webServiceIp
        self.webServicePort = webServicePort
        #self.basedUrl = 'https://{0}:{1}'.format(webServiceIp, webServicePort)
        self.basedUrl = 'https://{0}'.format(webServiceIp)
        self.shouldVerifySslCertification = False

        self.htiManager = HTIManager(self.serial, self.webServiceIp,
                                     self.webServicePort, self.sessionId)
        self.remoteManager = RemoteManager(self.serial,
                                           self.webServiceIp, self.webServicePort, self.sessionId)
        self.vsmManager = VirtualStorageSystem(self.serial,
                                               self.webServiceIp, self.webServicePort, self.sessionId)

    def isSessionNotFound(self, exMsg):
        strToMatch = 'Session is not found'
        if strToMatch in str(exMsg):
            return True
        else:
            return False

    def removeLogicalUnitFromResourceGroup(self, rgId, id):

        funcName = 'hpe_infra:removeLogicalUnitFromResourceGroup'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('rgId={}', rgId)
        self.logger.writeParam('id={}', id)

        urlPath = 'ResourceGroup/RemoveLogicalUnitFromResourceGroup'
        url = self.getUrl(urlPath)
        body = {
            'sessionId': self.sessionId,
            'serialNumber': self.serial,
            'luId': id,
            'rgId': rgId,
        }

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def addLogicalUnitToResourceGroup(self, rgId, id):

        funcName = 'hpe_infra:addLogicalUnitToResourceGroup'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('rgId={}', rgId)
        self.logger.writeParam('id={}', id)

        funcName = 'hpe_infra:addLogicalUnitToResourceGroup'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('rgId={}', rgId)
        self.logger.writeParam('id={}', id)

        urlPath = 'ResourceGroup/AddLogicalUnitToResourceGroup'
        url = self.getUrl(urlPath)
        body = {
            'sessionId': self.sessionId,
            'serialNumber': self.serial,
            'luId': id,
            'rgId': rgId,
        }

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def deleteResourceGroup(self, rgId):

        funcName = 'hpe_infra:deleteResourceGroup'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('rgId={}', rgId)

        urlPath = 'ResourceGroup/DeleteResourceGroup'
        url = self.getUrl(urlPath)
        body = {'sessionId': self.sessionId,
                'serialNumber': self.serial, 'rgId': rgId}

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def removeDriveGroupFromResourceGroup(self, rgId, parityGroupId):

        funcName = 'hpe_infra:removeDriveGroupFromResourceGroup'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('rgId={}', rgId)
        self.logger.writeParam('parityGroupId={}', parityGroupId)

        urlPath = 'ResourceGroup/RemoveDriveGroupFromResourceGroup'
        url = self.getUrl(urlPath)
        body = {
            'sessionId': self.sessionId,
            'serialNumber': self.serial,
            'parityGroupId': parityGroupId,
            'rgId': rgId,
        }

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def addFileServer(
        self,
        gatewayServer,
        fileServerIP,
        username,
        password,
    ):

        funcName = 'hpe_infra:StorageSystem:addFileServer'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('gatewayServer={}', gatewayServer)
        self.logger.writeParam('fileServerIP={}', fileServerIP)
        self.logger.writeParam('username={}', username)

        urlPath = 'NAS/StorageManager/AddFileServer'
        url = self.getUrl(urlPath)
        self.logger.writeInfo('url={}', url)
        body = {  # "gatewayServer": self.webServiceIp,
            'sessionId': self.sessionId,
            'fileServer': fileServerIP,
            'userID': username,
            'password': password,
            'gatewayServer': gatewayServer,
            'gatewayServerPort': 8444,
            'forceReinitialize': False,
        }

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def addDriveGroupToResourceGroup(self, rgId, parityGroupId):

        funcName = 'hpe_infra:addDriveGroupToResourceGroup'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('rgId={}', rgId)
        self.logger.writeParam('parityGroupId={}', parityGroupId)

        urlPath = 'ResourceGroup/AddDriveGroupToResourceGroup'
        url = self.getUrl(urlPath)
        body = {
            'sessionId': self.sessionId,
            'serialNumber': self.serial,
            'parityGroupId': parityGroupId,
            'rgId': rgId,
        }

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def removeHostGroupFromResourceGroup(
        self,
        rgId,
        hostGroupName,
        portId,
    ):

        funcName = 'hpe_infra:removeHostGroupFromResourceGroup'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('rgId={}', rgId)
        self.logger.writeParam('hostGroupName={}', hostGroupName)
        self.logger.writeParam('portId={}', portId)

        urlPath = 'ResourceGroup/RemoveHostGroupFromResourceGroup'
        url = self.getUrl(urlPath)
        body = {
            'sessionId': self.sessionId,
            'serialNumber': self.serial,
            'hostGroupName': hostGroupName,
            'portId': portId,
            'rgId': rgId,
        }

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:

            # return response.json()

            return response
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def addHostGroupToResourceGroup(
        self,
        rgId,
        hostGroupName,
        portId,
    ):

        funcName = 'hpe_infra:addHostGroupToResourceGroup'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('rgId={}', rgId)
        self.logger.writeParam('hostGroupName={}', hostGroupName)
        self.logger.writeParam('portId={}', portId)

        urlPath = 'ResourceGroup/AddHostGroupToResourceGroup'
        url = self.getUrl(urlPath)
        body = {
            'sessionId': self.sessionId,
            'serialNumber': self.serial,
            'hostGroupName': hostGroupName,
            'portId': portId,
            'rgId': rgId,
        }

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def removePortFromResourceGroup(self, rgId, id):

        funcName = 'hpe_infra:removePortFromResourceGroup'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('rgId={}', rgId)
        self.logger.writeParam('id={}', id)

        urlPath = 'ResourceGroup/RemovePortFromResourceGroup'
        url = self.getUrl(urlPath)
        body = {
            'sessionId': self.sessionId,
            'serialNumber': self.serial,
            'portId': id,
            'rgId': rgId,
        }

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getTypeFromModel(self, model):
        if 'VSP_G' in model:
            return 'VSP_GX00'
        if 'VSP_F' in model:
            return 'VSP_FX00'
        if 'VSP_N' in model:
            return 'VSP_NX00'
        if '00H' in model:
            return 'VSP_5X00H'
        if 'VSP_5' in model:
            return 'VSP_5X00'

    def createVirtualBoxResourceGroup(
        self,
        remoteStorageId,
        model,
        rgName,
    ):

        funcName = 'hpe_infra:createVirtualBoxResourceGroup'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('remoteStorageId={}', remoteStorageId)
        self.logger.writeParam('model={}', model)
        self.logger.writeParam('rgName={}', rgName)

        funcName = 'hpe_infra:createVirtualBoxResourceGroup'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('remoteStorageId={}', remoteStorageId)
        self.logger.writeParam('model={}', model)
        self.logger.writeParam('rgName={}', rgName)

        urlPath = 'ResourceGroup/CreateVirtualBoxResourceGroup'
        url = self.getUrl(urlPath)
        storage_type = \
            StorageType.fromString(self.getTypeFromModel(model))
        storage_model = StorageModel.fromString(model)
        body = {
            'sessionId': self.sessionId,
            'serialNumber': self.serial,
            'remoteStorageId': remoteStorageId,
            'type': storage_type.value,
            'model': storage_model.value,
            'rgName': rgName,
        }

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:

            return response
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def addPortToResourceGroup(self, rgId, id):

        funcName = 'hpe_infra:addPortToResourceGroup'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('rgId={}', rgId)
        self.logger.writeParam('id={}', id)

        urlPath = 'ResourceGroup/AddPortToResourceGroup'
        url = self.getUrl(urlPath)
        body = {
            'sessionId': self.sessionId,
            'serialNumber': self.serial,
            'portId': id,
            'rgId': rgId,
        }

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def isVirtualSerialInUse(self):
        return self.isVirtualSerial

    def getUrl(self, urlPath):
        return '{0}/porcelain/{1}'.format(self.basedUrl, urlPath)

    def addStorageSystem1(
        self,
        location,
        gatewayIP,
        gatewayPort,
        username,
        password,
        useOutOfBandConnection,
    ):

        funcName = 'hpe_infra:addStorageSystem'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('location={}', location)
        self.logger.writeParam('gatewayIP={}', gatewayIP)
        self.logger.writeParam('gatewayPort={}', gatewayPort)
        self.logger.writeParam('username={}', username)

        headers = self.getAuthToken()
        self.logger.writeParam('headers={}', headers)

        urlPath = 'v2/storage/devices'
        url = self.getUrl(urlPath)
        self.logger.writeParam('url={}', url)
        systems = self.getAllStorageSystems()
        self.logger.writeInfo('systems={}', systems)
        system = None
        for x in systems:
            self.logger.writeInfo('int(x[serialNumber]) == self.serial={}', int(x['serialNumber'])
                                   == self.serial)
            if int(x['serialNumber']) == self.serial:
                system = x
                break
        self.logger.writeInfo('system={}', system)

        if system is None:
            ucp_name = self.createUcpSystem(gatewayIP)
            systems = self.getAllStorageSystems()
            self.logger.writeInfo('systems={}', systems)
            system = None
            for x in systems:
                self.logger.writeInfo('int(x[serialNumber]) == self.serial={}', int(x['serialNumber'])
                                       == self.serial)
                if int(x['serialNumber']) == self.serial:
                    system = x
                    break
            self.logger.writeInfo('system={}', system)
            self.logger.writeInfo('ucp_name={}', ucp_name)
            if system is None:                                         
                body = {
                    'managementAddress': location,
                    'password': password,
                    'serialNumber': self.serial,
                    'ucpSystem': ucp_name,
                    'username': username,
                }
                self.logger.writeInfo('body={}', body)
                response = requests.post(url, json=body, headers=headers,
                                         verify=self.shouldVerifySslCertification)
        else:
            return StorageSystemManager.formatStorageSystem(system)

        if response.ok:
            if system is None:
                resJson = response.json()
                self.logger.writeInfo('response={}', resJson)
                resourceId = resJson['data'].get('resourceId')
                self.logger.writeInfo('resourceId={}', resourceId)
                taskId = response.json()['data'].get('taskId')
                self.logger.writeInfo('taskId={}', taskId)
                self.checkTaskStatus(taskId)
                time.sleep(5)
                system = self.getStorageInfoByResourceId(resourceId)
            self.logger.writeInfo('system={}', system)
            system['StorageGatewayServiceIP'] = self.webServiceIp
            #   system['webServicePort'] = self.webServicePort
            return StorageSystemManager.formatStorageSystem(system)
        elif 'HIJSONFAULT' in response.headers:
            self.logger.writeInfo('HIJSONFAULT response={}', response)
            Utils.raiseException(self.sessionId, response)
        else:
            self.logger.writeInfo('Unknown Exception response={}',
                                   response.json())
            self.throwException(response)

    def removeStorageSystem(self):
        funcName = 'hpe_infra:removeStorageSystem'
        self.logger.writeEnterSDK(funcName)
        self.removeStorageSystemFromUCP()
        resourceId = self.getStorageSystemResourceIdInISP()
        headers = self.getAuthToken()
        self.logger.writeParam('headers={}', headers)

        urlPath = 'v2/storage/devices/{0}'.format(resourceId)
        url = self.getUrl(urlPath)
        self.logger.writeParam('url={}', url)
        self.logger.writeInfo('system={}', resourceId)
        response = requests.delete(url, headers=headers, verify=self.shouldVerifySslCertification)
        if response.ok:
            resJson = response.json()
            self.logger.writeInfo('response={}', resJson)
            resourceId = resJson['data'].get('resourceId')
            self.logger.writeInfo('resourceId={}', resourceId)
            taskId = response.json()['data'].get('taskId')
            self.logger.writeInfo('taskId={}', taskId)
            self.checkTaskStatus(taskId)
            time.sleep(5)
        elif 'HIJSONFAULT' in response.headers:
            self.logger.writeInfo('HIJSONFAULT response={}', response)
            Utils.raiseException(self.sessionId, response)
        else:
            self.logger.writeInfo('Unknown Exception response={}',
                                   response.json())
            self.throwException(response)

    def removeStorageSystemFromUCP(self):
        funcName = 'hpe_infra:removeStorageSystem'
        self.logger.writeEnterSDK(funcName)
        systems = self.getAllStorageSystems()

        self.logger.writeInfo('systems={}', systems)

        system = None
        for x in systems:
            self.logger.writeInfo(int(x['serialNumber']))
            self.logger.writeInfo(self.serial)
            self.logger.writeInfo(int(x['serialNumber'])
                                   == self.serial)

            if str(x['serialNumber']) == str(self.serial):
                system = x
                break
        
        if system is None:
            return
        (resourceId, ucp_name) = (str(system.get('resourceId')), str(system.get('ucpSystems')[0]))
        ucpsystem = self.getUcpSystemByName(ucp_name)
        headers = self.getAuthToken()
        self.logger.writeParam('headers={}', headers)

        urlPath = 'v2/systems/{0}/device/{1}'.format(ucpsystem.get('resourceId'), resourceId)
        url = self.getUrl(urlPath)
        self.logger.writeParam('url={}', url)
        self.logger.writeInfo('system={}', resourceId)
        self.logger.writeInfo('ucp_name={}', ucp_name)
        self.logger.writeInfo('ucp_resource_id={}', ucpsystem.get('resourceId'))
        response = requests.delete(url, headers=headers, verify=self.shouldVerifySslCertification)
        if response.ok:
            resJson = response.json()
            self.logger.writeInfo('response={}', resJson)
            resourceId = resJson['data'].get('resourceId')
            self.logger.writeInfo('resourceId={}', resourceId)
            taskId = response.json()['data'].get('taskId')
            self.logger.writeInfo('taskId={}', taskId)
            self.checkTaskStatus(taskId)
            time.sleep(5)
        elif 'HIJSONFAULT' in response.headers:
            self.logger.writeInfo('HIJSONFAULT response={}', response)
            Utils.raiseException(self.sessionId, response)
        else:
            self.logger.writeInfo('Unknown Exception response={}',
                                   response.json())
            self.throwException(response)        

    def addStorageSystem(
        self,
        location,
        gatewayIP,
        gatewayPort,
        username,
        password,
        useOutOfBandConnection,
        storageGatewayServer
    ):

        funcName = 'hpe_infra:addStorageSystem'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('location={}', location)
        self.logger.writeParam('gatewayIP={}', gatewayIP)
        self.logger.writeParam('gatewayPort={}', gatewayPort)
        self.logger.writeParam('username={}', username)

        headers = self.getAuthToken()
        self.logger.writeParam('headers={}', headers)

        urlPath = 'v2/storage/devices'
        url = self.getUrl(urlPath)
        self.logger.writeParam('url={}', url)
        systems = self.getAllStorageSystems()
        self.logger.writeInfo('systems={}', systems)
        system = None
        for x in systems:
            self.logger.writeInfo('int(x[serialNumber]) == self.serial={}', int(x['serialNumber'])
                                   == self.serial)
            if int(x['serialNumber']) == self.serial:
                system = x
                break
        self.logger.writeInfo('system={}', system)

        if system is None:
            ucp_name = self.createUcpSystem(gatewayIP, storageGatewayServer, self.serial)
            time.sleep(5)
            body = {
                'managementAddress': location,
                'password': password,
                'serialNumber': self.serial,
                'username': username,
                'ucpSystem': ucp_name,
                'storageGatewayServer': storageGatewayServer,
            }
            self.logger.writeInfo('url={}', url)
            self.logger.writeInfo('addStorage_body={}', body)
            addStorageResponse = requests.post(url, json=body, headers=headers, verify=self.shouldVerifySslCertification)
            if addStorageResponse.ok:
                resposeJson = addStorageResponse.json()
                self.logger.writeInfo('addStorage resposeJson={}', resposeJson)
                taskId = resposeJson['data'].get('taskId')
                status = None
                status = self.checkTaskStatus(taskId)
                if status.lower() == 'pending':
                    time.sleep(30)
                    status = self.checkTaskStatus(taskId)
                if status.lower() == 'success':
                    systems = self.getAllStorageSystemsInISP()
                    system = None
                    for x in systems:
                        if int(x['serialNumber']) == self.serial:
                            system = x
                            break
                    #  self.updateUcpSystem(gatewayIP, system.get('resourceId'))  
                    #  time.sleep(5)  
                    systems = self.getAllStorageSystems()
                    for x in systems:
                        if int(x['serialNumber']) == self.serial:
                            system = x
                            break
                    self.logger.writeInfo('addStorage system={}', system)
                    return StorageSystemManager.formatStorageSystem(system)
                else:
                    self.throwException(addStorageResponse)
            else:
                self.logger.writeError('Unknown Exception response={}',
                                   addStorageResponse.json())
            self.throwException(addStorageResponse)               
        else:
            return StorageSystemManager.formatStorageSystem(system)


    def getStorageSystemResourceId(self):
        """
        docstring
        """

        funcName = 'hpe_infra:getStorageSystemResourceId'
        self.logger.writeEnterSDK(funcName)
        headers = self.getAuthToken()
        self.logger.writeParam('headers={}', headers)

        urlPath = 'v2/storage/devices'
        url = self.getUrl(urlPath)
        self.logger.writeParam('url={}', url)

        systems = self.getAllStorageSystems()

        # self.logger.writeInfo('systems={}', systems)

        system = None
        for x in systems:
            self.logger.writeInfo(int(x['serialNumber']))
            self.logger.writeInfo(self.serial)
            self.logger.writeInfo(int(x['serialNumber'])
                                   == self.serial)

            if str(x['serialNumber']) == str(self.serial):
                system = x
                break

        if system is None:
            raise Exception('Storage systems = {0} have not been registered. Please run add_storagesystems.yml first.'.format(self.serial))

        ucp = system.get('ucpSystems')[0]
        self.logger.writeExitSDK(funcName)
        return (str(system.get('resourceId')), str(ucp))

    def getStorageSystem(self):
        """
        docstring
        """

        headers = self.getAuthToken()
        self.logger.writeParam('headers={}', headers)

        urlPath = 'v2/storage/devices'
        url = self.getUrl(urlPath)
        self.logger.writeParam('url={}', url)

        systems = self.getAllStorageSystems()
        self.logger.writeInfo('systems={}', systems)
        system = None
        for x in systems:
            self.logger.writeInfo(int(x['serialNumber']))
            self.logger.writeInfo(self.serial)
            self.logger.writeInfo(int(x['serialNumber'])
                                   == self.serial)

            if str(x['serialNumber']) == str(self.serial):
                system = x
                break
        self.logger.writeInfo('system={}', system)
        return StorageSystemManager.formatStorageSystem(system)

    def getAuthToken(self):
        funcName = 'hpe_infra:getAuthToken'
        body = {'username': 'ucpadmin', 'password': 'overrunsurveysroutewarnssent'}
        urlPath = 'v2/auth/login'
        url = '{0}/porcelain/{1}'.format(self.basedUrl, urlPath)
        self.logger.writeInfo('url={}', url)
        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        token = None
        if response.ok:
            authResponse = response.json()
            data = authResponse['data']
            token = data.get('token')
        elif 'HIJSONFAULT' in response.headers:
            self.logger.writeInfo('HIJSONFAULT response={}', response)
            Utils.raiseException(self.sessionId, response)
        else:
            self.logger.writeInfo('Unknown Exception response={}',
                                   response)
            self.throwException(response)

        headers = {'Authorization': 'Bearer {0}'.format(token)}

        return headers

    def createUcpSystem(self, gatewayIp, storageGateway, serial):
        funcName = 'hpe_infra:getAuthToken'
        self.logger.writeEnterSDK(funcName)

        serialLast5 = str(serial).replace('', '')[-5:]
        ucp_name = 'ucp-{0}'.format(serialLast5)
        ucp_serial = 'Logical-UCP-{0}'.format(serialLast5)
        system = self.getUcpSystem(gatewayIp)
        self.logger.writeInfo('ucpsystem={}', system)
        if system is None:
            body = {
                'gatewayAddress': storageGateway,
                'model': 'Logical UCP',
                'name': ucp_name,
                'region': 'EMEA',
                'serialNumber': ucp_serial,
                "country": "Belgium",
                "zipcode": 1020,
                "zone": "zone"
            }
            urlPath = 'v2/systems'
            url = '{0}/porcelain/{1}'.format(self.basedUrl, urlPath)
            self.logger.writeInfo('url={}', url)
            self.logger.writeInfo('body={}', body)

            response = requests.post(url, headers=self.getAuthToken(),
                                     json=body, verify=self.shouldVerifySslCertification)
            self.logger.writeExitSDK(funcName)

            if response.ok:
                resposeJson = response.json()
                self.logger.writeInfo('createUCPRespose={}', resposeJson)
                taskId = resposeJson['data'].get('taskId')
                self.checkTaskStatus(taskId)
            elif 'HIJSONFAULT' in response.headers:
                self.logger.writeInfo('HIJSONFAULT response={}',
                                       response)
                Utils.raiseException(self.sessionId, response)
            else:
                self.logger.writeInfo('Unknown Exception response={}',
                                       response)
                raise Exception('Unknown error HTTP {0}'.format(response.status_code + response.message))
        return ucp_name

    def updateUcpSystem(self, gatewayIp, deviceId):
        system = self.getUcpSystem(gatewayIp)
        funcName = 'hpe_infra:updateUcpSystem'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('deviceId={}', deviceId)
        urlPath = 'v2/systems/{0}/device/{1}'.format(system.get('resourceId'), deviceId)
        url = self.getUrl(urlPath)
        self.logger.writeInfo('url={}', url)
        headers = self.getAuthToken()
        self.logger.writeInfo('headers={}', headers)
        response = requests.patch(url, headers=headers,
                                  verify=self.shouldVerifySslCertification)
        self.logger.writeInfo('response={}', response.json())
        self.logger.writeExitSDK(funcName)
        if response.ok:
            resourceId = response.json()['data']['resourceId']
            self.logger.writeInfo('resourceId={}', resourceId)
            taskId = response.json()['data'].get('taskId')
            self.checkTaskStatus(taskId)
            time.sleep(10)
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

        return system    

    def getUcpSystem(self, gatewayIp):
        funcName = 'hpe_infra:getUcpSystem'
        self.logger.writeEnterSDK(funcName)

        gatewayLast5 = gatewayIp.replace('.', '')[-5:]
        ucp_name = 'ucp-{0}'.format(gatewayLast5)
        ucp_serial = 'Logical-UCP-{0}'.format(gatewayLast5)

        systems = self.getAllUcpSystem()
        system = next((x for x in systems if x.get('name')
                       == ucp_name), None)

        self.logger.writeExitSDK(funcName)
        return system

    def getStorageSystemResourceIdInISP(self):
        """
        docstring
        """

        funcName = 'hpe_infra:getStorageSystemResourceIdInISP'
        self.logger.writeEnterSDK(funcName)
        headers = self.getAuthToken()
        self.logger.writeParam('headers={}', headers)

        urlPath = 'v2/storage/devices'
        url = self.getUrl(urlPath)
        self.logger.writeParam('url={}', url)

        systems = self.getAllISPStorageSystems()

        self.logger.writeInfo('systems={}', systems)

        system = None
        for x in systems:
            self.logger.writeInfo(int(x['serialNumber']))
            self.logger.writeInfo(self.serial)
            self.logger.writeInfo(int(x['serialNumber'])
                                    == self.serial)
            if str(x['serialNumber']) == str(self.serial):
                system = x
                break
        if system is None:
            raise Exception('Storage systems = {0} have not been registered. Please run add_storagesystems.yml first.'.format(self.serial))

        self.logger.writeExitSDK(funcName)
        return (str(system.get('resourceId')))    
    
    def getAllISPStorageSystems(self):
        funcName = 'hpe_infra:getAllISPStorageSystems'
        self.logger.writeEnterSDK(funcName)

        urlPath = 'v2/systems/default'
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()

        response = requests.get(url, headers=headers, verify=self.shouldVerifySslCertification)
        storage_systems = []
        if response.ok:
            authResponse = response.json()
            self.logger.writeInfo('ISP response Json={}', authResponse)
            data = authResponse.get('data')
            storage_systems.extend(data.get('storageDevices'))
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)
        return storage_systems


    def getUcpSystemByName(self, ucpname):
        funcName = 'hpe_infra:getUcpSystem'
        self.logger.writeEnterSDK(funcName)
        systems = self.getAllUcpSystem()
        system = next((x for x in systems if x.get('serialNumber')
                        == ucpname), None)
        self.logger.writeExitSDK(funcName)
        return system      

    def getAllUcpSystem(self):
        funcName = 'hpe_infra:getAllUcpSystem'
        self.logger.writeEnterSDK(funcName)

        urlPath = 'v2/systems'
        url = self.getUrl(urlPath)
        self.logger.writeInfo('url={}', url)
        headers = self.getAuthToken()
        response = requests.get(url, headers=headers,
                                verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            authResponse = response.json()
            self.logger.writeInfo('GetAllUcpResponse={}', authResponse)
            systems = authResponse.get('data')
            return systems
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getAllStorageSystemsInISP(self):
        funcName = 'hpe_infra:getAllStorageSystemsInISP'
        self.logger.writeEnterSDK(funcName)
        urlPath = 'v2/systems/default'
        url = self.getUrl(urlPath)
        self.logger.writeInfo('url={}', url)
        storage_systems = []
        headers = self.getAuthToken()
        response = requests.get(url, headers=headers, verify=self.shouldVerifySslCertification)
        if response.ok:
            ispResponse = response.json()
            self.logger.writeInfo('getAllStorageSystemsInISP Response={}', ispResponse)
            systems = ispResponse.get('data').get('storageDevices')
            storage_systems.extend(systems)
            self.logger.writeInfo('ispResponse={}', ispResponse)
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
           self.throwException(response)
        return storage_systems        

    def getAllStorageSystems(self):
        funcName = 'hpe_infra:getAllStorageSystems'
        self.logger.writeEnterSDK(funcName)

        urlPath = 'v2/storage/devices'
        url = self.getUrl(urlPath)
        ucp_systems = self.getAllUcpSystem()
        storage_systems = []
        for ucp in ucp_systems:
            sn = str(ucp.get('serialNumber'))
            self.logger.writeInfo(sn)
            body = {'ucpSystem': sn}
            self.logger.writeInfo('body={}', body)
            headers = self.getAuthToken()

            response = requests.get(url, headers=headers, params=body,
                                    verify=self.shouldVerifySslCertification)

            if response.ok:
                authResponse = response.json()

                # self.logger.writeInfo('authResponse={}', authResponse)

                systems = authResponse.get('data')
                storage_systems.extend(systems)
            elif 'HIJSONFAULT' in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:

                # self.logger.writeInfo('authResponse={}', response.json())

                self.throwException(response)
        return storage_systems

    def getStorageInfoByResourceId(self, resourceId):

        funcName = 'hpe_infra:getStorageInfoByResourceId'

        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('resourceId={}', resourceId)
        urlPath = 'v2/storage/devices/{0}'.format(resourceId)
        url = self.getUrl(urlPath)

        # body = {'id': resourceId}

        headers = self.getAuthToken()
        response = requests.get(url, headers=headers,
                                verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            authResponse = response.json()
            system = authResponse['data']
            #   system['StorageDeviceType'] = system.get('deviceType')
            #   system['StorageDeviceModel'] = system.get('model')

            #   self.logger.writeInfo(system.get('model'))
            #   del system['model']
            #   del system['deviceType']
            if system['operationalStatus'] is 'Running':
                time.sleep(10)
                system = self.getStorageInfoByResourceId(resourceId)
            return system
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    # def createLunInDP(
    #     self,
    #     lun,
    #     pool,
    #     sizeInGB,
    #     stripeSize,
    #     metaResourceSerial,
    #     luName,
    # ):

    #     funcName = 'hpe_infra:createLunInDP'
    #     self.logger.writeEnterSDK(funcName)
    #     self.logger.writeParam('lun={}', lun)
    #     self.logger.writeParam('pool={}', pool)
    #     self.logger.writeParam('sizeInGB={}', sizeInGB)
    #     self.logger.writeParam('stripeSize={}', stripeSize)
    #     self.logger.writeParam('metaResourceSerial={}',
    #                            metaResourceSerial)
    #     self.logger.writeParam('luName={}', luName)
    #     resourceId = 'storage-c6aaa5b557fd584db37e55e8b77b03c6'
    #     urlPath = 'porcelain/v2/storage/devices/{0}/volumes'.format(
    #         resourceId)
    #     url = self.getUrl(urlPath)
    #     self.logger.writeInfo('url={}', url)
    #     body = {
    #         'deduplicationCompressionMode': 'DISABLED',
    #         'poolId': 2,
    #         'name': 'test',
    #         'capacity': 1048576,
    #         'resourceGroupId': 0,
    #         'ucpSystem': 'demo-datastore-api-team',
    #     }

    #     headers = self.getAuthToken()

    #     response = requests.post(url, json=body, headers=headers,
    #                              verify=self.shouldVerifySslCertification)

    #     self.logger.writeExitSDK(funcName)
    #     if response.ok:
    #         resourceId = response.json()['resourceId']
    #         return self.getLunByResourceId(resourceId)
    #     elif 'HIJSONFAULT' in response.headers:
    #         Utils.raiseException(self.sessionId, response)
    #     else:
    #         raise Exception(
    #            self.throwException(response)

    def createLunInDP(
        self,
        lun,
        pool,
        size,
        dedup,
        name='',
    ):
        funcName = 'hpe_infra:createLunInDP'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lun={}', lun)
        self.logger.writeParam('pool={}', pool)
        self.logger.writeParam('sizeInGB={}', size)
        self.logger.writeParam('luName={}', name)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam('resourceId={}', resourceId)
        self.logger.writeParam('ucp={}', ucp)

        urlPath = 'v2/storage/devices/{0}/volumes'.format(resourceId)
        url = self.getUrl(urlPath)
        self.logger.writeInfo('url={}', url)
        body = {
            'deduplicationCompressionMode': 'DISABLED',
            'poolId': pool,
            'name': name,
            'capacity': size,
            'resourceGroupId': 0,
            'ucpSystem': ucp,
        }
        if lun is not None:
            body['lunId'] = lun
        self.logger.writeInfo('body={}', body)
        headers = self.getAuthToken()
        self.logger.writeInfo('headers={}', headers)
        response = requests.post(url, json=body, headers=headers,
                                 verify=self.shouldVerifySslCertification)
        self.logger.writeInfo('response={}', response.json())
        self.logger.writeExitSDK(funcName)
        if response.ok:
            resourceId = response.json()['data']['resourceId']
            self.logger.writeInfo('resourceId={}', resourceId)
            taskId = response.json()['data'].get('taskId')
            self.checkTaskStatus(taskId)
            time.sleep(15)
            lun = self.getLunIdFromTaskStatusEvents(taskId)
            return lun
        elif 'HIJSONFAULT' in response.headers:

            # return self.getLunByResourceId1(resourceId)

            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def updateLunInDP(
        self,
        lunResourceId,
        size
    ):
        funcName = 'hpe_infra:updateLunInDP'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lunResourceId={}', lunResourceId)
        self.logger.writeParam('sizeInGB={}', size)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam('resourceId={}', resourceId)
        self.logger.writeParam('lunResourceId={}', lunResourceId)
        self.logger.writeParam('ucp={}', ucp)

        urlPath = 'v2/storage/devices/{0}/volumes/{1}'.format(
            resourceId, lunResourceId)
        url = self.getUrl(urlPath)
        self.logger.writeInfo('url={}', url)
        body = {
            'capacity': size
        }
        self.logger.writeInfo('body={}', body)
        headers = self.getAuthToken()
        self.logger.writeInfo('headers={}', headers)
        response = requests.patch(url, json=body, headers=headers,
                                  verify=self.shouldVerifySslCertification)
        self.logger.writeInfo('response={}', response.json())
        self.logger.writeExitSDK(funcName)
        if response.ok:
            resourceId = response.json()['data']['resourceId']
            self.logger.writeInfo('resourceId={}', resourceId)
            taskId = response.json()['data'].get('taskId')
            self.checkTaskStatus(taskId)
            time.sleep(10)
        elif 'HIJSONFAULT' in response.headers:

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

        # funcName = 'hpe_infra:createLunInPG'
        # self.logger.writeEnterSDK(funcName)
        # self.logger.writeParam('lun={}', lun)
        # self.logger.writeParam('parityGroup={}', parityGroup)
        # self.logger.writeParam('sizeInGB={}', sizeInGB)
        # self.logger.writeParam('stripeSize={}', stripeSize)
        # self.logger.writeParam('metaResourceSerial={}',
                               # metaResourceSerial)
        # self.logger.writeParam('luName={}', luName)

        # urlPath = 'LogicalUnit/LogicalUnit/CreateInPGLite'
        # url = self.getUrl(urlPath)
        # self.logger.writeInfo('url={}', url)
        # body = {
            # 'sessionId': self.sessionId,
            # 'serialNumber': self.serial,
            # 'lun': lun or -1,
            # 'pg': parityGroup,
            # 'sizeInGB': sizeInGB,
            # 'stripeSize': stripeSize,
            # 'metaResourceSerial': metaResourceSerial or -1,
            # 'luName': luName or '',
        # }

        # response = requests.post(url, json=body,
                                 # verify=self.shouldVerifySslCertification)

        # self.logger.writeExitSDK(funcName)
        # if response.ok:
            # return response.json()
        # elif 'HIJSONFAULT' in response.headers:
            # Utils.raiseException(self.sessionId, response)
        # else:
            # self.throwException(response)
        funcName = 'hpe_infra:createLunInPG'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lun={}', lun)
        self.logger.writeParam('parityGroupId={}', parityGroup)
        self.logger.writeParam('sizeInGB={}', size)
                                                           
                                                       
                                                  
        self.logger.writeParam('luName={}', luName)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam('resourceId={}', resourceId)
        self.logger.writeParam('ucp={}', ucp)

        urlPath = 'v2/storage/devices/{0}/volumes'.format(resourceId)
        url = self.getUrl(urlPath)
        self.logger.writeInfo('url={}', url)
        body = {
            'parityGroupId': parityGroup,
            'name': luName,
            'capacity': size,
            'resourceGroupId': 0,
            'ucpSystem': ucp,
        }

        if lun is not None:
            body['lunId'] = lun
        self.logger.writeInfo('body={}', body)
        headers = self.getAuthToken()
        self.logger.writeInfo('headers={}', headers)
        response = requests.post(url, json=body, headers=headers,
                                 verify=self.shouldVerifySslCertification)
        self.logger.writeInfo('response={}', response.json())
        self.logger.writeExitSDK(funcName)
        if response.ok:
            resourceId = response.json()['data']['resourceId']
            self.logger.writeInfo('resourceId={}', resourceId)
            taskId = response.json()['data'].get('taskId')
            self.checkTaskStatus(taskId)
            time.sleep(5)
            if lun is None:
                lun = self.getLunIdFromTaskStatusEvents(taskId)
            return lun
        elif 'HIJSONFAULT' in response.headers:

            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def updateLunName(self,
        lunResourceId,
        lunName):
        funcName = 'hpe_infra:updateLunInDP'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lunResourceId={}', lunResourceId)
        self.logger.writeParam('sizeInGB={}', lunName)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam('resourceId={}', resourceId)
        self.logger.writeParam('lunResourceId={}', lunResourceId)
        self.logger.writeParam('ucp={}', ucp)

        urlPath = 'v2/storage/devices/{0}/volumes/{1}'.format(
            resourceId, lunResourceId)
        url = self.getUrl(urlPath)
        self.logger.writeInfo('url={}', url)
        body = {
            'lunName': lunName
        }
        self.logger.writeInfo('body={}', body)
        headers = self.getAuthToken()
        self.logger.writeInfo('headers={}', headers)
        response = requests.patch(url, json=body, headers=headers,
                                  verify=self.shouldVerifySslCertification)
        self.logger.writeInfo('response={}', response.json())
        self.logger.writeExitSDK(funcName)
        if response.ok:
            resourceId = response.json()['data']['resourceId']
            self.logger.writeInfo('resourceId={}', resourceId)
            taskId = response.json()['data'].get('taskId')
            self.checkTaskStatus(taskId)
            time.sleep(10)
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def setDedupCompression(self, lunResourceId, dedupMode):
        funcName = 'hpe_infra:setDedupCompression'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lunResourceId={}', lunResourceId)
        self.logger.writeParam('dedupMode={}', dedupMode)

        (resourceId, ucp) = self.getStorageSystemResourceId()

        self.logger.writeParam('resourceId={}', resourceId)
        self.logger.writeParam('lunResourceId={}', lunResourceId)
        self.logger.writeParam('ucp={}', ucp)

        urlPath = 'v2/storage/devices/{0}/volumes/{1}'.format(
            resourceId, lunResourceId)
        url = self.getUrl(urlPath)
        self.logger.writeInfo('url={}', url)
        body = {
            'deduplicationCompressionMode': dedupMode
        }
        self.logger.writeInfo('body={}', body)
        headers = self.getAuthToken()
        self.logger.writeInfo('headers={}', headers)
        response = requests.patch(url, json=body, headers=headers,
                                  verify=self.shouldVerifySslCertification)
        self.logger.writeInfo('response={}', response.json())
        self.logger.writeExitSDK(funcName)
        if response.ok:
            resourceId = response.json()['data']['resourceId']
            self.logger.writeInfo('resourceId={}', resourceId)
            taskId = response.json()['data'].get('taskId')
            self.checkTaskStatus(taskId)
            time.sleep(10)
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def cloneLunInDP(
        self,
        sourceLun,
        pool,
        clonedLunName,
    ):

        funcName = 'hpe_infra:cloneLunInDP'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('sourceLun={}', sourceLun)
        self.logger.writeParam('pool={}', pool)
        self.logger.writeParam('clonedLunName={}', clonedLunName)

        urlPath = 'LogicalUnit/LogicalUnit/CloneInDP'
        url = self.getUrl(urlPath)
        body = {
            'sessionId': self.sessionId,
            'serialNumber': self.serial,
            'lun': sourceLun,
            'pool': pool,
            'lunName': clonedLunName,
        }

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            taskId = response.json()['data'].get('taskId')
            return self.checkTaskStatus(taskId)
        elif 'HIJSONFAULT' in response.headers:
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

        funcName = 'hpe_infra:createPresentedVolume'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lun={}', lun)
        self.logger.writeParam('pool={}', pool)
        self.logger.writeParam('resourceGroupId={}', resourceGroupId)

        urlPath = 'LogicalUnit/LogicalUnit/CreatePresentedVolume'
        url = self.getUrl(urlPath)
        body = {
            'sessionId': self.sessionId,
            'serialNumber': self.serial,
            'lun': lun or -1,
            'resourceGroupId': resourceGroupId,
            'hostGroupName': hostGroupName or '',
            'port': port or '',
            'pool': pool,
            'sizeInMB': sizeInMB,
            'stripeSize': stripeSize or 0,
            'luName': luName or '',
        }

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def expandLun(self, lun, sizeInGB):

        funcName = 'hpe_infra:expandLun'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lun={}', lun)
        self.logger.writeParam('sizeInGB={}', sizeInGB)
        self.logger.writeParam('dryRun={}', self.dryRun)
        if self.dryRun:
            return

        urlPath = 'LogicalUnit/LogicalUnit/Expand'
        url = self.getUrl(urlPath)
        body = {
            'sessionId': self.sessionId,
            'serialNumber': self.serial,
            'lun': lun,
            'expandSizeInGB': sizeInGB,
        }

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            if 'HIJSONFAULT' in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)

    def expandLunInBytes(self, lun, sizeInBytes):

        funcName = 'hpe_infra:expandLun'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lun={}', lun)
        self.logger.writeParam('sizeInBytes={}', sizeInBytes)
        self.logger.writeParam('dryRun={}', self.dryRun)
        if self.dryRun:
            return

        urlPath = 'LogicalUnit/LogicalUnit/ExpandInBytes'
        url = self.getUrl(urlPath)
        body = {
            'sessionId': self.sessionId,
            'serialNumber': self.serial,
            'lun': lun,
            'expandSize': sizeInBytes,
        }

        response = RequestsUtils.post(url, json=body,
                                      verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            if 'HIJSONFAULT' in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)

    def deleteLun(self, lunResourceId):
        funcName = 'hpe_infra:deleteLun'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lunResourceId={}', lunResourceId)
        (storageResourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = \
            'v2/storage/devices/{0}/volumes/{1}'.format(storageResourceId,
                                                        lunResourceId)
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        self.logger.writeParam('url={}', url)
        response = requests.delete(url, headers=headers,
                                   verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        self.logger.writeInfo(response.status_code)
        if response.ok:
            return True
        else:
            self.throwException(response)

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            if 'HIJSONFAULT' in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)

    def getLun(self, lun, doRetry=True):

        funcName = 'hpe_infra:getLun'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lun={}', lun)
        luns = self.getAllLuns()
        foundlun = None
        for item in luns:
            try:
                if str(item['ldevId']) == str(lun):
                    foundlun = item
                    self.logger.writeInfo(foundlun)
                    break
            except Exception as e:
                self.logger.writeInfo(str(e))

        self.logger.writeExitSDK(funcName)
        return foundlun

    def getLunByResourceId(self, lunResourceId, doRetry=True):

        funcName = 'hpe_infra:getLunByResourceId'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lunResourceId={}', lunResourceId)
        (storageResourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = 'v2/storage/devices/{0}/volumes/{1}'.format(storageResourceId,
                                                              lunResourceId)
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        self.logger.writeParam('url={}', url)
        response = requests.get(url, headers=headers,
                                verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        self.logger.writeInfo(response.status_code)
        if response.ok:
            return response.json()['data']
        elif 'HIJSONFAULT' in response.headers:
            if doRetry:
                self.logger.writeInfo(funcName + ':{}', 'retry once')
                return self.getLunByResourceId(lunResourceId, False)
            else:
                Utils.raiseException(self.sessionId, response, False)
        else:
            self.throwException(response)

    def getLunByResourceId1(self, lunResourceId, doRetry=True):

        funcName = 'hpe_infra:getLunByResourceId1'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lunResourceId={}', lunResourceId)

        luns = self.getAllLuns()
        foundlun = None
        for item in luns:
            try:
                if str(item['resourceId']) == str(lunResourceId):
                    foundlun = item
                    break
            except Exception as e:
                self.logger.writeInfo(str(e))

        self.logger.writeExitSDK(funcName)
        return foundlun

    def throwException(self, response):
        raise Exception('{0}:{1}'.format(response.status_code, response.json().get('error')))

    def getLunByNaa(self, canonicalName):

        funcName = 'hpe_infra:getLunByNaa'
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

            self.serial = int(storageSerial)
            self.logger.writeInfo("storageSerial={0}".format(self.serial))

            lun = int(lunCode, 16)
            self.logger.writeInfo("lun={0}".format(lun))
            self.logger.writeExitSDK(funcName)
            return self.getLun(lun)

    def getLunByCountByNaa(self, lunCanonicalName, maxCount):

        funcName = 'hpe_infra:getLunByCountByNaa'
        self.logger.writeEnterSDK(funcName)

        urlPath = 'LogicalUnit/LogicalUnit/GetListByCountByCanonicalName'
        url = self.getUrl(urlPath)
        params = {'sessionId': self.sessionId,
                  'canonicalName': lunCanonicalName,
                  'maxCount': maxCount}

        self.logger.writeParam('url={}', url)
        self.logger.writeParam('params={}', params)

        response = requests.get(url, params=params,
                                verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getLunsByCount(self, startLDev, maxCount):

        funcName = 'hpe_infra:getLunsByCount'
        self.logger.writeEnterSDK(funcName)

        urlPath = 'LogicalUnit/LogicalUnit/GetListByCount'
        url = self.getUrl(urlPath)
        params = {
            'sessionId': self.sessionId,
            'serial': self.serial,
            'startLDev': startLDev,
            'maxCount': maxCount,
        }

        self.logger.writeParam('url={}', url)
        self.logger.writeParam('params={}', params)

        response = requests.get(url, params=params,
                                verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getLunsByRange(self, beginLDev, endLDev):

        funcName = 'hpe_infra:getLunsByRange'
        self.logger.writeEnterSDK(funcName)

        urlPath = 'LogicalUnit/LogicalUnit/GetListByRange'
        url = self.getUrl(urlPath)
        params = {
            'sessionId': self.sessionId,
            'serial': self.serial,
            'beginLDev': beginLDev,
            'endLDev': endLDev,
        }

        self.logger.writeParam('url={}', url)
        self.logger.writeParam('params={}', params)

        response = requests.get(url, params=params,
                                verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getAllLuns(self):

        funcName = 'hpe_infra:getAllLuns'
        self.logger.writeEnterSDK(funcName)
        (resourceId, ucp) = self.getStorageSystemResourceId()
        self.logger.writeInfo('Storage_resource_id={0}'.format(resourceId))
        urlPath = 'v2/storage/devices/{0}/volumes'.format(resourceId)
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.get(url, headers=headers,
                                verify=self.shouldVerifySslCertification)

        # self.logger.writeInfo('response.json()={}', response.json())

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()['data']
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def presentLun(
        self,
        luns,
        hgName,
        port,
    ):

        funcName = 'hpe_infra:presentLun'
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
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        body = {'ldevIds': list(map(int, luns))}

        response = requests.post(url, headers=headers, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)

        if not response.ok:
            if 'HIJSONFAULT' in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)
        else:
            taskId = response.json()['data'].get('taskId')
            self.checkTaskStatus(taskId)

    def checkTaskStatus(self, taskId):
        funcName = 'hpe_infra:checkTaskStatus'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('taskId={}', taskId)
        (status, name) = self.getTaskStatus(taskId)
        while status == 'Running':
            self.logger.writeInfo('{0} task with id {1} status is Running'.format(name,
                                                                                  taskId))
            time.sleep(5)
            (status, name) = self.getTaskStatus(taskId)

        if status.lower() == 'failed':
            description = self.getFailedTaskStatusDescription(taskId)
            self.logger.writeInfo('{0} task with id {1} is failed.'.format(name, taskId))
                                                                                  
            raise Exception('Operation failed. {0}'.format(description))
        self.logger.writeExitSDK(funcName)
        return status

    def getLunIdFromTaskStatusEvents(self, taskId):
        funcName = 'hpe_infra:getTaskStatusEvents'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('taskId={}', taskId)
        headers = self.getAuthToken()
        urlPath = '/v2/tasks/{0}'.format(taskId)
        url = self.getUrl(urlPath)
        response = requests.get(url, headers=headers,
                                verify=self.shouldVerifySslCertification)
        status = None
        name = None
        lun = None
        description = None
        if response.ok:
            status = response.json()['data'].get('status')
            name = response.json()['data'].get('name')

        if status.lower() == 'success':
            if event['description'].find("Successfully set capacity") != -1:
                    description = event['description']
            self.logger.writeParam('description={}', description)
            start = description.find("Successfully set capacity saving mode to DISABLED for volume") + len("Successfully set capacity saving mode to DISABLED for volume")
            end = description. find(" on")
            lun = description[start:end]
            parsedLun = 'parsedLun={0}'.format(lun)
            self.logger.writeInfo(parsedLun)
        elif status.lower() == 'processing':
            lun = self.getLunIdFromTaskStatusEvents(taskId)
        else:
            for event in response.json()['data']['events']:
                if event['description'].find("Unable to create volume") != -1:
                    description = event['description']           
                    self.logger.writeParam('description={}', description)
                    raise Exception('Operation failed. {0}'.format(description))
        self.logger.writeExitSDK(funcName)
        return lun.strip()

    def getTaskStatus(self, taskId):
        funcName = 'hpe_infra: getTaskStatus'
        self.logger.writeEnterSDK(funcName)
        headers = self.getAuthToken()
        urlPath = '/v2/tasks/{0}'.format(taskId)
        url = self.getUrl(urlPath)
        response = requests.get(url, headers=headers, verify=self.shouldVerifySslCertification)
        status = None
        name = None
        if response.ok:
            status = response.json()['data'].get('status')
            name = response.json()['data'].get('name')
        return (status, name)
      
    def getFailedTaskStatusDescription(self, taskId):
        funcName = 'hpe_infra: getFailedTaskStatusDescription'
        self.logger.writeEnterSDK(funcName)
        headers = self.getAuthToken()
        urlPath = '/v2/tasks/{0}'.format(taskId)
        url = self.getUrl(urlPath)
        response = requests.get(url, headers=headers, verify=self.shouldVerifySslCertification)
        description = None
        if response.ok:
            status = response.json()['data'].get('status')
            name = response.json()['data'].get('name')
            events = response.json()['data'].get('events')
            descriptions = [element.get('description') for element in events]
            self.logger.writeInfo('-'.join(descriptions))
            description = events[-1].get('description')
            self.logger.writeInfo(description)
        return ('-'.join(descriptions))    
        

    def unpresentLun(
        self,
        luns,
        hgName,
        port,
    ):

        funcName = 'hpe_infra:UnpresentLun'
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
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        body = {'ldevIds': list(map(int, luns))}

        response = requests.delete(url, headers=headers, json=body,
                                   verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)

        self.logger.writeExitSDK(funcName)
        if not response.ok:
            if 'HIJSONFAULT' in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)
        else:
            taskId = response.json()['data'].get('taskId')
            self.checkTaskStatus(taskId)

    def createHostGroup(
        self,
        hgName,
        port,
        wwnList,
        hostmode,
        hostModeOptions
    ):

        funcName = 'hpe_infra:createHostGroup'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('wwnList={}', wwnList)
        self.logger.writeParam('hgName={}', hgName)
        self.logger.writeParam('port={}', port)
        self.logger.writeParam('dryRun={}', self.dryRun)
        if self.dryRun:
            return

        (resourceId, ucp) = self.getStorageSystemResourceId()
        self.logger.writeParam('resourceId={}', resourceId)
        self.logger.writeParam('ucp={}', ucp)
        wwns=[]
        for x in list(wwnList):
           wwns.append( {
                "id": x
            })
        body = {
            'hostGroupName': str(hgName),
            'port': str(port),
            'ucpSystem': ucp,
            'hostMode': hostmode,                                      
            'hostModeOptions': list(hostModeOptions)
        }
        
        if len(wwns) >0 :
            body['wwns']=wwns

        self.logger.writeParam('body={}', body)
        urlPath = 'v2/storage/devices/{0}/hostGroups'.format(resourceId)
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.post(url, headers=headers, json=body,
                                 verify=self.shouldVerifySslCertification)
        self.logger.writeInfo(url)
        self.logger.writeInfo(body)
        if not response.ok:
            if 'HIJSONFAULT' in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)
        else:
            taskId = response.json()['data'].get('taskId')
            self.checkTaskStatus(taskId)

        self.logger.writeExitSDK(funcName)

    def deleteHostGroup(self, hgName, port):

        funcName = 'hpe_infra:deleteHostGroup'
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
        hgResourceId = hostgroup.get('resourceId')
        urlPath = 'v2/storage/devices/{0}/hostGroups/{1}'.format(
            resourceId, hgResourceId)
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.delete(url, headers=headers,
                                   verify=self.shouldVerifySslCertification)
        if not response.ok:
            if 'HIJSONFAULT' in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)
        else:
            self.logger.writeInfo(response)
            # taskId = response.json()['data'].get('taskId')
            # self.checkTaskStatus(taskId)
            self.logger.writeExitSDK(funcName)

    def getHostGroup(
        self,
        hgName,
        port,
        doRetry=True,
    ):

        funcName = 'hpe_infra:getHostGroup'
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
                break
        return hostgroup

    def getVSM(self):

        funcName = 'hpe_infra:getVSM'
        self.logger.writeEnterSDK(funcName)

        urlPath = 'StorageManager/StorageManager/GetVirtualStorageSystems'
        url = self.getUrl(urlPath)
        body = {'sessionId': self.sessionId}

        response = requests.get(url, params=body,
                                verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getAllHostGroups(self):

        funcName = 'hpe_infra:getAllHostGroups'
        self.logger.writeEnterSDK(funcName)

        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = 'v2/storage/devices/{0}/hostGroups?refresh=false'.format(resourceId)
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.get(url, headers=headers,
                                verify=self.shouldVerifySslCertification)
        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()['data']
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    # def getAllHostgroups(self):
    #     funcName = 'hpe_infra:getAllHostgroups'
    #     self.logger.writeEnterSDK(funcName)
    #     resourceId = self.getStorageSystemResourceId()
    #     urlPath = 'v2/storage/devices/{0}/hostGroups'.format(resourceId)
    #     url = self.getUrl(urlPath)
    #     headers = self.getAuthToken()
    #     response = requests.get(url, headers=headers,
    #                             verify=self.shouldVerifySslCertification)

    #     self.logger.writeExitSDK(funcName)
    #     if response.ok:
    #         self.logger.writeInfo('response.json()={}',
    #                                response.json())
    #         return response.json()['data']
    #     elif 'HIJSONFAULT' in response.headers:
    #         Utils.raiseException(self.sessionId, response)
    #     else:
    #         raise Exception(
    #            self.throwException(response)

    def getHostGroupsForLU(self, lun):

        funcName = 'hpe_infra:getHostGroupsForLU'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('lun={}', lun)

        urlPath = 'HostGroup/HostGroup/GetHostGroupsForLU'
        url = self.getUrl(urlPath)
        body = {'sessionId': self.sessionId,
                'serialNumber': self.serial, 'lu': lun}

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif 'HIJSONFAULT' in response.headers:
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
        funcName = 'hpe_infra:setHostMode'
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
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
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
            if 'HIJSONFAULT' in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)
        else:
            taskId = response.json()['data'].get('taskId')
            self.checkTaskStatus(taskId)
            time.sleep(5)

        self.logger.writeExitSDK(funcName)

    def addWWN(
        self,
        hgName,
        port,
        wwnList,
    ):

        funcName = 'hpe_infra:addWWN'
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
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.post(url, headers=headers, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeInfo(url)
        self.logger.writeInfo(body)
        if not response.ok:
            if 'HIJSONFAULT' in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)
        else:
            taskId = response.json()['data'].get('taskId')
            self.checkTaskStatus(taskId)
        self.logger.writeExitSDK(funcName)

    def removeWWN(
        self,
        hgName,
        port,
        wwnList,
    ):

        funcName = 'hpe_infra:removeWWN'
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
        body = {
            'wwns': list(wwnList),
        }
        self.logger.writeParam('body={}', body)
        urlPath = 'v2/storage/devices/{0}/hostGroups/{1}/wwns'.format(resourceId, hgResourceId)
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.delete(url, headers=headers, json=body,
                                 verify=self.shouldVerifySslCertification)
        self.logger.writeInfo(url)
        self.logger.writeInfo(body)
        if not response.ok:
            if 'HIJSONFAULT' in response.headers:
                Utils.raiseException(self.sessionId, response)
            else:
                self.throwException(response)
        else:
            time.sleep(5)
            # taskId = response.json()['data'].get('taskId')
            # self.checkTaskStatus(taskId)

        self.logger.writeExitSDK(funcName)
    def getPorts(self):

        funcName = 'hpe_infra:getPorts'
        self.logger.writeEnterSDK(funcName)
        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = 'v2/storage/devices/{0}/ports?refresh={1}'.format(resourceId, True)
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.get(url, headers=headers,
                                verify=self.shouldVerifySslCertification)
        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getStoragePools(self):

        funcName = 'hpe_infra:getStoragePools'
        self.logger.writeExitSDK(funcName)

        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = 'v2/storage/devices/{0}/pools'.format(resourceId)
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.get(url, headers=headers,
                                verify=self.shouldVerifySslCertification)
        self.logger.writeExitSDK(funcName)
        if response.ok:
            self.logger.writeInfo('pools={}',
                                   response.json())
            return response.json()['data']
        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getJournalPools(self):

        funcName = 'hpe_infra:getJournalPools'
        self.logger.writeEnterSDK(funcName)

        (resourceId, ucp) = self.getStorageSystemResourceId()
        self.logger.writeInfo('Journal ucp={}', ucp)
        urlPath = 'v2/storage/devices/{0}/journalpool?refresh=true&ucpSystem={1}'.format(resourceId, ucp)
        url = self.getUrl(urlPath)
        self.logger.writeInfo('Journal urlpath={}', url)
        headers = self.getAuthToken()

        response = requests.get(url, headers=headers,
                                verify=self.shouldVerifySslCertification)
        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()['data']
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getFreeLUList(self):

        funcName = 'hpe_infra:getFreeLUList'
        self.logger.writeEnterSDK(funcName)

        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = 'v2/storage/devices/{0}/freeVolumes?count={1}&ucpSystem={2}'.format(resourceId, 100, ucp)
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.get(url, headers=headers,
                                verify=self.shouldVerifySslCertification)
        self.logger.writeExitSDK(funcName)
        if response.ok:
            self.logger.writeInfo('pools={}',
                                   response.json())
            return response.json()['data']
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getFreeGADConsistencyGroupId(self):

        funcName = 'hpe_infra:getFreeGADConsistencyGroupId'
        self.logger.writeEnterSDK(funcName)

        urlPath = 'TrueCopy/GetFreeGADConsistencyGroupId'
        url = self.getUrl(urlPath)

        body = {'sessionId': self.sessionId, 'serial': self.serial}

        response = requests.get(url, params=body,
                                verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getFreeHTIConsistencyGroupId(self):

        funcName = 'hpe_infra:getFreeHTIConsistencyGroupId'
        self.logger.writeEnterSDK(funcName)

        urlPath = 'TrueCopy/GetFreeLocalConsistencyGroupId'
        url = self.getUrl(urlPath)

        body = {'sessionId': self.sessionId, 'serial': self.serial}

        response = requests.get(url, params=body,
                                verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getFreeTCConsistencyGroupId(self):

        funcName = 'hpe_infra:getFreeTCConsistencyGroupId'
        self.logger.writeEnterSDK(funcName)

        urlPath = 'TrueCopy/GetFreeRemoteConsistencyGroup'
        url = self.getUrl(urlPath)

        body = {'sessionId': self.sessionId, 'serial': self.serial}

        response = requests.get(url, params=body,
                                verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getFreeURConsistencyGroupId(self):

        funcName = 'hpe_infra:getFreeURConsistencyGroupId'
        self.logger.writeEnterSDK(funcName)

        urlPath = 'TrueCopy/GetFreeUniversalReplicatorConsistencyGroup'
        url = self.getUrl(urlPath)

        body = {'sessionId': self.sessionId, 'serial': self.serial}

        response = requests.get(url, params=body,
                                verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getQuorumDisks(self):

        funcName = 'hpe_infra:getQuorumDisks'
        self.logger.writeEnterSDK(funcName)
        (resourceId, ucp) = self.getStorageSystemResourceId()
        urlPath = 'v2/storage/devices/{0}/quorum/disks'.format(resourceId)
        url = self.getUrl(urlPath)
        headers = self.getAuthToken()
        response = requests.get(url, headers=headers,
                                verify=self.shouldVerifySslCertification)
        self.logger.writeExitSDK(funcName)
        if response.ok:
            self.logger.writeInfo('pools={}',
                                   response.json())
            return response.json()['data']
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getResourceGroups(self):

        funcName = 'hpe_infra:getResourceGroups'
        self.logger.writeEnterSDK(funcName)

        urlPath = 'ResourceGroup/GetList'
        url = self.getUrl(urlPath)

        body = {'sessionId': self.sessionId, 'serial': self.serial}

        response = requests.get(url, params=body,
                                verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def getDynamicPools(self):

        funcName = 'hpe_infra:getDynamicPools'
        self.logger.writeEnterSDK(funcName)

        urlPath = 'StoragePool/GetStoragePools'
        url = self.getUrl(urlPath)

        body = {'sessionId': self.sessionId,
                'serialNumber': self.serial}

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def createDynamicPool(
        self,
        name,
        luns,
        poolType,
    ):

        funcName = 'hpe_infra:createDynamicPool'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('name={}', name)
        self.logger.writeParam('luns={}', luns)
        self.logger.writeParam('poolType={}', poolType)

        urlPath = 'StoragePool/CreateDynamicPool'
        url = self.getUrl(urlPath)

        body = {
            'sessionId': self.sessionId,
            'serialNumber': self.serial,
            'poolName': name,
            'luList': ','.join(map(str, luns)),
            'poolType': PoolCreateType.fromString(poolType),
        }

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return response.json()
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def expandDynamicPool(self, poolId, luns):

        funcName = 'hpe_infra:expandDynamicPool'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('luns={}', luns)
        self.logger.writeParam('poolId={}', poolId)

        urlPath = 'StoragePool/ExpandDynamicPool'
        url = self.getUrl(urlPath)

        body = {
            'sessionId': self.sessionId,
            'serialNumber': self.serial,
            'poolId': poolId,
            'ldevList': ','.join(map(str, luns)),
        }

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def shrinkDynamicPool(self, poolId, luns):

        funcName = 'hpe_infra:shrinkDynamicPool'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('luns={}', luns)
        self.logger.writeParam('poolId={}', poolId)

        urlPath = 'StoragePool/ShrinkDynamicPoolUsingPoolID'
        url = self.getUrl(urlPath)

        body = {
            'sessionId': self.sessionId,
            'serialNumber': self.serial,
            'poolId': poolId,
            'ldevList': ','.join(map(str, luns)),
        }

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def doPost(
        self,
        urlPath,
        body,
        returnJson=False,
    ):

        funcName = 'hpe_infra:doPost'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('urlPath={}', urlPath)
        self.logger.writeParam('body={}', body)
        url = self.getUrl(urlPath)
        self.logger.writeParam('url={}', url)
        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)
        self.logger.writeInfo('response={}', response)

        if response.ok:
            self.logger.writeExitSDK(funcName)
            if returnJson:
                self.logger.writeInfo('response.json()={}',
                                       response.json())
                return response.json()
            else:
                return
        elif 'HIJSONFAULT' in response.headers:
            Utils.raiseException(self.sessionId, response)
        else:
            self.throwException(response)

    def deleteDynamicPool(self, poolId):

        funcName = 'hpe_infra:deleteDynamicPool'
        self.logger.writeEnterSDK(funcName)
        self.logger.writeParam('poolId={}', poolId)

        urlPath = 'StoragePool/DeleteDynamicPool'
        url = self.getUrl(urlPath)

        body = {'sessionId': self.sessionId,
                'serialNumber': self.serial, 'poolId': poolId}

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        self.logger.writeExitSDK(funcName)
        if response.ok:
            return
        elif 'HIJSONFAULT' in response.headers:
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

        urlPath = 'StoragePool/SetDynamicPoolCapacityThreshold'
        url = self.getUrl(urlPath)

        body = {
            'sessionId': self.sessionId,
            'serialNumber': self.serial,
            'poolId': poolId,
            'warningRate': warningRate,
            'depletionRate': depletionRate,
            'enableNotification': enableNotification,
        }

        response = requests.post(url, json=body,
                                 verify=self.shouldVerifySslCertification)

        if response.ok:
            return
        elif 'HIJSONFAULT' in response.headers:
            raise Exception(json.loads(response.headers['HIJSONFAULT']))
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
        'UNKNOWN',
        'NOT_SPECIFIED',
        'RESERVED',
        'LINUX',
        'VMWARE',
        'HP',
        'OPEN_VMS',
        'TRU64',
        'SOLARIS',
        'NETWARE',
        'WINDOWS',
        'HI_UX',
        'AIX',
        'VMWARE_EXTENSION',
        'WINDOWS_EXTENSION',
        'UVM',
        'HP_XP',
        'DYNIX',
    ]

    @ staticmethod
    def getHostModeNum(hm):
        hostmode = hm.upper()

        if hostmode == 'STANDARD':
            hostmode = 'LINUX'
        hostmode = re.sub(r"WIN($|_)", r"WINDOWS\1", hostmode)
        hostmode = re.sub(r"EXT?$", 'EXTENSION', hostmode)

        if hostmode not in HostMode.modes:
            raise Exception("Invalid host mode: '{0}'".format(hm))

        return HostMode.modes.index(hostmode)

    @ staticmethod
    def getHostModeName(hostmode):
        if isinstance(hostmode, str):
            return hostmode
        return HostMode.modes[hostmode]


class DedupMode:

    modes = ['DISABLED', 'COMPRESSION', 'COMPRESSION_DEDUPLICATION']


class RequestsUtils:

    @ staticmethod
    def get(url, params, verify):
        try:
            return requests.get(url, params=params, verify=verify)
        except requests.exceptions.Timeout:
            raise Exception(' Timeout exception. Perhaps webserivce is not reachable or down ? '
                            )
        except requests.exceptions.TooManyRedirects:
            raise Exception('Mas retry error. Perhaps webserivce is not reachable or down ?'
                            )
        except requests.exceptions.RequestException as e:
            raise Exception(' Connection Error. Perhaps web serivce is not reachable is down ? '
                            )

    @ staticmethod
    def post(url, json, verify):
        try:
            return requests.post(url, json=json, verify=verify)
        except requests.exceptions.Timeout:
            raise Exception(' Timeout exception. Perhaps webserivce is not reachable or down ? '
                            )
        except requests.exceptions.TooManyRedirects:
            raise Exception('Mas retry error. Perhaps webserivce is not reachable or down ?'
                            )
        except requests.exceptions.RequestException as e:
            raise Exception(' Connection Error. Perhaps web serivce is not reachable is down ? '
                            )
