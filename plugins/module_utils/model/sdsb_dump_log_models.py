from dataclasses import dataclass
from typing import Optional, List

from .common_base_models import BaseDataClass, SingleBaseClass


BASE_MODES = ["Base", "Memory", "Monitor", "All"]


@dataclass
class CreateDumpFileSpec(SingleBaseClass):
    label: Optional[str] = None
    mode: Optional[str] = None
    file_name: Optional[str] = None
    split_files_index: Optional[int] = None
    file_path: Optional[str] = None

    def __post_init__(self):
        if self.mode is not None and self.mode.capitalize() not in BASE_MODES:
            raise ValueError(
                f"Invalid base mode, Select from {BASE_MODES} {self.mode} and it's case insensitive"
            )
        if self.mode is not None:
            self.mode = self.mode.capitalize()


@dataclass
class DownloadDumpFileSpec(SingleBaseClass):
    file_id: Optional[str] = None
    destination_path: Optional[str] = None
    file_name: Optional[str] = None
    file_path: Optional[str] = None


@dataclass
class IssueAuthTicketSpec(SingleBaseClass):
    max_age_days: Optional[int] = None


@dataclass
class DumpLogStatusSpec(SingleBaseClass):
    include_all_status: Optional[bool] = None


@dataclass
class DumpLogStatusResponse(SingleBaseClass):
    startedTime: Optional[str] = None
    completedTime: Optional[str] = None
    label: Optional[str] = None
    status: Optional[str] = None
    size: Optional[int] = None
    triggerType: Optional[str] = None
    mode: Optional[str] = None
    fileName: Optional[str] = None
    numberOfSplitFiles: Optional[int] = None
    error: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


@dataclass
class AllDumpLogStatusResponse(BaseDataClass):
    data: List[DumpLogStatusResponse] = None
