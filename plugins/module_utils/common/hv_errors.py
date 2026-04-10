class HvError(Exception):
    """Base class for common exceptions."""

    pass


class HvSocketTimeoutError(HvError):
    """Exception raised when there is a socket timeout error."""

    pass


class HvHttpError(HvError):
    """Exception raised when there is an HTTP error."""

    pass


class HvJobError(HvError):
    """Exception raised when there is an error in a job execution."""

    pass


class HvJobTimeoutError(HvJobError):
    """Exception raised when a job execution exceeds the specified timeout."""

    pass


class HvTokeenGenerationError(HvError):
    """Exception raised when there is an error in token generation."""

    pass


class HvTarFileReadingError(HvError):
    """Exception raised when there is an error reading a tar file."""

    pass


class HVUnknownError(HvError):
    """Exception raised for unknown errors."""

    pass
