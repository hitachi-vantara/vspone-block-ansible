# Hitachi Storage Modules for Red Hat Ansible

The Hitachi Storage Modules for Red Hat Ansible consists of the latest versions of the ansible modules for managing Hitachi VSP storage systems 

## Supported Platforms

### Hardware requirements
- Virtual Storage Platform F1500/VSP G1000/VSP G1500
    - Microcode version - 80-06-90_00/00 or later
    - Firmware version - SVOS 8.3 or later

- VSP G200
    - Microcode version - 83-05-44-60/00 or later
    - Firmware version - SVOS 7.4.0 or later

- VSP Gx00 (x=4/6)
    - Microcode version - 83-05-45-40/00 or later
    - Firmware version - SVOS 7.4.0 or later

- VSP Fx00 (x=4/6)
    - Microcode version - 83-05-45-40/00 or later
    - Firmware version - SVOS 7.4.0 or later

- VSP G800
    - Microcode version - 83-05-45-60/00 or later
    - Firmware version - SVOS 7.4.0 or later
      
- VSP F800
    - Microcode version - 83-05-45-60/00 or later
    - Firmware version - SVOS 7.4.0 or later
      
- VSP G350
    - Microcode version - 88-08-07-20/00 or later
    - Firmware version - SVOS 9.6.0 or later
      
- VSP F350/VSP F370/VSP F700/VSP F900
    - Microcode version - 88-08-06-20/00 or later
    - Firmware version - SVOS 9.6.0 or later
 
- VSP G370/VSP G700/VSP G900
    - Microcode version - 88-08-06-20/00 or later
    - Firmware version - SVOS 9.6.0 or later
 
- VSP 5100, 5500, 5100H, 5500H/VSP 5200, 5600, 5200H, 5600H (SAS)
    - Microcode version - 90-08-42-00/00 or later
    - Firmware version - SVOS 9.8.2 or later

- VSP 5100, 5500, 5100H, 5500H/VSP 5200, 5600, 5200H, 5600H (NVMe)
    - Microcode version - 90-08-42-00/00 or later
    - Firmware version - SVOS 9.8.2 or later

- VSP E590/VSP E790
    - Microcode version - 93-06-42-40/00 or later
    - Firmware version - SVOS 9.8.2 or later

- VSP E990
    - Microcode version - 93-06-42-60/00 or later
    - Firmware version - SVOS 9.8.2 or later

- VSP E1090
    - Microcode version - 93-06-42-80/00 or later
    - Firmware version - SVOS 9.8.2 or later

### Software requirements
- Red Hat Ansible - 2.9.27 or higher
- Red Hat Ansible Core - 2.15.3 or higher
- Python - 2.7.5 or higher
- Python Requests Library - 2.27.1 or higher
- Extra Packages for Enterprise Linux (epel-release) - 7.11 or higher
- Python pip - 20.3.4 or higher

### Supported operating systems
- Oracle Enterprise Linux 8.9 or higher
- Red Hat Enterprise Linux 8.9 or higher

### Recommended Host for Hitachi Storage Ansible Modules configuration
- CPU/vCPU - 2
- Memory - 4 GB
- HardDisk - 30 GB

### Recommended Host for Hitachi Unified API Infrastructure Gateway
4.3.0 configuration
- CPU/vCPU - 4
- Memory - 15 GB
- HardDisk - 150 GB


### See Installing the Hitachi Unified API Infrastructure Gateway 4.3.0 using OVA
in https://docs.hitachivantara.com/v/u/en-us/adapters-and-drivers/2.3.x/mk-92adptr149

### Pre-requisites

- Python requests module should be installed before running any ansible module
    
    - To install the `requests` module for Python, you can use pip, the package manager for Python. Here are the steps to install it:

        # Step 1: Open Terminal or Command Prompt

        Open a terminal or command prompt on your system.

        # Step 2: Run the Installation Command

        Use the following command to install the `requests` module:

        ```bash
        pip install requests
        ```
-  Hitachi Unified API Infrastructure Gateway
    
    - Refer to "See Installing the Hitachi Unified API Infrastructure Gateway 4.3.0 using OVA"


## Idempotent
- Idempotent is supported for this release

## Available Modules
### VSP Ansible modules:
- hv_hg_facts.py - Provides host group details
- hv_hg.py - Manages host group
- hv_lun_facts.py - Provides logical unit details
- hv_lun.py - Manages logical unit
- hv_paritygroup_facts.py - Provides parity group details
- hv_storagepool_facts.py - Provides storage pool details
- hv_storagesystem_facts.py - Provides storage system details
- hv_storagesystem.py - Manages storage system
- hv_troubleshooting_facts.py - Provides troubleshooting details
- hv_ucp_facts.py - Provides system details
- hv_ucp.py - Manages system

## Instructions
- Clone the repository
- Go to the path "vspone-ansible-modules"
- Run below command to install it using "ansible-galaxy collection"
    - Run below command to build the ansible modules
    
    ``` bash
    ansible-galaxy collection build 
    ```
    - once build is done run below command to install

    ```bash
    ansible-galaxy collection install hitachi-storage-02.3.0.tar.gz
    ```

## License
[GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.en.html)


## Troubleshooting
- locate the log bundle script path inside the /script path of the ansible collection directory
    i.e. $HOME//.ansible/collections/ansible_collections/hitachi/storage

- Run your ansible playbook and look at the hitachi-ansible.log file in the ll  directory for self troubleshooting.
- For further troubleshooting from Hitachi, run generate_log_bundle.sh,  it will generate a log bundle called Ansible_Log_Bundle_yyyymmdd_ hh_mm_ss.zip under /var/log/hitachi/ansible-storage/log_bundles
      - Create an issue at https://github.com/hitachi-vantara/vspone-ansible-modules/issues and attach the generated log bundle to the issue.
      
## Author

This collection was created in 2024 by Hitachi Vantara Ansible Team
