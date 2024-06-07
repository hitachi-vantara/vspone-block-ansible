#!/usr/bin/python
# -*- coding: utf-8 -*-

__metaclass__ = type

import json
import re
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_ucpmanager import (
    UcpManager,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_infra import (
    StorageSystem,
    HostMode,
    StorageSystemManager,
    Utils,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_exceptions import (
    HiException,
)


from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    camel_to_snake_case,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import camel_to_snake_case_dict_array
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import CommonConstants

logger = Log()
moduleName = "UCP System Facts runner"


def runPlaybook(module):

    logger.writeEnterModule(moduleName)

    serial = module.params["serial_number"]
    model = module.params["model"]
    # name = module.params['name']
    name = CommonConstants.UCP_NAME
    
    connection_info = module.params["connection_info"]
    management_address = connection_info.get("address", None)
    management_username = connection_info.get("username", None)
    management_password = connection_info.get("password", None)
    subscriberId = connection_info.get("subscriber_id", None)
    api_token = connection_info.get("api_token", None)
    
    logger.writeDebug("54 connection_info={}", connection_info)
    logger.writeDebug("54 management_address={}", management_address)
    
    # 2.4 MT get_all_storages.yml
    
    ########################################################
    # True: test the rest of the module using api_token
    
    if False:
        ucpManager = UcpManager(
            management_address,
            management_username,
            management_password,
            api_token,
        )    
        api_token = ucpManager.getAuthTokenOnly()
        management_username = ''
        
    ########################################################
      
    ucpManager = UcpManager(
        management_address, management_username, management_password, api_token
    )

    if serial == "":
        serial = None
    if model == "":
        model = None

    logger.writeInfo("44 name={0}".format(name))
    if model is not None:
        x = re.search("^(UCP CI|UCP HC|UCP RS|Logical UCP)$", model)
        if not x:
            raise Exception(
                'The model is invalid, must be "UCP CI" or "UCP HC" or "UCP RS" or "Logical UCP".'
            )

    warning = ""
    # ss = 'Enter both the serial_number and the model to list one UCP, otherwise all UCPs are listed.'
    # if serial is None and model is not None:
    #    warning = ss
    # if model is None and serial is not None:
    #    warning = ss

    logger.writeInfo("56 name={0}".format(name))
    # if serial is None and model is None and name is None:
    if False:
        ucps = ucpManager.getAllUcpSystem()
        ucpManager.formatUCPs(ucps)
        module.exit_json(ucps=ucps, warning=warning)
    elif name is not None:

        #   str = model.replace(" ","-")
        #   str = str + '-' + serial
        #   x = re.search("^(UCP-CI|UCP-HC|UCP-RS|Logical-UCP)-\d{5,10}$", str)
        #   if not x:
        #       raise Exception('The serial number is invalid, must be minimum 5 digits and max 10 digits')
        serial = name

        ucps = ucpManager.getUcpSystem(serial)
        logger.writeDebug("67 name={0}".format(name))
        logger.writeInfo(ucps)

        if ucps is None:
            raise Exception("System is not found.")

        #   logger.writeDebug('20230605 ucps={}',ucps)
        # ucpManager.formatUCP(ucps)
        storages = ucpManager.getStorageDevices(ucps)
        ucpManager.formatStorages(storages)
        injectEntitlement(storages)        

    storages = camel_to_snake_case_dict_array(storages)
    logger.writeExitModule(moduleName)
    module.exit_json(storages=storages, warning=warning)
    
def injectEntitlement(ss):
    funcName = "injectEntitlement"
    logger.writeEnterSDK(funcName)
    try:
        for x in ss:
            x['entitlementStatus'] = 'assigned'
            x['partnerId'] = 'apiadmin'
            
        logger.writeExitSDK(funcName)
    except Exception as ex:
        logger.writeDebug("116 Exception={}", ex)
