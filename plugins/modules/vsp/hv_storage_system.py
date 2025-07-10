#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_storage_system
short_description: This module specifies storage systems settings like updating the date and time.
description:
  - This module allows you to configure various storage system settings, such as updating the date and time, enabling or disabling NTP, setting time zones.
  - For example usage, visit
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/storage_system.yml)
version_added: '4.0.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.8
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: none
extends_documentation_fragment:
  - hitachivantara.vspone_block.common.gateway_note
  - hitachivantara.vspone_block.common.connection_info
options:
  spec:
    description: Specification storage system.
    type: dict
    required: true
    suboptions:
      date_time:
        description: Date and time configuration for the storage system.
        type: dict
        required: true
        suboptions:
          is_ntp_enabled:
            description: Whether NTP is enabled.
            type: bool
            required: true
          ntp_server_names:
            description: List of NTP server names.
            type: list
            elements: str
            required: false
          time_zone_id:
            description: Time zone identifier.
            type: str
            required: true
          system_time:
            description: System time in ISO format.
            type: str
            required: true
          synchronizing_local_time:
            description: Synchronizing local time.
            type: str
            required: false
          adjusts_daylight_saving_time:
            description: Whether daylight saving time is adjusted.
            type: bool
            required: false
          synchronizes_now:
            description: Whether to synchronize time immediately.
            type: bool
            required: false
"""

EXAMPLES = """
- name: Configure storage system date and time settings
  hitachivantara.vspone_block.vsp.hv_storage_system:
    connection_info:
      address: 192.0.2.10
      username: admin
      password: secret
    spec:
      date_time:
        is_ntp_enabled: true
        ntp_server_names:
          - "ntp1.example.com"
          - "ntp2.example.com"
        time_zone_id: "UTC"
        system_time: "2024-06-01T12:00:00Z"
        synchronizing_local_time: "2024-06-01T12:00:00Z"
        adjusts_daylight_saving_time: true
        synchronizes_now: false
"""

RETURN = """

"""


from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPStorageSystemARgs,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_storage_system import (
    VSPStorageSystemReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class StorageSystemModule:
    """
    Class representing StorageSystemModule Module.
    """

    def __init__(self):

        self.logger = Log()
        self.argument_spec = VSPStorageSystemARgs().storage_system_args()

        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
        )
        try:
            self.parameter_manager = VSPParametersManager(self.module.params)
            self.spec = self.parameter_manager.set_storage_system_spec()
        except Exception as e:
            self.logger.writeError(f"An error occurred during initialization: {str(e)}")
            self.module.fail_json(msg=str(e))

    def apply(self):

        self.logger.writeInfo("=== Start of Storage System Module ===")
        registration_message = validate_ansible_product_registration()

        try:
            response, msg = VSPStorageSystemReconciler(
                self.parameter_manager.connection_info
            ).storage_system_reconcile(self.spec)

        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of Storage System Module ===")
            self.module.fail_json(msg=str(e))

        data = {
            "system_info": response,
            "changed": self.parameter_manager.connection_info.changed,
            "message": msg,
        }
        if registration_message:
            data["user_consent_required"] = registration_message

        self.logger.writeInfo(f"{data}")
        self.logger.writeInfo("=== End of Storage System Module ===")
        self.module.exit_json(**data)


def main():
    obj_store = StorageSystemModule()
    obj_store.apply()


if __name__ == "__main__":
    main()
