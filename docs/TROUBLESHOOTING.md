# Troubleshooting

## Logging

- **Enabling Debug Mode:**
  The default log level for Ansible module is INFO
  Run the following command to change the log level to DEBUG
    export HV_ANSIBLE_LOG_LEVEL="DEBUG"
  Run the following command to change the log level back to INFO
    export HV_ANSIBLE_LOG_LEVEL="INFO"

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
