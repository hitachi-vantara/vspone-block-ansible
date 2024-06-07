#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2020, Hewlett Packard Enterprise Development LP.

__metaclass__ = type

try:
    from enum import Enum

    class MessageID(Enum):

        ERR_AddRAIDStorageDevice = 0xA004
        ERR_CreateCommandDevice = 0xA076
        ERR_AddHNASStorageDevice = 0xA19B
        ERR_GET_SUPPORT_LOGS = 0xA1ED
        ERR_OPERATION_HOSTGROUP = 0xA1F1
        ERR_OPERATION_LUN = 0xA1F2
        ERR_CREATE_DYNAMICPOOL = 0xA088

except ImportError as error:

    # Output expected ImportErrors.
    # print("enum module not found")

    pass
