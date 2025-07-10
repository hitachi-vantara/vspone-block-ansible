#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_snmp_settings_facts
short_description: Retrieves SNMP configuration from Hitachi VSP storage systems.
description:
  - This module retrieves SNMP settings (v1, v2c, v3) from Hitachi VSP storage systems.
  - For example usage, visit
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/snmp.yml)
version_added: '4.0.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.8
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: full
extends_documentation_fragment:
  - hitachivantara.vspone_block.common.gateway_note
  - hitachivantara.vspone_block.common.connection_info
"""

EXAMPLES = """
- name: Enable SNMP agent and configure SNMPv2c with trap destinations
  hitachivantara.vspone_block.vsp.hv_snmp_settings_facts:
    connection_info:
      address: 192.0.2.10
      username: admin
      password: secret
"""
RETURN = """
ansible_facts:
  description: SNMP settings and related information retrieved from the storage system.
  returned: always
  type: dict
  contains:
    snmp_settings:
      description: SNMP configuration details.
      type: dict
      sample:
        isSNMPAgentEnabled: true
        snmpVersion: v3
        sendingTrapSetting:
          snmpv3Settings:
            - userName: MyRestSNMPUser1
              sendTrapTo: 192.0.2.100
              authentication:
                protocol: SHA
                password: ""
                encryption:
                  protocol: AES
                  key: ""
            - userName: MyRestSNMPUser2
              sendTrapTo: 192.0.2.200
        requestAuthenticationSetting:
          snmpv3Settings:
            - userName: MyRestSNMPUser3
              authentication:
                protocol: MD5
                password: ""
                encryption:
                  protocol: DES
                  key: ""
        systemGroupInformation:
          storageSystemName: VSP_G700
          contact: confmanager.@example.com
          location: Data Center 1F
        snmpEngineID: "0x80000074046361336663353061"
"""


from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPSNMPArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_initial_system_config_reconciler import (
    InitialSystemConfigReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class SNMPSettingsFacts:
    """
    Class representing SNMPv3 settings.
    """

    def __init__(self):

        self.logger = Log()
        self.argument_spec = VSPSNMPArguments().snmp_facts()

        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )
        try:
            self.parameter_manager = VSPParametersManager(self.module.params)
        except Exception as e:
            self.logger.writeError(f"An error occurred during initialization: {str(e)}")
            self.module.fail_json(msg=str(e))

    def apply(self):

        self.logger.writeInfo("=== Start of SNMP Settings Facts ===")
        registration_message = validate_ansible_product_registration()

        try:
            response = InitialSystemConfigReconciler(
                self.parameter_manager.connection_info
            ).snmp_facts()

        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of SNMP Settings Facts ===")
            self.module.fail_json(msg=str(e))

        data = {
            "snmp_settings": response,
        }
        if registration_message:
            data["user_consent_required"] = registration_message

        self.logger.writeInfo(f"{data}")
        self.logger.writeInfo("=== End of SNMP Settings Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)


def main():
    obj_store = SNMPSettingsFacts()
    obj_store.apply()


if __name__ == "__main__":
    main()
