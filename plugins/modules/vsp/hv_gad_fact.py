DOCUMENTATION = '''
---
module: hv_gad_fact
short_description: Retrieves GAD pairs information from Hitachi VSP storage systems.
description:
  - This module allows to fetch GAD pairs on Hitachi VSP storage systems.
version_added: '3.1.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.1.0
requirements:
options:
  storage_system_info:
    description: Information about the Hitachi storage system.
    type: dict
    required: true
    suboptions:
      serial:
        description: Serial number of the Hitachi storage system.
        type: str
        required: true
  connection_info:
    description: Information required to establish a connection to the storage system.
    required: true
    type: dict
    suboptions:
      address:
        description: IP address or hostname of either the UAI gateway .
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
        required: True
        choices: ['gateway']
      subscriber_id:
        description: Subscriber ID for multi-tenancy (required for "gateway" connection type).
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway (required for authentication either 'username,password' or api_token).
        type: str
        required: false
  spec:
    description: Specification for the GAD pairs task.
    type: dict
    required: true
    suboptions:
      primary_volume_id:
        description: Primary Volume Id.
        type: int
        required: True
'''

EXAMPLES = '''
- name: Get all GAD pairs
  hv_gad_fact:
    state: "present"
    storage_system_info:
      serial: 123456
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: "sub123"s
        

- name: Get GAD pairs by primary volume id
  hv_gad_fact:
    storage_system_info:
      serial: 123456
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: "sub123"
    spec:
      primary_volume_id: 11

'''

RETURN = '''
data:
  description: GAD pairs.
  returned: success
  type: dict
  elements: dict
  sample:
    {
        "consistency_group_id": 1,
        "copy_pace_track_size": -1,
        "copy_rate": 0,
        "mirror_unit_id": 1,
        "pair_name": "",
        "primary_hex_volume_id": "00:00:01",
        "primary_v_s_m_resource_group_name": "",
        "primary_virtual_hex_volume_id": "00:00:01",
        "primary_virtual_storage_id": "",
        "primary_virtual_volume_id": -1,
        "primary_volume_id": 1,
        "primary_volume_storage_id": 811111,
        "secondary_hex_volume_id": "00:00:02",
        "secondary_v_s_m_resource_group_name": "",
        "secondary_virtual_hex_volume_id": -1,
        "secondary_virtual_storage_id": "",
        "secondary_virtual_volume_id": -1,
        "secondary_volume_id": 2,
        "secondary_volume_storage_id": 811112,
        "status": "PAIR",
        "storage_serial_number": "811111",
        "svol_access_mode": "READONLY",
        "type": "GAD"
    }
'''




from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_gad_pair,
)
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPGADArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)


class VSPGADPairManagerFact:

    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPGADArguments().gad_pair_fact_args()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.gad_pair_fact_spec()
            self.serial = self.params_manager.get_serial()
            self.connection_info = self.params_manager.get_connection_info()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        try:
            response = vsp_gad_pair.VSPGadPairReconciler(
                self.connection_info, self.serial
            ).gad_pair_facts(self.spec)

            result = response if not isinstance(response, str) else None
            response_dict = {
                "gad_pair": result,
            }
            self.module.exit_json(**response_dict)
        except Exception as ex:
            self.logger.writeException(ex)
            self.module.fail_json(msg=str(ex))


def main():
    obj_store = VSPGADPairManagerFact()
    obj_store.apply()


if __name__ == "__main__":
    main()
