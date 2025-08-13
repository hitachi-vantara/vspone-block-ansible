#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_sds_block_fault_domain_facts
short_description: Get fault domains from storage system
description:
  - Get fault domains from storage system.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/sdsb_fault_domain_facts.yml)
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
    description: Specification for retrieving CHAP user information.
    type: dict
    required: false
    suboptions:
      id:
        description: Filter fault domains by ID (UUID format).
        type: str
      name:
        description: Filter fault domains by name.
        type: str
"""

EXAMPLES = """
- name: Retrieve information about all fault_domain
  hitachivantara.vspone_block.sds_block.hv_sds_fault_domain_facts:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"

- name: Retrieve information about fault_domain by specifying id
  hitachivantara.vspone_block.sds_block.hv_sds_fault_domain_facts:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      id: "126f360e-c79e-4e75-8f7c-7d91bfd2f0b8"

- name: Retrieve information about fault_domain by specifying name
  hitachivantara.vspone_block.sds_block.hv_sds_fault_domain_facts:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      name: "SC01-PD01-FD01"
"""

RETURN = r"""
ansible_facts:
  description: >
    Dictionary containing the discovered properties of the fault_domain.
  returned: always
  type: dict
  contains:
    data:
      description: List of fault domain entries.
      type: list
      elements: dict
      contains:
        id:
          description: Unique identifier for the fault domain.
          type: str
          sample: "355d32ce-c97f-4adf-9057-49d2e287974b"
        name:
          description: Name of the fault domain.
          type: str
          sample: "SC01-PD01-FD01"
        statusSummary:
          description: Summary of the fault domain's status.
          type: str
          sample: "Normal"
        status:
          description: Current operational status of the fault domain.
          type: str
          sample: "Normal"
        numberOfStorageNodes:
          description: Number of storage nodes in the fault domain.
          type: int
          sample: 3
        availabilityZoneId:
          description: UUID of the availability zone associated with the fault domain, if any.
          type: str
          sample: null
        totalCapacity:
          description: Total physical capacity of the fault domain in GB.
          type: int
          sample: 0
        usedCapacity:
          description: Used physical capacity of the fault domain in GB.
          type: int
          sample: 0
        freeCapacity:
          description: Free physical capacity of the fault domain in GB.
          type: int
          sample: 0
        usedCapacityRate:
          description: Percentage of used capacity in the fault domain.
          type: int
          sample: 0
        totalVolumeCapacity:
          description: Total logical volume capacity in the fault domain.
          type: int
          sample: 0
        provisionedVolumeCapacity:
          description: Total provisioned volume capacity.
          type: int
          sample: 0
        otherVolumeCapacity:
          description: Capacity used by volumes not categorized elsewhere.
          type: int
          sample: 0
        temporaryVolumeCapacity:
          description: Capacity used by temporary volumes.
          type: int
          sample: 0
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBFaultDomainArguments,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_fault_domain_reconciler import (
    SDSBFaultDomainReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class SDSBBlockFaultDomainFactsManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = SDSBFaultDomainArguments().fault_domain_facts()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()
        self.spec = parameter_manager.get_fault_domain_fact_spec()
        self.logger.writeDebug(f"MOD:hv_sds_fault_domain_facts:spec= {self.spec}")

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB Fault Domain Facts ===")
        fault_domain = None
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_reconciler = SDSBFaultDomainReconciler(self.connection_info)
            fault_domain = sdsb_reconciler.get_fault_domains(self.spec)

            self.logger.writeDebug(
                f"MOD:hv_sds_fault_domain_facts:fault_domain= {fault_domain}"
            )

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB Fault Domain Facts ===")
            self.module.fail_json(msg=str(e))

        data = {"fault_domain": fault_domain}
        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo("=== Start of SDSB Fault Domain Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)


def main():
    obj_store = SDSBBlockFaultDomainFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
