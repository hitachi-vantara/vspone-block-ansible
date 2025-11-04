#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_sds_block_user
short_description: Create and update users from storage system
description:
  - Create and update users from storage system.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/sdsb_users.yml)
version_added: "4.1.0"
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
options:
  state:
    description: The level of the user task.
    type: str
    required: false
    choices: ['present', 'update']
    default: 'present'
  spec:
    description: Specification for the user task.
    type: dict
    required: false
    suboptions:
      user_id:
        description: The user ID (username) whose information is to be retrieved.
        type: str
        required: false
      password:
        description: Password for the user.
        type: str
        required: false
      current_password:
        description: Current password for the user.
        type: str
        required: false
      new_password:
        description: New password for the user.
        type: str
        required: false
      authentication:
        description: Authentication method for the user.
        type: str
        choices: ['local', 'external']
        default: 'local'
      user_group_ids:
        description: List of user group IDs to which the user belongs.
        type: list
        elements: str
      is_enabled_console_login:
        description: Whether the user can log in to the console.
        type: bool
        default: true
"""

EXAMPLES = """
- name: Create a new user
  hitachivantara.vspone_block.sds_block.hv_sds_block_user:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    state: present
    spec:
      user_id: "new_user"
      password: "CHANGE_ME_SET_YOUR_PASSWORD"
      user_group_ids:
        - "admin_group"
      authentication: "local"
      is_enabled_console_login: true

- name: Update an existing user password
  hitachivantara.vspone_block.sds_block.hv_sds_block_user:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    state: update
    spec:
      user_id: "existing_user"
      current_password: "CHANGE_ME_SET_YOUR_PASSWORD"
      new_password: "CHANGE_ME_SET_YOUR_PASSWORD"
"""

RETURN = r"""
users:
  description: Details of the user retrieved or managed by the module.
  type: dict
  returned: always
  contains:
    authentication:
      description: Type of authentication for the user.
      type: str
      sample: "local"
    is_built_in:
      description: Indicates if the user is a built-in system user.
      type: bool
      sample: false
    is_enabled:
      description: Indicates if the user account is enabled.
      type: bool
      sample: true
    is_enabled_console_login:
      description: Indicates if console login is allowed for the user.
      type: bool
      sample: true
    password_expiration_time:
      description: Expiration time of the user's password in ISO 8601 format.
      type: str
      sample: "2025-10-17T17:49:42Z"
    privileges:
      description: List of privileges assigned to the user.
      type: list
      elements: dict
      contains:
        role_names:
          description: List of role names assigned in this privilege.
          type: list
          elements: str
          sample: ["Security", "Monitor"]
        scope:
          description: Scope of the privilege.
          type: str
          sample: "system"
    role_names:
      description: Roles assigned to the user.
      type: list
      elements: str
      sample: ["Security", "Monitor"]
    user_groups:
      description: User groups the user belongs to.
      type: list
      elements: dict
      contains:
        user_group_id:
          description: Identifier of the user group.
          type: str
          sample: "SecurityAdministrators"
        user_group_object_id:
          description: Object ID of the user group.
          type: str
          sample: "SecurityAdministrators"
    user_id:
      description: Unique ID of the user.
      type: str
      sample: "radey1"
    user_object_id:
      description: Object ID of the user.
      type: str
      sample: "radey1"
    vps_id:
      description: ID of the VPS or system the user belongs to.
      type: str
      sample: "(system)"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBUsersArguments,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_users_reconciler import (
    SDSBUsersReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class SDSBBlockFaultDomainFactsManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = SDSBUsersArguments().users()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()
        self.spec = parameter_manager.get_users_spec()
        self.state = parameter_manager.get_state()

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB User Operation ===")
        users = None
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_reconciler = SDSBUsersReconciler(self.connection_info)
            users = sdsb_reconciler.reconcile_user(self.spec, self.state)

            self.logger.writeDebug(f"MOD:hv_sds_users_facts:users= {users}")

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB User Operation ===")
            self.module.fail_json(msg=str(e))

        msg = None
        data = {"users": users}
        if self.state == "present":
            msg = "User created successfully."
        elif self.state == "update":
            msg = "User password updated successfully."
        data["msg"] = msg
        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo("=== End of SDSB User Operation ===")
        self.module.exit_json(**data)


def main():
    obj_store = SDSBBlockFaultDomainFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
