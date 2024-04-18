#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
import re
import collections
import time

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_infra import StorageSystem, \
    StorageSystemManager, DedupMode
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_infra import Utils
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_log import Log, \
    HiException

logger = Log()
moduleName = 'LUN'


def loggingDebug(msg):
    logger.writeDebug(msg)
    pass


def loggingInfo(msg):
    logger.writeInfo(msg)
    pass


def handleResizeInDP(
    storageSystem,
    logicalUnit,
    size,
    storagePool,
    cap_saving_setting,
    lun_name,
    result,
):
    size = getSizeInbytes(size)
    loggingInfo(' entered handleResizeInDP, size={0}'.format(size))
    if logicalUnit.get('parityGroup'):
        raise Exception('Cannot resize ({0}) logical units in a parity group.'.format(logicalUnit.get('TotalCapacity'
                                                                                                      )))
    elif float(size) < float(logicalUnit.get('totalCapacity')):
        raise Exception('Cannot resize logical unit to a size less than its current total capacity.'
                        )
    elif float(size) > float(logicalUnit.get('totalCapacity')):
        lun = logicalUnit['ldevId']
        lunResourceId = logicalUnit['resourceId']
        # size = (size * 1024 - logicalUnit.get('totalCapacity')) / 1024
        # loggingDebug('expandLun lun={0}'.format(lun))
        # sizeInBlock = size * 1024 * 1024 * 1024 / 512
        # sizeInBytes = long(sizeInBlock) * 512
        # storageSystem.expandLunInBytes(lun, sizeInBytes)
        storageSystem.updateLunInDP(lunResourceId, size)
        result['changed'] = True
        loggingDebug('after expandLun')
        logicalUnit = storageSystem.getLun(lun)
    return logicalUnit


def handleResize(
    storageSystem,
    logicalUnit,
    size,
    result,
):
    size = getSizeInbytes(size)
    loggingDebug(' enter handleResizeInDP, size={0}'.format(size))
    if logicalUnit.get('parityGroup'):
        raise Exception('Cannot resize ({0}) logical units in a parity group.'.format(logicalUnit.get('TotalCapacity'
                                                                                                      )))
    elif float(size) < logicalUnit.get('totalCapacity'):
        raise Exception('Cannot resize logical unit to a size less than its current total capacity.'
                        )
    elif float(size) > logicalUnit.get('totalCapacity'):
        lun = logicalUnit['ldevId']
        size = (size * 1024 - logicalUnit.get('totalCapacity')) / 1024
        loggingDebug('expandLun lun={0}'.format(lun))
        # sizeInBlock = size * 1024 * 1024 * 1024 / 512
        # sizeInBytes = long(sizeInBlock) * 512
        # storageSystem.expandLunInBytes(lun, sizeInBytes)
        if lun.get('totalCapacity') is not None:
            lun['totalCapacity'] = \
                Utils.formatCapacity(lun['totalCapacity'])
        result['changed'] = True
        loggingDebug('after expandLun')
        # logicalUnit = storageSystem.getLun(lun)

    return logicalUnit


def getSizeInbytes(size):
    match = re.match(r'(^\d*[.]?\d*)(\D*)', str(size))
    if match:
        sizetype = match.group(2).upper().strip() or 'GB'
        logger.writeInfo('sizetype={}', sizetype)
        if sizetype not in ('GB', 'TB'):
            raise Exception('This module only accepts GB or TB sizes.')
        else:
            size = float(match.group(1))
            if sizetype == 'TB':
                size *= 1024
        sizeInBlock = size * 1024 * 1024 * 1024 / 512
        sizeInBytes = long(sizeInBlock) * 512
        return sizeInBytes


def getLogicalUnit(storageSystem, lun):
    loggingDebug('Enter local getLogicalUnit lun={0}'.format(lun))

    if lun is None:
        return None

    logicalUnit = storageSystem.getLun(lun)

    return logicalUnit


def getLogicalUnitsByName(storageSystem, lun_name):
    loggingDebug('Enter getLogicalUnitsByName lun_name={0}'.format(lun_name))

    if lun_name is None:
        return None

    logicalUnits = []

    # # SIEAN-201
    # # for idempotent, we cannot getLun this way,
    # # it will error out with exception in the main(),
    # # have to get all then search
    # # logicalUnit = storageSystem.getLun(lun)

    luns = storageSystem.getAllLuns()

    # loggingDebug("luns={0}".format(luns))

    for item in luns:
        if str(item['Name']) == str(lun_name):
            logicalUnits.append(item)
            break

    return logicalUnits


def isExistingLun(storageSystem, lun):
    try:
        lun = storageSystem.getLun(lun)
        loggingDebug('isExistingLun, lun={0}'.format(lun))
        return True
    except Exception as ex:
        loggingDebug('is NOT ExistingLun, ex={0}'.format(ex))
        return False

def isValidParityGroup(paritygroup):
    try:
        pg = parity_group.replace("-","")
        loggingDebug('isValidaParityGroup, pg={0}'.format(pg))
        p = int(pg)
        return True
    except Exception as ex:
        return False

def runPlaybook(module):
    logger.writeEnterModule(moduleName)
    storage_serial = module.params['storage_serial']

    if not Utils.isGivenValidSerial(storage_serial):
        raise Exception(
            'Storage system {0} is not registered. Double-check the serial number or run the hv_storagesystem \
            module with this storage system.'.format(storage_serial))

    storageSystem = StorageSystem(storage_serial)
    data = json.loads(module.params['data'])
    lun = data.get('luns', None)

    parity_group = data.get('parity_group', None)
    if parity_group == '':
        parity_group = None

    # if parity_group is not None and not isValidParityGroup(parity_group):
    #     raise Exception('Not a valid Parity group: {0}, please check once and try again.'.format(parity_group))
    

    if lun is not None and lun == '':

        # # example: luns is optional items in the del_lun playbook and omitted

        lun = None

    if lun is None:
        lun = data.get('lun', None)
        if lun == '':
            lun = None
    else:
        if isinstance(lun, list) and len(lun) == 0:
            lun = None
    clonedLunName = data.get('cloned_lun_name', None)
    if clonedLunName == '':
        clonedLunName = None

    result = {'changed': False}

    stripeSizes = ['0', '64', '256', '512']
    stripeSize = data.get('stripe_size', 512)
    if str(stripeSize) not in stripeSizes:
        raise Exception('Valid value for stripe size is 0, 64, 256 or 512 KB'
                        )

    logger.writeParam('lun={}', lun)
    logger.writeParam('clonedLunName={}', clonedLunName)
    logger.writeParam('stripeSizes={}', stripeSizes)
    logger.writeParam('state={}', module.params['state'])

    loggingDebug('luns={0}'.format(lun))
    logicalUnit = None
    logicalUnits = None
    lunName = data.get('name', None)
    if lunName == '':
        lunName = None

    def compare(x, y):
        return collections.Counter(x) == collections.Counter(y)

    c_d_setting = ['compression', 'deduplication']
    cap_saving_setting = data.get('cap_saving', None)
    loggingDebug('cap_saving_setting={0}'.format(cap_saving_setting))
    if isinstance(cap_saving_setting, list):
        c_list = [str(c).strip() for c in cap_saving_setting]
        logger.writeDebug(c_list)
        if compare(c_d_setting, sorted(c_list)):
            cap_saving_setting = "COMPRESSION_DEDUPLICATION"
        elif compare(['compression'], c_list):
            cap_saving_setting = "COMPRESSION"
        elif compare(['disable'], c_list):
            cap_saving_setting = "DISABLED"
        else:
            raise Exception(
                'Entered {0} is not a valid cap save setting.'.format(cap_saving_setting))
    elif cap_saving_setting == '':
        cap_saving_setting = None

    loggingDebug('lunName={0}'.format(lunName))
    loggingDebug('cap_saving_setting={0}'.format(cap_saving_setting))
    lunNameMatch = []

    if lun is not None and ':' in str(lun):
        lun = Utils.getlunFromHex(lun)
        loggingDebug('Hex converted lun={0}'.format(lun))

    if lun is not None:
        try:
            lun = int(lun)
        except ValueError:
            raise Exception('Entered {0} is not valid.'.format(lun))

    # # lun can be an empty array

    if lun is not None:

        # #handle delete

        if lun > 65535:
            raise Exception('Entered ldevid {0} is not valid.'.format(lun))
        elif isExistingLun(storageSystem, lun) is False \
                and module.params['state'] == 'absent':
            logicalUnit = None
        else:
            logicalUnit = getLogicalUnit(storageSystem, lun)
    elif lunName is not None:

        lunNameMatch = [unit for unit in storageSystem.getAllLuns()
                        if str(unit.get('name')) == lunName]
        loggingDebug('lunNameMatch={0}'.format(lunNameMatch))
        if len(lunNameMatch) > 0:
            logicalUnits = lunNameMatch
        if len(lunNameMatch) == 1:
            logicalUnit = lunNameMatch[0]

    loggingInfo('logicalUnit={0}'.format(logicalUnit))

    if module.params['state'] == 'present':
        size = data.get('size', None)
        if size == '':
            size = None

        # match = re.match(r'(\d+)(\D*)', str(size))

        logger.writeParam('size={}', size)
        entered_size = size
        if size is not None:
            match = re.match(r'(^\d*[.]?\d*)(\D*)', str(size))
            if match:
                sizetype = match.group(2).upper().strip() or 'GB'
                logger.writeInfo('sizetype={}', sizetype)
                if sizetype not in ('GB', 'TB'):
                    raise Exception('This module only accepts GB or TB sizes.'
                                    )
                else:
                    size = float(match.group(1))
                    if sizetype == 'TB':
                        size *= 1024
        elif logicalUnit is None and size is None:
            raise Exception('Size is required. This module only accepts GB or TB sizes.'
                            )

        if size is not None and float(size * 1024) < 1024:
            entered_size = str(float(int(size * 1024))) + 'MB'
        if lun is None and logicalUnit is not None and lunName \
            == logicalUnit.get('name') and entered_size \
            == Utils.formatCapacity(logicalUnit.get('totalCapacity'),
                                    2):
            logicalUnit = None

        loggingDebug('state={0}'.format(module.params['state']))

        # ###Update Lun Name

        if lunName is not None and lun is not None and logicalUnit \
                is not None:

            # # LUN exists, idempotent

            if lunName != logicalUnit.get('name'):
                loggingDebug('update the lunName')
                result['changed'] = True
                lunResourceId = logicalUnit['resourceId']
                storageSystem.updateLunName(lunResourceId, lunName)
                logicalUnit['name'] = lunName

        if cap_saving_setting is not None and logicalUnit is not None:
            loggingDebug(cap_saving_setting)

            if str(logicalUnit.get('deduplicationCompressionMode')) != str(cap_saving_setting):
                loggingDebug('update the cap_saving_setting')
                result['changed'] = True
                lunResourceId = logicalUnit['resourceId']
                storageSystem.setDedupCompression(lunResourceId,
                                                    cap_saving_setting)
                logicalUnit = getLogicalUnit(storageSystem, lun)


        poolInfo = data.get('storage_pool', None)
        if poolInfo == '':
            poolInfo = None
        storagePool = None
        parity_group = data.get('parity_group', None)
        if parity_group == '':
            parity_group = None

        if poolInfo is not None:
            loggingDebug('storagePool={0}'.format(storagePool))
            storage_pool_id = poolInfo.get('id', None)
            if storage_pool_id == '':
                storage_pool_id = None
            storage_pool_name = poolInfo.get('name', None)
            if storage_pool_name == '':
                storage_pool_name = None

            if parity_group:
                raise Exception('Cannot create LUN with both storage pool and parity group!'
                                )
            elif storage_pool_id is not None:
                storagePool = int(storage_pool_id)
                loggingDebug(
                    'storagePool.id from poolInfo={0}'.format(storagePool))
            elif storage_pool_name is not None:
                matchingPools = [pool for pool in
                                 storageSystem.getStoragePools()
                                 if pool['Name'] and pool['Name']
                                 == str(poolInfo['name'])]
                if matchingPools:
                    storagePool = int(matchingPools[0]['Id'])
                else:
                    raise Exception('No storage pools found with name {0}'.format(poolInfo['name'
                                                                                           ]))

            # else:
            #     raise Exception("Cannot create LUN using storage pool without specifying its name or id")
            #

        loggingDebug('check clonedLunName')
        loggingDebug(size)
        loggingDebug(poolInfo)
        loggingDebug(parity_group)
        loggingDebug(storagePool)
        loggingDebug(logicalUnit)

        if clonedLunName is not None:
            loggingDebug('Clone mode')
            if not logicalUnit:
                reason = ('More than 1 LUN found with the given name'
                          if len(lunNameMatch)
                          > 1 else 'No LUN found with the given lun/name'
                          )
                raise Exception(
                    'Cannot clone logical unit. {0}.'.format(reason))
            elif storagePool is not None:
                new_lun = \
                    storageSystem.cloneLunInDP(logicalUnit['ldevId'
                                                           ], storagePool, clonedLunName)
                lunInfo = storageSystem.getLun(new_lun)
                logger.writeInfo('lunInfo={}', lunInfo)
                result['lun'] = lunInfo
                result['changed'] = True
                Utils.formatLun(result['lun'])
            else:
                raise Exception('Cannot clone logical unit without a storage pool.'
                                )
        elif size is not None and logicalUnit is not None:

            # if lun is None, consider create only, no idempotent,
            # even if logicalUnit is not None, since it is found by lun_name

            loggingDebug('Expand mode, lun={0}'.format(logicalUnit['ldevId']))
            loggingDebug('Expand mode, name={0}'.format(logicalUnit['name']))

            # Expand mode. Only if logical unit was found.

            if len(lunNameMatch) > 1:
                raise Exception('Cannot expand logical unit. More than 1 LUN found with the given name. Use lun parameter instead.')
            elif logicalUnit:
                result['changed'] = False
                logicalUnit = handleResizeInDP(storageSystem, logicalUnit, size, storagePool, cap_saving_setting, lunName, result)
                result['lun'] = logicalUnit
                Utils.formatLun(result['lun'])
        elif logicalUnit is None and (storagePool is not None
                                      or parity_group is not None):

            loggingDebug(
                'Create mode, parity_group.id={0}'.format(parity_group))

            # Create mode.

            if lun is None:

                # # if lun is not given, no idempotent, let it create

                logicalUnit = None

            loggingDebug('lun={0}'.format(lun))
            loggingDebug('logicalUnit={0}'.format(logicalUnit))

            if not size:
                raise Exception('Cannot create logical unit. No size given (or size was set to 0).'
                                )
            elif storagePool is not None:
                loggingDebug('storagePool={0}'.format(storagePool))
                loggingDebug('logicalUnit={0}'.format(logicalUnit))
                if logicalUnit is not None:

                    # idempotency

                    result['comment'] = 'Logical unit already exist.'

                    # check for invalid pool id

                    if str(storagePool) != str(logicalUnit['poolId']):
                        loggingDebug('storagePool={0}'.format(logicalUnit['poolId'
                                                                          ]))
                        result['comment'] = \
                            'Logical unit {0} is already created with PoolId {1}'.format(
                                logicalUnit['ldevId'], logicalUnit['poolId'])
                    stripeSize = data.get('stripeSize')
                    if stripeSize is not None and str(stripeSize) \
                            != str(logicalUnit['stripeSize']):
                        result['comment'] = \
                            'Logical unit {0} is already created with stripeSize {1}'.format(logicalUnit['ldevId'
                                                                                                         ], logicalUnit['stripeSize'])
                    result['changed'] = False
                    new_lun = None

                    # handleResize idempotent

                    logicalUnit = handleResize(storageSystem,
                                               logicalUnit, size, result)
                    loggingInfo('LogicalUnit={0}'.format(logicalUnit))

                else:
                    loggingDebug('size={0}'.format(size))

                    # new_lun = storageSystem.createLunInDP(
                    #     lun,
                    #     storagePool,
                    #     size,
                    #     data.get('stripe_size', 0),
                    #     data.get('meta_serial', -1)
                    # )

                    new_lun = storageSystem.createLunInDP(
                        lun, storagePool, getSizeInbytes(size), cap_saving_setting, lunName)
                    if len(lunNameMatch) > 0:
                        lunName = lunName + '_' + hex(int(new_lun))
                    else:
                        lunName = data.get('name', '')
                    loggingDebug('lunName={0}'.format(lunName))
                    loggingDebug('new_lun={0}'.format(new_lun))

                    # if lunName != '':
                    #    storageSystem.updateLunName(new_lun, lunName)
                # if cap_saving_setting is not None:

                    # # LUN exists, idempotent

                    # loggingDebug('update the cap_saving_setting')
                    # storageSystem.setDedupCompression(new_lun, cap_saving_setting)
            elif parity_group is not None:
                loggingDebug('parity_group={0}'.format(parity_group))
                loggingDebug('logicalUnit={0}'.format(logicalUnit))
                if logicalUnit is not None:

                    # idempotency

                    result['comment'] = 'Logical unit already exist.'

                    # check for invalid pool id

                    if parity_group != logicalUnit['poolId']:
                        raise Exception('Logical unit {0} is already created with PoolId {1}'.format(logicalUnit['ldevId'
                                                                                                                 ], logicalUnit['poolId']))
                    stripeSize = data.get('stripeSize')
                    if stripeSize is not None and str(stripeSize) \
                            != str(logicalUnit['stripeSize']):
                        raise Exception('Logical unit {0} is already created with stripeSize {1}'.format(logicalUnit['ldevId'
                                                                                                                     ], logicalUnit['stripeSize']))
                    result['changed'] = False
                    new_lun = None
                else:

                    # resize lun in parity group is not supported?
                    # logicalUnit = handleResize(storageSystem, logicalUnit, size, result)

                    new_lun = storageSystem.createLunInPG(
                        lun,
                        parity_group,
                        getSizeInbytes(size),
                        data.get('stripe_size', 0),
                        data.get('meta_serial', -1),
                        data.get('name', ''),
                    )
                    lunName = data.get('name', '')
                    # if lunName != '':
                    #     storageSystem.updateLunName(new_lun, lunName)
                    if cap_saving_setting is not None:

                        # # LUN exists, idempotent

                        loggingDebug('update the cap_saving_setting')
                        storageSystem.setDedupCompression(new_lun,
                                                          cap_saving_setting)
            else:
                raise Exception('Cannot create logical unit. No storage pool or parity group given.'
                                )

            if new_lun is None:
                result['lun'] = logicalUnit
                result['comment'] = 'Logical unit already exist.'
            else:
                # Get the successful lun object for returning
                lunInfo = None
                i = 0
                while i < 100 and lunInfo is None:
                  lunInfo = storageSystem.getLun(new_lun)
                  i += 1
                  time.sleep(10)                  
                logger.writeInfo('lunInfo={}', lunInfo)
                Utils.formatLun(lunInfo)
                result['lun'] = lunInfo
                result['changed'] = True
        else:
            loggingInfo(logicalUnit)
            result['lun'] = logicalUnit
            Utils.formatLun(result['lun'])
    else:

        # state == absent

        loggingDebug('delete mode')
        if logicalUnit is not None:
            loggingInfo(int(logicalUnit['pathCount']))
            if int(logicalUnit['pathCount']) >= 1:
                raise Exception('Cannot delete LUN: Lun is mapped to a hostgroup!')
            storageSystem.deleteLun(logicalUnit['resourceId'])
            result['comment'] = 'LUN is deleted'
            result['lun'] = logicalUnit
            result['changed'] = True
            Utils.formatLun(result['lun'])
        elif lun is None and lunName is None:
            raise Exception('Cannot delete LUN: No lun or name was specified!'
                            )
        elif lunName is not None and len(lunNameMatch) > 1:
            raise Exception('Cannot delete LUN: More than 1 LUN with matching name found! Use lun parameter instead.'
                            )
        else:
            result['lun'] = None
            result['comment'] = \
                'LUN not found. (Perhaps it has already been deleted?)'
            result['skipped'] = True

    logger.writeExit(moduleName)
    module.exit_json(**result)
