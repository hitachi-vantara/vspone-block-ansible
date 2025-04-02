#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_troubleshooting_facts
short_description: Collects the log bundles for Hitachi ansible modules host and Hitachi gateway service host.
description:
    - This module collects all logs from the different services and all the relevant configuration files
       for further troubleshooting. The log bundle is a zip archive that contains this information.
    - This module is supported for both C(direct) and C(gateway) connection types.
    - For C(direct) connection type examples, go to URL
      U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/tools/logbundle_direct_connection.yml)
    - For C(gateway) connection type examples, go to URL
      U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/tools/logbundle_gateway_connection.yml)
version_added: '3.0.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.8
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: full
options:
    uai_gateway_address:
        description: IP address or hostname of the UAI gateway. If not provided, UAI gateway logs will not be included in the log bundle.
        type: str
        required: false
    api_token:
        description: Token value to access UAI gateway.
        type: str
        required: false
    remote_gateway_host_connection_info:
        description: Information required to establish a connection to the remote gateway host.
        type: list
        required: false
        elements: dict
        suboptions:
            address:
                description: IP address or hostname of the remote gateway host.
                type: str
                required: true
            username:
                description: Username for authentication for the remote gateway host.
                type: str
                required: true
            password:
                description: Password for authentication for the remote gateway host.
                type: str
                required: true
"""

EXAMPLES = """
- name: Collect LogBundle including Local and Remote UAI gateway logs
  hitachivantara.vspone_block.vsp.hv_troubleshooting_facts:
    uai_gateway_address: "172.25.99.99"
    api_token: apitokenvalue
    remote_gateway_host_connection_info:
      - address: remotegateway1.company.com
        username: admin
        password: login-password

- name: Collect log bundle for direct only
  hitachivantara.vspone_block.vsp.hv_troubleshooting_facts:
  # no_log: true
"""

RETURN = """
ansible_facts:
    description: The facts collected by the module.
    returned: always
    type: dict
    sample: {
        "filename": "$HOME/logs/hitachivantara/ansible/vspone_block/log_bundles/ansible_log_bundle_2024_05_23_13_15_36.zip",
        "msg": "LogBundle with UAI gateway logs"
    }
"""

import json
from zipfile import ZipFile
from datetime import datetime
from ansible.module_utils.basic import AnsibleModule
import pathlib

# nosec - This is a trusted command that is used to get the ansible version from the system
import subprocess  # nosec
import shutil
import os
import time
import glob
import platform

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_exceptions import (
    HiException,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_ucpmanager import (
    UcpManager,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    get_logger_dir,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.uaig_utils import (
    UAIGResourceID,
)

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "supported_by": "certified",
    "status": ["stableinterface"],
}

try:
    from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_logger import (
        MessageID,
    )

    HAS_MESSAGE_ID = True
except ImportError:
    HAS_MESSAGE_ID = False

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_http_client import (
    HTTPClient as requests,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common_constants import (
    NAMESPACE,
    PROJECT_NAME,
    TELEMETRY_FILE_NAME,
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
        response.json()["data"].get("status")
        response.json()["data"].get("name")
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
        # uca-2607 don't writeout the token
        # logger.writeDebug("headers={}", headers)
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
    # uca-2607 don't writeout the token
    # logger.writeDebug("headers={}", headers)
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


def updateRemoteGatewayLoginSSH(
    hitachiAPIGatewayService,
    remote_gateway_address,
    remote_gateway_username,
    remote_gateway_password,
    ucpManager,
):
    writeLog("Enter updateRemoteGatewayLoginSSH")
    writeLog("ip={}", hitachiAPIGatewayService)

    # get the Ucp
    conv_system_name, conv_system_serial, conv_mgmt_address = (
        UAIGResourceID.getSystemSerial(hitachiAPIGatewayService, remote_gateway_address)
    )
    logger.writeDebug("name={}", conv_system_name)
    logger.writeDebug("serial={}", conv_system_serial)
    logger.writeDebug("gateway={}", conv_mgmt_address)

    theUCP = ucpManager.getUcpSystem(conv_system_name)
    logger.writeDebug("resourceId={}", theUCP["resourceId"])

    # v2/systems/ucp-9fe3b3a7b3234212e55871f268231a14/gateway
    urlPath = "v2/systems/{}/gateway".format(theUCP["resourceId"])
    baseUrl = "https://{0}".format(hitachiAPIGatewayService)
    url = "{0}/porcelain/{1}".format(baseUrl, urlPath)
    body = {
        "username": remote_gateway_username,
        "password": remote_gateway_password,
    }
    logger.writeInfo("url={}", url)
    # logger.writeInfo("body={}", body)
    response = requests.patch(
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
        file_path = os.path.join(tempdir, "gateway_service.zip")  # nosec
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
    pattern = os.path.join(zipdir, "ansible_log_bundle_*.zip")  # nosec
    # Get a list of all zip files matching the pattern
    zip_files = glob.glob(pattern)
    # Sort files by creation time (or last modification time if creation time is unavailable)
    zip_files.sort(key=os.path.getmtime, reverse=True)
    # Keep only the latest 3 files
    files_to_delete = zip_files[3:]
    # Delete the older files
    for file_path in files_to_delete:
        os.remove(file_path)
        logger.writeDebug(f"Deleted: {file_path}")
    logger.writeDebug("Cleanup completed. Kept the latest 3 zip files.")


def get_linux_distro_info():
    try:
        with open("/etc/os-release") as f:
            os_info = f.read()
        # Extract distribution name and version from /etc/os-release
        distro_name = None
        distro_version = None
        for line in os_info.splitlines():
            if line.startswith("NAME="):
                distro_name = line.split("=")[1].strip('"')
            elif line.startswith("VERSION="):
                distro_version = line.split("=")[1].strip('"')
        return distro_name, distro_version
    except Exception as ex:
        logger.writeError("File /etc/os-release is not available.")
        logger.writeError(str(ex))
        raise


def get_os_version(os_edition):
    # Get OS version based on the platform
    if os_edition == "Linux":
        # Get detailed Linux distribution info
        distro_name, distro_version = get_linux_distro_info()
        if distro_name and distro_version:
            os_version = f"{distro_name} {distro_version}"
        else:
            # Fallback to kernel version if the distribution info is unavailable
            os_version = platform.release()
    elif os_edition == "Darwin":
        os_version = platform.mac_ver()[0]  # macOS version
    elif os_edition == "Windows":
        os_version = platform.version()  # Windows version
    else:
        os_version = platform.release()  # Fallback for other systems
    return os_version


def get_os_info():
    # Get OS edition
    os_edition = platform.system()

    # Get OS version
    try:
        os_version = get_os_version(os_edition)
    except Exception as e:
        logger.writeError(f"Error getting OS version: {e}")
        os_version = "Unknown OS version"

    # Get Ansible version (if installed)
    ansible_version = ""
    try:
        # Check if Ansible is installed
        ansible_full_path = shutil.which("ansible")

        # Check if the Ansible executable is valid
        if not ansible_full_path:
            raise FileNotFoundError("Ansible executable not found.")

        # Check if the Ansible executable is valid and accessible
        # nosec - This is a trusted command that is used to get the ansible version from the system
        if not os.path.isfile(ansible_full_path) or not os.access(
            ansible_full_path, os.X_OK
        ):
            raise FileNotFoundError(f"'{ansible_full_path}' is not a valid executable.")

        # Get the Ansible version
        # nosec - This is a trusted command that is used to get the ansible version from the system
        ansible_version = subprocess.check_output(
            [ansible_full_path, "--version"], text=True
        )
    except FileNotFoundError:
        ansible_version = "Ansible not installed"
    except subprocess.SubprocessError as e:
        ansible_version = f"Error retrieving Ansible version: {e}"
    except Exception as e:
        ansible_version = f"Unexpected error: {e}"
    # Get Python version
    python_version = platform.python_version()
    return os_edition, os_version, ansible_version, python_version


def write_os_info_to_file(filename):
    # Get system information
    os_edition, os_version, ansible_version, python_version = get_os_info()

    # Print the results
    writeLog(f"OS Edition: {os_edition}")
    writeLog(f"OS Version: {os_version}")
    writeLog(f"Ansible Version: {ansible_version}")
    writeLog(f"Python Version: {python_version}")

    # Write the system information to file
    with open(filename, "w") as file:
        file.write(f"OS Edition: {os_edition}\n")
        file.write(f"OS Version: {os_version}\n")
        file.write(f"Ansible Version: {ansible_version}\n")
        file.write(f"Python Version: {python_version}\n")

    # Print a success message
    writeLog("System information has been written to os_info.txt")


def main(module=None):
    fields = {
        "uai_gateway_address": {"required": False, "type": "str"},
        "api_token": {"required": False, "type": "str", "no_log": True},
        # "username": {"required": False, "type": "str"},
        # "password": {"required": False, "type": "str", "no_log": True},
        "remote_gateway_host_connection_info": {
            "required": False,
            "type": "list",
            "elements": "dict",
            "options": {
                "address": {
                    "required": True,
                    "type": "str",
                },
                "username": {
                    "required": True,
                    "type": "str",
                },
                "password": {"required": True, "type": "str", "no_log": True},
            },
        },
    }

    if module is None:
        module = AnsibleModule(argument_spec=fields, supports_check_mode=True)

    logger.writeEnterModule(moduleName)

    # params = json.loads(module.params)
    remote_gateway_infos = module.params.get(
        "remote_gateway_host_connection_info", None
    )
    management_address = module.params.get("uai_gateway_address", None)
    management_username = module.params.get("username", None)
    management_password = module.params.get("password", None)
    global gauth_token
    gauth_token = module.params.get("api_token", None)
    logger.writeDebug("management_address={}", management_address)
    logger.writeDebug("management_username={}", management_username)

    uai_flag = True
    comments = ""
    if management_address is None or management_address == "":
        uai_flag = False
        comments = "LogBundle with direct connection logs"
        writeLog("Collecting logbundle for direct connection logs")
    else:
        uai_flag = True
        comments = "LogBundle with UAI gateway logs"
        writeLog("Collecting logbundle including UAI gateway logs")

    global gmanagement_address
    global gmanagement_username
    global gmanagement_password
    gmanagement_address = management_address
    gmanagement_username = management_username
    gmanagement_password = management_password

    if uai_flag is True:
        #  updateRemoteGatewayLoginSSH
        if remote_gateway_infos is not None:
            for remote_gateway_info in remote_gateway_infos:
                logger.writeDebug("remote_gateway_info={}", remote_gateway_info)
                logger.writeDebug("address={}", remote_gateway_info["address"])
                # logger.writeDebug("username={}", remote_gateway_info['username'])
                # logger.writeDebug("password={}", remote_gateway_info['password'])
                remote_gateway_address = remote_gateway_info["address"]
                remote_gateway_username = remote_gateway_info["username"]
                remote_gateway_password = remote_gateway_info["password"]
                ucpManager = UcpManager(
                    management_address,
                    management_username,
                    management_password,
                    gauth_token,
                )
                try:
                    updateRemoteGatewayLoginSSH(
                        gmanagement_address,
                        remote_gateway_address,
                        remote_gateway_username,
                        remote_gateway_password,
                        ucpManager,
                    )
                except Exception as e:
                    logger.writeDebug("Error updateRemoteGatewayLoginSSH: {}", e)
                    # module.fail_json(msg=str(e))

    tempdir = datetime.now().strftime("ansible_log_bundle_%Y_%m_%d_%H_%M_%S")
    zipdir = get_logger_dir() + "/log_bundles"
    zipPath = os.path.join(zipdir, "{0}.zip".format(tempdir))  # nosec
    usages_dir = pathlib.Path.home() / f"ansible/{NAMESPACE}/{PROJECT_NAME}/usages"
    temp_usages_dir = os.path.join(tempdir, "usages")  # nosec

    consent_dir = (
        pathlib.Path.home() / f"ansible/{NAMESPACE}/{PROJECT_NAME}/user_consent"
    )
    try:
        os.makedirs(tempdir)

        if not os.path.exists(zipdir):
            os.makedirs(zipdir)
        for subdir in ("gateway_service", "modules", "playbooks"):
            subpath = os.path.join(tempdir, subdir)  # nosec
            if not os.path.exists(subpath):
                os.makedirs(subpath)

        write_os_info_to_file(os.path.join(tempdir, "os_info.txt"))  # nosec

        writeLog("Copying Ansible playbooks")

        # Log.getHomePath() is /opt/hitachivantara/ansible
        playb_src = Log.getHomePath() + "/playbooks"
        playb_dest = os.path.join(tempdir, "playbooks")  # nosec

        for dirpath, dirnames, filenames in os.walk(playb_src):
            # Calculate relative path to preserve the directory structure in the destination
            relative_path = os.path.relpath(dirpath, playb_src)
            dest_path = os.path.join(playb_dest, relative_path)  # nosec

            # Make sure each corresponding directory exists in the destination
            if not os.path.exists(dest_path):
                os.makedirs(dest_path)

            # Copy each .yml file to the corresponding directory in the destination
            for filename in filenames:
                if filename.endswith(".yml"):
                    src_file = os.path.join(dirpath, filename)  # nosec
                    dest_file = os.path.join(dest_path, filename)  # nosec
                    shutil.copy(src_file, dest_file)
                    logger.writeInfo(f"Copied {src_file} to {dest_file}")

        # copy registration files

        # handle the usage file content
        try:
            if os.path.exists(usages_dir):
                shutil.copytree(usages_dir, temp_usages_dir)
                if management_address is not None:
                    with open(
                        os.path.join(temp_usages_dir, TELEMETRY_FILE_NAME),
                        "r+",  # nosec
                    ) as file:
                        file_data = json.load(file)
                        new_data = {
                            "gatewayStorageSystems": file_data.get(
                                "gatewayStorageSystems"
                            ),
                            "gatewayTasks": file_data.get("gatewayTasks"),
                        }
                        file.seek(0)
                        json.dump(new_data, file, indent=4)
                        file.truncate()

                else:
                    with open(
                        os.path.join(temp_usages_dir, TELEMETRY_FILE_NAME),
                        "r+",  # nosec
                    ) as file:
                        file_data = json.load(file)
                        new_data = {
                            "directConnectTasks": file_data.get("directConnectTasks"),
                            "sdsBlockTasks": file_data.get("sdsBlockTasks"),
                            "directConnectStorageSystems": file_data.get(
                                "directConnectStorageSystems"
                            ),
                            "sdsBlockStorageSystems": file_data.get(
                                "sdsBlockStorageSystems"
                            ),
                        }
                        file.seek(0)
                        json.dump(new_data, file, indent=4)
                        file.truncate()
                logger.writeInfo(f"Copied usages files to {temp_usages_dir}")
                # comment out the registration files

            if os.path.exists(consent_dir):
                shutil.copytree(
                    consent_dir, os.path.join(tempdir, "user_consent")
                )  # nosec
                logger.writeInfo(f"Copied user_consent files to {tempdir}/user_consent")
        except Exception as e:
            logger.writeInfo(e)

        for file in glob.glob(Log.getHomePath() + "/support/*.yml"):
            shutil.copy(file, playb_dest)
        try:
            shutil.copy(
                os.path.join(Log.getHomePath(), "MANIFEST.json"), tempdir
            )  # nosec
        except Exception as e:
            logger.writeInfo(e)
        if uai_flag is True:
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
            full_file_name = os.path.join(src, file_name)  # nosec
            if os.path.isfile(full_file_name):
                shutil.copy(full_file_name, os.path.join(tempdir, "modules"))  # nosec

        filePaths = []
        for root, directories, files in os.walk(tempdir):
            for filename in files:
                filePath = os.path.join(root, filename)  # nosec
                filePaths.append(filePath)
        with ZipFile(zipPath, "w") as zip_file:
            for file in filePaths:
                zip_file.write(file)

        remove_old_logbundles(zipdir)

        logger.writeExitModule(moduleName)
        module.exit_json(
            changed=False, ansible_facts={"filename": zipPath, "msg": comments}
        )
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
