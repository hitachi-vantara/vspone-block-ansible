#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


__metaclass__ = type


DOCUMENTATION = \
    r'''
---
module: hv_troubleshooting_facts
short_description: This module provides Log collecting script for Hitachi Ansible Modules host and Hitachi Gateway Service host.
description:
     - This log collecting script collects all logs from the different services and all the relevant configuration files
       for further troubleshooting. The output of the script is an .tar.gz archive that contains this information.
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
    ucp_advisor_info:
        required: yes
        description:
        - ucp_advisor_info has the following properties
        - =================================================================
        - UCP Advisor information
        - =================================================================
        - C(ucpadvisor_address:) Mandatory input. String type. UCPA address.
        - C(ucpadvisor_ansible_vault_user:) Mandatory input. String type. UCPA user name.
        - C(ucpadvisor_ansible_vault_secret:) Mandatory input. String type. UCPA password in clear text.
        - =================================================================
        default: n/a

'''
EXAMPLES = \
    r'''
-
  name: Collecting Hitachi Storage Management Server Support Log Bundle
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: ../ansible_vault_var/ansible.vault.vars.ucpa.yml
  tasks:
    - hv_troubleshooting_facts:
          
        ucp_advisor_info:
          address: "{{ucpadvisor_address}}"
          username: "{{ucpadvisor_ansible_vault_user}}"
          password: "{{ucpadvisor_ansible_vault_secret}}"

      register: result
    - debug: var=result
'''
RETURN = r'''
'''

from zipfile import ZipFile
from datetime import datetime
from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log, \
    HiException
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystem, \
    HostMode, StorageSystemManager, Utils
from ansible_collections.hitachi.storage.plugins.module_utils.hv_ucpmanager import UcpManager
from ansible.module_utils.basic import AnsibleModule
import tempfile
import subprocess
import requests
import socket
import shutil
import os
import time
import json
import glob
ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'supported_by': 'certified',
                    'status': ['stableinterface']}
try:
    import scp
except ImportError as error:
    pass

try:
    from ansible_collections.hitachi.storage.plugins.module_utils.hv_logger import MessageID
    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False


logger = Log()
moduleName = 'hv_troubleshooting_facts'
gucpadvisor_address = ''
gucpadvisor_ansible_vault_user = ''
gucpadvisor_ansible_vault_secret = ''

def writeLog(*args):
    logger.writeInfo(*args)

def checkTaskStatus(taskId, hitachiAPIGatewayService):
    funcName = 'hv_infra:checkTaskStatus'
    logger.writeEnterSDK(funcName)
    logger.writeParam('taskId={}', taskId)
    (status, name) = getTaskStatus(taskId, hitachiAPIGatewayService)
    while status == 'Running':
        logger.writeInfo('{0} task with id {1} status is Running'.format(name,
                                                                                taskId))
        time.sleep(5)
        (status, name) = getTaskStatus(taskId, hitachiAPIGatewayService)

    if status.lower() == 'failed':
        description = getFailedTaskStatusDescription(taskId, hitachiAPIGatewayService)
        logger.writeInfo('{0} task with id {1} is failed.'.format(name, taskId))
        raise Exception('Operation failed. {0}'.format(description))

    logger.writeExitSDK(funcName)
    return status

def getTaskStatus(taskId, hitachiAPIGatewayService ):
    funcName = 'hv_infra: getTaskStatus'
    logger.writeEnterSDK(funcName)
    headers = getAuthToken(hitachiAPIGatewayService)
    urlPath = '/v2/tasks/{0}'.format(taskId)
    baseUrl = 'https://{0}'.format(hitachiAPIGatewayService)
    url = '{0}/porcelain/{1}'.format(baseUrl, urlPath)
    response = requests.get(url, headers=headers, verify=False)
    status = None
    name = None
    if response.ok:
        status = response.json()['data'].get('status')
        name = response.json()['data'].get('name')
    return (status, name)
        
def getFailedTaskStatusDescription( taskId, hitachiAPIGatewayService):
    funcName = 'hv_infra: getFailedTaskStatusDescription'
    logger.writeEnterSDK(funcName)
    headers = getAuthToken(hitachiAPIGatewayService)
    urlPath = '/v2/tasks/{0}'.format(taskId)
    baseUrl = 'https://{0}'.format(hitachiAPIGatewayService)
    url = '{0}/porcelain/{1}'.format(baseUrl, urlPath)
    response = requests.get(url, headers=headers, verify=False)
    description = None
    if response.ok:
        status = response.json()['data'].get('status')
        name = response.json()['data'].get('name')
        events = response.json()['data'].get('events')
        descriptions = [element.get('description') for element in events]
        logger.writeInfo('-'.join(descriptions))
        description = events[-1].get('description')
        logger.writeInfo(description)
    return ('-'.join(descriptions))      

def getAuthToken(hitachiAPIGatewayService):
    funcName = 'hv_infra:getAuthToken'
    body = {'username': gucpadvisor_ansible_vault_user, 'password': gucpadvisor_ansible_vault_secret}
    urlPath = 'v2/auth/login'
    baseUrl = 'https://{0}'.format(hitachiAPIGatewayService)
    url = '{0}/porcelain/{1}'.format(baseUrl, urlPath)
    
    response = requests.post(url, json=body,
                                verify=False)

    token = None
    if response.ok:
        logger.writeDebug('response.ok')
        authResponse = response.json()
        data = authResponse['data']
        token = data.get('token')
    elif 'HIJSONFAULT' in response.headers:
        logger.writeInfo('HIJSONFAULT response={}', response)
    else:
        logger.writeInfo('Unknown Exception response={}',
                                response)

    headers = {'Authorization': 'Bearer {0}'.format(token)}
    logger.writeDebug('headers={}',headers)
    logger.writeExitSDK(funcName)

    return headers

def generateLogBundles(hitachiAPIGatewayService):
    # hitachiAPIGatewayService = module.params['hitachiAPIGatewayService']

    writeLog('Enter generateLogBundles')
    writeLog('ip={}', hitachiAPIGatewayService)

    urlPath = 'v2/logbundle/'
    baseUrl = 'https://{0}'.format(hitachiAPIGatewayService)
    url = '{0}/porcelain/{1}'.format(baseUrl, urlPath)
    body = {
            "bundleName": "gateway_service"
           }
    logger.writeInfo('url={}', url)
    logger.writeInfo('body={}', body)
    response = requests.post(url, headers=getAuthToken(hitachiAPIGatewayService), json=body, verify=False)
    logger.writeInfo('response={}', response.json())
    if response.ok:
        resourceId = response.json()['data']['resourceId']
        logger.writeInfo('resourceId={}', resourceId)
        taskId = response.json()['data'].get('taskId')
        status = checkTaskStatus(taskId, hitachiAPIGatewayService)
        time.sleep(5)
        return status
    else: 
        return "Failed"  

def downLoadLogBundle( bundleName, hitachiAPIGatewayService, tempdir):
    writeLog('Enter downLoadLogBundle')
    writeLog('ip={}', hitachiAPIGatewayService)

    urlPath = 'v2/logbundle/download?fileName={}'.format(bundleName)
    baseUrl = 'https://{0}'.format(hitachiAPIGatewayService)
    url = '{0}/porcelain/{1}'.format(baseUrl, urlPath)
    logger.writeInfo('url={}', url)
    hdrs=getAuthToken(hitachiAPIGatewayService)
    hdrs['Content-Range'] = 'bytes=0-*'       
    response = requests.get(url, headers=hdrs, verify=False)
    with open(os.path.join(tempdir, 'gateway_service.zip'), 'wb') as file:
        file.write(response.content)       

def getLogBundles(hitachiAPIGatewayService):
    funcName = 'hv_infra:getLogBundles'
    logger.writeEnterSDK(funcName)
    urlPath = 'v2/logbundle/'
    baseUrl = 'https://{0}'.format(hitachiAPIGatewayService)
    url = '{0}/porcelain/{1}'.format(baseUrl, urlPath)
    headers = getAuthToken(hitachiAPIGatewayService)
    response = requests.get(url, headers=headers,
                            verify=False)
    logger.writeInfo('log_bundles={}', response.json())
    logger.writeExitSDK(funcName)
    if response.ok:
        return response.json()['data']
    logger.writeExitSDK(funcName)
    if response.ok:
        return response.json()
    else:
        return None   

def main(module=None):
    fields = {
        'hitachiAPIGatewayService': {'required': False, 'type': 'str'},
        'sanStorageSystems': {'required': False, 'type': 'list'},
        'ucp_advisor_info': {'required': True, 'type': 'json'},
    }

    logger.writeEnterModule(moduleName)

    if module is None:
        module = AnsibleModule(argument_spec=fields)

        
    ucp_advisor_info = json.loads(module.params['ucp_advisor_info'])
    ucpadvisor_address = ucp_advisor_info.get('address', None)
    ucpadvisor_ansible_vault_user = ucp_advisor_info.get('username', None)
    ucpadvisor_ansible_vault_secret = ucp_advisor_info.get('password', None)
    logger.writeDebug('ucpadvisor_address={}', ucpadvisor_address)
    logger.writeDebug('ucpadvisor_ansible_vault_user={}', ucpadvisor_ansible_vault_user)

    if ucpadvisor_ansible_vault_user is None or \
        ucpadvisor_ansible_vault_secret is None or \
        ucpadvisor_address is None or \
        ucpadvisor_ansible_vault_user == '' or \
        ucpadvisor_ansible_vault_secret == '' or \
        ucpadvisor_address == '' :
        raise Exception("UCPA is not configured.")
    
    global gucpadvisor_address
    global gucpadvisor_ansible_vault_user
    global gucpadvisor_ansible_vault_secret
    gucpadvisor_address = ucpadvisor_address
    gucpadvisor_ansible_vault_user = ucpadvisor_ansible_vault_user
    gucpadvisor_ansible_vault_secret = ucpadvisor_ansible_vault_secret

    tempdir = \
        datetime.now().strftime('hitachi_ansible_02.3.0_support_artifacts_%Y_%m_%d_%H_%M_%S'
                                )
    zipdir = Log.getHomePath() + '/support'
    zipPath = os.path.join(zipdir, '{0}.zip'.format(tempdir))

    try:
        # localhostName = socket.gethostname()
        # localIp = socket.gethostbyname(localhostName)

        os.makedirs(tempdir)

        if not os.path.exists(zipdir):
            os.makedirs(zipdir)
        for subdir in ('gateway_service', 'ansible_service', 'modules', 'playbooks'):
            subpath = os.path.join(tempdir, subdir)
            if not os.path.exists(subpath):
                os.makedirs(subpath)

        # hitachiPeerServices = getGatewayServers(module)
        # processGatewayServers(hitachiPeerServices, tempdir)

        writeLog('Copying Ansible playbooks')

        # storageJson = os.getenv('HV_STORAGE_ANSIBLE_PROFILE',
        #                         './storage.json')
        # shutil.copy(storageJson, os.path.join(tempdir, 'playbooks'))

        # shutil.copy(Log.getHomePath()+"/bin/.storage.new.json", os.path.join(tempdir, "playbooks"))

        # shutil.copy(Log.getHomePath() + '/storage-connectors.json',
        #             os.path.join(tempdir, 'playbooks'))
        for file in glob.glob(Log.getHomePath() + '/support/*.yml'):
            shutil.copy(file, os.path.join(tempdir, 'playbooks'))
        for file in glob.glob(Log.getHomePath()
                              + '/playbooks/*.yml'):
            shutil.copy(file, os.path.join(tempdir, 'playbooks'))
        for file in glob.glob(Log.getHomePath()
                              + '/playbooks/file/*.yml'):
            shutil.copy(file, os.path.join(tempdir, 'playbooks'))

       
        writeLog('Copying Ansible log files')
        src = "/var/log/hitachi/ansible/"
        src_files = os.listdir(src)
        for file_name in src_files:
            full_file_name = os.path.join(src, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name,  os.path.join(tempdir,'modules')) 
        # shutil.copy('/var/log/hitachi/ansible/hv_storage_modules.log',
        #             os.path.join(tempdir,
        #                          'modules/hv_storage_modules.log'))
        shutil.copy('/var/log' + '/ansible.log',
                    os.path.join(tempdir, 'ansible_service'))
        
        hitachiAPIGatewayService = gucpadvisor_address
        status= generateLogBundles(hitachiAPIGatewayService)
        if status == "Success":
            bundles = getLogBundles(hitachiAPIGatewayService)
            writeLog(bundles)
            bundle = bundles['previousLogBundles'][0]
            bundle_name = bundle['name']
            writeLog(bundle)
            downLoadLogBundle(bundle_name, hitachiAPIGatewayService, tempdir)

        filePaths = []
        for (root, directories, files) in os.walk(tempdir):
            for filename in files:
                filePath = os.path.join(root, filename)
                filePaths.append(filePath)
        with ZipFile(zipPath, 'w') as zip_file:
            for file in filePaths:
                zip_file.write(file)

        logger.writeExitModule(moduleName)
        module.exit_json(filename=zipPath)
    except EnvironmentError as ex:
        if HAS_MESSAGE_ID:
            logger.writeError(MessageID.ERR_GET_SUPPORT_LOGS)
        logger.writeError(str(ex))
        module.fail_json(msg=ex.strerror)
    except HiException as ex:
        if HAS_MESSAGE_ID:
            logger.writeAMException(MessageID.ERR_GET_SUPPORT_LOGS)
        module.fail_json(msg=ex.format())
    except Exception as ex:
        if HAS_MESSAGE_ID:
            logger.writeError(MessageID.ERR_GET_SUPPORT_LOGS)
        logger.writeError(str(ex))
        module.fail_json(msg=repr(ex), type=ex.__class__.__name__,
                         log=module._debug)
    finally:
        shutil.rmtree(tempdir, ignore_errors=True)


if __name__ == '__main__':
    main()
