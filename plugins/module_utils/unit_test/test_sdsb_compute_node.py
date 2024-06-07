import os
import sys
import unittest
from dataclasses import dataclass, asdict

# Add the parent directory to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)


from reconciler.sdsb_compute_node import SDSBComputeNodeReconciler
from reconciler.sdsb_properties_extractor import (
    ComputeNodePropertiesExtractor,
    ComputePortPropertiesExtractor,
    ComputeNodeAndVolumePropertiesExtractor,
)
from model.common_base_models import ConnectionInfo
from model.sdsb_compute_node_models import (
    ComputeNodeFactSpec,
    ComputeNodeSpec,
)
from model.sdsb_port_models import PortFactSpec
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
        self.recon = SDSBComputeNodeReconciler(self.connection_info)
        # logger.writeDebug('=== Create Compute Node ===')

    def test_get_compute_nodes(self):
        spec = {
            # "names" : []
            "names": ["asishtest", "computeA1"],
            # "names" : ["p1-compute-node", "RD-compute-node-111"]
            # "hba_name": "iqn.1991-05.com.hitachi:test-iscsi-iqn0002",
            # "vps_name": "(system)"
        }
        spec = ComputeNodeFactSpec(**spec)
        compute_nodes = self.recon.get_compute_nodes(spec)
        print(compute_nodes)

        output_dict = compute_nodes.data_to_list()

        # new_data = ComputeNodePropertiesExtractor().extract(output_dict)

        new_data = ComputeNodeAndVolumePropertiesExtractor().extract(output_dict)

        
        print(new_data)
        self.assertIsNotNone(compute_nodes)

    def xtest_get_compute_ports(self):
        spec = {
            "nicknames": ["000-iSCSI-000", "001-iSCSI-001"]
            # "names" : ["p1-compute-node", "RD-compute-node-111"]
            # "hba_name": "iqn.1992-01.com.company:server"
            # "vps_name": "(system)"
        }
        spec = PortFactSpec(**spec)
        compute_ports = self.recon.get_compute_ports(spec)
        output_dict = compute_ports.data_to_list()
        new_data = ComputePortPropertiesExtractor().extract(output_dict)
        print(new_data)
        self.assertIsNotNone(compute_ports)

    def xtest_get_compute_port_ids(self):
        spec = {
            # "names" : []
            # "names" : ["RD-compute-node-111"],
            # "names" : ["p1-compute-node", "RD-compute-node-111"]
            # "hba_name": "iqn.1992-01.com.company:server"
            # "vps_name": "(system)"
        }
        spec = ComputeNodeFactSpec(**spec)
        compute_port_ids = self.recon.get_compute_port_ids()
        # output_dict = compute_nodes.data_to_list()
        # new_data = ComputeNodePropertiesExtractor().extract(output_dict)
        print(compute_port_ids)
        self.assertIsNotNone(compute_port_ids)

    def xtest_create_compute_node_add_iqn_initiators(self):
        state = "present"
        spec = {
            "name": "RD-compute-node-4",
            "os_type": "VMware",
            # "names" : ["RD-compute-node-111"],
            # "names" : ["p1-compute-node", "RD-compute-node-111"]
            "state": "add_iscsi_initiator",
            "iscsi_initiators": [
                "iqn.1991-05.com.hitachi:test-iscsi-iqn3",
                "iqn.1991-05.com.hitachi:test-iscsi-iqn4",
            ],
            # "vps_name": "(system)"
        }

        spec = ComputeNodeSpec(**spec)
        logger.writeDebug("spec={}", spec)
        compute_node = self.recon.reconcile_compute_node(state, spec)
        logger.writeDebug("UT:OBJ:compute_node={}", compute_node)
        output_dict = asdict(compute_node)  # .to_dict()
        print(type(output_dict))
        logger.writeDebug("UT:DICT:compute_node={}", output_dict)
        new_data = ComputeNodePropertiesExtractor().extract_dict(output_dict)
        print(new_data)
        self.assertIsNotNone(compute_node)

    def xtest_create_compute_node_attach_volumes(self):
        state = "present"
        spec = {
            "name": "RD-compute-node-7",
            "os_type": "VMware",
            # "names" : ["RD-compute-node-111"],
            # "names" : ["p1-compute-node", "RD-compute-node-111"]
            # "iscsi_initiators" : ["iqn.1998-01.com.vmware:scpodl-esxi202:1586230596:68"]
            # "vps_name": "(system)"
            "state": "attach_volume",
            "volumes": ["test-volume1", "test-volume2"],
        }

        spec = ComputeNodeSpec(**spec)
        logger.writeDebug("spec={}", spec)
        compute_node = self.recon.reconcile_compute_node(state, spec)
        logger.writeDebug("compute_node={}", compute_node)
        # output_dict = compute_nodes.data_to_list()
        # new_data = ComputeNodePropertiesExtractor().extract(output_dict)
        print(compute_node)
        self.assertIsNotNone(compute_node)

    def xtest_update_compute_node_attach_volumes(self):
        state = "present"
        spec = {
            "name": "RD-compute-node-4",
            "os_type": "VMware",
            # "names" : ["RD-compute-node-111"],
            # "names" : ["p1-compute-node", "RD-compute-node-111"]
            # "iscsi_initiators" : ["iqn.1998-01.com.vmware:scpodl-esxi202:1586230596:68"]
            # "vps_name": "(system)"
            "state": "attach_volume",
            "volumes": ["test-volume1", "test-volume2"],
        }

        spec = ComputeNodeSpec(**spec)
        logger.writeDebug("spec={}", spec)
        compute_node = self.recon.reconcile_compute_node(state, spec)
        logger.writeDebug("compute_node={}", compute_node)
        # output_dict = compute_nodes.data_to_list()
        # new_data = ComputeNodePropertiesExtractor().extract(output_dict)
        print(compute_node)
        self.assertIsNotNone(compute_node)

    def xtest_update_compute_node_detach_volumes(self):
        state = "present"
        spec = {
            "name": "RD-compute-node-7",
            "state": "detach_volume",
            "volumes": ["test-volume1"],
        }

        spec = ComputeNodeSpec(**spec)
        logger.writeDebug("spec={}", spec)
        compute_node = self.recon.reconcile_compute_node(state, spec)
        logger.writeDebug("compute_node={}", compute_node)
        # output_dict = compute_nodes.data_to_list()
        # new_data = ComputeNodePropertiesExtractor().extract(output_dict)
        print(compute_node)
        self.assertIsNotNone(compute_node)

    def xtest_delete_compute_node_by_id(self):
        state = "absent"
        spec = {
            "id": "5e9b431d-67ae-45b2-bc09-5b9aba53bcae",
        }

        spec = ComputeNodeSpec(**spec)
        logger.writeDebug("spec={}", spec)
        compute_node = self.recon.reconcile_compute_node(state, spec)
        logger.writeDebug("compute_node={}", compute_node)
        # output_dict = compute_nodes.data_to_list()
        # new_data = ComputeNodePropertiesExtractor().extract(output_dict)
        print(compute_node)
        self.assertIsNotNone(compute_node == spec.id)

    def xtest_delete_compute_node_by_name(self):
        state = "absent"
        spec = {"name": "RD-compute-node-4", "should_delete_all_volumes": True}

        spec = ComputeNodeSpec(**spec)
        logger.writeDebug("spec={}", spec)
        compute_node = self.recon.reconcile_compute_node(state, spec)
        logger.writeDebug("compute_node={}", compute_node)
        # output_dict = compute_nodes.data_to_list()
        # new_data = ComputeNodePropertiesExtractor().extract(output_dict)
        print(compute_node)
        self.assertIsNotNone(compute_node == spec.name)

    def xtest_update_compute_node_name(self):
        state = "present"
        spec = {
            "id": "5cf4ee57-07cb-4c51-ba55-2643dff00514",
            "name": "RD-compute-node-3333",
            "os_type": "Linux",
        }

        spec = ComputeNodeSpec(**spec)
        logger.writeDebug("spec={}", spec)
        recon = SDSBComputeNodeReconciler(self.connection_info)

        compute_node = recon.reconcile_compute_node(state, spec)
        logger.writeDebug("compute_node={}", compute_node)
        output_dict = asdict(compute_node)
        new_data = ComputeNodePropertiesExtractor().extract_dict(output_dict)
        print(new_data)
        self.assertIsNotNone(compute_node)


if __name__ == "__main__":
    unittest.main()
