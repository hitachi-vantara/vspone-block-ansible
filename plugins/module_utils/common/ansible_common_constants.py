import os
import logging



##PROJECT DETAILS
NAMESPACE = "hitachivantara"
PROJECT_NAME = "vspone_block"



#LOGGING CONSTANTS
ANSIBLE_LOG_PATH = os.environ.get("HV_ANSIBLE_LOG_PATH", os.path.expanduser(f"~/logs/{NAMESPACE}/ansible/{PROJECT_NAME}"))
LOGGER_LEVEL = os.getenv('HV_ANSIBLE_LOG_LEVEL', 'INFO').upper()
LOGFILE_NAME =  os.getenv('HV_ANSIBLE_LOG_FILE', "hv_vspone_block_modules.log")
ROOT_LEVEL =  os.getenv('HV_ANSIBLE_ROOT_LEVEL', "INFO").upper()


