import os
import sys
import unittest
from dataclasses import dataclass, asdict

# Add the parent directory to the Python path
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_dir)


from reconciler.uaig_auth_token import UAIGAuthTokenReconciler
from model.common_base_models import ConnectionInfo
from model.sdsb_chap_user_models import ChapUserFactSpec
from common.hv_log import Log

logger = Log()


class TestUAIGAuthToken(unittest.TestCase):

    def setUp(self):
        connection_info = {
            "address": "172.25.20.54",
            # "address": "172.25.58.151",
            "username": "ucpadmin",
            "password": "Passw0rd!",
            "connection_type": "direct",
        }
        self.connection_info = ConnectionInfo(**connection_info)
        # logger.writeDebug('=== Create Compute Node ===')

    def test_get_auth_token(self):

        token = UAIGAuthTokenReconciler(self.connection_info).get_auth_token()
        print(token)
        self.assertIsNotNone(token)


if __name__ == "__main__":
    unittest.main()
