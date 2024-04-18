#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2020, Hewlett Packard Enterprise Development LP.
from __future__ import absolute_import, division, print_function
__metaclass__ = type

try:
    import requests
except ImportError as error:
    pass

from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log, \
    HiException


class ViService():
    def __init__(self, ip, port):
        self.baseUrl = "https://{0}:{1}".format(ip, port)

    def createRDM(self, vcIP, cluster, user, pwd, vmNames, lun):
        url = self.baseUrl + "/createRdmDisk"

        if isinstance(vmNames, list):
            vmNames = "||".join(vmNames)

        body = {
            "vcip": vcIP,
            "clusterName": cluster,
            "user": user,
            "pwd": pwd,
            "vmNames": vmNames,
            "lunIdStr": str(lun)
        }

        response = requests.post(url, json=body, verify=False)

        if response.ok:
            result = response.json()

            if not result.get("result"):
                raise Exception("Create RDM failed:" + result["failureReason"])
        else:
            raise Exception(
                "Unknown error HTTP {0}".format(response.status_code))
