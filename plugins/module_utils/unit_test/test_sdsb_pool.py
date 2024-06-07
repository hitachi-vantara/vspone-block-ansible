import os
import sys
import unittest
from dataclasses import dataclass, asdict

# Add the parent directory to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)


from gateway.sdsb_pool_gateway import SDSBPoolDirectGateway
from reconciler.sdsb_chap_users import SDSBChapUserReconciler
from reconciler.sdsb_properties_extractor import ChapUserPropertiesExtractor
from model.common_base_models import ConnectionInfo
from model.sdsb_chap_user_models import ChapUserFactSpec, ChapUserSpec
from common.hv_log import Log

logger = Log()


class TestSdsbChapUser(unittest.TestCase):

    def setUp(self):
        connection_info = {
            "address": "10.76.47.55",
            # "address": "172.25.58.151",
            "username": "admin",
            "password": "vssb-789",
            "connection_type": "direct",
        }
        self.connection_info = ConnectionInfo(**connection_info)
        self.gw = SDSBPoolDirectGateway(self.connection_info)
        # logger.writeDebug('=== Create Compute Node ===')

    def xtest_get_pools(self):
        spec = {
            # "id": "",
            # "target_chap_user": ""
        }
        pools = self.gw.get_pools()
        print(pools)

        # output_dict = compute_nodes.data_to_list()

        # new_data = ChapUserPropertiesExtractor().extract(output_dict)
        # print(new_data)
        # self.assertIsNotNone(compute_nodes)

    def  test_get_pool_by_name(self):
        name= "SP01"
        pool = self.gw.get_pool_by_name(name)
        print(pool)


if __name__ == "__main__":
    unittest.main()