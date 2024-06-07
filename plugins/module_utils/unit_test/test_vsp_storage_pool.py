import os
import sys
import unittest

# Add the parent directory to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)


from reconciler.vsp_storage_pool import (
    VSPStoragePoolReconciler,
    VSPStoragePoolCommonPropertiesExtractor,
)
from model.vsp_storage_pool_models import PoolFactSpec
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
        # self.serial = 810045
        self.serial = 715036

    def test_get_all_storage_pools(self):
        storage_pools = VSPStoragePoolReconciler(
            self.connection_info
        ).get_all_storage_pools()
        storage_pools_extracted = (
            VSPStoragePoolCommonPropertiesExtractor().extract_all_pools(
                storage_pools.data_to_list()
            )
        )
        print(storage_pools_extracted)
        if storage_pools is None:
            print("storage pool result is None.")
        self.assertIsNotNone(storage_pools)

    def test_get_storage_pool(self):
        spec_dict = {
            "pool_id": 0,
        }
        spec = PoolFactSpec(**spec_dict)
        storage_pool = VSPStoragePoolReconciler(self.connection_info).get_storage_pool(
            spec
        )
        storage_pool_extracted = VSPStoragePoolCommonPropertiesExtractor().extract_pool(
            storage_pool.to_dict()
        )
        print(storage_pool_extracted)
        if storage_pool is None:
            print("storage pool result is None.")
        self.assertIsNotNone(storage_pool)


if __name__ == "__main__":
    unittest.main()
