#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_sds_block_dump_log_status_facts
short_description: Dumps log status information from SDS Block storage system.
description:
    - Retrieve and dump log status information from SDS Block storage system
    - For examples, go to URL
        U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/sdsb_dump_log_file_status_facts.yml)
version_added: "4.6.0"
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
        description: Specification for dumping log status information.
        type: dict
        required: False
        suboptions:
            include_all_status:
                description: Get all dump log status information including completed, in-progress, and failed.
                type: bool
                required: False
"""

EXAMPLES = """
- name: Dump log status facts
  hitachivantara.vspone_block.sds_block.hv_sds_block_dump_log_status_facts:
    connection_info:
        address: sdsb.company.com
        username: "admin"
        password: "password"
    spec:
        include_all_status: true
"""

RETURN = r"""
ansible_facts:
    description: >
        Dictionary containing the dumped log status information.
    returned: always
    type: dict
    contains:
        dump_status:
            description: List of dump log status information.
            returned: always
            type: list
            elements: dict
            contains:
                started_time:
                    description: The time when the dump log started.
                    type: str
                completed_time:
                    description: The time when the dump log completed.
                    type: str
                label:
                    description: Label of the dump log.
                    type: str
                status:
                    description: Status of the dump log.
                    type: str
                size:
                    description: Size of the dump log file.
                    type: int
                trigger_type:
                    description: Trigger type of the dump log.
                    type: str
                mode:
                    description: Mode of the dump log.
                    type: str
                file_name:
                    description: Name of the dump log file.
                    type: str
                number_of_split_files:
                    description: Number of split files.
                    type: int
                error:
                    description: Error information if the dump log failed.
                    type: dict
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


class SDSBDumpLogStatusFactsManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = DumpLogModuleArgs().dump_log_status_facts()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()
        self.spec = parameter_manager.get_dump_file_status_spec()
        self.logger.writeDebug(
            f"MOD:hv_sds_block_dump_log_status_facts:spec= {self.spec}"
        )

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB Dump Log Status Facts ===")
        status = None
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_reconciler = SDSBDumpLogReconciler(self.connection_info)
            status = sdsb_reconciler.dump_log_status_facts_reconcile(self.spec)

            self.logger.writeDebug(
                f"MOD:hv_sds_block_dump_log_status_facts:status= {status}"
            )
        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB Dump Log Status Facts ===")
            self.module.fail_json(msg=str(e))

        data = {"dump_status": status}
        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo("=== End of SDSB Dump Log Status Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)


def main():
    obj_store = SDSBDumpLogStatusFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
