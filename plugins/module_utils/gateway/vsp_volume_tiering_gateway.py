from typing import List, Dict, Any

try:
    from ..common.uaig_constants import Endpoints
    from ..common.hv_constants import CommonConstants
    from .gateway_manager import UAIGConnectionManager
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
except ImportError:
    from common.uaig_constants import Endpoints
    from common.hv_constants import CommonConstants
    from .gateway_manager import UAIGConnectionManager
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit


class VSPVolTieringUAIGateway:

    def __init__(self, connection_info):
        self.logger = Log()
        self.connection_manager = UAIGConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )
        self.end_points = Endpoints
        self.connectionInfo = connection_info

    @log_entry_exit
    def set_storage_serial_number(self, serial: str):
        self.storage_serial_number = serial

    @log_entry_exit
    def get_ucpsystems(self) -> List[Dict[str, Any]]:
        end_point = self.end_points.GET_UCPSYSTEMS
        ucpsystems = self.connection_manager.get(end_point)
        return ucpsystems["data"]

    @log_entry_exit
    def check_storage_in_ucpsystem(self) -> bool:
        storage_serial_number = self.storage_serial_number
        ucpsystems = self.get_ucpsystems()

        for u in ucpsystems:
            # if u.get("name") == CommonConstants.UCP_NAME:
            for s in u.get("storageDevices"):
                if str(s.get("serialNumber")) == str(storage_serial_number):
                    return s.get("healthState") != CommonConstants.ONBOARDING
        return False

    #  20240822 - VSPVolTieringUAIGateway apply_vol_tiering
    @log_entry_exit
    def apply_vol_tiering(
        self,
        name: str,
        lunId: int,
        is_relocation_enabled: bool,
        tier_level_for_new_page_allocation: bool,
        tier_level: int,
        tier1_allocation_rate_min: int,
        tier1_allocation_rate_max: int,
        tier3_allocation_rate_min: int,
        tier3_allocation_rate_max: int,
    ) -> Dict[str, Any]:

        tierLevelForNewPageAlloc = "L"
        if tier_level_for_new_page_allocation:
            tierLevelForNewPageAlloc = "H"

        end_point = self.end_points.APPLY_VOL_TIERING
        payload = {
            "enableRelocation": is_relocation_enabled,
            "name": "lunId",
            "lunId": lunId,
            "serialNumber": str(self.storage_serial_number),
            "ucpSystem": CommonConstants.UCP_SERIAL,
            "tierLevel": tier_level,
            "tierLevelForNewPageAlloc": tierLevelForNewPageAlloc,
            "tier1AllocRateMax": tier1_allocation_rate_max,
            "tier1AllocRateMin": tier1_allocation_rate_min,
            "tier3AllocRateMax": tier3_allocation_rate_max,
            "tier3AllocRateMin": tier3_allocation_rate_min,
            "shouldAllowDelete": False,
        }

        headers = self._populate_headers()
        self.logger.writeDebug(f"apply_vol_tiering payload: {payload}")
        return self.connection_manager.post(end_point, payload, headers_input=headers)

    def _populate_headers(self) -> Dict[str, str]:
        headers = {"partnerId": CommonConstants.PARTNER_ID}
        # self.logger.writeDebug("168 self.connectionInfo.subscriber_id={}", self.connectionInfo.subscriber_id)
        if self.connectionInfo.subscriber_id is not None:
            headers["subscriberId"] = self.connectionInfo.subscriber_id
        return headers
