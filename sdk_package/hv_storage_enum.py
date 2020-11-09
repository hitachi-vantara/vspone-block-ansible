from enum import Enum
from re import match

class StorageType(Enum):
    UNKNOWN = 0
    VSP = 4
    VSP_G1000 = 6
    VSP_GX00 = 7
    VSP_FX00 = 8
    VSP_G1500 = 9
    VSP_F1500 = 10
    VSP_5X00 = 12

    @classmethod
    def fromString(cls, value):
        for storage_type in cls:
            if match(storage_type.name.replace('X', '.') + '$', value.upper()):
                return storage_type
        return cls.UNKNOWN

    @classmethod
    def parse(cls, value):
        try:
            storage_type = cls(value)
        except ValueError:
            storage_type = cls.UNKNOWN
        return storage_type


class StorageModel(Enum):
    UNKNOWN = 0
    VSP_G200 = 1
    VSP_G800 = 3
    VSP_G400 = 4
    VSP_G600 = 5
    VSP_G350 = 6
    VSP_G370 = 7
    VSP_G700 = 8
    VSP_G900 = 9
    VSP_G130 = 10
    VSP_G150 = 11
    VSP_5100 = 12
    VSP_5500 = 13
    VSP_F400 = 15
    VSP_F600 = 16
    VSP_F800 = 17
    VSP_F350 = 18
    VSP_F370 = 19
    VSP_F700 = 20
    VSP_F900 = 21
    VSP = 54
    VSP_G1000 = 55
    VSP_G1500 = 56
    VSP_F1500 = 57

    @classmethod
    def fromString(cls, value):
        if value.upper() in cls.__members__:
            return cls[value.upper()]
        else:
            return cls.UNKNOWN

    @classmethod
    def parse(cls, value):
        try:
            model = cls(value)
        except ValueError:
            model = cls.UNKNOWN
        return model

class SNAPSHOT_OPTION_ENUM():
    nameValues = [
        "SSOPTION_HIDE_AND_DISABLE_ACCESS",  # 0
        "SSOPTION_HIDE_AND_ALLOW_ACCESS",    # 1
        "",                                  # 2
        "SSOPTION_SHOW_AND_ALLOW_ACCESS",    # 3
    ]

    @staticmethod
    def getValueNum(name):
        
        if name not in SNAPSHOT_OPTION_ENUM.nameValues:
            return 0

        return SNAPSHOT_OPTION_ENUM.nameValues.index(name)

    @staticmethod
    def getName(num):
        return SNAPSHOT_OPTION_ENUM.nameValues[num]

class NODE_STATUS_ENUM():
    nameValues = [
        "INVALID",                  # 0
        "UNKNOWN",        # 1
        "UP",     # 2
        "ONLINE",     # 2
        "NOTUP",     # 2
        "DEAD",     # 2
        "DORMANT",
    ]

    @staticmethod
    def getValueNum(name):
        
        if name not in NODE_STATUS_ENUM.nameValues:
            return 0

        return NODE_STATUS_ENUM.nameValues.index(name)

    @staticmethod
    def getName(num):
        return NODE_STATUS_ENUM.nameValues[num]
    
        
class CLUSTER_HEALTH_ENUM():
    nameValues = [
        "ROBUST",                  # 0
        "DEGRADED",        # 1
        "CRITICAL",     # 2
    ]

    @staticmethod
    def getValueNum(name):
        
        if name not in CLUSTER_HEALTH_ENUM.nameValues:
            return 0

        return CLUSTER_HEALTH_ENUM.nameValues.index(name)

    @staticmethod
    def getName(num):
        return CLUSTER_HEALTH_ENUM.nameValues[num]
    
        
class LOCAL_READ_CACHE_OPTION_ENUM():
    nameValues = [
        "DISABLED",                  # 0
        "ENABLEDFORALLFILES",        # 1
        "ENABLEDFORTAGGEDFILES",     # 2
        "ENABLEDFORCVLS",            # 3
    ]

    @staticmethod
    def getValueNum(name):
        
        if name not in LOCAL_READ_CACHE_OPTION_ENUM.nameValues:
            return 0

        return LOCAL_READ_CACHE_OPTION_ENUM.nameValues.index(name)

    @staticmethod
    def getName(num):
        return LOCAL_READ_CACHE_OPTION_ENUM.nameValues[num]
    
        
class TRANSFER_TO_REPLICATION_TARGET_SETTING_ENUM():
    nameValues = [
        "DONOTTRANSFER",    # 0
        "TRANSFER",         # 1
        "USEFSDEFAULT",     # 2
        "INVALID",          # 3
    ]

    @staticmethod
    def getValueNum(name):
        
        if name not in TRANSFER_TO_REPLICATION_TARGET_SETTING_ENUM.nameValues:
            return 0

        return TRANSFER_TO_REPLICATION_TARGET_SETTING_ENUM.nameValues.index(name)

    @staticmethod
    def getName(num):
        return TRANSFER_TO_REPLICATION_TARGET_SETTING_ENUM.nameValues[num]



class PoolCreateType:
    types = {
        "SNAPSHOT": 0,
        "HTI": 1,
        "TI":  1,
        "HDP": 2,
        "DP":  2,
        "HDT": 3,
        "HDT_AF": 4,
    }

    @classmethod
    def fromString(cls, value):
        if value.upper() in cls.types:
            return cls.types[value.upper()]
        else:
            raise Exception("Invalid {} type: {}".format(cls.__name__, value.upper()))

class PoolType(Enum):
    UNKNOWN  = 0
    HDP      = 1
    SNAPSHOT = 2
    HDT      = 3
    HTI      = 4
    DATAPOOL = 5
    HDT_AF   = 6

    # Enum aliases
    DP       = 1
    TI       = 4

    @classmethod
    def fromValue(cls, value):
        enums = [e for e in cls if e.value == value]
        return enums[0] if enums else None
    
    @classmethod
    def fromString(cls, value):
        if value.upper() in cls.__members__:
            return cls[value.upper()]
        else:
            return cls.UNKNOWN

    @classmethod
    def parse(cls, value):
        try:
            model = cls(value)
        except ValueError:
            model = cls.UNKNOWN
        return model

class PoolStatus:
    values = [
        "UNKNOWN",      # 0
        "NORMAL",       # 1
        "OVERTHRESHOLD",# 2
        "SUSPENDED",    # 3
        "FAILURE",      # 4
        "SHRINKING",    # 5
        "REGRESSED",    # 6
        "DETACHED"      # 7
    ]

    @classmethod
    def getValueNum(cls, name):
        
        if name not in cls.values:
            return 0

        return cls.values.index(name)

    @classmethod
    def getName(cls, num):
        return cls.values[num]