#!/usr/bin/python
# -*- coding: utf-8 -*-

__metaclass__ = type

import json
import re
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachi.storage.plugins.module_utils.hv_ucpmanager import UcpManager

from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log, \
    HiException

logger = Log()
moduleName = 'UCP System runner'


def writeNameValue(name, value):
    logger.writeDebug(name, value)


def runPlaybook(module):

    logger.writeEnterModule(moduleName)

    state = module.params['state']

    gateway_address = module.params['gateway_address']
    serial_number = module.params['serial_number']
    model = module.params['model']
    name = module.params['name']
    region = module.params['region']
    country = module.params['country']
    zipcode = module.params['zipcode']
    zone = ""
    ucpadvisor_address = module.params['ucpadvisor_address']
    ucpadvisor_ansible_vault_user = module.params['ucpadvisor_ansible_vault_user']
    ucpadvisor_ansible_vault_secret = module.params['ucpadvisor_key']

    logger.writeDebug('20230505 ucpadvisor_address={}',ucpadvisor_address)
    logger.writeDebug('20230505 ucpadvisor_ansible_vault_user={}',ucpadvisor_ansible_vault_user)
    logger.writeDebug('serial_number={}'.format(serial_number))
    logger.writeDebug('gateway_address={0}'.format(gateway_address))

    ucpManager = UcpManager(
        ucpadvisor_address,
        ucpadvisor_ansible_vault_user,
        ucpadvisor_ansible_vault_secret)
    
    # first try to get UCP by name,
    # if exist, it is update ucp,
    # else it is create
    theUCP = None
    if name is not None:
        theUCP = ucpManager.getUcpSystem( name )

    logger.writeDebug('theUCP={}',theUCP)
    logger.writeDebug('state={}',state)

    # check for delete ucp
    if state != 'present':

        logger.writeDebug('delete ucp')

        if theUCP is None:
            raise Exception("Unable to find the UCP.")
        resourceId = theUCP['resourceId']
        ucpManager.deleteUcpSystem( resourceId )
        ucp = theUCP
        ucpManager.formatUCP(ucp)
        logger.writeExitModule(moduleName)
        module.exit_json(ucps=ucp)
        return

    warning = ''
    ucp = None
    if theUCP is None:

        ## Create UCP

        ## find UCP by serial, TRG-13658
        ## won't work, this is not the ucp serial, it's the serial_number with out the model number
        # logger.writeDebug('83 serial_number={}'.format(serial_number))
        # theUCP = ucpManager.getUcpSystem( serial_number )
        # if theUCP is not None :
        #     raise Exception("UCP serial number is already in use.")

        # parameter is not given, it could be from two playbook with invalid inputs:
        # - create with missing name param
        # - update with incorrect serial_number
        format1 = 'UCP is not found with the serial number. In order to create the UCP, the '
        format2 = ' parameter is required.'
        if gateway_address is None:
            raise Exception(format1+'gateway_address'+format2)
        if model is None:
            raise Exception(format1+'model'+format2)
        if name is None:
            raise Exception(format1+'name'+format2)
        if region is None:
            raise Exception(format1+'region'+format2)
        if country is None:
            raise Exception(format1+'country'+format2)
        if zipcode is None:
            raise Exception(format1+'zipcode'+format2)
        
        if serial_number is None:
            raise Exception('The serial number is required.')
        if model is None:
            raise Exception('The model is required.')

        if len(serial_number) < 5:
            raise Exception('The serial number is invalid, must be minimum 5 digits and max 10 digits')

        x = re.search("^(UCP CI|UCP HC|UCP RS|Logical UCP)$", model)
        if not x:
            raise Exception('The model is invalid, must be "UCP CI" or "UCP HC" or "UCP RS" or "Logical UCP".')

        str = model.replace(" ","-")
        str = str + '-' + serial_number
        x = re.search("^(UCP-CI|UCP-HC|UCP-RS|Logical-UCP)-\d{5,10}$", str)
        if not x:
            raise Exception('The serial number is invalid, must be minimum 5 digits and max 10 digits')

        serial_number = str        
        
        theUCP = ucpManager.getUcpSystemByName( name )
        if theUCP is not None:
            raise Exception('The name is already in use.')

        ucp = ucpManager.createUcpSystem(
            serial_number,
            gateway_address,
            model,
            name,
            region,
            country,
            zipcode,
            zone
            )
    else:
        resourceId = theUCP['resourceId']
        if resourceId is None:
            raise Exception('The UCP is not found')
        
        format1 = 'In order to update the UCP, the '
        format2 = ' parameter is required.'
        if gateway_address is None:
            raise Exception(format1+'gateway_address'+format2)
        if region is None:
            raise Exception(format1+'region'+format2)
        if country is None:
            raise Exception(format1+'country'+format2)
        if zipcode is None:
            raise Exception(format1+'zipcode'+format2)         
        if name is not None and name != theUCP['name']:
            warning= 'UCP name cannot be updated, the name parameter is ignored.'
               
        ucp = ucpManager.updateUcpSystem(
            resourceId,
            gateway_address,
            region,
            country,
            zipcode,
            )
        
    ucp = ucpManager.getUcpSystem( name )
    # logger.writeDebug('state={}',state)
    # logger.writeDebug('20230506 ucp={}',ucp)
    ucpManager.formatUCP(ucp)
    logger.writeExitModule(moduleName)
    module.exit_json(ucps=ucp, warning=warning)
