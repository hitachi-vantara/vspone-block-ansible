import json

__metaclass__ = type

DOCUMENTATION = '''
---
module: hv_sds_block_compute_node
short_description: Manages Hitachi SDS block storage system compute nodes.
description:
  - This module allows for the creation, updation and deletion of compute node, 
    adding iqn initiators to compute node, remove iqn initiators from compute node,
    attach volumes to compute node, detach volumes from compute node.
  - It supports various compute node operations based on the specified task level.
version_added: '3.0.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.0.0
requirements:
options:
  state:
    description: The level of the compute node task. Choices are 'present', 'absent'.
    type: str
    required: true
  connection_info:
    description: Information required to establish a connection to the storage system.
    required: true
    type: dict
    suboptions:
      address:
        description: IP address or hostname of the storage system.
        type: str
        required: true
      username:
        description: Username for authentication.
        type: str
        required: true
      password:
        description: Password for authentication.
        type: str
        required: true
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['direct']
        default: 'direct'
  spec:
    description: Specification for the compute node task.
    type: dict
    required: true
    suboptions:
      id:
        description: ID of the compute node.
        type: str
        required: false
      name:
        description: Name of the compute node.
        type: str
        required: false
      os_type:
        description: The OS type of the compute node.
        type: str
        required: false
      state:
        description: The state of the compute node task. Choices are 'add_iscsi_initiator', 'remove_iscsi_initiator', 'attach_volume', 'detach_volume'.
        type: str
        required: false
      iscsi_initiators:
        description: The array of iSCSI Initiators.
        type: list
        required: false
      volumes:
        description: The array of name of volumes.
        type: list
        required: false
      should_delete_all_volumes:
        description: Will delete the volumes that are not attached to any compute node.
        type: bool
        required: false
'''

EXAMPLES = '''
- name: Create compute node
  hv_sds_block_compute_node:
    state: present
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
    spec:
      name: "computenode1"
      os_type: "VMWARE"
      iscsi_initiators: ["iqn.1991-05.com.hitachi:test-iscsi-iqn1", "iqn.1991-05.com.hitachi:test-iscsi-iqn2"]
      volumes: ["test-volume1", "test-volume2"]

- name: Delete compute node by ID
  hv_sds_block_compute_node:
    state: present
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
    spec:
      id: "3d971bb3-40fd-4cb5-bf68-2010b30aa74d"

- name: Delete compute node by name
  hv_sds_block_compute_node:
    state: present
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
    spec:
      name: "computenode1"
      should_delete_all_volumes: true

- name: Update compute node name
  hv_sds_block_compute_node:
    state: present
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
    spec:
      id: "3d971bb3-40fd-4cb5-bf68-2010b30aa74d"
      name: "computenode1a"
      os_type: "LINUX"

- name: Add iqn initiators to compute node
  hv_sds_block_compute_node:
    state: present
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
    spec:
      state: "add_iscsi_initiator"
      name: "computenode1"
      os_type: "VMWARE"
      iscsi_initiators: ["iqn.1991-05.com.hitachi:test-iscsi-iqn3", "iqn.1991-05.com.hitachi:test-iscsi-iqn4"]
  
- name: Remove iqn initiators from compute node
  hv_sds_block_compute_node:
    state: present
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
    spec:
      state: "remove_iscsi_initiator"
      name: "computenode1"
      os_type: "VMWARE"
      iscsi_initiators: ["iqn.1991-05.com.hitachi:test-iscsi-iqn3", "iqn.1991-05.com.hitachi:test-iscsi-iqn4"]

- name: Attach volumes to compute node
  hv_sds_block_compute_node:
    state: present
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
    spec:
      state: "attach_volume"
      name: "computenode1"
      volumes: ["test-volume3", "test-volume4"]

- name: Detach volumes from compute node
  hv_sds_block_compute_node:
    state: present
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
    spec:
      state: "detach_volume"
      name: "computenode1"
      volumes: ["test-volume3", "test-volume4"]
'''

RETURN = '''
data:
  description: The compute node information.
  returned: always
  type: dict
  elements: dict/list
  sample:
    {
      "compute_node_info": {
          "id": "ca1beba6-4392-4d21-a161-3e3e94fb45e2",
          "lun": -1,
          "nickname": "spc-iqn.1994-05.com.redhat:5475aab33df5",
          "number_of_paths": -1,
          "number_of_volumes": 2,
          "os_type": "Linux",
          "paths": [
              {
                  "hba_name": "iqn.1994-05.com.redhat:5475aab33df5",
                  "port_ids": [
                      "932962b5-ab61-429f-ba06-cd976e1a8f97",
                      "181d4ed3-ae8a-418d-9deb-72a4eb1e2204",
                      "0f13e320-53e7-4088-aa11-418636b58376"
                  ]
              }
          ],
          "total_capacity_mb": 90112,
          "used_capacity_mb": 4998,
          "vps_id": "(system)",
          "vps_name": "(system)"
      },
      "volume_info": [
          {
              "id": "3ac02c92-05f0-4eba-9c00-3503afc18290",
              "name": "spc-a879277ec4"
          },
          {
              "id": "c792486a-283f-4ac0-b98a-ff0ebd021057",
              "name": "spc-147090e05b"
          }
      ]
    }
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    StateValue,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_compute_node import (
    SDSBComputeNodeReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_properties_extractor import (
    ComputeNodePropertiesExtractor,
    ComputeNodeAndVolumePropertiesExtractor,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBComputeNodeArguments,
    SDSBParametersManager,
)

logger = Log()


class SDSBComputeNodeManager:
    def __init__(self):

        self.argument_spec = SDSBComputeNodeArguments().compute_node()
        logger.writeDebug(
            f"MOD:hv_sds_block_compute_node:argument_spec= {self.argument_spec}"
        )
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )

        params_manager = SDSBParametersManager(self.module.params)
        self.state = params_manager.get_state()
        # self.compute_node_fact_spec = params_manager.get_compute_node_spec()

        self.connection_info = params_manager.get_connection_info()
        # logger.writeDebug(f"MOD:hv_sds_block_compute_node_facts:argument_spec= {self.connection_info}")
        self.spec = params_manager.get_compute_node_spec()
        logger.writeDebug(f"MOD:hv_sds_block_compute_node:argument_spec= {self.spec}")

    def apply(self):
        compute_node = None
        compute_node_data_extracted = None

        logger.writeInfo(f"{self.connection_info.connection_type} connection type")
        try:
            sdsb_reconciler = SDSBComputeNodeReconciler(self.connection_info)
            compute_node = sdsb_reconciler.reconcile_compute_node(self.state, self.spec)

            logger.writeDebug(
                f"MOD:hv_sds_block_compute_node_facts:compute_nodes= {compute_node}"
            )

            if self.state.lower() == StateValue.ABSENT:
                compute_node_data_extracted = compute_node
            else:
                output_dict = compute_node.to_dict()
                compute_node_data_extracted = ComputeNodeAndVolumePropertiesExtractor().extract_dict(
                    output_dict
                )

        except Exception as e:
            self.module.fail_json(msg=str(e))

        response = {"changed": self.connection_info.changed, "data": compute_node_data_extracted}
        # self.module.exit_json(compute_nodes=compute_node_data_extracted)
        self.module.exit_json(**response)


def main(module=None):
    obj_store = SDSBComputeNodeManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
