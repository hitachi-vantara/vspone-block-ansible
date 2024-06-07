# Red Hat® Ansible® Provider for Hitachi Storage

The Red Hat® Ansible® Provider for Hitachi Storage consists of ansible modules for managing iSCSI-based Hitachi Virtual 
Storage Platform One SDS Block and Hitachi VSP storage systems.


## Supported Platforms

### Hardware requirements
- Hitachi Virtual Storage Platform One SDS Block - v1.13
  
- Virtual Storage Platform 5100, 5500, 5100H, 5500H, 5200, 5600, 5200H, 5600H (SAS)
    - Microcode version - 90-08-42-00/00 or later
    - Frimware version - SVOS 9.8.2 or later

- Virtual Storage Platform E1090
    - Microcode version - 93-06-42-80/00 or later
    - Frimware version - SVOS 9.8.2 or later



### Software requirements
- Red Hat Ansible Core - 2.14 or higher
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
### VSP One SDS Block Ansible Modules:
- Todo

### VSP Ansible modules:
- Todo



## Installation

Before using this collection, you need to install it with the Ansible Galaxy command-line tool:

```
ansible-galaxy collection install hitachivantara.vspone_block
```

```
collections:
    - hitachivantara.vspone_block.sds_block
```

```
collections:
    - hitachivantara.vspone_block.vsp
```

Note that if you install the collection from Ansible Galaxy, it will not be upgraded automatically when you upgrade the Ansible package. 

To upgrade the collection to the latest available version, run the following command:

```
ansible-galaxy collection install hitachivantara.vspone_block --upgrade
```

You can also install a specific version of the collection, for example, if you need to downgrade when something is broken in the latest version (please report an issue in this repository). Use the following syntax to install version 1.0.0:

```
ansible-galaxy collection install hitachivantara.vspone_block:==3.0.0
```

See [using Ansible collections](https://docs.ansible.com/ansible/devel/user_guide/collections_using.html) for more details.

## License
[GPL-3.0-or-later](https://www.gnu.org/licenses/gpl-3.0.en.html)

## Known issues
- Unable to create multiple ShadowImage pairs with the same P-VOL. You can create ShadowImage pairs using a different unused PVOL.

## Troubleshooting
- Todo: Implement
      
## Author

This collection was created in 2024 by Hitachi Vantara Ansible Team