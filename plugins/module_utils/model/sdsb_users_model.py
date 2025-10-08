from dataclasses import dataclass
from typing import Optional


@dataclass
class SDSBUsersSpec:
    """Block Drives Facts Specification"""

    id: Optional[str] = None
    name: Optional[str] = None
    user_id: Optional[str] = None
    password: Optional[str] = None
    user_group_ids: list[str] = None
    authentication: Optional[str] = None
    is_enabled_console_login: Optional[bool] = None
    new_password: Optional[str] = None
    current_password: Optional[str] = None
    new_password: Optional[str] = None
