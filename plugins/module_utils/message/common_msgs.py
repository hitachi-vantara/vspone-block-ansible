from enum import Enum


class CommonMessage(Enum):
    STORAGE_SYSTEM_INFO_MISSING = "missing required arguments: storage_system_info"
    REGISTERED_PRODUCT_MISSING = "Ansible product is not registered. Please register the product using the register.yml playbook."
    SERIAL_NUMBER_NOT_FOUND = "Could not find serial number {} in the UAI Gateway. Please try again or provide the correct serial number."
    USER_CONSENT_MISSING = (
        "Hitachi Vantara LLC is collecting usage data by default for new installations. "
        "This data is used for product improvement only and remains confidential. "
        "To opt out, run the accept_user_consent.yml playbook and answer No. "
        "This reminder will appear up to 3 times; after that, usage data collection stays enabled unless you opt out."
    )
    FAILED_CONNECTION = "Failed to establish a connection, please check the Management System address or the credentials."
    PORTS_JOURNALS_LUNS = "Ports, Journals, Pools, Quorum disks and LUNs information are not supported for storage system facts."

    JOB_TIMEOUT = "Timeout Error! The tasks was not completed in 10 minutes."
