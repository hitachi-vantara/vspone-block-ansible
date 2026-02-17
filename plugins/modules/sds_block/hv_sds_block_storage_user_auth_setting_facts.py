#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_sds_block_storage_user_auth_setting_facts
short_description: Get user authentication settings from the storage system.
description:
  - Get user authentication settings from the storage system.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/user_auth_setting_facts.yml)
version_added: "4.6.0"
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
- name: Retrieve information about user authentication settings.
  hitachivantara.vspone_block.sds_block.hv_sds_block_storage_user_auth_setting_facts:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
"""

RETURN = r"""
---
ansible_facts:
  description: Facts containing details of user authentication settings configured in the system.
  returned: always
  type: dict
  contains:
    password_complexity_setting:
      description:
        - Password complexity configuration settings.
      returned: success
      type: dict
      contains:
        min_length:
          description:
            - Minimum required length of the password.
          type: int
          sample: 8
        min_number_of_upper_case_chars:
          description:
            - Minimum number of uppercase characters required.
          type: int
          sample: 0
        min_number_of_lower_case_chars:
          description:
            - Minimum number of lowercase characters required.
          type: int
          sample: 0
        min_number_of_numerals:
          description:
            - Minimum number of numeric characters required.
          type: int
          sample: 0
        min_number_of_symbols:
          description:
            - Minimum number of symbol characters required.
          type: int
          sample: 0
        number_of_password_history:
          description:
            - Number of previous passwords that cannot be reused.
          type: int
          sample: 1
    password_age_setting:
      description:
        - Password aging policy settings.
      returned: success
      type: dict
      contains:
        requires_initial_password_reset:
          description:
            - Whether an initial password reset is required.
          type: bool
          sample: true
        min_age_days:
          description:
            - Minimum number of days before a password can be changed.
          type: int
          sample: 0
        max_age_days:
          description:
            - Maximum number of days a password is valid.
          type: int
          sample: 42
    lockout_setting:
      description:
        - Account lockout policy settings.
      returned: success
      type: dict
      contains:
        max_attempts:
          description:
            - Maximum number of failed login attempts before lockout.
          type: int
          sample: 3
        lockout_seconds:
          description:
            - Duration of account lockout in seconds.
          type: int
          sample: 600
    session_setting:
      description:
        - User session timeout settings.
      returned: success
      type: dict
      contains:
        max_lifetime_seconds:
          description:
            - Maximum allowed session lifetime in seconds.
          type: int
          sample: 86400
        max_idle_seconds:
          description:
            - Maximum allowed idle time before session timeout in seconds.
          type: int
          sample: 1800
"""


from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBUserAuthArguments,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_user_auth_setting import (
    SDSBUserAuthSettingReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class SDSBUserAuthSettingFactsManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = SDSBUserAuthArguments().user_auth_facts()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB User Auth Setting Facts ===")
        user_auth_settings = None
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_reconciler = SDSBUserAuthSettingReconciler(self.connection_info)
            user_auth_settings = sdsb_reconciler.get_user_auth_setting()

            self.logger.writeDebug(
                f"MOD:hv_sds_block_storage_user_auth_setting_facts:user_auth_settings= {user_auth_settings}"
            )

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB User Auth Setting Facts ===")
            self.module.fail_json(msg=str(e))

        data = {"user_auth_settings": user_auth_settings}
        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo("=== End of SDSB User Auth Setting Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)


def main():
    obj_store = SDSBUserAuthSettingFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
