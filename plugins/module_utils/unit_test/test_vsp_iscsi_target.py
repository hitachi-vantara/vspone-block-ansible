import os
import sys
import unittest
from dataclasses import dataclass, asdict

# Add the parent directory to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)


from reconciler.vsp_iscsi_target import *
from model.vsp_iscsi_target_models import *
from model.common_base_models import ConnectionInfo


class TestVspIscsiTarget(unittest.TestCase):

    def setUp(self):
        connection_info = {
            "address": "172.25.44.126",
            "username": "maintenance",
            "password": "raid-maintenance",
            "connection_type": "direct",
        }

        self.ConnectionInfo = ConnectionInfo(**connection_info)
        self.serial = 715036

    def test_get_iscsi_target(self):
        spec = {
            "ports": ["CL4-C"],
        }
        spec = IscsiTargetFactSpec(**spec)
        iscsi_targets = VSPIscsiTargetReconciler(
            self.ConnectionInfo, self.serial
        ).get_iscsi_targets(spec)
        iscsi_target_to_list = iscsi_targets.data_to_list()
        new_data = VSPIscsiTargetCommonPropertiesExtractor().extract(
            iscsi_target_to_list
        )
        print(new_data)
        self.assertIsNotNone(iscsi_targets)


if __name__ == "__main__":
    unittest.main()
