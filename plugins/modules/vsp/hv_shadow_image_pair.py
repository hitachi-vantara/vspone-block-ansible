from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hv_shadow_image_pair
short_description: Manages shadow image pairs on Hitachi VSP storage systems.
description:
  - This module allows for the creation, deletion, splitting, syncing and restoring of shadow image pairs on Hitachi VSP storage systems.
  - It supports various shadow image pairs operations based on the specified task level.
version_added: '3.0.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.0.0
requirements:
options:
  state:
    description: The level of the shadow image pairs task. Choices are 'present', 'absent', 'split', 'restore', 'sync'.
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
        description: IP address or hostname of either the UAI gateway (if connection_type is gateway) or the storage system (if connection_type is direct).
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
        required: false
        choices: ['gateway', 'direct']
        default: 'direct'
      subscriber_id:
        description: Subscriber ID for multi-tenancy (required for "gateway" connection type).
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway (required for authentication either 'username,password' or api_token).
        type: str
        required: false
  spec:
    description: Specification for the shadow image pairs task.
    type: dict
    required: true
    suboptions:
      primary_volume_id:
        description: Primary volume id.
        type: int
        required: true
      secondary_volume_id:
        description: Secondary volume id.
        type: int
        required: true
      auto_split:
        description: Auto split.
        type: bool
        required: false
      allocate_new_consistency_group:
        description: New consistency group.
        type: bool
        required: false
      consistency_group_id:
        description: Consistency group id.
        type: int
        required: false
      copy_pace_track_size:
        description: Copy pace track size.
        type: str
        required: false
        choices: ['SLOW', 'MEDIUM', 'FAST']
      enable_quick_mode:
        description: Enable quick mode.
        type: bool
        required: false
      enable_read_write:
        description: Enable read write.
        type: bool
        required: false
      copy_pace:
        description: Copy pace.
        type: str
        required: false
        choices: ['SLOW', 'MEDIUM', 'FAST']
      pair_id:
        description: Pair Id.
        type: str
        required: false
    
'''

EXAMPLES = '''
- name: Create a shadow image pair
  hv_shadow_image_pair:
    state: "present"
    storage_system_info:
      serial: 123456
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: "sub123"
    spec:
      primary_volume_id: 274
      secondary_volume_id: 277
      allocate_new_consistency_group: true
      copy_pace_track_size: "MEDIUM"

- name: Split shadow image pair
  hv_shadow_image_pair:
    state: "split"
    storage_system_info:
      serial: 123456
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: "sub123"
    spec:
      primary_volume_id: 274
      secondary_volume_id: 277
      enable_quick_mode: true
      enable_read_write: false

- name: Sync shadow image pair
  hv_shadow_image_pair:
    state: "sync"
    storage_system_info:
      serial: 123456
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: "sub123"
    spec:
      primary_volume_id: 274
      secondary_volume_id: 277
      enable_quick_mode: true
      copy_pace: "FAST"

- name: Create and Auto-Split shadow image pair
  hv_shadow_image_pair:
    state: "split"
    storage_system_info:
      serial: 123456
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: "sub123"
    spec:
      primary_volume_id: 274
      secondary_volume_id: 277
      copy_pace_track_size: "MEDIUM"

- name: Restore shadow image pair
  hv_shadow_image_pair:
    state: "restore"
    storage_system_info:
      serial: 123456
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: "sub123"
    spec:
      primary_volume_id: 274
      secondary_volume_id: 277
      enable_quick_mode: true
      copy_pace: "FAST"

- name: Delete shadow image pair
  hv_shadow_image_pair:
    state: "absent"
    storage_system_info:
      serial: 123456
    connection_info:
      address: gateway.company.com
      api_token: "api_token_value"
      connection_type: "gateway"
      subscriber_id: "sub123"
    spec:
      primary_volume_id: 274
      secondary_volume_id: 277
'''

RETURN = '''
data:
  description: Newly created shadow image pair object.
  returned: success
  type: dict
  elements: dict
  sample:
    {
        "consistency_group_id": -1,
        "copy_pace_track_size": "MEDIUM",
        "copy_rate": 100,
        "entitlement_status": "assigned",
        "mirror_unit_id": -1,
        "partner_id": "partner123",
        "primary_hex_volume_id": "00:01:12",
        "primary_volume_id": 274,
        "resource_id": "localpair-2749fed78e8d23a61ed17a8af71c85f8",
        "secondary_hex_volume_id": "00:01:17",
        "secondary_volume_id": 279,
        "status": "PAIR",
        "storage_serial_number": "123456",
        "subscriber_id": "subscriber123",
        "svol_access_mode": "READONLY"
    }
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPShadowImagePairArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    StateValue,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_shadow_image_pair_reconciler,
)


try:
    from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_logger import (
        MessageID,
    )

    HAS_MESSAGE_ID = True
except ImportError as error:
    HAS_MESSAGE_ID = False


from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_exceptions import (
    HiException,
)

logger = Log()


class VSPShadowImagePairManager:
    def __init__(self):

        self.argument_spec = VSPShadowImagePairArguments().shadow_image_pair()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )

        try:
            self.params_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.params_manager.get_connection_info()
            self.serial = self.params_manager.get_serial()
            self.state = self.params_manager.get_state()
            if self.state is None:
                self.state = StateValue.PRESENT
            logger.writeInfo(f"State: {self.state}")

            self.spec = self.params_manager.set_shadow_image_pair_spec()
            # print("Spec: "+self.spec)
            logger.writeInfo(f"Spec: {self.spec}")
        except Exception as e:
            logger.writeError(f"An error occurred during initialization: {str(e)}")
            self.module.fail_json(msg=str(e))

    def shadow_image_pair(self):
        reconciler = vsp_shadow_image_pair_reconciler.VSPShadowImagePairReconciler(
            self.params_manager.connection_info,
            self.params_manager.storage_system_info.serial,
            self.spec,
        )
        return reconciler.shadow_image_pair_module(self.state)

    def apply(self):

        logger.writeInfo(
            f"{self.params_manager.connection_info.connection_type} connection type"
        )
        shadow_image_resposne = None
        try:            
            shadow_image_resposne = self.shadow_image_pair()

        except Exception as e:
            logger.writeError(f"An error occurred: {str(e)}")
            self.module.fail_json(msg=str(e))

        response = {
            "changed": self.connection_info.changed,
            "data": shadow_image_resposne,
        }
        self.module.exit_json(**response)

    


def main():
    """
    Create AWS FSx class instance and invoke apply
    :return: None
    """
    obj_store = VSPShadowImagePairManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
