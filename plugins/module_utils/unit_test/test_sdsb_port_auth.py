import os
import sys
import unittest
from dataclasses import dataclass, asdict

# Add the parent directory to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)


from reconciler.sdsb_port_auth import SDSBPortAuthReconciler
from reconciler.sdsb_properties_extractor import ChapUserPropertiesExtractor
from model.common_base_models import ConnectionInfo
from model.sdsb_port_auth_models import PortAuthSpec
from common.hv_log import Log

logger = Log()


class TestSdsbPortAuth(unittest.TestCase):

    def setUp(self):
        connection_info = {
            "address": "10.76.47.55",
            # "address": "172.25.58.151",
            "username": "admin",
            "password": "vssb-789",
            "connection_type": "direct",
        }
        self.connection_info = ConnectionInfo(**connection_info)
        self.recon = SDSBPortAuthReconciler(self.connection_info)
        # logger.writeDebug('=== Create Compute Node ===')

    def xtest_get_chap_users(self):
        spec = {
            # "id": "",
            # "target_chap_user": ""
        }
        spec = ChapUserFactSpec(**spec)
        compute_nodes = self.recon.get_chap_users(spec)

        output_dict = compute_nodes.data_to_list()

        new_data = ChapUserPropertiesExtractor().extract(output_dict)
        print(new_data)
        self.assertIsNotNone(compute_nodes)

    def test_port_auth(self):
        state = "present"
        spec = {
            "port_name": "iqn.1994-04.jp.co.hitachi:rsd.sph.t.0a85a.000",
            "authentication_mode" : "CHAP",
            "target_chap_users": ["RAHUL-1112"]
        }
        spec = PortAuthSpec(**spec)
        print(spec)
        volume = self.recon.reconcile_port_auth(state, spec)
        print(volume)

        self.assertIsNotNone(volume)


    def xtest_update_chap_user(self):
        state = "present"
        spec = {
            "id": "d95e8ade-14c4-42b2-ae68-280eed4d87a0",
            "target_chap_user_name" : "RAHUL-1112",
            "target_chap_secret": "RAHUL-1111111"
        }
        spec = ChapUserSpec(**spec)
        print(spec)
        volume = self.recon.reconcile_chap_user(state, spec)
        print(volume)

        self.assertIsNotNone(volume)
if __name__ == "__main__":
    unittest.main()