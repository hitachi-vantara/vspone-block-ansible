from dataclasses import dataclass
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass
except ImportError:
    from common_base_models import BaseDataClass, SingleBaseClass


@dataclass
class SpmFactSpec:
    ldev_id: Optional[int] = None
    host_wwn: Optional[str] = None
    iscsi_name: Optional[str] = None

    def is_empty(self):
        if self.ldev_id is None and self.host_wwn is None and self.iscsi_name is None:
            return True
        else:
            return False


@dataclass
class SpmSpec:
    ldev_id: Optional[int] = None
    host_wwn: Optional[str] = None
    iscsi_name: Optional[str] = None
    upper_limit_for_iops: Optional[int] = None
    upper_limit_for_transfer_rate_in_MBps: Optional[int] = None

    def is_empty(self):
        if (
            self.ldev_id is None
            and self.host_wwn is None
            and self.iscsi_name is None
            and self.upper_limit_for_iops is None
            and self.upper_limit_for_transfer_rate_in_MBps is None
        ):
            return True
        else:
            return False


@dataclass
class SpmSetObject:
    ldev_id: Optional[int] = None
    host_wwn: Optional[str] = None
    iscsi_name: Optional[str] = None
    upper_limit_for_iops: Optional[int] = None
    upper_limit_for_transfer_rate_in_MBps: Optional[int] = None


@dataclass
class SpmChangeObject:
    upper_limit_for_iops: Optional[int] = None
    upper_limit_for_transfer_rate_in_MBps: Optional[int] = None


@dataclass
class ServerPriorityManagerInfo(SingleBaseClass):
    ioControlLdevWwnIscsiId: Optional[str] = None
    ldevId: Optional[int] = None
    hostWwn: Optional[str] = None
    iscsiName: Optional[str] = None
    priority: Optional[str] = None
    upperLimitForIops: Optional[int] = None
    upperLimitForTransferRate: Optional[int] = None


@dataclass
class ServerPriorityManagerInfoList(BaseDataClass):
    data: List[ServerPriorityManagerInfo] = None
