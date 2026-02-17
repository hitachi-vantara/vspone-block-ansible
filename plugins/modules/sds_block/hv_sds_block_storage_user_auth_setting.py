#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_sds_block_storage_user_auth_setting
short_description: Manages external authentication server settings on VSP One SDS Block and Cloud systems.
description:
  - This module allows to configure external authentication server settings.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/user_auth_setting.yml)
version_added: '4.6.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.9
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: none
extends_documentation_fragment:
  - hitachivantara.vspone_block.common.sdsb_connection_info
options:
  state:
    description: State of the user authentication settings.
    required: false
    type: str
    choices: ['present']
    default: 'present'
  spec:
    description: Specification for user authentication settings.
    required: true
    type: dict
    suboptions:
      password_age_setting:
        description: Password aging policy configuration. Applicable to users whose authentication is local.
        required: false
        type: dict
        suboptions:
          requires_initial_password_reset:
            description: Whether users are required to reset their password on first login.
            required: false
            type: bool
          min_age_days:
            description: Minimum number of days before a password can be changed. 0 means that the expiration time
              is disabled (the user can change the password immediately). Valid range, 0 - 10.
            required: false
            type: int
          max_age_days:
            description: Maximum number of days a password remains valid. 0 means that this limit is disabled
              (the user can use the password indefinitely). Valid range, 0 - 365.
            required: false
            type: int
      password_complexity_setting:
        description: Password complexity policy configuration. Applicable to users whose authentication is local.
        required: false
        type: dict
        suboptions:
          min_length:
            description: Minimum required length of the password. Valid range, 1 - 256.
            required: false
            type: int
          min_number_of_upper_case_chars:
            description:
              - Minimum number of uppercase characters required. Valid range, 0 - 16.
            required: false
            type: int
          min_number_of_lower_case_chars:
            description: Minimum number of lowercase characters required. Valid range, 0 - 16.
            required: false
            type: int
          min_number_of_numerals:
            description: Minimum number of numeric characters required. Valid range, 0 - 16.
            required: false
            type: int
          min_number_of_symbols:
            description: Minimum number of symbol characters required. Valid range, 0 - 16.
            required: false
            type: int
          number_of_password_history:
            description: Number of previously used passwords that cannot be reused. 1 means that this limit is disabled
              (the user can set the same password as a past one). Valid range, 1 - 10.
            required: false
            type: int
      lockout_setting:
        description: Account lockout policy configuration. Applicable to users whose authentication is local.
        required: false
        type: dict
        suboptions:
          max_attempts:
            description: Maximum number of failed login attempts before the account is locked. 0 means that the function is disabled
              (the user can be unsuccessful an unlimited number of times). Valid range, 0 - 10.
            required: false
            type: int
          lockout_seconds:
            description: Duration of the account lockout in seconds. Valid range, 60 - 600.
            required: false
            type: int
      session_setting:
        description: User session timeout configuration.
        required: false
        type: dict
        suboptions:
          max_lifetime_seconds:
            description: Maximum allowed session lifetime in seconds. Valid range, 1800 - 604800.
            required: false
            type: int
          max_idle_seconds:
            description: Maximum idle time before the session expires, in seconds. Valid range, 300 - 86400.
            required: false
            type: int
"""

EXAMPLES = """
- name: Update user auth settings
  hitachivantara.vspone_block.sds_block.hv_sds_block_storage_user_auth_setting:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      password_age_setting:
        max_age_days: 42
        min_age_days: 0
        requires_initial_password_reset: true
      password_complexity_setting:
        min_length: 8
        min_number_of_lower_case_chars: 1
        min_number_of_numerals: 1
        min_number_of_symbols: 1
        min_number_of_upper_case_chars: 1
        number_of_password_history: 1
      lockout_setting:
        max_attempts: 5
        lockout_seconds: 600
      session_setting:
        max_lifetime_seconds: 86400
        max_idle_seconds: 1800
"""

RETURN = """
user_auth_settings:
  description:
    - User authentication and security policy settings.
  returned: success
  type: dict
  contains:
    lockout_setting:
      description:
        - Account lockout policy configuration.
      type: dict
      contains:
        lockout_seconds:
          description:
            - Duration of account lockout in seconds after exceeding maximum login attempts.
          type: int
          sample: 600
        max_attempts:
          description:
            - Maximum number of failed login attempts before the account is locked.
          type: int
          sample: 5
    password_age_setting:
      description:
        - Password aging policy configuration.
      type: dict
      contains:
        max_age_days:
          description:
            - Maximum number of days a password is valid.
          type: int
          sample: 42
        min_age_days:
          description:
            - Minimum number of days before a password can be changed.
          type: int
          sample: 0
        requires_initial_password_reset:
          description:
            - Indicates whether an initial password reset is required.
          type: bool
          sample: true
    password_complexity_setting:
      description:
        - Password complexity policy configuration.
      type: dict
      contains:
        min_length:
          description:
            - Minimum required length of the password.
          type: int
          sample: 8
        min_number_of_lower_case_chars:
          description:
            - Minimum number of lowercase characters required.
          type: int
          sample: 1
        min_number_of_numerals:
          description:
            - Minimum number of numeric characters required.
          type: int
          sample: 1
        min_number_of_symbols:
          description:
            - Minimum number of symbol characters required.
          type: int
          sample: 1
        min_number_of_upper_case_chars:
          description:
            - Minimum number of uppercase characters required.
          type: int
          sample: 1
        number_of_password_history:
          description:
            - Number of previously used passwords that cannot be reused.
          type: int
          sample: 1
    session_setting:
      description:
        - User session timeout configuration.
      type: dict
      contains:
        max_idle_seconds:
          description:
            - Maximum idle time before the session expires, in seconds.
          type: int
          sample: 1800
        max_lifetime_seconds:
          description:
            - Maximum allowed session lifetime, in seconds.
          type: int
          sample: 86400
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_user_auth_setting import (
    SDSBUserAuthSettingReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBUserAuthArguments,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)


class SDSBUserAuthSettingManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = SDSBUserAuthArguments().user_auth_setting()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )

        try:
            parameter_manager = SDSBParametersManager(self.module.params)
            self.state = parameter_manager.get_state()
            self.connection_info = parameter_manager.get_connection_info()
            self.spec = parameter_manager.get_user_auth_setting_spec()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB User Auth Setting Operation ===")
        registration_message = validate_ansible_product_registration()
        user_auth_settings = None

        try:
            sdsb_reconciler = SDSBUserAuthSettingReconciler(self.connection_info)
            user_auth_settings = sdsb_reconciler.reconcile_user_auth_settings(
                self.spec, self.state
            )

            self.logger.writeDebug(
                f"MOD:hv_sds_block_storage_user_auth_setting:user_auth_settings= {user_auth_settings}"
            )

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB User Auth Setting Operation ===")
            self.module.fail_json(msg=str(e))

        response = {
            "changed": self.connection_info.changed,
            "user_auth_settings": user_auth_settings,
        }

        if registration_message:
            response["user_consent_required"] = registration_message
        self.logger.writeInfo("=== End of SDSB User Auth Setting Operation ===")
        self.module.exit_json(**response)


def main(module=None):
    obj_store = SDSBUserAuthSettingManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
