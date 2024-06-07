import os
import sys
import unittest

# Add the parent directory to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)


from reconciler.uaig_subscriber_reconciler import SubscriberReconciler
from model.uaig_subscriber_models import *
from model.common_base_models import ConnectionInfo


class TestSubscriber(unittest.TestCase):

    def setUp(self):
        connection_info = {
            "address": "172.25.22.23",
            "username": "ucpadmin",
            "password": "Passw0rd!",
            "connection_type": "gateway",
        }

        self.ConnectionInfo = ConnectionInfo(**connection_info)

    def test_get_subscriber_facts(self):
        spec = {}
        spec = SubscriberFactSpec(**spec)
        response = SubscriberReconciler(self.ConnectionInfo).get_subscriber_facts(spec)
        print(response)
        self.assertIsNotNone(response)

    def test_create_subscriber(self):
        createSpec = {
            "name": "sub3",
            "subscriber_id": "3",
            "soft_limit": "70",
            "hard_limit": "80",
            "quota_limit": "20",
        }
        createSpec = SubscriberSpec(**createSpec)
        response = SubscriberReconciler(self.ConnectionInfo).create_subscriber(
            createSpec
        )
        print(response)
        self.assertIsNotNone(response)

    def test_update_subscriber(self):
        updateSpec = {"subscriber_id": "3", "soft_limit": "80", "hard_limit": "90"}
        updateSpec = SubscriberSpec(**updateSpec)
        spec = {"subscriber_id": "3"}
        spec = SubscriberFactSpec(**spec)
        response_get = SubscriberReconciler(self.ConnectionInfo).get_subscriber_facts(
            spec
        )
        response = SubscriberReconciler(self.ConnectionInfo).update_subscriber(
            updateSpec, response_get[0]
        )
        print(response)
        self.assertIsNotNone(response)

    def test_delete_subscriber(self):
        deleteSpec = {"subscriber_id": "3"}
        deleteSpec = SubscriberSpec(**deleteSpec)
        response = SubscriberReconciler(self.ConnectionInfo).delete_subscriber(
            deleteSpec
        )
        print(response)
        self.assertIsNotNone(response)


if __name__ == "__main__":
    unittest.main()
