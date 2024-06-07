import json

__metaclass__ = type

DOCUMENTATION = '''
---
module: hv_sds_block_volume_facts
short_description: Retrieve information about Hitachi sds block storage system volumes.
description:
  - This module retrieves information about storage volumes.
  - It provides details about a storage volume such as name, type and other details.
version_added: '3.0.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.0.0
requirements:
options:
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
        choices: ['direct', 'gateway']

  spec:
    description: Specification for retrieving volume information.
    suboptions:
      count:
        type: int
        description: The maximum number of obtained volume information items. Default is 500.
        required: false
      names:
        type: list
        description: The names of the volumes.
        required: false
      nicknames:
        type: list
        description: The nickname of the volume.
        required: false
      saving_setting:
        type: str
        description: Settings of the data reduction function for volumes. Choices are 'Disabled', 'Compression'.
        required: false
'''

EXAMPLES = '''
- name: Get volumes by default count
  hv_sds_block_volume_facts:         
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"

- name: Get volumes by count
  hv_sds_block_volume_facts:         
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"

    spec:
      count: 200

- name: Get volumes by names
  hv_sds_block_volume_facts:       
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"

    spec:
      names: [ 'test-volume1', 'test-volume2' ]

- name: Get volumes by other filters
  hv_sds_block_volume_facts:
          
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"

    spec:
      count: 200
      saving_setting: 'Disabled'

'''

RETURN = '''
volumes:
  description: A list of volumes.
  returned: always
  type: list
  elements: dict/list
  sample: [
    {
      "compute_node_info": [
          {
              "id": "4f9041aa-ab2f-4789-af2e-df4a0178a4d3",
              "name": "hitachitest"
          }
      ],
      "volume_info": {
          "data_reduction_effects": {
              "post_capacity_data_reduction": 0,
              "pre_capacity_data_reduction_without_system_data": 0,
              "system_data_capacity": 0
          },
          "data_reduction_progress_rate": false,
          "data_reduction_status": "Disabled",
          "full_allocated": false,
          "id": "ef69d5c6-ed7c-4302-959f-b8b8a7382f3b",
          "naa_id": "60060e810a85a000600a85a000000017",
          "name": "vol010",
          "nickname": "vol010",
          "number_of_connecting_servers": 1,
          "number_of_snapshots": 0,
          "pool_id": "cb9f7ecf-ceba-4d8e-808b-9c7bc3e59c03",
          "pool_name": "SP01",
          "protection_domain_id": "645c36b6-da9e-44bb-b711-430e06c7ad2b",
          "qos_param": {
              "upper_alert_allowable_time": -1,
              "upper_alert_time": false,
              "upper_limit_for_iops": -1,
              "upper_limit_for_transfer_rate": -1
          },
          "saving_mode": false,
          "saving_setting": "Disabled",
          "snapshot_attribute": "-",
          "snapshot_status": false,
          "status": "Normal",
          "status_summary": "Normal",
          "storage_controller_id": "fc22f6d3-2bd3-4df5-b5db-8a728e301af9",
          "total_capacity_mb": 120,
          "used_capacity_mb": 0,
          "volume_number": 23,
          "volume_type": "Normal",
          "vps_id": "(system)",
          "vps_name": "(system)"
      }
    },
    {
      "compute_node_info": [],
      "volume_info": {
          "data_reduction_effects": {
              "post_capacity_data_reduction": 0,
              "pre_capacity_data_reduction_without_system_data": 0,
              "system_data_capacity": 0
          },
          "data_reduction_progress_rate": false,
          "data_reduction_status": "Disabled",
          "full_allocated": false,
          "id": "fc57f5bd-35bb-482e-9416-6e20f1dc7b89",
          "naa_id": "60060e810a85a000600a85a00000001c",
          "name": "vol1-AnsibleAuto8403",
          "nickname": "nick1-AnsibleAuto8403",
          "number_of_connecting_servers": 0,
          "number_of_snapshots": 0,
          "pool_id": "cb9f7ecf-ceba-4d8e-808b-9c7bc3e59c03",
          "pool_name": "SP01",
          "protection_domain_id": "645c36b6-da9e-44bb-b711-430e06c7ad2b",
          "qos_param": {
              "upper_alert_allowable_time": -1,
              "upper_alert_time": false,
              "upper_limit_for_iops": -1,
              "upper_limit_for_transfer_rate": -1
          },
          "saving_mode": false,
          "saving_setting": "Disabled",
          "snapshot_attribute": "-",
          "snapshot_status": false,
          "status": "Normal",
          "status_summary": "Normal",
          "storage_controller_id": "fc22f6d3-2bd3-4df5-b5db-8a728e301af9",
          "total_capacity_mb": 100,
          "used_capacity_mb": 0,
          "volume_number": 28,
          "volume_type": "Normal",
          "vps_id": "(system)",
          "vps_name": "(system)"
      }
    }
  ]
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_volume import (
    SDSBVolumeReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_properties_extractor import (
    VolumePropertiesExtractor,
    VolumeAndComputeNodePropertiesExtractor
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBVolumeArguments,
    SDSBParametersManager,
)

logger = Log()


class SDSBVolumeFactsManager:
    def __init__(self):

        self.argument_spec = SDSBVolumeArguments().volume_facts()
        logger.writeDebug(
            f"MOD:hv_sds_volume_facts:argument_spec= {self.argument_spec}"
        )
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()
        # logger.writeDebug(f"MOD:hv_sds_block_compute_node_facts:argument_spec= {self.connection_info}")
        self.spec = parameter_manager.get_volume_fact_spec()
        logger.writeDebug(f"MOD:hv_sds_volume_facts:spec= {self.spec}")

    def apply(self):
        volumes = None
        volumes_data_extracted = None

        logger.writeInfo(f"{self.connection_info.connection_type} connection type")
        try:
            sdsb_reconciler = SDSBVolumeReconciler(self.connection_info)
            volumes = sdsb_reconciler.get_volumes(self.spec)

            logger.writeDebug(f"MOD:hv_sds_volume_facts:volumes= {volumes}")
            output_dict = volumes.data_to_list()
            volumes_data_extracted = VolumeAndComputeNodePropertiesExtractor().extract(output_dict)
            #volumes_data_extracted = VolumePropertiesExtractor().extract(output_dict)

        except Exception as e:
            self.module.fail_json(msg=str(e))

        self.module.exit_json(volumes=volumes_data_extracted)


def main(module=None):
    obj_store = SDSBVolumeFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
