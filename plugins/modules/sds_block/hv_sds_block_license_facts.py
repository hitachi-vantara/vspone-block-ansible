#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_sds_block_license_facts
short_description: Get license(s) from SDS Block storage system
description:
  - Get all licenses from SDS Block storage system.
  - Get a specific license by ID from SDS Block storage system.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/sdsb_license_facts.yml)
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
options:
  spec:
    description:
      - Specification for the license(s) to retrieve.
      - If spec.id is provided, retrieves a single license by ID.
      - If spec is not provided or spec.id is empty, retrieves all licenses.
    required: false
    type: dict
    suboptions:
      id:
        description:
          - The unique identifier of the license to retrieve.
          - If not provided, all licenses will be retrieved.
        required: false
        type: str
      program_product_name:
        description: The name of the program product.
        required: false
        type: str
      status:
        description: Status of the license. Case-insensitive. Valid values is 'Active', 'Warning', 'Overwritten', 'GracePeriod', 'Invalid'.
        required: false
        type: str
      status_summary:
        description: License status summary.
        required: false
        type: str
        choices: ['Normal', 'Warning', 'Error']
"""

EXAMPLES = """
- name: Retrieve all licenses
  hitachivantara.vspone_block.sds_block.hv_sds_block_license_facts:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"

- name: Retrieve specific license by ID
  hitachivantara.vspone_block.sds_block.hv_sds_block_license_facts:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      id: "4a7061b0-8cc0-4379-aec1-23184d26acd7"
"""

RETURN = r"""
ansible_facts:
  description: >
    Dictionary containing the discovered license(s).
    Returns 'license' (single object) if spec.id is provided.
    Returns 'licenses' (dict with data array) if spec.id is not provided.
  returned: always
  type: dict
  contains:
    license:
      description: Single license object if spec.id is provided. None if not found.
      type: dict
      returned: when spec.id is provided
    licenses:
      description: Dictionary containing all licenses if spec.id is not provided.
      type: dict
      returned: when spec.id is not provided
      contains:
        data:
          description: List of license objects.
          type: list
          elements: dict
          contains:
            id:
              description: License ID.
              type: str
              sample: "4a7061b0-8cc0-4379-aec1-23184d26acd7"
            program_product_name:
              description: Name of the licensed program product.
              type: str
              sample: "Data At Rest Encryption"
            status:
              description: License status.
              type: str
              sample: "Active"
            status_summary:
              description: Summary of license status.
              type: str
              sample: "Normal"
            key_type:
              description: Type of license key.
              type: str
              sample: "Perpetual"
            permitted_capacity_in_tib:
              description: Permitted capacity in TiB. Returns -1.0 if not set.
              type: float
              sample: -1.0
            total_pool_capacity_in_gib:
              description: Total pool capacity in GiB. Returns -1.0 if not set.
              type: float
              sample: -1.0
            remaining_days:
              description: Remaining days until license expiration. Returns -1 if not applicable (perpetual license).
              type: int
              sample: -1
            checked_out_license_usage_in_tib:
              description: Checked out license usage in TiB. Returns -1.0 if not set.
              type: float
              sample: -1.0
            capacity_rate:
              description: Capacity usage rate. Returns -1 if not set.
              type: int
              sample: -1
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


class SDSBLicensesFactsManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = SDSBLicenseSettingArguments().license_facts()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()
        self.spec = parameter_manager.get_license_facts_spec()

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB Licenses Facts ===")
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_reconciler = SDSBLicenseReconciler(self.connection_info)
            licenses = sdsb_reconciler.get_license_facts(self.spec)
        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB Licenses Facts ===")
            self.module.fail_json(msg=str(e))

        data = {"licenses": licenses}
        if registration_message:
            data["user_consent_required"] = registration_message

        self.logger.writeInfo("=== End of SDSB Licenses Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)


def main():
    obj_store = SDSBLicensesFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
