#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_iscsi_target_bulk
short_description: Manages iscsi targets in bulk mode on VSP block storage systems.
description:
  - The hv_iscsi_target module provides the following iscsi target management operations
  - 1. Create iscsi target
  - 2. Update host mode and host mode options
  - 3. Add iqn initiator to iscsi target
  - 4. Add LDEV to iscsi target
  - 5. Remove iqn initiator from iscsi target
  - 6. Remove LDEV from iscsi target
  - 7. Delete iscsi target
  - 8. Add CHAP User to iscsi target
  - 9. Remove CHAP User from iscsi target
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/iscsi_target_bulk.yml)
version_added: '4.7.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.9
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: none
extends_documentation_fragment:
- hitachivantara.vspone_block.common.connection_with_type
options:
  state:
    description:
      - Set state to present for create and update iscsi target
      - Set state to absent for delete iscsi target
    type: str
    required: false
    choices: ['present', 'absent', 'added', 'removed', 'updated']
    default: 'present'
  storage_system_info:
    description: Information about the storage system. This field is an optional field.
    type: dict
    required: false
    suboptions:
      serial:
        description: The serial number of the storage system.
        type: str
        required: false
  spec:
    description: Specification for iscsi target operation.
    type: dict
    required: true
    suboptions:
      # state:
      #   description:
      #     - State of the iscsi target tasks.
      #     - C(present) - Update iscsi target by override host mode and host mode option and append other parameters mentioned in spec.
      #     - C(absent) -  Update iscsi target by remove all parameters mentioned in spec.
      #     - C(added) - Update iscsi target by adding all IQN initiators, LUN paths, and CHAP users mentioned in spec.
      #     - C(removed) - Update iscsi target by removing all IQN initiators, LUN paths, and CHAP users mentioned in spec.
      #     - C(updated) - Update iscsi target by updating host mode, host mode options and release host reserve mentioned in spec.
      #   required: false
      #   choices: ['present', 'absent', 'added', 'removed', 'updated']
      #   default: 'present'
      #   type: str
      port_ids:
        description: Port IDs of the iscsi targets.
        required: true
        type: list
        elements: str
      name:
        description: Name of the iscsi target. If not given, id is required to identify the iscsi target.
        required: false
        type: str
      id:
        description: ID of the iSCSI target. If not given, name is required to identify the iscsi target.
        type: int
        required: false
      host_mode:
        description: Host mode of host group.
          Required for the Update iSCSI target host mode and host mode options task.
        type: str
        required: false
        choices: ['LINUX', 'VMWARE', 'HP', 'OPEN_VMS', 'TRU64', 'SOLARIS',
          'NETWARE', 'WINDOWS', 'HI_UX', 'AIX', 'VMWARE_EXTENSION',
          'WINDOWS_EXTENSION', 'UVM', 'HP_XP', 'DYNIX']
      host_mode_options:
        description:
          - List of host group host mode option numbers.
          - Required for the Update iSCSI target host mode and host mode options task.
          - '0 # RESERVED'
          - '2 # VERITAS_DB_EDITION_ADV_CLUSTER'
          - '6 # TPRLO'
          - '7 # AUTO_LUN_RECOGNITION'
          - '12 # NO_DISPLAY_FOR_GHOST_LUN'
          - '13 # SIM_REPORT_AT_LINK_FAILURE'
          - '14 # HP_TRUECLUSTER_WITH_TRUECOPY'
          - '15 # RAID_HACMP'
          - '22 # VERITAS_CLUSTER_SERVER'
          - '23 # REC_COMMAND_SUPPORT'
          - '25 # SUPPORT_SPC_3_PERSISTENT_RESERVATION'
          - '33 # SET_REPORT_DEVICE_ID_ENABLE'
          - '39 # CHANGE_NEXUS_SPECIFIED_IN_SCSI_TARGET_RESET'
          - '40 # VVOL_EXPANSION'
          - '41 # PRIORITIZED_DEVICE_RECOGNITION'
          - '42 # PREVENT_OHUB_PCI_RETRY'
          - '43 # QUEUE_FULL_RESPONSE'
          - '48 # HAM_SVOL_READ'
          - '49 # BB_CREDIT_SETUP_1'
          - '50 # BB_CREDIT_SETUP_2'
          - '51 # ROUND_TRIP_SETUP'
          - '52 # HAM_AND_CLUSTER_SW_FOR_SCSI_2'
          - '54 # EXTENDED_COPY'
          - '57 # HAM_RESPONSE_CHANGE'
          - '60 # LUN0_CHANGE_GUARD'
          - '61 # EXPANDED_PERSISTENT_RESERVE_KEY'
          - '63 # VSTORAGE_APIS_ON_T10_STANDARDS'
          - '65 # ROUND_TRIP_EXTENDED_SETUP'
          - '67 # CHANGE_OF_ED_TOV_VALUE'
          - '68 # PAGE_RECLAMATION_LINUX'
          - '69 # ONLINE_LUSE_EXPANSION'
          - '71 # CHANGE_UNIT_ATTENTION_FOR_BLOCKED_POOL_VOLS'
          - '72 # AIX_GPFS'
          - '73 # WS2012'
          - '78 # NON_PREFERRED_PATH'
          - '91 # DISABLE_IO_WAIT_FOR_OPEN_STACK'
          - '95 # CHANGE_SCSI_LU_RESET_NEXUS_VSP_HUS_VM'
          - '96 # CHANGE_SCSI_LU_RESET_NEXUS'
          - '97 # PROPRIETARY_ANCHOR_COMMAND_SUPPORT'
          - '100 # HITACHI_HBA_EMULATION_CONNECTION_OPTION'
          - '102 # GAD_STANDARD_INQURY_EXPANSION_HCS'
          - '105 # TASK_SET_FULL_RESPONSE_FOR_IO_OVERLOAD'
          - '110 # ODX Support for WS2012'
          - '113 # iSCSI CHAP Authentication Log'
          - '114 # Auto Asynchronous Reclamation on ESXi 6.5+ '
          - '122 # TASK_SET_FULL_RESPONSE_AFTER_QOS_UPPER_LIMIT'
          - '124 # GUARANTEED_RESPONSE_DURING_CONTROLLER_FAILURE'
          - '131 # WCE_BIT_OFF_MODE'
        type: list
        elements: int
        required: false
      iqn_initiators:
        description: List of IQN initiators that you want to add or remove.
        required: false
        type: list
        elements: dict
        suboptions:
          iqn:
            description: IQN of the initiator.
            required: true
            type: str
          nickname:
            description: Nickname of the initiator.
            required: false
            type: str
      lun_paths:
        description: List of LUN paths that you want to add or remove. Each LUN path contains LUN number and LDEV ID.
        required: false
        type: list
        elements: dict
        suboptions:
          lun:
            description: LUN number.
            required: false
            type: int
          ldev:
            description: LDEV ID.
            required: true
            type: str
      chap_users:
        description: List of CHAP users that you want to add or remove.
        required: false
        type: list
        elements: dict
      # should_delete_all_ldevs:
      #   description: Deprecated. Use should_delete_all_volumes instead.
      #   required: false
      #   type: bool
      should_delete_all_volumes:
        description: If the value is true, destroy the logical devices that are no longer attached to any iSCSI Target.
        required: false
        type: bool
        aliases: ['should_delete_all_ldevs']
      should_release_host_reserve:
        description: If the value is true, release the host reserve.
        required: false
        type: bool
"""

EXAMPLES = """
- name: Create multiple iSCSI targets
  hitachivantara.vspone_block.vsp.hv_iscsi_target_bulk:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    state: present
    spec:
      name: 'rd-server-1234'
      port_ids: ['CL1-C', 'CL2-C']
      host_mode: "LINUX"
      host_mode_options: [54, 63]
      iqn_initiators:
        - iqn: iqn.1993-08.org.debian.iscsi:01:107dc7e4254a
          nickname: "nickname_1"
        - iqn: iqn.1993-08.org.debian.iscsi:01:107dc7e4254b
          nickname: "nickname_2"
      lun_paths:
            - lun: 5
              ldev: 5150
            - lun: 6
              ldev: 5153
      chap_users:
        - chap_user_name: user1
          chap_secret: Secret123456

- name: Update iscsi target host mode and options
  hitachivantara.vspone_block.vsp.hv_iscsi_target_bulk:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    state: updated
    spec:
      name: 'iscsi-target-server-1'
      port_ids: ['CL1-C', 'CL2-C']
      host_mode: "LINUX"
      host_mode_options: [54, 63, 94]
      should_release_host_reserve: true

- name: Add iqn initiators, LUN paths and CHAP users to multiple iscsi targets
  hitachivantara.vspone_block.vsp.hv_iscsi_target_bulk:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    state: added
    spec:
      name: 'rd-server-0324'
      port_ids: ['CL1-C', 'CL2-C']
      iqn_initiators:
        - iqn: iqn.1993-08.org.debian.iscsi:01:107dc7e4254a
          nickname: "nickname_1"
        - iqn: iqn.1993-08.org.debian.iscsi:01:107dc7e4254b
          nickname: "nickname_2"
        - iqn: iqn.1993-08.org.debian.iscsi:01:107dc7e4254c
          nickname: "nickname_3"
      lun_paths:
            - lun: 5
              ldev: 5150
            - lun: 6
              ldev: 5153
            - lun: 7
              ldev: 5154
      chap_users:
        - chap_user_name: user1
          chap_secret: Secret123456
        - chap_user_name: user2
          chap_secret: Secret123456
        - chap_user_name: user3
          chap_secret: Secret123456
  register: result

- name: Remove chap user from iscsi target
  hitachivantara.vspone_block.vsp.hv_iscsi_target_bulk:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    state: present
    spec:
      state: remove_chap_user
      name: 'iscsi-target-server-1'
      port: 'CL4-C'
      chap_users:
        - chap_user_name: user2
          chap_secret: Secret2

- name: Add iqn initiators to iscsi target
  hitachivantara.vspone_block.vsp.hv_iscsi_target_bulk:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    state: present
    spec:
      state: add_iscsi_initiator
      name: 'iscsi-target-server-1'
      port: 'CL4-C'
      iqn_initiators:
        - iqn: iqn.1993-08.org.debian.iscsi:01:107dc7e4254b

- name: Release host reserve status of a iscsi target using lun
  hitachivantara.vspone_block.vsp.hv_iscsi_target_bulk:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    state: present
    spec:
      id: 20
      should_release_host_reserve: true
      port: 'CL4-C'
      lun: 100

- name: Release host reserve status of a iscsi targets
  hitachivantara.vspone_block.vsp.hv_iscsi_target_bulk:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    state: present
    spec:
      iscsi_id: 20
      port: 'CL4-C'
      should_release_host_reserve: true
"""

RETURN = r"""
iscsi_target:
  description: Details of the iSCSI target.
  returned: always
  type: dict
  contains:
    auth_param:
      description: Authentication parameters.
      type: dict
      contains:
        authentication_mode:
          description: Mode of authentication.
          type: str
          sample: "BOTH"
        is_chap_enabled:
          description: Indicates if CHAP is enabled.
          type: bool
          sample: true
        is_chap_required:
          description: Indicates if CHAP is required.
          type: bool
          sample: false
        is_mutual_auth:
          description: Indicates if mutual authentication is enabled.
          type: bool
          sample: false
    chap_users:
      description: List of CHAP users.
      type: list
      elements: str
      sample: []
    host_mode:
      description: Host mode details.
      type: dict
      contains:
        host_mode:
          description: Host mode.
          type: str
          sample: "LINUX"
        host_mode_options:
          description: List of host mode options.
          type: list
          elements: dict
          sample: []
    iqn:
      description: IQN of the iSCSI target.
      type: str
      sample: "iqn.1994-04.jp.co.hitachi:rsd.has.t.10050.4c0ee"
    iqn_initiators:
      description: List of IQN initiators.
      type: list
      elements: dict
      contains:
        iqn:
          description: IQN of the initiator.
          type: str
          sample: "iqn.1993-08.org.debian.iscsi:01:107dc7e4254a"
        nick_name:
          description: Nickname of the initiator.
          type: str
          sample: "iscsi-target-1"
    iscsi_id:
      description: ID of the iSCSI target.
      type: int
      sample: 238
    iscsi_name:
      description: Name of the iSCSI target.
      type: str
      sample: "isserver21"
    logical_units:
      description: List of logical units.
      type: list
      elements: dict
      sample: []
    port_id:
      description: Port ID.
      type: str
      sample: "CL4-C"
    resource_group_id:
      description: Resource group ID.
      type: int
      sample: 0
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_iscsi_target import (
    VSPIscsiTargetReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPIscsiTargetArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class VSPIscsiTargetBulkManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = VSPIscsiTargetArguments().iscsi_target_bulk()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )

        parameterManager = VSPParametersManager(self.module.params)
        self.connection_info = parameterManager.get_connection_info()
        self.spec = parameterManager.get_iscsi_target_bulk_spec()
        self.serial_number = parameterManager.get_serial()
        self.state = parameterManager.get_state()
        self.logger.writeDebug("spec = {}", self.spec)

    def apply(self):
        self.logger.writeInfo("=== Start of iSCSI Target Bulk operation. ===")
        registration_message = validate_ansible_product_registration()
        iscsi_target_data_extracted = None

        try:
            vsp_reconciler = VSPIscsiTargetReconciler(
                self.connection_info, self.serial_number
            )
            iscsi_targets = vsp_reconciler.reconcile_iscsi_target_bulk(
                self.state, self.spec
            )
            self.logger.writeDebug("iscsi_targets = {}", iscsi_targets)
            iscsi_target_data_extracted = iscsi_targets

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of iSCSI Target Bulk operation. ===")
            self.module.fail_json(msg=str(e))
        if registration_message:
            iscsi_target_data_extracted["user_consent_required"] = registration_message
        self.logger.writeInfo(f"{iscsi_target_data_extracted}")
        self.logger.writeInfo("=== End of iSCSI Target Bulk operation. ===")
        self.module.exit_json(**iscsi_target_data_extracted)


def main(module=None):
    obj_store = VSPIscsiTargetBulkManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
