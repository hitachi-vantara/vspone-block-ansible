#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


__metaclass__ = type


DOCUMENTATION = """
---
module: hv_troubleshooting_facts
short_description: Collects the log bundles for Hitachi ansible modules host and Hitachi gateway service host.
description:
     - This module collects all logs from the different services and all the relevant configuration files
       for further troubleshooting. The logbundle is a zip archive that contains this information.
version_added: '3.0.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.0.0
requirements:
options:
    uai_gateway_address:
        description: IP address or hostname of the UAI gateway. If not provided, UAI gateway logs will not be included in the log bundle.
        type: str
        required: false
    username:
        description: Username for authentication.
        type: str
        required: false
    password:
        description: Password for authentication.
        type: str
        required: false
    api_token:
        description: Token value to access UAI gateway (required for authentication either 'username,password' or api_token).
        type: str
        required: false
"""

EXAMPLES = """
tasks:
    - name: Collect log bundle including UAI gateway logs
        hv_troubleshooting_facts:
            uai_gateway_address: gateway.company.com
            api_token: "api_token_value"
        register: result
        no_log: true
    - debug: var=result

    - name: Collect log bundle for direct only
        hv_troubleshooting_facts:
        register: result
        no_log: true
    - debug: var=result
"""

RETURN = """
filename: 
  description: Path to the generated log bundle.
  returned: success
  type: str
  sample: "$HOME/logs/hitachivantara/ansible/vspone_block/log_bundles/ansible_log_bundle_2024_05_23_13_15_36.zip"
"""

from zipfile import ZipFile
from datetime import datetime
from ansible.module_utils.basic import AnsibleModule
import tempfile
import subprocess
import socket
import shutil
import os
import time
import json
import glob

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_exceptions import (
    HiException,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_infra import (
    StorageSystem,
    HostMode,
    StorageSystemManager,
    Utils,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_ucpmanager import (
    UcpManager,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    get_logger_dir
    )

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "supported_by": "certified",
    "status": ["stableinterface"],
}
try:
    import scp
except ImportError as error:
    pass

try:
    from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_logger import (
        MessageID,
    )

    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_http_client import (
    HTTPClient as requests,
)

logger = Log()
moduleName = "hv_troubleshooting_facts"
gmanagement_address = ""
gmanagement_username = ""
gmanagement_password = ""
gauth_token = ""


def writeLog(*args):
    logger.writeInfo(*args)


def checkTaskStatus(taskId, hitachiAPIGatewayService):
    funcName = "hv_infra:checkTaskStatus"
    logger.writeEnterSDK(funcName)
    logger.writeParam("taskId={}", taskId)
    (status, name) = getTaskStatus(taskId, hitachiAPIGatewayService)
    while status == "Running":
        logger.writeInfo("{0} task with id {1} status is Running".format(name, taskId))
        time.sleep(5)
        (status, name) = getTaskStatus(taskId, hitachiAPIGatewayService)

    if status.lower() == "failed":
        description = getFailedTaskStatusDescription(taskId, hitachiAPIGatewayService)
        logger.writeInfo("{0} task with id {1} is failed.".format(name, taskId))
        raise Exception("Operation failed. {0}".format(description))

    logger.writeExitSDK(funcName)
    return status


def getTaskStatus(taskId, hitachiAPIGatewayService):
    funcName = "hv_infra: getTaskStatus"
    logger.writeEnterSDK(funcName)
    headers = getAuthToken(hitachiAPIGatewayService)
    urlPath = "/v2/tasks/{0}".format(taskId)
    baseUrl = "https://{0}".format(hitachiAPIGatewayService)
    url = "{0}/porcelain/{1}".format(baseUrl, urlPath)
    response = requests.get(url, headers=headers, verify=False)
    status = None
    name = None
    if response.ok:
        status = response.json()["data"].get("status")
        name = response.json()["data"].get("name")
    return (status, name)


def getFailedTaskStatusDescription(taskId, hitachiAPIGatewayService):
    funcName = "hv_infra: getFailedTaskStatusDescription"
    logger.writeEnterSDK(funcName)
    headers = getAuthToken(hitachiAPIGatewayService)
    urlPath = "/v2/tasks/{0}".format(taskId)
    baseUrl = "https://{0}".format(hitachiAPIGatewayService)
    url = "{0}/porcelain/{1}".format(baseUrl, urlPath)
    response = requests.get(url, headers=headers, verify=False)
    description = None
    if response.ok:
        status = response.json()["data"].get("status")
        name = response.json()["data"].get("name")
        events = response.json()["data"].get("events")
        descriptions = [element.get("description") for element in events]
        logger.writeInfo("-".join(descriptions))
        description = events[-1].get("description")
        logger.writeInfo(description)
    return "-".join(descriptions)


def getAuthToken(hitachiAPIGatewayService):
    funcName = "hv_infra:getAuthToken"

    if gauth_token is not None:
        headers = {"Authorization": "Bearer {0}".format(gauth_token)}
        logger.writeDebug("headers={}", headers)
        logger.writeExitSDK(funcName)
        return headers

    body = {"username": gmanagement_username, "password": gmanagement_password}
    urlPath = "v2/auth/login"
    baseUrl = "https://{0}".format(hitachiAPIGatewayService)
    url = "{0}/porcelain/{1}".format(baseUrl, urlPath)

    response = requests.post(url, json=body, verify=False)

    token = None
    if response.ok:
        logger.writeDebug("response.ok")
        authResponse = response.json()
        data = authResponse["data"]
        token = data.get("token")
    elif "HIJSONFAULT" in response.headers:
        logger.writeInfo("HIJSONFAULT response={}", response)
    else:
        logger.writeInfo("Unknown Exception response={}", response)

    headers = {"Authorization": "Bearer {0}".format(token)}
    logger.writeDebug("headers={}", headers)
    logger.writeExitSDK(funcName)

    return headers


def generateLogBundles(hitachiAPIGatewayService):
    # hitachiAPIGatewayService = module.params['hitachiAPIGatewayService']

    writeLog("Enter generateLogBundles")
    writeLog("ip={}", hitachiAPIGatewayService)

    urlPath = "v2/logbundle/"
    baseUrl = "https://{0}".format(hitachiAPIGatewayService)
    url = "{0}/porcelain/{1}".format(baseUrl, urlPath)
    body = {"bundleName": "gateway_service"}
    logger.writeInfo("url={}", url)
    logger.writeInfo("body={}", body)
    response = requests.post(
        url, headers=getAuthToken(hitachiAPIGatewayService), json=body, verify=False
    )
    logger.writeInfo("response={}", response.json())
    if response.ok:
        resourceId = response.json()["data"]["resourceId"]
        logger.writeInfo("resourceId={}", resourceId)
        taskId = response.json()["data"].get("taskId")
        status = checkTaskStatus(taskId, hitachiAPIGatewayService)
        time.sleep(5)
        return status
    else:
        return "Failed"


def downLoadLogBundle(bundleName, hitachiAPIGatewayService, tempdir):
    writeLog("Enter downLoadLogBundle")
    writeLog("ip={}", hitachiAPIGatewayService)

    urlPath = "v2/logbundle/download?fileName={}".format(bundleName)
    baseUrl = "https://{0}".format(hitachiAPIGatewayService)
    url = "{0}/porcelain/{1}".format(baseUrl, urlPath)
    logger.writeInfo("url={}", url)
    hdrs = getAuthToken(hitachiAPIGatewayService)
    hdrs["Content-Range"] = "bytes=0-*"
    hdrs["Content-Type"] = ""
    logger.writeDebug("header: {}", hdrs)
    response = requests.get(url, headers=hdrs, verify=False, bytes=True)
    if response.ok:
        file_path = os.path.join(tempdir, "gateway_service.zip")
        with open(file_path, "wb") as file:
            file.write(response.content)
        logger.writeInfo("Log bundle downloaded successfully: %s", file_path)
    else:
        logger.writeDebug("Failed downloading log bundle")


def getLogBundles(hitachiAPIGatewayService):
    funcName = "hv_infra:getLogBundles"
    logger.writeEnterSDK(funcName)
    urlPath = "v2/logbundle/"
    baseUrl = "https://{0}".format(hitachiAPIGatewayService)
    url = "{0}/porcelain/{1}".format(baseUrl, urlPath)
    headers = getAuthToken(hitachiAPIGatewayService)
    response = requests.get(url, headers=headers, verify=False)
    logger.writeInfo("log_bundles={}", response.json())
    logger.writeExitSDK(funcName)
    if response.ok:
        return response.json()["data"]
    logger.writeExitSDK(funcName)
    if response.ok:
        return response.json()
    else:
        return None

def remove_old_logbundles(zipdir):
    # Define the directory and pattern for the zip files
    pattern = os.path.join(zipdir, 'ansible_log_bundle_*.zip')
    # Get a list of all zip files matching the pattern
    zip_files = glob.glob(pattern)
    # Sort files by creation time (or last modification time if creation time is unavailable)
    zip_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
    # Keep only the latest 3 files
    files_to_delete = zip_files[3:]
    # Delete the older files
    for file_path in files_to_delete:
        os.remove(file_path)
        logger.writeDebug(f"Deleted: {file_path}")
    logger.writeDebug("Cleanup completed. Kept the latest 3 zip files.")

def main(module=None):
    fields = {
        "uai_gateway_address": {"required": False, "type": "str"},
        "api_token": {"required": False, "type": "str"},
        "username": {"required": False, "type": "str"},
        "password": {"required": False, "type": "str", "no_log": True},
    }

    logger.writeEnterModule(moduleName)

    if module is None:
        module = AnsibleModule(argument_spec=fields)

    # params = json.loads(module.params)
    management_address = module.params.get("uai_gateway_address", None)
    management_username = module.params.get("username", None)
    management_password = module.params.get("password", None)
    global gauth_token
    gauth_token = module.params.get("api_token", None)
    logger.writeDebug("management_address={}", management_address)
    logger.writeDebug("management_username={}", management_username)

    uai_flag = True
    comments = ""
    if (
        management_address is None
        or management_address == ""
    ):
        uai_flag = False
        comments = 'LogBundle with direct connection logs'
        writeLog("Collecting logbundle for direct connection logs")
    else:
        uai_flag = True
        comments = 'LogBundle with UAI gateway logs'
        writeLog("Collecting logbundle including UAI gateway logs")

    global gmanagement_address
    global gmanagement_username
    global gmanagement_password
    gmanagement_address = management_address
    gmanagement_username = management_username
    gmanagement_password = management_password

    tempdir = datetime.now().strftime(
        "ansible_log_bundle_%Y_%m_%d_%H_%M_%S"
    )
    zipdir = get_logger_dir()
    zipPath = os.path.join(zipdir, "{0}.zip".format(tempdir))

    try:
        os.makedirs(tempdir)

        if not os.path.exists(zipdir):
            os.makedirs(zipdir)
        for subdir in ("gateway_service", "modules", "playbooks"):
            subpath = os.path.join(tempdir, subdir)
            if not os.path.exists(subpath):
                os.makedirs(subpath)

        writeLog("Copying Ansible playbooks")

        # Log.getHomePath() is /opt/hitachivantara/ansible
        playb_src = Log.getHomePath() + "/playbooks"
        playb_dest = os.path.join(tempdir, "playbooks")

        for dirpath, dirnames, filenames in os.walk(playb_src):
            # Calculate relative path to preserve the directory structure in the destination
            relative_path = os.path.relpath(dirpath, playb_src)
            dest_path = os.path.join(playb_dest, relative_path)
            
            # Make sure each corresponding directory exists in the destination
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)
            
            # Copy each .yml file to the corresponding directory in the destination
            for filename in filenames:
                if filename.endswith('.yml'):
                    src_file = os.path.join(dirpath, filename)
                    dest_file = os.path.join(dest_path, filename)
                    shutil.copy(src_file, dest_file)
                    logger.writeInfo(f"Copied {src_file} to {dest_file}")

        for file in glob.glob(Log.getHomePath() + "/support/*.yml"):
            shutil.copy(file, playb_dest)
        try:
            shutil.copy(os.path.join(Log.getHomePath(), "MANIFEST.json"), tempdir)
        except Exception as e:
            logger.writeInfo(e)
        if uai_flag == True:
            try:
                hitachiAPIGatewayService = gmanagement_address
                status = generateLogBundles(hitachiAPIGatewayService)
                if status == "Success":
                    bundles = getLogBundles(hitachiAPIGatewayService)
                    writeLog(bundles)
                    bundle = bundles["previousLogBundles"][0]
                    bundle_name = bundle["name"]
                    writeLog(bundle)
                    downLoadLogBundle(bundle_name, hitachiAPIGatewayService, tempdir)
                    # line below is only for testing
                    # shutil.copy('/tmp/gateway_service.zip', os.path.join(tempdir, "gateway_service.zip"))
            except Exception as e:
                logger.writeDebug("Error downloading log bundle: {}", e)
                # Do not return failed when the gateway is inaccessible.
                # module.fail_json(msg=str(e))

        writeLog("Copying Ansible log files")
        src = get_logger_dir()
        src_files = os.listdir(src)
        for file_name in src_files:
            full_file_name = os.path.join(src, file_name)
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, os.path.join(tempdir, "modules"))

        filePaths = []
        for root, directories, files in os.walk(tempdir):
            for filename in files:
                filePath = os.path.join(root, filename)
                filePaths.append(filePath)
        with ZipFile(zipPath, "w") as zip_file:
            for file in filePaths:
                zip_file.write(file)

        remove_old_logbundles(zipdir)

        logger.writeExitModule(moduleName)
        module.exit_json(filename=zipPath, comments=comments)
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
        module.fail_json(msg=repr(ex), type=ex.__class__.__name__, log=module._debug)
    finally:
        shutil.rmtree(tempdir, ignore_errors=True)


if __name__ == "__main__":
    main()
