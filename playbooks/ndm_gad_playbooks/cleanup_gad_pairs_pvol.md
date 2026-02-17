# cleanup_gad_pairs_pvol.yml

## Purpose

This playbook performs **post-migration cleanup** after a successful **Global-Active Device (GAD) Non-Disruptive Migration**.

It removes original source-side storage resources that are no longer required.

---

## What This Playbook Does

- Un-presents original primary volumes from host groups  
- Deletes original primary (source) LDEVs  
- Removes GAD remote connections and path groups  
- Deregisters quorum disks  

---

## High-Level Workflow

```
Validate Migration Success
        │
        v
Un-present Source Volumes
        │
        v
Delete Primary Volumes
        │
        v
Remove GAD Connections
        │
        v
Cleanup Quorum Disk
```

---

## Prerequisites

- Migration completed successfully  
- Application I/O validated on new primary volumes  
- GAD pairs no longer required  

---

## Output

- Source-side storage resources removed  
- Storage capacity reclaimed  

---

## Example Usage

```bash
ansible-playbook cleanup_gad_pairs_pvol.yml
```

---

## Important Warning

> ⚠️ **Destructive Operation**  
> This playbook permanently deletes storage resources. Execute only after full migration validation and customer approval.

---

## Disclaimer

This playbook is provided as an example only and is supplied **"AS IS"** without warranty of any kind. Use at your own risk.
