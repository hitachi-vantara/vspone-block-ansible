import os
import sys
import unittest

# Add the parent directory to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)


from reconciler.sdsb_storage_system import SDSBStorageSystemReconciler
from model.common_base_models import ConnectionInfo
from dataclasses import asdict


class TestSdsbpStorageSystem(unittest.TestCase):

    def setUp(self):
        connection_info = {
            "address": "10.76.47.55",
            "username": "admin",
            "password": "vssb-789",
            "connection_type": "direct",
        }

        self.connection_info = ConnectionInfo(**connection_info)

    def test_sdsb_get_storage_system(self):
        sdsb_storage_system = SDSBStorageSystemReconciler(
            self.connection_info
        ).sdsb_get_storage_system()
        print(asdict(sdsb_storage_system))
        if sdsb_storage_system is None:
            print("storage system result is None.")
        self.assertIsNotNone(sdsb_storage_system)


if __name__ == "__main__":
    unittest.main()
