name:          HPE_Storage_Ansible
Version:       2.2.0
Release:       1%{?dist}
Summary:       The Ansible modules allow the customer to run BLOCK and FILE storage playbooks.
Vendor:        Hitachi Vantara

Group:         Adapters 
License:       hiAdapterLicense
URL:           http://www.hitachivantara.com 
Source0:       HPE_Storage_Ansible-2.2.0.tar.gz        
BuildArch:     x86_64
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
AutoReqProv:   no 

#BuildRequires:  
#Requires:       

%description
HPE Ansible RPM Package


%pre

# Check for OS distribution and minimum version
min_major_ver=1
min_minor_ver=0
major_ver=0
minor_ver=0

if [[ -f /etc/centos-release ]]; then
    if [[ -x "$(command -v lsb_release)" ]]; then
        major_ver=$(lsb_release -r | cut -f2 -d: |cut -f1 -d. | sed 's/[ \t]*//g')
        minor_ver=$(lsb_release -r | cut -f2 -d: |cut -f2 -d. | sed 's/[ \t]*//g')
    else
        major_ver=$(cat /etc/centos-release | cut -d" " -f4 | cut -d. -f1)
        minor_ver=$(cat /etc/centos-release | cut -d" " -f4 | cut -d. -f2)
    fi
fi

if [[ "$1" = "1" ]]; then
    echo "Preparing for initial installation..."
elif [[ "$1" = "2" ]]; then
    echo "Preparing for upgrading..."
    #systemctl stop hv-infra-gateway
fi


%prep
%setup -q


%build
%define debug_package %{nil}
%define __jar_repack %{nil}
%define ansible_root_dir /opt/hpe

%define ansible_dir ansible
%define vro_sub_dir %{ansible_root_dir}/%{ansible_dir}


%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/
install -d $RPM_BUILD_ROOT/opt/hpe/ansible
install -d $RPM_BUILD_ROOT/opt/hpe/ansible/support
#install -d $RPM_BUILD_ROOT/opt/hpe/ansible/storage_management_services
#install -d $RPM_BUILD_ROOT/opt/hpe/ansible/vi_service
#install -d $RPM_BUILD_ROOT/opt/hpe/ansible/module_utils
install -d $RPM_BUILD_ROOT/opt/hpe/ansible/playbooks
#install -d $RPM_BUILD_ROOT/opt/hpe/ansible/modules
#install -d $RPM_BUILD_ROOT/opt/hpe/ansible/playbooks/block
#install -d $RPM_BUILD_ROOT/opt/hpe/ansible/playbooks/file
#install -d $RPM_BUILD_ROOT/opt/hpe/ansible/modules/block
#install -d $RPM_BUILD_ROOT/opt/hpe/ansible/modules/file
install -d $RPM_BUILD_ROOT/opt/hpe/ansible/bin
install -d $RPM_BUILD_ROOT%{ansible_root_dir}
#install -d /root/rpmbuild/VIService-ApacheLicense $RPM_BUILD_ROOT/opt/hpe/ansible/vi_service 

#services
install -d $RPM_BUILD_ROOT/etc/systemd/system
install -d $RPM_BUILD_ROOT/lib/systemd/system
install -d $RPM_BUILD_ROOT%{ansible_root_dir}/ansible

#install -m 755 /root/rpmbuild/hv-infra-gateway.service $RPM_BUILD_ROOT/etc/systemd/system/hv-infra-gateway.service
#install -m 755 /root/rpmbuild/hv-infra-gateway.service $RPM_BUILD_ROOT/lib/systemd/system/hv-infra-gateway.service
#install -m 755 /root/rpmbuild/hv-infra-gateway.service /etc/systemd/system/hv-infra-gateway.service
#install -m 755 /root/rpmbuild/hv-infra-gateway.service /lib/systemd/system/hv-infra-gateway.service
#install -m 755 /root/rpmbuild/vi.service $RPM_BUILD_ROOT/etc/systemd/system/vi.service
#install -m 755 /root/rpmbuild/vi.service $RPM_BUILD_ROOT/lib/systemd/system/vi.service
#install -m 755 /root/rpmbuild/vi.service /etc/systemd/system/vi.service
#install -m 755 /root/rpmbuild/vi.service /lib/systemd/system/vi.service
#install -m 755 /root/rpmbuild/open_firewall_ports.sh $RPM_BUILD_ROOT/opt/hpe/ansible/storage_management_services
#install -m 755 /root/rpmbuild/60EB41E9-71D5-4D5C-85E9-7E0BB76698ED.rpm  $RPM_BUILD_ROOT/opt/hpe

# Copy the whole previous directory
#cp -f -a %{previous_sub_dir} $RPM_BUILD_ROOT%{ansible_root_dir}
#cp -f -a /root/rpmbuild/Ansible/*  $RPM_BUILD_ROOT/opt/hpe/ansible/storage_management_services
cp -f -a /root/rpmbuild/ansible/storage.json $RPM_BUILD_ROOT/opt/hpe/ansible/storage.json
cp -f -a /root/rpmbuild/ansible/collection_playbooks/block-hpe/* $RPM_BUILD_ROOT/opt/hpe/ansible/playbooks
rm -f                                             $RPM_BUILD_ROOT/opt/hpe/ansible/playbooks/get_support_logs.yml
cp -f -a /root/rpmbuild/ansible/collection_playbooks/block/get_support_logs.yml $RPM_BUILD_ROOT/opt/hpe/ansible/support
cp -f -a /root/rpmbuild/uninstall.sh                                 $RPM_BUILD_ROOT/opt/hpe/ansible/support

cp -f -a /root/rpmbuild/goDoLogin/.grains.sh $RPM_BUILD_ROOT/opt/hpe/ansible/bin
cp -f -a /root/rpmbuild/goDoLogin/checkLoginConfigurations.sh $RPM_BUILD_ROOT/opt/hpe/ansible/bin
cp -f -a /root/rpmbuild/goDoLogin/.grains    $RPM_BUILD_ROOT/opt/hpe/ansible/bin
cp -f -a /root/rpmbuild/goDoLogin/addLoginToConfigurations $RPM_BUILD_ROOT/opt/hpe/ansible/bin
cp -f -a /root/rpmbuild/goDoLogin/storagejson.properties $RPM_BUILD_ROOT/opt/hpe/ansible/bin
cp -f -a /root/rpmbuild/goDoLogin/storagejson.properties $RPM_BUILD_ROOT/opt/hpe/ansible/
cp -f -a /root/rpmbuild/ansible/storage-HPE.json $RPM_BUILD_ROOT/opt/hpe/ansible/storage.json
        
#cp -f -a /root/rpmbuild/sdk_package/* $RPM_BUILD_ROOT/opt/hpe/ansible/module_utils
#rm -f                                 $RPM_BUILD_ROOT/opt/hpe/ansible/module_utils/basic.py
#cp -f -a /root/rpmbuild/VIService-ApacheLicense  $RPM_BUILD_ROOT/opt/hpe/ansible/vi_service
#cp -f -a /root/rpmbuild/open_firewall_ports.sh  $RPM_BUILD_ROOT/opt/hpe/ansible/storage_management_services
cp -f -a /root/rpmbuild/logger.config $RPM_BUILD_ROOT/opt/hpe/ansible/
cp -f -a /root/rpmbuild/logger-HPE.config $RPM_BUILD_ROOT/opt/hpe/ansible/logger.config
        
cp -f -a /root/rpmbuild/messages.properties $RPM_BUILD_ROOT/opt/hpe/ansible/

cp -f -a /root/rpmbuild/goDoLogin/storagejson-HPE.properties $RPM_BUILD_ROOT/opt/hpe/ansible/storagejson.properties
cp -f -a /root/rpmbuild/goDoLogin/storagejson-HPE.properties $RPM_BUILD_ROOT/opt/hpe/ansible/bin/storagejson.properties

# remove jar files for build to resolve blackduck report issues
#rm -rf $RPM_BUILD_ROOT/opt/hpe/ansible/vi_service/VIService-ApacheLicense/lib/javalang-compiler-2.2.12.jar
#rm -rf $RPM_BUILD_ROOT/opt/hpe/ansible/vi_service/VIService-ApacheLicense/lib/merger-1.0.1.jar
#rm -rf $RPM_BUILD_ROOT/opt/hpe/ansible/vi_service/VIService-ApacheLicense/lib/model-checker-1.1.jar
#rm -rf $RPM_BUILD_ROOT/opt/hpe/ansible/vi_service/VIService-ApacheLicense/lib/walkmod-core-2.3.3.jar
#rm -rf $RPM_BUILD_ROOT/opt/hpe/ansible/vi_service/VIService-ApacheLicense/lib/walkmod-javalang-plugin-2.6.10.jar
#rm -rf $RPM_BUILD_ROOT/opt/hpe/ansible/vi_service/VIService-ApacheLicense/lib/javalang-4.7.9.jar

#rm -rf $rpm_build_root/opt/hpe/ansible/storage_management_services/configuration/hilogger-hpe.config
#rm -rf $rpm_build_root/opt/hpe/ansible/storage_management_services/configuration/ucpsettings.json
#rm -rf $rpm_build_root/opt/hpe/ansible/storage_management_services/vro_service_restart.sh
#rm -rf $rpm_build_root/opt/hpe/ansible/storage_management_services/vro_service_start.sh
#rm -rf $rpm_build_root/opt/hpe/ansible/storage_management_services/vro_service_stop.sh
#rm -rf $rpm_build_root/opt/hpe/ansible/storage_management_services/hpeappsettings.json
#rm -rf $rpm_build_root/opt/hpe/ansible/storage_management_services/hpe_version*
#rm -rf $rpm_build_root/opt/hpe/ansible/storage_management_services/version.txt

#chmod 644 $RPM_BUILD_ROOT/etc/systemd/system/hv-infra-gateway.service
#chmod 644 $RPM_BUILD_ROOT/lib/systemd/system/hv-infra-gateway.service
#chmod 644 $RPM_BUILD_ROOT/etc/systemd/system/vi.service
#chmod 644 $RPM_BUILD_ROOT/lib/systemd/system/vi.service
#chmod 755 $RPM_BUILD_ROOT/opt/hpe/ansible/storage_management_services/hv-infra-gateway_service_start.sh
#chmod 755 $RPM_BUILD_ROOT/opt/hpe/ansible/storage_management_services/hv-infra-gateway_service_stop.sh
#chmod 755 $RPM_BUILD_ROOT/opt/hpe/ansible/storage_management_services/hv-infra-gateway_service_restart.sh
#chmod 755 $RPM_BUILD_ROOT/opt/hpe/ansible/storage_management_services/open_firewall_ports.sh
#chmod 755 $RPM_BUILD_ROOT/opt/hpe/ansible/storage_management_services/puma_external.sh
chmod 755 $RPM_BUILD_ROOT/opt/hpe/ansible/bin/checkLoginConfigurations.sh

%clean
rm -rf $RPM_BUILD_ROOT

%files
%dir %{ansible_root_dir}
%defattr(-,root,root,-)
%{ansible_root_dir}/*
/opt/hpe/ansible/
#/opt/hpe/ansible/storage_management_services/

#/etc/systemd/system/hv-infra-gateway.service
#/lib/systemd/system/hv-infra-gateway.service
#/etc/systemd/system/vi.service
#/lib/systemd/system/vi.service
#/opt/hpe/ansible/vi_service/
#/opt/hpe/60EB41E9-71D5-4D5C-85E9-7E0BB76698ED.rpm

%post
# chmod 755 -R %{ansible_root_dir}

#disable firewall on http, https ports from appsettings.json and 8444
#/opt/hpe/ansible/storage_management_services/open_firewall_ports.sh

#Service Actions
#sudo /usr/bin/systemctl daemon-reload
#sudo /usr/bin/systemctl enable vi
#sudo /usr/bin/systemctl enable hv-infra-gateway
#sudo /usr/bin/systemctl start vi
#sudo /usr/bin/systemctl start hv-infra-gateway

%preun
if [[ "$1" = "0" ]]; then
    # Do some tasks prior to uninstall
    echo "Preparing uninstall..."
    #systemctl stop hv-infra-gateway
elif [[ "$1" = "1" ]]; then
    # Do some tasks prior to upgrade 
    echo "Preparing uninstall for upgrading..."
fi

if [[ -d %{ansible_root_dir}/utils/.modules ]]; then
    cp -f --no-dereference --preserve=links %{ansible_root_dir}/utils/.modules/* %{ansible_root_dir}
fi


%postun
if [[ "$1" = "0" ]]; then
    # Do some tasks after uninstallation
    echo "Perform some post-tasks for uninstallation..."
elif [[ "$1" = "1" ]]; then
    # Do some tasks after upgrade
    echo "Perform some uninstalled post-tasks for upgrading..."
fi

%changelog
