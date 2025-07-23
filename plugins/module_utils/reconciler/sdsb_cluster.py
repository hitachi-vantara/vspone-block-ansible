import time
import os
from typing import Any

try:
    from ..provisioner.sdsb_cluster_provisioner import SDSBClusterProvisioner
    from ..provisioner.sdsb_storage_node_provisioner import SDSBStorageNodeProvisioner
    from ..common.hv_constants import StateValue
    from ..common.hv_log import Log
    from ..common.ansible_common import (
        log_entry_exit,
        camel_to_snake_case,
        unzip_targz,
    )
    from ..message.sdsb_cluster_msgs import SDSBClusterValidationMsg
except ImportError:
    from provisioner.sdsb_cluster_provisioner import SDSBClusterProvisioner
    from provisioner.sdsb_storage_node_provisioner import SDSBStorageNodeProvisioner
    from common.hv_log import Log
    from common.ansible_common import (
        log_entry_exit,
        camel_to_snake_case,
        unzip_targz,
    )
    from message.sdsb_cluster_msgs import SDSBClusterValidationMsg

logger = Log()


def get_json_for_config_file(file_path):
    result = {}
    current_section = None
    headers = []

    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue  # skip empty lines

            if line.startswith("[") and line.endswith("]"):
                current_section = line[1:-1]
                result[current_section] = []
                headers = []
                continue

            if current_section:
                # Handle the first line of the section as headers
                if not headers:
                    headers = line.split(",")
                    continue

                # Parse data lines
                values = line.split(",")
                row_dict = {
                    headers[i]: values[i] if i < len(values) else ""
                    for i in range(len(headers))
                }
                result[current_section].append(row_dict)

    return result


class SDSBClusterReconciler:

    def __init__(self, connection_info, state=None):
        self.connection_info = connection_info
        self.provisioner = SDSBClusterProvisioner(self.connection_info)
        self.state = state

    @log_entry_exit
    def get_clusters(self, spec=None):
        if spec and spec.query:
            query = spec.query
            if query == "cluster_config":
                return self.get_cluster_config()

    @log_entry_exit
    def get_cluster_config(self):
        dest_folder = self.download_and_unzip_config_file()
        file_name = "SystemConfigurationFile.csv"
        file_path = f"{dest_folder}/{file_name}"
        json_object = get_json_for_config_file(file_path)
        return json_object

    @log_entry_exit
    def reconcile_cluster(self, spec: Any) -> Any:
        state = self.state.lower()
        logger.writeDebug(f"spec = {spec}")
        resp_data = None
        if state == StateValue.ADD_STORAGE_NODE:
            resp_data = self.add_storage_node(spec=spec)
        elif state == StateValue.REMOVE_STORAGE_NODE:
            resp_data = self.remove_storage_node(spec=spec)
        elif state == StateValue.DOWNLOAD_CONFIG_FILE:
            resp_data = self.download_config_file(spec=spec)
        if resp_data:
            return resp_data

    @log_entry_exit
    def add_storage_node(self, spec=None):
        logger.writeDebug(
            f"add_storage_node:spec = {spec} pw = {spec.setup_user_password}"
        )
        if spec.setup_user_password is None:
            raise ValueError(
                SDSBClusterValidationMsg.STORAGE_NODE_SETUP_PASSWD_REQD.value
            )
        if spec.configuration_file:
            if not os.path.isfile(spec.configuration_file):
                raise ValueError(
                    SDSBClusterValidationMsg.CONFIG_FILE_DOES_NOT_EXIST.value.format(
                        spec.configuration_file
                    )
                )

        resp = self.provisioner.add_storage_node(
            spec.config_file, spec.setup_user_password
        )
        msg = f"""
        Successfully started add storage node to the cluster job. This is a long running operation, and might take an hour or so.
        You can check the status of the job started periodically using hv_sds_block_job_facts module.
        ID for this job = {resp}
        """
        return msg

    @log_entry_exit
    def remove_storage_node(self, spec):
        if spec.node_id is None and spec.node_name is None:
            raise ValueError(
                SDSBClusterValidationMsg.NO_NAME_OR_ID_FOR_STORAGE_NODE.value
            )
        try:
            if spec.node_id is None:
                storage_node_prov = SDSBStorageNodeProvisioner(self.connection_info)
                spec.node_id = storage_node_prov.get_node_id_by_node_name(
                    spec.node_name
                )
                if spec.node_id is None:
                    raise ValueError(
                        SDSBClusterValidationMsg.STORAGE_NODE_NOT_FOUND.value.format(
                            spec.node_name
                        )
                    )
            resp = self.provisioner.remove_storage_node(spec.node_id)
            msg = f"""
            Successfully started remove storage node from the cluster job. This is a long running operation, and might take few hours.
            You can check the status of the job started periodically using hv_sds_block_job_facts module.
            ID for this job = {resp}
            """
            return msg
        except Exception as e:
            logger.writeException(e)
            raise Exception(e)

    @log_entry_exit
    def download_and_unzip_config_file(self, spec=None):
        try:
            time_stamp = time.time_ns()
            file_name = f"/tmp/config_file_{time_stamp}.zip"
            self.provisioner.download_config_file(file_name)

            file_to_unzip = file_name
            if spec is None or spec.config_file_location is None:
                destination_folder = f"/tmp/{time_stamp}"
            else:
                destination_folder = spec.config_file_location
            resp = unzip_targz(file_to_unzip, destination_folder)
            if "Successfully" in resp:
                return destination_folder
            else:
                return None
        except Exception as e:
            logger.writeException(e)
            raise Exception(e)

    @log_entry_exit
    def download_config_file(self, spec):
        try:
            resp = self.download_and_unzip_config_file(spec)
            if resp:
                return f"Successfully downloaded SystemConfigurationFile.csv in the directory {resp}."
            else:
                return "Failed to  downloaded SystemConfigurationFile.csv in the directory."
        except Exception as e:
            logger.writeException(e)
            raise Exception(e)


class SDSBClusterExtractor:
    def __init__(self):
        self.common_properties = {
            "id": str,
            "biosUuid": str,
            "protectionDomainId": str,
            "faultDomainId": str,
            "faultDomainName": str,
            "name": str,
            "clusterRole": str,
            "storageNodeAttributes": list,
            "statusSummary": str,
            "status": str,
            "driveDataRelocationStatus": str,
            "controlPortIpv4Address": str,
            "internodePortIpv4Address": str,
            "softwareVersion": str,
            "modelName": str,
            "serialNumber": str,
            "memory": int,
            "insufficientResourcesForRebuildCapacity": dict,
            "rebuildableResources": dict,
            "availabilityZoneId": str,
        }
        self.parameter_mapping = {
            "memory": "memory_mb",
            # "user_object_id": "id",
            # "user_storage_port": "group_names",
        }

    def process_list(self, response_key):
        new_items = []

        if response_key is None:
            return []
        for item in response_key:
            new_dict = {}
            for key, value in item.items():
                key = camel_to_snake_case(key)

                if value is None:
                    # default_value = get_default_value(value_type)
                    # value = default_value
                    continue
                new_dict[key] = value
            new_items.append(new_dict)

        return new_items

    def process_dict(self, response_key):

        if response_key is None:
            return {}

        new_dict = {}
        for key in response_key.keys():
            value = response_key.get(key, None)
            key = camel_to_snake_case(key)

            if value is None:
                # default_value = get_default_value(value_type)
                # value = default_value
                continue
            new_dict[key] = value

        return new_dict

    def extract(self, responses):
        new_items = []

        for response in responses:
            new_dict = {}
            for key, value_type in self.common_properties.items():
                # Get the corresponding key from the response or its mapped key
                response_key = response.get(key)
                # logger.writeDebug("RC:extract:value_type={}", value_type)
                if value_type == list[dict]:
                    response_key = self.process_list(response_key)
                if value_type == dict:
                    response_key = self.process_dict(response_key)
                # Assign the value based on the response key and its data type
                cased_key = camel_to_snake_case(key)
                if cased_key in self.parameter_mapping.keys():
                    cased_key = self.parameter_mapping[cased_key]
                if response_key is not None:
                    new_dict[cased_key] = value_type(response_key)
                else:
                    pass
                    # DO NOT HANDLE MISSING KEYS
                    # Handle missing keys by assigning default values
                    # default_value = get_default_value(value_type)
                    # new_dict[cased_key] = default_value
            new_items.append(new_dict)
        return new_items
