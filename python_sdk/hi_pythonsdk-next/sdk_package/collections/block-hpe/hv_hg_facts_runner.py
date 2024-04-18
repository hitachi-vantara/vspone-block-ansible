#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_infra import StorageSystem, \
    HostMode, StorageSystemManager, Utils

from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_log import Log, \
    HiException

logger = Log()
moduleName = 'Host Group facts'


def writeNameValue(name, value):
    logger.writeDebug(name, value)


def runPlaybook(module):

    logger.writeEnterModule(moduleName)

    storageSystem = StorageSystem(module.params['storage_serial'])
    data = json.loads(module.params['data'])
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
        portSet = set(ports)
        hostGroups = [group for group in hostGroups if group['port'] in portSet]

    if name is not None:
        logger.writeParam('name={}', data['name'])
        # hostGroups = [group for group in hostGroups if group['hostGroupName'] == name]
        logger.writeDebug(hostGroups)
        hostGroups = [x for x in hostGroups if x['hostGroupName'] == name]
        logger.writeDebug(hostGroups)
    if lun is not None:
        logger.writeParam('lun={}', data['lun'])
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

            # if hg.get("hostModeOptions", None):

        # writeNameValue('hostModeOptions={}', hg['hostModeOptions'])
        # del hg['hostModeOptions']

        if hg.get('ResourceGroupId') == -1:
            hg['ResourceGroupId'] = ''

    logger.writeExitModule(moduleName)
    module.exit_json(hostGroups=hostGroups)
