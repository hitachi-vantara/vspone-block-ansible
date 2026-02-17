#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_sds_block_license
short_description: Manage licenses on SDS Block storage system
description:
  - Create a license by registering a key code on SDS Block storage system.
  - Delete a license from SDS Block storage system.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/sdsb_license.yml)
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
  state:
    description:
      - The desired state of the license.
      - Use 'present' to create/register a new license.
      - Use 'absent' to delete a license.
    required: false
    type: str
    choices: ['present', 'absent']
    default: 'present'
  spec:
    description:
      - Specification for the license to manage.
    required: true
    type: dict
    suboptions:
      key_code:
        description:
          - The license key code to register.
          - Required when state is 'present'.
        required: false
        type: str
      id:
        description:
          - The unique identifier of the license to delete.
          - Required when state is 'absent'.
        required: false
        type: str
"""

EXAMPLES = """
- name: Create a license by registering a key code
  hitachivantara.vspone_block.sds_block.hv_sds_block_license:
    state: present
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      key_code: "1LGB7VTDBH0J7QAQ3EEQM3O1VZLYBO1ER4HU7KXAN0DQ3GT6JW9NZCP1FS5IVAQ4BPF7DOO53TN"

- name: Delete a license by ID
  hitachivantara.vspone_block.sds_block.hv_sds_block_license:
    state: absent
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      id: "222c8201-805f-453d-99ac-0b21b8a66bd6"
"""

RETURN = r"""
changed:
  description: Whether the license was created or deleted
  returned: always
  type: bool
  sample: true
license_id:
  description: The ID of the created or deleted license
  returned: always
  type: str
  sample: "222c8201-805f-453d-99ac-0b21b8a66bd6"
license:
  description: The created license details
  returned: when state is present and license is created
  type: dict
  sample:
    id: "222c8201-805f-453d-99ac-0b21b8a66bd6"
    programProductName: "Data At Rest Encryption"
    status: "Active"
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


class SDSBLicenseManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = SDSBLicenseSettingArguments().license()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()
        self.state = parameter_manager.get_state()

        # Get license parameters from spec
        spec = self.module.params.get("spec", {})
        self.license_id = spec.get("id")
        self.key_code = spec.get("key_code")

        self.logger.writeDebug(f"MOD:license:state= {self.state}")
        self.logger.writeDebug(f"MOD:license:spec= {spec}")
        self.logger.writeDebug(f"MOD:license:license_id= {self.license_id}")
        if self.key_code:
            self.logger.writeDebug(f"MOD:license:key_code= {self.key_code[:20]}...")

        # Validate parameters based on state
        if self.state == "present" and not self.key_code:
            self.module.fail_json(msg="key_code is required when state is 'present'")
        if self.state == "absent" and not self.license_id:
            self.module.fail_json(msg="id is required when state is 'absent'")

        # Validate key_code format if provided
        if self.state == "present" and self.key_code:
            self._validate_key_code(self.key_code)

    def _validate_key_code(self, key_code):
        """
        Validate the license key code format.
        Must be between 1 and 75 uppercase alphanumeric characters.
        """
        import re

        # Check length
        if not (1 <= len(key_code) <= 75):
            self.module.fail_json(
                msg=f"key_code must be between 1 and 75 characters. Got: {len(key_code)} characters"
            )

        # Check if it contains only uppercase alphanumeric characters
        if not re.match(r"^[A-Z0-9]+$", key_code):
            self.module.fail_json(
                msg="key_code must contain only uppercase alphanumeric characters (A-Z, 0-9)"
            )

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB License Management ===")
        registration_message = validate_ansible_product_registration()

        if self.module.check_mode:
            self.logger.writeInfo("=== Check mode: no changes will be made ===")
            if self.state == "present":
                result = {
                    "changed": True,
                    "message": "Check mode: License would be created",
                }
            else:
                result = {
                    "changed": True,
                    "license_id": self.license_id,
                    "message": "Check mode: License would be deleted",
                }
            if registration_message:
                result["user_consent_required"] = registration_message
            self.module.exit_json(**result)

        changed = False
        result_data = {}

        try:
            sdsb_reconciler = SDSBLicenseReconciler(self.connection_info)

            if self.state == "present":
                # Create a new license
                self.logger.writeInfo("Creating license with key code")
                create_result = sdsb_reconciler.create_license(self.key_code)
                self.logger.writeDebug(
                    f"MOD:hv_sds_block_license:create_result= {create_result}"
                )

                changed = True
                result_data = {
                    "changed": True,
                    "message": "License created successfully",
                    "license": create_result,
                }
                if create_result and isinstance(create_result, dict):
                    if "id" in create_result:
                        result_data["license_id"] = create_result["id"]

            elif self.state == "absent":
                # Verify license exists before attempting to delete
                existing_license = sdsb_reconciler.get_license(self.license_id)

                if existing_license is None:
                    self.logger.writeInfo(f"License {self.license_id} not found")
                    result_data = {
                        "changed": False,
                        "license_id": self.license_id,
                        "message": "License not found - no action taken",
                    }
                else:
                    # Delete the license
                    self.logger.writeInfo(f"Deleting license: {self.license_id}")
                    delete_result = sdsb_reconciler.delete_license(self.license_id)
                    self.logger.writeDebug(
                        f"MOD:hv_sds_block_license:delete_result= {delete_result}"
                    )

                    changed = True
                    result_data = {
                        "changed": True,
                        "license_id": self.license_id,
                        "message": "License deleted successfully",
                    }

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB License Management ===")
            self.module.fail_json(msg=str(e))

        if registration_message:
            result_data["user_consent_required"] = registration_message

        self.logger.writeInfo("=== End of SDSB License Management ===")
        self.module.exit_json(**result_data)


def main():
    obj_store = SDSBLicenseManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
