#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


__metaclass__ = type

DOCUMENTATION = """
---
module: hv_storagesystem
short_description: This module manages Hitachi storage system.
description:
     - This module manages Hitachi storage system.

version_added: '3.0.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.0.0
options:
  state:
    description: The desired state of the storage system.
    type: str
    required: false
    choices: ['present', 'absent']
    default: 'present'
  storage_system_info:
    description:
      - Information about the Hitachi storage system.
    type: dict
    required: true
    suboptions:
      serial:
        description: Serial number of the Hitachi storage system.
        type: str
        required: true
      address:
        description: IP address or hostname of the storage system.
        type: str
        required: true
      username:
        description: Username for authentication.
        type: str
        required: true
      password:
        description: Password for authentication.
        type: str
        required: true
  connection_info:
    description: Information required to establish a connection to the storage system.
    type: dict
    required: true
    suboptions:
      address:
        description: IP address or hostname of either the UAI gateway (if connection_type is gateway) or the storage system (if connection_type is direct).
        type: str
        required: true
      username:
        description: Username for authentication.
        type: str
        required: false
      password:
        description: Password for authentication.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['gateway', 'direct']
        default: 'direct'
      subscriber_id:
        description: Subscriber ID for multi-tenancy (required for "gateway" connection type).
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway (required for authentication either 'username,password' or api_token).
        type: str
        required: false
"""

EXAMPLES = """
- name: Adding Storage System
  tasks:
    - hv_storagesystem:
        storage_system_info:
          serial: "ABC123"
          address: storage1.company.com
          username: "username"
          password: "password"
        connection_info:
          address: gateway.company.com
          api_token: "api token value"
          connection_type: "gateway"
          subscriber_id: "sub123"
        state: present
      register: result
    - debug: var=result

-
  name: Deleting Storage System
  tasks:
    - hv_storagesystem:
        storage_system_info:
          serial: "ABC123"
        connection_info:
          address: gateway.company.com
          api_token: "api token value"
          connection_type: "gateway"
          subscriber_id: "sub123"
        state: absent
      register: result
    - debug: var=result
"""

RETURN = """
storageSystems:
  description: The storage system information.
  returned: always
  type: dict
  sample: {
    "controllerAddress": "192.168.0.126",
    "deviceLimits": {
      "externalGroupNumberRange": {
        "isValid": true,
        "maxValue": 16384,
        "minValue": 1
      },
      "externalGroupSubNumberRange": {
        "isValid": true,
        "maxValue": 4096,
        "minValue": 1
      },
      "parityGroupNumberRange": {
        "isValid": true,
        "maxValue": 1,
        "minValue": 1
      },
      "parityGroupSubNumberRange": {
        "isValid": true,
        "maxValue": 32,
        "minValue": 1
      }
    },
    "freeCapacity": "15.88 TB",
    "freeCapacityInMb": 16655844,
    "freePoolCapacity": "10.79 TB",
    "freePoolCapacityInMb": 11314548,
    "managementAddress": "192.168.0.126",
    "microcodeVersion": "93-07-23-80/01",
    "model": "VSP E1090H",
    "operationalStatus": "Normal",
    "serialNumber": "715036",
    "syslogConfig": {
      "detailed": true,
      "syslogServers": [
        {
          "id": 0,
          "syslogServerAddress": "192.168.0.143",
          "syslogServerPort": "514"
        },
        {
          "id": 1,
          "syslogServerAddress": "192.168.0.188",
          "syslogServerPort": "514"
        }
      ]
    },
    "totalCapacity": "27.62 TB",
    "totalCapacityInMb": 28958726,
    "totalPoolCapacity": "10.90 TB",
    "totalPoolCapacityInMb": 11424504
  }
"""

import json
import os
import re

try:
    from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_messages import (
        MessageID,
    )

    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_exceptions import (
    HiException,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_infra import (
    StorageSystem,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_infra import (
    StorageSystemManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_ucpmanager import (
    UcpManager,
)
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    CommonConstants,
)

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "supported_by": "certified",
    "status": ["stableinterface"],
}

logger = Log()
moduleName = "Storage System"


def getStorageJson(storageProfile):
    logger.writeDebug("storageProfile={}", storageProfile)

    if storageProfile is None:
        storageProfile = "./storage.json"
    else:

        # expect the input from playbook a list

        storageProfile = storageProfile[0]

    logger.writeParam("storageProfile={}", storageProfile)

    if not os.path.exists(storageProfile):
        raise Exception(
            "The storage profile {0} does not exist.".format(storageProfile)
        )

    # setenv for password decrypt

    storageProfile = os.path.abspath(storageProfile)
    os.environ["HV_STORAGE_ANSIBLE_PROFILE"] = storageProfile
    logger.writeDebug("abs storageProfile={}", storageProfile)
    logger.writeDebug("env storageProfile={}", os.getenv("HV_STORAGE_ANSIBLE_PROFILE"))

    with open(storageProfile) as connectionFile:
        connections = json.load(connectionFile)

    return connections


def main(module=None):
    fields = {
        "state": {"default": "present", "choices": ["present", "absent"]},
        "storage_system_info": {"required": True, "type": "json"},
        "connection_info": {"required": True, "type": "json"},
    }

    if module is None:
        module = AnsibleModule(argument_spec=fields)

    try:

        logger.writeEnterModule(moduleName)

        storage_system_info = module.params.get("storage_system_info", None)
        if storage_system_info is None:
            raise Exception(
                "Invalid storage_system_info, please correct it and try again."
            )

        storage_system_info = json.loads(storage_system_info)
        if storage_system_info is None:
            raise Exception(
                "Invalid storage_system_info, please correct it and try again."
            )

        ###########################################################
        # valid UCP

        ucp_serial = CommonConstants.UCP_NAME
        logger.writeDebug("ucp_name={}", ucp_serial)

        if ucp_serial is None:
            raise Exception("The parameter ucp_name is required.")

        # x = re.search("^(UCP-CI|UCP-HC|UCP-RS|Logical-UCP)-\d{5,10}$", ucp_serial)
        # if not x:
        #     raise Exception('The UCP serial number is invalid.')

        connection_info = module.params.get("connection_info", None)
        if connection_info is None:
            raise Exception("Invalid connection_info, please correct it and try again.")

        connection_info = json.loads(connection_info)
        if connection_info is None:
            raise Exception("Invalid connection_info, please correct it and try again.")

        management_address = connection_info.get("address", None)
        management_username = connection_info.get("username", None)
        management_password = connection_info.get("password", None)
        auth_token = connection_info.get('api_token', None)
        logger.writeDebug("management_address={}", management_address)
        logger.writeDebug("management_username={}", management_username)

        if management_address is None:
            raise Exception(
                "Missing management_address, please correct it and try again."
            )
        # if management_username is None:
        #     raise Exception(
        #         "Missing management_username, please correct it and try again."
        #     )
        # if management_password is None:
        #     raise Exception(
        #         "Missing management_password, please correct it and try again."
        #     )
    
        ########################################################
        # True: test the rest of the module using api_token
        
        if False:
            ucpManager = UcpManager(
                management_address,
                management_username,
                management_password,
                auth_token,
            )    
            auth_token = ucpManager.getAuthTokenOnly()
            management_username = ''
            
        ########################################################
 
        ucpManager = UcpManager(
            management_address, management_username, management_password, auth_token
        )

        # theUCP = ucpManager.getUcpSystem( ucp_serial )
        # logger.writeDebug('theUCP={}', theUCP)

        ###########################################################
        # attach SS to UCP

        storage_serial = storage_system_info.get("serial", None)
        storage_address = storage_system_info.get("address", None)
        storage_user = storage_system_info.get("username", None)
        storage_password = storage_system_info.get("password", None)
        logger.writeDebug("storage_serial={}", storage_serial)
        logger.writeDebug("20230620 storage_user={}", storage_user)

        if storage_serial is None:
            raise Exception("Missing storage_serial, please correct it and try again.")

        if int(storage_serial) < 10000 or int(storage_serial) > 999999:
            raise Exception(
                "Invalid storage serial number, please correct it and try again."
            )

        # ucp is mantatory input
        # get the puma getway info out of it
        theUCP = ucpManager.getUcpSystem(ucp_serial)
        if theUCP is None:
          theUCP = ucpManager.createUcpSystem(
              CommonConstants.UCP_SERIAL,
              management_address,
              "UCP CI",
              ucp_serial,
              "AMERICA",
              "United States",
              "95054",
              ""
              )            
          theUCP = ucpManager.getUcpSystem( ucp_serial )
          # raise Exception("UCP {} is not found.".format(ucp_serial))
        if theUCP is None:
            ## sng,a2.4 system is not ready
            raise Exception("Unable to perform basic setup, the system is not ready.")

        logger.writeDebug("pcu={}", theUCP)
        ## to work with StorageSystem, it needs the serial, not name
        ucp_serial = theUCP["serialNumber"]
   
        
        state = module.params["state"]
        if state != "absent":
                  
            ## 2.4 - handle ss already onboarded
            # logger.writeDebug("380 theUCP={}", theUCP['storageDevices'])
            storageDevices = theUCP.get('storageDevices', None)
            if storageDevices:
              for storageDevice in storageDevices:
                # logger.writeDebug("380 storage_serial={}", storage_serial)
                # logger.writeDebug("380 storageDevice['serialNumber']={}", storageDevice['serialNumber'])
                if str(storageDevice['serialNumber']) == str(storage_serial):
                  # it is already onboarded
                  storageDevice.pop("ucpSystems", None)
                  logger.writeExitModule(moduleName)
                  module.exit_json(storageSystems=storageDevice)                     

            if storage_address is None:
                raise Exception(
                    "Missing storage_address, please correct it and try again."
                )
            if storage_user is None:
                raise Exception(
                    "Missing storage_user, please correct it and try again."
                )
            if storage_password is None:
                raise Exception(
                    "Missing storage_password, please correct it and try again."
                )

            gatewayIP = theUCP["gatewayAddress"]
            logger.writeDebug("20230616 gatewayIP={}", gatewayIP)

            results = ucpManager.addStorageSystem(
                storage_serial,
                storage_address,
                gatewayIP,
                8444,
                storage_user,
                storage_password,
                False,
                ucp_serial,
            )

            ## sng,a2.4 - expect only one ss here
            results.pop("ucpSystems", None)

            logger.writeExitModule(moduleName)
            module.exit_json(storageSystems=results)
            # module.exit_json(storageSystems=results['storageSystems'],
            # details=results['details'])
        else:
            results = ucpManager.removeStorageSystem(
                storage_serial,
                ucp_serial,
            )
            #    module.exit_json(**results)
            if results is not None and results:
                module.exit_json(msg="Storage is no longer in the system.")
            module.exit_json(msg=f"Storage with serial {storage_serial} successfully deleted.")

    except EnvironmentError as ex:
        logger.writeDebug("EnvironmentError={}", ex)
        if ex is None or ex.strerror is None:
            msg = "Failed to add storage, please check input parameters."
        else:
            msg = ex.strerror
        module.fail_json(msg=msg)
    except Exception as ex:
        logger.writeDebug("326 Exception={}", ex)
        # sng,a2.4 - there is no str(ex)?
        # if ex is None or str(ex) is None:
        if ex is None:
            msg = "Failed during add storage, please check input parameters."
        else:
            msg = str(ex)
        module.fail_json(msg=msg)


if __name__ == "__main__":
    main()
