from enum import Enum


class SDSBEncryptionKeyValidationMsg(Enum):
    KEY_NOT_FOUND = "Encryption key not found with the specified ID."
    INVALID_KEY_ID = "Invalid encryption key ID format."
    INVALID_NUMBER_OF_KEYS = "Number of keys must be between 1 and 4096."
    UNSUPPORTED_STATE = "The requested state '{}' is not supported for encryption keys. Supported states are 'present', and 'absent'."
    OPERATION_FAILED = "The operation on the encryption key failed due to an unexpected error. Please check the logs for more details."
    NOT_ABLE_TO_CREATE_KEY = "Could not create Encryption key. Cause = {}"
    DELETE_KEY_SUCCESS = "Encryption key '{}' deleted successfully."
    KEY_DOSE_NOT_EXIST = "Encryption key '{}' does not exist."
