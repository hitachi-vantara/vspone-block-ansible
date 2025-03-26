#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright: (c) 2021, [ Hitachi Vantara ]
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function

__metaclass__ = type


DOCUMENTATION = """
---
module: hv_shadow_image_pair_facts
short_description: Retrieves information about shadow image pairs from Hitachi VSP storage systems.
description:
  - This module retrieves information about shadow image pairs from Hitachi VSP storage systems.
  - It provides details about shadow image pair such as ID, status and other relevant information.
  - This module is supported for both C(direct) and C(gateway) connection types.
  - For C(direct) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_direct/shadow_image_pair_facts.yml)
  - For C(gateway) connection type examples, go to URL
    U(https://github.com/hitachi-vantara/vspone-block-ansible/blob/main/playbooks/vsp_uai_gateway/shadow_image_pair_facts.yml)
version_added: '3.0.0'
author:
  - Hitachi Vantara LTD (@hitachi-vantara)
requirements:
  - python >= 3.8
attributes:
  check_mode:
    description: Determines if the module should run in check mode.
    support: full
options:
  storage_system_info:
    description: Information about the Hitachi storage system. This field is required for gateway connection type only.
    type: dict
    required: false
    suboptions:
      serial:
        description: Serial number of the Hitachi storage system.
        type: str
        required: false
  connection_info:
    description: Information required to establish a connection to the storage system.
    required: true
    type: dict
    suboptions:
      address:
        description: IP address or hostname of either the UAI gateway (if connection_type is C(gateway)) or
          the storage system (if connection_type is C(direct)).
        type: str
        required: true
      username:
        description: Username for authentication.This field is valid for C(direct) connection type only, and it is a required field.
        type: str
        required: false
      password:
        description: Password for authentication.This field is valid for C(direct) connection type only, and it is a required field.
        type: str
        required: false
      connection_type:
        description: Type of connection to the storage system.
        type: str
        required: false
        choices: ['gateway', 'direct']
        default: 'direct'
      subscriber_id:
        description: This field is valid for C(gateway) connection type only. This is an optional field and only needed to support multi-tenancy environment.
        type: str
        required: false
      api_token:
        description: Token value to access UAI C(gateway) (required for authentication either 'username,password' or api_token).
        type: str
        required: false
  spec:
    description: Specification for retrieving shadow image pair information.
    type: dict
    required: false
    suboptions:
      primary_volume_id:
        type: int
        description: Primary volume id.
        required: false
"""

EXAMPLES = """
- name: Retrieve information about all shadow image pairs for direct connection type
  hitachivantara.vspone_block.vsp.hv_shadow_image_pair_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"

    storage_system_info:
      serial: 811150

- name: Retrieve information about a specific shadow image pair for direct connection type
  hitachivantara.vspone_block.vsp.hv_shadow_image_pair_facts:
    connection_info:
      address: storage1.company.com
      username: "admin"
      password: "password"
      connection_type: "direct"
    spec:
      primary_volume_id: 274
"""

RETURN = """
ansible_facts:
  description: List of shadow image pairs.
  returned: success
  type: dict
  contains:
    data:
      description: List of shadow image pairs.
      returned: success
      type: list
      elements: dict
      contains:
        consistency_group_id:
          description: Consistency group ID.
          type: int
          sample: -1
        copy_pace_track_size:
          description: Copy pace track size.
          type: str
          sample: "MEDIUM"
        copy_rate:
          description: Copy rate.
          type: int
          sample: 100
        entitlement_status:
          description: Entitlement status.
          type: str
          sample: "assigned"
        mirror_unit_id:
          description: Mirror unit ID.
          type: int
          sample: -1
        partner_id:
          description: Partner ID.
          type: str
          sample: "partner123"
        primary_hex_volume_id:
          description: Primary hex volume ID.
          type: str
          sample: "00:01:12"
        primary_volume_id:
          description: Primary volume ID.
          type: int
          sample: 274
        resource_id:
          description: Resource ID.
          type: str
          sample: "localpair-2749fed78e8d23a61ed17a8af71c85f8"
        secondary_hex_volume_id:
          description: Secondary hex volume ID.
          type: str
          sample: "00:01:17"
        secondary_volume_id:
          description: Secondary volume ID.
          type: int
          sample: 279
        status:
          description: Status of the shadow image pair.
          type: str
          sample: "PAIR"
        storage_serial_number:
          description: Storage serial number.
          type: str
          sample: "811150"
        subscriber_id:
          description: Subscriber ID.
          type: str
          sample: "subscriber123"
        svol_access_mode:
          description: SVol access mode.
          type: str
          sample: "READONLY"
"""


from ansible.module_utils.basic import AnsibleModule
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.hv_constants import (
    ConnectionTypes,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.common.vsp_utils import (
    VSPShadowImagePairArguments,
    VSPParametersManager,
)
from ansible_collections.hitachivantara.vspone_block.plugins.module_utils.reconciler import (
    vsp_shadow_image_pair_reconciler,
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


class VSPShadowImagePairManager:
    def __init__(self):

        self.logger = Log()
        self.argument_spec = (
            VSPShadowImagePairArguments().get_all_shadow_image_pair_fact()
        )
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True,
        )

        self.params_manager = VSPParametersManager(self.module.params)
        self.spec = self.params_manager.set_shadow_image_pair_fact_spec()
        self.logger.writeInfo(f"{self.spec} SPEC")

    def apply(self):
        self.logger.writeInfo("=== Start of Shadow Image Pair Facts ===")
        registration_message = validate_ansible_product_registration()
        shadow_image_pair_data = None

        try:

            shadow_image_pair_data = self.gateway_shadow_image_pair_read()

        except Exception as e:
            self.logger.writeError(str(e))
            self.logger.writeInfo("=== End of Shadow Image Pair Facts ===")
            self.module.fail_json(msg=str(e))

        data = {"data": shadow_image_pair_data}

        if not shadow_image_pair_data:
            if self.spec.pvol is not None:
                data["comment"] = "Data not available with pvol " + str(self.spec.pvol)
            else:
                data["comment"] = "Couldn't read shadow image pairs. "
        if registration_message:
            data["user_consent_required"] = registration_message

        self.logger.writeInfo(f"{data}")
        self.logger.writeInfo("=== End of Shadow Image Pair Facts ===")
        self.module.exit_json(changed=False, ansible_facts=data)

    def gateway_shadow_image_pair_read(self):

        reconciler = vsp_shadow_image_pair_reconciler.VSPShadowImagePairReconciler(
            self.params_manager.connection_info,
            self.params_manager.storage_system_info.serial,
        )
        if (
            self.params_manager.connection_info.connection_type.lower()
            == ConnectionTypes.GATEWAY
        ):
            oob = reconciler.is_out_of_band()
            if oob is True:
                raise ValueError(ModuleMessage.OOB_NOT_SUPPORTED.value)

        result = reconciler.shadow_image_pair_facts(self.spec)
        return result


def main():
    obj_store = VSPShadowImagePairManager()
    obj_store.apply()


if __name__ == "__main__":
    main()
