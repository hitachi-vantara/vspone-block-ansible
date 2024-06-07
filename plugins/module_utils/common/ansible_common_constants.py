import os
import logging


class LoggingConstants:
    RUN_LOG_FILE = "/var/log/hitachivantara/ansible/storage/hv_storage_modules.log"
    # INTERNAL_LOG_FILE = "/var/log/hitachivantara/ansible/ansible_internal.log"
    RUN_LOG_FORMAT = "%(asctime)s - %(filename)s - %(funcName)s %(lineno)d - %(levelname)s - %(message)s"
    MAX_BYTES = 10 * 1024 * 1024
    BACKUP_COUNT = 5
    PROPAGATE = True

    @staticmethod
    def get_log_level():
        """
        Set the log level as per need in the env variable
        export ANSIBLE_LOG_LEVEL="DEBUG"

        """
        level = os.environ.get("ANSIBLE_LOG_LEVEL")
        if level is None:
            return logging.INFO
        # Convert the level string to a logging level constant
        return getattr(logging, level.upper())
