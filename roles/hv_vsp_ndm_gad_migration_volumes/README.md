# hv_vsp_ndm_migrate_gad_pairs

An Ansible role for migrating GAD (Global-Active Device) pairs on Hitachi VSP One Block storage systems. This role performs post-GAD activities including non-Disruptive migration via swap-split operations followed by GAD pair deletion from the source system.

## Overview

This role handles the migration phase of GAD pair lifecycle management by:

1. **Identifying existing GAD pairs** - Discovers GAD pairs based on provided LDEV IDs
2. **Performing swap-split migration** - Non-Disruptively migrates GAD pairs to make secondary volumes primary
3. **Cleaning up source pairs** - Deletes migrated GAD pairs from the source storage system
4. **Comprehensive reporting** - Provides detailed migration status and results

## Features

- **Non-Disruptive migration**: Uses swap-split operations to preserve data integrity
- **Flexible input handling**: Accepts LDEV IDs from WWN query roles or direct input
- **Comprehensive validation**: Validates GAD pair existence before migration operations
- **Detailed reporting**: Generates migration reports with success/failure tracking

## Requirements

- Ansible 2.9+
- `hitachivantara.vspone_block` collection (version 1.0.0 or later)
- Valid connection credentials for both primary and secondary VSP One Block systems
- Existing GAD pairs to be migrated

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
  api_token: "your_api_token" # Alternative to username/password
```

#### Secondary Storage Connection

```yaml
secondary_connection_info:
  management_address: "192.168.1.200"
  management_username: "admin"
  management_password: "password"
  api_token: "your_api_token" # Alternative to username/password
```

## Migration Process Details

### 1. GAD Pair Discovery Phase

- Queries existing GAD pairs using provided LDEV IDs
- Validates GAD pair existence and status
- Filters out LDEVs without existing GAD pairs
- Reports missing GAD pairs for troubleshooting

### 2. Swap-Split Migration Phase

- Performs non-Disruptive swap-split operations
- Makes secondary volumes the new primary volumes
- Preserves data integrity throughout the process
- Tracks migration success/failure for each pair

### 3. Cleanup Phase

- Deletes migrated GAD pairs from source system
- Removes GAD relationships after successful migration
- Ensures clean state for migrated volumes
- Reports deletion status for audit purposes

### 4. Reporting Phase

- Generates comprehensive migration report
- Provides detailed success/failure tracking
- Includes timestamps for audit trails
- Supplies data for monitoring and alerting

## Author Information

**Hitachi Vantara Infrastructure Team**

- Role for migrating GAD pairs on Hitachi VSP One Block storage
- Part of comprehensive storage automation framework
- Supports enterprise storage migration workflows
