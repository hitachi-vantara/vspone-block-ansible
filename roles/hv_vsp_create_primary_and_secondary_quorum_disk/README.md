# hv_vsp_create_primary_and_secondary_quorum_disk

An Ansible role for creating primary and secondary quorum disks on Hitachi VSP One Block storage systems.

## Overview

This role handles the complete workflow for creating and configuring quorum disks for GAD (Global Active Device) pairs across primary and secondary storage systems. The role:

1. Creates an LDEV on the external storage (quorum disk storage provider)
2. Presents the LDEV to specified host groups on the external storage
3. Creates external volumes on both primary and secondary storage that map to the quorum disk LDEV
4. Creates and registers quorum disks on both primary and secondary storage systems
5. Validates quorum disk ID availability across both storage systems

## Requirements

- Ansible 2.9+
- `hitachivantara.vspone_block` collection (version 1.0.0 or later)
- Valid connection credentials for VSP One Block storage systems
- Proper permissions for quorum disk management operations

## Dependencies

No external role dependencies. Requires `hitachivantara.vspone_block` collection.

## Role Variables

### Mandatory Variables

#### hv_vsp_create_primary_and_secondary_quorum_disk_primary_storage_connection

Connection information for the primary storage.

```yaml
hv_vsp_create_primary_and_secondary_quorum_disk_primary_storage_connection:
  address: "192.168.1.100"
  username: "admin"
  password: "password"
```

#### hv_vsp_create_primary_and_secondary_quorum_disk_secondary_storage_connection

Connection information for the secondary storage.

```yaml
hv_vsp_create_primary_and_secondary_quorum_disk_secondary_storage_connection:
  address: "192.168.1.101"
  username: "admin"
  password: "password"
```

#### hv_vsp_create_primary_and_secondary_quorum_disk_quorum_disk_storage_connection

Connection information for the storage provider for the quorum disk.

```yaml
hv_vsp_create_primary_and_secondary_quorum_disk_quorum_disk_storage_connection:
  address: "192.168.1.102"
  username: "admin"
  password: "password"
```

#### hv_vsp_create_primary_and_secondary_quorum_disk_quorum_disk_storage_host_groups

Host groups of the storage provider for the quorum disk (list of host group input objects). Each host group must specify `host_group_name` and `port`.

```yaml
hv_vsp_create_primary_and_secondary_quorum_disk_quorum_disk_storage_host_groups:
  - host_group_name: "HG_001"
    port: "CL1-A"
  - host_group_name: "HG_002"
    port: "CL1-B"
```

### Optional Variables

#### hv_vsp_create_primary_and_secondary_quorum_disk_quorum_disk_id

Quorum disk ID (0-31). If not specified, the role will automatically select the first available ID. Returns error if the specified quorum ID is already in use on either storage system.

```yaml
hv_vsp_create_primary_and_secondary_quorum_disk_quorum_disk_id: 1
```

Default: `null`

#### hv_vsp_create_primary_and_secondary_quorum_disk_primary_ldev_id

LDEV ID for the external volume in the primary storage. If not specified, the role will automatically select a free LDEV ID.

```yaml
hv_vsp_create_primary_and_secondary_quorum_disk_primary_ldev_id: 1000
```

Default: `null`

#### hv_vsp_create_primary_and_secondary_quorum_disk_secondary_ldev_id

LDEV ID for the external volume in the secondary storage. If not specified, the role will automatically select a free LDEV ID.

```yaml
hv_vsp_create_primary_and_secondary_quorum_disk_secondary_ldev_id: 2000
```

Default: `null`

#### hv_vsp_create_primary_and_secondary_quorum_disk_external_pool_id

Pool ID on the quorum disk storage provider where the LDEV will be created.

```yaml
hv_vsp_create_primary_and_secondary_quorum_disk_external_pool_id: 0
```

Default: `0`

#### hv_vsp_create_primary_and_secondary_quorum_disk_quorum_disk_size

Size of the quorum disk LDEV to create on the external storage.

```yaml
hv_vsp_create_primary_and_secondary_quorum_disk_quorum_disk_size: "12300MB"
```

Default: `"12300MB"`

#### hv_vsp_create_primary_and_secondary_quorum_disk_quorum_disk_ldev_id

LDEV ID for the quorum disk on the external storage. If not provided, a free LDEV ID will be used.

```yaml
hv_vsp_create_primary_and_secondary_quorum_disk_quorum_disk_ldev_id: 1
```

Default: `1`

#### hv_vsp_create_primary_and_secondary_quorum_disk_quorum_disk_ldev_capacity_savings

Specifies the capacity savings method for the quorum disk LDEV.

Possible values are:

- `compression_deduplication`: Enables both compression and deduplication (default for B series storage).
- `compression`: Enables only compression.

## Example Playbook

```yaml
---
- name: Create primary and secondary quorum disk
  hosts: localhost
  gather_facts: false
  roles:
    - role: hv_vsp_create_primary_and_secondary_quorum_disk
      vars:
        hv_vsp_create_primary_and_secondary_quorum_disk_primary_storage_connection:
          address: "192.168.1.100"
          username: "admin"
          password: "{{ vault_primary_password }}"
        hv_vsp_create_primary_and_secondary_quorum_disk_secondary_storage_connection:
          address: "192.168.1.101"
          username: "admin"
          password: "{{ vault_secondary_password }}"
        hv_vsp_create_primary_and_secondary_quorum_disk_quorum_disk_storage_connection:
          address: "192.168.1.102"
          username: "admin"
          password: "{{ vault_quorum_password }}"
        hv_vsp_create_primary_and_secondary_quorum_disk_quorum_disk_storage_host_groups:
          - host_group_name: "HG_001"
            port: "CL1-A"
          - host_group_name: "HG_002"
            port: "CL1-B"
        hv_vsp_create_primary_and_secondary_quorum_disk_quorum_disk_id: 1
        hv_vsp_create_primary_and_secondary_quorum_disk_quorum_disk_size: "12300MB"
        hv_vsp_create_primary_and_secondary_quorum_disk_external_pool_id: 0
```

## What the Role Does

1. **Gather Storage Information**: Retrieves facts from primary, secondary, and quorum disk storage systems
2. **Determine Storage Types**: Automatically identifies storage types (R9, R8, RH20ETP, M8) based on model information
3. **Create External LDEV**: Creates an LDEV on the quorum disk storage provider
4. **Present to Host Groups**: Presents the created LDEV to specified host groups on the quorum disk storage
5. **Create External Volumes**: Creates external volume mappings on both primary and secondary storage
6. **Validate Quorum IDs**: Checks for available quorum disk IDs on both storage systems
7. **Create Quorum Disks**: Registers quorum disks on both primary and secondary storage
8. **Generate Report**: Provides a detailed report of the created quorum disk configuration

## License

Proprietary

## Author Information

Hitachi Vantara
