import os
import sys
import unittest
import json
from dataclasses import dataclass, asdict

# Add the parent directory to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)


from reconciler.sdsb_port import SDSBPortReconciler
from reconciler.sdsb_properties_extractor import (
    ComputePortPropertiesExtractor,
    PortDetailPropertiesExtractor,
)
from model.common_base_models import ConnectionInfo
from model.sdsb_port_models import (
    PortFactSpec,
)
from common.hv_log import Log

logger = Log()

class TestSdsbComputeNode(unittest.TestCase):

    def setUp(self):
        connection_info = {
            "address": "10.76.47.55",
            # "address": "172.25.58.151",
            "username": "admin",
            "password": "vssb-789",
            "connection_type": "direct",
        }
        self.connection_info = ConnectionInfo(**connection_info)
        self.recon = SDSBPortReconciler(self.connection_info)
        

    def test_get_compute_ports(self):
        spec = {
            "nicknames": ["000-iSCSI-000"]
            # "names" : ["p1-compute-node", "RD-compute-node-111"]
            # "hba_name": "iqn.1992-01.com.company:server"
            # "vps_name": "(system)"
        }
        spec = PortFactSpec(**spec)
        compute_ports = self.recon.get_compute_ports(spec)
        # print(compute_ports)
        output_dict = compute_ports.data_to_list()
        # print(output_dict)
        # x  = json.dumps(compute_ports, default=lambda o: o.__dict__)
        # print(x)
        #new_data = ComputePortPropertiesExtractor().extract(output_dict)
        new_data = PortDetailPropertiesExtractor().extract(output_dict)
        
        print(new_data)
        self.assertIsNotNone(compute_ports)

if __name__ == "__main__":
    unittest.main()