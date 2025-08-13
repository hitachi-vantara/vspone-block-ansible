==========================================
Hitachivantara.Vspone\_Block Release Notes
==========================================

.. contents:: Topics

v4.1.0
======

Release Summary
---------------

This minor release of `hitachivantara.vspone_block` adds new modules, enhances existing features, and includes various bug fixes.

Minor Changes
-------------

- Added a new `"hv_journal"` module as a replacement for the `"hv_journal_volume"` module.
- Added a new `"hv_journal_facts"` module as a replacement for the `"hv_journal_volume_facts"` module.
- Added a new `"hv_sds_block_authentication_ticket"` module to create, delete and update authentication tickets.
- Added a new `"hv_sds_block_cluster"` module to add and remove storage nodes from the cluster, and download cluster configuration files.
- Added a new `"hv_sds_block_cluster_config_facts"` module to retrieve information about SDS block cluster configurations.
- Added a new `"hv_sds_block_control_port_facts"` module to retrieve control port information from SDS block cluster.
- Added a new `"hv_sds_block_drives_facts"` module to retrieve drive information from SDS block cluster.
- Added a new `"hv_sds_block_event_logs_facts"` module to retrieve event logs from SDS block cluster.
- Added a new `"hv_sds_block_fault_domain_facts"` module to retrieve fault domains information from SDS block cluster.
- Added a new `"hv_sds_block_internode_port_facts"` module to retrieve internode port information from SDS block cluster.
- Added a new `"hv_sds_block_job_facts"` module to retrieve job details from SDS block cluster.
- Added a new `"hv_sds_block_protection_domain_facts"` module to retrieve protection domains from SDS block cluster.
- Added a new `"hv_sds_block_snapshot"` module to manage snapshots on SDS block cluster.
- Added a new `"hv_sds_block_snapshot_facts"` module to retrieve snapshot information from SDS block cluster.
- Added a new `"hv_sds_block_storage_controller_facts"` module to retrieve storage controller information from SDS block cluster.
- Added a new `"hv_sds_block_storage_network_setting_facts"` module to retrieve storage network settings from SDS block cluster.
- Added a new `"hv_sds_block_storage_node"` module to block and restore storage nodes.
- Added a new `"hv_sds_block_storage_node_facts"` module to retrieve information about storage nodes.
- Added a new `"hv_sds_block_storage_node_network_settings_facts"` module to retrieve storage node network settings from SDS block cluster.
- Added a new `"hv_sds_block_storage_pool"` module to expand storage pools on SDS block cluster.
- Added a new `"hv_sds_block_storage_pool_facts"` module to retrieve storage pools from SDS block cluster.
- Added a new `"hv_sds_block_storage_time_facts"` module to retrieve storage time from SDS block cluster.
- Added a new `"hv_sds_block_user"` module to create and update users on SDS block cluster.
- Added a new `"hv_sds_block_user_facts"` module to retrieve users on SDS block cluster.
- Note `"hv_journal_volume"` and `"hv_journal_volume_facts"` modules will be deprecated from future release.

New Modules
-----------

Sds Block
~~~~~~~~~

- hitachivantara.vspone_block.sds_block.hv_sds_block_authentication_ticket - Manages Hitachi SDS block storage system authentication tickets.
- hitachivantara.vspone_block.sds_block.hv_sds_block_cluster - Manages storage cluster on Hitachi SDS block storage systems.
- hitachivantara.vspone_block.sds_block.hv_sds_block_cluster_config_facts - Retrieves information about configuration of SDS block clusters from Hitachi SDS block storage systems.
- hitachivantara.vspone_block.sds_block.hv_sds_block_control_port_facts - Get control port from storage system.
- hitachivantara.vspone_block.sds_block.hv_sds_block_drives_facts - Get drives from storage system.
- hitachivantara.vspone_block.sds_block.hv_sds_block_event_logs_facts - Get event logs from storage system.
- hitachivantara.vspone_block.sds_block.hv_sds_block_fault_domain_facts - Get fault domains from storage system.
- hitachivantara.vspone_block.sds_block.hv_sds_block_internode_port_facts - Get internode port from storage system.
- hitachivantara.vspone_block.sds_block.hv_sds_block_job_facts - Retrieves information about Hitachi SDS block storage system storage nodes.
- hitachivantara.vspone_block.sds_block.hv_sds_block_protection_domain_facts - Get protection domains  from storage system.
- hitachivantara.vspone_block.sds_block.hv_sds_block_snapshot - Manages snapshots on Hitachi SDS Block storage systems.
- hitachivantara.vspone_block.sds_block.hv_sds_block_snapshot_facts - Gather facts about snapshots on Hitachi SDS Block storage systems.
- hitachivantara.vspone_block.sds_block.hv_sds_block_storage_controller_facts - Get storage_controllers from storage system.
- hitachivantara.vspone_block.sds_block.hv_sds_block_storage_network_setting_facts - Get storage network settings from storage system.
- hitachivantara.vspone_block.sds_block.hv_sds_block_storage_node - Manages storage node on Hitachi VSP storage systems.
- hitachivantara.vspone_block.sds_block.hv_sds_block_storage_node_facts - Retrieves information about Hitachi SDS block storage system storage nodes.
- hitachivantara.vspone_block.sds_block.hv_sds_block_storage_node_network_settings_facts - Get storage node network settings  from storage system.
- hitachivantara.vspone_block.sds_block.hv_sds_block_storage_pool - Manages storage pool on Hitachi VSP storage systems.
- hitachivantara.vspone_block.sds_block.hv_sds_block_storage_pool_facts - Retrieves information about Hitachi SDS block storage system storage pools.
- hitachivantara.vspone_block.sds_block.hv_sds_block_storage_time_facts - Get storage time from storage system.
- hitachivantara.vspone_block.sds_block.hv_sds_block_user - Create and update users from storage system.
- hitachivantara.vspone_block.sds_block.hv_sds_block_user_facts - Get users from storage system.

v4.0.0
======

Release Summary
---------------

This minor release of `hitachivantara.vspone_block` adds new modules, enhances existing features, and includes various bug fixes.

Minor Changes
-------------

- Added a new `"hv_audit_log_transfer_dest"` module to set the transfer destinations of audit log files using UDP/TCP ports.
- Added a new `"hv_audit_log_transfer_dest_facts"` module to get information about the transfer destinations of audit log files.
- Added a new `"hv_clpr"` module to create, update, and delete CLPR information.
- Added a new `"hv_clpr_facts"` module to get CLPR information.
- Added a new `"hv_external_paritygroup"` module to assign external volume groups to a CLPR.
- Added a new `"hv_external_paritygroup"` module to change the MP blade assigned to an external volume group.
- Added a new `"hv_server_priority_manager"` module to set, change, and delete Server Priority Manager information.
- Added a new `"hv_server_priority_manager_facts"` module to get Server Priority Manager information.
- Added a new `"hv_snmp_setting"` module to manage SNMP settings.
- Added a new `"hv_snmp_settings_facts"` module to get SNMP settings for a storage system.
- Added a new `"hv_storage_system"` module to set the date and time in a storage system with NTP disabled/enabled.
- Added a new `"hv_storage_system_monitor_facts"` module to get alert, hardware installed, and channel board information.
- Added a new `"hv_upload_file"` module to upload a primary/secondary client certificate file to a storage system for audit log.
- Added support for a secondary volume takeover HUR pair to the `"hv_hur"` module.
- Added support for assigning a CLPR ID to a parity group to the `"hv_paritygroup"` module.
- Added support for changing pool settings by pool name and by pool ID with new parameters to the `"hv_storage_pool"` module.
- Added support for creating a HUR pair with `"provisioned_secondary_volume_id"` to the `"hv_hur"`, `"hv_gad"` and `"hv_truecopy"` modules.
- Added support for creating a pair with `"provisioned_secondary_volume_id"` and hostgroups to the `"hv_hur"` , `"hv_gad"` and `"hv_truecopy"` modules.
- Added support for creating a storage pool with a specific pool ID and LDEV numbers to the `"hv_storage_pool"` module.
- Added support for creating a storage pool with a specific pool ID and start and end LDEV numbers to the `"hv_storage_pool"` module.
- Added support for deleting a pool including pool volumes to the `"hv_storage_pool"` module.
- Added support for getting a list of time zones that can be used in a storage system to the `"hv_storagesystem_facts"` module.
- Added support for getting free LDEV IDs to the `"hv_ldev_facts"` module.
- Added support for initializing the capacity saving function for a pool to the `"hv_storage_pool"` module.
- Added support for performing tier relocation of a pool to the `"hv_storage_pool"` module.
- Added support for restoring a pool to the `"hv_storage_pool"` module.
- Added support for running performance monitoring of a pool to the `"hv_storage_pool"` module.
- Added support for setting the CLPR ID of a volume to the `"hv_ldev"` module.
- Added support for taking over a remote copy group for the HUR replication type to the `"hv_remote_copy_group"` module.
- Enhanced the `"hv_storagepool_facts"` module to support additional output parameters.
- Removed query for ports, quorum disks, journalPools, and freeLogicalUnitList from the `"hv_storagesystem_facts"` module.

Removed Features (previously deprecated)
----------------------------------------

- `hv_gateway_admin_password` module has been removed.
- `hv_gateway_subscriber_facts` module has been removed.
- `hv_gateway_subscriber` module has been removed.
- `hv_gateway_subscription_facts` module has been removed.
- `hv_gateway_unsubscribe_resource` module has been removed.
- `hv_storagesystem` module has been removed.
- `hv_system_facts` module has been removed.
- `hv_uaig_token_facts` module has been removed.

New Modules
-----------

Vsp
~~~

- hitachivantara.vspone_block.vsp.hv_audit_log_transfer_dest - This module specifies settings related to the transfer of audit log files from a storage system to the syslog servers.
- hitachivantara.vspone_block.vsp.hv_audit_log_transfer_dest_facts - Retrieves about the settings related to the transfer of audit log files to the syslog servers.
- hitachivantara.vspone_block.vsp.hv_external_paritygroup - Manages assignment of MP blade and CLPR to an External Parity Group from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_server_priority_manager - Manage Server Priority Manager information on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_server_priority_manager_facts - Retrieves Server Priority Manager information from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_snmp_settings - Manage SNMP settings on Hitachi Vantara storage systems.
- hitachivantara.vspone_block.vsp.hv_snmp_settings_facts - Retrieves SNMP configuration from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_storage_system - This module specifies storage systems settings like updating the date and time.
- hitachivantara.vspone_block.vsp.hv_storage_system_monitor_facts - Retrieves alerts, hardware installed, and channel boards information from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_upload_file - This uploads the files required to set the transfer destination of audit log files.

v3.5.1
======

Release Summary
---------------

This minor release of `hitachivantara.vspone_block` adds new modules, enhances existing features, and includes various bug fixes.

Bugfixes
--------

- Resolved an issue where adding a path to an external path group for FC and retrieving external path group facts would fail.

v3.5.0
======

Release Summary
---------------

This minor release of `hitachivantara.vspone_block` introduces several new modules, improves existing functionality and bug fixes.

Minor Changes
-------------

- Added additional parameters primary_volume_device_group_name and secondary_volume_device_group_name to retrieve ShadowImage group details more quickly.
- Added new module `hv_external_paritygroup_facts` to retrieve information about External Parity Group.
- Added new module `hv_external_path_group_facts` to retrieve information about External Path Group.
- Added new module `hv_external_path_group` to manage External Path Groups.
- Added new module `hv_mp_facts` to retrieve MP Blades information from VSP storage models.
- Added support for begin_secondary_volume_id and end_secondary_volume_id to the remote replication modules - hv_gad, hv_hur, hv_truecopy.
- Added support for cloning a Thin Image pair to the hv_snapshot module.
- Added support for cloning pairs in a specified snapshot group to the hv_snapshot_group module.
- Added support for deleting an iSCSI name of an external storage system that is registered to a port on the local storage system to the hv_storage_port module.
- Added support for deleting garbage data for all Thin Image pairs in a snapshot tree to the hv_snapshot module.
- Added support for disconnecting from a volume on the external storage system to the hv_external_volume module.
- Added support for getting a list of LUs defined for a port on an external storage system to the hv_storage_port_facts module.
- Added support for getting a list of ports on an external storage system to the hv_storage_port_facts module.
- Added support for getting information about a specific LU path to the hv_hostgroup_facts module.
- Added support for getting information about a specific LU path to the hv_iscsi_target_facts module.
- Added support for getting information about an iSCSI target of a port on an external storage system to the hv_storage_port_facts module.
- Added support for getting the iSCSI name of an external storage system that is registered to a port on the local storage system to the hv_storage_port_facts module.
- Added support for lun_id for the secondary host group for TC and HUR. For GAD, lun_id and enable_preferred_path are supported.
- Added support for performing a login test on an iSCSI target of an external storage system that is registered to a port on the local storage system to the hv_storage_port module.
- Added support for reclaiming the zero pages of a DP volume to the hv_ldev module.
- Added support for registering an iSCSI name of an external storage system to a port on the local storage system to the hv_storage_port module.
- Added support for releasing the host reservation status by specifying a host group to the hv_hostgroup module.
- Added support for releasing the host reservation status by specifying an iSCSI target to the hv_iscsi_target module.
- Added support for releasing the host reservation status by specifying the LU path to the hv_hostgroup module.
- Added support for releasing the host reservation status by specifying the LU path to the hv_iscsi_target module.
- Added support for setting the nickname for a WWN to the hv_hostgroup module.
- Added support for setting the nickname for an iSCSI name to the hv_iscsi_target module.
- Added support for setting the nickname of an IQN initiator to the hv_iscsi_target module.
- Added the ability to change the settings of the following parameters of an LDEV using the hv_ldev module - data_reduction_process_mode, is_compression_acceleration_enabled, is_relocation_enabled,is_full_allocation_enabled, is_alua_enabled
- Added the ability to format a volume to the hv_ldev module.
- Added the ability to set the nick_name of an iSCSI using the hv_iscsi_target module.
- Added the following new parameters to the output of hv_ldev_facts is_compression_acceleration_enabled, data_reduction_process_mode, is_relocation_enabled, is_full_allocation_enabled
- Added the following parameters to creating an LDEV using the hv_ldev module is_parallel_execution_enabled, start_ldev_id, end_ldev_id, external_parity_group, is_compression_acceleration_enabled
- Enabled host group name together with port ID as identifiers for a host group.
- Enabled the iSCSI target name together with the port ID as identifiers for the iSCSI target.if both ID and name are specified, the ID is used together with the port ID as the iSCSI target identifier.

Bugfixes
--------

- Fixed output details of `host_group_number` and `host_group_id` in `hv_hg` and 'hv_hg_facts' modules to be consistent.

New Modules
-----------

Vsp
~~~

- hitachivantara.vspone_block.vsp.hv_external_paritygroup_facts - Retrieves information about External Parity Group from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_external_path_group - Manages External Path Groups in the Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_external_path_group_facts - Retrieves information about External Path Group from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_mp_facts - Retrieves MP blades information from Hitachi VSP storage systems.

v3.4.2
======

Release Summary
---------------

This minor release of `hitachivantara.vspone_block` bugfixes and improves existing functionality.

Bugfixes
--------

- Fixed the mapping lun to multiple HostGroup/Iscsi Target issues for remote replication.
- Resolved various documentation inconsistencies.

v3.4.1
======

Release Summary
---------------

This minor release of `hitachivantara.vspone_block` introduces several new modules and improves existing functionality.

Minor Changes
-------------

- Added back 'mu_number' parameter to the `hv_gad` module.
- Resolved various documentation inconsistencies.

v3.4.0
======

Release Summary
---------------

This minor release of `hitachivantara.vspone_block` introduces several new modules and improves existing functionality.

Minor Changes
-------------

- Added iSCSI target support for GAD, TrueCopy, HUR, ShadowImage, and Snapshot/ThinImage modules.
- Added new module `hv_ddp_pool_facts` to retrieve DDP-based pool details on VSP One Block storage models.
- Added new module `hv_ddp_pool` to create, update, and delete DDP-based pools on VSP One Block storage models.
- Added support to delete SVOL post-pair deletion for GAD, TrueCopy, HUR, ShadowImage, and Snapshot/ThinImage modules.
- Enhanced `hv_ldev_facts` module to support query parameters.
- Enhanced `hv_shadow_image` module: support for local copy group and copy pair name for shadow image pair management; group management of shadow image pairs.
- Enhanced `hv_snapshot_group` module to support retention period.
- Enhanced `hv_snapshot` module: added copy speed, clones automation, retention period, support for Floating Snapshot, and pair creation with specific or auto-selected SVOL and mirror unit.
- Enhanced `hv_storage_port` module to support attributes like connection, speed, and type.
- Removed gateway connection type from all the modules.

New Modules
-----------

Vsp
~~~

- hitachivantara.vspone_block.vsp.hv_ddp_pool - Manages DDP Pools on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_ddp_pool_facts - Get facts of DDP Pools on Hitachi VSP storage systems.

v3.3.0
======

Release Summary
---------------

This minor release of `hitachivantara.vspone_block` introduces several new modules and improves existing functionality.

Minor Changes
-------------

- Added NVMe-TCP and NVMe-FC support for GAD, TrueCopy, HUR, ShadowImage, and Snapshot/ThinImage modules.
- Added new facts module `hv_external_volume_facts` to retrieve external volume details.
- Added new facts module `hv_iscsi_remote_connection_facts` to retrieve iSCSI remote connection details.
- Added new facts module `hv_quorum_disk_facts` to retrieve quorum disk details.
- Added new facts module `hv_remote_connection_facts` to retrieve remote connection details.
- Added new facts module `hv_user_facts` to retrieve user details.
- Added new facts module `hv_user_group_facts` to retrieve user group details.
- Added new module `hv_external_volume` to create, and delete external volumes.
- Added new module `hv_iscsi_remote_connection` to create, and delete iSCSI remote connections.
- Added new module `hv_quorum_disk` to register, and deregister quorum disks.
- Added new module `hv_remote_connection` to create, update, and delete remote connections.
- Added new module `hv_user_group` to create, update, and delete user groups.
- Added new module `hv_user` to create, update, and delete users.
- The state 'resize' has been changed to 'expand' for `hv_gad`, `hv_hur` and `hv_truecopy` modules to expand the size of the copy pair.
- Updated `hv_snapshot_group_facts` to retrieve all snapshot group details.

Bugfixes
--------

- Added ansible_facts parameter to all the facts modules as per the ansible facts module standard.
- Done some enhancements related to the module documentation like formatting, examples, and descriptions.
- For remote replication pairs, if the free LDEV ID for SVOL was not part of the meta resource group, the pair creation failed. Now the module will automatically select a free LDEV ID from the metadata resource group.
- Made storage_system_info optional field for direct connection type modules.

New Modules
-----------

Vsp
~~~

- hitachivantara.vspone_block.vsp.hv_external_volume - Manages External Volumes in the Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_external_volume_facts - Retrieves information about External Volume from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_iscsi_remote_connection - Manages Remote connections through iSCSI ports on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_iscsi_remote_connection_facts - Retrieves Remote connection details from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_quorum_disk - Manages Quorum Disks in the Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_quorum_disk_facts - Retrieves information about Quorum Disks from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_remote_connection - Manages Remote connections on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_remote_connection_facts - Retrieves Remote connection details from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_user - Manages users on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_user_facts - Retrieves user information from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_user_group - Manages user groups on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_user_group_facts - Retrieves user group information from Hitachi VSP storage systems.

v3.2.0
======

Release Summary
---------------

This minor release of `hitachivantara.vspone_block` adds multiple new modules and enhances existing ones.

Minor Changes
-------------

- Added new facts module `hv_disk_drive_facts` to retrieve disk drive details.
- Added new facts module `hv_journal_volume_facts` to retrieve journal volume details.
- Added new facts module `hv_remote_copy_group_facts` to retrieve remote copy group details.
- Added new facts module `hv_remote_storage_registration_facts` to retrieve remote storage registration details.
- Added new facts module `hv_resource_group_facts` to retrieve resource group details.
- Added new facts module `hv_snapshot_group_facts` to retrieve snapshot group details.
- Added new module `hv_cmd_dev` to create, update, and delete command devices.
- Added new module `hv_disk_drive` to change disk drive settings.
- Added new module `hv_journal_volume` to create, update, and delete journal volumes.
- Added new module `hv_nvm_subsystems` to create, update, and delete NVM subsystems.
- Added new module `hv_paritygroup` to create, update, and delete parity groups.
- Added new module `hv_remote_copy_group` to create, update, and delete remote copy groups.
- Added new module `hv_remote_storage_registration` to manage remote storage registration and un-registration.
- Added new module `hv_resource_group_lock` to lock and unlock resource groups.
- Added new module `hv_resource_group` to create, update, and delete resource groups.
- Added new module `hv_snapshot_group` to create, update, and delete snapshots in units of snapshot groups.
- Added warnings for unsupported OOB features.
- Enhanced log messages.
- Introduced usage information collection to AWS with user consent.
- Updated `hv_gad_facts` to add GAD Pair facts for direct connection type.
- Updated `hv_gad` to support multiple operations for GAD pair for direct connection type, increased GAD pair volume size support, and enhanced SVOL naming.
- Updated `hv_hg` to add auto-generated name for hostgroup creation.
- Updated `hv_hur_fact` to add HUR Pair facts for direct connection type.
- Updated `hv_hur` to support multiple operations for HUR pair for direct connection type and increased HUR pair volume size support.
- Updated `hv_iscsi_target` to add auto-generated name for create iSCSI target task.
- Updated `hv_ldev_facts` to include encryption status in LDEV facts.
- Updated `hv_ldev` to add QoS settings, shredding option, and enhanced LDEV ID setting.
- Updated `hv_snapshot` to enhance SVOL naming logic.
- Updated `hv_storagepool_facts` to include encryption status.
- Updated `hv_system_facts` to add refresh parameter.
- Updated `hv_truecopy_fact` to add TrueCopy pair facts for direct connection type.
- Updated `hv_truecopy` to support multiple operations for TrueCopy pair for direct connection type and enhanced SVOL ID setting.

Bugfixes
--------

- Added missing details to enhance user understanding.
- Improved formatting and structure for better readability.
- Resolved inconsistencies in the documentation.

New Modules
-----------

Vsp
~~~

- hitachivantara.vspone_block.vsp.hv_cmd_dev - Manages command devices on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_disk_drive - Changes disk drive settings from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_disk_drive_facts - Retrieves information about hard drives from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_journal_volume_facts - Retrieves information about Journal Volumes from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_nvm_subsystems - Manages NVM subsystems on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_paritygroup - Create, delete parity group from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_remote_copy_group - Manages Remote Copy Group on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_remote_copy_group_facts - Retrieves Remote Copy Groups information from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_remote_storage_registration - Manages remote storage registration and unregistration on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_remote_storage_registration_facts - Retrieves remote storage registration information from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_resource_group - Manages resource groups on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_resource_group_facts - Retrieves resource group information from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_resource_group_lock - Allows the locking and unlocking of resource groups on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_snapshot_group - Manages snapshots in units of snapshot groups on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_snapshot_group_facts - Retrieves snapshot information in units of snapshot groups from Hitachi VSP storage systems.

v3.1.0
======

Release Summary
---------------

This minor release of `hitachivantara.vspone_block` introduces new modules and improvements to storage management.

Minor Changes
-------------

- Added new facts module `hv_gad_fact` to retrieve GAD pair details.
- Added new facts module `hv_gateway_subscription_facts` to retrieve subscriber details.
- Added new facts module `hv_hur_fact` to retrieve HUR pair details.
- Added new facts module `hv_nvm_subsystems_facts` to retrieve NVM subsystem details.
- Added new facts module `hv_sds_block_vps_fact` to retrieve VPS details.
- Added new facts module `hv_storage_port_facts` to retrieve storage port details.
- Added new facts module `hv_truecopy_facts` to retrieve TrueCopy pair details.
- Added new module `hv_gad` to create, update, and delete GAD pairs.
- Added new module `hv_gateway_unsubscribe_resource` to unsubscribe resources.
- Added new module `hv_hur` to create, update, and delete HUR pairs.
- Added new module `hv_sds_block_vps` to create, update, and delete VPS.
- Added new module `hv_storage_port` to update storage port settings.
- Added new module `hv_storagepool` to create, update, and delete storage pools.
- Added new module `hv_truecopy` to create, update, and delete TrueCopy pairs.
- Renamed module `hv_lun` to `hv_ldev`.
- Renamed parameter `lun` to `ldev`, `pvol` to `primary_volume_id`, `svol` to `secondary_volume_id`.
- Updated `hv_ldev_facts` to retrieve detailed LDEV information.
- Updated `hv_ldev` to enhance deletion and provisioning workflows.
- Updated `hv_sds_block_compute_node_facts` to retrieve Compute Node with NVMe-TCP details.
- Updated `hv_sds_block_compute_node` to manage Compute Node with NVMe-TCP connection.
- Updated `hv_sds_block_volume_facts` to retrieve NVMe-TCP volume details, Compute Node, and QoS information.
- Updated `hv_sds_block_volume` to support QoS settings during volume creation and update.
- Updated `hv_snapshot` to enhance Thin Image creation and management.

New Modules
-----------

Sds Block
~~~~~~~~~

- hitachivantara.vspone_block.sds_block.hv_sds_block_vps - Manages Hitachi SDS block storage system Virtual Private Storages (VPS) volume ADR setting.
- hitachivantara.vspone_block.sds_block.hv_sds_block_vps_facts - Retrieves information about Virtual Private Storages (VPS) of Hitachi SDS block storage system.

Vsp
~~~

- hitachivantara.vspone_block.vsp.hv_gad - Manages GAD pairs on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_gad_facts - Retrieves GAD pairs information from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_gateway_subscription_facts - Retrieves information about resources of a subscriber on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_gateway_unsubscribe_resource - Manages un-subscription of resources for a subscriber on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_hur - Manages HUR pairs on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_hur_facts - Retrieves HUR information from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_nvm_subsystems_facts - Retrieves information about NVM subsystems from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_storage_port - Change the storage port settings in the Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_storagepool - Manage storage pool information on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_truecopy - Manages TrueCopy pairs on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_truecopy_facts - Retrieves TrueCopy pairs information from Hitachi VSP storage systems.

v3.0.1
======

Release Summary
---------------

This bugfix release addresses authentication, compatibility, and data retrieval issues.

Bugfixes
--------

- Fixed LDEV ID retrieval issue in `hv_lun_facts`.
- Fixed compatibility issues with older Python versions.
- Fixed incorrect compute node information retrieval in `hv_sds_block_compute_node_facts`.
- Fixed multiple session authentication issue for direct connect type.

v3.0.0
======

Release Summary
---------------

This minor release of `hitachivantara.vspone_block` introduces new modules for storage and volume management.

Minor Changes
-------------

- Added new facts module `hv_gateway_subscriber_fact`.
- Added new facts module `hv_iscsi_target_facts`.
- Added new facts module `hv_lun_facts`.
- Added new facts module `hv_paritygroup_facts`.
- Added new facts module `hv_sds_block_chap_user_facts`.
- Added new facts module `hv_sds_block_compute_node_facts`.
- Added new facts module `hv_sds_block_storage_system_fact`.
- Added new facts module `hv_sds_block_volume_facts`.
- Added new facts module `hv_shadow_image_pair_facts`.
- Added new facts module `hv_snapshot_facts`.
- Added new facts module `hv_storagepool_facts`.
- Added new facts module `hv_storagesystem_facts`.
- Added new facts module `hv_system_facts`.
- Added new facts module `hv_troubleshooting_facts`.
- Added new facts module `hv_uaig_token_facts`.
- Added new module `hv_gateway_admin_password`.
- Added new module `hv_hg`.
- Added new module `hv_iscsi_target`.
- Added new module `hv_lun`.
- Added new module `hv_sds_block_chap_user`.
- Added new module `hv_sds_block_compute_node`.
- Added new module `hv_sds_block_compute_port_authentication`.
- Added new module `hv_sds_block_volume`.
- Added new module `hv_shadow_image_pair`.
- Added new module `hv_snapshot`.
- Added new module `hv_storagesystem`.

New Modules
-----------

Sds Block
~~~~~~~~~

- hitachivantara.vspone_block.sds_block.hv_sds_block_chap_user - Manages Hitachi SDS block storage system CHAP users.
- hitachivantara.vspone_block.sds_block.hv_sds_block_chap_user_facts - Retrieves information about Hitachi SDS block storage system CHAP users.
- hitachivantara.vspone_block.sds_block.hv_sds_block_compute_node - Manages Hitachi SDS block storage system compute nodes.
- hitachivantara.vspone_block.sds_block.hv_sds_block_compute_node_facts - Retrieves information about Hitachi SDS block storage system compute nodes.
- hitachivantara.vspone_block.sds_block.hv_sds_block_compute_port_authentication - Manages Hitachi SDS block storage system compute port authentication mode settings.
- hitachivantara.vspone_block.sds_block.hv_sds_block_port_facts - Retrieves information about Hitachi SDS block storage system compute ports.
- hitachivantara.vspone_block.sds_block.hv_sds_block_storage_system_facts - Retrieves information about a specific Hitachi SDS block storage system.
- hitachivantara.vspone_block.sds_block.hv_sds_block_volume - Manages Hitachi SDS block storage system volumes.
- hitachivantara.vspone_block.sds_block.hv_sds_block_volume_facts - Retrieves information about Hitachi SDS block storage system volumes.

Vsp
~~~

- hitachivantara.vspone_block.vsp.hv_gateway_admin_password - Updates password of gateway admin on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_gateway_subscriber - Manages subscribers of a partner on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_gateway_subscriber_facts - Retrieves information about subscriber on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_hg - Manages host group on Hitachi VSP storage system.
- hitachivantara.vspone_block.vsp.hv_hg_facts - Retrieves host group information from a specified Hitachi VSP storage system.
- hitachivantara.vspone_block.vsp.hv_iscsi_target - Manages iscsi target on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_iscsi_target_facts - Retrieves information about iscsi targets from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_journal_volume - Create, update, expand, shrink, delete journal volume from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_ldev - Manages logical devices (LDEVs) on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_ldev_facts - Retrieves information about logical devices (LDEVs) from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_paritygroup_facts - retrieves information about parity groups from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_shadow_image_pair - Manages shadow image pairs on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_shadow_image_pair_facts - Retrieves information about shadow image pairs from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_snapshot - Manages snapshots on Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_snapshot_facts - Retrieves snapshot information from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_storage_port_facts - Retrieves storage port information from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_storagepool_facts - Retrieves storage pool information from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_storagesystem - Manages Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_storagesystem_facts - retrieves storage system information from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_system_facts - Retrieves system information from Hitachi VSP storage systems.
- hitachivantara.vspone_block.vsp.hv_troubleshooting_facts - Collects the log bundles for Hitachi ansible modules host and Hitachi gateway service host.
- hitachivantara.vspone_block.vsp.hv_uaig_token_facts - Retrieves an API token for the Hitachi gateway service host.
