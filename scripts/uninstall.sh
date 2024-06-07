#!/bin/bash
# set -x
if [[ -z $1 || $1 != "--force" ]];then
    read -p "Are you sure you want to uninstall the package? (Y/N): " confirm
    if [[ ! $confirm == [yY] && ! $confirm == [yY][eE][sS] ]];then
        echo "The Uninstallation is aborted."
        return 1
    fi
fi
rpm -evh hitachi-infrastructure
if [ $? -ne 0 ]; then
    echo "The Uninstallation is failed."
    return 1
fi
rm -rf ~/.ansible/collections/ansible_collections/hitachivantara/vspone_block/
echo "The Uninstallation is successful."
