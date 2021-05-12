#!/bin/bash

# Remove old name version if it exists
/usr/bin/rpm -e Ansible 2>/dev/null
response_o=`echo $?`
/usr/bin/rpm -e HV_Ansible 2>/dev/null
response=`echo $?`

if [ $response -ne 0 ] && [ $response_o -ne 0 ] && [ "$1" != '-q' ]; then
     echo "Hitachi Ansible RPM uninstallation failed."
     exit 1
fi

# # Stop VI service.
# PROCESS_NUM=$(ps -ef | grep "VIService" | grep -v "grep" |  awk '{print $2}')
# #echo $PROCESS_NUM
# kill -9 $PROCESS_NUM

rm -rf /opt/hitachi/ansible
