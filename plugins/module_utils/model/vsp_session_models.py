from dataclasses import dataclass
from typing import Optional, List

try:
    from .common_base_models import BaseDataClass, SingleBaseClass
except ImportError:
    from .common_base_models import BaseDataClass, SingleBaseClass


@dataclass
class VSPSessionFactSpec(SingleBaseClass):
    id: Optional[str] = None
    token: Optional[str] = None
    comment: Optional[str] = None


@dataclass
class VSPSessionSpec(SingleBaseClass):
    id: Optional[str] = None
    force: Optional[bool] = None
    alive_time_in_seconds: Optional[int] = None
    authentication_timeout: Optional[int] = None
    token: Optional[str] = None


@dataclass
class CreateSessionResponse(SingleBaseClass):
    sessionId: Optional[str] = None
    token: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict


@dataclass
class SessionResponse(SingleBaseClass):
    sessionId: Optional[str] = None
    userId: Optional[str] = None
    ipAddress: Optional[str] = None
    createdTime: Optional[str] = None
    lastAccessTime: Optional[str] = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def camel_to_snake_dict(self):
        camel_dict = super().camel_to_snake_dict()
        return camel_dict


@dataclass
class SessionResponseList(BaseDataClass):
    data: List[SessionResponse] = None
