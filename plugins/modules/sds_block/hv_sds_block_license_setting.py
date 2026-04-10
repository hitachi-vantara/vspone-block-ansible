#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_sds_block_license_setting
short_description: Manage license settings for SDS Block storage system
description:
  - Modify license warning threshold settings for SDS Block storage system.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/sdsb_license_setting.yml)
version_added: '4.6.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.9
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: full
options:
  state:
    description:
      - The desired state of the license settings.
    type: str
    choices: ['present']
    default: present
  spec:
    description:
      - License setting specifications.
    type: dict
    suboptions:
      warning_threshold_setting:
        description:
          - Warning threshold settings for license monitoring.
        type: dict
        suboptions:
          remaining_days:
            description:
              - Number of days remaining until license expiration warning.
              - Use -1 to disable the warning.
              - Valid range is -1 to 60.
            type: int
          total_pool_capacity_rate:
            description:
              - Pool capacity usage rate threshold for warning (percentage).
              - Use -1 to disable the warning.
              - Valid range is -1 or 0 to 100.
            type: int
      allow_over_capacity:
        description:
          - This option is valid only for the AWS cloud model. It specifies whether to allow overcapacity when the license capacity is exceeded.
        type: bool
extends_documentation_fragment:
  - hitachivantara.vspone_block.common.sdsb_connection_info
"""

EXAMPLES = """
- name: Modify license warning threshold settings
  hitachivantara.vspone_block.sds_block.hv_sds_block_license_setting:
    state: present
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      warning_threshold_setting:
        remaining_days: -1
        total_pool_capacity_rate: -1

- name: Set license capacity warning at 80%
  hitachivantara.vspone_block.sds_block.hv_sds_block_license_setting:
    state: present
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      warning_threshold_setting:
        remaining_days: -1
        total_pool_capacity_rate: 80
"""

RETURN = r"""
license_setting:
  description: The updated license setting information.
  returned: always
  type: dict
  contains:
    warningThresholdSetting:
      description: Warning threshold settings.
      type: dict
      contains:
        remainingDays:
          description: Remaining days until license expiration warning.
          type: int
          sample: -1
        totalPoolCapacityRate:
          description: Total pool capacity rate threshold.
          type: int
          sample: 80
    overcapacityAllowed:
      description: Whether overcapacity is allowed.
      type: bool
      sample: null
"""


from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBLicenseSettingArguments,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_license_reconciler import (
    SDSBLicenseReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class SDSBLicenseSettingManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = SDSBLicenseSettingArguments().license_setting()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()
        self.state = parameter_manager.get_state()
        self.spec = parameter_manager.get_license_setting_spec()
        self.logger.writeDebug(f"MOD:license_setting:state= {self.state}")
        self.logger.writeDebug(f"MOD:license_setting:spec= {self.spec}")

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB License Setting Management ===")
        license_setting = None
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_reconciler = SDSBLicenseReconciler(self.connection_info)
            license_setting = sdsb_reconciler.reconcile_license_setting(
                self.spec, self.state
            )
            self.logger.writeDebug(
                f"MOD:hv_sds_block_license_setting:license_setting= {license_setting}"
            )
        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB License Setting Management ===")
            self.module.fail_json(msg=str(e))

        result = {
            "changed": self.connection_info.changed,
            "license_setting": license_setting,
        }

        if registration_message:
            result["user_consent_required"] = registration_message

        self.logger.writeInfo("=== End of SDSB License Setting Management ===")
        self.module.exit_json(**result)


def main():
    obj_store = SDSBLicenseSettingManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
