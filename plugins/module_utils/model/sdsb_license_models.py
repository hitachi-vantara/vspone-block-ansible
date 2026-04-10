from dataclasses import dataclass
from typing import Optional

try:
    from .common_base_models import SingleBaseClass
    from ..common.ansible_common import replace_nulls
except ImportError:
    from .common_base_models import SingleBaseClass
    from common.ansible_common import replace_nulls


@dataclass
class WarningThresholdSettingSpec(SingleBaseClass):
    remaining_days: Optional[int] = None
    total_pool_capacity_rate: Optional[int] = None


@dataclass
class LicenseManagementSpec(SingleBaseClass):
    warning_threshold_setting: Optional[WarningThresholdSettingSpec] = None
    allow_over_capacity: Optional[bool] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.__post_init__()

    def __post_init__(self):
        if self.warning_threshold_setting:
            self.warning_threshold_setting = WarningThresholdSettingSpec(
                **self.warning_threshold_setting
            )


@dataclass
class LicenseSpec(SingleBaseClass):
    id: Optional[str] = None
    key_code: Optional[str] = None
    comments: Optional[str] = None


@dataclass
class SDSBLicenseFactsSpec(SingleBaseClass):
    id: Optional[str] = None
    program_product_name: Optional[str] = None
    status: Optional[str] = None
    status_summary: Optional[str] = None
    comments: Optional[str] = None


@dataclass
class WarningThresholdSettingOfLicenseSetting(SingleBaseClass):
    remainingDays: Optional[int] = None
    totalPoolCapacityRate: Optional[int] = None


@dataclass
class LicenseSettingResponse(SingleBaseClass):
    warningThresholdSetting: Optional[WarningThresholdSettingOfLicenseSetting] = None
    overcapacityAllowed: Optional[bool] = None

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if "warningThresholdSetting" in kwargs:
            self.warningThresholdSetting = WarningThresholdSettingOfLicenseSetting(
                **self.warningThresholdSetting
            )

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        if self.warningThresholdSetting:
            camel_dict["warning_threshold_setting"] = (
                self.warningThresholdSetting.camel_to_snake_dict()
            )
        return replace_nulls(camel_dict)
