# Changelog

## [3.0.1] 
### Bugfixes
- **Miscellaneous 1:** Fixed multiple session auth issue for 'direct connect' connection type.
- **Miscellaneous 2:** Fixed Python older version issue, no sudo user installation issue.
- **hv_lun_facts:** Modified the parameter name from `naa_id` to `canonical_name` (available only for gateway connection type).
- **hv_storagesystem:** Storage system remains in spare pool after user off-boarded the storage from UAI Gateway.
- **hv_sds_block_compute_node_facts:** Fixed issue where the module was not returning the correct compute node information.
- **hv_sds_block_chap_user:** Updated the playbook file with the correct parameter name.
- **hv_storagesystem_facts:** Fixed compatibility issue with Python lower than 3.11.
- **hv_storagepool_facts:** Fixed compatibility issue with Python lower than 3.11.
- **hv_lun_facts:** Fixed LDEV ID not being returned in the facts in case of a `0` value.

## [3.0.0] - Release Date: 2024-06-17
### New Modules
- **hv_sds_block_chap_user_facts:** Retrieves information about Hitachi SDS block storage system CHAP users.
- **hv_sds_block_chap_user:** Manages Hitachi SDS block storage system CHAP users.
- **hv_sds_block_compute_node_facts:** Retrieves information about Hitachi SDS block storage system compute nodes.
- **hv_sds_block_compute_node:** Manages Hitachi SDS block storage system compute nodes.
- **hv_sds_block_compute_port_authentication:** Manages Hitachi SDS block storage system compute port authentication mode settings.
- **hv_sds_block_port_facts:** Retrieves information about Hitachi SDS block storage system compute ports.
- **hv_sds_block_storage_system_fact:** Retrieves information about a specific Hitachi SDS block storage system.
- **hv_sds_block_volume_facts:** Retrieves information about Hitachi SDS block storage system volumes.
- **hv_sds_block_volume:** Manages Hitachi SDS block storage system volumes.

- **hv_gateway_admin_password:** Updates the password of gateway admin on Hitachi VSP storage systems.
- **hv_gateway_subscriber_fact:** Retrieves information about a subscriber on Hitachi VSP storage systems.
- **hv_gateway_subscriber:** Manages subscribers of a partner on Hitachi VSP storage systems.
- **hv_hg_facts:** Retrieves host group information from a specified Hitachi VSP storage system.
- **hv_hg:** Manages host group on Hitachi VSP storage systems.
- **hv_iscsi_target_facts:** Retrieves information about iSCSI targets from Hitachi VSP storage systems.
- **hv_iscsi_target:** Manages iSCSI targets on Hitachi VSP storage systems.
- **hv_lun_facts:** Retrieves information about logical units (LUNs) from Hitachi VSP storage systems.
- **hv_lun:** Manages logical units (LUNs) on Hitachi VSP storage systems.
- **hv_paritygroup_facts:** Retrieves information about parity groups from Hitachi VSP storage systems.
- **hv_shadow_image_pair_facts:** Retrieves information about shadow image pairs from Hitachi VSP storage systems.
- **hv_shadow_image_pair:** Manages shadow image pairs on Hitachi VSP storage systems.
- **hv_snapshot_facts:** Retrieves snapshot information from Hitachi VSP storage systems.
- **hv_snapshot:** Manages snapshots on Hitachi VSP storage systems.
- **hv_storagepool_facts:** Retrieves storage pool information from Hitachi VSP storage systems.
- **hv_storagesystem_facts:** Retrieves storage system information from Hitachi VSP storage systems.
- **hv_storagesystem:** Manages Hitachi VSP storage systems.
- **hv_system_facts:** Retrieves system information from Hitachi VSP storage systems.
- **hv_troubleshooting_facts:** Collects the log bundles for Hitachi Ansible modules host and Hitachi gateway service host.
- **hv_uaig_token_fact:** Retrieves an API token for the Hitachi gateway service host.
