#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_pav_alias_facts
short_description: retrieves information about PAV aliases from VSP block storage systems.
description:
    - This module gathers facts about PAV aliases from VSP block storage systems.
    - For examples, go to URL
        U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/pav_alias_facts.yml)
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
    - hitachivantara.vspone_block.common.connection_info
options:
    spec:
        description: Specification for the PAV alias facts to be gathered.
        type: dict
        required: false
        suboptions:
            cu_number:
                description: The CU (Control Unit) number to retrieve PAV aliases for.
                    Required for getting PAV aliases for a specific control unit.
                type: int
                required: false
            base_ldev_id:
                description: The base LDEV ID to retrieve PAV aliases for.
                    Required for getting PAV aliases for a specific base LDEV.
                type: int
                required: false
            alias_ldev_id:
                description: The PAV LDEV ID to retrieve information for.
                    Required for getting information about a specific PAV LDEV.
                type: int
                required: false
"""

EXAMPLES = """
- name: Get PAV aliases for a specific control unit
  hitachivantara.vspone_block.hv_pav_alias_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    spec:
      cu_number: "0"

- name: Get all PAV aliases
  hitachivantara.vspone_block.hv_pav_alias_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
"""

RETURN = """
ansible_facts:
    description: >
        Dictionary containing the discovered properties of the PAV aliases.
    returned: always
    type: dict
    contains:
        pav_aliases:
            description: List of PAV aliases with their attributes.
            type: list
            elements: dict
            contains:
                cu_number:
                    description: Control Unit number.
                    type: int
                    sample: 0
                ldev_id:
                    description: Logical Device ID.
                    type: int
                    sample: 102
                pav_attribute:
                    description: PAV attribute type.
                    type: str
                    sample: "ALIAS"
                c_base_volume_id:
                    description: Base volume ID for command device.
                    type: int
                    sample: 100
                s_base_volume_id:
                    description: Base volume ID for secondary device.
                    type: int
                    sample: 100
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


class VspPavAliasFactManager:
    def __init__(self):
        # VSPStoragePoolArguments
        self.logger = Log()
        self.argument_spec = VSPPavLdevArguments().get_vsp_pav_ldev_facts_args()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.get_vsp_pav_facts_spec()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Pav Alias Facts ===")
        registration_message = validate_ansible_product_registration()
        try:
            pav_reconciler = vsp_pav_reconciler.VspPavReconciler(
                self.params_manager.get_connection_info()
            )
            pav_facts = pav_reconciler.vsp_pav_facts_reconciler(self.spec)

            ansible_facts = {"pav_aliases": pav_facts}

            if registration_message:
                ansible_facts["registration_message"] = registration_message

            self.logger.writeInfo("=== End of Pav Alias Facts ===")
            self.module.exit_json(changed=False, ansible_facts=ansible_facts)

        except Exception as ex:
            if "No resource exists at the specified URL" in str(ex):
                ex = Exception(
                    "This feature is not supported on this storage system."
                    " Please check if PAV alias functionality is available on your storage model."
                )
            self.logger.writeException(ex)
            self.logger.writeInfo("=== End of Pav Alias Facts ===")
            self.module.fail_json(msg=str(ex))


def main():
    obj_store = VspPavAliasFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
