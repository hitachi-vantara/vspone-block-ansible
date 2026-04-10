from enum import Enum


class SDSBJobValidationMsg(Enum):

    INVALID_COUNT = (
        "Invalid count information provided. It must be in the range 1 to 100."
    )
    NO_JOB_FOR_ID = "No job found for the provided job ID '{}'."
    NO_JOBS_FOUND = "No jobs found for the specified criteria."
    BAD_ENTRY = "Entries specified in the input might be wrong, please check them and run again."
