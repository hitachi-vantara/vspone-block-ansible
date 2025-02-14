# Changelog
#  [3.1.0] - Release Date: 2024-10-07
# # New Modules
- **hv_sds_block_vps_fact:** Retrieves information about Virtual Private Storages (VPS) of Hitachi SDS block storage system.
- **hv_sds_block_vps:** Manages Hitachi SDS block storage system Virtual Private Storages (VPS) volume ADR setting.

- **hv_gad_facts:** Retrieves GAD pairs information from Hitachi VSP storage systems (available only for gateway connection type).
- **hv_gad:** Manages GAD pairs on Hitachi VSP storage systems (available only for gateway connection type).
- **hv_gateway_subscription_facts:** Retrieves information about resources of a subscriber on Hitachi VSP storage systems.(available only for gateway connection type). 
- **hv_gateway_unsubscribe_resource:** Manages un-subscription of resources for a subscriber on Hitachi VSP storage systems.(available only for gateway connection type).
- **hv_hur_facts:** Retrieves HUR information from Hitachi VSP storage systems.(available only for gateway connection type).
- **hv_hur:** Manages HUR pairs on Hitachi VSP storage systems (available only for gateway connection type).
- **hv_nvm_subsystems_facts:** Retrieves information about NVM subsystems from Hitachi VSP storage systems.(available only for direct connection type).
- **hv_storage_port_facts:** Retrieves storage port information from Hitachi VSP storage systems.(available only for direct connection type).
- **hv_storage_port:** Change the storage port settings in the Hitachi VSP storage systems (available only for direct connection type).
- **hv_storagepool:** Create, update, delete storage pool information from Hitachi VSP storage systems (available only for gateway connection type).
- **hv_truecopy_facts:** Retrieves TrueCopy pairs information from Hitachi VSP storage systems (available only for gateway connection type).
- **hv_truecopy:** Manages TrueCopy pairs on Hitachi VSP storage systems.

# # Enhancements
- **hv_sds_block_compute_node:** 
    - Manage Compute Node with NVMe-TCP connection
- **hv_sds_block_compute_node_facts:** 
    - Get Compute Node with NVMe-TCP details
- **hv_sds_block_volume:**
    - Create and Update Volume with QoS Settings
- **hv_sds_block_volume_facts:**
    - Get NVMe-TCP volume details
    - Get detailed information [Compute Node, and QoS Settings] for a Volume
- Renamed module name from `hv_lun` to `hv_ldev`.
- Renamed parameter `lun` to `ldev` across all applicable playbooks.
- Renamed parameter `pvol` to `primary_volume_id` across all applicable playbooks.
- Renamed parameter `svol` to `secondary_volume_id` across all applicable playbooks.
- **hv_ldev:**
    - Using a single workflow, delete a volume attached to a host or iSCSI target. 
    - Using a single workflow, delete a volume attached to a host via NVMe-TCP (available only for direct connection type).
    - Using a single worflow, provision and attach a NVMe-TCP volume to host (available only for direct connection type).
    - Get LDEV with NAA details (available only for direct connection type).
    - Create Ldev with Data-Reduction-Share enabled (available only for gateway connection type).
    - Apply tiering policy for a new or existing HDT volume (available only for gateway connection type).
- **hv_ldev_facts:** 
    - Get detailed information [Snapshot, Hostgroup, iSCSI target, NVM Subsystem] for an LDEV (available only for direct connection type).
- **hv_snapshot:** 
    - Auto SVOL mapping during Thin Image creation (available only for direct connection type).
    - Create and Delete Thin Image Clone Pair (available only for gateway connection type).
    - Manage Thin Image Advanced Pair (available only for gateway connection type).


#  [3.0.1] 
# # Bugfixes
- **Miscellaneous 1:** Fixed multiple session auth issue for 'direct connect' connection type.
- **Miscellaneous 2:** Fixed Python older version issue, no sudo user installation issue.
- **hv_lun_facts:** Modified the parameter name from `naa_id` to `canonical_name` (available only for gateway connection type).
- **hv_storagesystem:** Storage system remains in spare pool after user off-boarded the storage from UAI Gateway.
- **hv_sds_block_compute_node_facts:** Fixed issue where the module was not returning the correct compute node information.
- **hv_sds_block_chap_user:** Updated the playbook file with the correct parameter name.
- **hv_storagesystem_facts:** Fixed compatibility issue with Python lower than 3.11.
- **hv_storagepool_facts:** Fixed compatibility issue with Python lower than 3.11.
- **hv_lun_facts:** Fixed LDEV ID not being returned in the facts in case of a `0` value.

#  [3.0.0] - Release Date: 2024-06-17
# # New Modules
- **hv_sds_block_chap_user_facts:** Retrieves information about Hitachi SDS block storage system CHAP users.
- **hv_sds_block_chap_user:** Manages Hitachi SDS block storage system CHAP users.
- **hv_sds_block_compute_node_facts:** Retrieves information about Hitachi SDS block storage system compute nodes.
- **hv_sds_block_compute_node:** Manages Hitachi SDS block storage system compute nodes.
- **hv_sds_block_compute_port_authentication:** Manages Hitachi SDS block storage system compute port authentication mode settings.
- **hv_sds_block_port_facts:** Retrieves information about Hitachi SDS block storage system compute ports.
- **hv_sds_block_storage_system_facts:** Retrieves information about a specific Hitachi SDS block storage system.
- **hv_sds_block_volume_facts:** Retrieves information about Hitachi SDS block storage system volumes.
- **hv_sds_block_volume:** Manages Hitachi SDS block storage system volumes.

- **hv_gateway_admin_password:** Updates the password of gateway admin on Hitachi VSP storage systems.
- **hv_gateway_subscriber_facts:** Retrieves information about a subscriber on Hitachi VSP storage systems.
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
- **hv_uaig_token_facts:** Retrieves an API token for the Hitachi gateway service host.