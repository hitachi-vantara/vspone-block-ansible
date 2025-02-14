from typing import List, Dict, Any

try:
    from ..common.uaig_constants import Endpoints
    from ..common.hv_constants import CommonConstants
    from .gateway_manager import UAIGConnectionManager
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..common.uaig_utils import UAIGResourceID

except ImportError:
    from common.uaig_constants import Endpoints
    from common.hv_constants import CommonConstants
    from .gateway_manager import UAIGConnectionManager
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from common.uaig_utils import UAIGResourceID


logger = Log()


class VSPUnsubscribeUAIGateway:

    def __init__(self, connection_info):

        self.connection_manager = UAIGConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )
        self.end_points = Endpoints
        self.connection_info = connection_info
        self.resource_types = {
            "port": "Port",
            "volume": "Volume",
            "hostgroup": "HostGroup",
            "shadowimage": "shadowimage",
            "storagepool": "StoragePool",
            "iscsitarget": "IscsiTarget",
            "snapshotpair": "snapshotpair",
            "hurpair": "hurpair",
            "gadpair": "gadpair",
            "truecopypair": "truecopypair",
        }

    @log_entry_exit
    def set_storage_serial_number(self, serial: str):
        self.storage_serial_number = serial

    def get_storage_id(self):
        return UAIGResourceID().storage_resourceId(self.storage_serial_number)

    @log_entry_exit
    def get_ucpsystems(self) -> List[Dict[str, Any]]:
        end_point = self.end_points.GET_UCPSYSTEMS
        ucpsystems = self.connection_manager.get(end_point)
        return ucpsystems["data"]

    @log_entry_exit
    def check_storage_in_ucpsystem(self) -> bool:
        storage_serial_number = self.storage_serial_number
        ucpsystems = self.get_ucpsystems()
        logger.writeDebug("GW:check_storage_in_ucpsystem:ucpsystems={}", ucpsystems)
        for u in ucpsystems:
            # if u.get("name") == CommonConstants.UCP_NAME:
            for s in u.get("storageDevices"):
                if s.get("serialNumber") == storage_serial_number:
                    return s.get("healthState") != CommonConstants.ONBOARDING
        return False

    @log_entry_exit
    def untag_subscriber_resource(self, serial, resource_id, type):
        if self.connection_info.subscriber_id is None:
            raise ValueError("subscriber_id is missing.")
        self.set_storage_serial_number(serial)
        storage_id = self.get_storage_id()
        subscriber_id = self.connection_info.subscriber_id
        end_point = self.end_points.UNTAG_SUBSCRIBER_RESOURCE.format(
            storage_id, resource_id, type, subscriber_id
        )
        return self.connection_manager.delete(end_point)
