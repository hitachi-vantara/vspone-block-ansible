#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_sds_block_license_setting_facts
short_description: Get license setting from SDS Block storage system
description:
  - Get license setting from SDS Block storage system.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/sdsb_license_setting_facts.yml)
version_added: '4.6.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.9
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: full
extends_documentation_fragment:
  - hitachivantara.vspone_block.common.sdsb_connection_info
"""

EXAMPLES = """
- name: Retrieve license setting information
  hitachivantara.vspone_block.sds_block.hv_sds_block_license_setting_facts:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
"""

RETURN = r"""
ansible_facts:
  description: >
    Dictionary containing the discovered license setting.
  returned: always
  type: dict
  contains:
    license_setting:
      description: License setting information.
      type: dict
      contains:
        warning_threshold_setting:
          description: Warning threshold settings.
          type: dict
          contains:
            remaining_days:
              description: Remaining days until license expiration warning.
              type: int
              sample: -1
            total_pool_capacity_rate:
              description: Total pool capacity rate threshold.
              type: int
              sample: 80
        overcapacity_allowed:
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


class SDSBLicenseSettingFactsManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = SDSBLicenseSettingArguments().license_setting_facts()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()
        self.logger.writeDebug(
            f"MOD:license_setting:connection_info= {self.connection_info}"
        )

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB License Setting Facts ===")
        license_setting = None
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_reconciler = SDSBLicenseReconciler(self.connection_info)
            license_setting = sdsb_reconciler.get_license_setting()

            self.logger.writeDebug(
                f"MOD:hv_sds_block_license_setting_facts:license_setting= {license_setting}"
            )

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB License Setting Facts ===")
            self.module.fail_json(msg=str(e))

        data = {"license_setting": license_setting}
        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo("=== End of SDSB License Setting Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)


def main():
    obj_store = SDSBLicenseSettingFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
