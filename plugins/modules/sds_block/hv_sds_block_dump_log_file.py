#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_sds_block_dump_log_file
short_description: Dumps log information from SDS Block storage system.
description:
    - Retrieve and dump log information from SDS Block storage system
    - For examples, go to URL
        U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/sdsb_dump_log_file.yml)
version_added: "4.6.0"
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
        description: The desired state of the storage pool.
        type: str
        required: false
        choices: ["present", "absent", "download"]
        default: "present"
    spec:
        description: Specification for dumping log information.
        type: dict
        required: true
        suboptions:
            label:
                description: The label of the log file.
                type: str
                required: false
            mode:
                description: The mode of the log file, options are "Base", "Memory","Monitor" and "All" , case insensitive.
                type: str
                required: false
            split_files_index:
                description: The index of the split file.
                type: int
                required: false
            file_name:
                description: The name of the log file.
                type: str
                required: false
            file_path:
                description: The path where the log file will be saved.
                type: str
                required: false
"""

EXAMPLES = """
- name: Dump log information with a specific label
  hitachivantara.vspone_block.hv_sds_block_dump_log_file:
    connection_info:
      address: 10.10.10.10
      username: admin
      password: password
    spec:
      label: "log_label_001"

- name: Download a log file with specific configuration
  hitachivantara.vspone_block.hv_sds_block_dump_log_file:
    connection_info:
      address: 10.10.10.10
      username: admin
      password: password
    state: download
    spec:
      file_path: "/tmp/"
      file_name: "sds_log_dump.tgz"
      split_files_index: 1
"""

RETURN = r"""
message:
    description: Log message content.
    type: str
    returned: always
    sample: "Dump file generated successfully"
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    DumpLogModuleArgs,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_dump_log_reconciler import (
    SDSBDumpLogReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class SDSBDumpLogManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = DumpLogModuleArgs().dump_log()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )
        try:
            parameter_manager = SDSBParametersManager(self.module.params)
            self.connection_info = parameter_manager.get_connection_info()
            self.state = parameter_manager.get_state()
            self.spec = parameter_manager.get_dump_file_spec()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))
        self.logger.writeDebug(f"MOD:hv_sds_block_dump_log:spec= {self.spec}")

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB Dump Log ===")
        status = None
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_reconciler = SDSBDumpLogReconciler(self.connection_info)
            status = sdsb_reconciler.dump_log_reconcile(self.spec, self.state)

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB Dump Log ===")
            self.module.fail_json(msg=str(e))

        data = {"message": status, "changed": self.connection_info.changed}
        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo("=== End of SDSB Dump Log ===")
        self.module.exit_json(**data)


def main():
    obj_store = SDSBDumpLogManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
