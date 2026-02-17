# migrate_gad_pairs.yml

## Purpose

This playbook performs **Non-Disruptive Migration (NDM)** of existing **Global-Active Device (GAD) pairs** using the **Swap-Split** operation.

It promotes secondary volumes to become the new primary volumes while maintaining data consistency and host access.

---

## What This Playbook Does

- Reads existing GAD pair information from a JSON status file  
- Executes **Swap-Split** operation on GAD pairs  
- Reverses P-VOL and S-VOL roles  
- Preserves data integrity during migration  

---

## High-Level Workflow

```
Read GAD Status File
        │
        v
Verify GAD Pair State
        │
        v
Execute Swap-Split
        │
        v
Secondary Volumes Become Primary
```

---

## Prerequisites

- GAD pairs already created and in **PAIR** status  
- Valid JSON status file generated during GAD creation  
- Network connectivity between storage systems  

---

## Output

- Successful role reversal of GAD pairs  
- Updated migration status in JSON file  

---

## Example Usage

```bash
ansible-playbook migrate_gad_pairs.yml
```

---

## Notes

- No volumes are deleted  
- No re-copy or resync is required  
- Minimal application impact  

---

## Disclaimer

This playbook is provided as an example only and is supplied **"AS IS"** without warranty of any kind. Use at your own risk.
