#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2020, Hewlett Packard Enterprise Development LP.
from __future__ import absolute_import, division, print_function
__metaclass__ = type

import json
import logging

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystem, \
    StorageSystemManager
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import Utils

from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log, \
    HiException

logger = Log()
moduleName = "VSM facts"


def cleanResult(vsmResult):
    if vsmResult.get("Model") is not None:
        del vsmResult["Model"]
    if vsmResult.get("Type") is not None:
        del vsmResult["Type"]

    ResourceGroups = vsmResult["ResourceGroups"]
    for rg in ResourceGroups:
        if rg.get("VirtualDeviceModel") is not None:
            del rg["VirtualDeviceModel"]
        if rg.get("VirtualDeviceType") is not None:
            del rg["VirtualDeviceType"]
        if rg.get("VirtualStorageMachineType") is not None:
            del rg["VirtualStorageMachineType"]
        if rg.get("VirtualStorageModelType") is not None:
            del rg["VirtualStorageModelType"]


def runPlaybook(module):

    logger.writeEnterModule(moduleName)

    data = json.loads(module.params["data"])
    virtual_storage_serial = data["virtual_storage_serial"]
    storageSystem = StorageSystem(virtual_storage_serial).vsmManager

    storage_serial = module.params.get("storage_serial", None)
    if storage_serial == "":
        storage_serial = None

    logger.writeParam("virtual_storage_serial={}", virtual_storage_serial)
    logger.writeParam("storage_serial={}", storage_serial)

    if storage_serial is None:
        vsmResult = storageSystem.getVSMBySerial(virtual_storage_serial)
    else:
        vsmResult = storageSystem.getVSMBySerial(storage_serial)

    if vsmResult is not None and vsmResult.get("Serial") is not None:
        vserial = vsmResult.get("Serial")
        if str(vserial) == str(0):
            vsmResult = {}
        else:
            cleanResult(vsmResult)
    else:
        vsmResult = {}

    logger.writeExitModule(moduleName)
    module.exit_json(vsm=vsmResult)
