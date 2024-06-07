import os
import sys
import unittest


parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)

from common.vsp_utils import VSPParametersManager
from model.common_base_models import ConnectionInfo
from model.vsp_volume_models import CreateVolumeSpec, VolumeFactSpec

from reconciler.vsp_volume import VolumeCommonPropertiesExtractor, VSPVolumeReconciler

# Add the parent directory to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)


class TestVssbVolume(unittest.TestCase):

    def setUp(self):
        self.raw_connection_info = {
            "address": "172.25.45.102",
            "username": "ucpa",
            "password": "Hitachi1",
            "connection_type": "direct",
            "subscriber_id": "",
        }

        self.ConnectionInfo = ConnectionInfo(**self.raw_connection_info)
        self.serial = 30595

        self.params = {
            "connection_info": {
                "address": "172.25.66.75",
                "username": "admin",
                "password": "overrunsurveysroutewarnssent",
                "connection_type": "direct",
                "subscriber_id": "",
            },
            "storage_system_info": {"serial": 810050},
            # 'spec' : {
            #     "pvol": 176,
            #     # "mirror_unit_id": 3
            # }
        }

    def test_get_volume(self):

        spec = {
            # "count":100,
            "start_ldev_id": 1,
            "end_ldev_id": 2,
            # "name":"Pool_Vol_Terraform"
            "lun": "",
        }
        self.params["spec"] = spec

        # spec = VolumeFactSpec(**spec)

        params_manager = VSPParametersManager(self.params)
        self.spec = params_manager.set_volume_fact_spec()

        volume = VSPVolumeReconciler(self.ConnectionInfo, self.serial).get_volumes(
            self.spec
        )
        volume_to_dict = volume.data_to_list()
        new_data = VolumeCommonPropertiesExtractor(30595).extract(volume_to_dict)
        print(new_data)
        self.assertIsNotNone(volume)

    def xtest_create_volume(self):
        spec = {"pool_id": 1, "size": "32GB", "lun": 390}
        serial = {"serial": 810050}
        state = "present"
        params = {
            "connection_info": self.raw_connection_info,
            "state": state,
            "spec": spec,
            "storage_system_info": serial,
        }
        params_manager = VSPParametersManager(params)
        spec = params_manager.set_volume_spec()
        connection_info = params_manager.get_connection_info()
        volume = VSPVolumeReconciler(connection_info, self.serial).volume_reconcile(
            state, spec
        )
        volume_to_dict = volume.to_dict()
        new_data = VolumeCommonPropertiesExtractor(self.serial).extract(
            [volume_to_dict]
        )
        print(new_data)
        self.assertIsNotNone(volume)


if __name__ == "__main__":
    unittest.main()
