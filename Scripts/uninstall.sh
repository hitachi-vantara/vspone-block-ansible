#!/bin/bash

# Back up the config file
config_file="/opt/hitachi/ansible/storage.json"
if [ -f "$config_file" ]; then
   cp -f "${config_file}" "${config_file}.bak"
fi

rm -rf /opt/hitachi/ansible/support/library > /dev/null
rm -rf /opt/hitachi/ansible/support/module_utils > /dev/null
rm -rf /opt/hitachi/ansible/playbooks/block/library > /dev/null
rm -rf /opt/hitachi/ansible/playbooks/file/library > /dev/null
rm -rf /opt/hitachi/ansible/playbooks/block/modules > /dev/null
rm -rf /opt/hitachi/ansible/playbooks/file/modules > /dev/null
rm -rf /opt/hitachi/ansible/playbooks/block/module_utils > /dev/null
rm -rf /opt/hitachi/ansible/playbooks/file/module_utils > /dev/null

# Remove old name version if it exists
/usr/bin/rpm -e Ansible 2>/dev/null
echo "Uninstalling Hitachi API Gateway Service..."
response_o=`echo $?`
/usr/bin/rpm -e HV_Storage_Ansible 2>/dev/null
response=`echo $?`

if [ $response -ne 0 ] && [ $response_o -ne 0 ] && [ "$1" != '-q' ]; then
     echo "Hitachi Ansible RPM uninstallation failed."
     exit 1
fi

# uninstall dependency server if vRO started it.
conf_file=/var/log/hitachi/pumaconf
if [ -f "$conf_file" ]; then
echo "Uninstalling Hitachi Peer Service..."
    /usr/bin/rpm -e puma 2>/dev/null
	response_o=`echo $?`
    # delete the conf file
    /bin/rm -rf  $conf_file
    /bin/rm -rf  /etc/pki/ca-trust/source/anchors/puma.pem
fi

response=`echo $?`
if [ $response -ne 0 ] && [ "$1" != '-q' ]; then
     echo "dependency service uninstallation failed."
     exit 1
fi

# Stop VI service.
PROCESS_NUM=$(ps -ef | grep "VIService" | grep -v "grep" |  awk '{print $2}')
#echo $PROCESS_NUM
kill -9 $PROCESS_NUM
