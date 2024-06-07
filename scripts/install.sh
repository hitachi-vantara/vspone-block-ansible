#!/bin/bash
# set -x
SCRIPT_PATH="${BASH_SOURCE}"
while [ -L "${SCRIPT_PATH}" ]; do
  SCRIPT_DIR="$(cd -P "$(dirname "${SCRIPT_PATH}")" >/dev/null 2>&1 && pwd)"
  SCRIPT_PATH="$(readlink "${SCRIPT_PATH}")"
  [[ ${SCRIPT_PATH} != /* ]] && SCRIPT_PATH="${SCRIPT_DIR}/${SCRIPT_PATH}"
done
SCRIPT_PATH="$(readlink -f "${SCRIPT_PATH}")"
SCRIPT_DIR="$(cd -P "$(dirname -- "${SCRIPT_PATH}")" >/dev/null 2>&1 && pwd)"
echo $SCRIPT_DIR
rpm -Uvh ${SCRIPT_DIR}/*.rpm
if [[ $? -ne 0 ]]; then
    if [[ -z $1 || $1 != "--force" ]];then
        echo "The Installation is aborted."
        return 1 || exit 1
    fi
    echo "Try to force install"
    rpm -Uvh ${SCRIPT_DIR}/*.rpm --force
    if [ $? -ne 0 ]; then
        echo "The Installation is failed."
        return 1 || exit 1
    fi
fi
fileTar=$(ls ${SCRIPT_DIR}/hitachivantara-vspone_block-[0-9.]*.tar.gz)
ansible-galaxy collection install ${fileTar} -p ~/.ansible/collections --force
if [[ $? -eq 0 ]]; then
    echo "The Installation is successful."
else
    echo "The Installation is failed."
fi
