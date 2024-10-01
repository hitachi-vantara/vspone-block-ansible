from typing import Optional, List, Dict, Any
try:
    from ..common.ansible_common import (
        log_entry_exit,
        camel_to_snake_case,
        get_response_key,
    )
    from ..common.hv_log import Log
    from ..common.hv_constants import *
    from ..provisioner.vsp_nvme_provisioner import VSPNvmeProvisioner


except ImportError:
    from common.ansible_common import (
        log_entry_exit,
        camel_to_snake_case,
        get_response_key,
    )
    from common.hv_log import Log
    from common.hv_constants import *
    from provisioner.vsp_nvme_provisioner import VSPNvmeProvisioner
    # from message.vsp_true_copy_msgs import VSPTrueCopyValidateMsg
    # from model.vsp_true_copy_models import TrueCopySpec


logger = Log()
class VSPNvmeReconciler:
    def __init__(self, connection_info, serial=None, state=None):

        self.connection_info = connection_info
        
        self.provisioner = VSPNvmeProvisioner(connection_info, serial=None)
        if state:
            self.state = state
        if serial:
            self.storage_serial_number = serial


    @log_entry_exit
    def get_nvme_subsystem_facts(self, spec):
        nvme_subsystems = self.provisioner.get_nvme_subsystems(spec)
        logger.writeDebug("RC:nvme_subsystems={}", nvme_subsystems)
        extracted_data = NvmeSubsystemDetailInfoExtractor(self.storage_serial_number).extract(nvme_subsystems.data_to_list())
        return extracted_data
    
    @log_entry_exit
    def get_nvme_subsystems(self, spec):
        nvme_subsystems = self.provisioner.get_nvme_subsystems(spec)
        # extracted_data = TrueCopyInfoExtractor(self.storage_serial_number).extract(tc_pairs)
        # return extracted_data

        return nvme_subsystems

    @log_entry_exit
    def get_nvme_subsystem_by_name(self, name):
        nvme_subsystem = self.provisioner.get_nvme_subsystem_by_name(name)
        return nvme_subsystem
    
    @log_entry_exit
    def get_nvme_subsystem_by_id(self, id):
        nvme_subsystem = self.provisioner.get_nvme_subsystem_by_id(id)
        return nvme_subsystem
    
    @log_entry_exit
    def get_host_nqns(self, nvm_system_id):
        host_nqns = self.provisioner.get_host_nqns(nvm_system_id)
        return host_nqns

    @log_entry_exit
    def get_namespaces(self, nvm_system_id):
        namespaces = self.provisioner.get_namespaces(nvm_system_id)
        return namespaces

    @log_entry_exit
    def get_namespace_paths(self, nvm_system_id):
        namespace_paths = self.provisioner.get_namespaces(nvm_system_id)
        return namespace_paths

    @log_entry_exit
    def get_nvme_ports(self, nvm_system_id):
        nvme_ports = self.provisioner.get_nvme_ports(nvm_system_id)
        return nvme_ports

    @log_entry_exit
    def get_host_nqn(self, host_nqn_id):
        host_nqn = self.provisioner.get_host_nqn(host_nqn_id)
        return host_nqn
    
    @log_entry_exit
    def register_host_nqn(self, nvm_subsystem_id, host_nqn):
        host_nqn = self.provisioner.register_host_nqn(nvm_subsystem_id, host_nqn)
        return host_nqn

    @log_entry_exit
    def set_host_namespace_path(self, nvm_subsystem_id, host_nqn, namespace_id):
        host_ns_path_id = self.provisioner.set_host_namespace_path(nvm_subsystem_id, host_nqn, namespace_id)
        return host_ns_path_id

    @log_entry_exit
    def get_nvme_subsystems_by_namespace(self):
        nvme_subsystems = self.provisioner.get_nvme_subsystems_by_namespace()
        return nvme_subsystems

    @log_entry_exit
    def delete_namespace(self, nvm_subsystem_id, namespace_id):
        ns_data = self.provisioner.delete_namespace(nvm_subsystem_id, namespace_id)
        return ns_data

class NvmeSubsystemDetailInfoExtractor:
    def __init__(self, serial):
        self.storage_serial_number = serial
        self.common_properties = {
            "nvmSubsystemInfo": dict,
            "portInfo": list,
            "namespacesInfo": list,
            "namespacePathsInfo" : list,
            "hostNqnInfo": list,
        }

    @log_entry_exit
    def change_keys(self, response_key):
        new_dict = {}
        if not response_key:
            return new_dict
        for key, value in response_key.items():
            key = camel_to_snake_case(key)
            value_type = type(value)
            if value is None:
                default_value = (
                    ""
                    if value_type == str
                    else (
                        -1
                        if value_type == int
                        else [] if value_type == list else False
                    )
                )
                value = default_value
            new_dict[key] = value
        return new_dict

    def process_list(self, response_key):
        new_items = []
        
        if response_key is None:
            return []
        
        for item in response_key:
            new_dict = {}
            for key, value in item.items():
                key = camel_to_snake_case(key)
                value_type = type(value)
                if value is None:
                    default_value = (
                        ""
                        if value_type == str
                        else (
                            -1
                            if value_type == int
                            else [] if value_type == list else False
                        )
                    )
                    value = default_value
                new_dict[key] = value
            new_items.append(new_dict)
        return new_items
   
    def extract(self, responses):
        new_items = []
        for response in responses:
            new_dict = {"storage_serial_number": self.storage_serial_number}
            for key, value_type in self.common_properties.items():
                # Get the corresponding key from the response or its mapped key
                response_key = response.get(key)
                if value_type == dict:
                    response_key = self.change_keys(response_key)
                if value_type == list:
                    response_key = self.process_list(response_key)
                # Assign the value based on the response key and its data type
                cased_key = camel_to_snake_case(key)
                if response_key is not None:
                    new_dict[cased_key] = value_type(response_key)
                else:
                    # Handle missing keys by assigning default values
                    default_value = (
                        "" if value_type == str else -1 if value_type == int else False
                    )
                    new_dict[cased_key] = default_value
            new_items.append(new_dict)
        return new_items

class NvmeSubsystemInfoExtractor:
    def __init__(self, serial):
        self.storage_serial_number = serial
        self.common_properties = {
            "nvmSubsystemId": int,
            "nvmSubsystemName": str,
            "resourceGroupId": int,
            "namespaceSecuritySetting": str,
            "t10piMode": str,
            "hostMode": str,
        }

    def extract(self, responses):
        new_items = []
        for response in responses:
            new_dict = {"storage_serial_number": self.storage_serial_number}
            for key, value_type in self.common_properties.items():
                # Get the corresponding key from the response or its mapped key
                response_key = response.get(key)
                # Assign the value based on the response key and its data type
                cased_key = camel_to_snake_case(key)
                if response_key is not None:
                    new_dict[cased_key] = value_type(response_key)
                else:
                    # Handle missing keys by assigning default values
                    default_value = (
                        "" if value_type == str else -1 if value_type == int else False
                    )
                    new_dict[cased_key] = default_value
            new_items.append(new_dict)
        return new_items