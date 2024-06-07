import os
import sys
import unittest
from dataclasses import dataclass, asdict

# Add the parent directory to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)


from reconciler.vsp_host_group import (
    VSPHostGroupReconciler,
    VSPHostGroupCommonPropertiesExtractor,
)
from model.vsp_host_group_models import *
from model.common_base_models import ConnectionInfo


class TestVspHostGroup(unittest.TestCase):

    def setUp(self):
        connection_info = {
            "address": "172.25.44.126",
            "username": "maintenance",
            "password": "raid-maintenance",
            "connection_type": "direct",
        }

        self.ConnectionInfo = ConnectionInfo(**connection_info)
        self.serial = 715036

    def xtest_get_host_group(self):
        spec = {
            "ports": ["CL1-A"],
        }
        spec = GetHostGroupSpec(**spec)
        host_group = VSPHostGroupReconciler(
            self.ConnectionInfo, self.serial
        ).get_host_groups(spec)
        host_group_to_dict = [asdict(ob) for ob in host_group]
        new_data = VSPHostGroupCommonPropertiesExtractor(self.serial).extract(
            host_group_to_dict
        )
        print(new_data)
        self.assertIsNotNone(host_group)

    def test_create_host_group(self):
        spec = {
            "state": "present",
            "name": "test-ansible-hg-thinh-1",
            "ports": ["CL1-A"],
        }

        state = "present"
        spec = HostGroupSpec(**spec)
        host_group = VSPHostGroupReconciler(
            self.ConnectionInfo, self.serial
        ).host_group_reconcile(state, spec)
        host_group_to_dict = asdict(host_group)
        new_data = VSPHostGroupCommonPropertiesExtractor(self.serial).extract_dict(
            host_group_to_dict
        )
        print(new_data)
        self.assertIsNotNone(host_group)

    def test_delete_host_group(self):
        spec = {
            "state": "absent",
            "name": "test-ansible-hg-thinh-1",
            "ports": ["CL1-A"],
        }

        state = "absent"
        spec = HostGroupSpec(**spec)
        host_group = VSPHostGroupReconciler(
            self.ConnectionInfo, self.serial
        ).host_group_reconcile(state, spec)
        host_group_to_dict = asdict(host_group)
        new_data = VSPHostGroupCommonPropertiesExtractor(self.serial).extract_dict(
            host_group_to_dict
        )
        print(new_data)
        self.assertIsNotNone(host_group)

    def test_delete_host_group_with_delete_all_luns(self):
        spec = {
            "state": "absent",
            "name": "vinh-test-host-group-002",
            "port": "CL8-B",
            "should_delete_all_luns": True,
        }

        state = "absent"
        spec = HostGroupSpec(**spec)
        host_group = VSPHostGroupReconciler(
            self.ConnectionInfo, self.serial
        ).host_group_reconcile(state, spec)
        host_group_to_dict = asdict(host_group)
        new_data = VSPHostGroupCommonPropertiesExtractor(self.serial).extract_dict(
            host_group_to_dict
        )
        print(new_data)
        self.assertIsNotNone(host_group)


if __name__ == "__main__":
    unittest.main()
