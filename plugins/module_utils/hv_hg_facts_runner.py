#!/usr/bin/python
# -*- coding: utf-8 -*-

__metaclass__ = type

import json
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystem, \
    HostMode, StorageSystemManager, Utils

from ansible_collections.hitachi.storage.plugins.module_utils.hv_storagemanager import StorageManager
from ansible_collections.hitachi.storage.plugins.module_utils.hv_ucpmanager import UcpManager
from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log, \
    HiException

logger = Log()
moduleName = 'Host Group facts'


def writeNameValue(name, value):
    logger.writeDebug(name, value)


def runPlaybook(module):

    logger.writeEnterModule(moduleName)

    ucp_advisor_info = json.loads(module.params['ucp_advisor_info'])
    ucpadvisor_address = ucp_advisor_info.get('address', None)
    ucpadvisor_ansible_vault_user = ucp_advisor_info.get('username', None)
    ucpadvisor_ansible_vault_secret = ucp_advisor_info.get('password', None)

    storage_system_info = json.loads(module.params['storage_system_info'])
    storage_serial = storage_system_info.get('serial', None)
    ucp_serial = storage_system_info.get('ucp_name', None)

    logger.writeDebug('20230606 storage_serial={}',storage_serial)

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

    data = json.loads(module.params['spec'])
    options = data.get('query', [])

    hostGroups = []
    ports = data.get('ports')
    name = data.get('name')
    if name == '':
        name = None

    lun = data.get('lun')
    if lun is not None and ':' in str(lun):
        lun = Utils.getlunFromHex(lun)
        logger.writeDebug('Hex converted lun={0}'.format(lun))
    if lun == '':
        lun = None

    logger.writeDebug('data={0}'.format(data))
    logger.writeDebug('Ports={0}'.format(ports))
    logger.writeDebug('name={0}'.format(name))
    logger.writeDebug('lun={0}'.format(lun))

    hostGroups = storageSystem.getAllHostGroups()
    
    if ports:
        ## apply port filter
        portSet = set(ports)
        hostGroups = [group for group in hostGroups if group['port'] in portSet]

    if name is not None:
        ## apply name filter
        logger.writeParam('name={}', data['name'])
        # hostGroups = [group for group in hostGroups if group['hostGroupName'] == name]
        logger.writeDebug(hostGroups)
        hostGroups = [x for x in hostGroups if x['hostGroupName'] == name]
        logger.writeDebug(hostGroups)

    if lun is not None:
        ## apply lun filter
        logger.writeParam('apply filter, lun={}', data['lun'])
        hostGroupsNew = []
        for hg in hostGroups:
            lunPaths = hg.get('lunPaths', None)
            if lunPaths:
                # logger.writeDebug('Paths={}', hg['lunPaths'])
                for lunPath in lunPaths:
                    if 'ldevId' in lunPath:
                        # logger.writeDebug('lunPath[ldevId]={}', lunPath['ldevId'])
                        if lun == str(lunPath['ldevId']) :
                            ## found the lun in the lunPaths, return the whole lunPaths,
                            ## if you only want to return the matching lun instead of the whole list,
                            ## then you need to add more code here
                            logger.writeDebug('found lun in lunPaths={}', hg['lunPaths'])
                            hostGroupsNew.append(hg)
                            break
        hostGroups = hostGroupsNew
        # hostGroups = storageSystem.getHostGroupsForLU(data['lun'])
        # if ports:
        #     portSet = set(ports)
        #     hostGroups = [group for group in hostGroups if group['Port'
        #                                                          ] in portSet]
        # else:
        #     hostGroups = storageSystem.getAllHostGroups()
        #     if ports:
        #         portSet = set(ports)
        #         hostGroups = [group for group in hostGroups if group['port'
        #                                                              ] in portSet]

    ## prepare output, apply filters
    for hg in hostGroups:

        if hg.get('hostModeOptions', None) is None:
            hg['hostModeOptions'] = []

        del hg['resourceId']

        # if not options or 'luns' in options:
        #     paths = hg.get('lunPaths', None)
        #     if paths:
        #         writeNameValue('Paths={}', hg['lunPaths'])
        #         for path in paths:
        #             if 'lupathHostID' in path:
        #                 path['hostGroupLunId'] = path['lupathHostID']
        #                 del path['lupathHostID']
        #             if 'lupathID' in path:

        #                 #                             path["lunId"] = path["lupathID"]

        #                 path['ldevId'] = path['lupathID']
        #                 del path['lupathID']
        #             if 'hexLupathID' in path:

        #                 # path["lunId"] = path["lupathID"]

        #                 path['hexLdevId'] = path['hexLupathID']
        #                 del path['hexLupathID']
        #     else:
        #         hg['Paths'] = []
        # else:
        #     del hg['Paths']

        if options:
            if 'wwns' not in options:
                del hg['wwns']
            if 'luns' not in options and lun is None:
                del hg['lunPaths']

            # if hg.get("hostModeOptions", None):

        # writeNameValue('hostModeOptions={}', hg['hostModeOptions'])
        # del hg['hostModeOptions']

        if hg.get('ResourceGroupId') == -1:
            hg['ResourceGroupId'] = ''

    logger.writeExitModule(moduleName)
    module.exit_json(hostGroups=hostGroups)
