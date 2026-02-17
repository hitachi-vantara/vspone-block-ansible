#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_sds_block_audit_log_setting
short_description: Manages Hitachi SDS block storage system audit log settings.
description:
  - This module allows for the configuration of audit log settings.
  - It supports updating syslog forwarding settings and server configurations.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/audit_log_setting.yml)
version_added: '4.6.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.9
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: none
extends_documentation_fragment:
  - hitachivantara.vspone_block.common.sdsb_connection_info
options:
  state:
    description: The level of the audit log settings task. Choices are C(present) and C(download_audit_log).
    type: str
    required: false
    choices: ['present', 'download_audit_log']
    default: 'present'
  spec:
    description: Specification for the audit log settings task.
    type: dict
    required: false
    suboptions:
      audit_log_file_location:
        description: The directory where the audit log file will be downloaded. This is a
          required field when the state field is C(download_audit_log).
        type: str
        required: false
      refresh:
        description: Whether to create the audit log file on the storage system before downloading.
          This is a valid field when the state field is C(download_audit_log).
        type: bool
        required: false
        default: false
      syslog_forwarding_setting:
        description: Syslog forwarding configuration.
        type: dict
        required: false
        suboptions:
          location_name:
            description: Location name for syslog forwarding.
            type: str
            required: false
          syslog_servers:
            description: List of syslog servers configuration.
            type: list
            elements: dict
            required: false
            suboptions:
              index:
                description: Index of the syslog server.
                type: int
                choices: [1, 2]
                required: true
              is_enabled:
                description: Whether the syslog server is enabled.
                type: bool
                required: false
              server_name:
                description: Syslog server name or IP address.
                type: str
                required: false
              port:
                description: Syslog server port number.
                type: int
                required: false
              transport_protocol:
                description: Transport protocol for syslog server.
                type: str
                choices: ['UDP']
                required: false
"""

EXAMPLES = """
- name: Configure audit log settings with syslog forwarding
  hitachivantara.vspone_block.sds_block.hv_sds_block_audit_log_setting:
    state: present
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      syslog_forwarding_setting:
        location_name: "datacenter1"
        syslog_servers:
          - index: 1
            is_enabled: true
            server_name: "syslog.example.com"
            port: 514
            transport_protocol: "UDP"
          - index: 2
            is_enabled: false
            server_name: "backup-syslog.example.com"
            port: 514
            transport_protocol: "UDP"

- name: Update syslog server configuration
  hitachivantara.vspone_block.sds_block.hv_sds_block_audit_log_setting:
    state: present
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      syslog_forwarding_setting:
        location_name: "datacenter1"
        syslog_servers:
          - index: 1
            is_enabled: true
            server_name: "new-syslog.example.com"
            port: 1514
            transport_protocol: "UDP"

- name: Download audit log file
  hitachivantara.vspone_block.sds_block.hv_sds_block_audit_log_setting:
    state: download_audit_log
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      audit_log_file_location: "/tmp/audit_logs"

- name: Create and download audit log file
  hitachivantara.vspone_block.sds_block.hv_sds_block_audit_log_setting:
    state: download_audit_log
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      audit_log_file_location: "/tmp/audit_logs"
      refresh: true
"""

RETURN = r"""
audit_log_settings:
  description: >
    Dictionary containing the configured audit log settings.
  returned: always
  type: dict
  contains:
    syslog_forwarding_setting:
      description: Syslog forwarding configuration details.
      type: dict
      contains:
        location_name:
          description: Location name for syslog forwarding.
          type: str
          sample: "datacenter1"
        syslog_servers:
          description: List of configured syslog servers.
          type: list
          elements: dict
          contains:
            index:
              description: Index of the syslog server.
              type: int
              sample: 1
            is_enabled:
              description: Whether the syslog server is enabled.
              type: bool
              sample: true
            server_name:
              description: Syslog server name or IP address.
              type: str
              sample: "syslog.example.com"
            port:
              description: Syslog server port number.
              type: int
              sample: 514
            transport_protocol:
              description: Transport protocol for syslog server.
              type: str
              sample: "UDP"
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_audit_log_settings import (
    SDSBAuditLogSettingsReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBAuditLogSettingArguments,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class SDSBAuditLogSettingsManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = SDSBAuditLogSettingArguments().audit_log_setting()
        self.logger.writeDebug(
            f"MOD:hv_sds_block_audit_log_setting:argument_spec= {self.argument_spec}"
        )
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )
        try:
            parameter_manager = SDSBParametersManager(self.module.params)
            self.state = parameter_manager.get_state()
            self.connection_info = parameter_manager.get_connection_info()
            self.spec = parameter_manager.get_audit_log_settings_spec()
            self.logger.writeDebug(f"MOD:spec= {self.spec}")
        except Exception as e:
            self.logger.writeError(f"An error occurred during initialization: {str(e)}")
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB Audit Log Settings Operation ===")
        audit_log_settings = None
        audit_log_data_extracted = None
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_reconciler = SDSBAuditLogSettingsReconciler(self.connection_info)
            audit_log_settings = sdsb_reconciler.reconcile_audit_log_settings(
                self.state, self.spec
            )

            self.logger.writeDebug(
                f"MOD:hv_sds_block_audit_log_setting:audit_log_settings= {audit_log_settings}"
            )

            # Handle download_audit_log state differently
            if self.state == "download_audit_log":
                # audit_log_settings is a string message for download
                response = {
                    "changed": self.connection_info.changed,
                    "messages": audit_log_settings,
                }
            else:
                response = {
                    "changed": self.connection_info.changed,
                    "audit_log_settings": audit_log_settings,
                }

            if registration_message:
                response["user_consent_required"] = registration_message

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB Audit Log Settings Operation ===")
            self.module.fail_json(msg=str(e))

        self.logger.writeInfo("=== End of SDSB Audit Log Settings Operation ===")
        self.module.exit_json(**response)


def main(module=None):
    obj_store = SDSBAuditLogSettingsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
