import os
import sys
import unittest

# Add the parent directory to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)


from reconciler.vsp_shadow_image_pair_reconciler import VSPShadowImagePairReconciler
from model.vsp_shadow_image_pair_models import *
from model.common_base_models import ConnectionInfo, StorageSystemInfo


class TestVspShadowImagePair(unittest.TestCase):

    def setUp(self):
        # connection_info = {
        #     "address": "172.25.20.50",
        #     #     "username": "ucpadmin",
        #     # "password": "Passw0rd!",
        #     "api_token": "eyJhbGciOiJSUzI1NiIsInR5cCIgOiAiSldUIiwia2lkIiA6ICJlQlVnUWFZUVF4YjV0eVMzREJzVDlLYnlqUDFhakJkcmtJUUc0aUJnaWs0In0.eyJleHAiOjE3MTY5MzQ5MjEsImlhdCI6MTcxNjg5ODkyMSwianRpIjoiMjlkZGRlOTQtNjI2ZC00YTQ1LWFhNDEtZDEwOTM0NTIyMTg4IiwiaXNzIjoiaHR0cHM6Ly9rZXljbG9hazo4MDgxL2F1dGgvcmVhbG1zL3VjcHN5c3RlbSIsImF1ZCI6InJlYWxtLW1hbmFnZW1lbnQiLCJzdWIiOiJkOWEzYmUzOS1hYzc1LTQ2OTgtOTk2Yi04ZWVmYWMzNmM1ZGIiLCJ0eXAiOiJCZWFyZXIiLCJhenAiOiJ1Y3BhZHZpc29yIiwic2Vzc2lvbl9zdGF0ZSI6IjU2MzBmMTQxLWY5YmMtNGRmYS1hMGZmLTc5YjRhMzkzODhiMyIsImFjciI6IjEiLCJyZWFsbV9hY2Nlc3MiOnsicm9sZXMiOlsidWNwQWRtaW5Sb2xlIl19LCJyZXNvdXJjZV9hY2Nlc3MiOnsicmVhbG0tbWFuYWdlbWVudCI6eyJyb2xlcyI6WyJ2aWV3LWlkZW50aXR5LXByb3ZpZGVycyIsIm1hbmFnZS1yZWFsbSIsIm1hbmFnZS1pZGVudGl0eS1wcm92aWRlcnMiLCJtYW5hZ2UtdXNlcnMiLCJ2aWV3LXVzZXJzIiwidmlldy1hdXRob3JpemF0aW9uIiwicXVlcnktZ3JvdXBzIiwicXVlcnktdXNlcnMiXX0sInVjcGFkdmlzb3IiOnsicm9sZXMiOlsidWNwQWR2aXNvckNsaWVudFJvbGUiXX19LCJzY29wZSI6Im9wZW5pZCBlbWFpbCBwcm9maWxlIiwic2lkIjoiNTYzMGYxNDEtZjliYy00ZGZhLWEwZmYtNzliNGEzOTM4OGIzIiwiZW1haWxfdmVyaWZpZWQiOmZhbHNlLCJwcmVmZXJyZWRfdXNlcm5hbWUiOiJhZG1pbiJ9.PDhKZUc3l7EntAevoLcWd4C4VEFW33hxBs10LAIKjay_llkUcSkC0HxX_tE-qlKmzHZeU2Au6ygddWsLGWN0VGYc7zSrq9gDibBYDWraJDM8WT8MxiSaXne__Ig2B3nWEbjDPjew-dGR_Me691LriX9IvNMQPCvMqDaenDq6GK1oD0A9tAQl8QbebO09AyVhTDY-OToFaKJT7U6mBqi60wFjwKAmWoN7FGs9ngDMWvlEP3v6fuznMErbdLScmdhnxBvuQn8PGITrjq7DbB0rjnZpVL7k3sfAAB_7EDThiYN6qs8XLGYOiHvRxfbAvoad2ILi1ID11n9I03lIvsWQ6w",
        #     "connection_type": "gateway",
        #     "subscriber_id": "12345",
        # }

        connection_info =  {
                                "address":"172.25.45.105",
                                "username":"ucpa",
                                "password":"Hitachi1",
                                "connection_type":"direct"}

        storage_system_info = {"serial": 810050}

        self.connectionInfo = ConnectionInfo(**connection_info)
        self.serial = 810050

    def xtest_get_all_shadow_image_pair(self):
        spec = {
            #"pvol": 279
        }
        spec = GetShadowImageSpec(**spec)
        response = VSPShadowImagePairReconciler(
            self.connectionInfo,
            self.serial,
        ).shadow_image_pair_facts(spec)
        print(response)
        self.assertIsNotNone(response)

    def xtest_get_shadow_image_pair_by_pvol_and_svol(self):
        spec = {
            "refresh": "false",
            "pvol": 274,
            "svol": 279,
        }
        spec = GetShadowImageSpec(**spec)
        response = VSPShadowImagePairReconciler(
            self.connectionInfo, self.serial
        ).shadow_image_pair_get_by_pvol_and_svol(spec)
        print(response)
        self.assertIsNotNone(response)

    

    def xtest_create_shadow_image_pair(self):
        spec = {
            "pvol": 279, 
            "svol": 282,
            # "new_consistency_group": True,
            # "copy_pace_track_size": "MEDIUM",
            #"enable_quick_mode": True,
            # "enable_read_write": True,
            "consistency_group_id": 32,
        }
        spec = ShadowImagePairSpec(**spec)
        state = "present"
        reconciler = VSPShadowImagePairReconciler(self.connectionInfo, self.serial,spec)
        #self.populate_data(reconciler, spec)
        response = reconciler.shadow_image_pair_module(state)
        self.assertIsNotNone(response)

    def xtest_split_shadow_image_pair(self):
        spec = {
            "pvol": 279,
            "svol": 282,
            #"new_consistency_group": True,
        }
        spec = ShadowImagePairSpec(**spec)
        state = "split"
        reconciler = VSPShadowImagePairReconciler(self.connectionInfo, self.serial,spec)
        #self.populate_data(reconciler, spec)
        response = reconciler.shadow_image_pair_module(state)
        print(response)
        self.assertIsNotNone(response)

    def xtest_resync_shadow_image_pair(self):
        spec = {
            "pvol": 274,
            "svol": 279,
            "copy_pace": "MEDIUM",
        }
        spec = ShadowImagePairSpec(**spec)
        state = "sync"
        reconciler = VSPShadowImagePairReconciler(self.connectionInfo, self.serial,spec)
        #self.populate_data(reconciler, spec)
        response = reconciler.shadow_image_pair_module(state)
        print(response)
        self.assertIsNotNone(response)

    def xtest_restore_shadow_image_pair(self):
        spec = {
            "pvol": 279,
            "svol": 281,
            "copy_pace": "MEDIUM",
        }
        spec = ShadowImagePairSpec(**spec)
        state = "restore"
        reconciler = VSPShadowImagePairReconciler(self.connectionInfo, self.serial,spec)
        #self.populate_data(reconciler, spec)
        response = reconciler.shadow_image_pair_module(state)
        print(response)
        self.assertIsNotNone(response)

    def xtest_delete_shadow_image_pair(self):
        spec = {
            "pvol": 274,
            "svol": 279,
        }
        state = "absent"
        spec = ShadowImagePairSpec(**spec)
        reconciler = VSPShadowImagePairReconciler(self.connectionInfo, self.serial,spec)
        #self.populate_data(reconciler, spec)
        response = reconciler.shadow_image_pair_module(state)
        print(response)
        self.assertIsNotNone(response)

    def populate_data(self, reconciler, spec):
        shadow_image_data = reconciler.shadow_image_pair_get_by_pvol_and_svol(
            spec.pvol, spec.svol
        )
        pairId = None
        if shadow_image_data is not None:
            pairId = shadow_image_data.get("resource_id")
        spec.pair_id = pairId


if __name__ == "__main__":
    unittest.main()
