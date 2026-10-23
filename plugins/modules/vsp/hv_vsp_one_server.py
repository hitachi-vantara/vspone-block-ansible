#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_vsp_one_server
short_description: Manages servers on VSP E series, VSP One Block 20 series, and VSP One Block 80 series storage systems.
description:
  - This module enables register, modification, and deletion of servers, as well as various server operations.
  - Supports various server operations depending on the specified state parameter.
  - Utilizes the Hitachi Virtual Storage Platform One Simple API for server management across VSP E series, VSP One B20 series, and VSP One B80 series models.
  - For usage examples, visit
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/vsp_one_server.yml)
version_added: '4.3.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.9
attributes:
  check_mode:
    description: Specifies whether the module operates in check mode.
    support: none
extends_documentation_fragment:
  - hitachivantara.vspone_block.common.connection_info
options:
  state:
    description: Defines the server operation type. Available options include C(present), C(absent),
      C(sync_server_nick_name), C(sync_server_nickname), C(add_host_groups), C(add_hba), C(remove_hba), C(add_path), and C(remove_path).
      Bulk operations are available via C(create_servers), C(add_hba_bulk), C(add_path_bulk), and C(remove_path_bulk).
      C(sync_server_nick_name) will be deprecated in favor of C(sync_server_nickname).
    type: str
    required: false
    choices: ['present', 'absent', 'sync_server_nick_name', 'sync_server_nickname', 'add_host_groups', 'add_hba',
            'remove_hba', 'add_path', 'remove_path', 'change_iscsi_target_settings', 'create_servers',
            'add_hba_bulk', 'add_path_bulk', 'remove_path_bulk']
    default: 'present'
  spec:
    description: Configuration parameters for the server operation.
    type: dict
    required: true
    suboptions:
      nickname:
        description: Server nickname specification.
          Required for the Register a basic server with minimal configuration
          /Register a FC server with HBA WWN
          /Register an iSCSI server with iSCSI names
          /Register server with host groups configuration
          /Register server with multiple HBAs and paths configuration
          /Register iSCSI server with multiple HBAs and paths
          /Register reserved server with specific configuration
          /Update existing server nickname (using server_id)
          /Register HP-UX server with comprehensive configuration
          /Delete server using nickname tasks.
        type: str
        required: false
        aliases: ['nick_name']
      protocol:
        description: Server protocol type.
          Required for the Register a basic server with minimal configuration
          /Register a FC server with HBA WWN
          /Register an iSCSI server with iSCSI names
          /Register server with host groups configuration
          /Register server with multiple HBAs and paths configuration
          /Register iSCSI server with multiple HBAs and paths
          /Register reserved server with specific configuration
          /Register HP-UX server with comprehensive configuration tasks.
        type: str
        required: false
        choices: ["FC", "iSCSI"]
      server_id:
        description: Server identifier.
          Required for the Update existing server nickname (using server_id)
          /Update existing server settings like os type options using server_id
          /Add host groups to existing server
          /Add HBA to existing FC server
          /Add iSCSI HBA to existing iSCSI server
          /Remove HBA from FC server
          /Remove iSCSI HBA from iSCSI server
          /Add path to server
          /Remove path from server
          /Sync server nickname
          /Change the iSCSI target settings for existing server
          /Delete server by server_id and keep lun configuration tasks.
        type: int
        required: false
      os_type:
        description: Operating system type of the server.
          Required for the Register a basic server with minimal configuration
          /Register a FC server with HBA WWN
          /Register an iSCSI server with iSCSI names
          /Register server with host groups configuration
          /Register server with multiple HBAs and paths configuration
          /Register iSCSI server with multiple HBAs and paths
          /Register reserved server with specific configuration
          /Update existing server settings like os type options using server_id
          /Register HP-UX server with comprehensive configuration tasks.
        type: str
        required: false
        choices: ["Linux", "HP-UX", "Solaris", "AIX", "VMware", "Windows"]
      port_ids:
        description: List of port identifiers.
        type: list
        required: false
        elements: str
      is_reserved:
        description: Indicates if the server is reserved.
          Required for the Register a basic server with minimal configuration
          /Register reserved server with specific configuration tasks.
        type: bool
        required: false
      os_type_options:
        description: List of OS type option identifiers.
          Required for the Register reserved server with specific configuration
          /Update existing server settings like os type options using server_id tasks.
        type: list
        required: false
        elements: int
      hbas:
        description: List of HBA configurations.
          Required for the Register a FC server with HBA WWN
          /Register an iSCSI server with iSCSI names
          /Register server with multiple HBAs and paths configuration
          /Register iSCSI server with multiple HBAs and paths
          /Register reserved server with specific configuration
          /Add HBA to existing FC server
          /Add iSCSI HBA to existing iSCSI server
          /Remove HBA from FC server
          /Remove iSCSI HBA from iSCSI server
          /Register HP-UX server with comprehensive configuration tasks.
        type: list
        required: false
        elements: dict
        suboptions:
          hba_wwn:
            description: HBA WWN address.
              Required for the Register a FC server with HBA WWN
              /Register server with multiple HBAs and paths configuration
              /Register reserved server with specific configuration
              /Add HBA to existing FC server
              /Remove HBA from FC server
              /Register HP-UX server with comprehensive configuration tasks.
            type: str
            required: false
          iscsi_name:
            description: iSCSI name.
              Required for the Register an iSCSI server with iSCSI names
              /Register iSCSI server with multiple HBAs and paths
              /Add iSCSI HBA to existing iSCSI server
              /Remove iSCSI HBA from iSCSI server tasks.
            type: str
            required: false
      paths:
        description: List of path configurations.
          Required for the Register server with multiple HBAs and paths configuration
          /Register iSCSI server with multiple HBAs and paths
          /Add path to server
          /Remove path from server
          /Register HP-UX server with comprehensive configuration tasks.
        type: list
        required: false
        elements: dict
        suboptions:
          port_ids:
            description: List of port identifiers.
              Required for the Register server with multiple HBAs and paths configuration
              /Register iSCSI server with multiple HBAs and paths
              /Add path to server
              /Remove path from server
              /Register HP-UX server with comprehensive configuration tasks.
            type: list
            required: true
            elements: str
          hba_wwn:
            description: HBA WWN address.
              Required for the Register server with multiple HBAs and paths configuration
              /Add path to server
              /Remove path from server
              /Register HP-UX server with comprehensive configuration tasks.
            type: str
            required: false
          iscsi_name:
            description: iSCSI name.
              Required for the Register iSCSI server with multiple HBAs and paths tasks
            type: str
            required: false
      keep_lun_config:
        description: Whether to keep LUN configuration.
          Required for the Register HP-UX server with comprehensive configuration
          /Delete server by server_id and keep lun configuration tasks.
        type: bool
        required: false
      iscsi_target_settings:
        description: List of iSCSI target configurations.
          Required for the Change the iSCSI target settings for existing server tasks.
        type: list
        required: false
        elements: dict
        suboptions:
          port_id:
            description: Port identifier.
              Required for the Change the iSCSI target settings for existing server task.
            type: str
            required: true
          target_iscsi_name:
            description: iSCSI target name.
              Required for the Change the iSCSI target settings for existing server task.
            type: str
            required: true
      host_groups:
        description: List of host group configurations.
          Required for the Register server with host groups configuration
          /Add host groups to existing server
          /Register HP-UX server with comprehensive configuration tasks.
        type: list
        required: false
        elements: dict
        suboptions:
          host_group_id:
            description: Host group identifier.
            type: int
            required: false
          host_group_name:
            description: Host group name.
              Required for the Register server with host groups configuration
              /Add host groups to existing server
              /Register HP-UX server with comprehensive configuration tasks.
            type: str
            required: false
          port_id:
            description: Port identifier.
              Required for the Register server with host groups configuration
              /Add host groups to existing server
              /Register HP-UX server with comprehensive configuration tasks.
            type: str
            required: false
      iscsi_targets:
        description: List of iSCSI target configurations.
        type: list
        required: false
        elements: dict
        suboptions:
          iscsi_target_id:
            description: iSCSI target identifier.
            type: int
            required: false
          iscsi_target_name:
            description: iSCSI target name.
            type: str
            required: false
          port_id:
            description: Port identifier.
            type: str
            required: false
      servers:
        description: List of servers to register in one API call when C(state=create_servers).
          When C(count=1) (default) each entry creates a single server and may include
          C(hbas) and C(paths). When C(count) is greater than 1 the C(nickname) is used
          as a name prefix and C(count) identical server registrations are created
          (C(nickname_01)…C(nickname_N)); C(hbas) and C(paths) are not allowed in this
          mode because HBA WWNs and iSCSI names are physically unique per host — use
          C(state=add_hba_bulk) and C(state=add_path_bulk) after creation instead.
          Maximum value for C(count) is 50 per task.
        type: list
        required: false
        elements: dict
        suboptions:
          nickname:
            description: Server nickname. When creating multiple servers this value is
              used as a prefix; servers are named C(<nickname>_1), C(<nickname>_2), etc.,
              zero-padded to the number of digits in the largest index.
            type: str
            required: true
          count:
            description: Number of servers to create. Allowed range is 1–50.
              Servers are named C(<nickname>_1) … C(<nickname>_N) starting from 1.
              Cannot be combined with C(end_index).
              Cannot be combined with C(hbas) or C(paths) when greater than 1.
              Mutually exclusive with C(end_index); use C(start_index)+C(end_index) for
              an explicit range.
            type: int
            required: false
          start_index:
            description: First index in the server name sequence.
              Must be paired with either C(end_index) or C(count).
              When paired with C(count), creates servers C(<nickname>_start) …
              C(<nickname>_start+count-1). Defaults to 1 when C(count) is used alone.
            type: int
            required: false
          end_index:
            description: Last index in the server name sequence (inclusive).
              Must be paired with C(start_index). The range C([start_index, end_index])
              must not exceed 50 servers. Cannot be combined with C(count).
            type: int
            required: false
          protocol:
            description: Connection protocol for the server.
            type: str
            required: false
            choices: ['FC', 'iSCSI']
          os_type:
            description: Operating system type of the server.
            type: str
            required: false
            choices: ['Linux', 'HP-UX', 'Solaris', 'AIX', 'VMware', 'Windows']
          os_type_options:
            description: List of OS type option identifiers.
            type: list
            required: false
            elements: int
          is_reserved:
            description: Whether the server is reserved.
            type: bool
            required: false
          hbas:
            description: HBAs to register on the created server immediately after creation.
              Only valid when creating a single server (no C(count)/C(start_index)/C(end_index)
              or C(count=1)). HBA WWNs and iSCSI names are unique per physical host and
              cannot be shared across multiple servers.
            type: list
            required: false
            elements: dict
            suboptions:
              hba_wwn:
                description: HBA WWN address (FC).
                type: str
                required: false
              iscsi_name:
                description: iSCSI initiator name (iSCSI).
                type: str
                required: false
          paths:
            description: Paths to register on the created server immediately after HBAs.
              Only valid when creating a single server. Paths are bound to specific HBA
              WWNs or iSCSI names which are unique per host.
            type: list
            required: false
            elements: dict
            suboptions:
              port_ids:
                description: List of port identifiers for this path.
                type: list
                required: true
                elements: str
              hba_wwn:
                description: HBA WWN address associated with the path (FC).
                type: str
                required: false
              iscsi_name:
                description: iSCSI initiator name associated with the path (iSCSI).
                type: str
                required: false
      bulk_hbas:
        description: List of server HBA payloads for C(state=add_hba_bulk).
        type: list
        required: false
        elements: dict
        suboptions:
          server_id:
            description: Identifier of the server to add HBAs to.
            type: int
            required: true
          hbas:
            description: List of HBAs to add to the server.
            type: list
            required: true
            elements: dict
            suboptions:
              hba_wwn:
                description: HBA WWN address.
                type: str
                required: false
              iscsi_name:
                description: iSCSI name.
                type: str
                required: false
      bulk_paths:
        description: List of server path payloads for C(state=add_path_bulk).
        type: list
        required: false
        elements: dict
        suboptions:
          server_id:
            description: Identifier of the server to add paths to.
            type: int
            required: true
          paths:
            description: List of paths to add to the server.
            type: list
            required: true
            elements: dict
            suboptions:
              port_ids:
                description: List of port identifiers for the path.
                type: list
                required: true
                elements: str
              hba_wwn:
                description: HBA WWN address associated with the path.
                type: str
                required: false
              iscsi_name:
                description: iSCSI name associated with the path.
                type: str
                required: false
      bulk_remove_paths:
        description: List of server path payloads for C(state=remove_path_bulk).
        type: list
        required: false
        elements: dict
        suboptions:
          server_id:
            description: Identifier of the server to remove paths from.
            type: int
            required: true
          paths:
            description: List of paths to remove from the server.
            type: list
            required: true
            elements: dict
            suboptions:
              port_ids:
                description: List of port identifiers for the path.
                type: list
                required: true
                elements: str
              hba_wwn:
                description: HBA WWN address associated with the path.
                type: str
                required: false
              iscsi_name:
                description: iSCSI name associated with the path.
                type: str
                required: false
"""

EXAMPLES = """
- name: Register a FC server with HBA WWN
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: present
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      nickname: "WebServer01"
      protocol: "FC"
      os_type: "Linux"
      hbas:
        - hba_wwn: "50060e8010203040"

- name: Register an iSCSI server with iSCSI name
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: present
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      nickname: "DatabaseServer01"
      protocol: "iSCSI"
      os_type: "Windows"
      hbas:
        - iscsi_name: "iqn.1991-05.com.microsoft:server01"

- name: Register server with host groups configuration
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: present
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      nickname: "VMwareCluster01"
      protocol: "FC"
      os_type: "VMware"
      host_groups:
        - host_group_name: "VMware_HG01"
          port_id: "CL1-A"
        - host_group_name: "VMware_HG02"
          port_id: "CL1-B"

- name: Register server with multiple HBAs and paths configuration
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: present
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      nickname: "AppServer01"
      protocol: "FC"
      os_type: "Linux"
      hbas:
        - hba_wwn: "50060e8010203040"
        - hba_wwn: "50060e8010203041"
      paths:
        - port_ids: ["CL1-A", "CL1-B"]
          hba_wwn: "50060e8010203040"
        - port_ids: ["CL2-A", "CL2-B"]
          hba_wwn: "50060e8010203041"

- name: Register iSCSI server with multiple iSCSI names and paths
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: present
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      nickname: "HybridServer01"
      protocol: "iSCSI"
      os_type: "Linux"
      hbas:
        - iscsi_name: "iqn.1991-05.com.example:server01-iscsi1"
        - iscsi_name: "iqn.1991-05.com.example:server01-iscsi2"
      paths:
        - port_ids: ["CL1-A"]
          iscsi_name: "iqn.1991-05.com.example:server01-iscsi1"
        - port_ids: ["CL1-B"]
          iscsi_name: "iqn.1991-05.com.example:server01-iscsi2"

- name: Update existing server nickname with server_id
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: present
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      server_id: 123
      nickname: "UpdatedServerName"

- name: Update existing server settings like os type os type options using server_id
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: present
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      server_id: 123
      os_type: "Windows"
      os_type_options: [1, 2]

- name: Add host groups to existing server
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: add_host_groups
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      server_id: 123
      host_groups:
        - host_group_name: "NewHostGroup01"
          port_id: "CL2-A"
- name: Add HBA to existing server using server_id
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: add_hba
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      server_id: 123
      hbas:
        - hba_wwn: "50060e8010203042"
- name: Remove HBA from server
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: remove_hba
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      server_id: 12
      hbas:
        - hba_wwn: "50060e8010203042"

- name: Add path to server
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: add_path
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      server_id: 12
      paths:
        - port_ids: ["CL1-C", "CL1-D"]
          hba_wwn: "50060e8010203040"

- name: Remove path from server
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: remove_path
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      server_id: 12
      paths:
        - port_ids: ["CL1-C"]
          hba_wwn: "50060e8010203040"

- name: Sync server nickname with host group
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: sync_server_nickname
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      server_id: 123

- name: Register reserved server with specific configuration
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: present
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      nickname: "ReservedServer01"
      protocol: "FC"
      os_type: "Solaris"
      is_reserved: true
      keep_lun_config: true
      os_type_options: [1, 2]

- name: Change the iSCSI target settings for existing server (change target name)
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: present
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      server_id: 123
      iscsi_targets:
        - port_id: "CL1-A"
          iscsi_target_name: "iqn.1992-04.com.hitachi:target01"
        - port_id: "CL1-B"
          iscsi_target_name: "iqn.1992-04.com.hitachi:target02"

- name: Delete server using server_id and keep lun configuration
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: absent
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      server_id: 123
      keep_lun_config: true

- name: Delete server using nickname.
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: absent
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      nickname: "WebServer01"

- name: Bulk create multiple servers in a single request
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: create_servers
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      servers:
        - nickname: "BulkServer01"
          protocol: "FC"
          os_type: "Linux"
          os_type_options: [1, 2]
        - nickname: "BulkServer02"
          protocol: "iSCSI"
          os_type: "Windows"
          is_reserved: true

- name: Bulk create servers with inline HBAs and paths
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: create_servers
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      servers:
        - nickname: "AppServer01"
          protocol: "FC"
          os_type: "Linux"
          hbas:
            - hba_wwn: "50060e8010203040"
          paths:
            - port_ids: ["CL1-A", "CL1-B"]
              hba_wwn: "50060e8010203040"
        - nickname: "DBServer01"
          protocol: "iSCSI"
          os_type: "Windows"
          hbas:
            - iscsi_name: "iqn.1991-05.com.example:dbserver01"
          paths:
            - port_ids: ["CL1-A"]
              iscsi_name: "iqn.1991-05.com.example:dbserver01"

- name: Bulk create N servers using count (creates WebServer_1, WebServer_2, WebServer_3)
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: create_servers
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      servers:
        - nickname: "WebServer"
          count: 3                   # creates WebServer_1, WebServer_2, WebServer_3
          protocol: "FC"
          os_type: "Linux"
          os_type_options: [1, 2]

- name: Bulk create servers using start_index and end_index (creates WebServer_05 to WebServer_10)
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: create_servers
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      servers:
        - nickname: "WebServer"
          start_index: 5
          end_index: 10             # creates WebServer_05, WebServer_06 … WebServer_10
          protocol: "FC"
          os_type: "Linux"

- name: Bulk create servers using start_index and count (creates WebServer_05, WebServer_06, WebServer_07)
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: create_servers
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      servers:
        - nickname: "WebServer"
          start_index: 5
          count: 3                  # creates WebServer_05, WebServer_06, WebServer_07
          protocol: "FC"
          os_type: "Linux"

- name: Bulk add HBAs to multiple servers in a single request
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: add_hba_bulk
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      bulk_hbas:
        - server_id: 101
          hbas:
            - hba_wwn: "50060e8010203040"
            - hba_wwn: "50060e8010203041"
        - server_id: 102
          hbas:
            - iscsi_name: "iqn.1991-05.com.example:server102-iscsi1"

- name: Bulk add paths to multiple servers in a single request
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: add_path_bulk
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      bulk_paths:
        - server_id: 101
          paths:
            - port_ids: ["CL1-A", "CL1-B"]
              hba_wwn: "50060e8010203040"
        - server_id: 102
          paths:
            - port_ids: ["CL2-A"]
              iscsi_name: "iqn.1991-05.com.example:server102-iscsi1"

- name: Bulk remove paths from multiple servers in a single request
  hitachivantara.vspone_block.vsp.hv_vsp_one_server:
    state: remove_path_bulk
    connection_info:
      address: vsp.company.com
      username: "admin"
      password: "password"
    spec:
      bulk_remove_paths:
        - server_id: 101
          paths:
            - port_ids: ["CL1-A"]
              hba_wwn: "50060e8010203040"
        - server_id: 102
          paths:
            - port_ids: ["CL2-A"]
              iscsi_name: "iqn.1991-05.com.example:server102-iscsi1"
"""

RETURN = """
server:
  description: Server information returned after operation
  returned: always
  type: dict
  contains:
    compatibility:
      description: Server compatibility status
      type: str
      returned: always
      sample: ""
    has_non_fullmesh_lu_paths:
      description: Indicates if server has non-fullmesh LU paths
      type: bool
      returned: always
      sample: true
    has_unaligned_os_type_options:
      description: Indicates if server has unaligned OS type options
      type: bool
      returned: always
      sample: true
    has_unaligned_os_types:
      description: Indicates if server has unaligned OS types
      type: bool
      returned: always
      sample: true
    id:
      description: Server identifier
      type: int
      returned: always
      sample: 13
    is_inconsistent:
      description: Indicates if server configuration is inconsistent
      type: bool
      returned: always
      sample: false
    is_reserved:
      description: Indicates if server is reserved
      type: bool
      returned: always
      sample: false
    modification_in_progress:
      description: Indicates if server modification is in progress
      type: bool
      returned: always
      sample: false
    nickname:
      description: Server nickname
      type: str
      returned: always
      sample: "WebServer414"
    nick_name:
      description: Deprecated. Use C(nickname) instead.
      type: str
      returned: always
      sample: "WebServer414"
    number_of_paths:
      description: Number of paths configured for the server
      type: int
      returned: always
      sample: 2
    number_of_volumes:
      description: Number of volumes attached to the server
      type: int
      returned: always
      sample: 1
    os_type:
      description: Operating system type of the server
      type: str
      returned: always
      sample: "Linux"
    os_type_options:
      description: List of OS type option identifiers
      type: list
      elements: int
      returned: always
      sample: [68]
    paths:
      description: List of server path configurations
      type: list
      elements: dict
      returned: always
      contains:
        hba_wwn:
          description: HBA WWN address
          type: str
          returned: always
          sample: "210003e08b0256f9"
        iscsi_name:
          description: iSCSI name
          type: str
          returned: always
          sample: ""
        port_ids:
          description: List of port identifiers
          type: list
          elements: str
          returned: always
          sample: ["CL1-A"]
    protocol:
      description: Server protocol type
      type: str
      returned: always
      sample: "FC"
    total_capacity:
      description: Total capacity in GB
      type: int
      returned: always
      sample: 50
    used_capacity:
      description: Used capacity in GB
      type: int
      returned: always
      sample: 0
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_one_server_reconciler import (
    VSPServerSimpleAPIReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPOneServerArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class VSPOneServer:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = VSPOneServerArguments().get_vsp_one_server_args()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )
        try:
            params_manager = VSPParametersManager(self.module.params)
            self.spec = params_manager.get_vsp_one_server_spec()
            self.connection_info = params_manager.get_connection_info()
            self.state = params_manager.get_state()
        except Exception as e:
            self.logger.writeError(f"An error occurred during initialization: {str(e)}")
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of VSP One Server Operation ===")
        server = None
        registration_message = validate_ansible_product_registration()

        try:
            server_reconciler = VSPServerSimpleAPIReconciler(self.connection_info)
            server = server_reconciler.reconcile(self.state, self.spec)

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of VSP One Server Operation ===")
            self.module.fail_json(msg=str(e))

        response = {
            "changed": self.connection_info.changed,
            "server": server,
            "comments": self.spec.comments if self.spec.comments else [],
            "errors": self.spec.errors if self.spec.errors else [],
        }
        if registration_message:
            response["user_consent_required"] = registration_message
        self.logger.writeInfo("=== End of VSP One Server Operation ===")
        self.module.exit_json(**response)


def main():
    obj_store = VSPOneServer()
    obj_store.apply()


if __name__ == "__main__":
    main()
