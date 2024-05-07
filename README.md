# Red Hat® Ansible® Provider for Hitachi Storage

The Red Hat® Ansible® Provider for Hitachi Storage consists of the latest versions of the ansible modules for managing Hitachi VSP storage systems 
and Hitachi Virtual Storage Platform One SDS Block storage systems

## Supported Platforms

### Hardware requirements
- Virtual Storage Platform 5100, 5500, 5100H, 5500H, 5200, 5600, 5200H, 5600H (SAS)
    - Microcode version - 90-08-42-00/00 or later
    - Frimware version - SVOS 9.8.2 or later

- Virtual Storage Platform E1090
    - Microcode version - 93-06-42-80/00 or later
    - Frimware version - SVOS 9.8.2 or later

- Hitachi Virtual Storage Platform One SDS Block - v1.13

### Software requirements
- Red Hat Ansible - 2.9.27 or higher
- Red Hat Ansible Core - 2.15.3 or higher
- Python - 3.8 or higher

### Supported operating systems
- Oracle Enterprise Linux 8.9 or higher
- Red Hat Enterprise Linux 8.9 or higher

### Recomended Host configuration
- CPU/vCPU - 2
- Memory - 4 GB
- HardDisk - 30 GB

## Idempotency
- Idempotency is not supported for this release

## Available Modules
### VSP Ansible modules:
- hitachi_block_addChap - Adds a CHAP user on an iSCSI port
- hitachi_block_addHost - Adds the iSCSI name of the host on the initiator side for the iSCSI target of the specified port
- hitachi_block_addlun - Adds LUNs to an iSCSI target
- hitachi_block_changeNickName - Changes the nickname of an iSCSI name
- hitachi_block_createhg - Creates an iSCSI target
- hitachi_block_createSI - Creates a ShadowImage pair
- hitachi_block_createTI_with_gen - Creates a Thin Image pair with an autosplit option
- hitachi_block_createTI - Creates a Thin Image pair
- hitachi_block_createVol - Creates a volume
- hitachi_block_deleteHost - Deletes an iSCSI name from an iSCSI target
- hitachi_block_deleteVol - Deletes a volume
- hitachi_block_restoreTI - Restores a Thin Image pair
- hitachi_block_resyncSI - Resyncs a ShadowImage pair
- hitachi_block_resyncTI_oldest - Resyncs the oldest Thin Image pair
- hitachi_block_resyncTI - Resyncs a Thin Image pair
- hitachi_block_splitSI - Splits a ShadowImage pair
- hitachi_block_splitTI - Splits a Thin Image pair

### VSP One SDS Block Ansible Modules:
- add_chapuser_computeport - Adds a CHAP user to a compute port
- add_computenode - Adds a compute node
- add_hbas - Adds an iSCSI name to a compute node
- add_paths - Adds paths to a compute node 
- attach_volume - Attaches a volume to a compute node
- create_chapuser - Creates a CHAP user
- create_volume - Creates a volume
- delete_computenode - Deletes a compute node
- delete_tenant - Deletes a compute node and all volumes attached to that compute node
- delete_volume - Deletes a volume
- expand_volume - Expands a volume

## Instructions
- Create a folder /opt/hitachi/ansible-storage
- Copy the content of https://github.com/hitachi-vantara/ansible-collections/storage-direct/plugins/modules to  /opt/hitachi/ansible-storage/modules
- Copy the content of https://github.com/hitachi-vantara/ansible-collections/storage-direct/plugins/module_utils to  /opt/hitachi/ansible-storage/module_utils
- Add the following two lines to .bashrc files which is in user home directory:
    export ANSIBLE_LIBRARY=/opt/hitachi/ansible-storage/modules
    export ANSIBLE_MODULE_UTILS=/opt/hitachi/ansible-storage/module_utils
- run command: source  ~/.bashrc

## License
[GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.en.html)


## Troubleshotting
- Copy the file generate_log_bundle.sh from https://github.com/hitachi-vantara/ansible-collections/storage-direct/scripts to the machine where you are running Red Hat Ansible Provider for Hitachi
Storage
- Enable debug mode by running the following command:
  - export ANSIBLE_LOG_LEVEL=”DEBUG”
- Run your ansible playbook and look at the hitachi-ansible.log file in the /var/log/hitachi/ansible-storage directory for self troubleshooting.
- For further troubleshooting from Hitachi, run generate_log_bundle.sh,  it will generate a log bundle called Ansible_Log_Bundle_yyyymmdd_ hh_mm_ss.zip under /var/log/hitachi/ansible-storage/log_bundles
      - Create an issue at https://github.com/hitachi-vantara/ansible-collections/storage-direct/issues and attach the genareted log bundle to the issue.
      
## Author

This collection was created in 2024 by Hitachi Vantara Ansible Team