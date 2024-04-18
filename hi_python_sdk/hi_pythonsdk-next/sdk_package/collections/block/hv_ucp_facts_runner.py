#!/usr/bin/python
# -*- coding: utf-8 -*-

__metaclass__ = type

import json
import re
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachi.storage.plugins.module_utils.hv_ucpmanager import UcpManager

from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystem, \
    HostMode, StorageSystemManager, Utils

from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log, \
    HiException

logger = Log()
moduleName = 'UCP System Facts runner'


def runPlaybook(module):

    logger.writeEnterModule(moduleName)

    serial = module.params['serial_number']
    model = module.params['model']
    name = module.params['name']
    ucpadvisor_address = module.params['ucpadvisor_address']
    ucpadvisor_username = module.params['ucpadvisor_username']
    ucpadvisor_password = module.params['ucpadvisor_key']

    ucpManager = UcpManager(
        ucpadvisor_address,
        ucpadvisor_username,
        ucpadvisor_password)

    if serial == '':
        serial = None
    if model == '':
        model = None

    if model is not None:
      x = re.search("^(UCP CI|UCP HC|UCP RS|Logical UCP)$", model)
      if not x:
          raise Exception('The model is invalid, must be "UCP CI" or "UCP HC" or "UCP RS" or "Logical UCP".')

    warning = ''
    #ss = 'Enter both the serial_number and the model to list one UCP, otherwise all UCPs are listed.'
    # if serial is None and model is not None:
    #    warning = ss
    # if model is None and serial is not None:
    #    warning = ss

    if serial is None and model is None and name is None:
      ucps = ucpManager.getAllUcpSystem()
      ucpManager.formatUCPs(ucps)
    elif name is not None:

    #   str = model.replace(" ","-")
    #   str = str + '-' + serial
    #   x = re.search("^(UCP-CI|UCP-HC|UCP-RS|Logical-UCP)-\d{5,10}$", str)
    #   if not x:
    #       raise Exception('The serial number is invalid, must be minimum 5 digits and max 10 digits')
      serial = name

      logger.writeDebug('67 name={0}'.format(name))
      ucps = ucpManager.getUcpSystem(serial)

      if ucps is None:
          raise Exception('UCP is not found.')
         
      logger.writeDebug('20230605 ucps={}',ucps)
      ucpManager.formatUCP(ucps)

    logger.writeExitModule(moduleName)
    module.exit_json(ucps=ucps, warning=warning)
