#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_iscsi_target
short_description: Manages iscsi target on Hitachi VSP storage systems.
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
  - This module is supported for both direct and gateway connection types.
  - For direct connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/iscsi_target.yml)
  - For gateway connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/iscsi_target.yml)
version_added: '3.0.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
options:
  state:
    description:
      - set state to present for create and update iscsi target
      - set state to absent for delete iscsi target
    type: str
    required: false
    choices: ['present', 'absent']
    default: 'present'
  storage_system_info:
    required: false
    type: dict
    description:
      - Information about the Hitachi storage system.
    suboptions:
      serial:
        description: Serial number of the Hitachi storage system.
        required: false
        type: str
  connection_info:
    description: Information required to establish a connection to the storage system.
    required: true
    type: dict
    suboptions:
      address:
        description: IP address or hostname of either the UAI gateway (if connection_type is gateway) or the storage system (if connection_type is direct).
        type: str
        required: true
      username:
        description: Username for authentication.This field is valid for direct connection type only, and it is a required field.
        type: str
        required: false
      password:
        description: Password for authentication.This field is valid for direct connection type only, and it is a required field.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['gateway', 'direct']
        default: 'direct'
      subscriber_id:
        description: This field is valid for gateway connection type only.This is an optional field and only needed to support multi-tenancy environment.
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway.This is a required field for gateway connection type.
        type: str
        required: false
  spec:
    description: Specification for iscsi target operation.
    type: dict
    required: true
    suboptions:
      state:
        description:
          - State of the iscsi target tasks.
          - 'present: update iscsi target by override host mode and host mode option and append other paramters mentioned in spec'
          - 'absent: update iscsi target by remove all paramters mentioned in spec'
          - 'add_iscsi_initiator: update iscsi target by append all iqn initiators mentioned in spec'
          - 'remove_iscsi_initiator: update iscsi target by remove all iqn initiators mentioned in spec'
          - 'attach_ldev: update iscsi target by append all ldevs mentioned in spec'
          - 'detach_ldev: update iscsi target by remove all ldevs mentioned in spec'
          - 'add_chap_user: update iscsi target by append all chap users mentioned in spec'
          - 'remove_chap_user: update iscsi target by remove all chap users mentioned in spec'
        required: false
        choices: ['present', 'absent', 'add_iscsi_initiator', 'remove_iscsi_initiator', 'attach_ldev', 'detach_ldev', 'add_chap_user', 'remove_chap_user']
        default: 'present'
        type: str
      port:
        description: port of the iscsi target.
        required: true
        type: str
      name:
        description: Name of the iscsi target.If not given,
          It will create the name will contain with prefix value "smrha-<10 digit random number>".
        required: false
        type: str
      host_mode:
        description: Host mode of host group.
        type: str
        required: false
        choices:
          - LINUX
          - VMWARE
          - HP
          - OPEN_VMS
          - TRU64
          - SOLARIS
          - NETWARE
          - WINDOWS
          - HI_UX
          - AIX
          - VMWARE_EXTENSION
          - WINDOWS_EXTENSION
          - UVM
          - HP_XP
          - DYNIX
      host_mode_options:
        description:
          - List of host group host mode option numbers.
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
      ldevs:
        description: LDEV ID in decimal or HEX of the LDEV that you want to present or unpresent.
        required: false
        type: list
        elements: int
      iqn_initiators:
        description: List of IQN initiators that you want to add or remove.
        required: false
        type: list
        elements: str
      chap_users:
        description: List of CHAP users that you want to add or remove.
        required: false
        type: list
        elements: dict
      should_delete_all_ldevs:
        description: If the value is true, destroy the logical devices that are no longer attached to any iSCSI Target.
        required: false
        type: bool
"""

EXAMPLES = """
- name: Create iscsi target with direct connection
  hv_iscsi_target:
    connection_info:
      connection_type: "direct"
      address: storage1.company.com
      username: "admin"
      password: "password"
    state: present
    spec:
      name: 'iscsi-target-server-1'
      port: 'CL4-C'
      iqn_initiators:
        - iqn.1993-08.org.debian.iscsi:01:107dc7e4254a
        - iqn.1993-08.org.debian.iscsi:01:107dc7e4254b
      ldevs: [100, 200]
      chap_users:
        - chap_user_name: user1
          chap_secret: Secret1
  register: result

- name: Update iscsi target host mode and options
  hv_iscsi_target:
    connection_info:
      connection_type: "direct"
      address: storage1.company.com
      username: "admin"
      password: "password"
    state: present
    spec:
      name: 'iscsi-target-server-1'
      port: 'CL4-C'
      host_mode: LINUX
      host_mode_options: [54, 63]
  register: result

- name: Add chap users to iscsi target
  hv_iscsi_target:
    connection_info:
      connection_type: "direct"
      address: storage1.company.com
      username: "admin"
      password: "password"
    state: present
    spec:
      state: add_chap_user
      name: 'iscsi-target-server-1'
      port: 'CL4-C'
      chap_users:
        - chap_user_name: user1
          chap_secret: Secret1
        - chap_user_name: user2
          chap_secret: Secret2
  register: result

- name: Remove chap user from iscsi target
  hv_iscsi_target:
    connection_info:
      connection_type: "direct"
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
  register: result

- name: Add iqn initiators to iscsi target
  hv_iscsi_target:
    connection_info:
      connection_type: "direct"
      address: storage1.company.com
      username: "admin"
      password: "password"
    state: present
    spec:
      state: add_iscsi_initiator
      name: 'iscsi-target-server-1'
      port: 'CL4-C'
      iqn_initiators:
        - iqn.1993-08.org.debian.iscsi:01:107dc7e4254b
  register: result

- name: Attach ldevs to iscsi target
  hv_iscsi_target:
    connection_info:
      connection_type: "gateway"
      address: gateway.company.com
      api_token: "api_token"
      subscriber_id: 12345
    state: present
    spec:
      state: attach_ldev
      name: 'iscsi-target-server-1'
      port: 'CL4-C'
      ldevs: [300, 400]
  register: result
"""

RETURN = """
Iscsi targets info:
  description: The iscsi targets information.
  returned: always
  type: dict
  sample: {
    "changed": true,
    "failed": false,
    "iscsi_target": {
      "auth_param": {
        "authentication_mode": "BOTH",
        "is_chap_enabled": true,
        "is_chap_required": false,
        "is_mutual_auth": false
      },
      "chap_users": [
        "chapuser1"
      ],
      "host_mode": {
        "host_mode": "VMWARE",
        "host_mode_options": [
          {
            "raid_option": "EXTENDED_COPY",
            "raid_option_number": 54
          }
        ]
      },
      "iqn": "iqn.rest.example.of.iqn.host",
      "iqn_initiators": [
        "iqn.2014-04.jp.co.hitachi:xxx.h70.i.62510.1a.ff"
      ],
      "iscsi_id": 1,
      "iscsi_name": "iscsi-name",
      "logical_units": [
        {
          "host_lun_id": 0,
          "logical_unit_id": 1
        }
      ],
      "partner_id": "partnerid",
      "port_id": "CL4-C",
      "resource_group_id": 0,
      "subscriber_id": "12345"
    }
  }
"""

from dataclasses import asdict

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_iscsi_target import (
    VSPIscsiTargetReconciler,
    VSPIscsiTargetCommonPropertiesExtractor,
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


class VSPIscsiTargetManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = VSPIscsiTargetArguments().iscsi_target()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        parameterManager = VSPParametersManager(self.module.params)
        self.connection_info = parameterManager.get_connection_info()
        self.spec = parameterManager.get_iscsi_target_spec()
        self.serial_number = parameterManager.get_serial()
        self.state = parameterManager.get_state()

    def apply(self):
        self.logger.writeInfo("=== Start of iSCSI Target operation. ===")
        registration_message = validate_ansible_product_registration()
        iscsi_target_data_extracted = None

        try:
            vsp_reconciler = VSPIscsiTargetReconciler(
                self.connection_info, self.serial_number
            )
            iscsi_targets = vsp_reconciler.iscsi_target_reconciler(
                self.state, self.spec
            )
            self.logger.writeDebug("iscsi_targets = {}", iscsi_targets)
            output_dict = asdict(iscsi_targets)
            self.logger.writeDebug("output_dict = {}", output_dict)
            iscsi_target_data_extracted = (
                VSPIscsiTargetCommonPropertiesExtractor().extract_dict(output_dict)
            )

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of iSCSI Target operation. ===")
            self.module.fail_json(msg=str(e))
        if registration_message:
            iscsi_target_data_extracted["user_consent_required"] = registration_message
        self.logger.writeInfo(f"{iscsi_target_data_extracted}")
        self.logger.writeInfo("=== End of iSCSI Target operation. ===")
        self.module.exit_json(**iscsi_target_data_extracted)


def main(module=None):
    obj_store = VSPIscsiTargetManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
