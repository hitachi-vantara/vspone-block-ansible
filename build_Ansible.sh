#!/bin/bash
# Make sure these two variables are correct - May 22
Ansible_ROOT=$(pwd)
Ansible_VER=HV_Storage_Ansible-02.3.0.7

MasterProject="HivROMultiPlatformWebService/HivROMultiPlatformWebService.Ans.csproj"
#ProductionOutDir=${Ansible_ROOT}/HivROMultiPlatformWebService/HivROMultiPlatformWebService
# Build Arch
BuildArch="x64"
# Build mode: release or debug
BUILD_MODE=$1
echo "Build Mode: $BUILD_MODE"

# function PublishTarget
# {
	# echo "++++++++++++++++++++++Building vRO ++++++++++++++++++++++++++++"
	# dotnet clean ${Ansible_ROOT}/HivROMultiPlatformWebService/${MasterProject}
	# mkdir -p $ProductionOutDir/Ansible
	# if [ "$BUILD_MODE" = "Release" ]; then
        	# echo "Release Build ..."
		# dotnet publish ${Ansible_ROOT}/HivROMultiPlatformWebService/${MasterProject} -o $ProductionOutDir/Ansible -c Release > build.log
	# elif [ "$BUILD_MODE" = "Debug" ]; then 
        	# echo "Debug Build ..."
		# dotnet publish ${Ansible_ROOT}/HivROMultiPlatformWebService/${#MasterProject} -o $ProductionOutDir/Ansible -c Debug > build.log
	# fi
	# response=`echo $?`
        # if [ $response -ne 0 ]; then
	   # echo "dotnet publish command failed. please see build.log for details."
           # exit 1
        # fi

	# echo "+++++++++++++++++++Done+++++++++++++++++++++++++++++"
# }


function buildDoLogin
{
	rm -rf ${Ansible_ROOT}/GO_WORKSPACE
	mkdir -p ${Ansible_ROOT}/GO_WORKSPACE/src/doLogin
	
	# Copy doLogin.go in the source tree under goDoLogin
	/usr/bin/cp -f ${Ansible_ROOT}/goDoLogin/doLogin.go ${Ansible_ROOT}/GO_WORKSPACE/src/doLogin

	export GOPATH=${Ansible_ROOT}/GO_WORKSPACE

	echo "======================================================================================"
 	echo "Start building doLogin"
 	echo "======================================================================================"
	cd ${Ansible_ROOT}/GO_WORKSPACE/src/doLogin
	go mod init doLogin
    go mod tidy
	echo "======================================================================================"
 	echo "go build"
 	echo "======================================================================================"
	go build -buildvcs=false
	if [[ $? -ne 0 ]]; then
		echo "go build command failed. please see the log file for details."
		exit 1
	fi

        echo "======================================================================================"
 	echo "Copy to addLoginToConfigurations, .grains, and .checkLoginConfigurations"
 	echo "======================================================================================"
	/usr/bin/cp -f doLogin ${Ansible_ROOT}/goDoLogin/addLoginToConfigurations
        /usr/bin/cp -f doLogin ${Ansible_ROOT}/goDoLogin/.grains
        /usr/bin/cp -f doLogin ${Ansible_ROOT}/goDoLogin/.checkLoginConfigurations
		
        echo "======================================================================================"
 	echo "Done"
 	echo "======================================================================================"
}


function Clean
{
	echo "+++++++++++++++++++Cleaned Deployment folder+++++++++++++++++++++++"
	#for now clean is not done by pulbish we have to do manually.
	ex="`rm -rf $Ansible_ROOT/Ansible/*`"
	ex="`rm -f $Ansible_ROOT/Ansible.tar`"
	response=`echo $?`
	if [ $response -ne 0 ]; then
	   echo "cleanup command failed. please see the log file for details."
           exit 1
        fi
	
        echo "++++++++++++++++++++++++++Done +++++++++++++++++++++++++++"
}

function GenerateTar
{
	echo "++++++++++++++++++++++++++Generating Pacakge for export+++++++++++++++++"
	#will add version no later
	#ex="`tar cvfz $ProductionOutDir/vRO.tar.gz $ProductionOutDir/vRO-1.6.0`"
	ex="`tar cvf $Ansible_ROOT/Ansible.tar $Ansible_ROOT/ansible`"
        
        response=`echo $?`
        if [ $response -ne 0 ]; then
           echo "tar command failed. please see the log file for details."
           exit 1
        fi

	echo "++++++++++++++++++++++++++Done +++++++++++++++++++++++++++"
}

function CreateCollection
{
  echo "++++++++++++++++++++++++++creating collection+++++++++++++++++"
  mkdir -p ${Ansible_ROOT}/collections/ansible_collections/
  
  cd ${Ansible_ROOT}/collections/ansible_collections/
  ansible-galaxy collection init hitachi.storage --force
	
  mkdir ${Ansible_ROOT}/collections/ansible_collections/hitachi/storage/plugins/modules
  mkdir ${Ansible_ROOT}/collections/ansible_collections/hitachi/storage/plugins/module_utils

  cp -rf ${Ansible_ROOT}/hi_python_sdk/modules/collections/block/* ${Ansible_ROOT}/collections/ansible_collections/hitachi/storage/plugins/modules
  
  cp -rf ${Ansible_ROOT}/hi_python_sdk/sdk_package/collections/block/* ${Ansible_ROOT}/collections/ansible_collections/hitachi/storage/plugins/module_utils
  
  cp ${Ansible_ROOT}/ansible/collection_playbooks/galaxy-hitachi.yml ${Ansible_ROOT}/collections/ansible_collections/hitachi/storage/galaxy.yml
	
  cd ${Ansible_ROOT}/collections/ansible_collections/hitachi/storage 
  ansible-galaxy collection  build --force
	
  echo "++++++++++++++++++++++++++Done +++++++++++++++++++++++++++"
}

# function InstallPuma
# {
	# for file in ${Ansible_ROOT}/puma-* ; do
            # if [ -f "$file" ]; then
               	# echo "File exists...".
		# cp -f $file /root/rpmbuild/60EB41E9-71D5-4D5C-85E9-7E0BB76698ED.rpm
                # break;
            # else
               	# echo "File doesn't exists...".
            # fi
        # done

# }

echo  "Cleaning the build"
Clean
# echo  "publish the build"
# PublishTarget 
echo  "Generating tar file"
GenerateTar
# echo  "Build VI Service"
buildDoLogin
# buildVIService
# InstallPuma

echo Create Collection
CreateCollection

echo "Creating RPM. "

# Make sure below directories exist
echo "Making directories..."
mkdir -p /root/rpmbuild/SPECS
mkdir -p /root/rpmbuild/RPMS
mkdir -p /root/rpmbuild/SOURCES
mkdir -p /root/rpmbuild/RPMS/x86_64/release
mkdir -p /root/rpmbuild/RPMS/x86_64/debug
echo "Finished making directories..."

# Clean up
echo "Cleanin up..."
rm -rf /root/rpmbuild/${Ansible_VER}
mkdir -p /root/rpmbuild/${Ansible_VER}
rm -rf /root/rpmbuild/SPECS/*.spec
rm -rf /root/rpmbuild/RPMS/x86_64
rm -rf /root/rpmbuild/ansible
rm -rf /root/rpmbuild/sdk_package
rm -rf /root/rpmbuild/hi_python_sdk

# Blackduck issue, do not ship these jars, they only used by walkmod for java coding styling
# rm -f ${Ansible_ROOT}/Installer_Linux/Utilities/VIService-ApacheLicense/lib/javalang-compiler-2.2.12.jar
# rm -f ${Ansible_ROOT}/Installer_Linux/Utilities/VIService-ApacheLicense/lib/merger-1.0.1.jar
# rm -f ${Ansible_ROOT}/Installer_Linux/Utilities/VIService-ApacheLicense/lib/model-checker-1.1.jar
# rm -f ${Ansible_ROOT}/Installer_Linux/Utilities/VIService-ApacheLicense/lib/walkmod-core-2.3.3.jar
# rm -f ${Ansible_ROOT}/Installer_Linux/Utilities/VIService-ApacheLicense/lib/walkmod-javalang-plugin-2.6.10.jar

# rm -f ${Ansible_ROOT}/Installer/Utilities/VIService-ApacheLicense/lib/javalang-compiler-2.2.12.jar
# rm -f ${Ansible_ROOT}/Installer/Utilities/VIService-ApacheLicense/lib/merger-1.0.1.jar
# rm -f ${Ansible_ROOT}/Installer/Utilities/VIService-ApacheLicense/lib/model-checker-1.1.jar
# rm -f ${Ansible_ROOT}/Installer/Utilities/VIService-ApacheLicense/lib/walkmod-core-2.3.3.jar
# rm -f ${Ansible_ROOT}/Installer/Utilities/VIService-ApacheLicense/lib/walkmod-javalang-plugin-2.6.10.jar

echo "Finished cleanin up..."

# Spec file
cp -rf ${Ansible_ROOT}/spec/build_rpm.spec /root/rpmbuild/SPECS/
#cp -f ${Ansible_ROOT}/Scripts/hv-infra-gateway.service /root/rpmbuild/
#cp -f ${Ansible_ROOT}/Scripts/vi.service /root/rpmbuild/
#cp -f ${Ansible_ROOT}/Scripts/open_firewall_ports.sh /root/rpmbuild/
cp -f ${Ansible_ROOT}/Scripts/create_log_bundle.sh /root/rpmbuild/
cp -f ${Ansible_ROOT}/Scripts/uninstall.sh /root/rpmbuild/
cp -f ${Ansible_ROOT}/Scripts/.cleanup.sh /root/rpmbuild/
cp -f ${Ansible_ROOT}/Scripts/.cleanup4amo.sh /root/rpmbuild/
#cp -f ${Ansible_ROOT}/Scripts/crdetails.sh /root/rpmbuild/
#cp -f ${Ansible_ROOT}/Scripts/puma_external.sh /root/rpmbuild/
cp -f ${Ansible_ROOT}/logger.config /root/rpmbuild/
cp -f ${Ansible_ROOT}/messages.properties /root/rpmbuild/
cp -rf ${Ansible_ROOT}/ansible /root/rpmbuild/
cp -rf ${Ansible_ROOT}/goDoLogin /root/rpmbuild/
cp -rf ${Ansible_ROOT}/hi_python_sdk/modules /root/rpmbuild/ansible
cp -rf ${Ansible_ROOT}/hi_python_sdk/sdk_package /root/rpmbuild/
#cp -rf $Ansible_ROOT/Ansible /root/rpmbuild/
#cp -rf ${Ansible_ROOT}/Installer_Linux/Utilities/VIService-ApacheLicense /root/rpmbuild/
rm -rf /root/rpmbuild/${Ansible_VER}/*

if [[ $BUILD_MODE == "debug" ]]; then
    #Build vRO debug 
    
    if [[ -f ${Ansible_ROOT}/Ansible.tar ]]; then
        # DEBUG version
        echo "Starting build rpm for debug version..."
        cp -rf ${Ansible_ROOT}/Ansible.tar /root/rpmbuild/${Ansible_VER}
        cd /root/rpmbuild/${Ansible_VER}
        echo "unzip..."
        tar -xvf Ansible.tar
        cd /root/rpmbuild
        echo "untar..."
        tar -czvf SOURCES/${Ansible_VER}.tar.gz ${Ansible_VER}
        echo "rpmbuild..."
        rpmbuild --target=x86_64 -bb -v SPECS/build_rpm.spec
        echo "Finished build rpm for debug version..."
    else
        echo "${Ansible_ROOT}/HivROMultiPlatformWebService/HivROMultiPlatformWebService/Ansible.tar does not exist!"
    fi
else
    if [[ -f ${Ansible_ROOT}/Ansible.tar ]]; then
        # RELEASE version
        echo "Starting build rpm for release version..."
        cp -rf ${Ansible_ROOT}/Ansible.tar /root/rpmbuild/${Ansible_VER}
        cd /root/rpmbuild/${Ansible_VER}
        echo "untar..."
        tar -xvf Ansible.tar
        cd /root/rpmbuild
        echo "untar..."
        tar -czvf SOURCES/${Ansible_VER}.tar.gz ${Ansible_VER}
        rpmbuild --target=x86_64 -bb -v SPECS/build_rpm.spec
        echo "Finished build rpm for release version..."
    else
        echo "${Ansible_ROOT}/Ansible.tar does not exist!"
    fi
fi

# Create tar file 
mkdir -p  ${Ansible_ROOT}/HV_Storage_Ansible

cp -f  /root/rpmbuild/RPMS/x86_64/HV_Storage_Ansible-*.rpm  ${Ansible_ROOT}/Scripts/install.sh ${Ansible_ROOT}/Scripts/uninstall.sh ${Ansible_ROOT}/Scripts/.cleanup.sh  ${Ansible_ROOT}/Scripts/.cleanup4amo.sh ${Ansible_ROOT}/HV_Storage_Ansible

cp -f ${Ansible_ROOT}/collections/ansible_collections/hitachi/storage/hitachi-storage-2.3.0.7.tar.gz ${Ansible_ROOT}/HV_Storage_Ansible

cd $Ansible_ROOT

# change permissions on the shell scripts
chmod +x  HV_Storage_Ansible/install.sh
chmod +x  HV_Storage_Ansible/uninstall.sh
chmod +x  HV_Storage_Ansible/.cleanup.sh
chmod +x  HV_Storage_Ansible/.cleanup4amo.sh

tar -czvf  ${Ansible_VER}.tar.gz  HV_Storage_Ansible 
