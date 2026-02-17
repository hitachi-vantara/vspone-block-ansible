#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)


from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_ldev_facts
short_description: Retrieves information about logical devices (LDEVs) from VSP block storage systems.
description:
  - This module retrieves information about logical devices (LDEVs) from VSP block storage systems.
  - It provides details such as LDEV IDs, names, and other relevant information.
  - For examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/ldev_facts.yml)
version_added: "3.0.0"
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.9
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: full
extends_documentation_fragment:
  - hitachivantara.vspone_block.common.gateway_note
  - hitachivantara.vspone_block.common.connection_with_type
options:
  storage_system_info:
    description: Information about the storage system. This field is an optional field.
    type: dict
    required: false
    suboptions:
      serial:
        description: The serial number of the storage system.
        type: str
        required: false
  spec:
    description: Specification for retrieving LDEV information.
    type: dict
    required: false
    suboptions:
      ldev_id:
        description: ID of the specific LDEV to retrieve information for. Can be decimal or hexadecimal.
            Required for the Get one LDEV
            /Get one LDEV with detailed info
            /Get one ldev with detailed info by specifying one or more query parameters tasks.
        type: str
        required: false
      ldev_ids:
        description: List of LDEV IDs to retrieve information for. Can be decimal or hexadecimal.
            Required for the Get multiple LDEVs task.
        type: list
        elements: str
        required: false
      start_ldev_id:
        description: Starting LDEV ID for filtering LDEVs. Can be decimal or hexadecimal.
            Required for the Get LDEVs within range
            /Get LDEVs from start ID up to max count tasks.
            Optional for the Get Free LDEV IDs task.
        type: str
        required: false
      name:
        description: Name of the LDEV.
            Required for the Get LDEVs with the same name task.
        type: str
        required: false
      count:
        description: Number of LDEVs to retrieve.
            Required for the Get LDEVs from start ID up to max count task.
            Optional for the Get Free LDEV IDs task.
        type: int
        required: false
      end_ldev_id:
        description: Ending LDEV ID for filtering LDEVs. Can be decimal or hexadecimal.
            Required for the Get LDEVs within range task.
            Optional for the Get Free LDEV IDs task.
        type: str
        required: false
      is_detailed:
        description: Flag to retrieve all the additional properties that are not returned with regular LDEV facts output.
            Required for the Get one LDEV with detailed info task.
        type: bool
        required: false
        default: false
      pool_id:
        description: ID of the pool to filter LDEVs.
            Required for the Get LDEV details using pool ID task.
        type: int
        required: false
      resource_group_id:
        description: ID of the resource group to filter LDEVs.
            Required for the Get LDEV details using resource group ID task.
        type: int
        required: false
      journal_id:
        description: ID of the journal to filter LDEVs.
            Required for the Get LDEV details using journal ID task.
        type: int
        required: false
      parity_group_id:
        description: ID of the parity group to filter LDEVs.
            Required for the Get LDEV details using parity group ID task.
        type: str
        required: false
      query:
        description: >
          Getting all the additional properties of the LDEV facts output is time-consuming.
          To optimize the performance, you can specify a list of additional properties to be retrieved.
          This field allows you to specify a list of strings, where each string indicates which additional properties are retrieved.
          If is_detailed is set to true, this field will be ignored and all additional properties will be retrieved.
          The supported additional properties are: "cmd_device_settings", "encryption_settings", "nvm_subsystem_info", "qos_settings",
          "free_ldev_id" and "snapshots_info".
          Required for the Get one ldev with detailed info by specifying one or more query parameters
          /Get Free LDEV IDs tasks.
        type: list
        required: false
        elements: str
"""

EXAMPLES = """
- name: Get all ldevs
  hitachivantara.vspone_block.vsp.hv_ldev_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"

- name: Retrieve information about a specific LDEV
  hitachivantara.vspone_block.vsp.hv_ldev_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
    spec:
      ldev_id: 123
"""

RETURN = r"""
ansible_facts:
  description: Dictionary containing the discovered properties of the storage volumes.
  returned: always
  type: dict
  contains:
    volumes:
      description: List of storage volumes with their attributes.
      type: list
      elements: dict
      contains:
        canonical_name:
          description: Unique identifier for the volume.
          type: str
          sample: "naa.60060e8028273d005080273d00000102"
        clpr_id:
          description: CLPR (Control Logical Partition) ID.
          type: int
          sample: 0
        compression_acceleration_status:
          description: Status of compression accelerator.
          type: str
          sample: "ENABLED"
        cylinder:
          description: Cylinder number for mainframe volumes.
          type: int
          sample: 65945
        data_reduction_process_mode:
          description: Data reduction process mode.
          type: str
          sample: "inline"
        dedup_compression_progress:
          description: Progress percentage of deduplication and compression.
          type: int
          sample: -1
        dedup_compression_status:
          description: Status of deduplication and compression.
          type: str
          sample: "ENABLED"
        deduplication_compression_mode:
          description: Mode of deduplication and compression.
          type: str
          sample: "compression_deduplication"
        emulation_type:
          description: Emulation type of the volume.
          type: str
          sample: "3390-V-CVS"
        hostgroups:
          description: List of host groups associated with the volume.
          type: list
          elements: dict
          sample: []
        is_alua:
          description: Indicates if ALUA is enabled.
          type: bool
          sample: false
        is_command_device:
          description: Indicates if the volume is a command device.
          type: bool
          sample: null
        is_compression_acceleration_enabled:
          description: Whether compression accelerator is enabled.
          type: bool
          sample: true
        is_data_reduction_share_enabled:
          description: Indicates if data reduction share is enabled.
          type: bool
          sample: true
        is_device_group_definition_enabled:
          description: Indicates if device group definition is enabled.
          type: bool
          sample: null
        is_encryption_enabled:
          description: Indicates if encryption is enabled.
          type: bool
          sample: false
        is_full_allocation_enabled:
          description: Indicates if full allocation is enabled.
          type: bool
          sample: false
        is_relocation_enabled:
          description: Indicates if tier relocation is enabled.
          type: bool
          sample: null
        is_security_enabled:
          description: Indicates if security is enabled.
          type: bool
          sample: null
        is_user_authentication_enabled:
          description: Indicates if user authentication is enabled.
          type: bool
          sample: null
        is_write_protected:
          description: Indicates if write protection is enabled.
          type: bool
          sample: null
        is_write_protected_by_key:
          description: Indicates if write protection by key is enabled.
          type: bool
          sample: null
        iscsi_targets:
          description: List of iSCSI targets associated with the volume.
          type: list
          elements: dict
          sample: []
        ldev_id:
          description: Logical Device ID.
          type: int
          sample: 10010
        ldev_id_hex:
          description: Logical Device ID in hexadecimal.
          type: str
          sample: "00:27:1A"
        mp_blade_id:
          description: MP blade ID.
          type: int
          sample: 3
        name:
          description: Name of the volume.
          type: str
          sample: "smrha-258"
        num_of_ports:
          description: Number of ports associated with the volume.
          type: int
          sample: 2
        nvm_subsystems:
          description: List of NVMe subsystems associated with the volume.
          type: list
          elements: dict
          sample: []
        parent_volume_id:
          description: Parent volume ID for snapshot volumes.
          type: int
          sample: -1
        parent_volume_id_hex:
          description: Parent volume ID in hexadecimal format.
          type: str
          sample: "-0:00:01"
        parity_group_id:
          description: Parity group ID.
          type: str
          sample: "1-8"
        path_count:
          description: Path count to the volume.
          type: int
          sample: 2
        pool_id:
          description: Pool ID where the volume resides.
          type: int
          sample: 13
        ports:
          description: List of ports associated with the volume.
          type: list
          elements: dict
          contains:
            host_group_name:
              description: Host group name.
              type: str
              sample: "1C-G00"
            host_group_number:
              description: Host group number.
              type: int
              sample: 156
            lun:
              description: Logical Unit Number.
              type: int
              sample: 26
            port_id:
              description: Port identifier.
              type: str
              sample: "CL1-C"
          sample: [
            {
              "host_group_name": "1C-G00",
              "host_group_number": 156,
              "lun": 26,
              "port_id": "CL1-C"
            }
          ]
        provision_type:
          description: Provisioning type of the volume.
          type: str
          sample: "CVS"
        qos_settings:
          description: QoS settings for the volume.
          type: dict
          sample: null
        resource_group_id:
          description: Resource group ID of the volume.
          type: int
          sample: 0
        snapshots:
          description: List of snapshots associated with the volume.
          type: list
          elements: dict
          sample: []
        ssid:
          description: Subsystem ID for mainframe volumes.
          type: str
          sample: "000C"
        status:
          description: Current status of the volume.
          type: str
          sample: "NML"
        storage_serial_number:
          description: Serial number of the storage system.
          type: str
          sample: "70033"
        tiering_policy:
          description: Tiering policy details.
          type: dict
          sample: {}
        total_capacity:
          description: Total capacity of the volume.
          type: str
          sample: "54.71GB"
        total_capacity_in_mb:
          description: Total capacity of the volume in megabytes.
          type: float
          sample: 56023.04
        used_capacity:
          description: Used capacity of the volume.
          type: str
          sample: "0.00B"
        used_capacity_in_mb:
          description: Used capacity of the volume in megabytes.
          type: float
          sample: 0
        virtual_ldev_id:
          description: Virtual Logical Device ID.
          type: int
          sample: -1
        virtual_ldev_id_hex:
          description: Virtual Logical Device ID in hexadecimal.
          type: str
          sample: ""
    free_ldev_ids:
      description: List of free LDEV IDs when querying for available LDEVs.
      type: list
      elements: int
      sample: [100, 101, 102, 103, 104]
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPVolumeArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_volume,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.message.module_msgs import (
    ModuleMessage,
)


class VSPVolumeFactManager:
    def __init__(self):
        self.logger = Log()
        self.argument_spec = VSPVolumeArguments().volume_fact()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandatory , optional mandatory arguments
        )
        try:
            params_manager = VSPParametersManager(self.module.params)
            self.spec = params_manager.set_volume_fact_spec()
            self.connection_info = params_manager.get_connection_info()
            self.serial = params_manager.get_serial()
        except Exception as e:
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of LDEV Facts ===")
        registration_message = validate_ansible_product_registration()

        volume_data = None

        try:
            volume_data = self.direct_volume_read()
            if not isinstance(volume_data, list) and not isinstance(volume_data, str):
                volume_data_extracted = vsp_volume.VolumeCommonPropertiesExtractor(
                    self.serial
                ).extract(volume_data.data_to_list())
            else:
                volume_data_extracted = volume_data
        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of LDEV Facts ===")
            self.module.fail_json(msg=str(e))
        if (
            isinstance(volume_data, list)
            or (isinstance(volume_data, str))
            and "free_ldev_id" in self.spec.query
        ):
            data = {"free_ldev_ids": volume_data}
        else:
            data = {"volumes": volume_data_extracted}

        if registration_message:
            data["user_consent_required"] = registration_message

        self.logger.writeInfo(f"{data}")
        self.logger.writeInfo("=== End of LDEV Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)

    def direct_volume_read(self):

        result = vsp_volume.VSPVolumeReconciler(
            self.connection_info,
            self.serial,
        ).get_volumes(self.spec)

        if not result:
            raise ValueError(ModuleMessage.VOLUME_NOT_FOUND.value)
        return result


def main(module=None):
    obj_store = VSPVolumeFactManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
