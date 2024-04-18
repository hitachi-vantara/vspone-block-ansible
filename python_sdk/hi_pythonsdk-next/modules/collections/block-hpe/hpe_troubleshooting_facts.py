#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, [ Hewlett Packard Enterprise Development LP ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type


DOCUMENTATION = \
    r'''
---
module: hpe_troubleshooting_facts
short_description: This module provides Log collecting script for HPE Ansible Module host and HPE Gateway Service host.
description:
     - This log collecting script collects all logs from the different services and all the relevant configuration files\
       for further troubleshooting.The output of the script is an .tar.gz archive that contains this information.
version_added: '02.9.0'
author:
  - Hewlett Packard Enterprise Development LP. VERSION 02.3.0.7

requirements:
options:
    collections:
     description:
      - Ansible collections name for HPE XP storage modules 
     type: string
     required: yes
     default: hpe.xp_storage
    data:
     description:
      - data has the following properties
      - =================================================================
      - Collect Logs
      - =================================================================
      - C(storage.json:) Mandatory input.json file type.JSON file that contains connection information of the physical storage systems
        and the storage gateway service.
      - =================================================================

'''
EXAMPLES = \
    r'''
-
  name: Collecting HPE Storage Management Server Support Log Bundle
  hosts: localhost
  collections:
    - hpe.xp_storage
  gather_facts: false
  vars_files:
    - /opt/hpe/ansible/storage.json
  tasks:
    - hpe_troubleshooting_facts:
        sanStorageSystems: '{{ sanStorageSystems }}'
        hpeAPIGatewayService: '{{ hpeAPIGatewayService }}'
      register: result
    - debug: var=result
'''
RETURN = r'''
'''

from zipfile import ZipFile
from datetime import datetime
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_log import Log, \
    HiException
from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_infra import StorageSystem, \
    HostMode, StorageSystemManager, Utils
from ansible.module_utils.basic import AnsibleModule
import tempfile
import subprocess
import socket
import shutil
import os
import json
import glob
import requests
import time
ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'supported_by': 'certified',
                    'status': ['stableinterface']}
try:
    import scp
except ImportError as error:
    pass

try:
    from ansible_collections.hpe.xp_storage.plugins.module_utils.hv_logger import MessageID
    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False


logger = Log()
moduleName = 'hv_troubleshooting_facts'


def writeLog(*args):
    logger.writeInfo(*args)

def checkTaskStatus(taskId, hpeAPIGatewayService):
    funcName = 'hv_infra:checkTaskStatus'
    logger.writeEnterSDK(funcName)
    logger.writeParam('taskId={}', taskId)
    (status, name) = getTaskStatus(taskId, hpeAPIGatewayService)
    while status == 'Running':
        logger.writeInfo('{0} task with id {1} status is Running'.format(name,
                                                                                taskId))
        time.sleep(5)
        (status, name) = getTaskStatus(taskId, hpeAPIGatewayService)

    if status.lower() == 'failed':
        description = getFailedTaskStatusDescription(taskId, hpeAPIGatewayService)
        logger.writeInfo('{0} task with id {1} is failed.'.format(name, taskId))
        raise Exception('Operation failed. {0}'.format(description))

    logger.writeExitSDK(funcName)
    return status

def getTaskStatus(taskId, hpeAPIGatewayService ):
    funcName = 'hv_infra: getTaskStatus'
    logger.writeEnterSDK(funcName)
    headers = getAuthToken(hpeAPIGatewayService)
    urlPath = '/v2/tasks/{0}'.format(taskId)
    baseUrl = 'https://{0}'.format(hpeAPIGatewayService)
    url = '{0}/porcelain/{1}'.format(baseUrl, urlPath)
    response = requests.get(url, headers=headers, verify=False)
    status = None
    name = None
    if response.ok:
        status = response.json()['data'].get('status')
        name = response.json()['data'].get('name')
    return (status, name)
        
def getFailedTaskStatusDescription( taskId, hpeAPIGatewayService):
    funcName = 'hv_infra: getFailedTaskStatusDescription'
    logger.writeEnterSDK(funcName)
    headers = getAuthToken(hpeAPIGatewayService)
    urlPath = '/v2/tasks/{0}'.format(taskId)
    baseUrl = 'https://{0}'.format(hpeAPIGatewayService)
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

def getAuthToken(hpeAPIGatewayService):
    funcName = 'hv_infra:getAuthToken'
    body = {'username': 'ucpadmin', 'password': 'ucpadmin'}
    urlPath = 'v2/auth/login'
    baseUrl = 'https://{0}'.format(hpeAPIGatewayService)
    url = '{0}/porcelain/{1}'.format(baseUrl, urlPath)
    
    response = requests.post(url, json=body,
                                verify=False)

    logger.writeExitSDK(funcName)
    token = None
    if response.ok:
        authResponse = response.json()
        data = authResponse['data']
        token = data.get('token')
    elif 'HIJSONFAULT' in response.headers:
        logger.writeInfo('HIJSONFAULT response={}', response)
    else:
        logger.writeInfo('Unknown Exception response={}',
                                response)

    headers = {'Authorization': 'Bearer {0}'.format(token)}

    return headers

def generateLogBundles(hpeAPIGatewayService):
    # hpeAPIGatewayService = module.params['hpeAPIGatewayService']

    writeLog('Enter generateLogBundles')
    writeLog('ip={}', hpeAPIGatewayService)

    urlPath = 'v2/logbundle/'
    baseUrl = 'https://{0}'.format(hpeAPIGatewayService)
    url = '{0}/porcelain/{1}'.format(baseUrl, urlPath)
    body = {
            "bundleName": "gateway_service"
           }
    logger.writeInfo('url={}', url)
    logger.writeInfo('body={}', body)
    response = requests.post(url, headers=getAuthToken(hpeAPIGatewayService), json=body, verify=False)
    logger.writeInfo('response={}', response.json())
    if response.ok:
        resourceId = response.json()['data']['resourceId']
        logger.writeInfo('resourceId={}', resourceId)
        taskId = response.json()['data'].get('taskId')
        status = checkTaskStatus(taskId, hpeAPIGatewayService)
        time.sleep(5)
        return status
    else: 
        return "Failed"  

def downLoadLogBundle( bundleName, hpeAPIGatewayService, tempdir):
    writeLog('Enter downLoadLogBundle')
    writeLog('ip={}', hpeAPIGatewayService)

    urlPath = 'v2/logbundle/download?fileName={}'.format(bundleName)
    baseUrl = 'https://{0}'.format(hpeAPIGatewayService)
    url = '{0}/porcelain/{1}'.format(baseUrl, urlPath)
    logger.writeInfo('url={}', url)
    hdrs=getAuthToken(hpeAPIGatewayService)
    hdrs['Content-Range'] = 'bytes=0-*'       
    response = requests.get(url, headers=hdrs, verify=False)
    with open(os.path.join(tempdir, 'gateway_service.zip'), 'wb') as file:
        file.write(response.content)       

def getLogBundles(hpeAPIGatewayService):
    funcName = 'hv_infra:getLogBundles'
    logger.writeEnterSDK(funcName)
    urlPath = 'v2/logbundle/'
    baseUrl = 'https://{0}'.format(hpeAPIGatewayService)
    url = '{0}/porcelain/{1}'.format(baseUrl, urlPath)
    headers = getAuthToken(hpeAPIGatewayService)
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
        'hpeAPIGatewayService': {'required': True, 'type': 'str'},
        'sanStorageSystems': {'required': True, 'type': 'list'},
    }

    logger.writeEnterModule(moduleName)

    if module is None:
        module = AnsibleModule(argument_spec=fields)

    tempdir = \
        datetime.now().strftime('hpe_ansible_02.3.0.7_support_artifacts_%Y_%m_%d_%H_%M_%S'
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

        # hpePeerServices = getGatewayServers(module)
        # processGatewayServers(hpePeerServices, tempdir)

        writeLog('Copying Ansible playbooks')
        storageJson = os.getenv('HV_STORAGE_ANSIBLE_PROFILE',
                                './storage.json')
        shutil.copy(storageJson, os.path.join(tempdir, 'playbooks'))

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
        src = "/var/log/hpe/ansible/"
        src_files = os.listdir(src)
        for file_name in src_files:
            full_file_name = os.path.join(src, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name,  os.path.join(tempdir,'modules')) 
        # shutil.copy('/var/log/hpe/ansible/hpe_storage_modules.log',
        #             os.path.join(tempdir,
        #                          'modules/hpe_storage_modules.log'))
        shutil.copy('/var/log' + '/ansible.log',
                    os.path.join(tempdir, 'ansible_service'))
        
        hpeAPIGatewayService = module.params['hpeAPIGatewayService']    
        status= generateLogBundles(hpeAPIGatewayService)
        if status == "Success":
            bundles = getLogBundles(hpeAPIGatewayService)
            writeLog(bundles)
            bundle = bundles['previousLogBundles'][0]
            bundle_name = bundle['name']
            writeLog(bundle)
            downLoadLogBundle(bundle_name, hpeAPIGatewayService, tempdir)

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
