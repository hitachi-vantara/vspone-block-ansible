# Troubleshooting

## Logging

- **Log File Location:**  
  `$HOME/logs/hitachivantara/ansible/vspone_block/hv_vspone_block_modules.log`
  `$HOME/logs/hitachivantara/ansible/vspone_block/hv_vspone_block_audit.log`

## Log Bundle Collection

Playbooks for generating log bundles are provided in the collection:

- **Location:**  
  `/opt/hitachivantara/ansible/vspone_block/tools`

- **Playbooks:**
  - `logbundle_collection.yml`

After executing the appropriate playbook, a ZIP archive (e.g., `ansible_log_bundle_2024_06_04_23_28_44.zip`) will be created in:

- **Output Directory:**  
  `$HOME/logs/hitachivantara/ansible/vspone_block/log_bundles/`

## Environment Variables

To customize logging behavior, set the following environment variables:

- `HV_ANSIBLE_LOG_PATH`
- `HV_ANSIBLE_LOG_LEVEL`
- `HV_ANSIBLE_LOG_FILE`
