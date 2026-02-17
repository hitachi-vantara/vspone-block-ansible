#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_supported_host_mode_facts
short_description: Retrieves supported host mode options information from a specified VSP block storage system.
description:
    - This module fetches detailed information about supported host mode options available in a given VSP block storage system.
    - For examples, go to URL
        U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/supported_host_mode_facts.yml)
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
- hitachivantara.vspone_block.common.connection_with_type
"""

EXAMPLES = """
- name: Get all host groups
  hitachivantara.vspone_block.vsp.hv_supported_host_mode_facts:
    connection_info:
      address: storage1.company.com
      username: "dummy_user"
      password: "dummy_password"
"""

RETURN = """
ansible_facts:
    description: The collected supported host mode facts.
    returned: always
    type: dict
    contains:
        host_modes:
            description: Information about supported host modes and options.
            returned: always
            type: dict
            contains:
                host_mode_options:
                    description: List of supported host mode options.
                    returned: always
                    type: list
                    elements: dict
                    contains:
                        host_mode_option_description:
                            description: Description of the host mode option.
                            type: str
                            sample: "VERITAS Database Edition/Advanced Cluster"
                        host_mode_option_id:
                            description: ID of the host mode option.
                            type: int
                            sample: 2
                        required_host_modes:
                            description: List of required host modes for this option.
                            type: list
                            elements: str
                            sample: []
                        scope:
                            description: Scope of the host mode option.
                            type: str
                            sample: ""
                host_modes:
                    description: List of supported host modes.
                    returned: always
                    type: list
                    elements: dict
                    contains:
                        host_mode_display:
                            description: Display name of the host mode.
                            type: str
                            sample: "LINUX/IRIX"
                        host_mode_id:
                            description: ID of the host mode.
                            type: int
                            sample: 0
                        host_mode_name:
                            description: Name of the host mode.
                            type: str
                            sample: "Standard"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPHostGroupArguments,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_host_group,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class VSPHostGroupHostModeFactsManager:
    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPHostGroupArguments().get_host_mode_options()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        try:
            self.params = VSPParametersManager(self.module.params)
            self.serial_number = self.params.storage_system_info.serial
            self.connection_info = self.params.get_connection_info()

        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Host Mode Facts ===")
        registration_message = validate_ansible_product_registration()

        try:
            response = vsp_host_group.VSPHostGroupReconciler(
                self.connection_info, self.serial_number
            ).host_group_host_mode_options_reconcile()

            result = {"host_modes": response}

        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of Host Mode Facts ===")
            self.module.fail_json(msg=str(e))
        if registration_message:
            result["user_consent_required"] = registration_message
        self.logger.writeInfo(f"{result}")
        self.logger.writeInfo("=== End of Host Mode Facts ===")
        self.module.exit_json(changed=False, ansible_facts=result)


def main():
    obj_store = VSPHostGroupHostModeFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
