# Red Hat® Ansible® Infrastructure Provider for Hitachi Storage

The Red Hat® Ansible® Infrastructure Provider for Hitachi Storage consists of the latest versions of the ansible modules for managing Hitachi VSP storage systems 

## Supported Platforms

### Hardware requirements
- Virtual Storage Platform 5100, 5500, 5100H, 5500H, 5200, 5600, 5200H, 5600H (SAS)
    - Microcode version - 90-08-42-00/00 or later
    - Firmware version - SVOS 9.8.2 or later

- Virtual Storage Platform E1090
    - Microcode version - 93-06-42-80/00 or later
    - Firmware version - SVOS 9.8.2 or later

### Software requirements
- Red Hat Ansible - 2.9.27 or higher
- Red Hat Ansible Core - 2.15.3 or higher
- Python - 3.8 or higher

### Supported operating systems
- Oracle Enterprise Linux 8.9 or higher
- Red Hat Enterprise Linux 8.9 or higher

### Recommended Host configuration
- CPU/vCPU - 2
- Memory - 4 GB
- HardDisk - 30 GB

### Pre-requisites

- Python requests module should be installed before running any ansible module

    - To install the requests module for Python, you can use pip, the package manager for Python. Here are the steps to install it:


    - To install the `requests` module for Python, you can use pip, the package manager for Python. Here are the steps to install it:

        # Step 1: Open Terminal or Command Prompt

        Open a terminal or command prompt on your system.

        # Step 2: Run the Installation Command

        Use the following command to install the `requests` module:

        ```bash
        pip install requests
        ```

## Idempotent
- Idempotent is supported for this release

## Available Modules
### VSP Ansible modules:

        hv_cmddev.py
        hv_hg_facts.py
        hv_hg.py
        hv_lun_facts.py
        hv_lun.py
        hv_paritygroup_facts.py
        hv_resourcegroup_facts.py
        hv_resourcegroup.py
        hv_storagepool_facts.py
        hv_storagepool.py
        hv_storagereplication_facts.py
        hv_storagereplication.py
        hv_storagesystem_facts.py
        hv_storagesystem.py
        hv_troubleshooting_facts.py
        hv_ucp_facts.py
        hv_ucp.py

## Instructions
- Clone the repository
- Go to the path "ansible-infra-provider-hitachi"
- Run below command to install it using "ansible-collection"
    - Run below command to build the ansible modules
    ''' bash
    ansible-galaxy collection build 
    '''
    - once build is done run below command to install
    ''' bash
    ansible-galaxy collection install hitachi-storage-02.3.0.7.tar.gz
    '''

## License
[GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.en.html)


## Troubleshooting
- Copy the file generate_log_bundle.sh from https://github.com/hitachi-vantara/ansible-collections/storage/scripts to the machine where you are running Red Hat Ansible Provider for Hitachi
Storage

- Run your ansible playbook and look at the hitachi-ansible.log file in the /var/log/hitachi/ansible-storage directory for self troubleshooting.
- For further troubleshooting from Hitachi, run generate_log_bundle.sh,  it will generate a log bundle called Ansible_Log_Bundle_yyyymmdd_ hh_mm_ss.zip under /var/log/hitachi/ansible-storage/log_bundles
      - Create an issue at https://github.com/hitachi-vantara/ansible-infra-provider-hitachi/issues and attach the generated log bundle to the issue.
      
## Author

This collection was created in 2024 by Hitachi Vantara Ansible Team