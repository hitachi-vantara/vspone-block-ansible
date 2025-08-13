#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_sds_block_user_facts
short_description: Get users from storage system
description:
  - Get users from storage system.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/sdsb_user_facts.yml)
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
  spec:
    description: Specification for the storage node to be added to or removed from the cluster.
    type: dict
    required: false
    suboptions:
      id:
        description: Filter userss by ID (UUID format).
        type: str
"""

EXAMPLES = """
- name: Retrieve information about all users
  hitachivantara.vspone_block.sds_block.hv_sds_block_user_facts:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"

- name: Retrieve information about user by specifying id
  hitachivantara.vspone_block.sds_block.hv_sds_block_user_facts:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      id: "1"
"""

RETURN = r"""
ansible_facts:
  description: >
    Dictionary containing user account information discovered from the system.
  returned: always
  type: dict
  contains:
    data:
      description: List of user account entries.
      type: list
      elements: dict
      contains:
        userId:
          description: Username of the account.
          type: str
          sample: "admin"
        userObjectId:
          description: Unique object identifier for the user.
          type: str
          sample: "admin"
        passwordExpirationTime:
          description: Timestamp indicating when the password will expire.
          type: str
          sample: "2022-11-30T07:21:21Z"
        isEnabled:
          description: Indicates if the user account is enabled.
          type: bool
          sample: true
        userGroups:
          description: List of groups the user belongs to.
          type: list
          elements: dict
          contains:
            userGroupId:
              description: ID of the user group.
              type: str
              sample: "SystemAdministrators"
            userGroupObjectId:
              description: Object ID of the user group.
              type: str
              sample: "SystemAdministrators"
        isBuiltIn:
          description: Indicates if the user is a built-in system account.
          type: bool
          sample: true
        authentication:
          description: Authentication method used by the user (e.g., local or LDAP).
          type: str
          sample: "local"
        roleNames:
          description: List of roles assigned to the user.
          type: list
          elements: str
          sample: ["Security", "Storage", "Monitor", "Service", "Audit", "Resource"]
        isEnabledConsoleLogin:
          description: Indicates whether the user can log in to the console.
          type: bool
          sample: null
        vpsId:
          description: VPS identifier associated with the user account.
          type: str
          sample: "(system)"
        privileges:
          description: List of privileges assigned to the user.
          type: list
          elements: dict
          contains:
            scope:
              description: Scope to which the privileges apply.
              type: str
              sample: "system"
            roleNames:
              description: Roles granted within the specified scope.
              type: list
              elements: str
              sample: ["Audit", "Security", "Storage", "Monitor", "Service", "Resource"]
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
        self.argument_spec = SDSBUsersArguments().user_facts()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()
        self.spec = parameter_manager.get_users_spec()
        self.logger.writeDebug(f"MOD:hv_sds_users_facts:spec= {self.spec}")

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB User Facts ===")
        users = None
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_reconciler = SDSBUsersReconciler(self.connection_info)
            users = sdsb_reconciler.get_users(self.spec)

            self.logger.writeDebug(f"MOD:hv_sds_users_facts:users= {users}")

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB User Facts ===")
            self.module.fail_json(msg=str(e))

        data = {"users": users}
        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo("=== End of SDSB User Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)


def main():
    obj_store = SDSBBlockFaultDomainFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
