from enum import Enum


class SDSBEncryptionKeySettingMsg(Enum):
    UNSUPPORTED_STATE = "The requested state '{}' is not supported for encryption key settings. Supported state is 'present'."
