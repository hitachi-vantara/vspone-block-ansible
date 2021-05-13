#!/bin/bash

#gateway_server_install_only=0
#gateway_server_install_exclude=0
#storage_mgmt_server_install_exclude=0
ansible_modules_only=0
full_install=1
is_source_subshell=0


# signal handler
control_c () {
  echo -e "Caught Ctrl+C\n Exiting program. \n Your Hitachi Ansible installation may be in an unstable state.\n".
  /bin/rm -rf $rpm_file
  if [[ "$is_source_subshell" -eq 1 ]]; then
    trap - SIGINT
    return 1
  else
    exit 1
  fi
}

function my_function() {
  #echo we are running using source
  is_source_subshell=1
}

function is_subshell() {
  if [[ "$1" = "-bash" ]]; then
    return 0
  fi
  return 1
}

is_subshell $0 && my_function

usage()
{
  echo "Invalid option"
}

configAMOnly()
{
  #gateway_server_install_exclude=1
  #storage_mgmt_server_install_exclude=1
  ansible_modules_only=1
  full_install=0
  echo "installing Ansible Modules only"  
}

configGSOnly()
{
  #gateway_server_install_only=1
  #storage_mgmt_server_install_exclude=1
  full_install=0
}

while [ "$1" != "" ]; do
    case $1 in
        -ogs | --gateway_server_only )           shift
                                        configGSOnly
                                ;;
        -ngs | --ansible_modules_only ) configAMOnly
                                ;;
        * )                     usage
                                if [[ "$is_source_subshell" -eq 0 ]]; then
                                  exit 1
                                else
                                  return 1
                                fi
    esac
    shift
done

#echo $gateway_server_install_only
#echo $gateway_server_install_exclude
#echo $storage_mgmt_server_install_exclude
#echo $ansible_modules_only

trap control_c SIGINT

# doPuma=1
# if [[ "$gateway_server_install_exclude" -eq 1 ]]; then
  # #echo exclude the Gateway Server 
  # doPuma=0
# fi

#doMgmtService=1
doAnsibleModule=1
# if [[ "$gateway_server_install_only" -eq 1 ]]; then
  # #echo installing the Gateway Server only
  # doAnsibleModule=0
  # doMgmtService=0
# fi

# Install dependency RPM
#rpm_file="/opt/hitachi/60EB41E9-71D5-4D5C-85E9-7E0BB76698ED.rpm"

# Function to compare Java versions https://stackoverflow.com/a/24067243/9761984
function version_gt() { test "$(printf '%s\n' "$@" | sort -V | head -n 1)" != "$1"; }

# Install Pip SCP library
check_scp_install()
{
        if type -p pip && pip list | fgrep -w scp ; then
            echo "Python SCP library is already installed."
        else
                read -p "Python SCP library is required. Do you want to install Python SCP library? [y/Y] " -n 1 -r
                echo    # (optional) move to a new line
                if [[ $REPLY =~ ^[Yy]$ ]]; then

                        echo "Installing pip..."
                        yum install -y  python-pip
                        pip install scp
                else
                    echo "Please install Python SCP library and rerun install.sh."
		            if [[ "$is_source_subshell" -eq 0 ]]; then
		              exit 1
		            else
		              return 1
		            fi
                fi
        fi
}

# Install Pip Requests library
check_requests_install()
{
        if type -p pip && pip list | fgrep -w requests ; then
            echo "Python Requests library is already installed."
        else
                read -p "Python Requests library is required. Do you want to install Python Requests library? [y/Y] " -n 1 -r
                echo    # (optional) move to a new line
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                		# check_scp_install should have already installed pip
                        pip install requests
                else
                    echo "Please install Python Requests library and rerun install.sh."
		            if [[ "$is_source_subshell" -eq 0 ]]; then
		              exit 1
		            else
		              return 1
		            fi  
                fi
        fi
}

# Install dependency server
###################################################################################33
## Installation execution starts here
###################################################################################33

if [[ "$is_source_subshell" -eq 0 ]]; then
              echo Please use \"source install.sh\"
              exit 1
fi

if [[ "$ansible_modules_only" -eq 0 ]]; then	
	# check if Java is installed
	# no need to check if ansible_modules_only (AMO)
    response=`echo $?`
    if [ $response -ne 0 ]; then
      return 1
    fi
fi

# check for previous version of the management service
if rpm -qa | grep -qw '\(HV_Storage_\)\?Ansible'; then

    if [[ "$ansible_modules_only" -eq 1 ]]; then
      echo "please uninstall management service first before installing Ansible Modules only"
      return 1	
    fi
    
	echo "Uninstalling previous version..."
	yes | ./uninstall.sh -q
fi

if [[ "$ansible_modules_only" -eq 0 ]]; then
	# check if net-tools package is installed on the system
	if ! rpm -qa | grep -qw net-tools; then
	    yum install -y net-tools
	fi
fi	

if [[ "$ansible_modules_only" -eq 1 ]]; then
	# Back up the storage.json config file
	config_file="/opt/hitachi/ansible/storage.json"
	if [ -f "$config_file" ]; then
	   #ls -l "$config_file"
	   cp -f "${config_file}" "${config_file}.bak"
	fi
fi	

# Install C# storage gateway webservice RPM for all installation type,
# since we need all the files to be installed
# if [[ "$storage_mgmt_server_install_exclude" -eq 1 ]]; then
    # ## for ams/puma only, don't show that we extracting everything
  	# /usr/bin/rpm -Uvh HV_Storage_Ansible-02.1.0-1.el7.x86_64.rpm > /dev/null 2>&1
# else
  	/usr/bin/rpm -Uvh HV_Storage_Ansible-02.2.0-1.el7.x86_64.rpm 
# fi

response=`echo $?`
if [ $response -ne 0 ]; then
        echo "Ansible RPM installation failed."
	    if [[ "$is_source_subshell" -eq 0 ]]; then
	      exit 1
	    else
	      return 1
	    fi
fi

if [[ "$ansible_modules_only" -eq 1 ]]; then
	# abort if puma is installed
	PROCESS_NUM=$(ps -ef | grep "puma" | grep -v "grep" | wc -l)
	#echo $PROCESS_NUM
	if [ "$PROCESS_NUM" -eq "0" ]; then
		#echo puma is not installed, continue
		echo 
	else
	    echo "Gateway server is installed, please run the uninstall then try again."
	    return 1
	fi
fi	

if [[ "$full_install" -eq 1 ]]; then
	echo "Installation: Full" >> /opt/hitachi/ansible/playbooks/version.txt
fi 

if [[ "$ansible_modules_only" -eq 1 ]]; then
	echo "Installation: Ansible Modules only" >> /opt/hitachi/ansible/playbooks/version.txt
	yes | ./.cleanup4amo.sh -q >> /dev/null
fi 

if [[ "$doAnsibleModule" -eq 1 ]]; then	

	# Replace the config file
	config_file="/opt/hitachi/ansible/storage.json"
	if [ -f "${config_file}.bak" ]; then
	  echo "${config_file}.bak" is your most recently used storage.json.
	  echo Do you want to overwrite the newly installed storage.json with it,
	  cp -f "${config_file}.bak" "$config_file"
	fi		
	

    export PATH=$PATH:/opt/hitachi/ansible/bin
	export HV_STORAGE_ANSIBLE_PROFILE=/opt/hitachi/ansible/storage.json
	export HV_STORAGE_ANSIBLE_LOG_PATH=/var/log
	export HV_STORAGE_ANSIBLE_PATH=/opt/hitachi/ansible
	export HV_STORAGE_MGMT_VAR_LOG_PATH=/var/log
	export HV_STORAGE_MGMT_PATH=/opt/hitachi/ansible
	export HV_STORAGE_JSON_PROPERTIES_FILE=/opt/hitachi/ansible/storagejson.properties
	#export ANSIBLE_LIBRARY=/opt/hitachi/ansible/modules/block:/opt/hitachi/ansible/modules/file
	#export ANSIBLE_MODULE_UTILS=/opt/hitachi/ansible/module_utils/
	if [ -f /etc/profile.d/custom.sh ]; then
	    #echo "file exists."
	    #echo 'export PATH=$PATH:/opt/hitachi/ansible/bin' >>/etc/profile.d/custom.sh
	   # grep "ansible/modules/block" /etc/profile.d/custom.sh
	    #if [ $? -ne 0 ]; then
	        #echo "export ANSIBLE_LIBRARY=/opt/hitachi/ansible/modules/block:/opt/hitachi/ansible/modules/file" >>/etc/profile.d/custom.sh
	    #fi
	    grep "ansible/module_utils" /etc/profile.d/custom.sh
	    if [ $? -ne 0 ]; then
	        echo "export ANSIBLE_MODULE_UTILS=/opt/hitachi/ansible/module_utils/" >>/etc/profile.d/custom.sh
	    fi
	    grep "HV_STORAGE_ANSIBLE_PROFILE" /etc/profile.d/custom.sh
	    if [ $? -ne 0 ]; then
	        echo "export HV_STORAGE_ANSIBLE_PROFILE=/opt/hitachi/ansible/storage.json"  >>/etc/profile.d/custom.sh		
	    fi
	    grep "HV_STORAGE_ANSIBLE_PATH" /etc/profile.d/custom.sh
	    if [ $? -ne 0 ]; then
	        echo "export HV_STORAGE_ANSIBLE_PATH=/opt/hitachi/ansible"  >>/etc/profile.d/custom.sh		
	        echo "export HV_STORAGE_ANSIBLE_LOG_PATH=/var/log"  >>/etc/profile.d/custom.sh		
	    fi
		grep "HV_STORAGE_JSON_PROPERTIES_FILE" /etc/profile.d/custom.sh
		if [ $? -ne 0 ]; then
	       export HV_STORAGE_JSON_PROPERTIES_FILE=/opt/hitachi/ansible/storagejson.properties  >>/etc/profile.d/custom.sh		
	    fi
	    grep "HV_STORAGE_MGMT_PATH" /etc/profile.d/custom.sh
	    if [ $? -ne 0 ]; then
	        echo "export HV_STORAGE_MGMT_PATH=/opt/hitachi/ansible"  >>/etc/profile.d/custom.sh		
	        echo "export HV_STORAGE_MGMT_VAR_LOG_PATH=/var/log"  >>/etc/profile.d/custom.sh		
	    fi
	else
	    #echo "export ANSIBLE_MODULE_UTILS=/opt/hitachi/ansible/module_utils/"  >/etc/profile.d/custom.sh
	    #echo "export ANSIBLE_LIBRARY=/opt/hitachi/ansible/modules/block:/opt/hitachi/ansible/modules/file" >>/etc/profile.d/custom.sh
	    echo "export HV_STORAGE_ANSIBLE_PATH=/opt/hitachi/ansible"  >>/etc/profile.d/custom.sh		
	    echo "export HV_STORAGE_ANSIBLE_LOG_PATH=/var/log"  >>/etc/profile.d/custom.sh		
	    echo "export HV_STORAGE_ANSIBLE_PROFILE=/opt/hitachi/ansible/storage.json"  >>/etc/profile.d/custom.sh		
	    echo 'export PATH=$PATH:/opt/hitachi/ansible/bin' >>/etc/profile.d/custom.sh
        echo "export HV_STORAGE_MGMT_PATH=/opt/hitachi/ansible"  >>/etc/profile.d/custom.sh		
	    echo "export HV_STORAGE_MGMT_VAR_LOG_PATH=/var/log"  >>/etc/profile.d/custom.sh	
		echo " export HV_STORAGE_JSON_PROPERTIES_FILE=/opt/hitachi/ansible/storagejson.properties"  >>/etc/profile.d/custom.sh			
	fi
	
	   #need to mkdir for the -ngs case
       mkdir -p /var/log/hitachi
       mkdir -p /var/log/hitachi/ansible
       mkdir -p /var/log/hitachi/ansible/support
	
			
fi

if [[ "$is_source_subshell" -eq 1 ]]; then
    trap - SIGINT
    return 0
fi

