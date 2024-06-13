import os
import sys
import unittest

# Add the parent directory to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)


from gateway.vsp_snapshot_gateway import VSPHtiSnapshotUaiGateway
from provisioner.vsp_snapshot_provisioner import VSPHtiSnapshotProvisioner
from reconciler.vsp_snapshot_reconciler import (
    VSPHtiSnapshotReconciler,
    SnapshotCommonPropertiesExtractor,
)
from model.common_base_models import ConnectionInfo, StorageSystemInfo
from common.uaig_utils import UAIGSnapshotArguments, UAIGParametersManager
from common.vsp_utils import VSPSnapshotArguments, VSPParametersManager
from common.hv_constants import CommonConstants


class TestVSPHtiSnapshotUai(unittest.TestCase):

    def setUp(self):
        params = {
            "connection_info": {
                "address": "172.25.20.54",
                "username": "ucpadmin",
                "password": "Passw0rd!",
                "connection_type": "gateway",
            },
            "storage_system_info": {"serial": 810050},
            "task_level": {"state": "present"},
            "spec": {"pvol": 194, "mirror_unit_id": 3},
        }

        connection_info = params["connection_info"]
        storage_system_info = params["storage_system_info"]
        spec = params["spec"]

        self.params = params
        self.serial = storage_system_info["serial"]
        self.spec = spec

        self.ConnectionInfo = ConnectionInfo(**connection_info)

    # # DELETE gateway
    # def test_gwy_delete_snapshot(self):
    #     conn = VSPHtiSnapshotUaiGateway(self.ConnectionInfo)
    #     conn.set_storage_serial_number(self.serial)
    #     snapshots = conn.delete_snapshot(self.spec['pvol'], self.spec['mirror_unit_id'])
    #     print(f"test_gwy_delete_snapshot: {snapshots}")
    #     self.assertIsNotNone(snapshots)

    # def test_gwy_delete_snapshot_by_resource_id(self):
    #     conn = VSPHtiSnapshotUaiGateway(self.ConnectionInfo)
    #     conn.set_storage_serial_number(self.serial)
    #     resourceId = ""
    #     snapshots = conn.delete_snapshot_by_resource_id(resourceId)
    #     print(f"test_gwy_delete_snapshot_by_resource_id: {snapshots}")
    #     self.assertIsNotNone(snapshots)

    # def test_prov_delete_snapshot(self):
    #     conn = VSPHtiSnapshotProvisioner(self.ConnectionInfo)
    #     snapshots = conn.delete_snapshot(self.spec['pvol'], self.spec['mirror_unit_id'])
    #     print(f"test_prov_delete_snapshot: {snapshots}")
    #     self.assertIsNotNone(snapshots)

    # def test_rec_delete_snapshot(self):
    #     self.params = UAIGParametersManager(self.params)
    #     self.spec = self.params.get_snapshot_reconcile_spec()
    #     self.spec.state = 'absent'
    #     conn = VSPHtiSnapshotReconciler(self.ConnectionInfo, self.serial, self.spec)
    #     snapshots = conn.reconcile_snapshot(self.spec)
    #     print(f"test_rec_delete_snapshot: {snapshots}")
    #     self.assertIsNotNone(snapshots)

    # # CREATE
    # def test_gwy_create_snapshot(self):
    #     # conn = VSPHtiSnapshotUaiGateway(self.ConnectionInfo)
    #     params = {
    #         'connection_info':  {
    #             "address":"172.25.20.54",
    #             "username":"ucpadmin",
    #             "password":"Passw0rd!",
    #             "connection_type":"gateway"
    #         },
    #         'storage_system_info': {
    #             "serial": 40014
    #         },
    #         'spec' : {
    #             "pvol": 176,
    #             "pool_id": 15,
    #             "allocate_consistency_group": False,
    #             "consistency_group_id": -1,
    #             "enable_quick_mode": False,
    #         }
    #     }
    #     connection_info =  params['connection_info']
    #     storage_system_info = params['storage_system_info']
    #     serial = storage_system_info['serial']
    #     spec = params['spec']
    #     connectionInfo = ConnectionInfo(**connection_info)

    #     conn = VSPHtiSnapshotUaiGateway(connectionInfo)
    #     conn.set_storage_serial_number(self.serial)
    #     # spec = UAIGParametersManager(params).get_snapshot_reconcile_spec()

    #     snapshots = conn.create_snapshot(serial,
    #         spec['pvol'],
    #         spec['pool_id'],
    #         spec['allocate_consistency_group'],
    #         spec['consistency_group_id'],
    #         spec['enable_quick_mode']
    #         )
    #     print(f"test_gwy_create_snapshot: {snapshots}")
    #     self.assertIsNotNone(snapshots)

    # def test_prov_create_snapshot(self):
    #     # conn = VSPHtiSnapshotProvisioner(self.ConnectionInfo)
    #     params = {
    #         'connection_info':  {
    #             "address":"172.25.20.54",
    #             "username":"ucpadmin",
    #             "password":"Passw0rd!",
    #             "connection_type":"gateway"
    #         },
    #         'storage_system_info': {
    #             "serial": 40014
    #         },
    #         'spec' : {
    #             "pvol": 176,
    #             "pool_id": 15,
    #             "allocate_consistency_group": False,
    #             "consistency_group_id": -1,
    #             "enable_quick_mode": False,
    #         },
    #         'task_level': {
    #             'state': 'present'
    #         }
    #     }
    #     connection_info =  params['connection_info']
    #     storage_system_info = params['storage_system_info']
    #     serial = storage_system_info['serial']
    #     spec = params['spec']
    #     connectionInfo = ConnectionInfo(**connection_info)

    #     conn = VSPHtiSnapshotProvisioner(connectionInfo)
    #     spec = UAIGParametersManager(params).get_snapshot_reconcile_spec()

    #     snapshots = conn.create_snapshot(serial, spec)
    #     print(f"test_prov_create_snapshot: {snapshots}")
    #     self.assertIsNotNone(snapshots)
    def xtest_rec_create_snapshot_gateway(self):
        # conn = VSPHtiSnapshotReconciler(self.ConnectionInfo)
        params = {
             "connection_info": {
                "address": "172.25.20.87",
                "username": "admin",
                "password": "overrunsurveysroutewarnssent",
                "connection_type": "gateway",
            },
            "storage_system_info": {"serial": 810050},
            "spec": {
                "pvol": 194,
                "pool_id": 0,
                # "allocate_consistency_group": False,
                # "consistency_group_id": -1,
                "snapshot_group_name": "newGrpName",
            },
            "state": "present",
        }
        connection_info = params["connection_info"]
        storage_system_info = params["storage_system_info"]
        serial = storage_system_info["serial"]
        spec = params["spec"]
        connectionInfo = ConnectionInfo(**connection_info)

        self.params = VSPParametersManager(params)
        self.spec = self.params.get_snapshot_reconcile_spec()

        conn = VSPHtiSnapshotReconciler(connectionInfo, self.serial, spec)
        # spec = UAIGParametersManager(params).get_snapshot_reconcile_spec()
        snapshots = conn.reconcile_snapshot(self.spec)
        print(f"test_rec_create_snapshot: {snapshots}")
        self.assertIsNotNone(snapshots)

    def test_rec_create_snapshot(self):
        # conn = VSPHtiSnapshotReconciler(self.ConnectionInfo)
        params = {
             "connection_info": {
                "address": "172.25.47.115",
                "username": "maintenance",
                "password": "raid-maintenance",
                "connection_type": "direct",
            },
            #  "connection_info": {
            #     "address": "172.25.45.102",
            #     "username": "ucpa",
            #     "password": "Hitachi1",
            #     "connection_type": "direct",
            # },
            "storage_system_info": {"serial": 810050},
            "spec": {
                # "pvol": 681,
                "pvol": 546,
                "pool_id": 15,
                # "allocate_consistency_group": False,
                # "consistency_group_id": -1,
                "snapshot_group_name": "newGrpName",
            },
            "state": "present",
        }
        connection_info = params["connection_info"]
        storage_system_info = params["storage_system_info"]
        serial = storage_system_info["serial"]
        spec = params["spec"]
        connectionInfo = ConnectionInfo(**connection_info)

        self.params = VSPParametersManager(params)
        self.spec = self.params.get_snapshot_reconcile_spec()

        conn = VSPHtiSnapshotReconciler(connectionInfo, self.serial, spec)
        # spec = UAIGParametersManager(params).get_snapshot_reconcile_spec()
        snapshots = conn.reconcile_snapshot(self.spec)
        print(f"test_rec_create_snapshot: {snapshots}")
        self.assertIsNotNone(snapshots)

    def xtest_rec_create_snapshot_direct(self):
        # conn = VSPHtiSnapshotReconciler(self.ConnectionInfo)
        params = {
             "connection_info": {
                "address": "172.25.20.87",
                "username": "admin",
                "password": "overrunsurveysroutewarnssent",
                "connection_type": "gateway",
            },
            "storage_system_info": {"serial": 810050},
            "spec": {
                "pvol": 293,
                "pool_id": 21,
                # "allocate_consistency_group": False,
                # "consistency_group_id": -1,
                "snapshot_group_name": "newGrpName1111",
            },
            "state": "present",
        }
        connection_info = params["connection_info"]
        storage_system_info = params["storage_system_info"]
        serial = storage_system_info["serial"]
        spec = params["spec"]
        connectionInfo = ConnectionInfo(**connection_info)

        self.params = VSPParametersManager(params)
        self.spec = self.params.get_snapshot_reconcile_spec()

        conn = VSPHtiSnapshotReconciler(connectionInfo, self.serial, spec)
        # spec = UAIGParametersManager(params).get_snapshot_reconcile_spec()
        snapshots = conn.reconcile_snapshot(self.spec)
        print(f"test_rec_create_snapshot: {snapshots}")
        self.assertIsNotNone(snapshots)

    # AUTO-SPLIT
    # def test_rec_auto_split_snapshot(self):
    #     params = {
    #         'connection_info':  {
    #             "address":"172.25.20.54",
    #             "username":"ucpadmin",
    #             "password":"Passw0rd!",
    #             "connection_type":"gateway"
    #         },
    #         'storage_system_info': {
    #             "serial": 40014
    #         },
    #         'spec' : {
    #             "pvol": 176,
    #             "pool_id": 15,
    #             "allocate_consistency_group": False,
    #             "consistency_group_id": -1,
    #             "enable_quick_mode": False,
    #         },
    #         'task_level': {
    #             'state': 'split'
    #         }
    #     }
    #     connection_info =  params['connection_info']
    #     storage_system_info = params['storage_system_info']
    #     serial = storage_system_info['serial']
    #     spec = params['spec']
    #     connectionInfo = ConnectionInfo(**connection_info)

    #     self.params = UAIGParametersManager(self.params)
    #     self.spec = self.params.get_snapshot_reconcile_spec()

    #     conn = VSPHtiSnapshotReconciler(connectionInfo, self.serial, spec)
    #     spec = UAIGParametersManager(params).get_snapshot_reconcile_spec()
    #     snapshots = conn.reconcile_snapshot(serial, spec)
    #     print(f"test_rec_create_snapshot: {snapshots}")
    #     self.assertIsNotNone(snapshots)

    # # OPS
    # def test_gwy_split_snapshot(self):
    #     conn = VSPHtiSnapshotUaiGateway(self.ConnectionInfo)
    #     conn.set_storage_serial_number(self.serial)
    #     snapshots = conn.split_snapshot(self.spec['pvol'], self.spec['mirror_unit_id'])
    #     print(f"test_gwy_split_snapshot: {snapshots}")
    #     self.assertIsNotNone(snapshots)

    # def test_rec_split_snapshot(self):
    #     self.params = UAIGParametersManager(self.params)
    #     self.spec = self.params.get_snapshot_reconcile_spec()
    #     self.spec.state = 'split'
    #     self.spec.pool_id = None
    #     self.spec.mirror_unit_id = 4
    #     self.spec.enable_quick_mode = False

    #     conn = VSPHtiSnapshotReconciler(self.ConnectionInfo, self.serial, self.spec)
    #     snapshots = conn.reconcile_snapshot(self.spec)
    #     print(f"test_rec_split_snapshot: {snapshots}")
    #     self.assertIsNotNone(snapshots)

    # def test_rec_split_snapshot_quick_mode(self):
    #     self.params = UAIGParametersManager(self.params)
    #     self.spec = self.params.get_snapshot_reconcile_spec()
    #     self.spec.state = 'split'
    #     self.spec.pool_id = None
    #     self.spec.mirror_unit_id = 4
    #     self.spec.enable_quick_mode = True

    #     conn = VSPHtiSnapshotReconciler(self.ConnectionInfo, self.serial, self.spec)
    #     snapshots = conn.reconcile_snapshot(self.spec)
    #     print(f"test_rec_split_snapshot_quick_mode: {snapshots}")
    #     self.assertIsNotNone(snapshots)

    # def test_gwy_resync_snapshot(self):
    #     conn = VSPHtiSnapshotUaiGateway(self.ConnectionInfo)
    #     conn.set_storage_serial_number(self.serial)
    #     snapshots = conn.resync_snapshot(self.spec['pvol'], self.spec['mirror_unit_id'])
    #     print(f"test_gwy_resync_snapshot: {snapshots}")
    #     self.assertIsNotNone(snapshots)

    # def test_rec_resync_snapshot(self):
    #     self.params = UAIGParametersManager(self.params)
    #     self.spec = self.params.get_snapshot_reconcile_spec()
    #     self.spec.state = 'resync'
    #     self.spec.pool_id = None
    #     self.spec.enable_quick_mode = False

    #     conn = VSPHtiSnapshotReconciler(self.ConnectionInfo, self.serial, self.spec)
    #     snapshots = conn.reconcile_snapshot(self.spec)
    #     print(f"test_rec_resync_snapshot: {snapshots}")
    #     self.assertIsNotNone(snapshots)

    # def test_gwy_restore_snapshot(self):
    #     conn = VSPHtiSnapshotUaiGateway(self.ConnectionInfo)
    #     conn.set_storage_serial_number(self.serial)
    #     snapshots = conn.restore_snapshot(self.spec['pvol'], self.spec['mirror_unit_id'])
    #     print(f"test_gwy_restore_snapshot: {snapshots}")
    #     self.assertIsNotNone(snapshots)

    # def test_rec_restore_snapshot(self):
    #     self.params = UAIGParametersManager(self.params)
    #     self.spec = self.params.get_snapshot_reconcile_spec()
    #     self.spec.state = 'restore'
    #     self.spec.pool_id = None
    #     self.spec.enable_quick_mode = False

    #     conn = VSPHtiSnapshotReconciler(self.ConnectionInfo, self.serial, self.spec)
    #     snapshots = conn.reconcile_snapshot(self.spec)
    #     print(f"test_rec_restore_snapshot: {snapshots}")
    #     self.assertIsNotNone(snapshots)

    # def test_gwy_create_snapshot_allocate_cg(self):
    #     pass


if __name__ == "__main__":
    unittest.main()
