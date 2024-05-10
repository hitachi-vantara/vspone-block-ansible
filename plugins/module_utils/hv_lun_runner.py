#!/usr/bin/python
# -*- coding: utf-8 -*-

__metaclass__ = type

import json
import re
import collections
import time

from ansible.module_utils.basic import AnsibleModule
# from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystem, \
#     StorageSystemManager, DedupMode
from ansible_collections.hitachi.storage.plugins.module_utils.hv_storagemanager import StorageManager
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import Utils
from ansible_collections.hitachi.storage.plugins.module_utils.hv_ucpmanager import UcpManager
from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log, \
    HiException

logger = Log()
moduleName = 'LUN'

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
    loggingInfo('handleResizeInDP, size={0}'.format(size))

    sizeInBytes = getSizeInbytes(size)
    loggingInfo('handleResizeInDP, size={0}'.format(size))

    loggingInfo(' entered handleResizeInDP, size={0}'.format(sizeInBytes))
    if logicalUnit.get('parityGroup'):
        raise Exception('Cannot resize ({0}) logical units in a parity group.'.format(logicalUnit.get('TotalCapacity'
                                                                                                      )))
    elif float(sizeInBytes) < float(logicalUnit.get('totalCapacity')):
        raise Exception('Cannot resize logical unit to a size less than its current total capacity.'
                        )
    elif float(sizeInBytes) > float(logicalUnit.get('totalCapacity')):
        lun = logicalUnit['ldevId']
        lunResourceId = logicalUnit['resourceId']
        # size = (size * 1024 - logicalUnit.get('totalCapacity')) / 1024
        loggingInfo('expandLun lun={0}'.format(lun))
        # sizeInBlock = size * 1024 * 1024 * 1024 / 512
        # sizeInBytes = long(sizeInBlock) * 512
        # storageSystem.expandLunInBytes(lun, sizeInBytes)
        logger.writeInfo('updateLunInDP sizeInBytes={0}'.format(sizeInBytes))
        storageSystem.updateLunInDP(lunResourceId, sizeInBytes)
        result['changed'] = True
        loggingInfo('after expandLun')
        logicalUnit = storageSystem.getLun(lun)
    return logicalUnit


def handleResize(
    storageSystem,
    logicalUnit,
    size,
    result,
):
    size = getSizeInbytes(size)
    loggingInfo(' enter handleResizeInDP, size={0}'.format(size))
    if logicalUnit.get('parityGroup'):
        raise Exception('Cannot resize ({0}) logical units in a parity group.'.format(logicalUnit.get('TotalCapacity'
                                                                                                      )))
    elif float(size) < logicalUnit.get('totalCapacity'):
        raise Exception('Cannot resize logical unit to a size less than its current total capacity.'
                        )
    elif float(size) > logicalUnit.get('totalCapacity'):
        lun = logicalUnit['ldevId']
        size = (size * 1024 - logicalUnit.get('totalCapacity')) / 1024
        loggingInfo('expandLun lun={0}'.format(lun))
        # sizeInBlock = size * 1024 * 1024 * 1024 / 512
        # sizeInBytes = long(sizeInBlock) * 512
        # storageSystem.expandLunInBytes(lun, sizeInBytes)
        if lun.get('totalCapacity') is not None:
            lun['totalCapacity'] = \
                Utils.formatCapacity(lun['totalCapacity'])
        result['changed'] = True
        loggingInfo('after expandLun')
        # logicalUnit = storageSystem.getLun(lun)

    return logicalUnit


def getSizeInbytes(size):
    logger.writeInfo('getSizeInbytes size={}', size)
    match = re.match(r'(^\d*[.]?\d*)(\D*)', str(size))
    if match:
        sizetype = match.group(2).upper().strip() or 'MB'
        logger.writeInfo('getSizeInbytes sizetype={}', sizetype)
        if sizetype not in ('GB', 'TB', 'MB'):
            raise Exception('This module only accepts MB, GB or TB sizes.')
        else:
            size = float(match.group(1))
            if sizetype == 'TB':
                size = size * 1024 * 1024
            if sizetype == 'GB':
                size *= 1024
        sizeInBlock = size * 1024 * 1024 / 512
        sizeInBytes = int(sizeInBlock) * 512
        return sizeInBytes


def getLogicalUnit(storageSystem, lun):
    loggingInfo('Enter local getLogicalUnit lun={0}'.format(lun))

    if lun is None:
        return None

    logicalUnit = storageSystem.getLun(lun)

    return logicalUnit


def getLogicalUnitsByName(storageSystem, lun_name):
    loggingInfo('Enter getLogicalUnitsByName lun_name={0}'.format(lun_name))

    if lun_name is None:
        return None

    logicalUnits = []

    # # SIEAN-201
    # # for idempotent, we cannot getLun this way,
    # # it will error out with exception in the main(),
    # # have to get all then search
    # # logicalUnit = storageSystem.getLun(lun)

    luns = storageSystem.getAllLuns()

    # loggingInfo("luns={0}".format(luns))

    for item in luns:
        if str(item['Name']) == str(lun_name):
            logicalUnits.append(item)
            break

    return logicalUnits


def isExistingLun(storageSystem, lun):
    try:
        lun = storageSystem.getLun(lun)
        loggingInfo('isExistingLun, lun={0}'.format(lun))
        return True
    except Exception as ex:
        loggingInfo('is NOT ExistingLun, ex={0}'.format(ex))
        return False

def isValidParityGroup(paritygroup):
    try:
        pg = parity_group.replace("-","")
        loggingInfo('isValidaParityGroup, pg={0}'.format(pg))
        p = int(pg)
        return True
    except Exception as ex:
        return False
       
def runPlaybook(module):
    logger.writeEnterModule(moduleName)

    storage_system_info = json.loads(module.params['storage_system_info'])
    storage_serial = storage_system_info.get('serial')
    ucp_serial = storage_system_info.get('ucp_name')

    ucp_advisor_info = json.loads(module.params['ucp_advisor_info'])
    ucpadvisor_address = ucp_advisor_info.get('address')
    ucpadvisor_ansible_vault_user = ucp_advisor_info.get('username')
    ucpadvisor_ansible_vault_secret = ucp_advisor_info.get('password')

    ucp_advisor_info['password'] = '******'
    module.params['ucp_advisor_info'] = json.dumps(ucp_advisor_info)

    if storage_serial is None:
        raise Exception('The input parameter storage_serial is required.')
    if ucp_serial is None:
        raise Exception('The input parameter ucp_name is required.')

    logger.writeParam('storage_serial={}', storage_serial)
    logger.writeParam('ucp_serial={}', ucp_serial)
    logger.writeParam('ucpadvisor_address={}', ucpadvisor_address)
    logger.writeParam('ucpadvisor_ansible_vault_user={}', ucpadvisor_ansible_vault_user)

    storageSystem = None
    try:
        storageSystem = StorageManager(
            ucpadvisor_address,
            ucpadvisor_ansible_vault_user,
            ucpadvisor_ansible_vault_secret,
            storage_serial,
            ucp_serial
        )
    except Exception as ex:
        module.fail_json(msg=ex.message)

    if not storageSystem.isStorageSystemInUcpSystem():
        raise Exception("Storage system is not under the ucp system.")

    ## check the healthStatus=onboarding
    ucpManager = UcpManager(
        ucpadvisor_address,
        ucpadvisor_ansible_vault_user,
        ucpadvisor_ansible_vault_secret,
        storage_serial,
        )
    if ucpManager.isOnboarding():
        raise Exception("Storage system is onboarding, please try again later.")

    lun_info = json.loads(module.params['spec'])
    lun = lun_info.get('luns', None) ### note, it is using 'luns'

    parity_group = lun_info.get('parity_group', None)
    if parity_group == '':
        parity_group = None
    # if parity_group is not None and not isValidParityGroup(parity_group):
    #     raise Exception('Not a valid Parity group: {0}, please check once and try again.'.format(parity_group))

    if lun is not None and lun == '':
        lun = None

    if lun is None:
        lun = lun_info.get('lun', None)
        if lun == '':
            lun = None
    else:
        if isinstance(lun, list) and len(lun) == 0:
            lun = None
    clonedLunName = lun_info.get('cloned_lun_name', None)
    if clonedLunName == '':
        clonedLunName = None

    result = {'changed': False}

    stripeSizes = ['0', '64', '256', '512']
    stripeSize = lun_info.get('stripe_size', 512)
    if str(stripeSize) not in stripeSizes:
        raise Exception('Valid value for stripe size is 0, 64, 256 or 512 KB'
                        )

    logger.writeParam('lun={}', lun)
    logger.writeParam('clonedLunName={}', clonedLunName)
    logger.writeParam('stripeSizes={}', stripeSizes)
    logger.writeParam('state={}', module.params['state'])

    loggingInfo('luns={0}'.format(lun))
    logicalUnit = None
    logicalUnits = None
    lunName = lun_info.get('name', None)
    if lunName == '':
        lunName = None

    def compare(x, y):
        return collections.Counter(x) == collections.Counter(y)

    c_d_setting = ['compression', 'deduplication']
    cap_saving_setting = lun_info.get('capacity_saving', None)    
    loggingInfo('20230621 cap_saving_setting={0}'.format(cap_saving_setting))

    if cap_saving_setting is not None:
        if isinstance(cap_saving_setting, list):
            c_list = [str(c).strip() for c in cap_saving_setting]
            logger.writeInfo(c_list)
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
        else:
            if cap_saving_setting == 'compression':
                cap_saving_setting = "COMPRESSION"
            elif cap_saving_setting == 'deduplication' :
                cap_saving_setting = "COMPRESSION_DEDUPLICATION"
            elif cap_saving_setting == 'disable' :
                cap_saving_setting = "DISABLED"
            elif module.params['state'] != 'absent':
                raise Exception( "Possible values for capacity_saving are ['compression', 'deduplication', 'disable']" )

    loggingInfo('lunName={0}'.format(lunName))
    loggingInfo('cap_saving_setting={0}'.format(cap_saving_setting))
    lunNameMatch = []

    if lun is not None and ':' in str(lun):
        lun = Utils.getlunFromHex(lun)
        loggingInfo('Hex converted lun={0}'.format(lun))

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

        loggingInfo('312 lunName={0}'.format(lunName))
        lunNameMatch = [unit for unit in storageSystem.getAllLuns()
                        if str(unit.get('name', None)) == lunName]
        loggingInfo('lunNameMatch={0}'.format(lunNameMatch))
        if len(lunNameMatch) > 0:
            logicalUnits = lunNameMatch
        if len(lunNameMatch) == 1:
            logicalUnit = lunNameMatch[0]

    loggingInfo('logicalUnit={0}'.format(logicalUnit))

    if module.params['state'] == 'present':
        size = lun_info.get('size', None)
        if size == '':
            size = None

        # match = re.match(r'(\d+)(\D*)', str(size))

        logger.writeParam('size={}', size)
        entered_size = size
        if size is not None:
            match = re.match(r'(^\d*[.]?\d*)(\D*)', str(size))
            if match:
                sizetype = match.group(2).upper().strip() or 'MB'
                logger.writeInfo('L333 sizetype={}', sizetype)
                if sizetype not in ('GB', 'TB', 'MB'):
                    raise Exception('This module only accepts MB, GB or TB sizes.'
                                    )
                else:
                    size = float(match.group(1))
                    if sizetype == 'TB':
                        size = size * 1024 * 1024
                    if sizetype == 'GB':
                        size *= 1024
        elif logicalUnit is None and size is None:
            raise Exception('Size is required. This module only accepts MB, GB or TB sizes.'
                            )

        if size is not None and float(size * 1024) < 1024:
            entered_size = str(float(int(size * 1024))) + 'MB'
        if lun is None and logicalUnit is not None and lunName \
            == logicalUnit.get('name') and entered_size \
            == Utils.formatCapacity(logicalUnit.get('totalCapacity'),
                                    2):
            logicalUnit = None

        loggingInfo('state={0}'.format(module.params['state']))

        # ###Update Lun Name

        if lunName is not None and lun is not None and logicalUnit \
                is not None:

            # # LUN exists, idempotent

            if lunName != logicalUnit.get('name'):
                loggingInfo('update the lunName')
                result['changed'] = True
                lunResourceId = logicalUnit['resourceId']
                storageSystem.updateLunName(lunResourceId, lunName)
                logicalUnit['name'] = lunName

        if cap_saving_setting is not None and logicalUnit is not None:
            loggingInfo(cap_saving_setting)
            # loggingInfo(DedupMode.modes.index(str(logicalUnit.get('dedupCompressionMode'
            #                                                        ))))

            if str(logicalUnit.get('deduplicationCompressionMode')) != str(cap_saving_setting):
                loggingInfo('update the cap_saving_setting')
                result['changed'] = True
                lunResourceId = logicalUnit['resourceId']
                storageSystem.setDedupCompression(lunResourceId,
                                                  cap_saving_setting)
                logicalUnit = getLogicalUnit(storageSystem, lun)

        parity_group = lun_info.get('parity_group', None)
        if parity_group == '':
            parity_group = None

        storagePool = None
        storage_pool_id = lun_info.get('pool_id', None)
        if storage_pool_id == '':
            storage_pool_id = None

        loggingInfo('20230617 parity_group={0}'.format(parity_group))
        loggingInfo('20230617 storage_pool_id={0}'.format(storage_pool_id))

        if parity_group is not None and storage_pool_id is not None:
            raise Exception('Cannot create LUN with both storage pool and parity group!'
                            )
        
        if lun is None:
            if parity_group is None and storage_pool_id is None:
                # for create lun only
                raise Exception('Either pool_id or parity_group is required.')

        if parity_group is not None:
            if cap_saving_setting is not None:
                raise Exception('The capacity_saving parameter is in conflict with parity_group.')
            if parity_group.count('-') > 1:
                raise Exception('The parity_group value is not valid.')
            if parity_group[0] == 'E':
                x = re.search(r"^E([1-9]|[1-9][0-9])-([1-9]|[1-9][0-9])\b", parity_group)
            else:
                x = re.search( r"^([1-9]|[1-9][0-9])-([1-9]|[1-9][0-9])\b", parity_group)
            if not x :
                raise Exception('The parity_group value is not valid.')

        if storage_pool_id is not None:
            storagePool = int(storage_pool_id)
            loggingInfo('storage_pool_id={0}'.format(storage_pool_id))

        loggingInfo('check clonedLunName')
        loggingInfo(size)
        loggingInfo(parity_group)
        loggingInfo(storagePool)
        loggingInfo(logicalUnit)

        if clonedLunName is not None:
            loggingInfo('Clone mode')
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
                lunInfo = None
                i = 0
                while i < 100 and lunInfo is None:
                  lunInfo = storageSystem.getLun(new_lun)
                  i += 1
                  time.sleep(3)
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

            loggingInfo('Expand mode, lun={0}'.format(logicalUnit['ldevId']))
            loggingInfo('Expand mode, name={0}'.format(logicalUnit['name']))

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

            loggingInfo('Create mode, parity_group.id={0}'.format(parity_group))
            if lun is None:
                logicalUnit = None

            loggingInfo('lun={0}'.format(lun))
            loggingInfo('logicalUnit={0}'.format(logicalUnit))

            if not size:
                raise Exception('Cannot create logical unit. No size given (or size was set to 0).'
                                )
            elif storagePool is not None:
                loggingInfo('storagePool={0}'.format(storagePool))
                loggingInfo('logicalUnit={0}'.format(logicalUnit))
                if logicalUnit is not None:

                    # idempotency

                    result['comment'] = 'Logical unit already exist.'

                    # check for invalid pool id

                    if str(storagePool) != str(logicalUnit['poolId']):
                        loggingInfo('storagePool={0}'.format(logicalUnit['poolId'
                                                                          ]))
                        result['comment'] = \
                            'Logical unit {0} is already created with PoolId {1}'.format(
                                logicalUnit['ldevId'], logicalUnit['poolId'])
                    stripeSize = lun_info.get('stripeSize')
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
                    logger.writeDebug('LogicalUnit={0}'.format(logicalUnit))

                else:
                    logger.writeInfo('createLunInDP size={0}'.format(size))
                    logger.writeInfo('createLunInDP sizetype={0}'.format(sizetype))

                    new_lun = storageSystem.createLunInDP(
                        lun, 
                        storagePool, 
                        getSizeInbytes(size), 
                        cap_saving_setting, 
                        lunName
                        )
                    if len(lunNameMatch) > 0:
                        lunName = lunName + '_' + hex(int(new_lun))
                    else:
                        lunName = lun_info.get('name', '')
                    logger.writeDebug('lunName={0}'.format(lunName))
                    logger.writeDebug('new_lun={0}'.format(new_lun))

                    # if lunName != '':
                    #     storageSystem.updateLunName(new_lun, lunName)
                # if cap_saving_setting is not None:

                    # # LUN exists, idempotent

                    # loggingInfo('update the cap_saving_setting')
                    # storageSystem.setDedupCompression(new_lun, cap_saving_setting)
            elif parity_group is not None:
                logger.writeDebug('parity_group={0}'.format(parity_group))
                logger.writeDebug('logicalUnit={0}'.format(logicalUnit))
                if logicalUnit is not None:

                    # idempotency
                    result['comment'] = 'Logical unit already exist.'

                    # check for invalid pool id

                    if parity_group != logicalUnit['poolId']:
                        raise Exception('Logical unit {0} is already created with PoolId {1}'.format(logicalUnit['ldevId'
                                                                                                                 ], logicalUnit['poolId']))
                    stripeSize = lun_info.get('stripeSize')
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
                        lun_info.get('stripe_size', 0),
                        lun_info.get('meta_serial', -1),
                        lun_info.get('name', ''),
                    )
                    lunName = lun_info.get('name', '')
                    # if lunName != '':
                        # storageSystem.updateLunName(new_lun, lunName)
                    # if cap_saving_setting is not None:

                        # # # LUN exists, idempotent

                        # loggingInfo('update the cap_saving_setting')
                        # storageSystem.setDedupCompression(new_lun,
                                                          # cap_saving_setting)
            else:
                raise Exception('Cannot create logical unit. No storage pool or parity group given.'
                                )

            if new_lun is None:
                result['lun'] = logicalUnit
                result['comment'] = 'Logical unit already exist.'
            else:
                lunInfo = None
                logger.writeDebug('20230617 validate new_lun={}', new_lun)

                i = 0
                while i < 100 and lunInfo is None:
                  lunInfo = storageSystem.getLun(new_lun)
                  i += 1
                  time.sleep(10) 

                # logger.writeDebug('lunInfo={}', lunInfo)
                if lunInfo is None:
                    logger.writeDebug('20230617 volume {} is created, but timed out looking for it.', new_lun)
                    result['comment'] = 'Volume {} is created, but timed out looking for it.'.format(new_lun)
                else:
                    Utils.formatLun(lunInfo)
                result['lun'] = lunInfo
                result['changed'] = True
        else:
            logger.writeDebug(logicalUnit)
            result['lun'] = logicalUnit
            Utils.formatLun(result['lun'])
    else:

        # state == absent

        loggingInfo('delete mode')
        if logicalUnit is not None:
            logger.writeDebug(int(logicalUnit['pathCount']))
            if int(logicalUnit['pathCount']) >= 1:
                raise Exception('Cannot delete LUN: Lun is mapped to a hostgroup!')
            if lunName is not None:
                raise Exception('The name parameter is not supported for delete.')
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
