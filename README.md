# Hitachi Vantara VSP One Block Storage Modules for Red Hat® Ansible® 3.0.1

The Hitachi Vantara VSP One Block Storage Modules provide a comprehensive set of Ansible modules for managing Hitachi VSP One SDS Block and Hitachi VSP One series systems. These modules enable seamless integration with Red Hat Ansible, allowing users to automate storage provisioning, configuration, and management tasks.

## Changelog
View the changelog [here](Changelog).

### Hardware requirements
- VSP One SDS Block v1.14
- VSP One Block 20
- VSP One Block 24
- VSP One Block 26
- VSP One Block 28
- VSP 5100, 5500, 5100H, 5500H, 5200, 5600, 5200H, 5600H (SAS)
- VSP 5100, 5500, 5100H, 5500H, 5200, 5600, 5200H, 5600H (NVMe)
- VSP E590, E790, E990, E1090, 
- VSP F350, F370, F700, F800, F900, F1000, F1500
- VSP G350, G370, G700, G900, G1000, G1500

### Software requirements
- Red Hat Ansible Core - 2.14 to 2.16
- Python - 3.8 or higher

### Supported operating systems
- Oracle Enterprise Linux 8.9 or higher
- Red Hat Enterprise Linux 8.9 or higher

### Recommended Host configuration
- CPU/vCPU - 2
- Memory - 4 GB
- HardDisk - 30 GB

## Idempotence
- Idempotence is supported for this release

## Available Modules
### VSP One SDS Block Ansible Modules:
- hv_sds_block_chap_user_facts - Retrieves information about Hitachi SDS block storage system CHAP users.
- hv_sds_block_chap_user - Manages Hitachi SDS block storage system CHAP users.
- hv_sds_block_compute_node_facts - Retrieves information about Hitachi SDS block storage system compute nodes.
- hv_sds_block_compute_node - Manages Hitachi SDS block storage system compute nodes.
- hv_sds_block_compute_port_authentication - Manages Hitachi SDS block storage system compute port authentication mode settings.
- hv_sds_block_port_facts - Retrieves information about Hitachi SDS block storage system compute ports.
- hv_sds_block_storage_system_fact - Retrieves information about a specific Hitachi SDS block storage system.
- hv_sds_block_volume_facts - Retrieves information about Hitachi SDS block storage system volumes.
- hv_sds_block_volume - Manages Hitachi SDS block storage system volumes.

### VSP Ansible modules:
- hv_gateway_admin_password - Updates password of gateway admin on Hitachi VSP storage systems.
- hv_gateway_subscriber_fact - Retrieves information about subscriber on Hitachi VSP storage systems.
- hv_gateway_subscriber - Manages subscribers of a partner on Hitachi VSP storage systems.
- hv_hg_facts - Retrieves host group information from a specified Hitachi VSP storage system.
- hv_hg - Manages host group on Hitachi VSP storage system.
- hv_iscsi_target_facts - Retrieves information about iSCSI targets from Hitachi VSP storage systems.
- hv_iscsi_target - Manages iSCSI target on Hitachi VSP storage systems.
- hv_lun_facts - Retrieves information about logical units (LUNs) from Hitachi VSP storage systems.
- hv_lun - Manages logical units (LUNs) on Hitachi VSP storage systems.
- hv_paritygroup_facts - Retrieves information about parity groups from Hitachi VSP storage systems.
- hv_shadow_image_pair_facts - Retrieves information about shadow image pairs from Hitachi VSP storage systems.
- hv_shadow_image_pair - Manages shadow image pairs on Hitachi VSP storage systems.
- hv_snapshot_facts - Retrieves snapshot information from from Hitachi VSP storage systems.
- hv_snapshot - Manages snapshots on Hitachi VSP storage systems.
- hv_storagepool_facts - Retrieves storage pool information from Hitachi VSP storage systems.
- hv_storagesystem_facts -  Retrieves storage system information from Hitachi VSP storage systems.
- hv_storagesystem - Manages Hitachi VSP storage systems.
- hv_system_facts - Retrieves system information from Hitachi VSP storage systems.
- hv_troubleshooting_facts - Collects the log bundles for Hitachi ansible modules host and Hitachi gateway service host.
- hv_uaig_token_fact - Retrieves an API token for the Hitachi gateway service host.



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

## Troubleshooting
- Logging and troubleshooting

    
    - The log files are located at `$HOME/logs/hitachivantara/ansible/vspone_block/hv_vspone_block_modules.log`.

    - Hitachi Ansible Storage Log Collection
        In the Ansible Module installation directory, the playbooks are located at `/opt/hitachivantara/ansible/vspone_block/tools`. The name of the playbooks are:
        - `logbundle_direct_connection.yml`
        - `logbundle_gateway_connection.yml`

        *There are two log bundle generation procedures each for gateway connect and direct connect.*
        - After executing the script, the resulting ZIP archive is named: e.g.`ansible_log_bundle_2024_06_04_23_28_44.zip` This log bundle is created in the `$HOME/logs/hitachivantara/ansible/vspone_block/log_bundles/` directory.
    - Set below environment variables to change the ansible log level, log directory and log file name
        - `HV_ANSIBLE_LOG_PATH` `HV_ANSIBLE_LOG_LEVEL` `HV_ANSIBLE_LOG_FILE` 
           
## Author

*This collection was created by Hitachi Vantara® Ansible Team in 2024.*
