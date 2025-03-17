#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_journal_volume
short_description: Create, update, expand, shrink, delete journal volume from Hitachi VSP storage systems.
description:
  - This module creates, update, expand, shrink, delete journal volume from Hitachi VSP storage systems.
  - This module is supported for both C(direct) and C(gateway) connection types.
  - For C(direct) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/journal_volume.yml)
  - For C(gateway) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/journal_volume.yml)
version_added: '3.0.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.8
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: full
options:
  state:
    description: State of the Journal Volume.
    type: str
    required: false
    choices: ['present', 'absent', 'update', 'expand_journal_volume', 'shrink_journal_volume']
    default: 'present'
  storage_system_info:
    description: Information about the Hitachi storage system.
    type: dict
    required: false
    suboptions:
      serial:
        description: Serial number of the Hitachi storage system.
        type: str
        required: false
  connection_info:
    description: Information required to establish a connection to the storage system.
    type: dict
    required: true
    suboptions:
      address:
        description: IP address or hostname of either the UAI gateway (if connection_type is C(gateway)) or
          the storage system (if connection_type is C(direct)).
        type: str
        required: true
      username:
        description: Username for authentication. This field is valid for C(direct) connection type only, and it is a required field.
        type: str
        required: false
      password:
        description: Password for authentication. This field is valid for C(direct) connection type only, and it is a required field.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['gateway', 'direct']
        default: 'direct'
      subscriber_id:
        description: This field is valid for C(gateway) connection type only. This is an optional field and only needed to support multi-tenancy environment.
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway. This is a required field for C(gateway) connection type.
        type: str
        required: false
  spec:
    description: Specification for creating Journal Volume.
    type: dict
    required: false
    suboptions:
      journal_id:
        description: Journal ID of the Journal Volume.
        type: int
        required: false
      startLdevId:
        description: Start LDEV ID of the Journal Volume.
        type: int
        required: false
      endLdevId:
        description: End LDEV ID of the Journal Volume.
        type: int
        required: false
      is_cache_mode_enabled:
        description: Cache mode enabled or not.
        type: bool
        required: false
      data_overflow_watchIn_seconds:
        description: Data overflow watch in seconds.
        type: int
        required: false
      mp_blade_id:
        description: MP Blade ID of the Journal Volume.
        type: int
        required: false
      ldev_ids:
        description: List of LDEVs.
        type: list
        required: false
        elements: int
"""

EXAMPLES = """
- name: Create Journal Volume
  hitachivantara.vspone_block.vsp.hv_journal_volume:
    connection_info:
      address: storage1.company.com
      api_token: "api_token"
      connection_type: "gateway"
    storage_system_info:
      serial: "811150"
    state: "present"
    spec:
      journal_id: 35
      ldev_ids: [105, 106]

- name: Expand Journal Volume
  hitachivantara.vspone_block.vsp.hv_journal_volume:
    connection_info:
      address: storage1.company.com
      api_token: "api_token"
      connection_type: "gateway"
    storage_system_info:
      serial: "811150"
    state: "expand_journal_volume"
    spec:
      journal_id: 35
      ldev_ids: [107]

- name: Delete Journal Volume
  hitachivantara.vspone_block.vsp.hv_journal_volume:
    connection_info:
      address: storage1.company.com
      api_token: "api_token"
      connection_type: "gateway"
    storage_system_info:
      serial: "811150"
    state: "absent"
    spec:
      journal_id: 35
"""

RETURN = r"""
data:
  description: >
    Dictionary containing the discovered properties of the Journal Volumes.
  returned: always
  type: dict
  contains:
    journal_volume:
      description: List of Journal Volumes managed by the module.
      returned: success
      type: dict
      contains:
        data_overflow_watch_seconds:
          description: Data overflow watch in seconds.
          type: int
          sample: 60
        first_ldev_id:
          description: First LDEV ID of the Journal Volume.
          type: int
          sample: 1992
        is_cache_mode_enabled:
          description: Indicates if cache mode is enabled.
          type: bool
          sample: true
        is_inflow_control_enabled:
          description: Indicates if inflow control is enabled.
          type: bool
          sample: false
        journal_id:
          description: Journal ID of the Journal Volume.
          type: int
          sample: 37
        journal_status:
          description: Status of the Journal Volume.
          type: str
          sample: "PJNN"
        mirror_unit_ids:
          description: List of mirror unit IDs.
          type: list
          elements: dict
          contains:
            consistency_group_id:
              description: Consistency group ID.
              type: int
              sample: 0
            copy_pace:
              description: Copy pace.
              type: str
              sample: "L"
            copy_speed:
              description: Copy speed.
              type: int
              sample: 256
            is_data_copying:
              description: Indicates if data copying is in progress.
              type: bool
              sample: true
            journal_status:
              description: Status of the journal.
              type: str
              sample: "SMPL"
            mu_number:
              description: Mirror unit number.
              type: int
              sample: 0
            path_blockade_watch_in_minutes:
              description: Path blockade watch in minutes.
              type: int
              sample: 5
        mp_blade_id:
          description: MP Blade ID of the Journal Volume.
          type: int
          sample: 1
        num_of_active_paths:
          description: Number of active paths.
          type: int
          sample: 2
        num_of_ldevs:
          description: Number of LDEVs.
          type: int
          sample: 1
        q_count:
          description: Queue count.
          type: int
          sample: 0
        q_marker:
          description: Queue marker.
          type: str
          sample: "00000002"
        total_capacity_mb:
          description: Total capacity in MB.
          type: int
          sample: 19
        usage_rate:
          description: Usage rate.
          type: int
          sample: 0
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_journal_volume,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPParametersManager,
    VSPJournalVolumeArguments,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class VSPJournalVolumeManager:
    def __init__(self):
        self.logger = Log()

        self.argument_spec = VSPJournalVolumeArguments().journal_volume()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.journal_volume_spec()
            self.serial = self.params_manager.get_serial()
            self.state = self.params_manager.get_state()
            self.connection_info = self.params_manager.get_connection_info()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Journal Volume operation. ===")
        try:
            registration_message = validate_ansible_product_registration()
            result, res_msg = vsp_journal_volume.VSPJournalVolumeReconciler(
                self.params_manager.connection_info, self.serial
            ).journal_volume_reconcile(self.state, self.spec)

            msg = res_msg if res_msg else self.get_message()
            result = result if not isinstance(result, str) else None
            response_dict = {
                "changed": self.connection_info.changed,
                "data": result,
                "msg": msg,
            }
            if registration_message:
                response_dict["user_consent_required"] = registration_message
            self.logger.writeInfo(f"{response_dict}")
            self.logger.writeInfo("=== End of Journal Volume operation. ===")
            self.module.exit_json(**response_dict)
        except Exception as ex:
            self.logger.writeException(ex)
            self.logger.writeInfo("=== End of Journal Volume operation. ===")
            self.module.fail_json(msg=str(ex))

    def get_message(self):

        if self.state == "present":
            return "Journal Volume created successfully."
        elif self.state == "absent":
            return "Journal Volume deleted successfully."
        elif self.state == "expand_journal_volume":
            return "Journal Volume expanded successfully."
        elif self.state == "shrink_journal_volume":
            return "Journal Volume shrunk successfully."
        elif self.state == "update":
            return "Journal Volume updated successfully."
        else:
            return "Unknown state provided."


def main(module=None):
    obj_store = VSPJournalVolumeManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
