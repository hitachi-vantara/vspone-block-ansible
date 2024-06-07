import os
import sys
import unittest

# Add the parent directory to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)


from reconciler.vsp_storage_system import (
    VSPStorageSystemReconciler,
    VSPStorageSystemCommonPropertiesExtractor,
)
from model.vsp_storage_system_models import StorageSystemFactSpec
from model.common_base_models import ConnectionInfo
from dataclasses import asdict


class TestVspStorageSystem(unittest.TestCase):

    def setUp(self):
        # connection_info =  {
        #                         "address":"172.25.44.126",
        #                         "username":"maintenance",
        #                         "password":"raid-maintenance",
        #                         "connection_type":"direct"}

        connection_info = {
            "address": "172.25.45.102",
            "username": "ucpa",
            "password": "Hitachi1",
            "connection_type": "direct",
        }

        self.connection_info = ConnectionInfo(**connection_info)
        self.serial = 810045
        # self.serial = 715036

    def test_get_storage_system(self):
        spec = {
            # "query":['journalPools','ports','pools','quorumdisks','freeLogicalUnitList'],
            "query": [],
        }
        spec = StorageSystemFactSpec(**spec)
        storage_system = VSPStorageSystemReconciler(
            self.connection_info, self.serial
        ).get_storage_system(spec)
        storage_system_extracted = VSPStorageSystemCommonPropertiesExtractor().extract(
            asdict(storage_system)
        )
        print(storage_system_extracted)
        if storage_system is None:
            print("storage system result is None.")
        self.assertIsNotNone(storage_system)


if __name__ == "__main__":
    unittest.main()
