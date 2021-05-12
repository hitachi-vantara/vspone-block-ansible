#!/bin/bash

cp -rf /opt/hpe/ansible /tmp/ansible.install.amo

# Remove old name version if it exists
/usr/bin/rpm -e Ansible 2>/dev/null
echo "Uninstalling Storage Management Service..."
response_o=`echo $?`
/usr/bin/rpm -e HPE_Storage_Ansible 2>/dev/null
response=`echo $?`

if [ $response -ne 0 ] && [ $response_o -ne 0 ] && [ "$1" != '-q' ]; then
     echo "hpe Ansible RPM uninstallation failed."
     exit 1
fi


	rm -rf /opt/hpe/ansible >> /dev/null
	mkdir -p /opt/hpe
    mv /tmp/ansible.install.amo /opt/hpe/ansible
	rm -rf /opt/hpe/ansible/vi_service/
	rm -rf /opt/hpe/ansible/storage_management_services
