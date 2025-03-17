#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_remote_storage_registration
short_description: Manages remote storage registration and unregistration on Hitachi VSP storage systems.
description:
  - This module manages remote storage registration and unregistration on Hitachi VSP storage systems.
  - This module is supported only for C(direct) connection type.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/remote_storage_registration.yml)
version_added: '3.2.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.8
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: full
options:
  state:
    description: The desired state of the task.
    type: str
    required: false
    choices: ['present', 'absent']
    default: 'present'
  storage_system_info:
    description: Information about the remote storage systems.
    type: dict
    required: false
    suboptions:
      serial:
        description: The serial number of the storage system.
        type: str
        required: false
  connection_info:
    description: Information required to establish a connection to the storage system.
    type: dict
    required: true
    suboptions:
      address:
        description: IP address or hostname of storage system.
        type: str
        required: true
      username:
        description: Username for authentication. This field is valid for C(direct) connection type only, and it is a required field.
        type: str
        required: false
      password:
        description: Password for authentication. This field is valid for C(direct) connection type only, and it is a required field.
        type: str
        required: false
      api_token:
        description: Value of the lock token to operate on locked resources.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system. Only C(direct) connection is supported.
        type: str
        required: false
        choices: ['gateway', 'direct']
        default: 'direct'
      subscriber_id:
        description: This field is valid for C(gateway) connection type only. This is an optional field and only needed to support multi-tenancy environment.
        type: str
        required: false
  secondary_connection_info:
    description: Information required to establish a connection to the secondary storage system.
    required: true
    type: dict
    suboptions:
      address:
        description: IP address or hostname of storage system.
        type: str
        required: true
      username:
        description: Username for authentication to the secondary storage system.
        type: str
        required: false
      password:
        description: Password for authentication to the secondary storage system.
        type: str
        required: false
      api_token:
        description: Value of the lock token to operate on locked resources.
        type: str
        required: false
  spec:
    description: Specification for the remote storage registration and unregistration.
    type: dict
    required: false
    suboptions:
      is_mutual_discovery:
        description: Specify whether to perform a mutual registration operation. true means perform a mutual registration operation.
        type: bool
        required: false
      is_mutual_deletion:
        description: Specify whether to perform a mutual deletion operation during unregistration. true means perform a mutual deletion operation.
        type: bool
        required: false
      rest_server_ip:
        description: IP address of the rest server of the remote storage system.
            If not provided, secondary_connection_info.address will be used for rest_server_ip.
        type: str
        required: false
      rest_server_port:
        description: Port number of the rest server of the remote storage system. If not provided, 443 will be used for rest_server_port.
        type: int
        required: false
"""

EXAMPLES = """
- name: Register Remote Storage
  hitachivantara.vspone_block.vsp.hv_remote_storage_registration:
    connection_info:
      address: 172.0.0.2
      username: "admin"
      password: "password"
    secondary_connection_info:
      address: 172.0.0.3
      username: "admin"
      password: "password"
    state: present
    spec:
      is_mutual_discovery: true
      rest_server_ip: 172.0.0.1

- name: Unregister Remote Storage
  hitachivantara.vspone_block.vsp.hv_remote_storage_registration:
    connection_info:
      address: 172.0.0.2
      username: "admin"
      password: "password"
    secondary_connection_info:
      address: 172.0.0.3
      username: "admin"
      password: "password"
    state: present
    spec:
      is_mutual_deletion: true
"""

RETURN = """
remote_storage:
  description: >
    A list of information about the storage systems registered on the REST API server.
  returned: always
  type: list
  elements: dict
  contains:
    storages_registered_in_local:
      description: List of storage systems registered locally.
      type: list
      elements: dict
      contains:
        communication_modes:
          description: List of communication modes.
          type: list
          elements: dict
          contains:
            communicationMode:
              description: Mode of communication.
              type: str
              sample: "lanConnectionMode"
        ctl1_ip:
          description: IP address of controller 1.
          type: str
          sample: "172.0.0.127"
        ctl2_ip:
          description: IP address of controller 2.
          type: str
          sample: "172.0.0.128"
        dkc_type:
          description: Type of DKC (Local or Remote).
          type: str
          sample: "Local"
        model:
          description: Model of the storage system.
          type: str
          sample: "VSP E1090H"
        rest_server_ip:
          description: IP address of the REST server.
          type: str
          sample: "172.0.0.2"
        rest_server_port:
          description: Port number of the REST server.
          type: int
          sample: 443
        serial_number:
          description: Serial number of the storage system.
          type: str
          sample: "710036"
        storage_device_id:
          description: Storage device ID.
          type: str
          sample: "938000710036"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_remote_storage_registration import (
    VSPRemoteStorageRegistrationReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPRemoteStorageRegistrationArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.message.module_msgs import (
    ModuleMessage,
)


class VSPRemoteStorageRegistrationManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = (
            VSPRemoteStorageRegistrationArguments().remote_storage_registration()
        )

        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
            # can be added mandotary , optional mandatory arguments
        )
        try:
            self.parameter_manager = VSPParametersManager(self.module.params)
            self.connection_info = self.parameter_manager.get_connection_info()
            self.storage_serial_number = (
                self.parameter_manager.storage_system_info.serial
            )
            self.spec = self.parameter_manager.get_remote_storage_registration_spec()
            self.state = self.parameter_manager.get_state()
            self.secondary_connection_info = (
                self.parameter_manager.get_secondary_connection_info()
            )
            self.spec.secondary_connection_info = self.secondary_connection_info
        except Exception as e:
            self.logger.writeError(f"An error occurred during initialization: {str(e)}")
            self.module.fail_json(msg=str(e))

    def apply(self):

        self.logger.writeInfo("=== Start of Remote Storage Registration operation. ===")
        registration_message = validate_ansible_product_registration()
        if (
            self.parameter_manager.connection_info.connection_type.lower()
            == ConnectionTypes.GATEWAY
        ):
            self.logger.writeError(f"{ModuleMessage.NOT_SUPPORTED_FOR_GW.value}")
            self.logger.writeInfo(
                "=== End of Remote Storage Registration operation ==="
            )
            self.module.fail_json(msg=ModuleMessage.NOT_SUPPORTED_FOR_GW.value)

        remote_storage = None
        comment = None
        try:
            reconciler = VSPRemoteStorageRegistrationReconciler(
                self.connection_info, self.storage_serial_number, self.state
            )
            remote_storage = reconciler.reconcile_remote_storage_registration(self.spec)

        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo(
                "=== End of Remote Storage Registration operation ==="
            )
            self.module.fail_json(msg=str(e))
        resp = {
            "changed": self.connection_info.changed,
        }
        comment = None
        if remote_storage is None and self.state == "absent":
            comment = "Remote storage is unregistered successfully."

        if remote_storage:
            if isinstance(remote_storage, str):
                comment = remote_storage
            else:
                resp["remote_storage"] = remote_storage
                comment = "Remote storage is registered successfully."
        if comment:
            resp["comment"] = comment
        if registration_message:
            resp["user_consent_required"] = registration_message

        self.logger.writeInfo(f"{resp}")
        self.logger.writeInfo("=== End of Remote Storage Registration operation ===")
        self.module.exit_json(**resp)


def main(module=None):
    obj_store = VSPRemoteStorageRegistrationManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
