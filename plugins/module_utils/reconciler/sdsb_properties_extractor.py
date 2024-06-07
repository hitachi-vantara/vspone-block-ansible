from abc import ABC, abstractmethod

try:
    from ..common.ansible_common import (
        camel_to_snake_case,
        camel_array_to_snake_case,
        camel_dict_to_snake_case,
        log_entry_exit,
    )
    from ..common.hv_log import Log
    from ..model.sdsb_volume_models import *
    from ..model.sdsb_port_models import *
except:
    from common.ansible_common import (
        camel_to_snake_case,
        camel_array_to_snake_case,
        camel_dict_to_snake_case,
        log_entry_exit,
    )
    from common.hv_log import Log
    from model.sdsb_volume_models import *
    from model.sdsb_port_models import *

logger = Log()

class SDSBBasePropertiesExtractor(ABC):
    def __init__(self):
        self.common_properties = {}
        self.parameter_mapping = {}
        self.size_properties = ("total_capacity", "used_capacity")

    @log_entry_exit
    def change_size_keys(self, response_key):
        new_dict = {}

        for key, value in response_key.items():
            key = camel_to_snake_case(key)
            if key in self.size_properties:
                new_key = key + "_mb"
                new_dict[new_key] = value
            else:
                value_type = type(value)
                # logger.writeDebug('RC:extract:change_size_keys:key={} value_type2 = {}', key, type(value))
                if value_type == dict:
                    value = self.change_size_keys(value)
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

    @log_entry_exit
    def extract(self, responses):
        new_items = []
        for response in responses:
            new_dict = {}
            for key, value_type in self.common_properties.items():

                # Get the corresponding key from the response or its mapped key
                response_key = response.get(key)
                if value_type == dict:
                    response_key = self.change_size_keys(response_key)
                # logger.writeDebug('RC:extract:self.size_properties = {}', self.size_properties)
                logger.writeDebug('RC:extract:key = {} response_key={}', key, response_key)
                logger.writeDebug('RC:extract:value_type={}', value_type)
                # Assign the value based on the response key and its data type
                key = camel_to_snake_case(key)
                if response_key is not None:
                    if key in self.size_properties: 
                        new_key = key + "_mb"
                        new_dict[new_key] = value_type(response_key)
                    else:
                        new_dict[key] = value_type(response_key)
                        logger.writeDebug('RC:extract:value_type(response_key)={}', value_type(response_key))
                else:
                    # Handle missing keys by assigning default values
                    default_value = (
                        ""
                        if value_type == str
                        else (
                            -1
                            if value_type == int
                            else [] if value_type == list else False
                        )
                    )
                    new_dict[key] = default_value
            new_items.append(new_dict)
        new_items = camel_array_to_snake_case(new_items)
        return new_items

    @log_entry_exit
    def extract_dict(self, response):
        new_dict = {}
        for key, value_type in self.common_properties.items():
            # Get the corresponding key from the response or its mapped key
            response_key = None
            if key in response:
                response_key = response.get(key)
                if value_type == dict:
                    response_key = self.change_size_keys(response_key)
            # Assign the value based on the response key and its data type
            cased_key = camel_to_snake_case(key)
            if response_key is not None:
                new_dict[cased_key] = value_type(response_key)
        new_dict = camel_dict_to_snake_case(new_dict)
        return new_dict


class ComputeNodePropertiesExtractor(SDSBBasePropertiesExtractor):
    def __init__(self):
        self.common_properties = {
            "id": str,
            "nickname": str,
            "osType": str,
            "totalCapacity": int,
            "usedCapacity": int,
            "numberOfPaths": int,
            "vpsId": str,
            "vpsName": str,
            "numberOfVolumes": int,
            "lun": int,
            "paths": list,
        }

        self.size_properties = ("total_capacity", "used_capacity")

class ComputePortPropertiesExtractor(SDSBBasePropertiesExtractor):
    def __init__(self):
        self.common_properties = {
            "id": str,
            "protocol": str,
            "type": str,
            "name": str,
            "nickname": str,
            "configuredPortSpeed": str,
            "portSpeed": str,
            "portSpeedDuplex": str,
            "protectionDomainId": str,
            "storageNodeId": str,
            "interfaceName": str,
            "statusSummary": str,
            "status": str,
            # "fcInformation": str,
            # "nvmeTcpInformation": str,
            "iscsiInformation": dict,
        }
        self.size_properties = ("total_capacity", "used_capacity")

class PortDetailPropertiesExtractor(SDSBBasePropertiesExtractor):
    def __init__(self):
        self.common_properties = {
            "portInfo": dict,
            "portAuthInfo": dict,
            "chapUsersInfo": list,
        }
        self.size_properties = ("total_capacity", "used_capacity")

class VolumeAndComputeNodePropertiesExtractor(SDSBBasePropertiesExtractor):
    def __init__(self):
        self.common_properties = {
            "volumeInfo": dict,
            "computeNodeInfo": list,
        }
        self.size_properties = ("total_capacity", "used_capacity")

class ComputeNodeAndVolumePropertiesExtractor(SDSBBasePropertiesExtractor):
    def __init__(self):
        self.common_properties = {
            "computeNodeInfo": dict,
            "volumeInfo": list,
        }
        self.size_properties = ("total_capacity", "used_capacity")

class ChapUserPropertiesExtractor(SDSBBasePropertiesExtractor):
    def __init__(self):
        self.common_properties = {
            "id": str,
            "targetChapUserName": str,
            "initiatorChapUserName": str,
        }
        self.size_properties = ("total_capacity", "used_capacity")

class VolumePropertiesExtractor(SDSBBasePropertiesExtractor):
    def __init__(self):
        self.common_properties = {
            "dataReductionEffects": dict,
            "id": str,
            "name": str,
            "nickname": str,
            "volumeNumber": int,
            "poolId": str,
            "poolName": str,
            "totalCapacity": int,
            "usedCapacity": int,
            "numberOfConnectingServers": int,
            "numberOfSnapshots": int,
            "protectionDomainId": str,
            "fullAllocated": bool,
            "volumeType": str,
            "statusSummary": str,
            "status": str,
            "storageControllerId": str,
            "snapshotAttribute": str,
            "snapshotStatus": str,
            "savingSetting": str,
            "savingMode": str,
            "dataReductionStatus": str,
            "dataReductionProgressRate": str,
            "vpsId": str,
            "vpsName": str,
            "naaId": str,
            "qosParam" : dict,
        }
        self.size_properties = ("total_capacity", "used_capacity")
