#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type
import json

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_infra import StorageSystem, \
    StorageSystemManager
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_infra import Utils
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_log import Log, \
    HiException

logger = Log()
moduleName = 'LUN facts'


def runPlaybook(module):
    logger.writeEnterModule(moduleName)

    data = json.loads(module.params['data'])
    lun = data.get('lun')
    count = data.get('max_count')
    lun_end = data.get('lun_end')
    name = data.get('name')

    storage_serial = module.params.get('storage_serial', None)
    logger.writeParam('storage_serial={}', storage_serial)
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
    logger.writeDebug(isinstance(lun, int))

    if lun is not None and ':' in str(lun):
        lun = Utils.getlunFromHex(lun)
        logger.writeDebug('Hex converted lun={0}'.format(lun))

    if lun is not None:
        if not isinstance(lun, int) and lun.startswith('naa.'):
            logger.writeDebug('Parsing Naa lun={0}'.format(lun))
            storage_serial = Utils.getSerialByNaa(lun)
            logger.writeDebug('storage_serial={0}'.format(storage_serial))

    if storage_serial is None:
        if lun is not None and lun.startswith('naa.'):
            storage_serial = 'get.lun.naa'
        else:
            raise Exception('The storage_serial is missing.')
    logger.writeDebug('Utils.isGivenValidSerial(storage_serial)={0}'.format(
        Utils.isGivenValidSerial(storage_serial)))
    if not Utils.isGivenValidSerial(storage_serial):
        raise Exception(
            'Storage system {0} is not registered. Double-check the serial number or run the hv_storagesystem \
            module with this storage system.'.format(storage_serial))

    storageSystem = StorageSystem(storage_serial)

    if lun is not None:
        luns = []
        if not isinstance(lun, int) and lun.startswith('naa.'):
            if count is None:
                lun = storageSystem.getLunByNaa(lun)
                if lun:
                    luns.append(lun)
            else:
                if int(count) < 1:
                    raise Exception("The parameter 'count' must be a whole number greater than zero."
                                    )  #
                lunswithcount = None
                luns = storageSystem.getAllLuns()
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
            luns = storageSystem.getAllLuns()
            # g = (i for i, e in enumerate([1, 2, 1]) if e == 1)

            # logger.writeInfo(luns)
            # index = [index for index, item in luns if item.get(
            #     'ldevId') == str(lun)]
            lunswithcount = None
            for index, item in enumerate(luns):
                if(str(item.get('ldevId')) == str(lun)):
                    logger.writeDebug('index={}', index)
                    lunswithcount = luns[index:index + int(count)]
                    break
            logger.writeInfo(lunswithcount)
            luns = lunswithcount
            # luns = storageSystem.getLunsByCount(lun, count)
        elif lun_end is not None:
            lunswithcount = []
            luns = storageSystem.getAllLuns()
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
    elif data.get('luns') is not None:

        # # terraform only

        logger.writeParam('luns={}', data['luns'])
        luns = [unit for unit in storageSystem.getAllLuns()
                if unit['ldevId'] in data['luns']]
    elif data.get('name') is not None:
        logger.writeParam('name={}', data['name'])
        luns = [unit for unit in storageSystem.getAllLuns()
                if unit['name'] == data['name']]
    else:
        luns = storageSystem.getAllLuns()

    Utils.formatLuns(luns)
    logger.writeExitModule(moduleName)
    module.exit_json(luns=luns)
