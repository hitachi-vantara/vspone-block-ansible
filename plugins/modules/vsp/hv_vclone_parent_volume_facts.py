#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_vclone_parent_volume_facts
short_description: Retrieves virtual clone parent volume information from VSP block storage systems.
description:
  - This module retrieves information about virtual clone parent volume from VSP block storage systems.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/vclone_parent_volume_facts.yml)
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
- hitachivantara.vspone_block.common.gateway_note
- hitachivantara.vspone_block.common.connection_with_type
options:
  spec:
    description: Specification for the virtual clone parent volume facts to be gathered.
    type: dict
    required: false
    suboptions:
      vclone_volume_id:
        description: The ID of the virtual clone volume.
        type: str
        required: false
"""

EXAMPLES = """
- name: Gather virtual clone parent volume facts
  hitachivantara.vspone_block.vsp.hv_vclone_parent_volume_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    spec:
      vclone_volume_id: '12345'
"""


RETURN = r"""
ansible_facts:
  description:
    - Dictionary containing facts gathered by the module.
  returned: always
  type: dict
  contains:
    parent_volume_ids:
      description:
        - List of parent volume identifiers.
      returned: always
      type: list
      elements: dict
      contains:
        ldev_id:
          description:
            - Logical device (LDEV) identifier of the parent volume.
          type: int
          sample: 104
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPVcloneParentVolumeArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_vclone import (
    VSPVcloneReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log_decorator import (
    LogDecorator,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


@LogDecorator.debug_methods
class VSPVcloneParentVolumeFactManager:

    def __init__(self):
        self.logger = Log()
        self.argument_spec = (
            VSPVcloneParentVolumeArguments().get_vclone_parent_volume_fact()
        )
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:

            self.params_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.params_manager.connection_info
            self.storage_serial_number = None
            self.spec = self.params_manager.get_vclone_parent_volume_fact_spec()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Vclone Parent Volume Facts ===")
        vclone_parent_volume_data = None
        registration_message = validate_ansible_product_registration()

        try:
            vclone_parent_volume_data = VSPVcloneReconciler(
                self.connection_info, self.storage_serial_number
            ).get_vclone_parent_volume_facts(self.spec)

        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of Vclone Parent Volume Facts ===")
            self.module.fail_json(msg=str(e))
        data = {
            "parent_volume_ids": vclone_parent_volume_data,
        }
        if registration_message:
            data["user_consent_required"] = registration_message

        self.logger.writeInfo(f"{data}")
        self.logger.writeInfo("=== End of Vclone Parent Volume Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)


def main(module=None):
    """Main function to execute the module."""
    obj_store = VSPVcloneParentVolumeFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
