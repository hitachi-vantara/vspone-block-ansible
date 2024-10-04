DOCUMENTATION = '''
---
module: hv_gad
short_description: Manages GAD pairs on Hitachi VSP storage systems.
description:
  - This module allows for the creation, deletion, splitting and resync of GAD pairs on Hitachi VSP storage systems.
  - It supports various GAD pairs operations based on the specified task level.
version_added: '3.1.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.1.0
requirements:
options:
  state:
    description: The level of the GAD pairs task. Choices are 'present', 'absent', 'split', 'resync'.
    type: str
    required: true
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
        description: IP address or hostname of either the UAI gateway.
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
      primary_storage_serial_number:
        description: The serial number of the primary storage device (required for create).
        type: str
        required: false
      secondary_storage_serial_number:
        description: The serial number of the secondary storage device (required for create).
        type: str
        required: false
      primary_volume_id:
        description: Primary Volume Id.
        type: int
        required: True
      secondary_pool_id:
        description: Pool Id of secondary storage system (required for create).
        type: int
        required: False
      consistency_group_id:
        description: Consistency Group ID, 0 to 255 default is -1.
        type: int
        required: false
      allocate_new_consistency_group:
        description: Allocate and assign new consistency group ID, cannot be true if consistency_group_id is specified.
        type: bool
        required: false
      set_alua_mode:
        description: Set the ALUA mode to True on the primary and secondary volumes.
        type: bool
        required: false
      primary_resource_group_name:
        description: The primary resource group name
        type: str
        required: false
      secondary_resource_group_name:
        description: The secondary resource group name
        type: str
        required: false
      quorum_disk_id:
        description: The quorum disk ID Required for create operation only
        type: int
        required: false
      primary_hostgroups:
        description: The list of host groups on the primary storage device where the primary volume is to be provisioned.
        type: list
        element: dict
        required: false
        suboptions:
          id:
            description: Host group ID.
            type: int
            required: true
          name:
            description: Host group Name.
            type: str
            required: true
          resource_group_id:
            description: The storage resource group ID.
            type: int
            required: true
          port:
            description: Port name.
            type: str
            required: true
          enable_preferred_path:
            description: Enables the preferred path for the specified host group.
            type: str
            required: false
      secondary_hostgroups:
        description: The list of host groups on the secondary storage device where the secondary volume is to be provisioned(Required on create).
        type: list
        element: dict
        required: false
        suboptions:
          id:
            description: Host group ID.
            type: int
            required: true
          name:
            description: Host group Name.
            type: str
            required: true
          resource_group_id:
            description: The storage resource group ID.
            type: int
            required: true
          port:
            description: Port name.
            type: str
            required: true
          enable_preferred_path:
            description: Enables the preferred path for the specified host group.
            type: str
            required: false
'''

EXAMPLES = '''
- name: Create a GAD pair
  hv_gad:
    state: "present"
    storage_system_info:
      serial: 123456
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: "sub123"
    spec:
      primary_storage_serial_number: 12345
      secondary_storage_serial_number: 12346
      primary_volume_id: 11
      secondary_pool_id: 1
      primary_hostgroups: 
        - id: 1
          name: "hostgroup1"
          resource_group_id: 1
          port: "port1"
          enable_preferred_path: False
      secondary_hostgroups:
        - id: 2
          name: "hostgroup2"
          resource_group_id: 2
          port: "port2"
      primary_resource_group_name: "Sample"
      secondary_resource_group_name: "Sample"
      quorum_disk_id: 1
        

- name: Split GAD pair
  hv_gad:
    state: "split"
    storage_system_info:
      serial: 123456
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: "sub123"
    spec:
      primary_volume_id: 11

- name: Resync GAD pair
  hv_gad:
    state: "resync"
    storage_system_info:
      serial: 123456
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: "sub123"
    spec:
      primary_volume_id: 11

- name: Delete GAD pair
  hv_gad:
    state: "absent"
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
  description: Newly created GAD pair object.
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
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    operation_constants,
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


class VSPGADPairManager:

    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPGADArguments().gad_pair_args_spec()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )
        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.spec = self.params_manager.gad_pair_spec()
            self.serial = self.params_manager.get_serial()
            self.state = self.params_manager.get_state()
            self.connection_info = self.params_manager.get_connection_info()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        try:
            response = vsp_gad_pair.VSPGadPairReconciler(
                self.connection_info, self.serial
            ).gad_pair_reconcile(self.state, self.spec)

            result = response if not isinstance(response, str) else None 
            operation = operation_constants(self.module.params["state"])
            response_dict = {
                "changed": self.connection_info.changed,
                "data": result,
                "msg": f"Gad Pair {operation} successfully.",
            }
            self.module.exit_json(**response_dict)
        except Exception as ex:
            self.logger.writeException(ex)
            self.module.fail_json(msg=str(ex))


def main():
    obj_store = VSPGADPairManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
