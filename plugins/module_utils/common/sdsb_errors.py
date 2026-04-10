class SdsbError(Exception):
    """Base class for all VSP related exceptions."""

    pass


class SdsbRestApiError(SdsbError):
    """Exception raised when there is an error creating the audit log file."""

    pass


class SdsbAuditLogFileCreationError(SdsbError):
    """Exception raised when there is an error creating the audit log file."""

    pass


class SdsbVolumeCreationError(SdsbError):
    """Exception raised for errors during volume creation."""

    pass


class SdsbDownloadConfigFileError(SdsbError):
    """Exception raised when there is an error downloading the config file."""

    pass


class SdsbChapUserCreationError(SdsbError):
    """Exception raised when there is an error creating CHAP user."""

    pass


class SdsbSnmpUpdateError(SdsbError):
    """Exception raised when there is an error updating SNMP settings."""

    pass
