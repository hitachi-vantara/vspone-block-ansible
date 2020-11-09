import logging
import os.path

from enum import Enum
from logging.config import fileConfig
from logging.handlers import RotatingFileHandler
from time import gmtime, strftime
from ansible.module_utils.hv_messages import MessageID

class Logger():
	logger = None
	
	@staticmethod
	def getHomePath():

		path = os.getenv('HV_STORAGE_MGMT_PATH') # example: "/opt/hitachi/ansible"
		
		if path is None:
			raise Exception("Improper environment home configuration, please execute the 'bash' command and try again.")
		
		if Log.logger:
			Log.logger.debug("getHomePath=", path)
			
		return path

	def __init__(self):
		if not self.logger:
			## FIXME - remove hard coded path
			config = Log.getHomePath()+"/logger.config"
			if os.path.exists(config):
				with open(config) as file:
					fileConfig(file)
				self.logger = logging.getLogger("hv_logger")
			else:
				FORMAT = "%(asctime)-15s %(message)s"
				logging.basicConfig(format=FORMAT)
				self.logger = logging.getLogger("hv_logger")
				self.logger.setLevel(logging.INFO)
				handler = RotatingFileHandler("/var/log/hitachi/ansible.log", maxBytes=2048, backupCount=5)
				self.logger.addHandler(handler)

			## FIXME - remove hard coded path
			resources = Log.getHomePath()+"/messages.properties"
			self.messageIDs = {}
			if os.path.exists(resources):
				with open(resources) as file:
					for line in file.readlines():
						key, value = line.split("=")
						self.messageIDs[key.strip()] = value.strip()

	def getMessageIDString(self, messageID):
		if isinstance(messageID, MessageID):
			return "[{:06X}] {}".format(messageID.value, self.messageIDs.get(messageID.name, messageID.name))
		else:
			return "[------] {}".format(messageID)

	def writeInfo(self, messageID, *args):
		messageID = self.getMessageIDString(messageID)

		if args:
			messageID = messageID.format(*args)

		message = strftime("%Y-%m-%d %H:%M:%S ", gmtime()) + messageID
		self.logger.info(message)

	def writeWarning(self, messageID, *args):
		messageID = self.getMessageIDString(messageID)

		if args:
			messageID = messageID.format(*args)

		message = strftime("%Y-%m-%d %H:%M:%S ", gmtime()) + messageID
		self.logger.warning(message)

	def writeError(self, messageID, *args):
		messageID = self.getMessageIDString(messageID)

		if args:
			messageID = messageID.format(*args)

		message = strftime("%Y-%m-%d %H:%M:%S ", gmtime()) + messageID
		self.logger.error(message)

	def writeException(self, exception, messageID, *args):
		messageID = self.getMessageIDString(messageID)

		if args:
			messageID = messageID.format(*args)

		message = strftime("%Y-%m-%d %H:%M:%S {} {}", gmtime()).format(messageID, exception)
		self.logger.error(message)
