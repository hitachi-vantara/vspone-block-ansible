
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

- **hv_gad_facts:** Retrieves GAD pairs information (gateway connection type only).
- **hv_gateway_admin_password:** Updates the gateway admin password.
- **hv_gateway_subscriber_facts:** Retrieves subscriber information.
- **hv_gateway_subscriber:** Manages subscribers.
- **hv_gateway_subscription_facts:** Retrieves subscriber resource information (gateway connection type only).
- **hv_gateway_unsubscribe_resource:** Manages un-subscription of resources (gateway connection type only).
- **hv_hg_facts:** Retrieves host group information.
- **hv_hg:** Manages host groups.
- **hv_hur_facts:** Retrieves HUR information (gateway connection type only).
- **hv_hur:** Manages HUR pairs (gateway connection type only).
- **hv_iscsi_target_facts:** Retrieves iSCSI target information.
- **hv_iscsi_target:** Manages iSCSI targets.
- **hv_ldev_facts:** Retrieves logical device information.
- **hv_ldev:** Manages logical devices.
- **hv_nvm_subsystems_facts:** Retrieves NVM subsystems information (direct connection type only).
- **hv_paritygroup_facts:** Retrieves parity group information.
- **hv_shadow_image_pair_facts:** Retrieves shadow image pair information.
- **hv_shadow_image_pair:** Manages shadow image pairs.
- **hv_snapshot_facts:** Retrieves snapshot information.
- **hv_snapshot:** Manages snapshots.
- **hv_storage_port_facts:** Retrieves storage port information (direct connection type only).
- **hv_storage_port:** Changes storage port settings (direct connection type only).
- **hv_storagepool_facts:** Retrieves storage pool information.
- **hv_storagepool:** Manages storage pool information (gateway connection type only).
- **hv_storagesystem_facts:** Retrieves storage system information.
- **hv_storagesystem:** Manages storage systems.
- **hv_system_facts:** Retrieves system information.
- **hv_troubleshooting_facts:** Collects log bundles from the Ansible modules host and gateway service host.
- **hv_truecopy_facts:** Retrieves TrueCopy pairs information (gateway connection type only).
- **hv_truecopy:** Manages TrueCopy pairs.
- **hv_uaig_token_facts:** Retrieves an API token for the Hitachi gateway service host.
