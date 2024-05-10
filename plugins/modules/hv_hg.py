#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)



__metaclass__ = type
DOCUMENTATION = \
    r'''
---
module: hv_hg
author: Hitachi Vantara, LTD. VERSION 02.3.0
short_description: This module manages host group on Hitachi Storage System.
description:
     - The M(hv_hg) module provides the following host group management operations
     - 1. create host group.
     - 2. delete host group.
     - 3. add logical unit to host group.
     - 4. remove logical unit from host group.
     - 5. add host WWN to host group.
     - 6. remove host WWN from host group.
     - 7. set host mode.
     - 8. add host mode option to host group.
     - 9. remove host mode option from host group.
version_added: '02.9.0'
requirements:
options:
  collections:
    description:
      - Ansible collections name for Hitachi storage modules 
    type: string
    required: yes
    default: hitachi.storage
  state:
    description:
      - set state to I(present) for create and update host group
      - set state to I(absent) for delete host group
    type: str
    default: present
    choices: [present, absent]
  storage_system_info:
    required: yes
    description:
      - storage_system_info has the following properties
      - =================================================================
      - Storage System information
      - =================================================================
      - C(storage_serial:) Mandatory input. String type. Storage system serial number.
      - C(ucp_name:) Mandatory input. String type. UCP system name.
      - =================================================================
    default: n/a
  ucp_advisor_info:
    required: yes
    description:
      - ucp_advisor_info has the following properties
      - =================================================================
      - UCP Advisor information
      - =================================================================
      - C(ucpadvisor_address:) Mandatory input. String type. UCPA address.
      - C(ucpadvisor_ansible_vault_user:) Mandatory input. String type. UCPA user name.
      - C(ucpadvisor_ansible_vault_secret:) Mandatory input. String type. UCPA password in clear text.
      - =================================================================
    default: n/a
  hg_info:
    required: yes
    description:
      - data has the following properties
      - =================================================================
      - Create Host Group
      - =================================================================
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(name:) Mandatory input. String type. Name of the Host group to be created.
      - C(host_mode :) Optional. String type. Valid values
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
      - C(host_mode_options :) Optional. string type. Valid values
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
      - 95 [CHANGE_SCSI_LU_RESET_NEXUS_VSP_HUS_VM]
      - 96 [CHANGE_SCSI_LU_RESET_NEXUS]
      - 97 [PROPRIETARY_ANCHOR_COMMAND_SUPPORT]
      - 100 [HITACHI_HBA_EMULATION_CONNECTION_OPTION]
      - 102 [GAD_STANDARD_INQURY_EXPANSION_HCS]
      - 105 [TASK_SET_FULL_RESPONSE_FOR_IO_OVERLOAD]
      - 110 [ODX Support for WS2012]
      - 113 [iSCSI CHAP Authentication Log]
      - 114 [Auto Asynchronous Reclamation on ESXi 6.5+]
      - C(wwns :) Optional. array type. List of Host WWN.
      - C(ports :) Mandatory input. array type. List of FC Ports.
      - C(luns :) Optional. array type. LUNs to be mapped with the host group.Supported format can be decimal or HEX.
      - =================================================================
      - Delete Host Group
      - =================================================================
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(name:) Mandatory input. String type. Name of the Host group to be deleted.
      - C(ports :) Mandatory input. array type. List of FC Ports from where the hostgroup need to be deleted.

      - =================================================================
      - Unpresent LUN
      - =================================================================
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(name:) Mandatory input. String type. Name of the Host group.
      - C(ports :) Optional input. array type. List of FC Ports.
      - C(luns :) Mandatory input. array type. LUNs to be unmapped from the host group.Supported format can be decimal or HEX

      - =================================================================
      - present LUN
      - =================================================================
      - C(storage_serial:) Mandatory input. integer type. Storage system serial number.
      - C(name:) Mandatory input. String type. Name of the Host group.
      - C(ports :) Optional input. array type. List of FC Ports.
      - C(luns :) Mandatory input. array type. LUNs to be mapped with the host group.Supported format can be decimal or HEX

      - =================================================================

'''

EXAMPLES = \
    r'''
-
  name: Create Host Group with LUN in decimal
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: ../ansible_vault_vars/ansible.vault.vars.ucpa.yml.20.90
  vars:
    - storage_serial: 446039
    - ucp_name: UCP-CI-71366
    - host_group_name: testhg26dec
    - ports:
      - CL1-A
      - CL1-B
    - host_mode: LINUX
    - host_mode_options:
      - 40
    - storage_serial: 12345
    - wwns:
      - 100000109B583B2D
      - 100000109B583B3C
    - luns:
      - 393
      - 851
  tasks:
    - hv_hg:
        state: present

        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
          
        ucp_advisor_info:
          address: "{{ucpadvisor_address}}"
          username: "{{ucpadvisor_ansible_vault_user}}"
          password: "{{ucpadvisor_ansible_vault_secret}}"

        host_group_info:
         state: '{{ state | default(omit)}}'
         name: '{{ host_group_name }}'
         ports: '{{ ports }}'
         host_mode: '{{ host_mode | default(None)}}'
         host_mode_options: '{{ host_mode_options | default(None)}}'
         wwns: '{{ wwns | default(None) }}'
         Luns: '{{ luns | default(None) }}'
      register: result
    - debug: var=result.hostGroups
-
-
  name: Create Host Group with LUN in HEX
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: ../ansible_vault_vars/ansible.vault.vars.ucpa.yml.20.90
  vars:
    - storage_serial: 446039
    - host_group_name: nest99
    - ports:
      - CL1-A
      - CL2-B
    - host_mode: VMWARE_EXTENSION
    - host_mode_options:
      - 54
      - 63
    - storage_serial: 12345
    - luns:
      - 00:23:A4
    - wwns:
      - 5555511111391237
  tasks:
    - hv_hg:
        state: present

        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
          
        ucp_advisor_info:
          address: "{{ucpadvisor_address}}"
          username: "{{ucpadvisor_ansible_vault_user}}"
          password: "{{ucpadvisor_ansible_vault_secret}}"

        host_group_info:
          name: '{{ host_group_name }}'
          ports: '{{ ports }}'
          host_mode: '{{ host_mode | default(None)}}'
          host_mode_options: '{{ host_mode_options | default(None)}}'
          wwns: '{{ wwns | default(None) }}'
          luns: '{{ luns | default(None) }}'
          state: '{{ state | default(None) }}'
      register: result
    - debug: var=result.hostGroups
-
  name: Testing Delete Host Group
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: ../ansible_vault_vars/ansible.vault.vars.ucpa.yml
  vars:
    - storage_serial: "715035"
    - ucp_name: "20-253"
    - host_group_name: test-ansible-hg-1
    - ports:
      - CL2-B
  tasks:
    - hv_hg:
        state: absent

        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
          
        ucp_advisor_info:
          address: "{{ucpadvisor_address}}"
          username: "{{ucpadvisor_ansible_vault_user}}"
          password: "{{ucpadvisor_ansible_vault_secret}}"

        spec:
          name: '{{ host_group_name }}'
          ports: '{{ ports | default(None) }}'
          
      register: result
    - debug: var=result
-
-
  name: Testing Unpresent LUN with LUN in HEX
  hosts: localhost
  gather_facts: false
  collections:
    - hitachi.storage
  pre_tasks:
    - include_vars: ../ansible_vault_vars/ansible.vault.vars.ucpa.yml.20.90
  vars:
    - storage_serial: 446039
    - host_group_name: test-ansible-hg-1
    - luns:
      - 00:00:1D
      - 00:00:1A
    - storage_serial: 12345
  tasks:
    - hpe_hg:
        state: present

        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
          
        ucp_advisor_info:
          address: "{{ucpadvisor_address}}"
          username: "{{ucpadvisor_ansible_vault_user}}"
          password: "{{ucpadvisor_ansible_vault_secret}}"

        host_group_info:
          state: unpresent_lun
          name: '{{ host_group_name }}'
          ports: '{{ ports | default(None) }}'
          luns: '{{ luns }}'
      register: result
-
  name: Testing Unpresent LUN with LUN in decimal
  hosts: localhost
  gather_facts: false
  collections:
    - hitachi.storage
  pre_tasks:
    - include_vars: ../ansible_vault_vars/ansible.vault.vars.ucpa.yml.20.90
  vars:
    - storage_serial: 446039
    - host_group_name: test-ansible-hg-1
    - luns:
      - 800
      - 801
    - storage_serial: 12345
  tasks:
    - hpe_hg:
        state: present

        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
          
        ucp_advisor_info:
          address: "{{ucpadvisor_address}}"
          username: "{{ucpadvisor_ansible_vault_user}}"
          password: "{{ucpadvisor_ansible_vault_secret}}"

        host_group_info:
          state: unpresent_lun
          name: '{{ host_group_name }}'
          ports: '{{ ports | default(None) }}'
          luns: '{{ luns }}'
      register: result
-
-
  name: Testing Present LUN with LUN in HEX
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: ../ansible_vault_vars/ansible.vault.vars.ucpa.yml.20.90
  vars:
    - storage_serial: 446039
    - host_group_name: delta1
    - luns:
      - 00:05:77
      - 00:05:7D
    - ports:
      - CL2-A
    - storage_serial: 12345
  tasks:
    - hv_hg:
        state: present

        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
          
        ucp_advisor_info:
          address: "{{ucpadvisor_address}}"
          username: "{{ucpadvisor_ansible_vault_user}}"
          password: "{{ucpadvisor_ansible_vault_secret}}"

        host_group_info:
          state: present_lun
          name: '{{ host_group_name }}'
          ports: '{{ ports | default(None) }}'
          luns: '{{ luns | default(None) }}'
      register: result
-
-
  name: Testing Present LUN with LUN in decimal
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: ../ansible_vault_vars/ansible.vault.vars.ucpa.yml.20.90
  vars:
    - storage_serial: 446039
    - host_group_name: snewar-ansible-hg-111
    - luns:
      - 859
      - 847
    - storage_serial: 12345
    - ports:
      - CL2-A
  tasks:
    - hv_hg:

        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
          
        ucp_advisor_info:
          address: "{{ucpadvisor_address}}"
          username: "{{ucpadvisor_ansible_vault_user}}"
          password: "{{ucpadvisor_ansible_vault_secret}}"

        spec:
          state: present_lun
          name: '{{ host_group_name }}'
          ports: '{{ ports | default(None) }}'
          luns: '{{ luns | default(None) }}'
      register: result

-
  name: Update Host Group WWN
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: ../ansible_vault_vars/ansible.vault.vars.ucpa.yml
  vars:
    - storage_serial: "715035"
    - ucp_name: "20-253"
    - host_group_name: test-ansible-hg-1
    - wwns:
      - 200000109B3C0FD3
    - ports:
      - CL2-B
  tasks:
    - hv_hg:
        state: present

        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
          
        ucp_advisor_info:
          address: "{{ucpadvisor_address}}"
          username: "{{ucpadvisor_ansible_vault_user}}"
          password: "{{ucpadvisor_ansible_vault_secret}}"

        spec:
          state: add_wwn
          name: '{{ host_group_name }}'
          ports: '{{ ports }}'
          wwns: '{{ wwns }}'
      register: result
    - debug: var=result
      
-
  name: Update Host Group
  hosts: localhost
  collections:
    - hitachi.storage
  gather_facts: false
  pre_tasks:
    - include_vars: ../ansible_vault_vars/ansible.vault.vars.ucpa.yml
  vars:
    - storage_serial: "715035"
    - ucp_name: "20-253"
    - host_group_name: test-ansible-hg-1
    - ports:
      - CL2-A
    - host_mode: VMWARE_EXTENSION
    - host_mode_options:
      - 54
      - 63
  tasks:
    - hv_hg:
        state: present

        storage_system_info:
          serial: '{{ storage_serial }}'
          ucp_name: '{{ ucp_name }}'
          
        ucp_advisor_info:
          address: "{{ucpadvisor_address}}"
          username: "{{ucpadvisor_ansible_vault_user}}"
          password: "{{ucpadvisor_ansible_vault_secret}}"

        spec:
          state: set_host_mode_and_hmo
          name: '{{ host_group_name }}'
          ports: '{{ ports }}'
          host_mode: '{{ host_mode | default(None)}}'
          host_mode_options: '{{ host_mode_options | default(None)}}'
      register: result
    - debug: var=result


'''

RETURN = """
"""

try:
    from ansible_collections.hitachi.storage.plugins.module_utils.hv_logger import MessageID
    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False

from ansible_collections.hitachi.storage.plugins.module_utils.hv_log import Log, \
    HiException
from ansible_collections.hitachi.storage.plugins.module_utils.hv_infra import StorageSystem, \
    StorageSystemManager
from ansible.module_utils.basic import AnsibleModule
import ansible_collections.hitachi.storage.plugins.module_utils.hv_hg_runner as runner
ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'supported_by': 'certified',
                    'status': ['stableinterface']}

logger = Log()


def main(module=None):
    fields = {'storage_serial': {'required': True, 'type': 'int'},
              'state': {'default': 'present', 'choices': ['present', 'absent']}, 'data': {'required': False, 'type': 'json'}}
    fields = {
        'storage_system_info': {'required': True, 'type': 'json'},
        'ucp_advisor_info': {'required': True, 'type': 'json'},
        'spec': {'required': True, 'type': 'json'},
        'state': {'default': 'present', 'choices': ['present', 'absent']}
        }
    if module is None:
        module = AnsibleModule(argument_spec=fields)

    try:
        runner.runPlaybook(module)
    except HiException as ex:
        if HAS_MESSAGE_ID:
            logger.writeAMException(MessageID.ERR_OPERATION_HOSTGROUP)
        else:
            logger.writeAMException("0x000000")
        module.fail_json(msg=ex.format())
    except Exception as ex:
        module.fail_json(msg=str(ex))


if __name__ == '__main__':
    main()
