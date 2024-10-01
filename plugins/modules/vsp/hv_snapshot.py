from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_snapshot
short_description: Manages snapshots on Hitachi VSP storage systems.
description:
  - This module allows for the creation, deletion, splitting, syncing, and restoring of snapshots on Hitachi VSP storage systems.
  - It supports various snapshot operations based on the specified task level.
version_added: '3.0.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.0.0
requirements:
options:
  state:
    description: The level of the snapshot task. Choices are 'present', 'absent', 'split', 'sync', 'restore', 'clone'.
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
    type: dict
    required: true
    suboptions:
      address:
        description: IP address or hostname of the storage system.
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
        choices: ['direct']
        default: 'direct'
      
  spec:
    description: Specification for the snapshot task.
    type: dict
    required: true
    suboptions:
      primary_volume_id:
        description: ID of the primary volume.
        type: str
        required: true
      pool_id:
        description: ID of the pool where the snapshot will be allocated.
        type: int
        required: true
      snapshot_group_name:
        description: Name of the snapshot group (required for 'direct' connection type and thin image advance).
        type: str
        required: false
      is_data_reduction_force_copy:
        description: Specify whether to forcibly create a pair for a volume for which the capacity saving function is enabled (Required for 'direct' connection type and thin image advance, Default is True when capacity savings is not 'disabled').
        required: false
      is_clone:
        description: Specify true to create a thin image advance clone pair
        required: false
      can_cascade:
        description: Specify whether the pair can be cascaded. (Required for 'direct' connection type and thin image advance, Default is True when capacity savings is not 'disabled', Lun may not required to add to any host group when is it true). 
        required: false
      allocate_new_consistency_group:
        description: Specify whether to allocate a consistency group.
        required: false
"""

EXAMPLES = """
- name: Create a snapshot
  hv_snapshot:
    state: present
    storage_system_info:
      serial: "ABC123"
      connection_info:
        address: gateway.company.com
        username: "username"
        password: "password"
        connection_type: "direct"
    spec:
      primary_volume_id: 123
      pool_id: 1
      snapshot_group_name: "snap_group"

- name: Create a thin image advance cascade pair
  hv_snapshot:
    state: present
    storage_system_info:
      serial: "ABC123"
      connection_info:
        address: gateway.company.com
        username: "username"
        password: "password"
        connection_type: "direct"
    spec:
      primary_volume_id: 123
      pool_id: 1
      snapshot_group_name: "snap_group"
      can_cascade: true
      is_data_reduction_force_copy: true

- name: Create a thin image advance clone pair
  hv_snapshot:
    state: present
    storage_system_info:
      serial: "ABC123"
      connection_info:
        address: gateway.company.com
        username: "username"
        password: "password"
        connection_type: "direct"
    spec:
      primary_volume_id: 123
      pool_id: 1
      snapshot_group_name: "snap_group"
      is_clone: true
      is_data_reduction_force_copy: true
            
- name: Clone a thin image advance clone pair
  hv_snapshot:
    state: clone
    storage_system_info:
      serial: "ABC123"
      connection_info:
        address: gateway.company.com
        username: "username"
        password: "password"
        connection_type: "direct"
    spec:
      primary_volume_id: 123
      mirror_unit: 3
      
- name: Delete a snapshot
  hv_snapshot:
    state: absent
    storage_system_info:
      serial: "ABC123"
      connection_info:
        address: gateway.company.com
        username: "username"
        password: "password"
        connection_type: "direct"
    spec:
      primary_volume_id: 123
      mirror_unit: 10

- name: Split a snapshot
  hv_snapshot:
    state: split
    storage_system_info:
      serial: "ABC123"
      connection_info:
        address: gateway.company.com
        username: "username"
        password: "password"
        connection_type: "direct"
    spec:
      primary_volume_id: 123
      mirror_unit: 10

- name: Resync a snapshot
  hv_snapshot:
    state: resync
    storage_system_info:
      serial: "ABC123"
      connection_info:
        address: gateway.company.com
        username: "username"
        password: "password"
        connection_type: "direct"
    spec:
      primary_volume_id: 123
      mirror_unit: 10

- name: Restore a snapshot
  hv_snapshot:
    state: restore
    storage_system_info:
      serial: "ABC123"
      connection_info:
        address: gateway.company.com
        username: "username"
        password: "password"
        connection_type: "direct"
    spec:
      primary_volume_id: 123
      mirror_unit: 3

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

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    operation_constants,
)
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
class VSPHtiSnapshotManager:

    def __init__(self):
        self.logger = Log()
        try:

            self.argument_spec = VSPSnapshotArguments().get_snapshot_reconcile_args()
            self.module = AnsibleModule(
                argument_spec=self.argument_spec,
                supports_check_mode=True,
                # can be added mandotary , optional mandatory arguments
            )

            self.params_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.params_manager.connection_info
            self.storage_serial_number = self.params_manager.storage_system_info.serial
            self.spec = self.params_manager.get_snapshot_reconcile_spec()
        except Exception as e:
            self.logger.writeException(e)
            self.module.fail_json(msg=str(e))

    def apply(self):
        snapshot_data = None
        self.logger.writeInfo(
            f"{self.params_manager.connection_info.connection_type} connection type"
        )
        try:

            snapshot_data = self.reconcile_snapshot()
            operation = operation_constants(self.module.params["state"])
            msg = f"Snapshot {operation} successfully" if not isinstance(snapshot_data, str) else snapshot_data
            resp = {
                "changed": self.connection_info.changed,
                "snapshot_data": snapshot_data if isinstance(snapshot_data, dict) else None,
                "msg": msg,
            }

        except Exception as e:
            self.module.fail_json(msg=str(e))

        self.module.exit_json(**resp)

    def reconcile_snapshot(self):
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

        result = reconciler.reconcile_snapshot(self.spec)
     
        
        ## 20240826 TIA post processing
        if self.connection_info.connection_type == ConnectionTypes.GATEWAY:
          # result can be just a string on negative test cases
          snapshot = result
          if snapshot and isinstance(snapshot, dict) :
              snapshot['can_cascade'] = False
              snapshot['is_cloned'] = ''
              snapshot['is_data_reduction_force_copy'] = False
              
            
              
              ttype = snapshot.get('type')
              if ttype == 'CASCADE':
                  snapshot['is_data_reduction_force_copy'] = True
                  snapshot['can_cascade'] = True
                  snapshot['is_cloned'] = False
              elif ttype == 'CLONE':
                  snapshot['is_data_reduction_force_copy'] = True
                  snapshot['can_cascade'] = True
                  snapshot['is_cloned'] = True
                  
              ## 20240826 inject the subscriber info
              snapshot['entitlement_status'] = "unassigned"
              subscriberId = self.connection_info.subscriber_id
              if subscriberId and subscriberId != "":
                  snapshot['entitlement_status'] = "assigned"
                  snapshot['partner_id'] = CommonConstants.PARTNER_ID
                  snapshot['subscriber_id'] = subscriberId
                                         
              result = snapshot
        
        return result


def main():
    """
    Create AWS FSx class instance and invoke apply
    :return: None
    """
    obj_store = VSPHtiSnapshotManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
