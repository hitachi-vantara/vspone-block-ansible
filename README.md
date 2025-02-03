# Hitachi Vantara VSP One Block Storage Modules for Red Hat® Ansible®

The Hitachi Vantara VSP One Block Storage Modules provide a comprehensive set of Ansible modules for managing Hitachi VSP One SDS Block and Hitachi VSP One series systems. These modules enable seamless integration with Red Hat Ansible, allowing users to automate storage provisioning, configuration, and management tasks.

## Getting started
The following steps are required to get the VSP One Block Storage Modules ready to execute your first playbook.

### Prerequisites

#### Mandatory software dependencies
- Red Hat Ansible Core - V2.13.9, V2.14, V2.15, V2.16, V2.17
- Python - V3.8 or higher

#### Optional software dependency
- Hitachi UAI Gateway - V4.7

### Supported storage controllers

| VSP One SDS Block Versions | VSP One Series | VSP 5000 Series (SAS/NVMe) | VSP E Series | VSP F Series | VSP G Series |
| -------------------------- | -------------- | --------------- | ------------ | ------------ | ------------ |
| V1.13, V1.14               | Block 20, Block 24, Block 26, Block 28 | 5100, 5500, 5100H, 5500H, 5200, 5600, 5200H, 5600H | E590, E790, E990, E1090 | F350, F370, F700, F800, F900, F1000, F1500 | G350, G370, G700, G900, G1000, G1500 |

### Install modules from Ansible Galaxy
To install and verify the latest version of the modules follow these steps.
1. Install: `ansible-galaxy collection install hitachivantara.vspone_block`
2. Verify: `ansible-galaxy collection verify hitachivantara.vspone_block`

**Example output from verification**
```
user@system dev % ansible-galaxy collection verify hitachivantara.vspone_block
Downloading https://galaxy.ansible.com/api/v3/plugin/ansible/content/published/collections/artifacts/hitachivantara-vspone_block-3.1.118.tar.gz to /Users/mihay/.ansible/tmp/ansible-local-26544jolxqc3m/tmp_dt2t_5s/hitachivantara-vspone_block-3.1.118-ht7b78_a
Verifying 'hitachivantara.vspone_block:3.1.118'.
Installed collection found at '/Users/user/.ansible/collections/ansible_collections/hitachivantara/vspone_block'
MANIFEST.json hash: 393f2b53ccfeef286516c219c72702f3d82e723597149f2ea9a5d6c6158c5655
Successfully verified that checksums for 'hitachivantara.vspone_block:3.1.118' match the remote collection.
``` 

### Upgrade modules
If the collection was installed from Ansible Galaxy, to upgrade the collection to the latest available version, rerun the install with the **--upgrade** switch: `ansible-galaxy collection install hitachivantara.vspone_block --upgrade`


## External documentation

- [User guide](https://docs.hitachivantara.com/v/u/en-us/adapters-and-drivers/3.1.0/rn-92adptr150).
- [Release notes](https://docs.hitachivantara.com/v/u/en-us/adapters-and-drivers/3.1.0/rn-92adptr150)
- [Using Ansible collections](https://docs.ansible.com/ansible/devel/user_guide/collections_using.html) for more details.

## Module manifest
A listing of all available modules with descriptions can be found in the [module manifest](docs/ModuleManifest.md).

## Contributing
Contribution guidelines and procedures are kept in [./docs/CONTRIBUTING](docs/CONTRIBUTING.md).
           
## Author(s)

*This collection was created by Hitachi Vantara® Ansible Team in 2024.*
