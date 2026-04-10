# hv_vsp_create_primary_and_secondary_diskless_quorum_disk

An Ansible role for creating diskless quorum disks between primary and secondary Hitachi VSP One Block storage systems.

## Overview

This role handles the complete workflow for creating diskless quorum disk configurations for GAD (Global Active Device) pairs across primary and secondary storage systems. Unlike the external LDEV-based quorum disk role, this role creates a direct quorum disk relationship between two storage systems without requiring an external storage LDEV. The role:

1. Retrieves storage system information from both primary and secondary storage
2. Automatically determines storage types (R9, R8, RH20ETP, M8) based on model information
3. Validates quorum disk ID availability across both storage systems
4. Creates diskless quorum disks on both primary and secondary storage systems using remote storage serial numbers
5. Generates a detailed report of the quorum disk configuration

## Requirements

- Ansible 2.9+
- `hitachivantara.vspone_block` collection (version 1.0.0 or later)
- Valid connection credentials for VSP One Block storage systems
- Proper permissions for quorum disk management operations
- Network connectivity between primary and secondary storage systems

## Dependencies

No external role dependencies. Requires `hitachivantara.vspone_block` collection.

## Role Variables

### Mandatory Variables

#### hv_vsp_create_primary_and_secondary_diskless_quorum_disk_primary_storage_connection

Connection information for the primary storage.

```yaml
hv_vsp_create_primary_and_secondary_diskless_quorum_disk_primary_storage_connection:
  address: "192.168.1.100"
  username: "admin"
  password: "password"
```

#### hv_vsp_create_primary_and_secondary_diskless_quorum_disk_secondary_storage_connection

Connection information for the secondary storage.

```yaml
hv_vsp_create_primary_and_secondary_diskless_quorum_disk_secondary_storage_connection:
  address: "192.168.1.101"
  username: "admin"
  password: "password"
```

### Optional Variables

#### hv_vsp_create_primary_and_secondary_diskless_quorum_disk_quorum_disk_id

Quorum disk ID (0-31). If not specified, the role will automatically select the first available ID that is free on both storage systems. If specified, the role will validate that the ID is available on both systems and return an error if it's already in use.

```yaml
hv_vsp_create_primary_and_secondary_diskless_quorum_disk_quorum_disk_id: 1
```

Default: `null` (automatically selects first available ID)

## Example Playbook

```yaml
---
- name: Create diskless quorum disk between primary and secondary storage
  hosts: localhost
  gather_facts: false
  roles:
    - role: hv_vsp_create_primary_and_secondary_diskless_quorum_disk
      vars:
        hv_vsp_create_primary_and_secondary_diskless_quorum_disk_primary_storage_connection:
          address: "192.168.1.100"
          username: "admin"
          password: "{{ vault_primary_password }}"
        hv_vsp_create_primary_and_secondary_diskless_quorum_disk_secondary_storage_connection:
          address: "192.168.1.101"
          username: "admin"
          password: "{{ vault_secondary_password }}"
        hv_vsp_create_primary_and_secondary_diskless_quorum_disk_quorum_disk_id: 1
```

## What the Role Does

1. **Gather Storage Information**: Retrieves facts from primary and secondary storage systems including model and serial number
2. **Determine Storage Types**: Automatically identifies storage types (R9, R8, RH20ETP, M8) based on model information for proper quorum disk configuration
3. **Validate Quorum IDs**: Queries existing quorum disks on both systems and identifies available quorum disk IDs (0-31)
4. **Validate User Input**: If a specific quorum disk ID is provided, validates that it's available on both systems
5. **Select Quorum ID**: Automatically selects the first available common quorum disk ID if none is specified
6. **Create Quorum Disks**: Registers diskless quorum disks on both primary and secondary storage using remote storage serial numbers and storage types
7. **Generate Report**: Provides a detailed report including quorum disk ID, storage serials, and creation results

## Key Differences from External LDEV Quorum Role

This role (`hv_vsp_create_primary_and_secondary_diskless_quorum_disk`) differs from the external LDEV-based quorum role (`hv_vsp_create_primary_and_secondary_quorum_disk`) in the following ways:

- **No External Storage Required**: Does not require a third storage system to provide the quorum disk LDEV
- **Direct Storage Communication**: Creates a direct quorum disk relationship between primary and secondary storage using remote storage serial numbers
- **Simplified Configuration**: Only requires connection information for the two storage systems involved
- **No LDEV/Host Group Management**: Does not create or manage external LDEVs, host groups, or external volume mappings

## License

Proprietary

## Author Information

Hitachi Vantara
