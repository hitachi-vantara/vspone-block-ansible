#!/usr/bin/python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
__metaclass__ = type

import logging
import os
import sys

try:
    from enum import Enum
except ImportError as error:
    pass

from logging.config import fileConfig
from time import gmtime, strftime

try:
    from ansible_collections.hitachi.storage.plugins.module_utils.hv_messages import MessageID
    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False


class Log:

    logger = None

    @staticmethod
    def getHomePath():

        # example: "/opt/hitachi/ansible"

        path = os.getenv('HV_STORAGE_MGMT_PATH')

        if HAS_MESSAGE_ID and path is None:
            raise Exception("Improper environment home configuration, please execute the 'bash' command and try again."
                            )

        if Log.logger:
            msg = 'getHomePath={0}'.format(path)
            Log.logger.debug(msg)

        return path

    @staticmethod
    def getLogPath():
        path = os.getenv('HV_STORAGE_MGMT_VAR_LOG_PATH')  # example: "/var/log"

        if HAS_MESSAGE_ID and path is None:
            raise Exception("Improper environment configuration, please execute the 'bash' command and try again."
                            )

        if Log.logger:
            msg = 'getHomePath={0}'.format(path)
            Log.logger.debug(msg)

        return path

    def __init__(self):
        if not Log.logger:

            # this is working, the urllib3 debug would show up
            # ............logging.basicConfig(
            # ............................filename='/var/log/hitachi/ansible/hv_storage_modules.log',
            # ............................level=logging.INFO,
            # ............................format='%(asctime)s %(name)-9s: %(levelname)s %(message)s'
            # ............................)
            # ............Log.logger = logging.getLogger("hv_logger")

            # funcName is the caller of the logging member func, like writeError
            # that is not what we want,
            # we might have to look at the call stack
            # ............logging.basicConfig(filename='/var/log/hitachi/ansible/hv_storage_modules.log',
            # ............................level=logging.DEBUG,format='%(asctime)s - %(levelname)-10s - %(funcName)s - %(message)s'
            # ............................)

            config = None
            if Log.getHomePath() is not None:
                config = Log.getHomePath() + '/logger.config'

            if config is not None and os.path.exists(config):
                with open(config) as file:
                    fileConfig(file)
                Log.logger = logging.getLogger('hv_logger')
            else:
                logpath = "/var/log/"
                if Log.getLogPath() is not None:
                    logpath = Log.getLogPath()
                logging.basicConfig(filename=logpath
                                    + '/hv_storage_modules.log',
                                    level=logging.INFO,
                                    format='%(asctime)s: %(levelname)-6s %(message)s'
                                    )

                Log.logger = logging.getLogger('hv_logger')

            self.logger = Log.logger
        self.loadMessageIDs()

    def writeException(self, exception, messageID=None, *args):
        if isinstance(exception, Exception) is True and messageID is None:
            message = 'ErrorType={0}. Message={1}'.format(type(exception), exception.message)
        else:
            messageID = self.getMessageIDString(messageID, 'E', 'ERROR')
            if args:
                messageID = messageID.format(*args)
            message = strftime('%Y-%m-%d %H:%M:%S {} {}',
                               gmtime()).format(messageID, exception)
        self.logger.error(message)

    def writeAMException(self, messageID, *args):

        # ........if isinstance(messageID, HiException):
        # ............messageId = exception.messageId
        # ............errorMessage = exception.errorMessage
        # ............self.logger.error("ERROR ANS [{}] {}".format(messageId, errorMessage))

        messageID = self.getMessageIDString(messageID, 'E', 'ERROR')
        if args:
            messageID = messageID.format(*args)
        msg = 'MODULE {0}'.format(messageID)
        self.logger.error(msg)

    def writeHiException(self, exception):

        # ....................self.logger.debug("writeHiException")

        if isinstance(exception, HiException):

            # ........................self.writeParam("exception={}",str(exception))

            messageId = exception.messageId
            errorMessage = exception.errorMessage

            # ........................self.writeParam("messageId={}",messageId)
            # ........................self.writeParam("errorMessage={}",str(type(errorMessage)))
            # ........................self.writeParam("errorMessage={}",str(errorMessage))
            # message = exception.errorMessage
            # ........................self.writeParam("errorMessage={}",errorMessage)
            msg = 'SDK [{0}] {1}'.format(messageId, errorMessage)
            self.logger.error(msg)

    def addHandler(self):
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)-10s - %(funcName)s - %(message)s'))
        handler.setLevel(10)
        self.logger.addHandler(handler)

    def loadMessageIDs(self):
        if Log.getHomePath() is not None:
            resources = Log.getHomePath() + '/messages.properties'
        else:
            resources = '/opt/hitachi/ansible/messages.properties'
        self.messageIDs = {}
        if os.path.exists(resources):
            with open(resources) as file:
                for line in file.readlines():
                    (key, value) = line.split('=')
                    self.messageIDs[key.strip()] = value.strip()

    def getMessageIDString(self, messageID, charType, strType):
        if HAS_MESSAGE_ID and isinstance(messageID, MessageID):
            return '[{0}56{1:06X}] {2}'.format(charType, messageID.value, self.messageIDs.get(messageID.name, messageID.name))
        else:
            return messageID

    def writeParam(self, messageID, *args):
        if args:
            messageID = messageID.format(*args)
        msg = 'PARAM: ' + messageID
        self.logger.info(msg)

    def writeInfo(self, messageID, *args):
        if args:
            messageID = messageID.format(*args)
        self.logger.info(messageID)

    def writeDebug(self, messageID, *args):
        if args:
            messageID = messageID.format(*args)
        self.logger.debug(messageID)

    def writeEnter(self, messageID, *args):
        if args:
            messageID = messageID.format(*args)
        msg = 'ENTER: ' + messageID
        self.logger.info(msg)

    def writeEnterModule(self, messageID, *args):
        if args:
            messageID = messageID.format(*args)
        msg = 'ENTER MODULE: ' + messageID
        self.logger.info(msg)

    def writeEnterSDK(self, messageID, *args):
        if args:
            messageID = messageID.format(*args)
        msg = 'ENTER SDK: ' + messageID
        self.logger.info(msg)

    def writeExit(self, messageID, *args):
        if args:
            messageID = messageID.format(*args)
        msg = 'EXIT: ' + messageID
        self.logger.info(msg)

    def writeExitSDK(self, messageID, *args):
        if args:
            messageID = messageID.format(*args)
        msg = 'EXIT SDK: ' + messageID
        self.logger.info(msg)

    def writeExitModule(self, messageID, *args):
        if args:
            messageID = messageID.format(*args)
        msg = 'EXIT MODULE: ' + messageID
        self.logger.info(msg)

    def writeWarning(self, messageID, *args):
        messageID = self.getMessageIDString(messageID, 'W', 'WARN')

        if args:
            messageID = messageID.format(*args)

        message = strftime('%Y-%m-%d %H:%M:%S ', gmtime()) + messageID
        self.logger.warning(messageID)

    def writeError(self, messageID, *args):
        messageID = self.getMessageIDString(messageID, 'E', 'ERROR')

        if args:
            messageID = messageID.format(*args)

        message = strftime('%Y-%m-%d %H:%M:%S ', gmtime()) + messageID
        message = messageID
        self.logger.error(messageID)

    def writeErrorModule(self, messageID, *args):
        messageID = self.getMessageIDString(messageID, 'E', 'ERROR')

        if args:
            messageID = messageID.format(*args)

        message = messageID
        msg = 'MODULE ' + messageID
        self.logger.error(msg)

    def writeErrorSDK(self, messageID, *args):
        messageID = self.getMessageIDString(messageID, 'E', 'ERROR')

        if args:
            messageID = messageID.format(*args)

        message = messageID
        msg = 'SDK ' + messageID
        self.logger.error(msg)

    def writeException1(self, exception, messageID, *args):
        messageID = self.getMessageIDString(messageID, 'E', 'ERROR')

        if args:
            messageID = messageID.format(*args)

        message = strftime('%Y-%m-%d %H:%M:%S {} {}',
                           gmtime()).format(messageID, exception)
        self.logger.error(messageID)


class HiException0(Exception):

    pass


class HiException(Exception):

    def format(self):
        result = {}
        result['ErrorMessage'] = self.errorMessage
        result['MessageID'] = self.messageId
        return result

    def __init__(self, arg1=None, arg2=None):

        self.logger = Log()
        self.messageId = 'E0000000'
        self.errorMessage = ''
        self.parentException = None
        self.arg1 = arg1
        self.arg2 = arg2

        if isinstance(arg1, Exception):

            self.message = arg1.message
            arg = arg1.message
            if 'ErrorMessage' in arg:
                self.errorMessage = arg['ErrorMessage']
            if 'MessageID' in arg:
                self.messageId = arg['MessageID']

        if isinstance(arg1, dict):
            if 'ErrorMessage' in arg1:
                self.errorMessage = arg1['ErrorMessage']
            if 'MessageID' in arg1:
                self.messageId = arg1['MessageID']


class HiException2(Exception):

    def __init__(self, arg1=None, arg2=None):
        self.logger = Log()
        self.logger.writeInfo('HiException.init')
        self.messageId = 'E0000000'
        self.parentException = None
        self.arg1 = arg1
        self.arg2 = arg2

        if isinstance(arg1, Exception):
            self.logger.writeInfo('Exception')
            self.parentException = arg1
            hiJsonException = arg1.args[0]
            if isinstance(hiJsonException, dict):
                if 'ErrorMessage' in hiJsonException:
                    super().message = arg1.args[0]['ErrorMessage']
                if 'MessageID' in hiJsonException:
                    self.messageId = arg1.args[0]['MessageID']
            elif isinstance(hiJsonException, str):
                super().message = hiJsonException
        elif isinstance(arg1, tuple):
            self.logger.writeInfo('tuple')
            hiJsonException = arg1.args[0]
            if isinstance(hiJsonException, dict):
                if 'ErrorMessage' in hiJsonException:
                    super().message = arg1.args[0]['ErrorMessage']
                if 'MessageID' in hiJsonException:
                    self.messageId = arg1.args[0]['MessageID']
            elif isinstance(hiJsonException, str):
                super().message = hiJsonException
