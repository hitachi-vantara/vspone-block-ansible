#!/bin/bash

cp -rf /opt/hitachi/ansible /tmp/ansible.install.amo

# Remove old name version if it exists
/usr/bin/rpm -e Ansible 2>/dev/null
echo "Uninstalling Storage Management Service..."
response_o=`echo $?`
/usr/bin/rpm -e HV_Storage_Ansible 2>/dev/null
response=`echo $?`

if [ $response -ne 0 ] && [ $response_o -ne 0 ] && [ "$1" != '-q' ]; then
     echo "Hitachi Ansible RPM uninstallation failed."
     exit 1
fi

# uninstall dependency server if vRO started it.
# conf_file=/var/log/hitachi/pumaconf
# if [ -f "$conf_file" ]; then
# echo "Uninstalling Storage Gateway Service..."
    # /usr/bin/rpm -e puma 2>/dev/null
        # response_o=`echo $?`
    # # delete the conf file
    # /bin/rm -rf  $conf_file
    # /bin/rm -rf  /etc/pki/ca-trust/source/anchors/puma.pem
# fi

# response=`echo $?`
# if [ $response -ne 0 ] && [ "$1" != '-q' ]; then
     # echo "dependency service uninstallation failed."
     # exit 1
# fi

	rm -rf /opt/hitachi/ansible >> /dev/null
	mkdir -p /opt/hitachi
    mv /tmp/ansible.install.amo /opt/hitachi/ansible
	#rm -rf /opt/hitachi/ansible/vi_service/
	#rm -rf /opt/hitachi/ansible/storage_management_services
