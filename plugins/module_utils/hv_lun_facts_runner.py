#!/usr/bin/python
# -*- coding: utf-8 -*-

__metaclass__ = type
import json
import re

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_storagemanager import (
    StorageManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_ucpmanager import (
    UcpManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_infra import (
    StorageSystem,
    StorageSystemManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_infra import Utils
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_exceptions import (
    HiException,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    CommonConstants,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    camel_to_snake_case_dict_array,
    camel_to_snake_case_dict,
)


logger = Log()
moduleName = "LUN facts"


def runPlaybook(module):
    logger.writeEnterModule(moduleName)

    lun = None
    count = None
    lun_end = None
    name = None
    data = module.params.get("spec")
    if data:
        lun = data.get("lun")
        count = data.get("max_count")
        lun_end = data.get("lun_end")
        name = data.get("name")

    connection_info = module.params["connection_info"]
    management_address = connection_info.get("address", None)
    management_username = connection_info.get("username", None)
    management_password = connection_info.get("password", None)
    subscriberId = connection_info.get("subscriber_id", None)
    auth_token = connection_info.get("api_token", None)

    storage_system_info = module.params["storage_system_info"]
    storage_serial = storage_system_info.get("serial", None)
    ucp_serial = CommonConstants.UCP_NAME

    logger.writeParam("20230606 storage_serial={}", storage_serial)
    logger.writeParam("lun={}", lun)
    logger.writeParam("name={}", name)
    logger.writeParam("count={}", count)
    logger.writeParam("lun_end={}", lun_end)

    if storage_serial == "":
        storage_serial = None
    if lun == "":
        lun = None
    if count == "":
        count = None
    if lun_end == "":
        lun_end = None
    if name == "":
        name = None

    if ucp_serial == "":
        ucp_serial = None

    if ucp_serial is None:
        raise Exception("The ucp_name is invalid.")

    # x = re.search("^(UCP-CI|UCP-HC|UCP-RS|Logical-UCP)-\d{5,10}$", ucp_serial)
    # if not x:
    #     raise Exception('The ucp_serial is invalid.')

    partnerId = CommonConstants.PARTNER_ID
    # subscriberId=CommonConstants.SUBSCRIBER_ID
    
    ########################################################
    # True: test the rest of the module using api_token
    
    if False:
        ucpManager = UcpManager(
            management_address,
            management_username,
            management_password,
            auth_token,
            partnerId,
            subscriberId,
            storage_serial,
        )    
        auth_token = ucpManager.getAuthTokenOnly()
        management_username = ''
    ########################################################
    
    ## check the healthStatus=onboarding
    ucpManager = UcpManager(
        management_address,
        management_username,
        management_password,
        auth_token,
        partnerId,
        subscriberId,
        storage_serial,
    )
    if ucpManager.isOnboarding():
        raise Exception("Storage system is onboarding, please try again later.")

    # lun is a int?
    logger.writeDebug("82 lun={}", lun)
    logger.writeDebug(isinstance(lun, int))

    if lun is not None and ":" in str(lun):
        lun = Utils.getlunFromHex(lun)
        logger.writeDebug("Hex converted lun={0}".format(lun))
        if lun is None:
            raise Exception("The LUN is not found.")

    # if lun is not None:
    #     if not isinstance(lun, int) and lun.startswith('naa.'):
    #         logger.writeDebug('Parsing Naa lun={0}'.format(lun))
    #         storage_serial = Utils.getSerialByNaa(lun)
    #         logger.writeDebug('storage_serial={0}'.format(storage_serial))

    if storage_serial is None:
        if lun is not None and lun.startswith("naa."):
            storage_serial = "get.lun.naa"
        else:
            raise Exception("The storage_serial is missing.")
    # logger.writeDebug('Utils.isGivenValidSerial(storage_serial)={0}'.format(
    #     Utils.isGivenValidSerial(storage_serial)))
    # if not Utils.isGivenValidSerial(storage_serial):
    #     raise Exception(
    #         'Storage system {0} is not registered. Double-check the serial number or run the hv_storagesystem \
    #         module with this storage system.'.format(storage_serial))

    # storageSystem = StorageSystem(storage_serial)
    logger.writeDebug("108 storage_serial={}", storage_serial)
    storageSystem = UcpManager(
        management_address,
        management_username,
        management_password,
        auth_token,
        partnerId,
        subscriberId,
        storage_serial,
    )

    if lun is None and count is not None:
        raise Exception("The lun parameter is required along with max_count.")

    luns = None
    if lun is not None:
        luns = []
        logger.writeDebug("121 lun={}", lun)
        if not isinstance(lun, int) and lun.startswith("naa."):
            
            ####### get lun by NAA ##########
            
            logger.writeDebug("20230606 count={}", count)
            if count is None or count == 0:
                lun = storageSystem.getLunByNaa(lun)
                if lun:
                    luns.append(lun)
            else:
                raise Exception(
                    "The parameter 'count' must be zero if lun starts with 'naa'."
                )
                if int(count) < 1:
                    raise Exception(
                        "The parameter 'count' must be a whole number greater than zero."
                    )  #
                lunswithcount = None
                logger.writeInfo("getLunByNaa getAllLuns")
                # FIXME a2.4 - bug, lun is naa here!!
                luns = storageSystem.getLunByID(lun)
                logger.writeDebug("20230606 count={}", count)
                lun = storageSystem.getLunByNaa(lun)
                for index, item in enumerate(luns):
                    if str(item.get("ldevId")) == str(lun.get("ldevId")):
                        logger.writeDebug("index={}", index)
                        lunswithcount = luns[index : index + int(count)]
                        break
                luns = lunswithcount
            logger.writeDebug("luns={}", luns)
        elif count is not None:
            if int(count) < 1:
                raise Exception(
                    "The parameter 'count' must be a whole number greater than zero."
                )
            if lun_end is not None:
                raise Exception(
                    "Ambiguous parameters, max_count and lun_end cannot co-exist."
                )

            ####### get lun with count ##########
            
            logger.writeInfo("168 getLunByID count={}", count)
            # luns = storageSystem.getAllLuns()
            luns = storageSystem.getLunByID(lun)
            # logger.writeInfo('157 luns={}', luns)
            # g = (i for i, e in enumerate([1, 2, 1]) if e == 1)

            # logger.writeInfo(luns)
            # index = [index for index, item in luns if item.get(
            #     'ldevId') == str(lun)]
            lunswithcount = []
            logger.writeDebug("deduce the output starting at lun={}", lun)
            if luns:
                for index, item in enumerate(luns):
                    # logger.writeDebug('165 item={}', item)
                    item_ldevId = str(item.get("ldevId"))
                    if (
                        (item_ldevId == str(lun))
                        or (str(lun) == "1")
                        or int(item_ldevId) > int(lun)
                    ):
                        logger.writeDebug("20230606 found index={}", index)
                        logger.writeDebug("20230606 count={}", count)
                        lunswithcount = luns[index : index + int(count)]
                        break
            # logger.writeDebug('173 lunswithcount={}', lunswithcount)
            luns = lunswithcount
            # luns = storageSystem.getLunsByCount(lun, count)
        elif lun_end is not None:
            lunswithcount = []
            logger.writeInfo("192 getLunByID lun_end={}", lun_end)
            # luns = storageSystem.getAllLuns()
            luns = storageSystem.getLunByID(lun)
            logger.writeInfo("179 luns={}", luns)
            # luns = storageSystem.getLunsByRange(lun, lun_end)

            # Ensure lun and lun_end are integers (assuming they're not already)
            lun = int(lun)
            lun_end = int(lun_end)

            for item in luns:
                # Safely retrieve ldevId and convert it to an integer, assuming it's numeric
                ldev_id = int(
                    item.get("ldevId", 0)
                )  # Default to 0 if ldevId is not found

                # Check if the current LUN is within the range [lun, lun_end]
                if lun <= ldev_id <= lun_end:
                    lunswithcount.append(item)
                    logger.writeParam("lunswithcount={}".format(lunswithcount))

                # Break the loop if ldev_id reaches or exceeds lun_end
                if ldev_id >= lun_end:
                    break

            luns = lunswithcount

        else:
            lun = storageSystem.getLun(lun)
            if lun:
                luns.append(lun)
        if luns:
            logger.writeDebug("response: luns={}", luns)
    elif luns is not None:

        # # terraform only

        logger.writeInfo("getAllLuns luns={}", luns)
        luns = [unit for unit in storageSystem.getAllLuns() if unit["ldevId"] in luns]
    elif name is not None:
        logger.writeInfo("getAllLuns name={}", name)
        luns = [unit for unit in storageSystem.getAllLuns() if unit["name"] == name]
    else:
        logger.writeInfo("214 getAllLuns")
        luns = storageSystem.getAllLuns()

    logger.writeInfo("223 luns={}", luns)
    Utils.formatLuns(luns)
    if luns:
        luns = camel_to_snake_case_dict_array(luns)
    logger.writeExitModule(moduleName)
    # return luns
    module.exit_json(data=luns)
