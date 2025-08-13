#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_sds_block_protection_domain_facts
short_description: Get protection domains  from storage system
description:
  - Get protection domains from storage system.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/sdsb_protection_domains_facts.yml)
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
"""

EXAMPLES = """
- name: Retrieve information about Protection Domains
  hitachivantara.vspone_block.sds_block.hv_sds_block_protection_domain_facts:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
"""

RETURN = r"""
ansible_facts:
  description: >
    Dictionary containing the discovered properties of the parity domains.
  returned: always
  type: dict
  contains:
    data:
      description: List of parity domain entries.
      type: list
      elements: dict
      contains:
        id:
          description: Unique identifier for the parity domain.
          type: str
          sample: "0778a123-42e5-43ff-8fbc-c8580b79f2cf"
        name:
          description: Name of the parity domain.
          type: str
          sample: "SC01-PD01"
        redundantPolicy:
          description: Redundancy policy used by the parity domain.
          type: str
          sample: "HitachiPolyphaseErasureCoding"
        redundantType:
          description: Redundancy type used in the parity domain (e.g., 4D+1P).
          type: str
          sample: "4D+1P"
        driveDataRelocationStatus:
          description: Current status of drive data relocation.
          type: str
          sample: "Stopped"
        driveDataRelocationProgressRate:
          description: Progress percentage of data relocation. Null if not active.
          type: int
          sample: null
        rebuildStatus:
          description: Current rebuild status.
          type: str
          sample: "Stopped"
        rebuildProgressRate:
          description: Rebuild progress rate as a percentage. Null if not rebuilding.
          type: int
          sample: null
        memoryMode:
          description: Memory mode used in the parity domain.
          type: str
          sample: "VolatileMemory"
        asyncProcessingResourceUsageRate:
          description: Usage level of asynchronous processing resources.
          type: str
          sample: "High"
        numberOfFaultSets:
          description: Number of fault sets in the parity domain.
          type: int
          sample: 1
        storageControllerClusteringPolicy:
          description: Clustering policy of the storage controllers.
          type: str
          sample: "OneRedundantStorageNode"
        minimumMemorySize:
          description: Minimum memory size in MB.
          type: int
          sample: 131072
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBParametersManager,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_cluster_information_reconciler import (
    SDSBClusterInformationReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class SDSBBlockBlockDomainsFactsManager:
    def __init__(self):
        self.logger = Log()
        argument_spec = {
            "connection_info": {
                "required": True,
                "type": "dict",
                "options": {
                    "address": {"required": True, "type": "str"},
                    "username": {"required": True, "type": "str"},
                    "password": {"required": True, "type": "str", "no_log": True},
                    "connection_type": {
                        "required": False,
                        "type": "str",
                        "choices": ["direct"],
                        "default": "direct",
                    },
                },
            }
        }

        self.module = AnsibleModule(
            argument_spec=argument_spec,
            supports_check_mode=True,
        )

        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB Protection Domain Facts ===")
        settings = None
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_reconciler = SDSBClusterInformationReconciler(self.connection_info)
            settings = sdsb_reconciler.get_protection_domain_settings()

            self.logger.writeDebug(
                f"MOD:get_protection_domain_settings:get_protection_domain_settings= {settings}"
            )

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB Protection Domain Facts ===")
            self.module.fail_json(msg=str(e))

        data = {"protection_domains": settings}
        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo("=== End of SDSB Protection Domain Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)


def main():
    obj_store = SDSBBlockBlockDomainsFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
