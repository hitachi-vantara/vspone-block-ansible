#!/usr/bin/python
# -*- coding: utf-8 -*-

__metaclass__ = type
import json
import re

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachi.storage.plugins.module_utils.hv_storagemanager import StorageManager
from ansible_collections.hitachi.storage.plugins.module_utils.hv_ucpmanager import UcpManager
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystem, \
    StorageSystemManager
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import Utils
from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log, \
    HiException

logger = Log()
moduleName = 'LUN facts'


def runPlaybook(module):
    logger.writeEnterModule(moduleName)

    data = json.loads(module.params['spec'])
    lun = data.get('lun')
    count = data.get('max_count')
    lun_end = data.get('lun_end')
    name = data.get('name')

    ucp_advisor_info = json.loads(module.params['ucp_advisor_info'])
    ucpadvisor_address = ucp_advisor_info.get('address', None)
    ucpadvisor_username = ucp_advisor_info.get('username', None)
    ucpadvisor_password = ucp_advisor_info.get('password', None)

    storage_system_info = json.loads(module.params['storage_system_info'])
    storage_serial = storage_system_info.get('serial', None)
    ucp_serial = storage_system_info.get('ucp_name', None)

    logger.writeParam('20230606 storage_serial={}', storage_serial)
    logger.writeParam('lun={}', lun)
    logger.writeParam('name={}', name)
    logger.writeParam('count={}', count)
    logger.writeParam('lun_end={}', lun_end)

    if storage_serial == '':
        storage_serial = None
    if lun == '':
        lun = None
    if count == '':
        count = None
    if lun_end == '':
        lun_end = None
    if name == '':
        name = None

    if ucp_serial == '':
        ucp_serial = None

    if ucp_serial is None:
        raise Exception('The ucp_name is invalid.')

    # x = re.search("^(UCP-CI|UCP-HC|UCP-RS|Logical-UCP)-\d{5,10}$", ucp_serial)
    # if not x:
    #     raise Exception('The ucp_serial is invalid.')

 
    ## check the healthStatus=onboarding
    ucpManager = UcpManager(
        ucpadvisor_address,
        ucpadvisor_username,
        ucpadvisor_password,
        storage_serial,
        )
    if ucpManager.isOnboarding():
        raise Exception("Storage system is onboarding, please try again later.")
   

    # lun is a int?    
    logger.writeDebug(isinstance(lun, int))

    if lun is not None and ':' in str(lun):
        lun = Utils.getlunFromHex(lun)
        logger.writeDebug('Hex converted lun={0}'.format(lun))
        if lun is None:
            raise Exception('The LUN is not found.')

    # if lun is not None:
    #     if not isinstance(lun, int) and lun.startswith('naa.'):
    #         logger.writeDebug('Parsing Naa lun={0}'.format(lun))
    #         storage_serial = Utils.getSerialByNaa(lun)
    #         logger.writeDebug('storage_serial={0}'.format(storage_serial))

    if storage_serial is None:
        if lun is not None and lun.startswith('naa.'):
            storage_serial = 'get.lun.naa'
        else:
            raise Exception('The storage_serial is missing.')
    # logger.writeDebug('Utils.isGivenValidSerial(storage_serial)={0}'.format(
    #     Utils.isGivenValidSerial(storage_serial)))
    # if not Utils.isGivenValidSerial(storage_serial):
    #     raise Exception(
    #         'Storage system {0} is not registered. Double-check the serial number or run the hv_storagesystem \
    #         module with this storage system.'.format(storage_serial))

    # storageSystem = StorageSystem(storage_serial)
    logger.writeDebug('20230606 storage_serial={}',storage_serial)
    storageSystem = UcpManager(
        ucpadvisor_address,
        ucpadvisor_username,
        ucpadvisor_password,
        storage_serial)
    
    if lun is None and count is not None:
        raise Exception("The lun parameter is required along with max_count.")
    
    luns = None
    if lun is not None:
        luns = []
        if not isinstance(lun, int) and lun.startswith('naa.'):
            logger.writeDebug('20230606 count={}',count)
            if count is None:
                lun = storageSystem.getLunByNaa(lun)
                if lun:
                    luns.append(lun)
            else:
                if int(count) < 1:
                    raise Exception("The parameter 'count' must be a whole number greater than zero."
                                    )  #
                lunswithcount = None
                logger.writeInfo('getLunByNaa getAllLuns')
                luns = storageSystem.getLunByID(lun)
                logger.writeDebug('20230606 count={}',count)
                lun = storageSystem.getLunByNaa(lun)
                for index, item in enumerate(luns):
                    if(str(item.get('ldevId')) == str(lun.get('ldevId'))):
                        logger.writeDebug('index={}', index)
                        lunswithcount = luns[index:index + int(count)]
                        break
                luns = lunswithcount
            logger.writeDebug('luns={}', luns)
        elif count is not None:
            if int(count) < 1:
                raise Exception("The parameter 'count' must be a whole number greater than zero."
                                )
            if lun_end is not None:
                raise Exception('Ambiguous parameters, max_count and lun_end cannot co-exist.'
                                )
            
            logger.writeInfo('getAllLuns count={}',count)
            # luns = storageSystem.getAllLuns()
            luns = storageSystem.getLunByID(lun)
            # logger.writeDebug('20230606 getAllLuns luns={}', luns)
            # g = (i for i, e in enumerate([1, 2, 1]) if e == 1)

            # logger.writeInfo(luns)
            # index = [index for index, item in luns if item.get(
            #     'ldevId') == str(lun)]
            lunswithcount = []
            logger.writeDebug('20230606 find lun by ldevId={}', lun)
            for index, item in enumerate(luns):
                if(str(item.get('ldevId')) == str(lun)):
                    logger.writeDebug('20230606 found index={}', index)
                    logger.writeDebug('20230606 count={}', count)
                    lunswithcount = luns[index:index + int(count)]
                    break
            # logger.writeDebug('20230606 lunswithcount={}', lunswithcount)
            luns = lunswithcount
            # luns = storageSystem.getLunsByCount(lun, count)
        elif lun_end is not None:
            lunswithcount = []
            logger.writeInfo('20230606 lun_end={}', lun_end)
            # luns = storageSystem.getAllLuns()
            luns = storageSystem.getLunByID(lun)
            # luns = storageSystem.getLunsByRange(lun, lun_end)
            foundlun = None
            foundLunEnd = None
            for index, item in enumerate(luns):
                if str(item.get('ldevId')) == str(lun):
                    lunswithcount.append(item)
                    logger.writeParam('lunswithcount={}', lunswithcount)
                    foundlun = True
                elif foundlun and int(item.get('ldevId')) <= int(lun_end):
                    if str(item.get('ldevId')) == str(lun_end):
                        foundLunEnd = True
                    lunswithcount.append(item)
                    logger.writeParam('lunswithcount={}', lunswithcount)
                    if foundLunEnd:
                        break
                elif foundlun and int(item.get('ldevId')) > int(lun_end):
                    break

            luns = lunswithcount

        else:
            lun = storageSystem.getLun(lun)
            if lun:
                luns.append(lun)
        if luns:
            logger.writeDebug('response: luns={}', luns)
    elif luns is not None:

        # # terraform only

        logger.writeInfo('getAllLuns luns={}', luns)
        luns = [unit for unit in storageSystem.getAllLuns()
                if unit['ldevId'] in luns]
    elif name is not None:
        logger.writeInfo('getAllLuns name={}', name)
        luns = [unit for unit in storageSystem.getAllLuns()
                if unit['name'] == name]
    else:
        logger.writeInfo('getAllLuns')
        luns = storageSystem.getAllLuns()

    Utils.formatLuns(luns)
    logger.writeExitModule(moduleName)
    module.exit_json(luns=luns)
