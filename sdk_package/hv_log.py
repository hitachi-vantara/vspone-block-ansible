import sys
import logging
import os

from enum import Enum
from logging.config import fileConfig
from logging.handlers import RotatingFileHandler
from time import gmtime, strftime
from ansible.module_utils.hv_messages import MessageID

class Log():
	logger = None
    
	@staticmethod
	def getHomePath():

		path = os.getenv('HV_STORAGE_MGMT_PATH') # example: "/opt/hitachi/ansible"
		
		if path is None:
			raise Exception("Improper environment home configuration, please execute the 'bash' command and try again.")
		
		if Log.logger:
			Log.logger.debug("getHomePath=", path)
			
		return path

	@staticmethod
	def getLogPath():
		path = os.getenv('HV_STORAGE_MGMT_VAR_LOG_PATH') # example: "/var/log"
		
		if path is None:
			raise Exception("Improper environment configuration, please execute the 'bash' command and try again.")
		
		if Log.logger:
			Log.logger.debug("getLogPath=", path)
			
		return path

	def __init__(self):
		if not Log.logger:
			
			## this is working, the urllib3 debug would show up
# 			logging.basicConfig(
# 							filename='/var/log/hitachi/ansible/hv_storage_modules.log',
# 							level=logging.INFO,
# 							format='%(asctime)s %(name)-9s: %(levelname)s %(message)s'
# 							)
# 			Log.logger = logging.getLogger("hv_logger")
			
			## funcName is the caller of the logging member func, like writeError
			## that is not what we want,
			## we might have to look at the call stack
# 			logging.basicConfig(filename='/var/log/hitachi/ansible/hv_storage_modules.log',
# 							level=logging.DEBUG,format='%(asctime)s - %(levelname)-10s - %(funcName)s - %(message)s'
# 							)
			
			config = Log.getHomePath()+"/logger.config"
			if os.path.exists(config):
				with open(config) as file:
					fileConfig(file)
				Log.logger = logging.getLogger("hv_logger")
			else:
	 			logging.basicConfig(
	 							filename=Log.getLogPath()+'/hv_storage_modules.log',
	 							level=logging.INFO,
	 							#format='%(asctime)s %(name)-9s: %(levelname)s %(message)s'
	 							format='%(asctime)s: %(levelname)-6s %(message)s'
	 							)
	 			Log.logger = logging.getLogger("hv_logger")

			self.logger = Log.logger
# 			self.writeInfo("SDK:Log:init")
			
		## FIXME - if the messagid table is static, we shouldn't have to load it everytime!! 	
		self.loadMessageIDs()			
		
	def writeException(self, exception, messageID=None, *args):
		
		if isinstance(exception, Exception) == True and messageID == None:
			message = "ErrorType={}. Message={}".format(type(exception), exception.message)
		else:
			messageID = self.getMessageIDString(messageID, "E", "ERROR")
			if args:
				messageID = messageID.format(*args)
			message = strftime("%Y-%m-%d %H:%M:%S {} {}", gmtime()).format(messageID, exception)
		self.logger.error(message)
	
	def writeAMException(self, messageID, *args):
		
# 		if isinstance(messageID, HiException):
# 			messageId = exception.messageId
# 			errorMessage = exception.errorMessage
# 			self.logger.error("ERROR ANS [{}] {}".format(messageId, errorMessage))
					
		messageID = self.getMessageIDString(messageID, "E", "ERROR")
		if args:
			messageID = messageID.format(*args)
		self.logger.error("MODULE {}".format(messageID))

	def writeHiException(self, exception):
# 					self.logger.debug("writeHiException")
					if isinstance(exception, HiException):
# 						self.writeParam("exception={}",str(exception))
						messageId = exception.messageId
						errorMessage = exception.errorMessage
# 						self.writeParam("messageId={}",messageId)
# 						self.writeParam("errorMessage={}",str(type(errorMessage)))
# 						self.writeParam("errorMessage={}",str(errorMessage))
						#message = exception.errorMessage
# 						self.writeParam("errorMessage={}",errorMessage)
						self.logger.error("SDK [{}] {}".format(messageId, errorMessage))
			
	def addHandler(self):
			handler = logging.StreamHandler(sys.stderr)
			handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)-10s - %(funcName)s - %(message)s') )
			handler.setLevel(10)
			self.logger.addHandler(handler)
		
	def loadMessageIDs(self):
			resources = Log.getHomePath()+"/messages.properties"
# 			self.writeInfo("loadMessageIDs:{}",resources)
			self.messageIDs = {}
			if os.path.exists(resources):
# 				self.writeInfo("path.exists open")
				with open(resources) as file:
					for line in file.readlines():
						key, value = line.split("=")
						#self.writeInfo("key",key)
						#self.writeInfo("value",value)
						self.messageIDs[key.strip()] = value.strip()

	def getMessageIDString(self, messageID, charType, strType):
		if isinstance(messageID, MessageID):
			return "[{}56{:06X}] {}".format(charType, messageID.value, self.messageIDs.get(messageID.name, messageID.name))
		else:
			#return "[------] {} {}".format(strType, messageID)
			return messageID
	
	
# 	def debug(self, msg, *args):
# 		self.logger.debug(msg, args)
# 		
# 	def debug(self, *args):
# 		self.logger.debug(args)
		
	def writeParam(self, messageID, *args):	
		if args:
			messageID = messageID.format(*args)
		self.logger.info("PARAM: " + messageID)
		
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
		self.logger.info("ENTER: " + messageID)
		
	def writeEnterModule(self, messageID, *args):	
		if args:
			messageID = messageID.format(*args)
		self.logger.info("ENTER MODULE: " + messageID)
		
	def writeEnterSDK(self, messageID, *args):	
		if args:
			messageID = messageID.format(*args)
		self.logger.info("ENTER SDK: " + messageID)
		
	def writeExit(self, messageID, *args):	
		if args:
			messageID = messageID.format(*args)
		self.logger.info("EXIT: " + messageID)
		
	def writeExitSDK(self, messageID, *args):	
		if args:
			messageID = messageID.format(*args)
		self.logger.info("EXIT SDK: " + messageID)
		
	def writeExitModule(self, messageID, *args):	
		if args:
			messageID = messageID.format(*args)
		self.logger.info("EXIT MODULE: " + messageID)
		
# 	def writeInfo(self, *args):
# 		self.logger.info(args)
# 		
# 	def writeInfo(self, messageID, *args):
# 		messageID = self.getMessageIDString(messageID, "I", "INFO")
# 
# 		if args:
# 			messageID = messageID.format(*args)
# 
# 		message = strftime("%Y-%m-%d %H:%M:%S ", gmtime()) + messageID
# 		
# 		## messageID is not known, display as raw message
# 		message = messageID
# 		#self.logger.error("ERROR {file::function}:" + messageID)
# 		self.logger.info("INFO " + messageID)

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
		
		## messageID is not known, display as raw message
		message = messageID
		#self.logger.error("ERROR {file::function}:" + messageID)
		self.logger.error(messageID)

	def writeErrorModule(self, messageID, *args):
		messageID = self.getMessageIDString(messageID, "E", "ERROR")

		if args:
			messageID = messageID.format(*args)

		message = messageID
		self.logger.error("MODULE "+messageID)

	def writeErrorSDK(self, messageID, *args):
		messageID = self.getMessageIDString(messageID, "E", "ERROR")

		if args:
			messageID = messageID.format(*args)

		message = messageID
		self.logger.error("SDK "+messageID)

	def writeException1(self, exception, messageID, *args):
		messageID = self.getMessageIDString(messageID, "E", "ERROR")

		if args:
			messageID = messageID.format(*args)

		message = strftime("%Y-%m-%d %H:%M:%S {} {}", gmtime()).format(messageID, exception)
		self.logger.error(messageID)



class HiException0(Exception):
	pass

class HiException(Exception):
	
	def format(self):
		result = {}
		result["ErrorMessage"] = self.errorMessage
		result["MessageID"] = self.messageId
		return result
	
	def __init__(self, arg1=None, arg2=None):
				
		self.logger = Log()
# 		self.logger.writeEnter("HiException.init")
		
		self.messageId = "E0000000"
		self.errorMessage = ""
		self.parentException = None
		self.arg1 = arg1
		self.arg2 = arg2
		
# 		self.logger.writeInfo(str(type(arg1)))
		
		if isinstance(arg1, Exception):
# 			self.logger.writeInfo("arg1 is Exception={}",arg1)
			self.message = arg1.message
			#self.logger.writeInfo("super={}",super())
			#self.logger.writeInfo("super().message={}",super.message)
			arg = arg1.message
			if 'ErrorMessage' in arg:
				self.errorMessage = arg["ErrorMessage"] 
			if 'MessageID' in arg:
				self.messageId = arg["MessageID"] 
		
		if isinstance(arg1, dict):
			if 'ErrorMessage' in arg1:
				self.errorMessage = arg1["ErrorMessage"] 
			if 'MessageID' in arg1:
				self.messageId = arg1["MessageID"] 
	
class HiException2(Exception):
	
    # case #1:
    #   arg1 can be the Exception with HiJsonException dictionary assigned to Exception.args[0]
    #   Note: this is for handling the exception coming from the C# Rest API Service
    # case #2:
    #   arg1 is message id (string)
    #   arg2 is message (string)
    # case #3:
    #   arg1 is HiJsonException dictionary
    # case #4:
    #   arg1 is message (string)
    def __init__(self, arg1=None, arg2=None):    	
    	self.logger = Log()
    	self.logger.writeInfo("HiException.init")
        self.messageId = "E0000000"
        self.parentException = None
        self.arg1 = arg1
        self.arg2 = arg2
        
        
        if isinstance(arg1, Exception) :
			self.logger.writeInfo("Exception")
			self.parentException = arg1
			hiJsonException = arg1.args[0]
			if isinstance(hiJsonException, dict):
				if 'ErrorMessage' in hiJsonException:
				    super().message = arg1.args[0]["ErrorMessage"] 
				if 'MessageID' in hiJsonException:
				    self.messageId = arg1.args[0]["MessageID"] 
			elif isinstance(hiJsonException, str): 
				super().message = hiJsonException
        elif isinstance(arg1, tuple) :
			self.logger.writeInfo("tuple")
			hiJsonException = arg1.args[0]
			if isinstance(hiJsonException, dict):
				if 'ErrorMessage' in hiJsonException:
					super().message = arg1.args[0]["ErrorMessage"] 
				if 'MessageID' in hiJsonException:
					self.messageId = arg1.args[0]["MessageID"] 
			elif isinstance(hiJsonException, str):
				super().message = hiJsonException

# 		elif isinstance(arg1, str) and isinstance(arg2, str):
# 			self.logger.writeInfo("arg1, arg2 str")
# 			self.messageId = arg1
# 			super().message = arg2
# 		elif isinstance(arg1, str):
# 			self.logger.writeInfo("arg1 str")
# 			super().message = arg1

        



