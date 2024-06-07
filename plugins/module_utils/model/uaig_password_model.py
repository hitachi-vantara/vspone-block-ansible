from dataclasses import dataclass, asdict
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass
except ImportError:
    from common_base_models import BaseDataClass


@dataclass
class PasswordSpec:
    password: Optional[str] = None
