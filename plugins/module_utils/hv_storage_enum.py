from re import match

try:
    from enum import Enum

    class StorageType(Enum):
        UNKNOWN = 0
        VSP = 4
        VSP_G1000 = 6
        VSP_GX00 = 7
        VSP_FX00 = 8
        VSP_G1500 = 9
        VSP_F1500 = 10
        VSP_5X00 = 12
        VSP_5X00H = 13
        VSP_EX90 = 14

        @classmethod
        def fromString(cls, value):
            for storage_type in cls:
                if match(storage_type.name.replace("X", ".") + "$", value.upper()):
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
        VSP = 1
        VSP_G200 = 2
        VSP_G400_G600 = 3
        VSP_G800 = 4
        VSP_G400 = 5
        VSP_G600 = 6
        VSP_G350 = 7
        VSP_G370 = 8
        VSP_G700 = 9
        VSP_G900 = 10
        VSP_G130 = 11
        VSP_G150 = 12
        VSP_5100 = 13
        VSP_5500 = 14
        VSP_E990 = 15
        VSP_F400 = 16
        VSP_F600 = 17
        VSP_F800 = 18
        VSP_F350 = 19
        VSP_F370 = 20
        VSP_F700 = 21
        VSP_F900 = 22
        VSP_N400_N600 = 23
        VSP_N400 = 24
        VSP_N600 = 25
        VSP_N800 = 26
        VSP_5100H = 27
        VSP_5500H = 28
        VSP_G1000 = 29
        VSP_G1500 = 30
        VSP_F1500 = 31
        XP7 = 32
        XP8 = 33

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

    class RG_StorageModel(Enum):
        UNKNOWN = 0
        VSP_G200 = 1
        VSP_G400 = 2
        VSP_G400_G600 = 3
        VSP_G600 = 4
        VSP_G800 = 5
        VSP_F400 = 6
        VSP_F400_F600 = 7
        VSP_F600 = 8
        VSP_F800 = 9
        VSP_G130 = 10
        VSP_G150 = 11
        VSP_G350 = 12
        VSP_F350 = 13
        VSP_G370 = 14
        VSP_F370 = 15
        VSP_G700 = 16
        VSP_G900 = 17
        VSP_F900 = 18
        VSP_E990 = 19
        VSP = 20
        VSP_G1000 = 21
        VSP_G1500 = 22
        VSP_F1500 = 23
        VSP_NX00 = 24
        VSP_5X00 = 25
        VSP_5X00H = 26

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

    class SNAPSHOT_OPTION_ENUM:
        nameValues = [
            "SSOPTION_HIDE_AND_DISABLE_ACCESS",  # 0
            "SSOPTION_HIDE_AND_ALLOW_ACCESS",  # 1
            "",  # 2
            "SSOPTION_SHOW_AND_ALLOW_ACCESS",  # 3
        ]

        @staticmethod
        def getValueNum(name):
            if name not in SNAPSHOT_OPTION_ENUM.nameValues:
                return 0

            return SNAPSHOT_OPTION_ENUM.nameValues.index(name)

        @staticmethod
        def getName(num):
            return SNAPSHOT_OPTION_ENUM.nameValues[num]

    class RG_StorageType(Enum):
        VSP = 0
        VSP_G1000 = 1
        VSP_GX00 = 2
        VSP_FX00 = 3
        VSP_G1500 = 4
        VSP_F1500 = 5
        VSP_NX00 = 6
        VSP_5X00 = 7
        VSP_5X00H = 8
        VSP_EX00 = 9
        UNKNOWN = 10

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

    class NODE_STATUS_ENUM:
        nameValues = [
            "INVALID",  # 0
            "UNKNOWN",  # 1
            "UP",  # 2
            "ONLINE",  # 2
            "NOTUP",  # 2
            "DEAD",  # 2
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

    class CLUSTER_HEALTH_ENUM:
        nameValues = [
            "ROBUST",  # 0
            "DEGRADED",  # 1
            "CRITICAL",  # 2
        ]

        @staticmethod
        def getValueNum(name):
            if name not in CLUSTER_HEALTH_ENUM.nameValues:
                return 0

            return CLUSTER_HEALTH_ENUM.nameValues.index(name)

        @staticmethod
        def getName(num):
            return CLUSTER_HEALTH_ENUM.nameValues[num]

    class LOCAL_READ_CACHE_OPTION_ENUM:
        nameValues = [
            "DISABLED",  # 0
            "ENABLEDFORALLFILES",  # 1
            "ENABLEDFORTAGGEDFILES",  # 2
            "ENABLEDFORCVLS",  # 3
        ]

        @staticmethod
        def getValueNum(name):
            if name not in LOCAL_READ_CACHE_OPTION_ENUM.nameValues:
                return 0

            return LOCAL_READ_CACHE_OPTION_ENUM.nameValues.index(name)

        @staticmethod
        def getName(num):
            return LOCAL_READ_CACHE_OPTION_ENUM.nameValues[num]

    class TRANSFER_TO_REPLICATION_TARGET_SETTING_ENUM:
        nameValues = [
            "DONOTTRANSFER",  # 0
            "TRANSFER",  # 1
            "USEFSDEFAULT",  # 2
            "INVALID",  # 3
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
            "TI": 1,
            "HDP": 2,
            "DP": 2,
            "HDT": 3,
            "HDT_AF": 4,
        }

        @classmethod
        def fromString(cls, value):
            if value.upper() in cls.types:
                return cls.types[value.upper()]
            else:
                raise Exception(
                    "Invalid {0} type: {1}".format(cls.__name__, value.upper())
                )

    class PoolType(Enum):
        UNKNOWN = 0
        HDP = 1
        SNAPSHOT = 2
        HDT = 3
        HTI = 4
        DATAPOOL = 5
        HDT_AF = 6

        # Enum aliases
        DP = 1
        TI = 4

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
            "UNKNOWN",  # 0
            "NORMAL",  # 1
            "OVERTHRESHOLD",  # 2
            "SUSPENDED",  # 3
            "FAILURE",  # 4
            "SHRINKING",  # 5
            "REGRESSED",  # 6
            "DETACHED",  # 7
        ]

        @classmethod
        def getValueNum(cls, name):
            if name not in cls.values:
                return 0

            return cls.values.index(name)

        @classmethod
        def getName(cls, num):
            return cls.values[num]

except ImportError:

    # Output expected ImportErrors.

    pass
