#!/usr/bin/python
# -*- coding: utf-8 -*-

__metaclass__ = type

import logging
import os
import sys
import configparser
import ast
try:
    from enum import Enum
except ImportError as error:
    pass

from logging.config import fileConfig
from time import gmtime, strftime

try:
    from .hv_messages import MessageID
    from .ansible_common import get_ansible_home_dir

    HAS_MESSAGE_ID = True
    

except ImportError as error:
    from .ansible_common import get_ansible_home_dir

    HAS_MESSAGE_ID = False


class Log:

    logger = None

    @staticmethod
    def getHomePath():

        # example: "/opt/hitachivantara/ansible"

        path = os.getenv("HV_STORAGE_MGMT_PATH")

        if path is None:
            path = get_ansible_home_dir()
            # raise Exception("Improper environment home configuration, please execute the 'bash' command and try again.")

        if Log.logger:
            msg = "getHomePath={0}".format(path)
            #Log.logger.debug(msg)

        return path

    @staticmethod
    def getLogPath():
        path = os.getenv("HV_STORAGE_MGMT_VAR_LOG_PATH")  # example: "/var/log"

        # if HAS_MESSAGE_ID and path is None:
        #     path = '/var/log/hitachivantara/ansible/storage'
        #     #raise Exception("Improper environment configuration, please execute the 'bash' command and try again.")

        if Log.logger:
            msg = "getHomePath={0}".format(path)
            Log.logger.debug(msg)

        return path

    def __init__(self):

        if not Log.logger:

            # this is working, the urllib3 debug would show up
            # ............logging.basicConfig(
            # ............................filename='/var/log/hitachivantara/ansible/hv_storage_modules.log',
            # ............................level=logging.INFO,
            # ............................format='%(asctime)s %(name)-9s: %(levelname)s %(message)s'
            # ............................)
            # ............Log.logger = logging.getLogger("hv_logger")

            # funcName is the caller of the logging member func, like writeError
            # that is not what we want,
            # we might have to look at the call stack
            # ............logging.basicConfig(filename='/var/log/hitachivantara/ansible/hv_storage_modules.log',
            # ............................level=logging.DEBUG,format='%(asctime)s - %(levelname)-10s - %(funcName)s - %(message)s'
            # ............................)

            config = None
            if Log.getHomePath() is not None:
                config = os.path.join(Log.getHomePath(), "logger.config")

            if config is not None and os.path.exists(config):
                self.ensure_log_dirs(config)
                with open(config) as file:
                    fileConfig(file)
                Log.logger = logging.getLogger("hv_logger")
            else:
                logpath = "/var/log/hitachivantara/ansible/vspone_block"
                if Log.getLogPath() is not None:
                    logpath = Log.getLogPath()
                logging.basicConfig(
                    filename=logpath + "/hv_vspone_block_modules.log",
                    level=logging.INFO,
                    format="%(asctime)s: %(levelname)-6s %(message)s",
                )

                Log.logger = logging.getLogger("hv_logger")

            self.logger = Log.logger
        self.loadMessageIDs()


    def ensure_log_dirs(self, config_file):
        config = configparser.ConfigParser()
        config.read(config_file)

        # Iterate through handlers to find FileHandlers
        for section in config.sections():
            if section.startswith('handler_') and config[section]['class'] == 'handlers.RotatingFileHandler':
                # Extract the file path from the args parameter
                args = config.get(section, 'args')
                # args is expected to be a string representation of a tuple, e.g., "('logs/app.log', 'a')"
                try:
                    log_file_path = ast.literal_eval(args)[0]  # Use ast.literal_eval to safely parse the args tuple
                    log_dir = os.path.dirname(log_file_path)
                    os.makedirs(log_dir, exist_ok=True)
                except (ValueError, SyntaxError) as e:
                    raise ValueError(f"Error parsing log file path from args: {args}")


    def writeException(self, exception, messageID=None, *args):
        if isinstance(exception, Exception) is True and messageID is None:
            message = str(exception) #if not isinstance(exception, AttributeError) else exception.message
            message = "ErrorType={0}. Message={1}".format(
                type(exception), message
            )
        else:
            messageID = self.getMessageIDString(messageID, "E", "ERROR")
            if args:
                messageID = messageID.format(*args)
            message = strftime("%Y-%m-%d %H:%M:%S {} {}", gmtime()).format(
                messageID, exception
            )
        self.logger.error(message)

    def writeAMException(self, messageID, *args):

        # ........if isinstance(messageID, HiException):
        # ............messageId = exception.messageId
        # ............errorMessage = exception.errorMessage
        # ............self.logger.error("ERROR ANS [{}] {}".format(messageId, errorMessage))

        messageID = self.getMessageIDString(messageID, "E", "ERROR")
        if args:
            messageID = messageID.format(*args)
        msg = "MODULE {0}".format(messageID)
        self.logger.error(msg)

    def writeHiException(self, exception):
        from .hv_exceptions import HiException


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
            msg = "SDK [{0}] {1}".format(messageId, errorMessage)
            self.logger.error(msg)

    def addHandler(self):
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(
            logging.Formatter(
                "%(asctime)s - %(levelname)-10s - %(funcName)s - %(message)s"
            )
        )
        handler.setLevel(10)
        self.logger.addHandler(handler)

    def loadMessageIDs(self):
        if Log.getHomePath() is not None:
            resources = os.path.join(Log.getHomePath(), "/messages.properties")
        else:
            resources = "/opt/hitachivantara/ansible/messages.properties"
        self.messageIDs = {}
        if os.path.exists(resources):
            with open(resources) as file:
                for line in file.readlines():
                    (key, value) = line.split("=")
                    self.messageIDs[key.strip()] = value.strip()

    def getMessageIDString(self, messageID, charType, strType):
        if HAS_MESSAGE_ID and isinstance(messageID, MessageID):
            return "[{0}56{1:06X}] {2}".format(
                charType,
                messageID.value,
                self.messageIDs.get(messageID.name, messageID.name),
            )
        else:
            return messageID

    def writeParam(self, messageID, *args):
        if args:
            messageID = messageID.format(*args)
        msg = "PARAM: " + messageID
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
        msg = "ENTER: " + messageID
        self.logger.info(msg)

    def writeEnterModule(self, messageID, *args):
        if args:
            messageID = messageID.format(*args)
        msg = "ENTER MODULE: " + messageID
        self.logger.info(msg)

    def writeEnterSDK(self, messageID, *args):
        if args:
            messageID = messageID.format(*args)
        msg = "ENTER SDK: " + messageID
        self.logger.info(msg)

    def writeExit(self, messageID, *args):
        if args:
            messageID = messageID.format(*args)
        msg = "EXIT: " + messageID
        self.logger.info(msg)

    def writeExitSDK(self, messageID, *args):
        if args:
            messageID = messageID.format(*args)
        msg = "EXIT SDK: " + messageID
        self.logger.info(msg)

    def writeExitModule(self, messageID, *args):
        if args:
            messageID = messageID.format(*args)
        msg = "EXIT MODULE: " + messageID
        self.logger.info(msg)

    def writeWarning(self, messageID, *args):
        messageID = self.getMessageIDString(messageID, "W", "WARN")

        if args:
            messageID = messageID.format(*args)

        message = strftime("%Y-%m-%d %H:%M:%S ", gmtime()) + messageID
        self.logger.warning(messageID)

    def writeError(self, messageID, *args):
        messageID = self.getMessageIDString(messageID, "E", "ERROR")

        if args:
            messageID = messageID.format(*args)

        message = strftime("%Y-%m-%d %H:%M:%S ", gmtime()) + messageID
        message = messageID
        self.logger.error(messageID)

    def writeErrorModule(self, messageID, *args):
        messageID = self.getMessageIDString(messageID, "E", "ERROR")

        if args:
            messageID = messageID.format(*args)

        message = messageID
        msg = "MODULE " + messageID
        self.logger.error(msg)

    def writeErrorSDK(self, messageID, *args):
        messageID = self.getMessageIDString(messageID, "E", "ERROR")

        if args:
            messageID = messageID.format(*args)

        message = messageID
        msg = "SDK " + messageID
        self.logger.error(msg)

    def writeException1(self, exception, messageID, *args):
        messageID = self.getMessageIDString(messageID, "E", "ERROR")

        if args:
            messageID = messageID.format(*args)

        message = strftime("%Y-%m-%d %H:%M:%S {} {}", gmtime()).format(
            messageID, exception
        )
        self.logger.error(messageID)
