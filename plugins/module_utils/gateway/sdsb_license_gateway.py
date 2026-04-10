from urllib.parse import urlencode

try:
    from .gateway_manager import SDSBConnectionManager
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..common.sdsb_utils import convert_keys_to_snake_case, replace_nulls
    from ..model.sdsb_license_models import LicenseSettingResponse
except ImportError:
    from .gateway_manager import SDSBConnectionManager
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from common.sdsb_utils import convert_keys_to_snake_case, replace_nulls
    from model.sdsb_license_models import LicenseSettingResponse

GET_LICENSE_SETTING = "v1/objects/license-setting"
MODIFY_LICENSE_SETTING = "v1/objects/license-setting"
GET_LICENSES = "v1/objects/licenses"
GET_LICENSE_BY_ID = "v1/objects/licenses/{}"
DELETE_LICENSE_BY_ID = "v1/objects/licenses/{}"

logger = Log()


class SDSBLicenseGateway:

    def __init__(self, connection_info):
        self.connection_manager = SDSBConnectionManager(
            connection_info.address, connection_info.username, connection_info.password
        )

    @log_entry_exit
    def get_license_setting(self):
        end_point = GET_LICENSE_SETTING
        settings = self.connection_manager.get(end_point)
        logger.writeDebug("GW:get_license_setting:data={}", settings)
        return LicenseSettingResponse(**settings)

    @log_entry_exit
    def modify_license_setting(
        self, warning_threshold_setting, overcapacity_allowed=None
    ):
        logger.writeDebug(
            "GW:modify_license_setting:warning_threshold_setting={}",
            warning_threshold_setting,
        )
        end_point = MODIFY_LICENSE_SETTING
        payload = {
            "warningThresholdSetting": {
                "remainingDays": (
                    warning_threshold_setting.remaining_days
                    if warning_threshold_setting.remaining_days is not None
                    else -1
                ),
                "totalPoolCapacityRate": (
                    warning_threshold_setting.total_pool_capacity_rate
                    if warning_threshold_setting.total_pool_capacity_rate is not None
                    else -1
                ),
            },
        }
        if overcapacity_allowed is not None:
            payload["overcapacityAllowed"] = overcapacity_allowed

        logger.writeDebug("GW:modify_license_setting:payload={}", payload)

        # Perform the patch operation
        patch_result = self.connection_manager.patch(end_point, payload)
        logger.writeDebug("GW:modify_license_setting:patch_result={}", patch_result)

        # Return the updated settings by getting the current state
        return self.get_license_setting()

    key_mapping = {
        "checked_out_license_usage_in_ti_b": "checked_out_license_usage_in_tib",
        "permitted_capacity_in_ti_b": "permitted_capacity_in_tib",
        "total_pool_capacity_in_gi_b": "total_pool_capacity_in_gib",
    }

    def fix_bad_keys(self, obj):
        if isinstance(obj, dict):
            return {self.key_mapping.get(k, k): v for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.fix_bad_keys(item) for item in obj]
        else:
            return obj

    @log_entry_exit
    def fix_license_output(self, license_data):
        snake_case_data = replace_nulls(convert_keys_to_snake_case(license_data))
        fixed_output = self.fix_bad_keys(snake_case_data["data"])
        return fixed_output

    @log_entry_exit
    def get_query_parameters(self, spec):
        params = {}
        if spec.program_product_name:
            params["programProductName"] = spec.program_product_name
        if spec.status:
            params["status"] = spec.status
        if spec.status_summary:
            params["statusSummary"] = spec.status_summary

        query = ""
        if params:
            query = "?" + urlencode(params)

        return query

    @log_entry_exit
    def get_licenses(self, spec=None):
        end_point = GET_LICENSES
        if spec is not None:
            query = self.get_query_parameters(spec)
            end_point = end_point + query
        licenses = self.connection_manager.get(end_point)
        logger.writeDebug("GW:get_licenses:data={}", licenses)

        return self.fix_license_output(licenses)

    @log_entry_exit
    def get_license_by_id(self, id):
        end_point = GET_LICENSE_BY_ID.format(id)
        response = self.connection_manager.get(end_point)
        return response
        # return SdsbLicenseResponse(**response)
        # # Get all licenses
        # all_licenses = self.get_licenses()
        # logger.writeDebug("GW:get_license:all_licenses={}", all_licenses)

        # # Filter by ID
        # if all_licenses:
        #     for license_obj in all_licenses:
        #         if license_obj.id == license_id:
        #             logger.writeDebug("GW:get_license:found={}", license_obj)
        #             return license_obj

        # logger.writeDebug("GW:get_license:not found for id={}", license_id)
        # return None

    @log_entry_exit
    def delete_license(self, license_id):
        if not license_id:
            raise ValueError("license_id is required and cannot be empty")

        logger.writeDebug("GW:delete_license:license_id={}", license_id)

        end_point = DELETE_LICENSE_BY_ID.format(license_id)
        result = self.connection_manager.delete(end_point)
        logger.writeDebug("GW:delete_license:result={}", result)

        return result

    @log_entry_exit
    def create_license(self, key_code):
        if not key_code:
            raise ValueError("key_code is required and cannot be empty")

        logger.writeDebug("GW:create_license:key_code={}", key_code[:20] + "...")

        end_point = GET_LICENSES
        payload = {"keyCode": key_code}
        result = self.connection_manager.post(end_point, payload)
        logger.writeDebug("GW:create_license:result={}", result)

        return result
