#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

DOCUMENTATION = """
---
module: hv_session_facts
short_description: Retrieves information about sessions on VSP block storage systems.
description:
  - This module retrieves information about sessions.
  - It provides details about a session.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/session_facts.yml)
version_added: '4.6.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.9
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: full
extends_documentation_fragment:
  - hitachivantara.vspone_block.common.connection_with_type
options:
  spec:
    description: Specification for retrieving session information.
    type: dict
    required: false
    suboptions:
      id:
        description: ID of the session to retrieve information for.
        type: int
        required: false
      token:
        description: Authentication token for the session. Required when specifying 'id'.
        type: str
        required: false
"""

EXAMPLES = """
- name: Get all Sessions
  hitachivantara.vspone_block.vsp.hv_session_facts:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"

- name: Get Session by ID
  hitachivantara.vspone_block.vsp.hv_session_facts:
    connection_info:
      address: sdsb.company.com
      username: "admin"
      password: "password"
    spec:
      id: 9
      token: "d7c7bd35d3854a9f973d934800fb70ab"
"""

RETURN = r"""
ansible_facts:
  description: Facts collected by the module.
  returned: always
  type: dict
  contains:
    sessions:
      description: List of active and historical user sessions.
      returned: always
      type: list
      elements: dict
      contains:
        session_id:
          description: Unique identifier of the session.
          type: int
          sample: 15851
        user_id:
          description: User name associated with the session.
          type: str
          sample: ucpa
        ip_address:
          description: IP address from which the session was created.
          type: str
          sample: 172.25.94.70
        created_time:
          description: Session creation timestamp in ISO 8601 format.
          type: str
          sample: "2026-01-18T17:33:12Z"
        last_access_time:
          description: Timestamp of the last access for the session. Empty if the information is not available.
          type: str
          sample: ""
"""

from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.vsp_session import (
    VSPSessionReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPSessionArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)


class VSPSessionFactsManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = VSPSessionArguments().session_facts()
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        parameter_manager = VSPParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()
        self.spec = parameter_manager.get_session_fact_spec()

    def apply(self):
        self.logger.writeInfo("=== Start of VSP Session Facts ===")
        registration_message = validate_ansible_product_registration()

        try:
            vsp_reconciler = VSPSessionReconciler(self.connection_info)
            sessions = vsp_reconciler.get_session_facts(self.spec)

            # self.logger.writeDebug(f"MOD:hv_session_facts:session= {sessions}")

        except Exception as e:
            self.logger.writeInfo("=== End of VSP Session Facts ===")
            self.module.fail_json(msg=str(e))
        data = {"sessions": sessions}
        if self.spec.comment:
            data["comment"] = self.spec.comment

        if registration_message:
            data["user_consent_required"] = registration_message
        self.logger.writeInfo("=== End of VSP Session Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)


def main(module=None):
    obj_store = VSPSessionFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
