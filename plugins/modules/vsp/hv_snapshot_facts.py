#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_snapshot_facts
short_description: Retrieves snapshot information from from Hitachi VSP storage systems.
description:
  - This module retrieves information about snapshots from from Hitachi VSP storage systems.
version_added: '3.0.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.0.0
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
        no_log: true
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['direct']
        default: 'direct'
  spec:
    description:
      - Specification for the snapshot facts to be gathered.
    type: dict
    required: true
    suboptions:
      primary_volume_id:
        description:
          - The primary volume identifier. If not provided, it will be omitted.
        type: str
        required: false
      mirror_unit_id:
        description:
          - The mirror unit identifier. If not provided, it will be omitted.
        type: str
        required: false
"""

EXAMPLES = """
  - name: Gather snapshot facts with primary volume and mirror unit ID
    hv_snapshot_facts:
      storage_system_info:
        serial: '1234567890'
      connection_info:
        address: storage1.company.com
        username: "admin"
        password: "secret"
        connection_type: "direct"
      spec:
        primary_volume_id: 525
        mirror_unit_id: 10
  - name: Gather snapshot facts with only primary volume
    hv_snapshot_facts:
      storage_system_info:
        serial: '1234567890'
      connection_info:
        address: storage1.company.com
        username: "admin"
        password: "secret"
        connection_type: "direct"
      spec:
        primary_volume_id: 'volume1'
        
  - name: Gather snapshot facts without specific volume or mirror unit ID
    hv_snapshot_facts:
      storage_system_info:
        serial: '1234567890'
      connection_info:
        address: storage1.company.com
        username: "admin"
        password: "secret"
        connection_type: "direct"
"""

RETURN = """
snapshots:
  description: A list of snapshots gathered from the storage system.
  returned: always
  type: list
  elements: dict
  sample:
    - storage_serial_number: 810050
      primary_volume_id: 1030
      primary_hex_volume_id: "00:04:06"
      secondary_volume_id: 1031
      secondary_hex_volume_id: "00:04:07"
      svol_access_mode: ""
      pool_id: 12
      consistency_group_id: -1
      mirror_unit_id: 3
      copy_rate: -1
      copy_pace_track_size: ""
      status: "PAIR"
      type: ""
      snapshot_id: "1030,3"
      is_consistency_group: true
      primary_or_secondary: "P-VOL"
      snapshot_group_name: "NewNameSPG"
      can_cascade: true
"""

from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPSnapshotArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    StateValue,
    ConnectionTypes,
    CommonConstants,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_snapshot_reconciler import (
    VSPHtiSnapshotReconciler,
    SnapshotCommonPropertiesExtractor,
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
class VSPHtiSnapshotFactManager:

    def __init__(self):
        self.logger = Log()
        try:
            self.argument_spec = VSPSnapshotArguments().get_snapshot_fact_args()
            self.module = AnsibleModule(
                argument_spec=self.argument_spec,
                supports_check_mode=True,
                # can be added mandotary , optional mandatory arguments
            )

            self.params_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.params_manager.connection_info
            self.storage_serial_number = self.params_manager.storage_system_info.serial
            self.spec = self.params_manager.get_snapshot_fact_spec()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        snapshot_data = None
        self.logger.writeInfo(
            f"{self.params_manager.connection_info.connection_type} connection type"
        )
        try:

            snapshot_data = self.get_snapshot_facts()
        
            if snapshot_data:
                for snapshot in snapshot_data:
                    # thinImagePropertiesDto = None
                    # dto = snapshot.get('thin_image_properties_dto')
                    # if dto and isinstance(dto, dict) :
                    #     thinImagePropertiesDto = dto
                    # else:
                    #     del snapshot['thin_image_properties_dto']
                        
                    # dto = snapshot.get('thin_image_properties')
                    # if dto and isinstance(dto, dict) :
                    #     thinImagePropertiesDto = dto
                    # else:
                    #     del snapshot['thin_image_properties']
                    
                    if not isinstance(snapshot, dict) :
                      break
                        
                    snapshot['can_cascade'] = False
                    snapshot['is_cloned'] = ''
                    snapshot['is_data_reduction_force_copy'] = False
                    if True :
                        ttype = snapshot.get('type')
                        if ttype == 'CASCADE':
                            snapshot['is_data_reduction_force_copy'] = True
                            snapshot['can_cascade'] = True
                            snapshot['is_cloned'] = False
                        elif ttype == 'CLONE':
                            snapshot['is_data_reduction_force_copy'] = True
                            snapshot['can_cascade'] = True
                            snapshot['is_cloned'] = True
                    
        except Exception as e:
            self.module.fail_json(msg=str(e))

        self.module.exit_json(data=snapshot_data)

    def get_snapshot_facts(self):
        reconciler = VSPHtiSnapshotReconciler(
            self.connection_info,
            self.storage_serial_number,
        )
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
            found = reconciler.check_storage_in_ucpsystem()
            if not found:
                self.module.fail_json(
                    "The storage system is still onboarding or refreshing, Please try after sometime"
                )

        result = reconciler.get_snapshot_facts(self.spec)
        return result


def main():

    obj_store = VSPHtiSnapshotFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
