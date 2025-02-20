#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_journal_volume_facts
short_description: Retrieves information about Journal Volumes from Hitachi VSP storage systems.
description:
  - This module retrieves information about Journal Volumes from Hitachi VSP storage systems.
  - It provides details such as journalId, journalStatus, and other relevant information.
  - This module is supported for both direct and gateway connection types.
  - For direct connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/journal_volume_facts.yml)
  - For gateway connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/journal_volume_facts.yml)
version_added: '3.2.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
options:
  storage_system_info:
    description:
      - Information about the Hitachi storage system.
    type: dict
    required: false
    suboptions:
      serial:
        description:
          - Serial number of the Hitachi storage system.
        type: str
        required: false
  connection_info:
    description: Information required to establish a connection to the storage system.
    type: dict
    required: true
    suboptions:
      address:
        description: IP address or hostname of either the UAI gateway (if connection_type is gateway) or the storage system (if connection_type is direct).
        type: str
        required: true
      username:
        description: Username for authentication. This field is valid for direct connection type only, and it is a required field.
        type: str
        required: false
      password:
        description: Password for authentication. This field is valid for direct connection type only, and it is a required field.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['gateway', 'direct']
        default: 'direct'
      subscriber_id:
        description: This field is valid for gateway connection type only. This is an optional field and only needed to support multi-tenancy environment.
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway. This is a required field for gateway connection type.
        type: str
        required: false
  spec:
    description: Specification for retrieving Journal Volume information.
    type: dict
    required: false
    suboptions:
      journal_id:
        description: Journal ID of the Journal Volume.
        type: int
        required: false
      is_free_journal_pool_id:
        description: Whether to get free journal id.
        type: bool
        required: false
        default: false
      free_journal_pool_id_count:
        description: Number of free journal id to get.
        type: int
        required: false
        default: 1
      is_mirror_not_used:
        description: Whether to get mirror not used.
        type: bool
        required: false
        default: false

"""

EXAMPLES = """
- name: Retrieve information about all Journal Volumes
  hv_journal_volume_facts:
    storage_system_info:
      serial: "811150"
    connection_info:
      address: gateway.company.com
      api_token: "api token value"
      connection_type: "gateway"
      subscriber_id: 811150
    spec:
      journal_id: 10
"""

RETURN = """
ldevs:
  description: List of Journal Volume managed by the module.
  returned: success
  type: list
  elements: dict
  sample: [
    {
      "journalId": 0,
      "muNumber": 1,
      "consistencyGroupId": 5,
      "journalStatus": "PJSF",
      "numOfActivePaths": 1,
      "usageRate": 0,
      "qMarker": "575cc653",
      "qCount": 0,
      "byteFormatCapacity": "1.88 G",
      "blockCapacity": 3956736,
      "numOfLdevs": 1,
      "firstLdevId": 513
    }
  ]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_journal_volume,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPParametersManager,
    VSPJournalVolumeArguments,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class VSPJournalVolumeFactManager:
    def __init__(self):
        self.logger = Log()

        self.argument_spec = VSPJournalVolumeArguments().journal_volume_fact()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.get_journal_volume_fact_spec()
            self.serial = self.params_manager.get_serial()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of Journal Volume Facts ===")
        registration_message = validate_ansible_product_registration()
        try:
            result = []
            result = vsp_journal_volume.VSPJournalVolumeReconciler(
                self.params_manager.connection_info, self.serial
            ).journal_volume_facts(self.spec)

        except Exception as ex:

            self.logger.writeException(ex)
            self.logger.writeInfo("=== End of Journal Volume Facts ===")
            self.module.fail_json(msg=str(ex))
        data = {
            "journal_volume": result,
        }
        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo(f"{data}")
        self.logger.writeInfo("=== End of Journal Volume Facts ===")
        self.module.exit_json(**data)


def main(module=None):
    obj_store = VSPJournalVolumeFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
