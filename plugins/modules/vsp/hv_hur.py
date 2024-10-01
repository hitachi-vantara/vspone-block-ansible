from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hv_hur
short_description: Manages HUR pairs on Hitachi VSP storage systems.
description:
  - This module allows for the creation, deletion, splitting and re-syncing of HUR pairs on Hitachi VSP storage systems.
  - It supports various HUR pairs operations based on the specified task level.
version_added: '3.1.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.1.0
requirements:
options:
  state:
    description: The level of the HUR pairs task. Choices are 'present', 'absent', 'split', 'resync'.
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
        default: 'direct'
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
    description: Specification for the HUR pairs task.
    type: dict
    required: true
    suboptions:
      primary_volume_id:
        description: Primary volume id.
        type: int
        required: true
      primary_volume_journal_id:
        description: Primary volume journal id, required for create.
        type: int
        required: false
      secondary_volume_journal_id:
        description: Secondary volume journal id, required for create.
        type: int
        required: false
      secondary_storage_serial_number:
        description: Secondary storage serial number, required for create.
        type: int
        required: false
      consistency_group_id:
        description: Consistency Group ID, 0 to 255.
        type: int
        required: false
      allocate_new_consistency_group:
        description: Allocate and assign new consistency group ID, cannot be true if consistency_group_id is specified.
        type: bool
        required: false
      enable_delta_resync:
        description: Creates a delta-resync HUR pair.
        type: bool
        required: false
      mirror_unit_id:
        description: Mirror Unit Id, required for non-create operations.
        type: int
        required: false
      secondary_pool_id:
        description: Id of dynamic pool where the secondary volume will be created.
        type: int
        required: false
      secondary_hostgroup:
        description: Host group details of secondary volume .
        type: dict
        required: false
        suboptions:
          name:
            description: Name of the host group.
            type: str
            required: True
          port:
            description: Port of the host group.
            type: str
            required: True
          
    
'''

EXAMPLES = '''
- name: Create a HUR pair
  hv_hur:
    state: "present"
    storage_system_info:
      serial: 123456
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: "sub123"
    spec:
      primary_volume_id: 11
      primary_volume_journal_id: 11
      secondary_volume_journal_id: 11
      secondary_pool_id: 1
      allocate_new_consistency_group: true
      secondary_storage_serial_number: 123456

- name: Split HUR pair
  hv_hur:
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
      mirror_unit_id: 2

- name: Resync HUR pair
  hv_hur:
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
      mirror_unit_id: 2

- name: Delete HUR pair
  hv_hur:
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
      mirror_unit_id: 2
'''

RETURN = '''
data:
  description: Newly created HUR pair object.
  returned: success
  type: dict
  elements: dict
  sample:
    {
        "consistency_group_id": 1,
        "copy_pace_track_size": -1,
        "copy_rate": 0,
        "mirror_unit_id": 1,
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
        "type": "HUR"
    }
'''


from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPHurArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    StateValue,
    ConnectionTypes,
    CommonConstants,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_hur import (
    VSPHurReconciler,
)

try:
    from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_logger import (
        MessageID,
    )

    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log


from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log_decorator import (
    LogDecorator,
)

@LogDecorator.debug_methods
class VSPSHurManager:

    def __init__(self):
        self.logger = Log()
        try:
            self.argument_spec = VSPHurArguments().hur()

            self.module = AnsibleModule(
                argument_spec=self.argument_spec,
                supports_check_mode=True,
                # can be added mandotary , optional mandatory arguments
            )

            self.params_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.params_manager.connection_info
            self.storage_serial_number = self.params_manager.storage_system_info.serial
            self.spec = self.params_manager.hur_spec()
            self.state = self.params_manager.get_state()

        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        port_data = None
        self.logger.writeInfo(
            f"{self.params_manager.connection_info.connection_type} connection type"
        )
        try:

            _ , data = self.hur_module()

        except Exception as e:
            self.module.fail_json(msg=str(e))
            
        # msg = comment
        # if msg is None:
        #   msg = self.get_message()

        resp = {
                "changed": self.connection_info.changed,
                "hur_info": data,
                "msg": self.get_message(),
            }
        self.module.exit_json(**resp)

    def hur_module(self):
        reconciler = VSPHurReconciler(
            self.connection_info,
            self.storage_serial_number,
            self.state
        )
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            found = reconciler.check_storage_in_ucpsystem()
            if not found:
                self.module.fail_json(
                    "The storage system is still onboarding or refreshing, Please try after sometime"
                )

        result = reconciler.reconcile_hur(self.spec)
        return result

    def get_message(self):

        if self.state == "present":
            return "HUR Pair created successfully."
        elif self.state == "absent":
            return "HUR Pair deleted successfully."
        elif self.state == "resync":
            return "HUR Pair re-synced successfully."
        elif self.state == "split":
            return "HUR Pair split successfully."
        else:
            return "Unknown state provided."

def main():
    """
    :return: None
    """
    obj_store = VSPSHurManager()
    obj_store.apply()


if __name__ == "__main__":
    main()