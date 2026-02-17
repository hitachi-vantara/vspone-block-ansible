#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_sds_block_event_log_setting
short_description: Manages Hitachi SDS block storage system event log settings.
description:
  - This module allows for the configuration of event log settings.
  - It supports updating syslog forwarding settings and email report settings.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/event_log_setting.yml)
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
    description: >
      The level of the event log settings task. Choices are C(present),
      C(import_smtp_certificate), and C(download_smtp_certificate).
    type: str
    required: false
    choices: ['present', 'import_smtp_certificate', 'download_smtp_certificate']
    default: 'present'
  spec:
    description: Specification for the event log settings task.
    type: dict
    required: false
    suboptions:
      smtp_root_certificate:
        description: SMTP server root certificate configuration.
          This is a required field when the state field is C(import_smtp_certificate) or C(download_smtp_certificate).
        type: dict
        required: false
        suboptions:
          certificate_path:
            description: Absolute path to the certificate file to import.
              Required when state is C(import_smtp_certificate).
            type: str
            required: false
          download_location:
            description: Directory path where the certificate will be downloaded.
              Required when state is C(download_smtp_certificate).
            type: str
            required: false
          target_smtp_server:
            description: Index of the SMTP server for which to import/download the certificate.
            type: int
            required: false
            choices: [1, 2]
            default: 1
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
                default: true
              server_name:
                description: Syslog server name or IP address.
                type: str
                required: true
              port:
                description: Syslog server port number.
                type: int
                required: false
                default: 514
              transport_protocol:
                description: Transport protocol for syslog server.
                type: str
                choices: ['UDP']
                required: false
                default: 'UDP'
      email_report_setting:
        description: Email report configuration.
        type: dict
        required: false
        suboptions:
          smtp_settings:
            description: List of SMTP server settings.
            type: list
            elements: dict
            required: false
            suboptions:
              index:
                description: Index of the SMTP server.
                type: int
                choices: [1, 2]
                required: true
              is_enabled:
                description: Whether the SMTP server is enabled.
                type: bool
                required: false
              smtp_server_name:
                description: SMTP server name or IP address.
                type: str
                required: false
              port:
                description: SMTP server port number.
                type: int
                required: false
              connection_encryption_type:
                description: Connection encryption type for SMTP.
                type: str
                choices: ['None', 'STARTTLS', 'SSL/TLS']
                required: false
              is_smtp_auth_enabled:
                description: Whether SMTP authentication is enabled.
                type: bool
                required: false
              smtp_auth_account:
                description: SMTP authentication account.
                type: str
                required: false
              smtp_auth_password:
                description: SMTP authentication password.
                type: str
                required: false
              from_address:
                description: Email from address.
                type: str
                required: false
              to_address1:
                description: Primary email recipient address.
                type: str
                required: false
              to_address2:
                description: Secondary email recipient address.
                type: str
                required: false
              to_address3:
                description: Tertiary email recipient address.
                type: str
                required: false
"""

EXAMPLES = """
- name: Configure event log settings with syslog forwarding
  hitachivantara.vspone_block.sds_block.hv_sds_block_event_log_setting:
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

- name: Configure event log settings with email reporting
  hitachivantara.vspone_block.sds_block.hv_sds_block_event_log_setting:
    state: present
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      email_report_setting:
        smtp_settings:
          - index: 1
            is_enabled: true
            smtp_server_name: "smtp.example.com"
            port: 587
            connection_encryption_type: "STARTTLS"
            is_smtp_auth_enabled: true
            smtp_auth_account: "eventlog@example.com"
            smtp_auth_password: "secure_password"
            from_address: "storage-alerts@example.com"
            to_address1: "admin@example.com"
            to_address2: "team@example.com"
            to_address3: ""

- name: Update syslog server configuration
  hitachivantara.vspone_block.sds_block.hv_sds_block_event_log_setting:
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

- name: Import SMTP root certificate for SMTP server 1
  hitachivantara.vspone_block.sds_block.hv_sds_block_event_log_setting:
    state: import_smtp_certificate
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      smtp_root_certificate:
        certificate_path: "/etc/ssl/certs/smtp_root_ca.pem"
        target_smtp_server: 1

- name: Import SMTP root certificate for SMTP server 2
  hitachivantara.vspone_block.sds_block.hv_sds_block_event_log_setting:
    state: import_smtp_certificate
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      smtp_root_certificate:
        certificate_path: "/etc/ssl/certs/smtp_root_ca.pem"
        target_smtp_server: 2

- name: Download SMTP root certificate from server 1
  hitachivantara.vspone_block.sds_block.hv_sds_block_event_log_setting:
    state: download_smtp_certificate
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      smtp_root_certificate:
        download_location: "/tmp/certificates"
        # target_smtp_server: 1  # Optional - defaults to 1

- name: Download SMTP root certificate from server 2
  hitachivantara.vspone_block.sds_block.hv_sds_block_event_log_setting:
    state: download_smtp_certificate
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      smtp_root_certificate:
        download_location: "/tmp/certificates"
        target_smtp_server: 2
"""

RETURN = r"""
event_log_settings:
  description: >
    Dictionary containing the configured event log settings.
  returned: always
  type: dict
  contains:
    syslogForwardingSetting:
      description: Syslog forwarding configuration details.
      type: dict
      contains:
        locationName:
          description: Location name for syslog forwarding.
          type: str
          sample: "datacenter1"
        syslogServers:
          description: List of configured syslog servers.
          type: list
          elements: dict
          contains:
            index:
              description: Index of the syslog server.
              type: int
              sample: 1
            isEnabled:
              description: Whether the syslog server is enabled.
              type: bool
              sample: true
            serverName:
              description: Syslog server name or IP address.
              type: str
              sample: "syslog.example.com"
            port:
              description: Syslog server port number.
              type: int
              sample: 514
            transportProtocol:
              description: Transport protocol for syslog server.
              type: str
              sample: "UDP"
    emailReportSetting:
      description: Email report configuration details.
      type: dict
      contains:
        smtpSettings:
          description: List of configured SMTP servers.
          type: list
          elements: dict
          contains:
            index:
              description: Index of the SMTP server.
              type: int
              sample: 1
            isEnabled:
              description: Whether the SMTP server is enabled.
              type: bool
              sample: true
            smtpServerName:
              description: SMTP server name or IP address.
              type: str
              sample: "smtp.example.com"
            port:
              description: SMTP server port number.
              type: int
              sample: 587
            connectionEncryptionType:
              description: Connection encryption type.
              type: str
              sample: "STARTTLS"
            isSmtpAuthEnabled:
              description: Whether SMTP authentication is enabled.
              type: bool
              sample: true
            smtpAuthAccount:
              description: SMTP authentication account.
              type: str
              sample: "eventlog@example.com"
            fromAddress:
              description: Email from address.
              type: str
              sample: "storage-alerts@example.com"
            toAddress1:
              description: Primary recipient address.
              type: str
              sample: "admin@example.com"
            toAddress2:
              description: Secondary recipient address.
              type: str
              sample: "team@example.com"
            toAddress3:
              description: Tertiary recipient address.
              type: str
              sample: ""
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_event_log_settings import (
    SDSBEventLogSettingsReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBEventLogSettingArguments,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class SDSBEventLogSettingsManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = SDSBEventLogSettingArguments().event_log_setting()
        self.logger.writeDebug(
            f"MOD:hv_sds_block_event_log_setting:argument_spec= {self.argument_spec}"
        )
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=False,
        )
        try:
            parameter_manager = SDSBParametersManager(self.module.params)
            self.state = parameter_manager.get_state()
            self.connection_info = parameter_manager.get_connection_info()
            self.spec = parameter_manager.get_event_log_settings_spec()
            self.logger.writeDebug(f"MOD:spec= {self.spec}")
        except Exception as e:
            self.logger.writeError(f"An error occurred during initialization: {str(e)}")
            self.module.fail_json(msg=str(e))

    def apply(self):
        self.logger.writeInfo("=== Start of SDSB Event Log Settings Operation ===")
        event_log_settings = None
        event_log_data_extracted = None
        registration_message = validate_ansible_product_registration()

        try:
            sdsb_reconciler = SDSBEventLogSettingsReconciler(self.connection_info)
            event_log_settings = sdsb_reconciler.reconcile_event_log_settings(
                self.state, self.spec
            )

            self.logger.writeDebug(
                f"MOD:hv_sds_block_event_log_setting:event_log_settings= {event_log_settings}"
            )

            # Handle download_event_log, import_smtp_certificate, and download_smtp_certificate states differently
            if (
                self.state == "import_smtp_certificate"
                or self.state == "download_smtp_certificate"
            ):
                response = {
                    "changed": self.connection_info.changed,
                    "messages": event_log_settings,
                }
            else:
                output_dict = event_log_settings.camel_to_snake_dict()
                response = {
                    "changed": self.connection_info.changed,
                    "data": output_dict,
                }

            if registration_message:
                response["user_consent_required"] = registration_message

        except Exception as e:
            self.logger.writeException(e)
            self.logger.writeInfo("=== End of SDSB Event Log Settings Operation ===")
            self.module.fail_json(msg=str(e))

        self.logger.writeInfo("=== End of SDSB Event Log Settings Operation ===")
        self.module.exit_json(**response)


def main(module=None):
    obj_store = SDSBEventLogSettingsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
