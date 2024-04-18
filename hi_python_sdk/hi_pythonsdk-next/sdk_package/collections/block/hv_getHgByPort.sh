#!/bin/bash

curl  -k \
-H "Content-Type: application/json"   \
-H "X-Access-Mode: OOB" -H "X-Subsystem-Type: BLOCK" \
-H "X-Management-IPs: $1" \
-H "X-Storage-Id: $2" \
-H "X-Subsystem-User: $3"  \
-H "X-Subsystem-Password: $4" \
-X GET -d "{ \"port\" : \"$5\"  }" \
"https://172.25.20.27:8444/v8/storage/host-groups" 
