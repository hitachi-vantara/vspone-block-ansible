=================================================================
Hitachi Vantara VSP One Block Collection Release Notes
==================================================================

.. contents:: Topics

This changelog describes changes after version 2.0.0.

v3.2.0
=======

Release Summary
---------------
This is a minor release of the ``hitachivantara.vspone_block`` collection.
This changelog includes all new modules that are added to the collection. This also contains all changes to the modules and plugins in this
collection that have been made after the previous release.

New Modules
-----------
- The following modules are added to the collection:
    - ``hv_cmd_dev``: This module is used to create, update, and delete command devices.
    - ``hv_disk_drive``: This module is used to change disk drive settings.
    - ``hv_journal_volume``: This module is used to create, update, and delete journal volumes.
    - ``hv_nvm_subsystems``: This module is used to create, update, and delete NVM subsystems.
    - ``hv_paritygroup``: This module is used to create, update, and delete parity group.
    - ``hv_remote_copy_group``: This module is used to create, update, and delete remote copy groups.
    - ``hv_remote_storage_registration``: This module is used to manage remote storage registration and unregistration.
    - ``hv_resource_group_lock``: This module is used to lock and unlock resource groups.
    - ``hv_resource_group``: This module is used to create, update, and delete resource groups.
    - ``hv_snapshot_group``: This module is used to create, update, and delete snapshots in units of snapshot groups.

- The following facts modules are added in the collection:
    - ``hv_disk_drive_facts``: This module is used to get facts about disk drives.
    - ``hv_journal_volume_facts``: This module is used to get facts about journal volumes.
    - ``hv_remote_copy_group_facts``: This module is used to get facts about remote copy groups.
    - ``hv_remote_storage_registration_facts``: This module is used to get facts about remote storage registration.
    - ``hv_resource_group_facts``: This module is used to get facts about resource groups.
    - ``hv_snapshot_group_facts``: This module is used to get facts about snapshots in units of snapshot groups.

Updated Modules
---------------
- The following modules are updated in the collection:
    - ``hv_gad_facts``: Added GAD Pair facts for direct connection type.
    - ``hv_gad``: Added multiple operations for GAD pair for direct connection type; Increased GAD pair volumes size support; SVOL naming enhancements.
    - ``hv_hg``: Added auto-generated name for create hostgroup tasks.
    - ``hv_hur_fact``: Added HUR Pair facts for direct connection type.
    - ``hv_hur``: Added multiple operations for HUR pair for direct connection type; Increased HUR pair volumes size support.
    - ``hv_iscsi_target``: Added auto-generated name for create iSCSI target task.
    - ``hv_ldev_facts``: Added encryption status in LDEV facts.
    - ``hv_ldev``: Added QoS settings and shredding option; enhanced LDEV ID setting.
    - ``hv_snapshot``: Enhanced SVOL naming logic.
    - ``hv_storagepool_facts``: Added encryption status.
    - ``hv_system_facts``: Added refresh parameter.
    - ``hv_truecopy_fact``: Added TrueCopy pair facts for direct connection type.
    - ``hv_truecopy``: Added multiple operations for TrueCopy pair for direct connection type; Enhanced SVOL ID setting.
    - ``others``: Enhanced log messages; Added warnings for unsupported OOB features; Usage information collection to AWS with user consent.

v3.1.0
=======

Release Summary
---------------
This is a minor release of the ``hitachivantara.vspone_block`` collection.
This changelog includes all new modules that are added to the collection. This also contains all changes to the modules and plugins in this
collection that have been made after the previous release.

New Modules
-----------
- The following modules are added to the collection:
    - ``hv_sds_block_vps``: This module is used to create, update, and delete VPS.
    - ``hv_gad``: This module is used to create, update, and delete GAD pairs.
    - ``hv_hur``: This module is used to create, update, and delete HUR pairs.
    - ``hv_gateway_unsubscribe_resource``: This module is used to unsubscribe resources.
    - ``hv_storage_port``: This module is used to update storage port settings.
    - ``hv_storagepool``: This module is used to create, update, and delete storage pools.
    - ``hv_truecopy``: This module is used to create, update, and delete TrueCopy pairs.

- The following facts modules are added in the collection:
    - ``hv_sds_block_vps_fact``: This module is used to get facts about VPS.
    - ``hv_gad_fact``: This module is used to get facts about GAD pairs.
    - ``hv_hur_fact``: This module is used to get facts about HUR pairs.
    - ``hv_gateway_subscription_facts``: This module is used to get facts of a subscriber.
    - ``hv_nvm_subsystems_facts``: This module is used to get facts about NVM subsystems.
    - ``hv_storage_port_facts``: This module is used to get facts about storage ports.
    - ``hv_truecopy_facts``: This module is used to get facts about TrueCopy pairs.

Updated Modules
---------------
- The following modules are updated in the collection:
    - ``hv_sds_block_compute_node``: Manage Compute Node with NVMe-TCP connection.
    - ``hv_sds_block_compute_node_facts``: Get Compute Node with NVMe-TCP details.
    - ``hv_sds_block_volume``: Create and Update Volume with QoS Settings.
    - ``hv_sds_block_volume_facts``: Get NVMe-TCP volume details; Get detailed Compute Node and QoS information.
    - ``hv_ldev``: Enhanced deletion and provisioning workflows.
    - ``hv_ldev_facts``: Added detailed LDEV information retrieval.
    - ``hv_snapshot``: Enhanced Thin Image creation and management.
    - ``others``: Renamed module: hv_lun to hv_ldev; Updated parameter names: lun to ldev, pvol to primary_volume_id, svol to secondary_volume_id.

v3.0.1
=======

Release Summary
---------------
This is a minor release of the ``hitachivantara.vspone_block`` collection.
This release contains only bug fixes.

Bugfixes
---------
- The following bugs are fixed in this release:
    - Fixed multiple session auth issue for direct connect type.
    - Fixed Python older version compatibility issues.
    - Fixed incorrect compute node information retrieval in hv_sds_block_compute_node_facts.
    - Fixed LDEV ID retrieval issue in hv_lun_facts.

v3.0.0
=======

Release Summary
---------------
This is a minor release of the ``hitachivantara.vspone_block`` collection.
This changelog includes all new modules that are added to the collection. This also contains all changes to the modules and plugins in this
collection that have been made after the previous release.

New Modules
-----------
- The following modules are added to the collection:
    - ``hv_sds_block_chap_user``: This module is used to create, update, and delete CHAP users.
    - ``hv_sds_block_compute_node``: This module is used to create, update, and delete compute nodes.
    - ``hv_sds_block_compute_port_authentication``: This module is used to update port authentication settings.
    - ``hv_sds_block_volume``: This module is used to create, update, and delete volumes.
    - ``hv_gateway_admin_password``: This module is used to update admin password.
    - ``hv_sds_block_compute_node``: This module is used to create, update, and delete subscribers.
    - ``hv_hg``: This module is used to create, update, and delete host groups.
    - ``hv_iscsi_target``: This module is used to create, update, and delete iSCSI targets.
    - ``hv_lun``: This module is used to create, update, and delete luns/LDEVs.
    - ``hv_shadow_image_pair``: This module is used to create, update, and delete shadow image pairs.
    - ``hv_snapshot``: This module is used to create, update, and delete snapshots.
    - ``hv_storagesystem``: This module is used to create, update, and delete storage systems.

- The following facts modules are added in the collection:
    - ``hv_sds_block_chap_user_facts``: This module is used to get facts about CHAP users.
    - ``hv_sds_block_compute_node_facts``: This module is used to get facts about compute nodes.
    - ``hv_sds_block_storage_system_fact``: This module is used to get facts about storage systems.
    - ``hv_sds_block_volume_facts``: This module is used to get facts about volumes.
    - ``hv_gateway_subscriber_fact``: This module is used to get facts about subscribers.
    - ``hv_snapshot_facts``: This module is used to get facts about snapshots in units of LUNs.
    - ``hv_iscsi_target_facts``: This module is used to get facts about iSCSI targets.
    - ``hv_lun_facts``: This module is used to get facts about luns/LDEVs.
    - ``hv_paritygroup_facts``: This module is used to get facts about parity groups.
    - ``hv_shadow_image_pair_facts``: This module is used to get facts about shadow image pairs.
    - ``hv_snapshot_facts``: This module is used to get facts about snapshots.
    - ``hv_storagepool_facts``: This module is used to get facts about the storage pools.
    - ``hv_storagesystem_facts``: This module is used to get facts about the storage system.
    - ``hv_system_facts``: This module is used to get facts about systems.
    - ``hv_troubleshooting_facts``: This module is used to get logs.
    - ``hv_uaig_token_facts``: This module is used to get API token for the gateway.
