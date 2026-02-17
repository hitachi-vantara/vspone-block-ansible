#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_pav_alias
short_description: Manages PAV (Parallel Access Volume) alias assignments for VSP block storage systems.
description:
    - This module manages PAV (Parallel Access Volume) alias assignments for VSP block storage systems.
    - Supports assigning alias devices to base devices and unassign them.
    - For examples, go to URL
        U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/pav_alias.yml)
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
    - hitachivantara.vspone_block.common.connection_info
options:
    state:
        description: The desired state of the PAV alias assignment.
        type: str
        choices: [present, absent]
        default: present
        required: false
    spec:
        description: Specification for the PAV alias assignment.
        type: dict
        required: true
        suboptions:
            base_ldev_id:
                description: The base LDEV ID to assign or unassign aliases.
                type: int
                required: false
            alias_ldev_ids:
                description: List of alias LDEV IDs to assign or unassign to/from the base LDEV.
                type: list
                elements: int
                required: true
"""

EXAMPLES = """
- name: Assign PAV aliases to a base LDEV
  hitachivantara.vspone_block.hv_pav_alias:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    state: present
    spec:
      base_ldev_id: 100
      alias_ldev_ids: [102, 103, 104]

- name: Unassign PAV aliases from a base LDEV
  hitachivantara.vspone_block.hv_pav_alias:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    state: absent
    spec:
      alias_ldev_ids: [102, 103]
"""

RETURN = """
changed:
    description: Whether any changes were made to the PAV alias assignments.
    type: bool
    returned: always
    sample: true
pav_aliases:
    description: List of PAV aliases after the operation.
    type: list
    elements: dict
    returned: always
    contains:
        ldev_id:
            description: Logical Device ID of the alias.
            type: int
            sample: 102
        base_ldev_id:
            description: Base LDEV ID that this alias is associated with.
            type: int
            sample: 100
        pav_attribute:
            description: PAV attribute indicating the role (BASE or ALIAS).
            type: str
            sample: "ALIAS"
        assignment_status:
            description: Current assignment status of the PAV alias.
            type: str
            sample: "assigned"
"""


from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPPavLdevArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_pav_reconciler,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class VspPavLdevFactManager:
    def __init__(self):
        # VSPStoragePoolArguments
        self.logger = Log()
        self.argument_spec = VSPPavLdevArguments().get_vsp_pav_ldev_args()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.get_vsp_pav_spec()
            self.state = self.params_manager.get_state()
            self.connect_info = self.params_manager.get_connection_info()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Pav Ldev Facts ===")
        registration_message = validate_ansible_product_registration()
        try:
            pav_reconciler = vsp_pav_reconciler.VspPavReconciler(self.connect_info)
            aliases = pav_reconciler.reconcile_pav_ldevs(self.spec, self.state)

            pav_alias = {
                "changed": self.connect_info.changed,
                "msg": self.spec.comment,
                "pav_aliases": aliases,
            }

            if registration_message:
                pav_alias["registration_message"] = registration_message

            self.logger.writeInfo("=== End of Pav Ldev Facts ===")
            self.module.exit_json(**pav_alias)

        except Exception as ex:
            if "No resource exists at the specified URL" in str(ex):
                ex = Exception(
                    "This feature is not supported on this storage system."
                    " Please check if PAV alias functionality is available on your storage model."
                )
            self.logger.writeException(ex)
            self.logger.writeInfo("=== End of Pav Ldev Facts ===")
            self.module.fail_json(msg=str(ex))


def main():
    obj_store = VspPavLdevFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
