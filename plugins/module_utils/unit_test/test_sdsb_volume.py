import os
import sys
import unittest

# Add the parent directory to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)


from reconciler.sdsb_volume import SDSBVolumeReconciler
from reconciler.sdsb_properties_extractor import (
    VolumePropertiesExtractor,
    VolumeAndComputeNodePropertiesExtractor
)
from model.common_base_models import ConnectionInfo
from model.sdsb_volume_models import VolumeFactSpec, VolumeSpec
from common.hv_log import Log

logger = Log()


class TestSdsbVolume(unittest.TestCase):

    def setUp(self):
        connection_info = {
            "address": "10.76.47.55",
            #"address": "172.25.58.151",
            "username": "admin",
            "password": "vssb-789",
            "connection_type": "direct",
        }
        self.connection_info = ConnectionInfo(**connection_info)
        self.recon = SDSBVolumeReconciler(self.connection_info)

    def xtest_get_all_volume_names(self):
        spec = {"name": "test-volume2"}
        spec = VolumeFactSpec(**spec)

        # volume = recon.get_volume()
        volume = self.recon.get_all_volume_names()
        print(volume)
        self.assertIsNotNone(volume)

    def test_get_volumes(self):
        # spec = {}
        spec = {
            "names" : ["test-volume2"],
        }
        spec = VolumeFactSpec(**spec)

        # volume = recon.get_volume()
        volumes = self.recon.get_volumes(spec)
        output_dict = volumes.data_to_list()
        print(volumes)
        # new_data = VolumePropertiesExtractor().extract(output_dict)
        new_data = VolumeAndComputeNodePropertiesExtractor().extract(output_dict)
        print(new_data)        
 
        self.assertIsNotNone(volumes)

    def xtest_get_size_mb(self):
        state = "present"
        spec = {
            "capacity": "10 GB",
        }
        spec = VolumeSpec(**spec)
        print(spec)
        size = self.recon.get_size_mb(spec.capacity)
        print(size)

        self.assertIsNotNone(size)

    def xtest_create_volume(self):
        state = "present"
        spec = {
            "pool_name": "SP01",
            "name": "RD-volume-4",
            "capacity": 99,
            "compute_nodes": ["CAPI123678", "ComputeNode-1"]
        }
        spec = VolumeSpec(**spec)
        print(spec)
        volume = self.recon.reconcile_volume(state, spec)
        print(volume)

        self.assertIsNotNone(volume)

    def xtest_delete_volume_by_id(self):
        state = "absent"
        spec = {
            "id": "df63a5d9-32ea-4ae1-879a-7c23fbc574db",
        }

        spec = VolumeSpec(**spec)
        logger.writeDebug("spec={}", spec)
        volume = self.recon.reconcile_volume(state, spec)
        logger.writeDebug("volume={}", volume)
        # output_dict = compute_nodes.data_to_list()
        # new_data = ComputeNodePropertiesExtractor().extract(output_dict)
        print(volume)
        self.assertIsNotNone(volume == spec.id)

    def xtest_delete_volume_by_name(self):
        state = "absent"
        spec = {"name": "RD-volume-4",}

        spec = VolumeSpec(**spec)
        logger.writeDebug("spec={}", spec)
        volume = self.recon.reconcile_volume(state, spec)
        logger.writeDebug("volume={}", volume)
        # output_dict = compute_nodes.data_to_list()
        # new_data = ComputeNodePropertiesExtractor().extract(output_dict)
        print(volume)
        self.assertIsNotNone(volume == spec.name)

    def xtest_expand_volume(self):
        state = "present"
        spec = {
            "name": "RD-volume-4",
            "capacity": 202,
        }
        spec = VolumeSpec(**spec)
        print(spec)
        volume = self.recon.reconcile_volume(state, spec)
        print(volume)

        self.assertIsNotNone(volume)

    def xtest_change_nickname(self):
        state = "present"
        spec = {
            "name": "RD-volume-4",
            "nickname": "RD-volume-0004",     
        }
        spec = VolumeSpec(**spec)
        print(spec)
        volume = self.recon.reconcile_volume(state, spec)
        print(volume)

    def xtest_change_name(self):
        state = "present"
        spec = {
            "id": "aba5c900-b04c-4beb-8ca4-ed53537afb09",
            "name": "RD-volume-0004",
            "nickname": "RD-volume-0004",     
        }
        spec = VolumeSpec(**spec)
        print(spec)
        volume = self.recon.reconcile_volume(state, spec)
        print(volume)
        self.assertIsNotNone(volume)

    def xtest_remove_compute_nodes(self):
        state = "present"
        spec = {
            "id": "aba5c900-b04c-4beb-8ca4-ed53537afb09",
            "state": "remove_compute_node",
            "compute_nodes": ["ComputeNode-1"]
        }
        spec = VolumeSpec(**spec)
        print(spec)
        volume = self.recon.reconcile_volume(state, spec)
        print(volume)
        self.assertIsNotNone(volume)

    def xtest_add_compute_nodes(self):
        state = "present"
        spec = {
            "id": "aba5c900-b04c-4beb-8ca4-ed53537afb09",
            "state": "add_compute_node",
            "compute_nodes": ["ComputeNode-1"]
        }
        spec = VolumeSpec(**spec)
        print(spec)
        volume = self.recon.reconcile_volume(state, spec)
        print(volume)
        self.assertIsNotNone(volume)

if __name__ == "__main__":
    unittest.main()
