#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_ldev
short_description: Manages logical devices (LDEVs) on Hitachi VSP storage systems.
description:
  - This module allows for the creation, modification, or deletion of logical devices (LDEVs) on Hitachi VSP storage systems.
  - It supports operations such as creating a new LDEV, updating an existing LDEV, or deleting a LDEV.
  - This module is supported for both direct and gateway connection types.
  - For direct connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/ldev.yml)
  - For gateway connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/ldev.yml)
version_added: '3.0.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
options:
  state:
    description: The desired state of the LDEV.
    type: str
    required: false
    choices: ['present', 'absent']
    default: 'present'
  storage_system_info:
    description: Information about the Hitachi storage system.
    type: dict
    required: false
    suboptions:
      serial:
        description: Serial number of the Hitachi storage system.
        type: str
        required: false
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
        description: Username for authentication. This field is valid for direct connection type only, and it is a required field.
        type: str
        required: false
      password:
        description: Password for authentication. This field is valid for direct connection type only, and it is a required field.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['gateway', 'direct']
        default: 'direct'
      subscriber_id:
        description: This field is valid for gateway connection type only. This is an optional field and only needed to support multi-tenancy environment.
        type: str
        required: false
      api_token:
        description: Token value to access UAI gateway. This is a required field for gateway connection type.
        type: str
        required: false
  spec:
    description: Specification for the LDEV.
    type: dict
    required: true
    suboptions:
      pool_id:
        description: ID of the pool where the LDEV will be created. Options pool_id and parity_group_id are mutually exclusive.
        type: int
        required: false
      parity_group:
        description: ID of the parity_group where the LDEV will be created. Options pool_id and parity_group_id are mutually exclusive.
        type: str
        required: false
      size:
        description: Size of the LDEV. Can be specified in units such as GB, TB, or MB (e.g., '10GB', '5TB', '100MB', 200).
        type: str
        required: false
      ldev_id:
        description: ID of the LDEV (required for delete and update operations), for new it will assigned to this ldev if it's free.
        type: int
        required: false
      name:
        description: Name of the LDEV (optional). If not given, it assigns the name of the LDEV to "smrha-<ldev_id>".
        type: str
        required: false
      capacity_saving:
        description: >
          Whether to enable the capacity saving functions. Valid value is one of the following three options:
          - 1. compression -  Enable the capacity saving function (compression).
          - 2. compression_deduplication - Enable the capacity saving function (compression and deduplication).
          - 3 disabled - Disable the capacity saving function (compression and deduplication)
          Default value is disabled.
        type: str
        required: false
      data_reduction_share:
        description: Specify whether to create a data reduction shared volume.
          This value is set to true for Thin Image Advance when the connect type is direct.
        type: bool
        required: false
      nvm_subsystem_name:
        description: Specify whether the LDEV created will be part of an NVM subsystem.
        type: str
        required: false
      state:
        description:
          - State of the NVM subsystems task. This is valid only when nvm_subsystem_name is specified.
          - 'add_host_nqn : Add the host NQNs to the LDEV.'
          - 'remove_host_nqn : Remove the host NQNs from the LDEV.'
        type: str
        required: false
        choices: ['add_host_nqn', 'remove_host_nqn']
        default: 'add_host_nqn'
      host_nqns:
        description: List of host nqns to add to or remove from the LDEV depending on the state value.
        type: list
        required: false
        elements: str
      is_relocation_enabled:
        description: Specify whether to enable the tier relocation setting for the HDT volume.
        type: bool
        required: false
      tier_level_for_new_page_allocation:
        description: Specify which tier of the HDT pool will be prioritized when a new page is allocated.
        type: str
        required: false
      tiering_policy:
        description: Tiering policy for the LDEV.
        type: dict
        required: false
        suboptions:
          tier_level:
            description: Tier level, a value from 0 to 31.
            type: int
            required: false
          tier1_allocation_rate_min:
            description: Tier1 min, a value from 1 to 100.
            type: int
            required: false
          tier1_allocation_rate_max:
            description: Tier1 max, a value from 1 to 100.
            type: int
            required: false
          tier3_allocation_rate_min:
            description: Tier3 min, a value from 1 to 100.
            type: int
            required: false
          tier3_allocation_rate_max:
            description: Tier3 max, a value from 1 to 100.
            type: int
            required: false
      vldev_id:
        description: Specify the virtual LDEV id.
        type: int
        required: false
      force:
        description: Force delete. Delete the LDEV and removes the LDEV from hostgroups, iscsi targets or NVM subsystem namespace.
        type: bool
        required: false
      should_shred_volume_enable:
        description: It shreds an LDEV (basic volume) or DP volume. Overwrites the volume three times with dummy data.
        type: bool
        required: false
      qos_settings:
        description: QoS settings for the LDEV. This is available for direct connection type only.
        type: dict
        required: false
        suboptions:
          upper_iops:
            description: Upper IOPS limit.
            type: int
            required: false
          lower_iops:
            description: Lower IOPS limit.
            type: int
            required: false
          upper_transfer_rate:
            description: Upper transfer rate limit.
            type: int
            required: false
          lower_transfer_rate:
            description: Lower transfer rate limit.
            type: int
            required: false
          upper_alert_allowable_time:
            description: Upper alert allowable time.
            type: int
            required: false
          lower_alert_allowable_time:
            description: Lower alert allowable time.
            type: int
            required: false
          response_priority:
            description: Response priority.
            type: int
            required: false
          response_alert_allowable_time:
            description: Response alert allowable time.
            type: int
            required: false
"""

EXAMPLES = """
- name: Create a new LDEV
  hv_ldev:
    state: present
    storage_system_info:
      serial: "811150"
      connection_info:
        address: gateway.company.com
        api_token: "api_token_value"
        connection_type: "gateway"
        subscriber_id: 811150
    spec:
      pool_id: 1
      size: "10GB"
      name: "New_LDEV"
      capacity_saving: "compression_deduplication"
      data_reduction_share: true

- name: Update an existing LDEV
  hv_ldev:
    state: present
    storage_system_info:
      serial: "811150"
      connection_info:
        address: gateway.company.com
        api_token: "api_token_value"
        connection_type: "gateway"
        subscriber_id: 811150
    spec:
      ldev_id: 123
      size: "5TB"
      capacity_saving: "disabled"

- name: Create a new LDEV and assign vLDEV
  hv_ldev:
    state: present
    storage_system_info:
      serial: "811150"
      connection_info:
        address: gateway.company.com
        api_token: "api_token_value"
        connection_type: "gateway"
        subscriber_id: 811150
    spec:
      pool_id: 1
      size: "10GB"
      name: "New_LDEV"
      vldev_id: 456
      capacity_saving: "compression_deduplication"
      data_reduction_share: true

- name: Update an existing LDEV with vLDEV
  hv_ldev:
    state: present
    storage_system_info:
      serial: "811150"
      connection_info:
        address: gateway.company.com
        api_token: "api_token_value"
        connection_type: "gateway"
        subscriber_id: 811150
    spec:
      ldev_id: 123
      vldev_id: 234
      size: "5TB"
      capacity_saving: "disabled"

- name: Create ldev with free id and present to NVM System
  hv_ldev:
    state: present
    storage_system_info:
      serial: "811150"
      connection_info:
        address: gateway.company.com
        username: "admin"
        password: "passw0rd"
        connection_type: "direct"
    spec:
      pool_id: 1
      size: "10GB"
      name: "New_LDEV"
      capacity_saving: "compression_deduplication"
      data_reduction_share: true
      state: "add_host_nqn"
      nvm_subsystem_name: "nvm_subsystem_01"
      host_nqns: ["nqn.2014-08.org.example:uuid:4b73e622-ddc1-449a-99f7-412c0d3baa39"]

- name: Present existing volume to NVM System
  hv_ldev:
    state: present
    storage_system_info:
      serial: "811150"
      connection_info:
        address: gateway.company.com
        username: "admin"
        password: "passw0rd"
        connection_type: "direct"
    spec:
      ldev_id: 1
      state: "add_host_nqn"
      nvm_subsystem_name: "nvm_subsystem_01"
      host_nqns: ["nqn.2014-08.org.example:uuid:4b73e622-ddc1-449a-99f7-412c0d3baa39"]

- name: Delete a LDEV
  hv_ldev:
    state: absent
    storage_system_info:
      serial: "811150"
      connection_info:
        address: gateway.company.com
        api_token: "api_token_value"
        connection_type: "gateway"
        subscriber_id: 811150
    spec:
      ldev_id: 123
- name: Force delete ldev removes the ldev from hostgroups, iscsi targets or NVMe subsystem namespace
  hv_ldev:
    state: absent
    storage_system_info:
      serial: "811150"
      connection_info:
        address: gateway.company.com
        api_token: "api_token_value"
        connection_type: "gateway"
        subscriber_id: 811150
    spec:
      ldev_id: 123
      force: true

- name: Update the qos settings for an existing LDEV
  hv_ldev:
    state: absent
    storage_system_info:
      serial: "811150"
      connection_info:
        address: gateway.company.com
        username: "admin"
        password: "passw0rd"
        connection_type: "direct"
    spec:
      ldev_id: 123
      qos_settings:
        upper_iops: 1000
        lower_iops: 500
        upper_transfer_rate: 1000
        lower_transfer_rate: 500
        upper_alert_allowable_time: 1000
        lower_alert_allowable_time: 500
        response_priority: 1000
        response_alert_allowable_time: 1000
"""

RETURN = """
ldevs:
  description: Info of a logical device (LDEV).
  returned: success
  type: dict
  sample:
    ldev_id: 123
    deduplication_compression_mode: "Enabled"
    emulation_type: "Fibre Channel"
    name: "LDEV1"
    parity_group_id: "PG1"
    pool_id: 1
    resource_group_id: 1
    status: "Online"
    total_capacity: "10 GB"
    used_capacity: "5 GB"
    path_count: 2
    provision_type: "Thin Provisioning"
    logical_unit_id_hex_format: "0x123456789ABCDEF"
    canonical_name: "naa.123456789ABCDEF"
    dedup_compression_progress: 100
    dedup_compression_status: "Completed"
    is_alua: true
    is_data_reduction_share_enabled: true
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPVolumeArguments,
    VSPParametersManager,
)

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    StateValue,
    ConnectionTypes,
)
import ansible_collections.hitachivantara.vspone_block.plugins.module_utils.hv_ldev_runner as runner

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_volume,
)

try:
    from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_logger import (
        MessageID,
    )

    HAS_MESSAGE_ID = True
except ImportError:
    HAS_MESSAGE_ID = False


from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_exceptions import (
    HiException,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class VSPVolume:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = VSPVolumeArguments().volume()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        try:
            params_manager = VSPParametersManager(self.module.params)
            self.spec = params_manager.set_volume_spec()
            self.connection_info = params_manager.get_connection_info()
            self.serial = params_manager.get_serial()
            self.state = params_manager.get_state()
        except Exception as e:
            self.logger.writeError(f"An error occurred during initialization: {str(e)}")
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of LDEV operation ===")
        registration_message = validate_ansible_product_registration()

        try:
            comment = ""
            isGateway = False
            if self.connection_info.connection_type.lower() == ConnectionTypes.GATEWAY:
                isGateway = True
                volume_data = self.gateway_volume()
                # self.logger.writeDebug("20240726 volume_data, is partner? inject here?={}", volume_data)
                #  volume_data={'changed': False, 'lun': None, 'comment': 'LUN not found. (Perhaps it has already been deleted?)', 'skipped': True}
                self.connection_info.changed = volume_data.get("changed")
            else:
                volume_data = self.direct_volume()

            if self.state == StateValue.ABSENT and isGateway:
                comment = volume_data.get("comment", None)
                volume_response = []
            elif self.state == StateValue.ABSENT and not volume_data:
                volume_response = "Volume deleted"
            else:
                if isinstance(volume_data, str):
                    volume_response = volume_data
                else:
                    if isinstance(volume_data, dict):
                        comment = volume_data.get("comment", None)
                    volume_response = self.extract_volume_properties(volume_data)
                # if isGateway :
                #   volume_dict = volume_data.get("lun")
                #   if volume_dict:
                if self.spec.should_shred_volume_enable:
                    comment = "Volume shredded successfully," + comment

                if self.spec.vldev_id:
                    vldev_id = self.spec.vldev_id
                    if comment is None:
                        comment = ""
                    else:
                        comment = comment + " "
                    if vldev_id == -1:
                        comment = "Unassigned vldev_id successfully." + comment
                    else:
                        comment = (
                            "Assigned vldev_id "
                            + str(self.spec.vldev_id)
                            + " successfully."
                            + comment
                        )

        except Exception as e:
            self.logger.writeError(f"An error occurred: {str(e)}")
            self.logger.writeInfo("=== End of LDEV operation ===")
            self.module.fail_json(msg=str(e))

        response = {"changed": self.connection_info.changed, "volume": volume_response}
        if comment:
            response["comment"] = comment

        if registration_message:
            response["user_consent_required"] = registration_message

        self.logger.writeInfo(f"{response}")
        self.logger.writeInfo("=== End of LDEV operation ===")
        self.module.exit_json(**response)

    def direct_volume(self):

        result = vsp_volume.VSPVolumeReconciler(
            self.connection_info,
            self.serial,
        ).volume_reconcile(self.state, self.spec)

        return result

    def gateway_volume(self):

        try:
            return runner.runPlaybook(self.module)
        except HiException as ex:
            if HAS_MESSAGE_ID:
                self.logger.writeAMException(MessageID.ERR_OPERATION_LUN)
            else:
                self.logger.writeAMException("0X0000")
            raise Exception(ex.format())
        except Exception as ex:
            raise Exception(str(ex))

    def extract_volume_properties(self, volume_data):
        if not volume_data:
            return None

        # self.logger.writeDebug('20240726 volume_data={}',volume_data)
        self.logger.writeDebug("115 type={}", type(volume_data))
        if isinstance(volume_data, dict):
            volume_dict = volume_data.get("lun")
        else:
            volume_dict = volume_data.to_dict() if volume_data else {}
        return vsp_volume.VolumeCommonPropertiesExtractor(self.serial).extract(
            [volume_dict]
        )[0]


def main(module=None):
    """
    :return: None
    """
    obj_store = VSPVolume()
    obj_store.apply()


if __name__ == "__main__":
    main()
