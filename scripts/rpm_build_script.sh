#!/bin/bash
# set -x
ANSIBLE_INFRASTRUCTURE_VERSION="3.0.0"
ANSIBLE_INFRASTRUCTURE_NAME="hitachi-infrastructure"
ANSIBLE_MODULES_FOLDER_NAME="HV_Storage_Ansible_Modules"
SCRIPT_PATH="${BASH_SOURCE}"
while [ -L "${SCRIPT_PATH}" ]; do
  SCRIPT_DIR="$(cd -P "$(dirname "${SCRIPT_PATH}")" >/dev/null 2>&1 && pwd)"
  SCRIPT_PATH="$(readlink "${SCRIPT_PATH}")"
  [[ ${SCRIPT_PATH} != /* ]] && SCRIPT_PATH="${SCRIPT_DIR}/${SCRIPT_PATH}"
done
SCRIPT_PATH="$(readlink -f "${SCRIPT_PATH}")"
SCRIPT_DIR="$(cd -P "$(dirname -- "${SCRIPT_PATH}")" >/dev/null 2>&1 && pwd)"
ROOT_DIR=${SCRIPT_DIR}/..
COLLECTION_DIR=${ROOT_DIR}/collection

#################### Determing platform/arch/version/etc. ##############
X_ARCH=$(uname -m| sed 's/[ \t]*//g')
#################### if not 64-bit, assume 32-bit ######################
if [[ ${X_ARCH} != x86_64 ]]; then
    echo "******************X_ARCH: ${X_ARCH}...***********************"
    X_ARCH="x86"
fi
########################################################################

display_usage() {
	echo "Format to run the script: ${0} <build_number>"
}

if [[ -z $1 ]]; then
	echo "Missing parameter"
	display_usage
	exit 1
elif [[ $1 == --help || $1 == -h ]]; then
	display_usage
	exit 1
fi

ANSIBLE_INFRASTRUCTURE_BUILD_NUMBER=$1

function CreateCollection {
  echo "++++++++++++++++++++++++++creating collection+++++++++++++++++"
  mkdir -p ${COLLECTION_DIR}
  cd ${COLLECTION_DIR}
  cp -rf ${ROOT_DIR}/plugins .
  cp -rf ${ROOT_DIR}/playbooks .
  cp -rf ${ROOT_DIR}/tools .
  cp -rf ${ROOT_DIR}/logger.config .
  cp -rf ${ROOT_DIR}/messages.properties .
  cp -rf ${ROOT_DIR}/galaxy.yml .
  sed -i "s/version:.*/version: ${ANSIBLE_INFRASTRUCTURE_VERSION}-${ANSIBLE_INFRASTRUCTURE_BUILD_NUMBER}/" galaxy.yml
  ansible-galaxy collection  build --force
  echo "++++++++++++++++++++++++++Done +++++++++++++++++++++++++++"
}
echo Remove old tar.gz files
rm -rf ${ROOT_DIR}/hitachivantara-vspone_block-[0-9.]*.tar.gz

echo Create Collection
CreateCollection

echo "Buidling RPM file"

#sh ${ROOT_DIR}/scripts/RPM_build_script.sh $1

SPEC_DIR=${ROOT_DIR}/spec
PLAYBOOK_DIR=${ROOT_DIR}/playbooks
BIN_DIR=${ROOT_DIR}/bin

CFG="Release"

rm -rf /root/rpmbuild/SOURCES/* || true
rm -rf /root/rpmbuild/BUILD/* || true
rm -rf /root/rpmbuild/BUILDROOT/* || true
rm -rf /root/rpmbuild/RPMS/* || true
cd /root/rpmbuild/
cp -rf ${SPEC_DIR}/build_rpm.spec SPECS/

rm -rf ${ANSIBLE_INFRASTRUCTURE_NAME}-${ANSIBLE_INFRASTRUCTURE_VERSION}
mkdir ${ANSIBLE_INFRASTRUCTURE_NAME}-${ANSIBLE_INFRASTRUCTURE_VERSION}
mkdir ${ANSIBLE_INFRASTRUCTURE_NAME}-${ANSIBLE_INFRASTRUCTURE_VERSION}/sample
cd ${ANSIBLE_INFRASTRUCTURE_NAME}-${ANSIBLE_INFRASTRUCTURE_VERSION}
cp -rf ${PLAYBOOK_DIR} sample/
cp -rf ${ROOT_DIR}/tools .
cp -rf ${ROOT_DIR}/version.txt .
cp -rf ${ROOT_DIR}/logger.config .

cd ../
tar czf SOURCES/${ANSIBLE_INFRASTRUCTURE_NAME}-${ANSIBLE_INFRASTRUCTURE_VERSION}.tar.gz ${ANSIBLE_INFRASTRUCTURE_NAME}-${ANSIBLE_INFRASTRUCTURE_VERSION}

rpmbuild --target=${X_ARCH} -bb --define '_BUILD Release' --define "_ANSIBLE_INFRASTRUCTURE_VERSION ${ANSIBLE_INFRASTRUCTURE_VERSION}" --define "_BUILD_NUMBER $1" -v SPECS/build_rpm.spec

if [[ ! -d ${BIN_DIR} ]]; then
	mkdir -p ${BIN_DIR}
fi
rm -rf ${BIN_DIR}/*
cd ${BIN_DIR}
mkdir -p ${ANSIBLE_MODULES_FOLDER_NAME}
cd ${ANSIBLE_MODULES_FOLDER_NAME}
echo "CHECK if all the files including generated rpm exists or not before copying into tar.gz file"
ls -lrtha 
cp -rf ${SCRIPT_DIR}/readme.md .
cp -rf ${SCRIPT_DIR}/install.sh .
cp -rf ${SCRIPT_DIR}/uninstall.sh .
cp -rf /root/rpmbuild/RPMS/${X_ARCH}/${ANSIBLE_INFRASTRUCTURE_NAME}-${ANSIBLE_INFRASTRUCTURE_VERSION}-$1.${X_ARCH}.rpm .
mv ${COLLECTION_DIR}/hitachivantara-vspone_block-${ANSIBLE_INFRASTRUCTURE_VERSION}-$1.tar.gz .
cd ${BIN_DIR}
tar czf ${ANSIBLE_INFRASTRUCTURE_NAME}-${ANSIBLE_INFRASTRUCTURE_VERSION}-$1.tar.gz ${ANSIBLE_MODULES_FOLDER_NAME}
rm -rf ${COLLECTION_DIR}