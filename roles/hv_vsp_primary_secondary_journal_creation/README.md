# hv_vsp_primary_secondary_journal_creation

An Ansible role for creating journal on Hitachi VSP One Block storage for both primary and secondary 
storage systems. 

## Overview

This role handles the creation on journal on primary and secondary storages.

## Features

- **Create journal on primary storage**
- **Create journal on secondary storage**
- **Detailed reporting**: Generates execution reports with success/failure tracking for all operations

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

#### Secondary Storage Connection

```yaml
secondary_connection_info:
  management_address: "192.168.1.200"
  management_username: "admin"
  management_password: "password"
  api_token: "your_api_token"  # Alternative to username/password
```

### Configuration Variables

#### Common Journal Creation Configuration

```yaml
# Size of the joutnal volume in GB.
# Minimum value is 8.
size_in_gb: 8
```

#### Primary Storage Journal Creation Configuration

```yaml
# Journal IDs for the primary storage.
# Specify a decimal (base 10) number in the range from 0 to 255.
primary_journal_ids: [221, 222]

# Use either pool_id or parity_group_id.
# ID of the dynamic pool for the ldev creation on primary storage.
primary_pool_id: 1

# ID of parity group for the ldev creation on primary storage.
primary_parity_group_id: "1-1"
```

#### Secondary Storage Journal Creation Configuration

```yaml
# Journal IDs for the secondary storage.
# Specify a decimal (base 10) number in the range from 0 to 255.
secondary_journal_ids: [229, 230]

# Use either pool_id or parity_group_id.
# ID of the dynamic pool for the ldev creation on secondary storage.
secondary_pool_id: 1

# ID of parity group for the ldev creation on secondary storage.
secondary_parity_group_id: "1-1"
```

## License

Apache License 2.0

## Author Information

**Hitachi Vantara Infrastructure Team**

- Role for creating journal on Hitachi VSP One Block storage for both primary and secondary storage systems
- Part of comprehensive storage automation framework
