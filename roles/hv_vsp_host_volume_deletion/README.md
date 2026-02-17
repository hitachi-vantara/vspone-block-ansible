# hv_vsp_host_volume_deletion

An Ansible role for comprehensive cleanup operations on Hitachi VSP One Block storage systems. This role performs post-migration cleanup by removing volumes from host groups, deleting volumes, deregistration quorum disks, and cleaning up remote connections between storage systems.

## Overview

This role handles the complete cleanup phase of storage management workflows by:

1. **Un-presenting volumes from host groups** - Safely removes LDEV assignments from host groups
2. **Deleting volumes from storage** - Permanently removes LDEVs from the storage system  
3. **De-registering quorum disks** - Removes quorum disk registrations from both primary and secondary storage systems
4. **Deleting remote connections** - Cleans up remote connections between primary and secondary storage systems
5. **Comprehensive validation** - Validates input data and processes volumes safely
6. **Detailed reporting** - Provides execution reports with operation status for all cleanup activities

## Features

- **Safe volume removal**: Un presents volumes from host groups before deletion
- **Complete volume cleanup**: Permanently removes LDEVs from storage systems
- **Quorum disk management**: Deregisters quorum disks from both primary and secondary storage systems
- **Remote connection cleanup**: Removes remote connections between storage systems
- **Flexible input handling**: Accepts LDEV data from WWN query roles or direct input
- **Batch processing**: Efficiently processes multiple volumes in a single operation
- **Dual storage support**: Manages operations across primary and secondary storage systems
- **Comprehensive validation**: Validates LDEV data before processing
- **Detailed reporting**: Generates execution reports with success/failure tracking for all operations
- **Integration ready**: Designed to work with GAD migration and WWN query workflows

## Requirements

- Ansible 2.9+
- `hitachivantara.vspone_block` collection (version 1.0.0 or later)
- Valid connection credentials for VSP One Block storage systems
- Proper permissions for volume management operations

## Dependencies

No external role dependencies. Requires `hitachivantara.vspone_block` collection.

## Role Variables

### Connection Information (Required)

#### Primary Storage Connection

```yaml
connection_info:
  management_address: "192.168.1.100"
  management_username: "admin"
  management_password: "password"
  api_token: "your_api_token"  # Alternative to username/password
```

#### Secondary Storage Connection (Required for GAD cleanup)

```yaml
secondary_connection_info:
  management_address: "192.168.1.200"
  management_username: "admin"
  management_password: "password"
  api_token: "your_api_token"  # Alternative to username/password
```

### Optional Configuration Variables

These parameters are optional - when present, the role will delete the corresponding resources:

#### Volume Deletion Configuration

```yaml
# List of primary volume IDs (LDEVs) to delete (optional)
# When defined: Deletes specified LDEVs from primary storage
primary_volume_ids:
  - "1000"
  - "1001"
  - "1002"
```

#### Quorum Disk Configuration

```yaml
# Quorum disk ID for deregistration (optional)
# When defined: Deregisters quorum disk from both primary and secondary storage systems
quorum_disk_id: "QD_001"
```

#### Remote Connection Configuration

```yaml
# Path group ID for remote connection deletion (optional)
# When defined: Deletes remote connections between primary and secondary storage systems
path_group_id: "PG_001"
```

## License

Apache License 2.0

## Author Information

**Hitachi Vantara Infrastructure Team**

- Role for deleting host volumes on Hitachi VSP One Block storage
- Part of comprehensive storage automation framework  
- Supports enterprise storage cleanup and migration workflows
