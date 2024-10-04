__metaclass__ = type

DOCUMENTATION = '''
---
module: hv_sds_block_vps
short_description: Manages Hitachi SDS block storage system Virtual Private Storages (VPS) volume ADR setting.
description:
  - This module allows to update Virtual Private Storages volume ADR setting.
version_added: '3.1.0'
author:
  - Hitachi Vantara, LTD. VERSION 3.1.0
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
        choices: ['direct']
        default: 'direct'
  spec:
    description: Specification for VPS information.
    suboptions:
      vps_id:
        type: str
        description: ID of the VPS to retrieve information for.
        required: false
      vps_name:
        type: str
        description: VPS name to retrieve information for.
        required: false
      capacity_saving:
        description: Capacity saving for the VPS volumes.
        type: str
        required: false
        choices: ['Disabled', 'Compression']    
        default: ['Disabled']
'''

EXAMPLES = '''
- name: Update VPS Volume ADR setting by VPS Id
  hv_sds_block_chap_user:        
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"

    spec:
      vps_id: "464e1fd1-9892-4134-866c-6964ce786676"
      capacity_saving: "Disabled"

- name: Update VPS Volume ADR setting by VPS name
  hv_sds_block_chap_user_facts:       
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"

    spec:
      vps_name: "VPS_01"
      capacity_saving: "Compression"

'''

RETURN = '''
vps:
  description: Attributes of the VPS.
  returned: always
  type: dict
  elements: dict
  sample: 
    {

        "id": "d2c1fa60-5c41-486a-9551-ec41c74d9f01",
        "name": "VPS_01",
        "number_of_hbas_created": 0,
        "number_of_servers_created": 0,
        "number_of_sessions_created": 0,
        "number_of_user_groups_created": 0,
        "number_of_users_created": 0,
        "number_of_volume_server_connections_created": 0,
        "upper_limit_for_number_of_hbas": 400,
        "upper_limit_for_number_of_servers": 100,
        "upper_limit_for_number_of_sessions": 436,
        "upper_limit_for_number_of_user_groups": 256,
        "upper_limit_for_number_of_users": 256,
        "upper_limit_for_number_of_volume_server_connections": 100,
        "volume_settings": {
            "capacity_of_volumes_created": 0,
            "capacity_saving_of_volume": "Compression",
            "number_of_volumes_created": 0,
            "pool_id": "f5ef8935-ed38-4894-a90b-f821ab6d3d89",
            "qos_param": {
                "upper_alert_allowable_time_of_volume": -1,
                "upper_limit_for_iops_of_volume": -1,
                "upper_limit_for_transfer_rate_of_volume": -1
            },
            "saving_mode_of_volume": "Inline",
            "upper_limit_for_capacity_of_single_volume": -1,
            "upper_limit_for_capacity_of_volumes": 100,
            "upper_limit_for_number_of_volumes": 50
        }
    }
'''
from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_vps import (
    SDSBVpsReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import Log
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBVpsArguments,
    SDSBParametersManager,
)

logger = Log()

class SDSBVpsManager:
    def __init__(self):

        self.argument_spec = SDSBVpsArguments().vps()
        logger.writeDebug(
            f"MOD:hv_sds_block_vps:argument_spec= {self.argument_spec}"
        )
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )

        parameter_manager = SDSBParametersManager(self.module.params)
        self.state = parameter_manager.get_state()
        self.connection_info = parameter_manager.get_connection_info()
        self.spec = parameter_manager.get_vps_spec()
        logger.writeDebug(f"MOD:hv_sds_block_vsp:spec= {self.spec}")

    def apply(self):

        logger.writeInfo(f"{self.connection_info.connection_type} connection type")
        try:
            sdsb_reconciler = SDSBVpsReconciler(self.connection_info)
            vps = sdsb_reconciler.reconcile_vps(self.state, self.spec)

            logger.writeDebug(
                f"MOD:hv_sds_block_vps:vps= {vps}"
            )

        except Exception as e:
            self.module.fail_json(msg=str(e))

        response = {
            "changed": self.connection_info.changed,
            "data": vps,
        }
        self.module.exit_json(**response)
        # self.module.exit_json(vsp=vps)


def main(module=None):
    obj_store = SDSBVpsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
