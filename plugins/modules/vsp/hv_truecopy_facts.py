
DOCUMENTATION = '''
---
module: hv_truecopy_facts
short_description: Retrieves TrueCopy pairs information from Hitachi VSP storage systems.
description:
     - This module retrieves the TrueCopy pairs information from Hitachi VSP storage systems.
version_added: '3.1.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.1.0
options:
  connection_info:
    description: Information required to establish a connection to the storage system.
    type: dict
    required: true
    suboptions:
      address:
        description: IP address or hostname of the UAI gateway.
        type: str
        required: true
      username:
        description: Username for authentication.
        type: str
        required: false
      password:
        description: Password for authentication.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: true
        choices: ['gateway']
      api_token:
        description: Token value to access UAI gateway.
        type: str
        required: false
  spec:
    description: Specification for retrieving TrueCopy pair information.
    type: dict
    required: false
    suboptions:
      primary_volume_id:
        description: ID of the primary volume to retrieve TrueCopy pair information for (Works only for gateway connection type).
        type: int
        required: false        
'''

EXAMPLES = '''
- name: Get all TrueCopy pairs
  hv_truecopy_facts:
    storage_system_info:
        serial: "ABC123"
    connection_info:
        address: gateway.company.com
        api_token: "api_token_value"
        connection_type: "gateway"
        subscriber_id: "sub123"

- name: Retrieve information TrueCopy pair information for a specific volume
  hv_truecopy_facts:
    storage_system_info:
        serial: "ABC123"
    connection_info:
        address: gateway.company.com
        api_token: "api_token_value"
        connection_type: "gateway"
        subscriber_id: "sub123"
    spec:
      primary_volume_id: 123
'''

RETURN = '''
truecopy_pairs:
  description: a list of TrueCopy pairs information.
  returned: always
  type: list
  elements: dict
  sample: [
    {
      "consistency_group_id": -1,
      "copy_rate": 100,
      "entitlement_status": "unassigned",
      "mirror_unit_id": 0,
      "pair_name": "",
      "partner_id": "apiadmin",
      "primary_hex_volume_id": "00:05:01",
      "primary_volume_id": 1281,
      "primary_volume_storage_id": 810050,
      "resource_id": "replpair-037f68f4f56351b2de6a68ff5dc0cdeb",
      "secondary_hex_volume_id": "00:00:82",
      "secondary_volume_id": 130,
      "secondary_volume_storage_id": 810045,
      "status": "PSUS",
      "storage_id": "storage-b2c93d5e8fadb70b208341b0e19c6527",
      "storage_serial_number": "810050",
      "svol_access_mode": "READWRITE",
      "type": "truecopypair"
    }
  ]
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_true_copy import (
    VSPTrueCopyReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_properties_extractor import (
    ChapUserPropertiesExtractor,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPTrueCopyArguments,
    VSPParametersManager,
)

logger = Log()


class VSPTrueCopyFactsManager:
    def __init__(self):

        self.argument_spec = VSPTrueCopyArguments().true_copy_facts()
        logger.writeDebug(
            f"MOD:hv_truecopy_facts:argument_spec= {self.argument_spec}"
        )
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )

        self.parameter_manager = VSPParametersManager(self.module.params)
        self.connection_info = self.parameter_manager.get_connection_info()
        self.storage_serial_number = self.parameter_manager.storage_system_info.serial
        self.spec = self.parameter_manager.get_true_copy_fact_spec()
        self.state = self.parameter_manager.get_state()
        logger.writeDebug(f"MOD:hv_truecopy_facts:spec= {self.spec}")

    def apply(self):

        logger.writeInfo(f"{self.connection_info.connection_type} connection type")
        try:
            reconciler = VSPTrueCopyReconciler(
                self.connection_info,
                self.storage_serial_number,
                self.state
            )
            tc_pairs = reconciler.get_true_copy_facts(self.spec)

            logger.writeDebug(
                f"MOD:hv_truecopy_facts:tc_pairs= {tc_pairs}"
            )
            # output_dict = chap_users.data_to_list()
            # chap_users_data_extracted = ChapUserPropertiesExtractor().extract(
            #     output_dict
            # )

        except Exception as e:
            self.module.fail_json(msg=str(e))

        self.module.exit_json(truecopy_pairs=tc_pairs)


def main(module=None):
    obj_store = VSPTrueCopyFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()