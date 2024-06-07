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
from model.common_base_models import ConnectionInfo, StorageSystemInfo, TenantInfo
from common.vsp_utils import VSPSnapshotArguments, VSPParametersManager
from common.hv_constants import CommonConstants


class TestVSPHtiSnapshotUai(unittest.TestCase):

    def setUp(self):
        params = {
            "connection_info": {
                "address": "172.25.45.102",
                "username": "ucpa",
                "password": "Hitachi1",
                "connection_type": "direct",
            },
            "storage_system_info": {"serial": 810050},
            "spec": { },
        }

        tenant_info = {"partnerId": "apiadmin"}
        self.tenant_info = TenantInfo(**tenant_info)
        connection_info = params["connection_info"]
        storage_system_info = params["storage_system_info"]
        spec = params["spec"]

        self.params = params
        self.serial = storage_system_info["serial"]
        self.spec = spec

        self.ConnectionInfo = ConnectionInfo(**connection_info)

    # GET gateway
    # def test_gwy_get_all_snapshots(self):
    #     conn = VSPHtiSnapshotUaiGateway(self.ConnectionInfo)
    #     conn.set_storage_serial_number(self.serial)
    #     snapshots = conn.get_all_snapshots(self.tenant_info)
    #     print(f"test_gwy_get_all_snapshots: {snapshots}")
    #     self.assertIsNotNone(snapshots)

    # def test_gwy_get_one_snapshot(self):
    #     conn = VSPHtiSnapshotUaiGateway(self.ConnectionInfo)
    #     conn.set_storage_serial_number(self.serial)
    #     snapshots = conn.get_one_snapshot(self.spec['pvol'], self.spec['mirror_unit_id'])
    #     print(f"test_gwy_get_one_snapshot: {snapshots}")
    #     self.assertIsNotNone(snapshots)

    # def test_gwy_get_snapshot_by_pvol(self):
    #     conn = VSPHtiSnapshotUaiGateway(self.ConnectionInfo)
    #     conn.set_storage_serial_number(self.serial)
    #     snapshots = conn.get_snapshot_by_pvol(self.spec['pvol'])
    #     print(f"test_gwy_get_snapshot_by_pvol: {snapshots}")
    #     self.assertIsNotNone(snapshots)

    # # GET provisioner
    # def test_prov_get_snapshot_facts_all(self):
    #     conn = VSPHtiSnapshotProvisioner(self.ConnectionInfo)
    #     # self.spec['pvol'] = None
    #     # self.spec['mirror_unit_id'] = None
    #     snapshots = conn.get_snapshot_facts()
    #     print(f"test_gwy_get_snapshot_no_pvol: {snapshots}")
    #     self.assertIsNotNone(snapshots)

    # def test_prov_get_snapshot_facts_pvol_mirrorid(self):
    #     conn = VSPHtiSnapshotProvisioner(self.ConnectionInfo)
    #     snapshots = conn.get_snapshot_facts(self.spec['pvol'], self.spec['mirror_unit_id'])
    #     print(f"test_gwy_get_snapshot_no_mirrorid: {snapshots}")
    #     self.assertIsNotNone(snapshots)

    # def test_prov_get_snapshot_facts_no_mirrorid(self):
    #     conn = VSPHtiSnapshotProvisioner(self.ConnectionInfo)
    #     snapshots = conn.get_snapshot_facts(self.spec['pvol'])
    #     print(f"test_gwy_get_snapshot_no_mirrorid: {snapshots}")
    #     self.assertIsNotNone(snapshots)

    def xtest_prov_get_one_snapshot(self):
        conn = VSPHtiSnapshotProvisioner(self.ConnectionInfo, self.serial)
        snapshot = conn.get_one_snapshot(self.spec["pvol"], self.spec["mirror_unit_id"])
        print(f"test_gwy_get_one_snapshot: {snapshot}")
        self.assertIsNotNone(snapshot)

    # GET reconciler
    def test_rec_get_snapshot_facts_pvol_mirrorid(self):

        params_manager = VSPParametersManager(self.params)
        spec = params_manager.get_snapshot_fact_spec()

        conn = VSPHtiSnapshotReconciler(self.ConnectionInfo, self.serial)
        snapshots = conn.get_snapshot_facts(spec)

        print(f"test_rec_get_snapshot_facts_pvol_mirrorid: {snapshots}")
        self.assertIsNotNone(snapshots)

    def xtest_rec_get_snapshot_facts_pvol_mirrorid_direct(self):
        connection_info = {
            "address": "172.25.20.87",
            "username": "admin",
            "password": "overrunsurveysroutewarnssent",
            "connection_type": "gateway",
        }
        self.params["connection_info"] = connection_info
        params_manager = VSPParametersManager(self.params)
        spec = params_manager.get_snapshot_fact_spec()
        connection_info = params_manager.get_connection_info()

        tenant_info = params_manager.get_tenant_info()
        if tenant_info.partnerId is None:
            tenant_info.partnerId = CommonConstants.PARTNER_ID
        conn = VSPHtiSnapshotReconciler(connection_info, self.serial)
        snapshots = conn.get_snapshot_facts(spec)

        print(f"test_rec_get_snapshot_facts_pvol_mirrorid: {snapshots}")
        self.assertIsNotNone(snapshots)

    # def test_rec_get_snapshot_facts(self):
    #     conn = VSPHtiSnapshotReconciler(self.ConnectionInfo, self.serial)
    #     params = {
    #         'connection_info':  {
    #             "address":"172.25.20.54",
    #             "username":"ucpadmin",
    #             "password":"Passw0rd!",
    #             "connection_type":"gateway"
    #         },
    #         'storage_system_info': {
    #             "serial": 40015
    #         },
    #         'spec' : {
    #         }
    #     }
    #     spec = VSPParametersManager(params).get_snapshot_fact_spec()
    #     snapshots = conn.get_snapshot_facts(spec)
    #     print(f"test_rec_get_snapshot_facts: {snapshots}")
    #     self.assertIsNotNone(snapshots)

    # def test_check_storage_in_ucpsystem(self):
    #     res = VSPHtiSnapshotUaiGateway(self.params).check_storage_in_ucpsystem()
    #     print(res)
    #     self.assertIsNotNone(res)


if __name__ == "__main__":
    unittest.main()
