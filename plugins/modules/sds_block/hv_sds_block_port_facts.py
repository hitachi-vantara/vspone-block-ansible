import json

__metaclass__ = type

DOCUMENTATION = '''
---
module: hv_sds_block_port_facts
short_description: Retrieve information about Hitachi sds block storage system compute ports.
description:
  - This module retrieves information about compute ports.
  - It provides details about a compute port such as ID, lun and other details.
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
    description: Specification for retrieving compute port information.
    suboptions:
      names:
        type: list
        description: A WWN or an iSCSI name.
        required: false
      nicknames:
        type: list
        description: The names of the compute nodes.
        required: false
'''

EXAMPLES = '''
- name: Retrieve information about all compute ports
  hv_sds_block_port_facts:         
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"

- name: Retrieve information about compute ports by compute node name
  hv_sds_block_port_facts:         
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"

    spec:
      nicknames: ["000-iSCSI-000"]

- name: Retrieve information about compute ports by names
  hv_sds_block_port_facts:        
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"

    spec:
      names: ["p1-compute-node", "RD-compute-node-111"]

'''

RETURN = '''
ports:
  description: A list of compute ports.
  returned: always
  type: list
  elements: dict/list
  sample: [
    {
        "chap_users_info": [
            {
                "id": "464e1fd1-9892-4134-866c-6964ce786676",
                "initiator_chap_user_name": "",
                "target_chap_user_name": "test"
            }
        ],
        "port_auth_info": {
            "auth_mode": "CHAP",
            "id": "932962b5-ab61-429f-ba06-cd976e1a8f97",
            "is_discovery_chap_auth": false,
            "is_mutual_chap_auth": true
        },
        "port_info": {
            "configured_port_speed": "Auto",
            "fc_information": null,
            "id": "932962b5-ab61-429f-ba06-cd976e1a8f97",
            "interface_name": "eth2",
            "iscsi_information": {
                "delayed_ack": true,
                "ip_mode": "ipv4",
                "ipv4_information": {
                    "address": "10.76.34.51",
                    "default_gateway": "10.76.34.1",
                    "subnet_mask": "255.255.255.0"
                },
                "ipv6_information": {
                    "default_gateway": "",
                    "global_address1": "",
                    "global_address_mode": "Manual",
                    "linklocal_address": "",
                    "linklocal_address_mode": "Auto",
                    "subnet_prefix_length1": 0
                },
                "is_isns_client_enabled": false,
                "isns_servers": [
                    {
                        "index": 1,
                        "port": 3205,
                        "server_name": ""
                    }
                ],
                "mac_address": "b4:96:91:c8:75:bc",
                "mtu_size": 9000
            },
            "name": "iqn.1994-04.jp.co.hitachi:rsd.sph.t.0a85a.000",
            "nickname": "000-iSCSI-000",
            "nvme_tcp_information": null,
            "port_speed": "25G",
            "port_speed_duplex": "25Gbps Full",
            "protection_domain_id": "645c36b6-da9e-44bb-b711-430e06c7ad2b",
            "protocol": "iSCSI",
            "status": "Normal",
            "status_summary": "Normal",
            "storage_node_id": "01f598b8-dc1c-45fc-b821-5ea108d42593",
            "type": "Universal"
        }
    }
  ]
'''

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_port import (
    SDSBPortReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_properties_extractor import (
    PortDetailPropertiesExtractor,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBPortArguments,
    SDSBParametersManager,
)

logger = Log()


class SDSBPortFactsManager:
    def __init__(self):

        self.argument_spec = SDSBPortArguments().port_facts()
        logger.writeDebug(
            f"MOD:hv_sds_block_port_facts:argument_spec= {self.argument_spec}"
        )
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )

        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()
        # logger.writeDebug(f"MOD:hv_sds_block_port_facts:connection_info= {self.connection_info}")
        self.spec = parameter_manager.get_compute_port_fact_spec()
        logger.writeDebug(f"MOD:hv_sds_block_port_facts:argument_spec= {self.spec}")

    def apply(self):
        ports = None
        ports_data_extracted = None

        logger.writeInfo(f"{self.connection_info.connection_type} connection type")
        try:
            sdsb_reconciler = SDSBPortReconciler(self.connection_info)
            ports = sdsb_reconciler.get_compute_ports(self.spec)

            logger.writeDebug(f"MOD:hv_sds_block_port_facts:ports= {ports}")
            output_dict = ports.data_to_list()
            ports_data_extracted = PortDetailPropertiesExtractor().extract(output_dict)
            # ports_data_extracted = json.dumps(ports.data, default=lambda o: o.__dict__, indent=4)

        except Exception as e:
            self.module.fail_json(msg=str(e))

        self.module.exit_json(ports=ports_data_extracted)


def main(module=None):
    obj_store = SDSBPortFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
