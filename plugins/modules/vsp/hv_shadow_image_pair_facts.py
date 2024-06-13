from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = '''
---
module: hv_shadow_image_pair_facts
short_description: Retrieves information about shadow image pairs from Hitachi VSP storage systems.
description:
  - This module retrieves information about shadow image pairs from Hitachi VSP storage systems.
  - It provides details about shadow image pair such as ID, status and other relevant information.
version_added: '3.0.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.0.0
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
    description: Specification for retrieving shadow image pair information.
    type: dict
    suboptions:
      pvol:
        type: int
        description: Primary volume id.
        required: false
'''

EXAMPLES = '''
- name: Retrieve information about all shadow image pairs
  hv_shadow_image_pair_facts:         
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"

    storage_system_info:
      serial: 123456

- name: Retrieve information about a specific shadow image pair
  hv_shadow_image_pair_facts:       
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"

    storage_system_info:
      serial: 123456

    spec:
      pvol: 274
'''

RETURN = '''
data:
  description: List of shadow image pairs.
  returned: success
  type: list
  elements: dict
  sample: [
    {
        "consistency_group_id": -1,
        "copy_pace_track_size": "MEDIUM",
        "copy_rate": 100,
        "entitlement_status": "assigned",
        "mirror_unitId": -1,
        "partner_id": "partner123",
        "primary_hex_volume_id": "00:01:12",
        "primary_volume_id": 274,
        "resource_id": "localpair-2749fed78e8d23a61ed17a8af71c85f8",
        "secondary_hex_volumeId": "00:01:17",
        "secondary_volume_id": 279,
        "status": "PAIR",
        "storage_serial_number": "123456",
        "subscriber_id": "subscriber123",
        "svol_access_mode": "READONLY"
    }
  ]
'''


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPShadowImagePairArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    StateValue,
    ConnectionTypes,
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

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log


logger = Log()


class VSPShadowImagePairManager:
    def __init__(self):

        self.argument_spec = (
            VSPShadowImagePairArguments().get_all_shadow_image_pair_fact()
        )
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )

        self.params_manager = VSPParametersManager(self.module.params)
        self.spec = self.params_manager.set_shadow_image_pair_fact_spec()
        logger.writeInfo(f"{self.spec} SPEC")

    def apply(self):

        shadow_image_pair_data = None
        logger.writeInfo(
            f"{self.params_manager.connection_info.connection_type} connection type"
        )
        try:

            shadow_image_pair_data = self.gateway_shadow_image_pair_read()            

        except Exception as e:
            self.module.fail_json(msg=str(e))

        data = {"data":shadow_image_pair_data}

        if not shadow_image_pair_data:
            if self.spec.pvol is not None:               
                data['comment'] = "Data not available with pvol " + str(self.spec.pvol)
            else:
                data['comment'] = "Couldn't read shadow image pairs. "

        self.module.exit_json(**data)

    def gateway_shadow_image_pair_read(self):

        result = vsp_shadow_image_pair_reconciler.VSPShadowImagePairReconciler(
            self.params_manager.connection_info,
            self.params_manager.storage_system_info.serial,
        ).shadow_image_pair_facts(self.spec)

        
        return result


def main():
    """
    Create AWS FSx class instance and invoke apply
    :return: None
    """
    obj_store = VSPShadowImagePairManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
