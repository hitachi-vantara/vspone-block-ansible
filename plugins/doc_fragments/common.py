# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


class ModuleDocFragment:
    #  Standard documentation
    DOCUMENTATION = r"""
    options: {}
    notes:
      - This module is part of the hitachivantara.vspone_block collection.
    """
    GATEWAY_NOTE = r"""
    options: {}
    notes:
      - Connection type C(gateway) was removed starting from version 3.4.0. Please use an earlier version if you require this connection type.
    """
    DEPRECATED_NOTE = r"""
    options: {}
    notes:
      - This module is deprecated and will be removed in a future release.
    """
    CONNECTION_INFO = r"""
    options:
      connection_info:
        description: Information required to establish a connection to the storage system.
        type: dict
        required: true
        suboptions:
          address:
            description: IP address or hostname of the storage system.
            type: str
            required: true
          username:
            description: Username for authentication. This is a required field.
            type: str
            required: false
          password:
            description: Password for authentication. This is a required field.
            type: str
            required: false
          api_token:
            description: Token used to operate on locked resources.
            type: str
            required: false
    """
    CONNECTION_INFO_BASIC = r"""
      options:
        connection_info:
          description: Information required to establish a connection to the storage system.
          type: dict
          required: true
          suboptions:
            address:
              description: IP address or hostname of the storage system.
              type: str
              required: true
            username:
              description: Username for authentication. This is a required field.
              type: str
              required: true
            password:
              description: Password for authentication. This is a required field.
              type: str
              required: true
    """

    CONNECTION_WITH_TYPE = r"""
    options:
      connection_info:
        description: Information required to establish a connection to the storage system.
        type: dict
        required: true
        suboptions:
          connection_type:
            description: Type of connection to the storage system.
            type: str
            required: false
            choices: ['direct']
            default: 'direct'
          address:
            description: IP address or hostname of the storage system.
            type: str
            required: true
          username:
            description: Username for authentication. This is a required field.
            type: str
            required: false
          password:
            description: Password for authentication. This is a required field.
            type: str
            required: false
          api_token:
            description: Token used to operate on locked resources.
            type: str
            required: false
    """

    CONNECTION_WITHOUT_TOKEN = r"""
    options:
      connection_info:
        description: Information required to establish a connection to the storage system.
        type: dict
        required: true
        suboptions:
          connection_type:
            description: Type of connection to the storage system.
            type: str
            required: false
            choices: ['direct']
            default: 'direct'
          address:
            description: IP address or hostname of the storage system.
            type: str
            required: true
          username:
            description: Username for authentication. This is a required field.
            type: str
            required: true
          password:
            description: Password for authentication. This is a required field.
            type: str
            required: true
    """

    SDSB_CONNECTION_INFO = r"""
    options:
      connection_info:
        description: Information required to establish a connection to the storage system.
        type: dict
        required: true
        suboptions:
          connection_type:
            description: Type of connection to the storage system.
            type: str
            required: false
            choices: ['direct']
            default: 'direct'
          address:
            description: IP address or hostname of the storage system.
            type: str
            required: true
          username:
            description: Username for authentication. This is a required field.
            type: str
            required: true
          password:
            description: Password for authentication. This is a required field.
            type: str
            required: true
    """

    GAD_NOTE = r"""
    options: {}
    notes:
      - Ansible modules use a technology called copy group to manage all remote replication pair types (GAD, TC, HUR). Therefore,
        replication pairs created by tools that do not use copy group technology are not compatible with the Ansible modules. As a result,
        replication pairs created without copy group technology cannot be managed by the Ansible modules.
      - This module supports Fibre Channel, iSCSI, NVMe Fibre Channel, and NVMe TCP-based GAD pairs.
      - For GAD single server, cluster, and crosspath configurations
      - 1. Before managing a GAD pair through Ansible Direct Connect, you must register (or pair) the source and target storage systems in the source
           storage's API server. This step is required because Ansible uses REST API calls on the backend. If you skip this step—especially if you
           are unfamiliar with Hitachi's REST API—you will encounter errors when managing a GAD pair through Ansible.
           For instructions, see Manage remote storage registration.
      - 2. After creating the secondary host group, you must manually add it to the VSM resource group.
      - 3. A valid WWN should be added to the host groups (primary and secondary).
      - 4. Before executing the GAD playbook, make sure that remote paths and the quorum disk are configured correctly as mentioned in the User Guide for GAD.
      - 5. For VSM to VSM GAD, a common VSM must be created on the primary and secondary storage systems.
      - 6. Add the P-VOL and host group to the VSM. Map the P-VOL to the host group.
      - 7. After adding a P-VOL to the VSM, the virtual ID of the P-VOL becomes the 'GAD Reserve' or 65534. Hence, update the virtual ID of the P-VOL using
           the Update volume with virtual ldev task from the LDEV playbook. The P-VOL's physical and virtual ID must match.
      - 8. Add the secondary host group to the VSM.
      - 9. If the P-VOL is unnamed, the S-VOL will be assigned a name in the format smrha-[ldev_id]. If the P-VOL has a name, the S-VOL should use the
           same name. (Here, smrha stands for Storage Module Red Hat Ansible.)
    """

    GAD_FACTS_NOTE = r"""
    options: {}
    notes:
      - Currently, only pairs that belong to a copy group are retrieved. Therefore, it is recommended to delete any existing pair that is not part of
        a copy group and re-create the replication pairs using direct connect with copy group technology.
      - When working with remote replication facts (GAD, HUR, TC), it's best practice to use the task that specifies the copy group name.
        For example, Get all GAD pairs by copy group name.
    """

    HUR_NOTE = r"""
      options: {}
      notes:
      - Ansible modules use a technology called copy group to manage all remote replication pair types (GAD, TC, HUR). Therefore,
        replication pairs created by tools that do not use copy group technology are not compatible with the Ansible modules. As a result,
        replication pairs created without copy group technology cannot be managed by the Ansible modules.
      - Before managing a HUR pair through Ansible Direct Connect, you must register (or pair) the source and target storage systems in the source
        storage's API server. This step is required because Ansible uses REST API calls on the backend. If you skip this step—especially if you are
        unfamiliar with Hitachi's REST API—you will encounter errors when managing a HUR pair through Ansible.
        For instructions, see Manage remote storage registration.
      - For Create HUR pair in new copy group, with existing copy group, and using a range for secondary volume ID
      - 1. If the P-VOL is unnamed, the S-VOL will be assigned a name in the format smrha-[ldev_id]. If the P-VOL has a name, the S-VOL should
           use the same name. (Here, smrha stands for Storage Module Red Hat Ansible.)
      - For Expand HUR pair
      - 1. First, the S-VOL size is increased, followed by the P-VOL size. If the pair is in the PAIR state, it is split before resizing. Once
           the resize operation is complete, the pair is re-synchronized.
      - 2. To use this API, enable System Option Mode (SOM) 1198 and disable SOM 1199 on both primary and secondary storage systems.

    """

    HUR_FACTS_NOTE = r"""
      options: {}
      notes:
      - Currently, only pairs that belong to a copy group are retrieved. Therefore, it is recommended to delete any existing pair that is not part
        of a copy group and re-create the replication pairs using direct connect with copy group technology.
      - When working with remote replication facts (GAD, HUR, TC), it's best practice to use the task that specifies the copy group name.
        For example, Get HUR pair using copy group.
    """

    TRUE_COPY_NOTE = r"""
      options: {}
      notes:
      - Ansible modules use a technology called copy group to manage all remote replication pair types (GAD, TC, HUR). Therefore,
        replication pairs created by tools that do not use copy group technology are not compatible with the Ansible modules. As a result,
        replication pairs created without copy group technology cannot be managed by the Ansible modules.
      - Before managing a TrueCopy pair through Ansible Direct Connect, you must register (or pair) the source and target storage systems in the
        source storage's API server. This step is required because Ansible uses REST API calls on the backend. If you skip this step—especially
        if you are unfamiliar with Hitachi's REST API—you will encounter errors when managing a TrueCopy pair through Ansible.
        For instructions, see Manage remote storage registration.
      - Before creating a TrueCopy pair, add the P-VOL to the host group, iSCSI target, or NVM subsystem on the primary storage system. Then,
        identify the host group to use on the secondary storage system.
      - For Create a TrueCopy pair by specifying only the required fields, by specifying all the fields, and using a range for secondary volume ID
      - 1. If the P-VOL is unnamed, the S-VOL will be assigned a name in the format smrha-[ldev_id]. If the P-VOL has a name, the S-VOL should use
           the same name. (Here, smrha stands for Storage Module Red Hat Ansible.)
      - For Expand TrueCopy pair
      - 1. First, the S-VOL size is increased, followed by the P-VOL size. If the pair is in the PAIR state, it is split before resizing.
           Once the resize operation is complete, the pair is re-synchronized.
      - 2. To use this API, enable System Option Mode (SOM) 1198 and disable SOM 1199 on both primary and secondary storage systems.

    """

    TRUE_COPY_FACTS_NOTE = r"""
      options: {}
      notes:
      - Currently, only pairs that belong to a copy group are retrieved. Therefore, it is recommended to delete any existing pair that is not part of
        a copy group and re-create the replication pairs using direct connect with copy group technology.
      - When working with remote replication facts (GAD, HUR, TC), it's best practice to use the task that specifies the copy group name.
        For example, Get TrueCopy pair by copy group name.
    """

    REMOTE_ISCSI_CONNECTION_NOTE = r"""
      options: {}
      notes:
      - To manage remote connections, register the remote storage system with the storage system you want to manage.
    """

    REMOTE_CONNECTION_NOTE = r"""
      options: {}
      notes:
      - To manage remote connections, register the remote storage system with the storage system you want to manage.
        For the Update the remote path of an existing remote connection
      - 1. The remote paths defined in the spec will overwrite any existing remote paths.
    """

    RESOURCE_GROUPS_NOTE = r"""
      options: {}
      notes:
      - To add or remove NVM subsystems from a VSM, the NVM subsystem must not already exist or be created.
    """

    RESOURCE_GROUP_LOCKS_NOTE = r"""
      options: {}
      notes:
      - For Lock Resource Groups
      - 1. For Direct Connect,  if a lock token remains unused for Ansible tasks for more than 5 minutes, the resource
           groups will automatically unlock. To prevent this, save the lock token and reference it in the appropriate
           playbooks, or include both lock and unlock tasks within a single playbook workflow.
    """

    SHADOW_IMAGE_PAIRS_NOTE = r"""
      options: {}
      notes:
      - During automatic SVOL creation in a pair setup, the system provisions a single secondary host group/iSCSI target.
      - The ShadowImage pair supports Fibre Channel, NVMe over FC, NVMe over TCP, and iSCSI protocols.
      - In Direct mode, you can create a ShadowImage pair without specifying a secondary volume ID. Instead, provide
        the secondary pool ID in the specification. Ansible then automatically creates the S-VOL and assigns it to
        the same NVMe subsystem, host group, and iSCSI target as the P-VOL.
      - For Create a ShadowImage pair for an existing secondary volume
      - 1. When creating a ShadowImage pair, if the primary volume (P-VOL) is the same, use a different copy group
           name. If the P-VOL is different, you may reuse the same copy group name. The copy pair name must always
           be unique.
      - For Migrate ShadowImage pair
      - 1. Once the data copy and synchronization between the source and target volumes are complete, the LDEV ID
           and host I/O of the source volume are swapped with those of the target volume. From the host perspective,
           the volume and path settings remain unchanged. However, the actual data now resides on the volume prepared
           for migration.
      - For Cancel Migration of ShadowImage Pair
      - 1. If a pair migration is canceled, its status changes to SMPL, allowing you to restart the migration process.
      - For Create ShadowImage pair for an existing secondary volume for migration
      - 1. When a volume migration pair is created, its status is set to SMPL. Data remains unchanged until the migration
           process begins.
      - For Create ShadowImage pair for non-existing secondary volume for migration
      - 1. The S-VOL will be automatically created and mapped to same NVMe subsystem, host group, and iSCSI as the P-VOL.
           When a volume migration pair is created, the pair status is SMPL. Data is not copied until migration is performed.
    """

    SHADOW_IMAGE_PAIR_FACTS_NOTE = r"""
      options: {}
      notes:
      - This module displays information about ShadowImage pairs, including their ID, status, and other relevant details.
        Only pairs that belong to a copy group are retrieved. Therefore, it is recommended to remove any existing pair
        that is not part of a copy group and re-create the replication pairs using direct connect with copy group technology.
    """

    SNAPSHOTS_NOTE = r"""
      options: {}
      notes:
      - During automatic SVOL creation in a pair setup, the system provisions a single secondary host group/iSCSI target.
      - For Create a snapshot pair
      - 1. If the P-VOL is unnamed, the S-VOL will be assigned a name in the format smrha-[ldev_id]. If the P-VOL has a
           name, the S-VOL should use the same name. (Here, smrha stands for Storage Module Red Hat Ansible.)
      - 2. Only VSP One B24, B26, and B28 support Thin Image Advanced.
      - For Create snapshot pair with a new consistency group
      - 1. If the P-VOL is unnamed, the S-VOL will be assigned a name in the format smrha-[ldev_id]. If the P-VOL has a
           name, the S-VOL should use the same name. (Here, smrha stands for Storage Module Red Hat Ansible.)
      - 2. Only VSP One B24, B26, and B28 support Thin Image Advanced.
      - For Split a snapshot pair
      - 1. Splitting a snapshot pair will fail if the pair belongs to a consistency group.
      - For Restore a snapshot pair
      - 1. To restore a Thin Image and Thin Image Advanced pair, the pair must be in PSUS status. After restoration, the
           Thin Image Advanced pair remains in PSUS status, while the Thin Image pair changes to PAIR status.
      - For Delete a snapshot pair
      - 1. If the pair includes an SVOL, it is unmapped from the associated host group(s), iSCSI target(s), and NVM
           subsystem(s), and then deleted.
      - For Delete Thin Image pairs by snapshot tree
      - 1. Thin Image Advanced is not available for this task.
      - For Assign floating snapshot pair
      - 1. Thin Image Advanced pairs must have a PSUS status assigned.
      - For Unassign floating snapshot pair
      - 1. The SVOL is detached from the mapped host groups, iSCSI targets, and NVM subsystems, and then deleted.
      - For Set retention period of an existing snapshot pair
      - If your P-VOL and S-VOL are a new Thin Image (HTI) pair and the desired state is split, the workflow is
      - 1. Create the new TI pair (from two unpaired volumes).
      - 2. Split the pair to store snapshot data (so the snapshot is preserved and copy-on-write stops).
      - For Set retention period of snapshot pair after split
        If your P-VOL and S-VOL are a new Thin Image (HTI) pair and the desired state is split, the workflow is
      - 1. Create the new TI pair (from two unpaired volumes).
      - 2. Split the pair to store snapshot data (so the snapshot is preserved and copy-on-write stops).
      - For Set retention period of snapshot pair with auto split
        If your P-VOL and S-VOL are a new Thin Image (HTI) pair and the desired state is split, the workflow is
      - 1. Create the new TI pair (from two unpaired volumes).
      - 2. Split the pair to store snapshot data (so the snapshot is preserved and copy-on-write stops).
      - For Deleting garbage data of all Thin Image pairs in a snapshot tree
      - 1. Thin Image Advanced pairs do not support this task.
    """

    SNAPSHOT_FACTS_NOTE = r"""
      options: {}
      notes:
      - Currently, only pairs that belong to a copy group are retrieved. Therefore, it is recommended to delete
        any existing pair that is not part of a copy group and re-create the replication pairs using direct
        connect with copy group technology.
    """

    SNMP_SETTINGS_NOTE = r"""
      options: {}
      notes:
      - For Sending a test SNMP trap
      - 1. Sends a test SNMP trap to verify that the SIM error reporting settings are correctly configured for
           the SNMP manager. If any resources on the target storage system are locked via the REST API,
          this task cannot run. Unlock those resources before proceeding.
    """

    STORAGE_SYSTEM_NOTE = r"""
      options: {}
      notes:
      - For Set date and time in Storage System with NTP disabled
      - This feature is supported on the following block storage systems
      - 1. VSP One Block 20 series
      - 2. VSP E series
      - 3. VSP G350, G370, G700, G900
      - 4. VSP F350, F370, F700, F900
      - For Set date and time in Storage System with NTP enabled
            - This feature is supported on the following block storage systems
      - 1. VSP One Block 20 series
      - 2. VSP E series
      - 3. VSP G350, G370, G700, G900
      - 4. VSP F350, F370, F700, F900
    """

    STORAGE_SYSTEM_FACTS_NOTE = r"""
      options: {}
      notes:
      - For Get storage system facts
      - 1. Use the controller IP instead of the SVP IP to obtain storage capacity details in the task output.
    """

    SDSB_AUTHENTICATION_TICKET_NOTE = r"""
      options: {}
      notes:
      - For Issue a new authentication ticket
      - 1. This authentication ticket is used when basic or session authentication fails. It enables access
           to APIs or CLI commands—such as those for creating dump files—that support ticket-based authentication.
    """

    SDSB_CHAP_USER_NOTE = r"""
      options: {}
      notes:
      - For Update a CHAP user name and secret
      - 1. To update only the secret, provide the CHAP user ID along with the new secret.
    """

    SDSB_CLUSTER_NOTE = r"""
      options: {}
      notes:
      - For Add storage node to the cluster with the configuration file
      - 1. The configuration file can be downloaded by running the Download cluster configuration file playbook.
      - 2. This task is supported on Bare Metal, Microsoft Azure, and Google Cloud, but not on AWS.
      - For Add storage node to the cluster using ansible variables
      - 1. This task is supported on Bare Metal and Google Cloud, but not on AWS or Microsoft Azure.
      - For Remove storage node from the cluster by storage node ID
      - 1. This task is supported on Bare Metal, Google Cloud (only for storage nodes that failed during
           the Add Storage Nodes task), and Microsoft Azure, but not on AWS.
      - For Remove the storage node from the cluster by storage node name
      - 1. This task is supported on Bare Metal, Google Cloud (only for storage nodes that failed during
           the Add Storage Nodes task), and Microsoft Azure, but not on AWS.
      - For Download cluster configuration file
      - 1. Supported on Bare Metal, Google Cloud, and Microsoft Azure. Not supported on AWS.
      - For Create the cluster configuration file and then download it
      - 1. Supported on Bare Metal, Google Cloud, and Microsoft Azure. Not supported on AWS.
      - For Create the cluster configuration file for different export file types (AddStorageNodes)
      - 1. Supported on Bare Metal, Google Cloud, and Microsoft Azure. Not supported on AWS.
      - For Create the cluster configuration file for different export file types (AddDrives)
      - 1. Supported on Bare Metal, Google Cloud, and Microsoft Azure. Not supported on AWS.
      - For Create the cluster configuration file for different export file types (AWS Only)
      - 1. This task applies exclusively to AWS and requires an additional parameter, template_s3_url.
    """

    SDSB_CLUSTER_CONFIG_FACTS_NOTE = r"""
      options: {}
      notes:
      - For Get cluster configuration information
      - 1. This task is supported for VSP One SDS Block on Bare Metal and on Google Cloud, but not supported
           on AWS or Microsoft Azure.
    """

    SDSB_STORAGE_NODE_NOTE = r"""
      options: {}
      notes:
      - For Block storage node for maintenance by node ID
      - 1. The nodes will shut down after the task is complete.
      - For Block storage node for maintenance by node name
      - 1. The nodes will shut down after the task is complete.
    """

    SDSB_STORAGE_NODE_FACTS_NOTE = r"""
      options: {}
      notes:
      - For Get all storage nodes
      - 1. In the task output, the is_storage_master_node_primary parameter indicates whether the
           node is the cluster's primary node. A value of true denotes the primary node.
    """

    BHE_HIGHER_MODELS = r"""
      options: {}
      notes:
      - This module is not supported for VSP One BHE and higher storage models.
    """
