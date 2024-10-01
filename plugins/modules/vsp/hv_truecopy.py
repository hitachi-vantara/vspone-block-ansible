from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hv_truecopy
short_description: Manages TrueCopy pairs on Hitachi VSP storage systems.
description:
  - This module allows for the creation, deletion, splitting and re-syncing of TrueCopy pairs on Hitachi VSP storage systems.
  - It supports various TrueCopy pairs operations based on the specified task level.
version_added: '3.1.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.1.0
requirements:
options:
  state:
    description: The level of the TrueCopy pairs task. Choices are 'present', 'absent', 'split', 'sync'.
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
    description: Specification for the TrueCopy pairs task.
    type: dict
    required: true
    suboptions:
      primary_volume_id:
        description: Primary volume id.
        type: int
        required: true
      consistency_group_id:
        description: Consistency Group ID, 0 to 255.
        type: int
        required: false
      fence_level:
        description: Specifies the primary volume fence level setting and determines if the host is denied access or continues to access the primary volume when the pair is suspended because of an error.
        type: str
        required: false
        choices: ['NEVER', 'DATA', 'STATUS']
        default: 'NEVER'
      allocate_new_consistency_group:
        description: Allocate and assign new consistency group ID, cannot be true if consistency_group_id is specified.
        type: bool
        required: false
      secondary_storage_serial_number:
        description: Secondary storage serial number, required for create.
        type: int
        required: false
      secondary_pool_id:
        description: Id of the dynamic pool where the secondary volume will be created.
        type: int
        required: false
      secondary_hostgroup:
        description: Host group details of secondary volume.
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
- name: Create a TrueCopy pair
  hv_truecopy:
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
      consistency_group_id: -1
      fence_level: 'NEVER'
      allocate_new_consistency_group: false
      secondary_storage_serial_number: 123456
      secondary_pool_id: 1

- name: Split TrueCopy pair
  hv_truecopy:
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

- name: Resync TrueCopy pair
  hv_truecopy:
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

- name: Delete TrueCopy pair
  hv_truecopy:
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
  description: Newly created TrueCopy pair object.
  returned: success
  type: dict
  elements: dict
  sample:
        {
        "consistency_group_id": -1,
        "copy_pace_track_size": 15,
        "copy_rate": 100,
        "mirror_unit_id": 0,
        "pair_name": "",
        "primary_hex_volume_id": "00:00:01",
        "primary_v_s_m_resource_group_name": "0",
        "primary_virtual_hex_volume_id": "00:00:01",
        "primary_virtual_storage_id": "0",
        "primary_virtual_volume_id": 0,
        "primary_volume_id": 1,
        "primary_volume_storage_id": 811111,
        "resource_id": "replpair-9c2a4c0e0c1e123454d56167851f45e4",
        "secondary_hex_volume_id": "00:00:63",
        "secondary_v_s_m_resource_group_name": "0",
        "secondary_virtual_hex_volume_id": -1,
        "secondary_virtual_storage_id": "811112",
        "secondary_virtual_volume_id": 99,
        "secondary_volume_id": 99,
        "secondary_volume_storage_id": 811112,
        "status": "PAIR",
        "storage_serial_number": "811112",
        "svol_access_mode": "READONLY",
        "type": "TRUE_COPY"
    }
'''
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPTrueCopyArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_true_copy import (
    VSPTrueCopyReconciler,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log


from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log_decorator import (
    LogDecorator,
)

@LogDecorator.debug_methods
class VSPSTrueCopyManager:

    def __init__(self):
        self.logger = Log()
        try:
            self.argument_spec = VSPTrueCopyArguments().true_copy()

            self.module = AnsibleModule(
                argument_spec=self.argument_spec,
                supports_check_mode=True,
                # can be added mandotary , optional mandatory arguments
            )

            self.params_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.params_manager.connection_info
            self.storage_serial_number = self.params_manager.storage_system_info.serial
            self.spec = self.params_manager.true_cpoy_spec()
            self.state = self.params_manager.get_state()

        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        data = None
        self.logger.writeDebug(
            f"{self.params_manager.connection_info.connection_type} connection type"
        )
        self.logger.writeDebug("state = {}", self.state)
        try:
            data = self.true_copy_module()

        except Exception as e:
            self.module.fail_json(msg=str(e))

        resp = {
                "changed": self.connection_info.changed,
                "truecopy_info": data,
                "msg": self.get_message(),
            }
        
        self.module.exit_json(**resp)

    def true_copy_module(self):
        reconciler = VSPTrueCopyReconciler(
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

        # result = reconciler.reconcile_true_copy(self.spec)
        return reconciler.reconcile_true_copy(self.spec)

    def get_message(self):
        
        if self.state == "present":
            return "TrueCopy Pair created successfully."
        elif self.state == "absent":
            return "TrueCopy Pair deleted successfully."
        elif self.state == "sync":
            return "TrueCopy Pair re-synced successfully."
        elif self.state == "split":
            return "TrueCopy Pair split successfully."
        else:
            return "Unknown state provided."

def main():
    """
    :return: None
    """
    obj_store = VSPSTrueCopyManager()
    obj_store.apply()


if __name__ == "__main__":
    main()