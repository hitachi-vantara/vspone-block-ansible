#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_hur_facts
short_description: Retrieves HUR information from from Hitachi VSP storage systems.
description:
  - This module retrieves information about HURs from from Hitachi VSP storage systems.
version_added: '3.1.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.1.0
requirements:
options:
  storage_system_info:
    description:
      - Information about the storage system.
    type: dict
    required: true
    suboptions:
      serial:
        description:
          - The serial number of the storage system.
        type: str
        required: true
  connection_info:
    description: Information required to establish a connection to the storage system.
    type: dict
    required: true
    suboptions:
      address:
        description: IP address or hostname of either the UAI gateway.
        type: str
        required: true
      api_token:
        description: API token.
        type: str
        required: false
      subscriber_id:
        description: Subscriber ID.
        type: int
        required: false
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: True
        choices: ['gateway']
  spec:
    description:
      - Specification for the HUR facts to be gathered.
    type: dict
    required: true
    suboptions:
      primary_volume_id:
        description:
          - The primary volume identifier. If not provided, it will be omitted.
        type: str
        required: false
      secondary_volume_id:
        description:
          - The secondary volume identifier. If not provided, it will be omitted.
        type: str
        required: false
      mirror_unit_id:
        description:
          - The mirror unit identifier. If not provided, it will be omitted.
        type: str
        required: false
"""

EXAMPLES = """
  - name: Gather HUR facts with primary volume and mirror unit ID
    hv_hur_facts:
      storage_system_info:
        serial: '1234567890'
      connection_info:
        address: storage1.company.com
        api_token: "xxx"
        connection_type: "gateway"
        subscriber_id: 12345
      spec:
        primary_volume_id: 111
        mirror_unit_id: 10
        
  - name: Gather HUR facts with only primary volume
    hv_hur_facts:
      storage_system_info:
        serial: '1234567890'
      connection_info:
        address: storage1.company.com
        api_token: "xxx"
        connection_type: "gateway"
        subscriber_id: 12345
      spec:
        primary_volume_id: 111
        
  - name: Gather HUR facts with only secondary volume
    hv_hur_facts:
      storage_system_info:
        serial: '1234567890'
      connection_info:
        address: storage1.company.com
        api_token: "xxx"
        connection_type: "gateway"
        subscriber_id: 12345
      spec:
        secondary_volume_id: 111
                
  - name: Gather HUR facts without specific volume or mirror unit ID
    hv_hur_facts:
      storage_system_info:
        serial: '1234567890'
      connection_info:
        address: storage1.company.com
        api_token: "xxx"
        connection_type: "gateway"
        subscriber_id: 12345
"""

RETURN = """
hurs:
  description: A list of hurs gathered from the storage system.
  returned: always
  type: list
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
"""

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
    HurInfoExtractor,
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
class VSPHurFactManager:

    def __init__(self):
        self.logger = Log()
        try:
            self.argument_spec = VSPHurArguments().get_hur_fact_args()
            self.module = AnsibleModule(
                argument_spec=self.argument_spec,
                supports_check_mode=True,
                # can be added mandotary , optional mandatory arguments
            )

            self.params_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.params_manager.connection_info
            self.storage_serial_number = self.params_manager.storage_system_info.serial
            self.spec = self.params_manager.get_hur_fact_spec()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        hur_data = None
        self.logger.writeInfo(
            f"{self.params_manager.connection_info.connection_type} connection type"
        )
        try:
            hur_data = self.get_hur_facts()
        except Exception as e:
            self.module.fail_json(msg=str(e))

        self.module.exit_json(data=hur_data)

    def get_hur_facts(self):
        reconciler = VSPHurReconciler(
            self.connection_info,
            self.storage_serial_number,
            None
        )
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            found = reconciler.check_storage_in_ucpsystem()
            if not found:
                self.module.fail_json(
                    "The storage system is still onboarding or refreshing, Please try after sometime"
                )

        result = reconciler.get_hur_facts(self.spec)
        return result


def main():
    """
    Create class instance and invoke apply
    :return: None
    """
    obj_store = VSPHurFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
