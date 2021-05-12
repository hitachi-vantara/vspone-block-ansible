#!/bin/bash

# Remove old name version if it exists
/usr/bin/rpm -e Ansible 2>/dev/null
response_o=`echo $?`
/usr/bin/rpm -e HPE_Storage_Ansible 2>/dev/null
response=`echo $?`

if [ $response -ne 0 ] && [ $response_o -ne 0 ] && [ "$1" != '-q' ]; then
     echo "HPE XP Ansible RPM uninstallation failed."
     exit 1
fi



rm -rf /opt/hpe/ansible
