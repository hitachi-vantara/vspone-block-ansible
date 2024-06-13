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
    description: The level of the snapshot task. Choices are 'present', 'absent', 'split', 'sync', 'restore'.
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
      pvol:
        description: ID of the primary volume.
        type: str
        required: true
      pool_id:
        description: ID of the pool where the snapshot will be allocated.
        type: int
        required: true
      snapshot_group_name:
        description: Name of the snapshot group (required for 'direct' connection type).
        type: str
        required: false
      is_data_reduction_force_copy:
        description: Specify whether to forcibly create a pair for a volume for which the capacity saving function is enabled (Required for 'direct' connection type, Default is True when capacity savings is not 'disabled').
        required: false
      can_cascade:
        description: Specify whether the pair can be cascaded. (Required for 'direct' connection type, Default is True when capacity savings is not 'disabled', Lun may not required to add to any host group when is it true). 
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
      pvol: "pvol123"
      pool_id: 1
      snapshot_group_name: "snap_group"

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
      pvol: 565
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
      pvol: 565
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
      pvol: 565
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
      pvol: 566
      mirror_unit: 3
"""

RETURN = """
snapshots:
  description: A list of snapshots gathered from the storage system.
  returned: always
  type: list
  elements: dict
  sample:
    - storageSerialNumber: 123456
      primaryVolumeId: 101
      primaryHexVolumeId: "0x65"
      secondaryVolumeId: 102
      secondaryHexVolumeId: "0x66"
      svolAccessMode: "read-write"
      poolId: 1
      consistencyGroupId: 1
      mirrorUnitId: 200
      copyRate: 3
      copyPaceTrackSize: "64KB"
      status: "available"
      type: "snapshot"
      entitlementStatus: "entitled"
      snapshotId: "snap001"
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
            resp = {
                "changed": self.connection_info.changed,
                "snapshot_data": snapshot_data,
                "msg": f"Snapshot {operation} successfully",
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
                    "Storage system is not onboard in the default UAI Gateway or still onboarding/refreshing"
                )

        result = reconciler.reconcile_snapshot(self.spec)
        if not result:
            self.module.fail_json("Couldn't read snapshot ")
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
