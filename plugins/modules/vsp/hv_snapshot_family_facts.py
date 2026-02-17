#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_snapshot_family_facts
short_description: Retrieves snapshot family information of the provided LDEV ID from VSP block storage systems.
description:
  - This module retrieves information about snapshot family of the provided LDEV IDfrom VSP block storage systems.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/snapshot_family_facts.yml)
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
    description: Specification for the snapshot family facts to be gathered.
    type: dict
    required: true
    suboptions:
      ldev_id:
        description: The ID of the logical device (LDEV).
        type: str
        required: true
"""

EXAMPLES = """
- name: Gather snapshot family facts
  hitachivantara.vspone_block.vsp.hv_snapshot_family_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "secret"
    spec:
      ldev_id: '12345'
"""


RETURN = r"""
ansible_facts:
  description:
    - Dictionary containing facts gathered by the module.
  returned: always
  type: dict
  contains:
    snapshots:
      description:
        - List of snapshot and virtual clone volume details.
      returned: always
      type: list
      elements: dict
      contains:
        ldev_id:
          description:
            - Logical device (LDEV) identifier of the snapshot or clone volume.
          type: int
          sample: 104
        parent_ldev_id:
          description:
            - LDEV identifier of the parent volume.
          type: int
          sample: 104
        is_virtual_clone_volume:
          description:
            - Indicates whether the volume is a virtual clone.
          type: bool
          sample: true
        is_virtual_clone_parent_volume:
          description:
            - Indicates whether the volume is a parent of a virtual clone.
          type: bool
          sample: true
        mu_number:
          description:
            - Mirror Unit (MU) number associated with the snapshot.
          type: int
          sample: 3
        pool_id:
          description:
            - Pool identifier where the snapshot or clone resides.
          type: int
          sample: 22
        primary_or_secondary:
          description:
            - Indicates whether the volume is a primary or secondary volume.
          type: str
          sample: P-VOL
        pvol_ldev_id:
          description:
            - LDEV identifier of the primary volume.
          type: int
          sample: 104
        snapshot_group_id:
          description:
            - Identifier of the snapshot group.
          type: str
          sample: test_sp_group
        snapshot_group_name:
          description:
            - Name of the snapshot group.
          type: str
          sample: test_sp_group
        snapshot_id:
          description:
            - Unique identifier of the snapshot, typically in the format LDEV,MU.
          type: str
          sample: "104,3"
        split_time:
          description:
            - Timestamp when the snapshot was split from the parent volume.
          type: str
          sample: "2025-08-28T18:12:39"
        status:
          description:
            - Current status of the snapshot or clone.
          type: str
          sample: PFUS
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPSnapshotFamilyArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_snapshot_family import (
    VSPSnapshotFamilyReconciler,
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
class VSPSnapshotFamilyFactManager:

    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPSnapshotFamilyArguments().get_snapshot_family_fact()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.params_manager.connection_info
            self.storage_serial_number = None
            self.spec = self.params_manager.get_snapshot_family_fact_spec()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Snapshot Family Facts ===")
        snapshot_family_data = None
        registration_message = validate_ansible_product_registration()

        try:
            snapshot_family_data = VSPSnapshotFamilyReconciler(
                self.connection_info, self.storage_serial_number
            ).get_snapshot_family_facts(self.spec)

        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of Snapshot Family Facts ===")
            self.module.fail_json(msg=str(e))
        data = {
            "snapshots": snapshot_family_data,
        }
        if registration_message:
            data["user_consent_required"] = registration_message

        self.logger.writeInfo(f"{data}")
        self.logger.writeInfo("=== End of Snapshot Family Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)


def main(module=None):
    """Main function to execute the module."""
    obj_store = VSPSnapshotFamilyFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
