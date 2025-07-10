
# Available Modules

This collection includes modules for managing both Hitachi VSP One SDS Block and Hitachi VSP storage systems.

## VSP One SDS Block Ansible Modules

- **hv_sds_block_chap_user_facts:** Retrieves information about Hitachi SDS block storage system CHAP users.
- **hv_sds_block_chap_user:** Manages Hitachi SDS block storage system CHAP users.
- **hv_sds_block_compute_node_facts:** Retrieves information about compute nodes.
- **hv_sds_block_compute_node:** Manages compute nodes.
- **hv_sds_block_compute_port_authentication:** Manages compute port authentication mode settings.
- **hv_sds_block_port_facts:** Retrieves information about compute ports.
- **hv_sds_block_storage_system_facts:** Retrieves information about a specific SDS block storage system.
- **hv_sds_block_volume_facts:** Retrieves information about storage system volumes.
- **hv_sds_block_volume:** Manages volumes.
- **hv_sds_block_vps_fact:** Retrieves information about Virtual Private Storages (VPS).
- **hv_sds_block_vps:** Manages VPS volume ADR settings.

## VSP Ansible Modules

- **hv_audit_log_transfer_dest:** Sets the transfer destinations of audit log files using UDP/TCP ports.
- **hv_audit_log_transfer_dest_facts:** Retrieves information about the transfer destinations of audit log files.
- **hv_clpr:** Creates, updates, and deletes CLPR information.
- **hv_clpr_facts:** Retrieves CLPR information.
- **hv_ddp_pool:** Manages DDP pools.
- **hv_ddp_pool_facts:** Retrieves information about DDP pools.
- **hv_disk_drive:** Manages disk drives.
- **hv_disk_drive_facts:** Retrieves information about disk drives.
- **hv_external_paritygroup:** Assigns external volume groups to a CLPR or changes the MP blade assigned to an external volume group.
- **hv_external_paritygroup_facts:** Retrieves information about External Parity Group.
- **hv_external_path_group:** Manages External Path Groups.
- **hv_external_path_group_facts:** Retrieves information about External Path Group.
- **hv_external_volume:** Manages external volumes.
- **hv_external_volume_facts:** Retrieves information about external volumes.
- **hv_gad:** Manages GAD pairs.
- **hv_gad_facts:** Retrieves information about GAD pairs.
- **hv_hg:** Manages host groups.
- **hv_hg_facts:** Retrieves information about host groups.
- **hv_hur:** Manages HUR pairs.
- **hv_hur_facts:** Retrieves information about HUR pairs.
- **hv_iscsi_remote_connection:** Manages iSCSI remote connections.
- **hv_iscsi_remote_connection_facts:** Retrieves information about iSCSI remote connections.
- **hv_iscsi_target:** Manages iSCSI targets.
- **hv_iscsi_target_facts:** Retrieves information about iSCSI targets.
- **hv_journal_volume:** Manages journal volumes.
- **hv_journal_volume_facts:** Retrieves information about journal volumes.
- **hv_ldev:** Manages logical devices.
- **hv_ldev_facts:** Retrieves information about logical devices.
- **hv_mp_facts:** Retrieves MP blades information.
- **hv_nvm_subsystems:** Manages NVM subsystems.
- **hv_nvm_subsystems_facts:** Retrieves information about NVM subsystems.
- **hv_paritygroup:** Manages parity groups.
- **hv_paritygroup_facts:** Retrieves information about parity groups.
- **hv_quorum_disk:** Manages quorum disks.
- **hv_quorum_disk_facts:** Retrieves information about quorum disks.
- **hv_remote_connection:** Manages remote connections.
- **hv_remote_connection_facts:** Retrieves information about remote connections.
- **hv_remote_copy_group:** Manages remote copy groups.
- **hv_remote_copy_group_facts:** Retrieves information about remote copy groups.
- **hv_remote_storage_registration:** Manages remote storage registrations.
- **hv_remote_storage_registration_facts:** Retrieves information about remote storage registrations.
- **hv_resource_group:** Manages resource groups.
- **hv_resource_group_facts:** Retrieves information about resource groups.
- **hv_resource_group_lock:** Manages resource group locks.
- **hv_server_priority_manager:** Sets, changes, and deletes Server Priority Manager information.
- **hv_server_priority_manager_facts:** Retrieves Server Priority Manager information.
- **hv_shadow_image_group:** Manages shadow image groups.
- **hv_shadow_image_group_facts:** Retrieves information about shadow image groups.
- **hv_shadow_image_pair:** Manages shadow image pairs.
- **hv_shadow_image_pair_facts:** Retrieves information about shadow image pairs.
- **hv_snapshot:** Manages snapshots.
- **hv_snapshot_facts:** Retrieves information about snapshots.
- **hv_snapshot_group:** Manages snapshot groups.
- **hv_snapshot_group_facts:** Retrieves information about snapshot groups.
- **hv_snmp_setting:** Manages SNMP settings.
- **hv_snmp_settings_facts:** Retrieves SNMP settings for a storage system.
- **hv_storage_port:** Manages storage port settings.
- **hv_storage_port_facts:** Retrieves information about storage ports.
- **hv_storage_system:** Sets the date and time in a storage system with NTP disabled/enabled.
- **hv_storage_system_monitor_facts:** Retrieves alert, hardware installed, and channel board information.
- **hv_storagepool:** Manages storage pools.
- **hv_storagepool_facts:** Retrieves information about storage pools.
- **hv_storagesystem_facts:** Retrieves information about storage systems.
- **hv_truecopy:** Manages TrueCopy pairs.
- **hv_truecopy_facts:** Retrieves information about TrueCopy pairs.
- **hv_troubleshooting_facts:** Collects log bundles from the Ansible modules host.
- **hv_upload_file:** Uploads a primary/secondary client certificate file to a storage system for audit log.
- **hv_user:** Manages users.
- **hv_user_facts:** Retrieves information about users.
- **hv_user_group:** Manages user groups.
- **hv_user_group_facts:** Retrieves information about user groups.