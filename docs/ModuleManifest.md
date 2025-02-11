# Available Modules

### VSP One SDS Block Ansible Modules:
- hv_sds_block_chap_user_facts - Retrieves information about Hitachi SDS block storage system CHAP users.
- hv_sds_block_chap_user - Manages Hitachi SDS block storage system CHAP users.
- hv_sds_block_compute_node_facts - Retrieves information about Hitachi SDS block storage system compute nodes.
- hv_sds_block_compute_node - Manages Hitachi SDS block storage system compute nodes.
- hv_sds_block_compute_port_authentication - Manages Hitachi SDS block storage system compute port authentication mode settings.
- hv_sds_block_port_facts - Retrieves information about Hitachi SDS block storage system compute ports.
- hv_sds_block_storage_system_fact - Retrieves information about a specific Hitachi SDS block storage system.
- hv_sds_block_volume_facts - Retrieves information about Hitachi SDS block storage system volumes.
- hv_sds_block_volume - Manages Hitachi SDS block storage system volumes.
- hv_sds_block_vps_fact: Retrieves information about Virtual Private Storages (VPS) of Hitachi SDS block storage system.
- hv_sds_block_vps: Manages Hitachi SDS block storage system Virtual Private Storages (VPS) volume ADR setting.

### VSP and VSP One Ansible modules:
- hv_gad_fact: Retrieves GAD pairs information from Hitachi VSP storage systems (available only for gateway connection type).
- Manages GAD pairs on Hitachi VSP storage systems (available only for gateway connection type).
- hv_gateway_admin_password - Updates password of gateway admin on Hitachi VSP storage systems.
- hv_gateway_subscriber_fact - Retrieves information about subscriber on Hitachi VSP storage systems.
- hv_gateway_subscriber - Manages subscribers of a partner on Hitachi VSP storage systems.
- hv_gateway_subscription_facts: Retrieves information about resources of a subscriber on Hitachi VSP storage systems.(available only for gateway connection type).
- hv_gateway_unsubscribe_resource: Manages un-subscription of resources for a subscriber on Hitachi VSP storage systems.(available only for gateway connection type).
- hv_hg_facts - Retrieves host group information from a specified Hitachi VSP storage system.
- hv_hg - Manages host group on Hitachi VSP storage system.
- hv_hur_facts: Retrieves HUR information from Hitachi VSP storage systems.(available only for gateway connection type).
- hv_hur: Manages HUR pairs on Hitachi VSP storage systems (available only for gateway connection type).
- hv_iscsi_target_facts - Retrieves information about iSCSI targets from Hitachi VSP storage systems.
- hv_iscsi_target - Manages iSCSI target on Hitachi VSP storage systems.
- hv_ldev_facts - Retrieves information about logical devices from Hitachi VSP storage systems.
- hv_ldev - Manages logical devices on Hitachi VSP storage systems.
- hv_nvm_subsystems_facts: Retrieves information about NVM subsystems from Hitachi VSP storage systems.(available only for direct connection type).
- hv_paritygroup_facts - Retrieves information about parity groups from Hitachi VSP storage systems.
- hv_shadow_image_pair_facts - Retrieves information about shadow image pairs from Hitachi VSP storage systems.
- hv_shadow_image_pair - Manages shadow image pairs on Hitachi VSP storage systems.
- hv_snapshot_facts - Retrieves snapshot information from from Hitachi VSP storage systems.
- hv_snapshot - Manages snapshots on Hitachi VSP storage systems.
- hv_storage_port_facts: Retrieves storage port information from Hitachi VSP storage systems.(available only for direct connection type).
- hv_storage_port: Change the storage port settings in the Hitachi VSP storage systems (available only for direct connection type).
- hv_storagepool_facts - Retrieves storage pool information from Hitachi VSP storage systems.
- hv_storagepool: Create, update, delete storage pool information from Hitachi VSP storage systems (available only for gateway connection type).
- hv_storagesystem_facts -  Retrieves storage system information from Hitachi VSP storage systems.
- hv_storagesystem - Manages Hitachi VSP storage systems.
- hv_system_facts - Retrieves system information from Hitachi VSP storage systems.
- hv_troubleshooting_facts - Collects the log bundles for Hitachi ansible modules host and Hitachi gateway service host.
- hv_truecopy_facts: Retrieves TrueCopy pairs information from Hitachi VSP storage systems (available only for gateway connection type).
- hv_truecopy: Manages TrueCopy pairs on Hitachi VSP storage systems.
- hv_uaig_token_fact - Retrieves an API token for the Hitachi gateway service host.