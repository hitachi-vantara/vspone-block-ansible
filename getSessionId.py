from __future__ import print_function
import json
import requests
import sys

USAGE = sys.argv[0] + " json_file"

def main():
	if len(sys.argv) < 2:
		print(USAGE, file=sys.stderr)
		exit(1);
	with open(sys.argv[1], 'r') as config:
		data = json.load(config)
		url = "https://{0}:{1}/HitachiStorageManagementWebServices/StorageManager/StorageManager/AddRAID".format(
			data["storageGateway"], data["storageGatewayPort"])
		sessionId = ""
		for subsystem in data["subsystems"]:
			subsystem["sessionId"] = sessionId;
			serialNumber = subsystem["serialNumber"]
			response = requests.post(url, json=subsystem, verify=False)
			if response.ok:
				if sessionId == "": sessionId = response.json()["SessionId"]
			else:
				errormsg = "Unknown Error Occurred for Subsystem {}".format(serialNumber)
				if "HIJSONFAULT" in response.headers:
					errormsg = "Storage Gateway Fault for Subsystem {}:\n{}".format(serialNumber, response.headers["HIJSONFAULT"])
				else:
					errormsg = "Storage Gateway Error for Subsystem {}: HTTP {}".format(serialNumber, response.status_code)
				print(errormsg, file=sys.stderr)
		fs_url = "NAS/StorageManager/AddFileServer"

	print(sessionId)

if __name__ == '__main__':
	main()
