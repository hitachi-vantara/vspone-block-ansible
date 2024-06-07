import os
import sys
import unittest

# Add the parent directory to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)


from reconciler.vsp_parity_group import (
    VSPParityGroupReconciler,
    VSPParityGroupCommonPropertiesExtractor,
)
from model.vsp_parity_group_models import ParityGroupFactSpec
from model.common_base_models import ConnectionInfo
from dataclasses import asdict


class TestVspStorageSystem(unittest.TestCase):

    def setUp(self):
        connection_info = {
            "address": "172.25.44.126",
            "username": "maintenance",
            "password": "raid-maintenance",
            "connection_type": "direct",
            "subscriber_id": "",
        }

        # connection_info =  {
        #                         "address":"172.25.45.102",
        #                         "username":"ucpa",
        #                         "password":"Hitachi1",
        #                         "connection_type":"direct"}

        self.connection_info = ConnectionInfo(**connection_info)

    def test_get_all_parity_groups(self):
        parity_groups = VSPParityGroupReconciler(
            self.connection_info
        ).get_all_parity_groups()
        parity_groups_extracted = (
            VSPParityGroupCommonPropertiesExtractor().extract_all_parity_groups(
                parity_groups.data_to_list()
            )
        )
        print(parity_groups_extracted)
        if parity_groups is None:
            print("Parity groups result is None.")
        self.assertIsNotNone(parity_groups)

    def test_get_parity_group(self):
        spec_dict = {
            "parity_group_id": "1-1",
        }
        spec = ParityGroupFactSpec(**spec_dict)
        parity_group = VSPParityGroupReconciler(self.connection_info).get_parity_group(
            spec.parity_group_id
        )
        parity_group_extracted = (
            VSPParityGroupCommonPropertiesExtractor().extract_parity_group(
                parity_group.to_dict()
            )
        )
        print(parity_group_extracted)
        if parity_group is None:
            print("Parity group result is None.")
        self.assertIsNotNone(parity_group)


if __name__ == "__main__":
    unittest.main()
