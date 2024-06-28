from logging.handlers import RotatingFileHandler
import os
import logging
import functools
import sys
import re
from typing import List


try:
    from .vsp_constants import PEGASUS_MODELS
    from .hv_constants import TARGET_SUB_DIRECTORY
    from .ansible_common_constants import ANSIBLE_LOG_PATH, LOGFILE_NAME
except ImportError:
    from hv_constants import TARGET_SUB_DIRECTORY
    from vsp_constants import PEGASUS_MODELS


def get_logger_file():
    return os.path.join(ANSIBLE_LOG_PATH, LOGFILE_NAME)

def get_logger_dir():
    return ANSIBLE_LOG_PATH

def snake_to_camel_case(string):
    # Split the string into words using '_' as delimiter
    parts = string.split("_")
    # Capitalize the first letter of each word except the first one
    camel_case_string = parts[0] + "".join(word.capitalize() for word in parts[1:])
    # camel_case_string = ''.join([word.capitalize() for word in words])
    return camel_case_string


def camel_to_snake_case(string):
    # Use regular expressions to find all occurrences of capital letters
    # followed by lowercase letters or digits
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    # Replace the capital letters with '_' followed by lowercase letters
    # using re.sub() function
    snake_case_string = pattern.sub("_", string).lower()
    return snake_case_string


def camel_array_to_snake_case(a):
    newArr = []
    for i in a:
        if isinstance(i, list):
            newArr.append(camel_array_to_snake_case(i))
        elif isinstance(i, dict):
            newArr.append(camel_dict_to_snake_case(i))
        else:
            newArr.append(i)
    return newArr


def camel_dict_to_snake_case(j):
    out = {}
    for k in j:
        newK = camel_to_snake_case(k)
        if isinstance(j[k], dict):
            out[newK] = camel_dict_to_snake_case(j[k])
        elif isinstance(j[k], list):
            out[newK] = camel_array_to_snake_case(j[k])
        else:
            out[newK] = j[k]
    return out


def convert_hex_to_dec(hex):
    if ":" in hex:
        hex = hex.replace(":", "")
    try:
        return int(hex, 16)
    except ValueError:
        return None


def dicts_to_dataclass_list(data: List[dict], clsName: type) -> List:
    if data is not None:
        return [clsName(**item) for item in data]
    return None


def convert_block_capacity(bytes_size: int, block_size=512) -> str:
    units = ["B", "KB", "MB", "GB", "TB"]
    factor = 1024
    size = bytes_size * block_size

    for unit in units:
        if size < factor:
            return f"{size:.2f}{unit}"
        size /= factor
    return f"{size:.2f}PB"  # If the size exceeds TB, assume it's in petabytes


def convert_to_bytes(size_str: str, block_size=512) -> int:
    size_str = (
        size_str.strip().upper()
    )  # Convert the string to uppercase for case-insensitivity
    units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}

    # Split the size string into value and unit
    value, unit = size_str[:-2], size_str[-2:]
    try:
        value = int(value)
        return (value * units[unit]) / block_size
    except (ValueError, KeyError):
        raise ValueError("Invalid size format")


def log_entry_exit(func):
    try:
        from .hv_log import Log
    except ImportError:
        from hv_log import Log

        ##importing here to avoid circular import error
    # This is helper functions to log and handle exception from each level
    logger = Log()

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        module_name = func.__module__
        func_name = func.__name__

        logger.writeEnter(f"{module_name}:{func_name}")

        result = func(*args, **kwargs)

        logger.writeExit(f"{module_name}:{func_name}")
        return result

    return wrapper


def process_size_string(size_str: str) -> str:
    size_str = size_str.upper()  # Convert to uppercase for case-insensitivity
    size_str = size_str.replace(" ", "")  # Remove white spaces
    if "MB" in size_str or "GB" in size_str or "TB" in size_str:
        size_str = size_str.replace("B", "")  # Remove 'B' if present
    else:
        size_str += "M"  # Append 'M' if none of MB, GB, TB are present
    return size_str


def get_response_key(response, *keys):
    for key in keys:
        response_key = response.get(key)
        if response_key is not None:
            return response_key
    return None


def get_ansible_home_dir():
    # Define the base directories to check
    ansible_base_dirs = [
        os.path.expanduser("~/.ansible/collections"),
        "/usr/share/ansible/collections",
    ]

    # Define the target subdirectory to look for

    # Iterate over the base directories to find the target subdirectory
    for base_dir in ansible_base_dirs:
        target_dir = os.path.join(base_dir, TARGET_SUB_DIRECTORY)
        if os.path.exists(target_dir):
            return target_dir

    # Fallback to determining the directory from the current file's location
    abs_path = os.path.dirname(os.path.abspath(__file__))
    split_path = abs_path.split("plugins")[0]

    for base in ansible_base_dirs:
        target_dir = os.path.join(base, split_path)
        if os.path.exists(target_dir):
            return target_dir

    # If none of the directories exist, return the default user-specific directory
    return os.path.join(ansible_base_dirs[0], TARGET_SUB_DIRECTORY)


def operation_constants(state):
    if state == "present":
        return "created"
    elif state == "absent":
        return "deleted"
    else:
        return state


def volume_id_to_hex_format(vol_id):
    hex_format = None

    # Split the hex value to string
    hex_value = format(vol_id, "06x")
    # Convert hexadecimal to 00:00:00 format
    part1_hex = hex_value[:2]
    part2_hex = hex_value[2:4]
    part3_hex = hex_value[4:6]

    # Combine the hexadecimal values into the desired format
    hex_format = f"{part1_hex}:{part2_hex}:{part3_hex}"

    return hex_format


def is_pegasus_model(storage_info) -> bool:
    return any(sub in storage_info.model for sub in PEGASUS_MODELS)
