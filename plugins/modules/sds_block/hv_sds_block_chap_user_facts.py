#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_sds_block_chap_user_facts
short_description: Retrieves information about Hitachi SDS block storage system CHAP users.
description:
  - This module retrieves information about CHAP users.
  - It provides details about a CHAP user such as initiator CHAP user name, target CHAP user name and ID.
  - For examples go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/sds_block_direct/chap_user_facts.yml)
version_added: '3.0.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
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
    description: Specification for retrieving CHAP user information.
    type: dict
    required: false
    suboptions:
      id:
        type: str
        description: ID of the CHAP user to retrieve information for.
        required: false
      target_chap_user_name:
        type: str
        description: Target CHAP user name to retrieve information for.
        required: false
"""

EXAMPLES = """
- name: Retrieve information about all CHAP users
  hv_sds_block_chap_user_facts:
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"

- name: Retrieve information about a specific CHAP user by ID
  hv_sds_block_chap_user_facts:
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"
    spec:
      id: "464e1fd1-9892-4134-866c-6964ce786676"

- name: Retrieve information about a specific CHAP user by name
  hv_sds_block_chap_user_facts:
    connection_info:
      address: vssb.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"
    spec:
      target_chap_user_name: "chapuser1"
"""

RETURN = """
chap_users:
  description: A list of CHAP users.
  returned: always
  type: list
  elements: dict
  sample: [
    {
      "id": "464e1fd1-9892-4134-866c-6964ce786676",
      "initiator_chap_user_name": "chapuser1",
      "target_chap_user_name": "newchapuser2"
    }
  ]
"""
from ansible.module_utils.basic import AnsibleModule

from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.sdsb_utils import (
    SDSBChapUserArguments,
    SDSBParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_log import (
    Log,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_properties_extractor import (
    ChapUserPropertiesExtractor,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler.sdsb_chap_users import (
    SDSBChapUserReconciler,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.ansible_common import (
    validate_ansible_product_registration,
)

logger = Log()


class SDSBChapUserFactsManager:
    def __init__(self):

        self.argument_spec = SDSBChapUserArguments().chap_user_facts()
        logger.writeDebug(
            f"MOD:hv_sds_block_chap_user_facts:argument_spec= {self.argument_spec}"
        )
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        parameter_manager = SDSBParametersManager(self.module.params)
        self.connection_info = parameter_manager.get_connection_info()
        self.spec = parameter_manager.get_chap_user_fact_spec()
        logger.writeDebug(f"MOD:hv_sds_block_chap_user_facts:spec= {self.spec}")

    def apply(self):
        chap_users = None
        chap_users_data_extracted = None
        registration_message = validate_ansible_product_registration()

        logger.writeInfo(f"{self.connection_info.connection_type} connection type")
        try:
            sdsb_reconciler = SDSBChapUserReconciler(self.connection_info)
            chap_users = sdsb_reconciler.get_chap_users(self.spec)

            logger.writeDebug(
                f"MOD:hv_sds_block_chap_user_facts:chap_users= {chap_users}"
            )
            output_dict = chap_users.data_to_list()
            chap_users_data_extracted = ChapUserPropertiesExtractor().extract(
                output_dict
            )

        except Exception as e:
            self.module.fail_json(msg=str(e))

        data = {"chap_users": chap_users_data_extracted}
        if registration_message:
            data["user_consent_required"] = registration_message
        self.module.exit_json(**data)


def main(module=None):
    obj_store = SDSBChapUserFactsManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
