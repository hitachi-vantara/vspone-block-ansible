#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


__metaclass__ = type
DOCUMENTATION = '''
---
module: hv_hg
author: Hitachi Vantara, LTD. VERSION 3.0.0
short_description: Manages host group on Hitachi VSP storage system.
description:
     - This module provides the following host group management operations
     - 1. create host group.
     - 2. delete host group.
     - 3. add logical unit to host group.
     - 4. remove logical unit from host group.
     - 5. add host WWN to host group.
     - 6. remove host WWN from host group.
     - 7. set host mode.
     - 8. add host mode option to host group.
     - 9. remove host mode option from host group.
version_added: '3.0.0'
requirements:
options:
  state:
    description:
      - set state to I(present) for create and update host group
      - set state to I(absent) for delete host group
    type: str
    required: false
    default: present
    choices: [present, absent]
  storage_system_info:
    description:
      - Information about the Hitachi storage system.
    type: dict
    required: true
    suboptions:
      serial:
        description: Serial number of the Hitachi storage system.
        type: str
        required: true
  connection_info:
    description: Information required to establish a connection to the storage system.
    type: dict
    required: true
    suboptions:
      address:
        description: IP address or hostname of either the UAI gateway (if connection_type is gateway) or the storage system (if connection_type is direct).
        type: str
        required: true
      username:
        description: Username for authentication.
        type: str
        required: false
      password:
        description: Password for authentication.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['gateway', 'direct']
        default: 'direct'
      subscriber_id:
        description: Subscriber ID for multi-tenancy (required for "gateway" connection type).
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway (required for authentication either 'username,password' or api_token).
        type: str
        required: false
  spec:
    description: Specification for hostgroup operation.
    type: dict
    required: true
    suboptions:
      state:
        description: sub task operation.
        type: str
        required: false
        choices: ['present_lun', 'unpresent_lun', 'add_wwn', 'remove_wwn', 'set_host_mode_and_hmo']
      name:
        description: Name of the host group.
        type: str
        required: true
      port:
        description: FC Port.
        type: str
        required: true
      wwns:
        description: List of host WWN to add or remove.
        type: list
        elements: str
        required: false
      luns:
        description: LUNs to be mapped/unmapped with the host group. Supported format can be decimal or HEX.
        type: list
        elements: str
        required: false
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
        description: List of host mode options of host group.
        type: list
        elements: int
        required: false
        choices:
          - 0 [RESERVED]
          - 2 [VERITAS_DB_EDITION_ADV_CLUSTER]
          - 6 [TPRLO]
          - 7 [AUTO_LUN_RECOGNITION]
          - 12 [NO_DISPLAY_FOR_GHOST_LUN]
          - 13 [SIM_REPORT_AT_LINK_FAILURE]
          - 14 [HP_TRUECLUSTER_WITH_TRUECOPY]
          - 15 [RAID_HACMP]
          - 22 [VERITAS_CLUSTER_SERVER]
          - 23 [REC_COMMAND_SUPPORT]
          - 25 [SUPPORT_SPC_3_PERSISTENT_RESERVATION]
          - 33 [SET_REPORT_DEVICE_ID_ENABLE]
          - 39 [CHANGE_NEXUS_SPECIFIED_IN_SCSI_TARGET_RESET]
          - 40 [VVOL_EXPANSION]
          - 41 [PRIORITIZED_DEVICE_RECOGNITION]
          - 42 [PREVENT_OHUB_PCI_RETRY]
          - 43 [QUEUE_FULL_RESPONSE]
          - 48 [HAM_SVOL_READ]
          - 49 [BB_CREDIT_SETUP_1]
          - 50 [BB_CREDIT_SETUP_2]
          - 51 [ROUND_TRIP_SETUP]
          - 52 [HAM_AND_CLUSTER_SW_FOR_SCSI_2]
          - 54 [EXTENDED_COPY]
          - 57 [HAM_RESPONSE_CHANGE]
          - 60 [LUN0_CHANGE_GUARD]
          - 61 [EXPANDED_PERSISTENT_RESERVE_KEY]
          - 63 [VSTORAGE_APIS_ON_T10_STANDARDS]
          - 65 [ROUND_TRIP_EXTENDED_SETUP]
          - 67 [CHANGE_OF_ED_TOV_VALUE]
          - 68 [PAGE_RECLAMATION_LINUX]
          - 69 [ONLINE_LUSE_EXPANSION]
          - 71 [CHANGE_UNIT_ATTENTION_FOR_BLOCKED_POOL_VOLS]
          - 72 [AIX_GPFS]
          - 73 [WS2012]
          - 78 [NON_PREFERRED_PATH]
          - 91 [DISABLE_IO_WAIT_FOR_OPEN_STACK]
          - 95 [CHANGE_SCSI_LU_RESET_NEXUS_VSP_HUS_VM]
          - 96 [CHANGE_SCSI_LU_RESET_NEXUS]
          - 97 [PROPRIETARY_ANCHOR_COMMAND_SUPPORT]
          - 100 [HITACHI_HBA_EMULATION_CONNECTION_OPTION]
          - 102 [GAD_STANDARD_INQURY_EXPANSION_HCS]
          - 105 [TASK_SET_FULL_RESPONSE_FOR_IO_OVERLOAD]
          - 110 [ODX Support for WS2012]
          - 113 [iSCSI CHAP Authentication Log]
          - 114 [Auto Asynchronous Reclamation on ESXi 6.5+]
          - 122 [TASK_SET_FULL_RESPONSE_AFTER_QOS_UPPER_LIMIT]
          - 124 [GUARANTEED_RESPONSE_DURING_CONTROLLER_FAILURE]
          - 131 [WCE_BIT_OFF_MODE]
      should_delete_all_luns:
        description: If the value is true, destroy the logical units that are no longer attached to any host group or iSCSI target.
        required: false
'''

EXAMPLES = '''
-
  name: Create host group with LUN in decimal
  tasks:
    - hv_hg:
        state: present
        storage_system_info:
          serial: '446039'
        connection_info:
          address: storage1.company.com
          username: "{{management_username}}"
          password: "{{management_password}}"
        spec:
         name: 'testhg26dec'
         port: 'CL1-A'
         host_mode: 'VMWARE_EXTENSION'
         wwns: [ '100000109B583B2D', '100000109B583B2C' ]
         luns: [ 393, 851 ]
      register: result
    - debug: var=result.hostGroups
-
  name: Create host group with LUN in HEX
  tasks:
    - hv_hg:
        state: present
        storage_system_info:
          serial: '446039'    
        connection_info:
          address: storage1.company.com
          username: "{{management_username}}"
          password: "{{management_password}}"
        host_group_info:
          name: 'testhg26dec'
          port: 'CL1-A'
          host_mode: 'VMWARE_EXTENSION'
          host_mode_options: [ 54, 63 ]
          wwns: [ '100000109B583B2D', '100000109B583B2C' ]
          luns: [ 00:23:A4 ]
      register: result
    - debug: var=result.hostGroups
-
  name: Delete host group
  vars:
    - storage_serial: "715035"
    - host_group_name: test-ansible-hg-1
    - port: CL2-B
  tasks:
    - hv_hg:
        state: absent
        storage_system_info:
          serial: '446039'
        connection_info:
          address: storage1.company.com
          username: "{{management_username}}"
          password: "{{management_password}}"
        spec:
          name: 'testhg26dec'
          port: 'CL1-A'
      register: result
    - debug: var=result
-
  name: Present LUN
  tasks:
    - hv_hg:
        state: present
        storage_system_info:
          serial: '446039'
        connection_info:
          address: storage1.company.com
          username: "{{management_username}}"
          password: "{{management_password}}"
        host_group_info:
          state: present_lun
          name: 'testhg26dec'
          port: 'CL1-A'
          luns: [ 00:05:77, 00:05:7D ]
      register: result
-
  name: Unpresent LUN
  tasks:
    - hpe_hg:
        state: present
        storage_system_info:
          serial: '446039'
        connection_info:
          address: storage1.company.com
          username: "{{management_username}}"
          password: "{{management_password}}"
        spec:
          state: unpresent_lun
          name: 'testhg26dec'
          port: 'CL1-A'
          luns: [ 800, 801 ]
      register: result
-
  name: Add WWN
  tasks:
    - hv_hg:
        state: present
        storage_system_info:
          serial: '446039'
        connection_info:
          address: storage1.company.com
          username: "{{management_username}}"
          password: "{{management_password}}"
        spec:
          state: add_wwn
          name: 'testhg26dec'
          port: 'CL1-A'
          wwns: [ 200000109B3C0FD3 ]
      register: result
    - debug: var=result
-
  name: Remove WWN
  tasks:
    - hv_hg:
        state: present
        storage_system_info:
          serial: '446039'
        connection_info:
          address: storage1.company.com
          username: "{{management_username}}"
          password: "{{management_password}}"
        spec:
          state: remove_wwn
          name: 'testhg26dec'
          port: 'CL1-A'
          wwns: [ 200000109B3C0FD3 ]
      register: result
    - debug: var=result
-
  name: Update host group
  tasks:
    - hv_hg:
        state: present
        storage_system_info:
          serial: '446039'
        connection_info:
          address: storage1.company.com
          username: "{{management_username}}"
          password: "{{management_password}}"
        spec:
          state: set_host_mode_and_hmo
          name: 'testhg26dec'
          port: 'CL1-A'
          host_mode: 'VMWARE_EXTENSION'
          host_mode_options: [ 54, 63 ]
      register: result
    - debug: var=result
'''

RETURN = '''
hostGroups:
  type: dict
  description: Info of host group.
  returned: always
  elements: dict
  sample: {
    "entitlement_status": "assigned",
    "host_group_id": 93,
    "host_group_name": "ansible-test-hg",
    "host_mode": "STANDARD",
    "host_mode_options": [
        {
            "host_mode_option": "EXTENDED_COPY",
            "host_mode_option_number": 54
        },
        {
            "host_mode_option": "VSTORAGE_APIS_ON_T10_STANDARDS",
            "host_mode_option_number": 63
        }
    ],
    "lun_paths": [
      {
        "ldevId": 166,
        "lunId": 0
      },
      {
        "ldevId": 206,
        "lunId": 1
      }
    ],
    "partner_id": "partnerid",
    "port": "CL1-A",
    "resource_group_id": 0,
    "storage_id": "storage-39f4eef0175c754bb90417358b0133c3",
    "subscriber_id": "12345",
    "wwns": [
      {
        "id": "1212121212121212",
        "name": ""
      }
    ]
  }
'''

import json
from dataclasses import dataclass, asdict

try:
    from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_logger import (
        MessageID,
    )

    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_exceptions import (
    HiException,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_infra import (
    StorageSystem,
    StorageSystemManager,
)
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_hg_runner as runner
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPHostGroupArguments,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    StateValue,
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_host_group,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    camel_to_snake_case,
    camel_dict_to_snake_case,
)

ANSIBLE_METADATA = {
    "metadata_version": "1.1",
    "supported_by": "certified",
    "status": ["stableinterface"],
}

logger = Log()


class VSPHostGroupManager:
    def __init__(self):
      try:
        self.argument_spec = VSPHostGroupArguments().host_group()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )

        self.params = VSPParametersManager(self.module.params)
        self.serial_number = self.params.storage_system_info.serial

        parameterManager = VSPParametersManager(self.module.params)
        self.state = parameterManager.get_state()
        self.spec = parameterManager.host_group_spec()
        self.connection_info = parameterManager.get_connection_info()
        
      except Exception as e:
        self.module.fail_json(msg=str(e))

    def apply(self):
        logger = Log()
        host_group_data = None
        host_group_data_extracted = None
        logger.writeInfo(
            f"{self.params.connection_info.connection_type} connection type"
        )
        try:
            if (
                self.params.connection_info.connection_type.lower()
                == ConnectionTypes.DIRECT
            ):
                host_group_data = asdict(self.direct_host_group_modification())
                logger.writeInfo("host_group_data {}", host_group_data)
            elif (
                self.params.connection_info.connection_type.lower()
                == ConnectionTypes.GATEWAY
            ):
                host_group_list = self.gateway_host_group_modification()
                host_group_data = {host_group_list}
            host_group_data_extracted = (
                vsp_host_group.VSPHostGroupCommonPropertiesExtractor(
                    self.serial_number
                ).extract_dict(host_group_data)
            )

        except Exception as e:
            self.module.fail_json(msg=str(e))

        self.module.exit_json(**host_group_data_extracted)

    def direct_host_group_modification(self):
        result = vsp_host_group.VSPHostGroupReconciler(
            self.connection_info, self.serial_number
        ).host_group_reconcile(self.state, self.spec)
        if result is None:
            self.module.fail_json("Couldn't read host group ")
        return result

    def gateway_host_group_modification(self):
        self.module.params["spec"] = self.module.params.get("spec")
        try:
            return runner.runPlaybook(self.module)
        except HiException as ex:
            self.module.fail_json(msg=ex.format())
        except Exception as ex:
            self.module.fail_json(msg=str(ex))


def main(module=None):
    obj_store = VSPHostGroupManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
