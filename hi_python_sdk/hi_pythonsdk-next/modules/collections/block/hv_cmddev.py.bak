#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2020, Hitachi Vantara, LTD

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'supported_by': 'certified',
                    'status': ['stableinterface']}

DOCUMENTATION = \
    r'''
---
module: hv_cmddev
short_description: This module creates a command device and map it to the vCenter VM mentioned in the storage.json file.
description:
     - The M(hv_cmddev)module is used to map the new command device from the SAN storage systems mentioned in the storage.json file to the VM that hosts Hitachi Storage Modules for Red Hat Ansible (Hitachi Storage Ansible Modules host).This module does not require a command device on the Gateway Service host as a prerequisite.
version_added: '02.9.0'
author:
  - Hitachi Vantara, LTD. VERSION 02.3.0
requirements:
options:
  collections:
    description:
      - Ansible collections name for Hitachi storage modules 
    type: string
    required: yes
    default: hitachi.storage
  var_files:
    description:
      - Path for storage.json file 
    type: string
    required: yes
    default: ../storage.json
  state:
    description:
      - set state to (present) for create command device
    type: string
    default: present
  data:
    required: yes
    description:
      - data has the following properties
      - =================================================================
      - Create command device
      - =================================================================
      - C(vCenterIP:) Mandatory input.String type.vCenter IP address where the VM is available.
      - C(vCenterUser:) Mandatory input. String type. vCenter user name.
      - C(vCenterKey:) Mandatory input. String type.vCenter encrypted password
      - C(vCenterVMName:) Mandatory input. string type.VM name available on the ESXi host.
      - C(sanStorageSystems:) Mandatory input. String type. Storage details on which the command device is to be created.
      - C(hitachiAPIGatewayService:) Mandatory input. String type. IP address of Hitachi Storage Gateway service host.
      - =================================================================

'''
EXAMPLES = \
    r'''
-
  name: create storage command device for each of the storage systems defined in storage.json file.
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  vars_files:
    - ../storage.json
  tasks:
    - hv_cmddev:
        state : 'present'
        sanStorageSystems: '{{ sanStorageSystems }}'
        hitachiAPIGatewayService: '{{ hitachiAPIGatewayService }}'
        vCenterVMName: '{{ vCenterVMName | default(omit) }}'
        vCenterIP: '{{ vCenterIP | default(omit) }}'
        vCenterKey: '{{ vCenterKey | default(omit) }}'
        vCenterCluster: '{{ vCenterCluster | default(omit) }}'
        vCenterUser: '{{ vCenterUser | default(omit) }}'
      register: result
    - debug: var=result

'''
RETURN = \
    r'''
[root@localhost playbooks]# ansible-playbook create_cmd_devs.yml
[WARNING]: provided hosts list is empty, only localhost is available. Note that the implicit localhost does not match 'all'

PLAY [create storage command device for each of the storage systems defined in storage.json file.] ***************************************************************************************

TASK [hv_cmddev] *************************************************************************************************************************************************************************
ok: [localhost]

TASK [debug] *****************************************************************************************************************************************************************************
ok: [localhost] => {
    "result": {
        "changed": false,
        "cmd_output": [
            "Starting command device operation",
            "Getting target server wwn",
            "Getting HostGroup Information",
            "Creating a command device",
            "Creating logical unit 135 in storage pool 1 of storage system 40001.",
            "Created logical Unit 135 in storage system 40001.",
            "Volume 135 is set successfully as command device storage=[40001].",
            "Successfully retrieved volume [135] storage=[40001]",
            "Scanning host group for an available logical unit ID.",
            "Using LUN ID 52 as consistent LUN across Hostgroups.",
            "Presenting logical unit 135 to Host group scPodL-204-vmhba1.",
            "Presented logical unit 135 to Host group scPodL-204-vmhba1.",
            "Presenting logical unit 135 to Host group scPodL-204-vmhba1.",
            "Presented logical unit 135 to Host group scPodL-204-vmhba1.",
            "Command Device successfully created",
            "Provisioning command device via RDM to Gateway VM podl_puma_94.245 in Vsphere",
            "Successfully Rescan host 172.25.94.204.",
            "Successfully Rescan host 172.25.94.204.",
            "Command device for storage 40001 created and mapped to vm podl_puma_94.245 successfully",
            "ProvisionStorageCmdDevForVM create successful"
        ],
        "failed": false
    }
}

PLAY RECAP *******************************************************************************************************************************************************************************
localhost                  : ok=2    changed=0    unreachable=0    failed=0    skipped=0    rescued=0    ignored=0
'''

import json
import subprocess
import re
import time
try:
    import requests
except ImportError, error:
    pass
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystem, \
    StorageSystemManager, HostMode, Utils
from ansible_collections.hitachi.storage.plugins.module_utils.hv_vi_service import ViService
try:
    from ansible_collections.hitachi.storage.plugins.module_utils.hv_logger import MessageID
    HAS_MESSAGE_ID = True
except ImportError, error:
    HAS_MESSAGE_ID = False
from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log, \
    HiException

hostToScanOnPhysical = None
ssh_client = None
logger = Log()
moduleName = 'Create command device'
printPwd = False


def handleHostGroupNew(
    module,
    pumaServer,
    user,
    password,
    storageIp,
    storageId,
    wwns,
    wwn,
    poolId,
    hostGroupName,
    isPhysical,
    ):

    logger.writeInfo('Enter handleHostGroupNew')
    result = False

    # # find the first port from either one of the wwns

    (wwn, portId) = getPortForWWN(
        pumaServer,
        wwns,
        user,
        password,
        storageIp,
        storageId,
        )

    if portId is None:

        # # wwn maybe not be configured with any ports, in the case of pre-provisioning

        logger.writeInfo('wwn is not found in any of the ports on the storage, try the given wwn: {}'
                         , wwn)

#         wwns = module.params.get("hostWWNs",None)
#         if wwns is not None:
#             wwn = wwns[0]

        # #FIXME, do we need to do this for provided wwn?
        # portId=getPortForWWN(pumaServer, wwn, user, password, storageIp, storageId)

        ports = module.params.get('hostPorts', None)
        if ports is not None:
            portId = ports[0]

        if portId is None:
            raise Exception('not enough parameters to create the command device.wwn {0} not found in any of the ports on the storage {1}'.format(wwn,
                            storageIp))

    logger.writeInfo('portId from playbook= {}', portId)

    hostGroupName = module.params.get('hostGroup', None)
    if hostGroupName is None:
        hostGroupName = 'HITACHI_ANSIBLE_HG'

    logger.writeInfo('hostGroupName= {}', hostGroupName)

    (foundHg, hgObjectId) = hostGroupIsCreated(
        pumaServer,
        hostGroupName,
        portId,
        user,
        password,
        storageIp,
        storageId,
        )
    if foundHg:
        logger.writeInfo('found the host group, hostGroupName: {}',
                         hostGroupName)
        logger.writeInfo('hgObjectId= {}', hgObjectId)
        logger.writeInfo('doAddWnnToHostGroup wwn= {}', wwn)
        doAddWnnToHostGroup(
            pumaServer,
            hgObjectId,
            wwn,
            user,
            password,
            storageIp,
            storageId,
            )
    else:

        # # addWWnToHG()
        # raise Exception("remove this debugging stop, hostGroupIsCreated")
        # raise Exception("remove this debugging stop, hostGroupIs NOT Created")
        # # add host group via puma OOB

        command = \
            'curl -v -k -H "X-Subsystem-User: {}"  -H "X-Access-Mode: OOB" '.format(user)
        command += \
            '-H "X-Subsystem-Type: BLOCK" -H "X-Management-IPs: {}" -H "X-Storage-Id: {}" '.format(storageIp,
                storageId)
        command += "-X POST -d '{ "
        command += '"portName" : "{}",'.format(portId)
        command += '"hostGroupName" : "{}"'.format(hostGroupName)
        command += "}' "
        command += \
            'https://{}:8444/v8/storage/host-groups '.format(pumaServer)
        logger.writeDebug('createHostGroup command= {}', command)
        command += ' -H "X-Subsystem-Password: {}" '.format(password)
        if printPwd:
            logger.writeDebug('createHostGroup command= {}', command)

        commandOutStr = subprocess.check_output(command, shell=True)
        commandOutJson = json.loads(commandOutStr)

    targetport = portId
    hostMode = module.params.get('hostMode', None)
    if hostMode is None:
        hostMode = 'VMWAREEXTENSION'

    commandOut = createCommandDevice(
        user,
        password,
        storageIp,
        targetport,
        wwns,
        hostGroupName,
        hostMode,
        poolId,
        wwn,
        False,
        isPhysical,
        )

    # raise Exception("remove this debugging stop")
    # # rescan and  createRDM would not work with new hg
    # # createRDM(module, commandOut)

    return commandOut


def lineBreakAppend(sstr, arr):

    # # given the string, tokenize by line feed and
    # # append each line to arrary

    if isinstance(sstr, list):
        tmpArr = sstr
    else:
        tmpArr = sstr.split('\n')

    # # remove the empty element at the end
#     ilen = len(tmpArr)-1
#     if ilen>=0 and len(tmpArr[ilen])==1:
#         #ss = str(len(tmpArr[ilen]))
#         #tmpArr[ilen] = ss
#         del tmpArr[ilen]

    arr.append(tmpArr)


#     for item in tmpArr:
#         if len(item)>0:
#             arr.append(item)

## wwnSet is for the ESXi server
## user, password, ip is for the storage

def processHostGroup(
    module,
    hg,
    user,
    password,
    ip,
    wwns,
    poolId,
    wwn,
    useWWNs,
    isPhysical,
    ):

    global ssh_client

    hostMode = 'VMWARE_EXTENSION'
    hostGroupName = hg.get('hostGroupName', '')
    portId = hg.get('portId', None)
    if portId is None:
        raise Exception('HostGroup port ID is not found!!')
    hostGroupOptions = hg.get('hostGroupOptions', None)
    if hostGroupOptions is not None:
        hostMode = hostGroupOptions.get('hostMode', 'VMWARE_EXTENSION')

    logger.writeInfo('==============processHostGroup.hostGroupName=  {}'
                     , hostGroupName)
    logger.writeInfo('hostMode=  {}', hostMode)

    targetport = portId
    logger.writeInfo('targetport=  {}', targetport)
    logger.writeInfo('poolId=  {}', poolId)
    logger.writeInfo('ssh_client={}', ssh_client)
    commandOut = createCommandDevice(
        user,
        password,
        ip,
        targetport,
        wwns,
        hostGroupName,
        hostMode,
        poolId,
        wwn,
        False,
        isPhysical,
        )

    if commandOut is None:
        raise Exception('Abort: failed to create command device')

    lun = getLunDecimal(commandOut)
    logger.writeInfo('LUN resulted from createCommandDevice =  {}', lun)

    if isPhysical:
        for host in hostToScanOnPhysical:
            doScanFcPort(ssh_client, host)
        doFindLun(ssh_client, str(lun))
    else:
        doRescan(module)
        createRDM(module, commandOut)

        # logger.writeInfo("commandOut= ", commandOut)

    return commandOut


## wwns is the array from the getHostGroups puma call
## wwnSet is for the ESXi server

def updateResult(hg, wwnSet, result):

    if hg is None:
        logger.writeInfo('updateResult hg is None!!')
        return

    wwns = hg.get('wwns', None)
    if wwns is None:
        logger.writeInfo('updateResult wwns is None!!')
        return

    if wwnSet is None:
        logger.writeInfo('updateResult wwnSet is None!!')
        return

    for wwn in wwns:
        wwnIdHex = wwn['wwnId']
        if wwnIdHex in wwnSet:
            item = result.get(wwnIdHex, None)
            if item is None:
                result[wwnIdHex] = []
            result[wwnIdHex].append(hg)


def doCreateRDMDisk(
    hitachiAPIGatewayService,
    vcip,
    cluster,
    user,
    pword,
    vmName,
    lun,
    ):

            # #FIXME - remove the hardcoding below!!!

    command = \
        'curl -v -k -X POST   -H "Content-Type: application/json" -d \'{ '
    command += '"vcip": "' + vcip + '",'
    command += '"clusterName": "' + cluster + '",'
    command += '"user": "' + user + '",'
    command += '"vmName": "' + vmName + '",'
    command += '"lunIdStr": "' + lun + '" } \'  '
    command += \
        '"https://{}:2023/HitachiStorageManagementWebServices/StorageManager/StorageManager/CreateRDMDisk"'.format(hitachiAPIGatewayService)
    logger.writeDebug('doCreateRDMDisk command= {}', command)

    command = \
        'curl -v -k -X POST   -H "Content-Type: application/json" -d \'{ '
    command += '"vcip": "' + vcip + '",'
    command += '"clusterName": "' + cluster + '",'
    command += '"user": "' + user + '",'
    command += '"pwd": "' + pword + '",'
    command += '"vmName": "' + vmName + '",'
    command += '"lunIdStr": "' + lun + '" } \'  '
    command += \
        '"https://{}:2023/HitachiStorageManagementWebServices/StorageManager/StorageManager/CreateRDMDisk"'.format(hitachiAPIGatewayService)
    if printPwd:
        logger.writeDebug('doCreateRDMDisk command= {}', command)
    commandOutStr = subprocess.check_output(command, shell=True)
    logger.writeInfo('doCreateRDMDisk commandOutStr= {}', commandOutStr)


def doRescan(module):

    hitachiAPIGatewayService = module.params['hitachiAPIGatewayService']
    vcip = module.params['vCenterIP']
    user = module.params['vCenterUser']
    pword = Utils.doGrains(vcip)
    esxiIP = module.params['vCenterVMHostIpAddress']

    StorageSystemManager.reScanHostStorage(hitachiAPIGatewayService,
            vcip, user, pword, esxiIP)
    StorageSystemManager.reScanVMFS(hitachiAPIGatewayService, vcip,
                                    user, pword, esxiIP)

#             command = 'curl -v -k -X POST -d "{}" '
#             command += '"https://{}:2023/HitachiStorageManagementWebServices/StorageManager/StorageManager/ReScanHostStorage?'.format( hitachiAPIGatewayService )
#             command += 'vcip={}&user={}&pwd=xxxxxx&hostIp={}"'.format(
#                 vcip, user, esxiIP )
#             logger.writeDebug("doRescan command= {}", command)
#
#             command = 'curl -v -k -X POST -d "{}" '
#             command += '"https://{}:2023/HitachiStorageManagementWebServices/StorageManager/StorageManager/ReScanHostStorage?'.format( hitachiAPIGatewayService )
#             command += 'vcip={}&user={}&pwd={}&hostIp={}"'.format(
#                 vcip, user, pword, esxiIP )
#             if printPwd:
#                 logger.writeDebug("doRescan command= {}", command)
#             commandOutStr = subprocess.check_output(command, shell=True)
#             logger.writeInfo("doRescan commandOutStr= {}", commandOutStr)

#             command = 'curl -v -k -X POST  -d "{}" '
#             command += '"https://{}:2023/HitachiStorageManagementWebServices/StorageManager/StorageManager/ReScanVMFS?'.format( hitachiAPIGatewayService )
#             command += 'vcip={}&user={}&hostIp={}"'.format(
#                 vcip, user, esxiIP )
#             logger.writeDebug("doRescan command= {}", command)
#
#             command = 'curl -v -k -X POST  -d "{}" '
#             command += '"https://{}:2023/HitachiStorageManagementWebServices/StorageManager/StorageManager/ReScanVMFS?'.format( hitachiAPIGatewayService )
#             command += 'vcip={}&user={}&pwd={}&hostIp={}"'.format(
#                 vcip, user, pword, esxiIP )
#             if printPwd:
#                 logger.writeDebug("doRescan command= {}", command)
#             commandOutStr = subprocess.check_output(command, shell=True)
#             logger.writeInfo("doRescan commandOutStr= {}", commandOutStr)

    logger.writeInfo('sleeping after the scans...')
    time.sleep(10.0)
    logger.writeInfo('wakeup and continue')


def getHostGroupForWWNs(
    pumaServer,
    wwns,
    user,
    pwd,
    storageIp,
    storageId,
    ):

    logger.writeInfo('getHostGroupForWWNs wwns= {}', wwns)
    logger.writeInfo('pumaServer= {}', pumaServer)
    logger.writeInfo('storage username= {}', user)
    logger.writeInfo('storageIp= {}', storageIp)
    logger.writeInfo('storageId= {}', storageId)

    result = {}

            # logger.writeInfo("getHostGroupForWWNs pumaServer= {}", pumaServer)
            # # curl the puma

    command = ' -v -k -H "X-Subsystem-User: {}"  '.format(user)
    command += \
        '-H "X-Subsystem-Type: BLOCK" -H "X-Management-IPs: {}"   -H "X-Access-Mode: OOB"  -H "X-Storage-Id: {}" '.format(storageIp,
            storageId)
    command += \
        'https://{}:8444/v8/storage/host-groups '.format(pumaServer)
    logger.writeDebug('getHostGroups command= {}', command)
    command += ' -H "X-Subsystem-Password: {}" '.format(pwd)
    if printPwd:
        logger.writeDebug('getHostGroups command= {}', command)

    command = 'curl ' + command
    commandOutStr = subprocess.check_output(command, shell=True)
    commandOutJson = json.loads(commandOutStr)

            # logger.writeInfo("getHostGroups commandOutJson= {}", commandOutJson)

            # #FIXME - we are getting a 501 from requests
#             url = "https://{}:8444/v8/storage/host-groups ".format(pumaServer)
#             headers = {
#                 "X-Subsystem-Type": "BLOCK",
#                 "X-Subsystem-IPs": str(storageIp),
#                 "X-Storage-Id": str(storageId),
#                 "X-Access-Mode": "OOB"
#             }
#             logger.writeInfo("url= {}", url)
#             logger.writeInfo("headers= {}", headers)
#             #headers["X-Subsystem-Password"] = pwd
#             response = requests.get(url, params={}, verify=False, headers=headers)
#             if response.ok:
#                 commandOutJson = response.json()
#                 logger.writeInfo("response= {}", commandOutJson)
#                 #return is a string
#                 #commandOutJson = json.loads(commandOut)
#             elif "HIJSONFAULT" in response.headers:
#                 ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
#                 hiex = HiException(ex)
#                 logger.writeHiException(hiex)
#                 raise hiex
#             else:
#                 raise Exception("Unknown error HTTP {}".format(response.status_code))

    if commandOutJson is None:
        return result

    hostGroups = commandOutJson.get('hostGroups', None)
    if hostGroups is None:
        return result

    for hg in hostGroups:

                # logger.writeInfo("getHostGroupForWWNs hostGroupName= {}", hg["hostGroupName"])
                # logger.writeInfo("getHostGroupForWWNs hostGroupName= {}", hg["wwns"])

        updateResult(hg, wwns, result)

    return result


def inWWNs(wwns, wwn):

    # logger.writeInfo("inWWNs? wwn=", wwn)

    result = False

    if wwns is None or wwn is None:
        return False

    for item in wwns:
        wwnId = item.get('wwnId', None)

        # logger.writeInfo("inWWNs wwnId=", wwnId)

        if wwnId is None:
            continue

        s1 = str(wwnId)
        s1 = s1.upper()
        s2 = str(wwn)
        s2 = s2.upper()

        # logger.writeInfo("s1=", s1)
        # logger.writeInfo("s2=", s2)

        if s1 == s2:
            logger.writeInfo('inWWNs objectId= {}', item['objectId'])
            return True

    return result


def doDeleteWwn(
    pumaServer,
    hostGroupObjectId,
    wwnObjectId,
    user,
    password,
    storageIp,
    storageId,
    ):
    command = \
        'curl -k -H "X-Subsystem-User: {}"  -H "Content-Type: application/json"   -H "X-Access-Mode: OOB" '.format(user)
    command += \
        '-H "X-Subsystem-Type: BLOCK" -H "X-Management-IPs: {}" -H "X-Storage-Id: {}" '.format(storageIp,
            storageId)
    command += ' -X DELETE '
    command += 'https://{}'.format(pumaServer) \
        + ':8444/v8/storage/host-groups/{}/wwns/{} '.format(hostGroupObjectId,
            wwnObjectId)
    logger.writeDebug('doDeleteWwn command= {}', command)
    command += ' -H "X-Subsystem-Password: {}" '.format(password)
    if printPwd:
        logger.writeDebug('doDeleteWwn command= {}', command)
    commandOutStr = subprocess.check_output(command, shell=True)
    logger.writeInfo('doDeleteWwn commandOutStr= {}', commandOutStr)
    if commandOutStr is None:
        pass


def doAddWnnToHostGroup(
    pumaServer,
    hostGroupObjectId,
    wwn,
    user,
    password,
    storageIp,
    storageId,
    ):
    command = \
        'curl -k -H "X-Subsystem-User: {}"  -H "Content-Type: application/json"   -H "X-Access-Mode: OOB" '.format(user)
    command += \
        '-H "X-Subsystem-Type: BLOCK" -H "X-Management-IPs: {}" -H "X-Storage-Id: {}" '.format(storageIp,
            storageId)
    command += " -X POST -d ' { "
    command += '"wwnId" : "{}"  '.format(wwn)
    command += "} ' "
    command += 'https://{}'.format(pumaServer) \
        + ':8444/v8/storage/host-groups/{}/wwns '.format(hostGroupObjectId)
    logger.writeDebug('doAddWnnToHostGroup command= {}', command)
    command += ' -H "X-Subsystem-Password: {}" '.format(password)
    if printPwd:
        logger.writeDebug('doAddWnnToHostGroup command= {}', command)
    commandOutStr = subprocess.check_output(command, shell=True)
    logger.writeInfo('doAddWnnToHostGroup commandOutStr= {}',
                     commandOutStr)
    if commandOutStr is None:
        pass


def hostGroupIsCreated(
    pumaServer,
    hostGroupName,
    port,
    user,
    password,
    storageIp,
    storageId,
    ):

    logger.writeInfo('Enter hostGroupIsCreated, hostGroupName, port= {},  {}'
                     , hostGroupName, port)

            # logger.writeInfo("getHostGroupForWWNs pumaServer= {}", pumaServer)

            # # get hgs by port

    command = \
        'curl -k -H "X-Subsystem-User: {}"  -H "Content-Type: application/json"   -H "X-Access-Mode: OOB" '.format(user)
    command += \
        '-H "X-Subsystem-Type: BLOCK" -H "X-Management-IPs: {}" -H "X-Storage-Id: {}" '.format(storageIp,
            storageId)
    command += " -d ' { "
    command += '"port" : "{}"  '.format(port)
    command += "} ' "
    command += 'https://{}'.format(pumaServer) \
        + ':8444/v8/storage/host-groups '
    logger.writeDebug('hostGroupIsCreated, getHostGroups curl command= {}'
                      , command)
    command += ' -H "X-Subsystem-Password: {}" '.format(password)

            # #FIXME
            # # the above results in the extra \' in the command and makes it failed,
            # # so we have the workaround below

    homePath = Log.getHomePath()
    command = 'bash ' + homePath \
        + '/module_utils/hv_getHgByPort.sh {} {} {} password "{}"'.format(storageIp,
            storageId, user, port)
    logger.writeDebug('hostGroupIsCreated bash command= {}', command)
    command = 'bash ' + homePath \
        + '/module_utils/hv_getHgByPort.sh {} {} {} {} "{}"'.format(storageIp,
            storageId, user, password, port)
    commandOutStr = subprocess.check_output(command, shell=True)

    commandOutStr = commandOutStr.replace('\n', '')
    commandOutStr = commandOutStr.replace('\r', '')
    commandOutStr = commandOutStr.replace('\t', '')

            # logger.writeInfo("commandOutStr= {}", commandOutStr)

    commandOutJson = json.loads(commandOutStr)

            # #logger.writeInfo("getHostGroups commandOutJson= {}", commandOutJson)

    if commandOutJson is None:
        return (False, None)

#

    hostGroups = commandOutJson.get('hostGroups', None)
    if hostGroups is None:
        return (False, None)

            # # see if the hostGroupName is created already

    for item in commandOutJson['hostGroups']:

                # logger.writeInfo("hostGroupName= {}", item["hostGroupName"])

        if hostGroupName == item['hostGroupName']:
            logger.writeInfo('hostGroupIsCreated TRUE')

                    # # test the doAddWnnToHostGroup
                    # wwn="10000000C9BA1DEA"
                    # hostGroupObjectId = item["hostGroupObjectId"]
                    # doAddWnnToHostGroup(pumaServer, hostGroupObjectId, wwn, user, password, storageIp, storageId)

            return (True, item['objectId'])

    logger.writeInfo('hostGroupIsCreated FALSE')
    return (False, None)


def getPortForWWN(
    pumaServer,
    wwns,
    user,
    pwd,
    storageIp,
    storageId,
    ):

    logger.writeInfo('getPortForWWN wwns= {}', wwns)

    result = {}

            # logger.writeInfo("getHostGroupForWWNs pumaServer= {}", pumaServer)
            # # curl the puma

    command = \
        'curl -v -k -H "X-Subsystem-User: {}"  -H "X-Access-Mode: OOB"  '.format(user)
    command += \
        '-H "X-Subsystem-Type: BLOCK" -H "X-Management-IPs: {}" -H "X-Storage-Id: {}" '.format(storageIp,
            storageId)
    command += \
        'https://{}:8444/v8/storage/ports/wwns '.format(pumaServer)
    logger.writeDebug('getHostGroups command= {}', command)
    command += ' -H "X-Subsystem-Password: {}" '.format(pwd)

    commandOutStr = subprocess.check_output(command, shell=True)
    commandOutJson = json.loads(commandOutStr)

            # #logger.writeInfo("getHostGroups commandOutJson= {}", commandOutJson)

    if commandOutJson is None:
        return result

    loginWWNsAllPorts = commandOutJson.get('loginWWNsAllPorts', None)

            # large output
            # logger.writeInfo("getPortForWWN loginWWNsAllPorts= {}", loginWWNsAllPorts)

    if loginWWNsAllPorts is None:
        return result

    portFound = None
    theWWN = None

    for wwn in wwns:
        theWWN = wwn
        for port in loginWWNsAllPorts:

            for (portName, wwnsInPort) in port.items():

                        # logger.writeInfo("looking for wwn in port=", portName)

                if inWWNs(wwnsInPort, wwn):
                    portFound = portName
                    logger.writeInfo('found in port, theWWN= {},  {}',
                            portName, theWWN)
                    logger.writeInfo('= {}, {}', portName, theWWN)
                    break

            if portFound is None:
                continue

            logger.writeInfo('break, portFound= {}', portFound)
            break
    return (theWWN, portFound)


## user, password, ip of the storage

def createCommandDevice(
    user,
    password,
    ip,
    targetport,
    wwns,
    hostgroup,
    hostmode,
    poolId,
    wwn,
    useWWNs,
    isPhysical,
    ):

    global ssh_client

            # puma_adm --createcmddev --user t5k --ip 10.69.69.69 --targetport CL4-A \
            # --wwns "10000000c9ef1f42 10000000c9ef1f43"
            # ( --pool 26 or --paritygroup 1-1 ) \
            # --hostgroup bsawa --cmddevname deleteme --instnum 69 \
            # --password mypass --hostmode Standard

            # hostmode needs to remove underscores because puma_adm accepts VMWAREEXTENSION, not VMWARE_EXTENSION like our other inputs.

    hostmode = hostmode.replace('_', '')

    wwnsStr = wwn
    if useWWNs:
        wwnsStr = ''
        sep = ''
        for wwn in wwns:
            wwnsStr = wwnsStr + sep + str(wwn)
            sep = ' '

            # logger.writeInfo("createCommandDevice, wwnsStr=", wwnsStr)

            # # create the command dev via puma_adm

    if poolId is None:
        pumaCommand = \
            'puma_adm --createcmddev --user {} --password xxx --ip {} --targetport "{}" --wwns "{}" --hostgroup {} --hostmode {}'.format(
            user,
            ip,
            targetport,
            wwnsStr,
            hostgroup,
            hostmode,
            )
        logger.writeInfo('createCommandDevice, pumaCommand= {}',
                         pumaCommand)
        pumaCommand = \
            'puma_adm --createcmddev --user {} --password {}  --ip {} --targetport "{}" --wwns "{}" --hostgroup {} --hostmode {}'.format(
            user,
            password,
            ip,
            targetport,
            wwnsStr,
            hostgroup,
            hostmode,
            )
    else:
        pumaCommand = \
            'puma_adm --createcmddev --user {} --password xxx --ip {} --targetport "{}" --wwns "{}" --hostgroup {} --hostmode {} --pool {} '.format(
            user,
            ip,
            targetport,
            wwnsStr,
            hostgroup,
            hostmode,
            poolId,
            )
        logger.writeInfo('createCommandDevice, pumaCommand= {}',
                         pumaCommand)
        pumaCommand = \
            'puma_adm --createcmddev --user {} --password {} --ip {} --targetport "{}" --wwns "{}" --hostgroup {} --hostmode {} --pool {} '.format(
            user,
            password,
            ip,
            targetport,
            wwnsStr,
            hostgroup,
            hostmode,
            poolId,
            )

              # # only feed both wwns if they are playbook inputs and wwn was not found on the esx host
#             pumaCommand = "puma_adm --createcmddev --user {} --password {} --ip {} --targetport \"{}\" --wwns \"100000109B588F34 100000109B588F35\" --hostgroup {} --hostmode {}".format(
#                 user, password, ip, targetport, hostgroup, hostmode
#             )

    if isPhysical:
        commandOut = doCommand(ssh_client, pumaCommand)
    else:
        commandOut = subprocess.check_output(pumaCommand, shell=True)

 #         doScanFcPort(ssh_client, "host1")
#         ssh_client.close()
#         raise Exception("Remove this debug stop 02/14")

    return commandOut


def exec_command(client, command):

    writeLog('execute_command={}', command)

    try:
        (_, ss_stdout, ss_stderr) = client.exec_command(command)
        (r_out, r_err) = (ss_stdout.readlines(), ss_stderr.read())
        writeLog('r_err={}', r_err)
        if len(r_err) > 5:
            logger.writeInfo(r_err)
            raise Exception('Failed to exec remote command: ' + r_err)
        else:
            logger.writeInfo(r_out)
            return (r_out, None)
    except IOError:

#             client.close()

        logger.writeInfo('.. host ' + address + ' is not up')
        return ('host not up', 'host not up')


def writeLog(*args):
    logger.writeInfo(*args)


def doScanFcPort(ssh, fchost):

    cmd = " echo '- - -' > /sys/class/scsi_host/" + fchost \
        + '/scan; echo $? '
    writeLog('doScanFcPort cmd={}', cmd)

    (rout, rerr) = exec_command(ssh, cmd)
    if rerr is not None or str(rout[0]) != '0\n':
        writeLog('Failed to ScanFcPort, err={}', rerr)
        return False

    writeLog('ScanFcPort output={}', rout)
    return True


def doFindLun(ssh, lun):

    lunHex = '{:04x}'.format(int(lun))

    cmd = 'ls /dev/disk/by-id/ | grep -i ' + lunHex
    writeLog('doFindLun cmd={}', cmd)

    (rout, rerr) = exec_command(ssh, cmd)
    if rerr is not None:
        writeLog('Failed to find LUN, err={}', rerr)
        return ''

    writeLog('rout={}', rout)
    return rout


def doCommand(ssh, command):
    (rout, rerr) = exec_command(ssh, command)
    if rerr is not None:
        msg = 'Failed to exec command: ' + str(rerr)
        raise Exception(msg)

    return rout


def doGetFcHostPortNameWWN(ssh, host):
    (rout, rerr) = exec_command(ssh, 'cat /sys/class/fc_host/' + host
                                + '/port_name')
    if rerr is not None:
        writeLog('Failed to getFcHostWWN, err={}', rerr)
        return ''

    return rout


def doGetFcHost(ssh):

    rlist = []

    (rout, rerr) = exec_command(ssh, '/usr/bin/ls /sys/class/fc_host')
    if rerr is not None:
        writeLog('Failed to getFcHost, err={}', rerr)
        return rlist

#         ss = rout.split(" ")

    if isinstance(rout, list) and len(rout) > 0:
        rlist = rout

#             for s1 in rlist:
#                 writeLog("s1=[{}]",s1)

    return rlist


## return all WWNs on the physical server

def getWWNsPhysical(ssh):
    wwns = []

    global hostToScanOnPhysical
    hostToScanOnPhysical = []

#     wwns.append("20000025B5A0004F")
#     wwns.append("20000025B5A000AF")

    # # get the two hosts from the physical server
    # # get wwn for each host
    # # sng
    # # have to create a map so we know which host to scan
    # # or could we just scan both hosts?
    # # and if the lun is found on either one of the host?

    hosts = doGetFcHost(ssh)
    for host in hosts:
        writeLog('host=[{}]', host)
        host = str(host).strip()
        hostToScanOnPhysical.append(host)
        wwns1 = doGetFcHostPortNameWWN(ssh, host)
        for wwn in wwns1:
            writeLog('wwn=[{}]', wwn)
            wwn = str(wwn).strip().upper()
            wwn = wwn.replace('0X', '')
            wwns.append(wwn)

    for wwn in wwns:
        writeLog('wwn=[{}]', wwn)

    return wwns


def getWWNsEsx(
    hitachiAPIGatewayService,
    vcip,
    user,
    pword,
    esxiIP,
    ):

            # # curl the VI service directly at port 2030
            # # here we assume the C# service and the VI service are always installed at the same host
#             command = "curl -X GET \"http://{}:2030/getHostWWN?vcip={}&user={}&pwd={}&hostIp={}\" ".format(
#                 hitachiAPIGatewayService, vcip, user, pword, esxiIP
#             )

#             command = "curl -k -X GET \"https://{}:2031/getHostWWN?vcip={}&user={}&pwd={}&hostIp={}\" ".format(
#                 hitachiAPIGatewayService, vcip, user, pword, esxiIP
#             )
#             logger.writeInfo("getEsxWWNs command= {}", command)

#             command = "curl -k -X GET \"https://{}:2023/HitachiStorageManagementWebServices/StorageManager/StorageManager/HostWWN?vcip={}&user={}&pwd={}&hostIp={}\" ".format(
#                 hitachiAPIGatewayService, vcip, user, pword, esxiIP
#             )

#             commandOutStr = subprocess.check_output(command, shell=True)
#             commandOutJson = json.loads(commandOutStr)
#             logger.writeInfo("getEsxWWNs commandOutJson= {}", commandOutJson)
#             wwns = commandOutJson.get("wwn", None)

#             url = "https://{0}:2023/HitachiStorageManagementWebServices/StorageManager/StorageManager/HostWWN".format(hitachiAPIGatewayService)
#             body = {
#                 "vcip": vcip,
#                 "user": user,
#                 "hostIp": esxiIP
#             }
#             logger.writeInfo("getEsxWWNs url= {}", url)
#             logger.writeInfo("getEsxWWNs body= {}", body)
#             body["pwd"] = pword
#
#             response = requests.get(url, params=body, verify=False)
#             if response.ok:
#                 commandOutJson = response.json()
#                 logger.writeInfo("getEsxWWNs response= {}", commandOutJson)
#                 #return is a string
#                 #commandOutJson = json.loads(commandOut)
#             elif "HIJSONFAULT" in response.headers:
#                 ex=Exception(json.loads(response.headers["HIJSONFAULT"]))
#                 hiex = HiException(ex)
#                 logger.writeHiException(hiex)
#                 raise hiex
#             else:
#                 raise Exception("Unknown error HTTP {}".format(response.status_code))

    commandOutJson = \
        StorageSystemManager.getHostWWNs(hitachiAPIGatewayService,
            vcip, user, pword, esxiIP)
    logger.writeInfo('getEsxWWNs response= {}', commandOutJson)
    if commandOutJson is None:
        raise Exception('Failed to get Host WWNs')

            # # let's return the list of wwns in hex

    wwns = commandOutJson.get('wwns', None)

    if wwns is None:
        raise Exception('Failed to get ESX WWNs')

    result = []
    for wwn in wwns:
        result.append(wwn['wwnHexString'])

    logger.writeInfo('getEsxWWNs result, wwns= {}', result)
    return result


def getLunDecimal(commandOut):

    if isinstance(commandOut, list):
        tmpArr = commandOut
    else:
        tmpArr = commandOut.split('\n')

    for item in tmpArr:

        # # view each line of the commandOut here
        # # logger.writeInfo(item)

        if 'LUN (decimal)' in item:
            lunMatch = re.findall("\d+", item)[0]
            return lunMatch

    return None


def createRDM(module, commandOut):

    logger.writeInfo('Enter createRDM')

            # logger.writeInfo("commandOut=", commandOut)

    if module.params['vCenterIP']:

                # this is not working
                # lunMatch = re.search("LUN (decimal): (\\d+)", commandOut)

        lunMatch = getLunDecimal(commandOut)
        logger.writeInfo('lunMatch= {}', lunMatch)
        if lunMatch:

                    # lun = lunMatch.group(1)

            lun = lunMatch
            logger.writeInfo('Created LUN {}', lun)
            vi = ViService(module.params['hitachiAPIGatewayService'],
                           2021)
            vcip = module.params['vCenterIP']
            user = module.params['vCenterUser']
            pword = Utils.doGrains(vcip)
            cluster = module.params['vCenterCluster']
            vmName = module.params['vCenterVMName']
            logger.writeInfo('vcip= {}', vcip)
            logger.writeInfo('user= {}', user)

                    # logger.writeInfo("pword=", pword)

            logger.writeInfo('cluster= {}', cluster)
            logger.writeInfo('vmName= {}', vmName)

                    # vi.createRDM(vcip, cluster, user, pword, vmName, lun)

            doCreateRDMDisk(
                module.params['hitachiAPIGatewayService'],
                vcip,
                cluster,
                user,
                pword,
                vmName,
                lun,
                )


def newSSHClient(host, user, password):
    from paramiko import AutoAddPolicy, SSHClient
    from scp import SCPClient
    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(host, username=user, password=password)
    return ssh


def main(module=None):

    # # these are optional params:
    # # "hostPorts" list, "hostMode", and "hostGroup"(host group name)

    fields = {  # "hostModeOptions": {"required": True, "type": "list"},
                # "poolId": {"required": False, "type": "int"},
        'vCenterIP': {'required': True, 'type': 'str'},
        'vCenterUser': {'required': True, 'type': 'str'},
        'vCenterKey': {'required': True, 'type': 'str'},
        'vCenterVMName': {'required': True, 'type': 'str'},
        'hitachiAPIGatewayService': {'required': True, 'type': 'str'},
        'state': {'default': 'present', 'choices': ['present', 'absent'
                  ], 'type': 'str'},
        'sanStorageSystems': {'required': True, 'type': 'list'},
        }

    logger.writeEnterModule(moduleName)
    if module is None:
        module = AnsibleModule(argument_spec=fields)

    try:

        # # TODO
        # # first get it to work with the playbook inputs, then
        # # then remove the params from the input by steps

        # # get wwns for the ESXi hosting this ansible vm

        vcip = module.params['vCenterIP']
        vUser = module.params['vCenterUser']
        pword = Utils.doGrains(vcip)
        vmName = module.params['vCenterVMName']
       
        # poolId = module.params["poolId"]

        hitachiAPIGatewayService = \
            module.params['hitachiAPIGatewayService']
       
        logger.writeParam('vCenterIP={}', vcip)
        logger.writeParam('vCenterUser={}', vUser)
        logger.writeParam('vmName={}', vmName)
        logger.writeParam('hitachiAPIGatewayService={}',
                          hitachiAPIGatewayService)

        storageArraySerialList = []
        storageCommandOutputs = []

        for systemInfo in module.params['sanStorageSystems']:

            logger.writeInfo('==========================  Processing storage system:  {} '
                             , systemInfo['serialNumber'])

            user = systemInfo['username']
            password = Utils.doGrains(systemInfo['svpIP'])
            svpip = systemInfo.get('controllerIP', systemInfo['svpIP'])
            gatewayServer = systemInfo.get('hitachiPeerService',
                                           hitachiAPIGatewayService)

            poolId = systemInfo.get('poolId', None)
            logger.writeInfo('poolId= {}', poolId)
            if poolId is None:
                raise Exception('Abort: poolId is required!')
            
            storageSerial = systemInfo['serialNumber']
            storageSystem = StorageSystem(storageSerial, hitachiAPIGatewayService)
            system =  storageSystem.addStorageSystemToISP(svpip, gatewayServer, 8444, user, password)
            (ucp_name, ucp_serial) = storageSystem.createUcpSystem(gatewayServer)
            vCenter = storageSystem.addvCenter(vcip, vUser, pword, ucp_name)
            descriptions = storageSystem.createCommandDevice(poolId, vcip, vUser, pword, vmName, ucp_serial)
            
            # formatted_json = json.dumps(json.loads(res), indent=4)
            # colorful_json = highlight(unicode(formatted_json, 'UTF-8'), lexers.JsonLexer(), formatters.TerminalFormatter())

            # json_object = json.loads(res)
            # json_formatted_str = json.dumps(res.data, sort_keys=True, indent=4)
            # jsonStr = json.dumps(descriptions, indent=4)
        logger.writeExit(moduleName)
        module.exit_json(cmd_output=descriptions)
    except HiException as ex:
        if HAS_MESSAGE_ID:
            logger.writeAMException(MessageID.ERR_CreateCommandDevice)
        else:
            logger.writeAMException("0x0000") 
        module.fail_json(msg=ex.format())
    except Exception as ex:
        module.fail_json(msg=str(ex))


if __name__ == '__main__':
    main()
