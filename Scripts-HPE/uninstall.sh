#!/bin/bash

# Back up the config file
config_file="/opt/hpe/ansible/storage.json"
if [ -f "$config_file" ]; then
   cp -f "${config_file}" "${config_file}.bak"
fi

rm -rf /opt/hpe/ansible/support/library > /dev/null
rm -rf /opt/hpe/ansible/support/module_utils > /dev/null
rm -rf /opt/hpe/ansible/playbooks/block/library > /dev/null
rm -rf /opt/hpe/ansible/playbooks/file/library > /dev/null
rm -rf /opt/hpe/ansible/playbooks/block/modules > /dev/null
rm -rf /opt/hpe/ansible/playbooks/file/modules > /dev/null
rm -rf /opt/hpe/ansible/playbooks/block/module_utils > /dev/null
rm -rf /opt/hpe/ansible/playbooks/file/module_utils > /dev/null

# Remove old name version if it exists
/usr/bin/rpm -e Ansible 2>/dev/null
echo "Uninstalling HPE API Gateway Service..."
response_o=`echo $?`
/usr/bin/rpm -e HPE_Storage_Ansible 2>/dev/null
response=`echo $?`

if [ $response -ne 0 ] && [ $response_o -ne 0 ] && [ "$1" != '-q' ]; then
     echo "HPE Ansible RPM uninstallation failed."
     exit 1
fi
