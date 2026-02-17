# hv_vsp_query_host_volumes_by_wwns

## Description

This Ansible role queries Hitachi VSP One Block storage to find host volumes by WWN (World Wide Name) identifiers. It retrieves comprehensive hostgroup information including WWNs, LDEV details, host modes, and host mode options. The role performs consistency validation and returns structured data about matching volumes, making it ideal for automated storage management workflows.

## Key Features

- **WWN-based Volume Discovery**: Find volumes associated with specific host WWNs
- **Consistency Validation**: Ensures all matching hostgroups have consistent host modes and options
- **Structured Output**: Returns detailed host volume information in a standardized format
- **Port Filtering**: Optional port-specific queries for targeted discovery
- **Error Handling**: Returns empty results if host configurations are inconsistent
- **Integration Ready**: Designed to work with GAD pair creation and other storage roles

## Requirements

- Ansible 2.9 or higher
- `hitachivantara.vspone_block` collection
- Access to Hitachi VSP One Block storage system
- Valid storage credentials with query permissions

### Installing Collection Requirements

Before using this role, install the required collection:

```bash
ansible-galaxy collection install -r requirements.yml
```

Or install the collection directly:

```bash
ansible-galaxy collection install hitachivantara.vspone_block
```

## Role Variables

### Required Variables

- `connection_info`: Connection details for the VSP One Block storage system

  ```yaml
  connection_info:
    address: "192.168.1.100"
    username: "storage_admin"
    password: "secure_password"
  ```

- `host_wwns`: List of WWN identifiers to search for (minimum 1 required)

  ```yaml
  host_wwns:
    - "100000109B583909"
    - "100000109B58390A"
    - "50060E8012345678"
  ```

### Optional Variables

- `ports`: List of specific ports to query (if not provided, all ports are queried)

  ```yaml
  ports:
    - "CL1-A"
    - "CL2-B"
    - "CL7-A"
  ```

- `debug_mode`: Enable detailed debug output (default: `false`)

  ```yaml
  debug_mode: true
  ```

## Query Behavior

### Port Filtering Logic

- **All Ports**: When `ports` is not specified, queries all storage ports
- **Specific Ports**: When `ports` is specified, only queries those ports
- **Performance**: Port filtering can improve query performance in large environments

### Consistency Validation

The role performs strict consistency checks across all matching hostgroups:

1. **Host Mode Consistency**: All hostgroups must have the same `host_mode`
2. **Host Mode Options Consistency**: All hostgroups must have identical `host_mode_options`
3. **Failure Behavior**: Returns empty results if any inconsistency is detected

## Return Values

The role sets `hv_vsp_one_query_result` with comprehensive information:

### Basic Results

- `input_wwns`: Original WWNs that were searched for
- `matched_ldev_ids`: Array of unique LDEV IDs found (sorted)
- `total_ldevs_found`: Count of unique LDEV IDs
- `timestamp`: ISO 8601 timestamp of query execution

### Detailed Host Volume Information

- `host_volumes`: Array of detailed host volume objects
- `total_host_volume_entries`: Count of host volume entries
- `hostgroup_ldev_summary`: Summary of hostgroups and their LDEVs

### Consistency Information  

- `host_mode_consistent`: Boolean indicating host mode consistency
- `host_mode_options_consistent`: Boolean indicating host mode options consistency
- `overall_consistency`: Boolean indicating overall consistency (both must be true)
- `consistency_error`: Error message if inconsistent (empty if consistent)

## Host Volume Object Structure

Each entry in `host_volumes` contains:

```yaml
{
  "ldev": 277,                           # LDEV ID
  "lun": 1,                             # LUN number
  "port": "CL7-A",                      # Storage port
  "host_group_name": "Production_HG",   # Hostgroup name
  "host_mode": "VMWARE_EXTENSION",      # Host mode
  "host_mode_options": [54, 63],        # Host mode option numbers
  "host_wwns": ["100000109B583909"],    # Matching WWNs only
  "host_group_id": 4                    # Hostgroup ID
}
```

## Example Playbooks

### Basic Usage

```yaml
---
- name: Query Host Volumes by WWNs
  hosts: localhost
  gather_facts: false
  
  vars:
    connection_info:
      address: "192.168.1.100"
      username: "admin"
      password: "password"
    
    host_wwns:
      - "100000109B583909"
      - "100000109B58390A"
  
  roles:
    - role: hv_vsp_query_host_volumes_by_wwns

  tasks:
    - name: Display results summary
      debug:
        msg:
          - "Found {{ hv_vsp_one_query_result.total_ldevs_found }} unique LDEVs"
          - "Total volume entries: {{ hv_vsp_one_query_result.total_host_volume_entries }}"
          - "Configuration consistent: {{ hv_vsp_one_query_result.overall_consistency }}"
```

### Port-Specific Query with Debug

```yaml
---
- name: Query Specific Ports with Debug
  hosts: localhost
  gather_facts: false
  
  vars:
    connection_info:
      address: "192.168.1.100"
      username: "admin"
      password: "password"
    
    host_wwns:
      - "100000109B583909"
    
    ports:
      - "CL7-A"
      - "CL8-A"
    
    debug_mode: true
  
  roles:
    - role: hv_vsp_query_host_volumes_by_wwns

  tasks:
    - name: Display detailed host volumes
      debug:
        var: hv_vsp_one_query_result.host_volumes
      when: hv_vsp_one_query_result.overall_consistency
```

### Integration with GAD Pair Creation

```yaml
---
- name: WWN Query to GAD Creation Pipeline
  hosts: localhost
  gather_facts: false
  
  tasks:
    # Step 1: Query volumes by WWNs
    - include_role:
        name: hv_vsp_query_host_volumes_by_wwns
      vars:
        host_wwns: ["100000109B583909", "100000109B58390A"]
    
    # Step 2: Create GAD pairs if consistent
    - include_role:
        name: hv_vsp_ndm_create_gad_pairs
      vars:
        matched_ldev_ids: "{{ hv_vsp_one_query_result.matched_ldev_ids }}"
      when:
        - hv_vsp_one_query_result.overall_consistency
        - hv_vsp_one_query_result.total_ldevs_found > 0
```

## Example Output

### Successful Query with Consistent Configuration

```yaml
hv_vsp_one_query_result:
  input_wwns:
    - "100000109B583909"
    - "100000109B58390A"
  matched_ldev_ids: [277, 289, 300]
  total_ldevs_found: 3
  host_volumes:
    - ldev: 277
      lun: 1
      port: "CL7-A"
      host_group_name: "Production_ESXi_HG"
      host_mode: "VMWARE_EXTENSION"
      host_mode_options: [54, 63]
      host_wwns: ["100000109B583909"]
      host_group_id: 4
    - ldev: 289
      lun: 3
      port: "CL7-A" 
      host_group_name: "Production_ESXi_HG"
      host_mode: "VMWARE_EXTENSION"
      host_mode_options: [54, 63]
      host_wwns: ["100000109B583909"]
      host_group_id: 4
  total_host_volume_entries: 2
  host_mode_consistent: true
  host_mode_options_consistent: true
  overall_consistency: true
  consistency_error: ""
  timestamp: "2025-11-14T10:30:45Z"
```

### Failed Query Due to Inconsistent Configuration

```yaml
hv_vsp_one_query_result:
  input_wwns: ["100000109B583909"]
  matched_ldev_ids: []                    # Cleared due to inconsistency
  total_ldevs_found: 0
  host_volumes: []                        # Cleared due to inconsistency
  total_host_volume_entries: 0
  host_mode_consistent: false
  host_mode_options_consistent: true
  overall_consistency: false
  consistency_error: "Host modes or host mode options are not consistent across host groups. Found host modes: ['VMWARE_EXTENSION', 'LINUX'], Found host mode options: [[54, 63]]"
  timestamp: "2025-11-14T10:30:45Z"
```

## Error Handling and Validation

### Input Validation

- Verifies `connection_info` is defined
- Ensures `host_wwns` is provided with at least one WWN
- Validates `ports` parameter if specified

### Consistency Enforcement

- **Host Mode Check**: All matching hostgroups must have identical host modes
- **Host Mode Options Check**: All matching hostgroups must have identical host mode options
- **Empty Response**: Returns empty `host_volumes` and `matched_ldev_ids` if inconsistent
- **Error Reporting**: Provides detailed error messages for troubleshooting

### Common Scenarios

1. **No WWNs Found**: Returns empty results with no error
2. **Inconsistent Host Modes**: Returns empty results with consistency error
3. **Mixed Host Mode Options**: Returns empty results with detailed error message
4. **Network/Auth Errors**: Role fails with connection error

## Best Practices

1. **WWN Format**: Use uppercase 16-character WWN format without colons or dashes
2. **Port Filtering**: Use port filtering in large environments for better performance
3. **Consistency Planning**: Ensure all hostgroups use consistent host modes before querying
4. **Error Handling**: Always check `overall_consistency` before using results in subsequent tasks
5. **Debug Mode**: Enable debug mode during development and troubleshooting
6. **Integration**: Design workflows to handle both successful and failed queries gracefully

## Troubleshooting

### Common Issues

- **Empty Results**: Check WWN format and verify they exist in hostgroups
- **Consistency Errors**: Review host mode configuration across all matching hostgroups
- **Connection Errors**: Verify storage system address, credentials, and network connectivity
- **Performance Issues**: Use port filtering to reduce query scope

### Debug Information

Enable `debug_mode: true` to see:

- Port filtering information
- Host mode consistency check details
- Detailed WWN matching process
- Raw hostgroup data structure

## Integration Points

This role is designed to integrate with:

- **GAD Pair Creation**: Provides `matched_ldev_ids` for automated GAD setup
- **Volume Management**: Supplies detailed volume information for bulk operations
- **Compliance Checking**: Validates host mode consistency across infrastructure
- **Reporting Systems**: Structured output suitable for documentation and monitoring

## Author

Generated for Hitachi VSP One Block storage management and automation workflows
