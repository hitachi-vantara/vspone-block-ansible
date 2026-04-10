class VspError(Exception):
    """Base class for all VSP related exceptions."""

    pass


class VspRestApiError(VspError):
    """Exception raised when there is an error in VSP REST API call."""

    pass


class VspFeatureNotSupportedError(VspError):
    """Exception raised when a requested feature is not supported."""

    pass


class VspVolumeCreationError(VspError):
    """Exception raised for errors during volume creation."""

    pass


class VspVolumeNoFreeLdevError(VspError):
    """Exception raised when there are no free LDEVs available for volume creation."""

    pass


class VspVolumeNotFoundError(VspError):
    """Exception raised when a specified volume is not found."""

    pass


class VspVolumeFeatureNotSupportedError(VspError):
    """Exception raised when a specified volume feature is not supported."""

    pass


class VspShadowImageDuplicateError(VspError):
    """Exception raised when a duplicate shadow image is detected."""

    pass


class VspShadowImageUnexpectedError(VspError):
    """Exception raised for unexpected errors during shadow image operations."""

    pass


class VspPortNotFoundError(VspError):
    """Exception raised when a specified port is not found."""

    pass


class VspHostGroupCreationError(VspError):
    """Exception raised when there is an error creating a host group."""

    pass


class VspHostGroupDeleteError(VspError):
    """Exception raised when there is an error deleting a host group."""

    pass


class VspClprIdNotFoundError(VspError):
    """Exception raised when a specified CLPR ID is not found."""

    pass


class VspLocalCopyGroupNotFoundError(VspError):
    """Exception raised when a specified local copy group is not found."""

    pass


class VspNoFreeHostGroupError(VspError):
    """Exception raised when there are no free host groups available."""

    pass


class VspHostModelNotSupportedError(VspError):
    """Exception raised when the host model is not supported."""

    pass


class VspGadSecondaryVolumeOperationError(VspError):
    """Exception raised when there is an error performing an operation on a GAD secondary volume."""

    pass


class VspSessionTokenGenerationError(VspError):
    """Exception raised when there is an error generating a VSP session token."""

    pass
