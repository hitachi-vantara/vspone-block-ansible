# NDM GAD Playbooks - Non-Disruptive Migration with Global Active Device

This directory contains Ansible playbooks for implementing complete storage migration workflows using Hitachi VSP One Block's Global Active Device (GAD) technology with Non-Disruptive Migration (NDM) capabilities.

## Overview

The NDM GAD playbooks provide a comprehensive solution for migrating storage volumes between Hitachi VSP storage systems while maintaining data availability and integrity. All operational details and status information are automatically saved in JSON format to a configurable status file for tracking and auditing purposes.

## Architecture

```
┌─────────────────┐    GAD Replication    ┌─────────────────┐
│   Primary VSP   │◄──────────────────────┤  Secondary VSP  │
│   Storage       │                       │   Storage       │
└─────────────────┘                       └─────────────────┘
         │                                         │
         │         Non-Disruptive Migration       │
         └─────────────────────────────────────────┘
                           │
                ┌─────────────────┐
                │  Status File    │
                │  (JSON Format)  │
                └─────────────────┘
```

## Playbooks

### 1. `create_gad_pairs_using_wwns.yml`

**Purpose**: Complete GAD migration workflow including discovery and GAD pair creation

**Key Features**:
- **Host Volume Discovery**: Queries existing volumes from primary storage using host World Wide Names (WWNs)
- **Volume Validation**: Validates host mode consistency across discovered volumes
- **GAD Infrastructure Setup**: Creates necessary GAD infrastructure components
- **Pair Creation**: Establishes GAD replication pairs between primary and secondary storage
- **Status Tracking**: All details saved in `gad_status_file` in JSON format

**Workflow Steps**:
1. **Discovery Phase**: Query host volumes by specified WWNs
2. **Validation Phase**: Check host mode consistency and volume availability
3. **GAD Creation Phase**: Create GAD pairs for discovered volumes

**Required Configuration**:
- Host WWNs for volume discovery
- Primary and secondary storage connection details
- Storage ports configuration
- GAD infrastructure settings
- Status file path for JSON output

### 2. `migrate_gad_pairs.yml`

**Purpose**: Performs migration of already created GAD pairs using non-disruptive operations

**Key Features**:
- **Non-Disruptive Migration**: Uses swap-split operation to preserve data integrity
- **Status File Integration**: Reads existing GAD pair information from JSON status file
- **Automated Migration**: Performs swap-split to make secondary volumes primary
- **Migration Reporting**: Generates comprehensive migration status reports

**Prerequisites**:
- GAD pairs must already be created (typically by `create_gad_pairs_using_wwns.yml`)
- Valid `gad_status_file` with existing GAD pair information

### 3. `cleanup_gad_pairs_pvol.yml`

**Purpose**: Post-migration cleanup of original storage resources

**Key Features**:
- **Volume Cleanup**: Removes original primary volumes after successful migration
- **Connection Cleanup**: Removes remote connections and path groups
- **Quorum Disk Management**: Deregisters and cleans up quorum disks
- **Resource Optimization**: Frees up storage resources on source system

**Cleanup Operations**:
1. Un-present volumes from original host groups
2. Delete original volumes from primary storage
3. Remove remote connections and path groups
4. Clean up quorum disk configurations

## Configuration Requirements

### Storage Connection Configuration

```yaml
connection_info:
  address: "{{storage_address}}"
  username: "{{vault_storage_username}}"
  password: "{{vault_storage_secret}}"

secondary_connection_info:
  address: "{{secondary_storage_address}}"
  username: "{{vault_secondary_storage_username}}"
  password: "{{vault_secondary_storage_secret}}"
```

### Host WWN Configuration

```yaml
host_wwns:
  - "50060E801234ABCD"  # Production host WWN 1
  - "50060E805678EFGH"  # Production host WWN 2
```

### GAD Status File Configuration

```yaml
gad_status_file: "~/logs/hitachivantara/ansible/vspone_block/gad_status_role_test.json"
```

**Important**: Ensure the path exists and is writable. This file stores:
- Discovered volume information
- GAD pair creation status
- Migration progress and results
- Infrastructure configuration details
- Timing and execution metadata

## Prerequisites

### Software Requirements
- Hitachi VSP One Block Ansible collection installed
- Ansible 2.9 or higher
- Python 3.6 or higher

### Storage Requirements
- Valid credentials for both primary and secondary VSP storage systems
- Network connectivity between storage systems
- Existing volumes assigned to host groups with specified WWNs
- Sufficient storage capacity on secondary system

### Infrastructure Requirements
- GAD-capable storage ports configured
- Quorum disk configuration (for GAD consistency)
- Remote path connectivity between storage systems

## Usage Workflow

### Complete Migration Workflow

1. **Discovery and GAD Creation**:
   ```bash
   ansible-playbook create_gad_pairs_using_wwns.yml
   ```

2. **Perform Migration**:
   ```bash
   ansible-playbook migrate_gad_pairs.yml
   ```

3. **Post-Migration Cleanup**:
   ```bash
   ansible-playbook cleanup_gad_pairs_pvol.yml
   ```

### Individual Operations

Run specific phases using tags:

```bash
# Discovery only
ansible-playbook create_gad_pairs_using_wwns.yml --tags discovery

# GAD creation only
ansible-playbook create_gad_pairs_using_wwns.yml --tags gad_creation

# Migration only
ansible-playbook migrate_gad_pairs.yml --tags migration
```
## Additional Configuration Options
### Debug Mode

Enable detailed debugging:

```yaml
debug_mode: true
```

---

**Note**: Additional configuration details and advanced usage scenarios will be documented as requirements evolve.