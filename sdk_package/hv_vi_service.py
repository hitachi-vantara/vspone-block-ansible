import requests

from ansible.module_utils.hv_log import Log, HiException

class ViService():
	def __init__(self, ip, port):
		self.baseUrl = "https://{}:{}".format(ip, port)

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
			raise Exception("Unknown error HTTP {}".format(response.status_code))