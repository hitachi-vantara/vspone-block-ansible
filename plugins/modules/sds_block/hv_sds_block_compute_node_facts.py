import json

__metaclass__ = type

DOCUMENTATION = '''
---
module: hv_sds_block_compute_node_facts
short_description: Retrieve information about Hitachi sds block storage system compute nodes.
description:
  - This module retrieves information about compute nodes.
  - It provides details about a compute node such as ID, volume and other details.
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
    description: Specification for retrieving compute node information.
    suboptions:
      names:
        type: list
        description: The names of the compute nodes.
        required: false
      hba_name:
        type: str
        description: A WWN or an iSCSI name.
        required: false
'''

EXAMPLES = '''
- name: Retrieve information about all compute nodes
  hv_sds_block_compute_node_facts:        
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"

- name: Retrieve information about compute nodes by hba_name
  hv_sds_block_compute_node_facts:         
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"

    spec:
      hba_name: 'iqn.1991-05.com.hitachi:test-iscsi-iqn1'

- name: Retrieve information about compute nodes by names
  hv_sds_block_compute_node_facts:        
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"

    spec:
      names: [ 'computenode1', 'computenode2' ]

'''

RETURN = '''
compute_nodes:
  description: A list of compute nodes.
  returned: always
  type: list
  elements: dict
  sample: [
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
  ]
'''

from ansible.module_utils.basic import AnsibleModule
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


class SDSBComputeNodeFactsManager:
    def __init__(self):

        self.argument_spec = SDSBComputeNodeArguments().compute_node_facts()
        logger.writeDebug(
            f"MOD:hv_sds_block_compute_node_facts:argument_spec= {self.argument_spec}"
        )
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )

        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()
        # logger.writeDebug(f"MOD:hv_sds_block_compute_node_facts:argument_spec= {self.connection_info}")
        self.spec = parameter_manager.get_compute_node_fact_spec()
        logger.writeDebug(f"MOD:hv_sds_block_compute_node_facts:spec= {self.spec}")

    def apply(self):
        compute_nodes = None
        compute_node_data_extracted = None

        logger.writeInfo(f"{self.connection_info.connection_type} connection type")
        try:
            sdsb_reconciler = SDSBComputeNodeReconciler(self.connection_info)
            compute_nodes = sdsb_reconciler.get_compute_nodes(self.spec)

            logger.writeDebug(
                f"MOD:hv_sds_block_compute_node_facts:compute_nodes= {compute_nodes}"
            )
            output_dict = compute_nodes.data_to_list()
            compute_node_data_extracted = ComputeNodeAndVolumePropertiesExtractor().extract(
                output_dict
            )

        except Exception as e:
            self.module.fail_json(msg=str(e))

        self.module.exit_json(compute_nodes=compute_node_data_extracted)


def main(module=None):
    obj_store = SDSBComputeNodeFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
