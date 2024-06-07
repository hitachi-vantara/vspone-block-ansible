from dataclasses import dataclass, asdict
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass
except ImportError:
    from common_base_models import BaseDataClass


@dataclass
class PortAuthSpec:
    port_name: Optional[str] = None
    state: Optional[str] = None
    target_chap_users: Optional[List[str]] = None
    authentication_mode: Optional[str] = None
    is_discovery_chap_authentication: Optional[bool] = False

@dataclass
class SDSBPortAuthInfo:
    id: str
    authMode: str
    isDiscoveryChapAuth: bool
    isMutualChapAuth: bool

    def to_dict(self):
        return asdict(self)