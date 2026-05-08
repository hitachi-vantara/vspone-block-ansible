from enum import Enum


class VspStorageSystemMsg(Enum):
    ONLY_SUPPORTED_ON_BHE = (
        "This module is only supported on VSP One Block High End (e.g. B85) models."
    )
