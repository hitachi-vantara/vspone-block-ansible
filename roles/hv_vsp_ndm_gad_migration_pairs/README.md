# hv_vsp_ndm_create_gad_pairs

## Description

This Ansible role creates GAD (Global-Active Device) pairs on Hitachi VSP One Block storage systems with complete infrastructure setup. It handles the creation of hostgroups, resource groups, quorum disks, remote connections, and GAD pairs. The role provides comprehensive execution reporting and can accept input from the WWN query role for automated workflows.

## Requirements

- Ansible 2.9 or higher
- `hitachivantara.vspone_block` collection
- Access to both primary and secondary VSP One Block storage systems
- Proper network connectivity between storage systems for GAD replication
- Configured quorum disks on both storage systems

## Role Variables

### Required Parameters

```yaml
connection_info:
  address: "{{storage_address}}"
  username: "{{vault_storage_username}}"
  password: "{{vault_storage_secret}}"

secondary_connection_info:
  address: "{{secondary_storage_address}}"
  username: "{{vault_secondary_storage_username}}"
  password: "{{vault_secondary_storage_secret}}"

# World Wide Names of hosts whose volumes need migration
host_wwns:
  - "50060E801234ABCD" # Production host WWN 1
  - "50060E805678EFGH" # Production host WWN 2

# Storage ports to query (optional - if not specified, all ports are queried)
ports:
  - "CL1-A" # Primary storage port
  - "CL1-B" # Backup storage port

# GAD Infrastructure Configuration
secondary_storage_ports:
  - "CL1-A" # Secondary storage port

# Mapping of local to remote storage ports for GAD connections
remote_paths:
  - local_port: "CL1-A" # Local storage port
    remote_port: "CL1-A" # Corresponding remote storage port

# GAD Copy Configuration
secondary_storage_pool_id: 1 # Remote storage pool ID

# Status tracking file for GAD operations
gad_status_file: "~/logs/hitachivantara/ansible/vspone_block/gad_status_role_test.json"

# Batch processing configuration
hv_vsp_ndm_gad_migration_pairs_batch_gad_pair_creation_size: 2 # Number of GAD pairs to create per batch (default: 2)
```

## Infrastructure Setup Tasks

The role performs the following infrastructure setup tasks in sequence:

1. **LDEV Input Processing**: Converts `matched_ldev_ids` to `new_ldevs` format if provided
2. **RCU Hostgroup Creation**: Creates hostgroup on secondary storage with Linux host mode
3. **RCU Resource Group Creation**: Creates resource group with specified ports and hostgroups
4. **MCU Quorum Disk Registration**: Registers quorum disk on primary storage
5. **RCU Quorum Disk Registration**: Registers quorum disk on secondary storage
6. **MCU Remote Connection**: Creates remote connection from primary to secondary
7. **RCU Remote Connection**: Creates remote connection from secondary to primary
8. **GAD Pair Creation**: Creates GAD pairs for each LDEV in the list using batch processing
9. **Execution Report**: Generates comprehensive execution report and saves to file

## Batch Processing

The role implements batch processing for GAD pair creation to optimize performance and resource utilization. Instead of creating all GAD pairs simultaneously, the role processes them in smaller batches.

### Configuration

- **Variable**: `hv_vsp_ndm_gad_migration_pairs_batch_gad_pair_creation_size`
- **Default Value**: `2`
- **Description**: Specifies the number of GAD pairs to create in each batch

### How It Works

1. Groups all LDEVs by their LDEV ID
2. Divides the LDEV groups into batches based on the batch size
3. Processes each batch sequentially by including `create_gad_batch.yml`
4. Displays batch progress information showing current batch number and total pairs per batch

This approach helps manage large-scale GAD pair creations by:

- Reducing memory and resource consumption
- Providing better progress tracking
- Allowing for more controlled error handling per batch
- Preventing API throttling on storage systems

You can adjust the batch size based on your environment's requirements and storage system capabilities.

## Return Values

The role generates an execution summary and saves it to a file with the following information:

- `total_ldevs_processed`: Number of LDEVs processed
- `mcu_storage_serial`: Primary storage serial number
- `rcu_storage_serial`: Secondary storage serial number
- `copy_group_name`: GAD copy group name
- `secondary_hostgroup`: Secondary hostgroup name
- `resource_group_name`: Resource group name
- `gad_pairs_created`: Number of successfully created GAD pairs
- `gad_pairs_failed`: Number of failed GAD pair creations
- `gad_pair_details`: Detailed information about each GAD pair

## Example Usage

```yaml
---
- name: Create GAD Migration Pairs
  hosts: localhost
  gather_facts: false
  
  vars:
    connection_info:
      address: "{{storage_address}}"
      username: "{{vault_storage_username}}"
      password: "{{vault_storage_secret}}"
    
    secondary_connection_info:
      address: "{{secondary_storage_address}}"
      username: "{{vault_secondary_storage_username}}"
      password: "{{vault_secondary_storage_secret}}"
    
    host_wwns:
      - "50060E801234ABCD"
      - "50060E805678EFGH"
    
    ports:
      - "CL1-A"
      - "CL1-B"
    
    secondary_storage_ports:
      - "CL1-A"
    
    remote_paths:
      - local_port: "CL1-A"
        remote_port: "CL1-A"
    
    secondary_storage_pool_id: 1
    gad_status_file: "~/logs/hitachivantara/ansible/vspone_block/gad_status_role_test.json"
  
  roles:
    - role: hitachivantara.vspone_block.hv_vsp_ndm_gad_migration_pairs
```

## Execution Report

The role generates a detailed execution report saved to the specified file location:

```
============================================================
GAD Pair Creation Execution Report
============================================================
Execution Time: 2025-11-14T10:30:45Z
Playbook: hv_vsp_ndm_create_gad_pairs

Storage Configuration:
- MCU Storage Serial: 400001
- RCU Storage Serial: 400002
- Copy Group Name: Production_GAD_Group
- Resource Group Name: GAD_Resource_Group

Hostgroup Configuration:
- Secondary Hostgroup: Production_GAD_HG
- Secondary Port: CL1-A

Quorum Disk Configuration:
- MCU Quorum ID: 1
- RCU Quorum ID: 1

GAD Pair Results:
- Total LDEVs Processed: 3
- GAD Pairs Created Successfully: 3
- GAD Pairs Failed: 0
============================================================
```

## Error Handling

- Individual task failures don't stop the entire operation
- Comprehensive error logging and reporting
- Input validation for LDEV data
- Detailed debug output when enabled
- Execution report includes success/failure statistics

## Best Practices

1. **Test Environment**: Always test in non-production environment first
2. **Network Connectivity**: Verify bi-directional connectivity between storage systems
3. **Quorum Disks**: Ensure quorum disks are properly configured before running
4. **Resource Planning**: Verify adequate pools and resources on both systems
5. **Monitoring**: Review execution reports for any failed operations
6. **Backup Configuration**: Document current storage configuration before changes

## Troubleshooting

- Check execution report file for detailed error information
- Verify storage system connectivity and credentials
- Ensure quorum disks are accessible and properly configured
- Validate remote connection paths and WWN assignments
- Review Hitachi storage system logs for additional error details

## Author

Generated for Hitachi VSP One Block GAD pair management
