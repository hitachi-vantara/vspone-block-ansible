from enum import Enum


class VSPClprMsg(Enum):

    CLPR_ID_NOT_FOUND = "CLPR with id {} does not exist."
    CLPR_ID_REQD = "CLPR ID cannot be None for delete operation."
    CLPRS_NOT_FOUND = "CLPRs not found for {}."
