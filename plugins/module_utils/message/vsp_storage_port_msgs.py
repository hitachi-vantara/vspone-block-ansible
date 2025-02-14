from enum import Enum


class VSPStoragePortValidateMsg(Enum):
    PORT_MODE_LUN_SECURITY_COMBINATION = "The port_mode and enable_port_security parameters cannot be used together. Use one or the other."
    VALID_PORT_ID = "The port parameter is invalid. The value must be provided in the format of 'CLx-PORTx'."
