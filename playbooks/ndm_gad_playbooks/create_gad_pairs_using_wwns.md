# create_gad_pairs_using_wwns.yml

## Purpose

This playbook discovers existing host-mapped volumes using **World Wide Names (WWNs)** and creates **Global-Active Device (GAD) pairs** between primary and secondary **Hitachi VSP One Block** storage systems.

It is the **starting point** for a Non-Disruptive Migration (NDM) workflow.

---

## What This Playbook Does

- Discovers LDEVs mapped to hosts by WWN  
- Validates host mode consistency across volumes  
- Creates required GAD infrastructure  
- Establishes GAD pairs in **PAIR** status using batch processing  
- Saves all operational details to a JSON status file  

---

## High-Level Workflow

```
Hosts (WWNs)
     │
     v
Discover Host-Mapped LDEVs
     │
Validate Host Mode Consistency
     │
Create GAD Infrastructure
     │
Create GAD Pairs (PAIR)
     │
Write Status File (JSON)
```

---

## Required Inputs

- Host WWNs  
- Primary and secondary storage credentials  
- Storage ports and remote path configuration  
- Secondary storage pool ID  
- Path to GAD status file
- (Optional) `hv_vsp_ndm_gad_migration_pairs_batch_gad_pair_creation_size` - Batch size for GAD pair creation (default: 2)

---

## Batch Processing

GAD pairs are created in batches to optimize performance and resource utilization. The batch size can be configured using the `hv_vsp_ndm_gad_migration_pairs_batch_gad_pair_creation_size` variable (default value is 2). This approach helps manage large-scale deployments by processing pairs in smaller groups, providing better progress tracking and preventing API throttling.

---

## Output

- GAD pairs created in **PAIR** status  
- JSON status file containing:
  - Discovered LDEV information
  - GAD pair details
  - Infrastructure metadata

---

## Example Usage

```bash
ansible-playbook create_gad_pairs_using_wwns.yml
```

---

## Notes

- No data is deleted  
- No application downtime is required  
- This playbook must complete successfully before migration  

---

## Disclaimer

This playbook is provided as an example only and is supplied **"AS IS"** without warranty of any kind. Use at your own risk.
