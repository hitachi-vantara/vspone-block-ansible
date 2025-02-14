try:
    from ..common.ansible_common import (
        log_entry_exit,
        camel_to_snake_case,
        get_default_value,
    )
    from ..common.hv_log import Log
    from ..provisioner.vsp_storage_port_provisioner import VSPStoragePortProvisioner


except ImportError:
    from common.ansible_common import (
        log_entry_exit,
        camel_to_snake_case,
        get_default_value,
    )
    from common.hv_log import Log
    from provisioner.vsp_storage_port_provisioner import VSPStoragePortProvisioner


class VSPStoragePortReconciler:
    def __init__(self, connection_info, serial):

        self.logger = Log()
        self.connectionInfo = connection_info
        self.storage_serial_number = serial
        self.provisioner = VSPStoragePortProvisioner(connection_info)

    @log_entry_exit
    def vsp_storage_port_facts(self, spec) -> dict:
        if spec.ports is not None:
            port_info = self.provisioner.filter_port_using_port_ids(
                spec.ports
            ).data_to_list()
            return StoragePortInfoExtractor(self.storage_serial_number).extract(
                port_info
            )
        else:
            port_info = self.provisioner.get_all_storage_ports().data_to_list()
            return ShortStoragePortInfoExtractor(self.storage_serial_number).extract(
                port_info
            )

    @log_entry_exit
    def vsp_storage_port_reconcile(self, spec) -> dict:

        portInfo = self.provisioner.change_port_settings(
            spec.port, spec.port_mode, spec.enable_port_security
        )

        return StoragePortInfoExtractor(self.storage_serial_number).extract(
            [portInfo.to_dict()]
        )

    @log_entry_exit
    def is_out_of_band(self):
        return self.provisioner.is_out_of_band()


class StoragePortInfoExtractor:
    def __init__(self, serial):
        self.storage_serial_number = serial
        self.common_properties = {
            "portId": str,
            "portMode": str,
            "portType": str,
            "portSecuritySetting": bool,
            "portAttributes": list,
            "portSpeed": str,
            "loopId": str,
            "fabricMode": bool,
            "portConnection": str,
            "wwn": str,
            "iscsiWindowSize": str,
            "keepAliveTimer": int,
            "tcpPort": str,
            "macAddress": str,
            "ipv4Address": str,
            "ipv4Subnetmask": str,
            "ipv4GatewayAddress": str,
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
                    default_value = get_default_value(value_type)
                    new_dict[cased_key] = default_value
            new_items.append(new_dict)
        return new_items


class ShortStoragePortInfoExtractor:
    def __init__(self, serial):
        self.storage_serial_number = serial
        self.common_properties = {
            "portId": str,
            "portType": str,
            "portAttributes": list,
            "portSpeed": str,
            "loopId": str,
            "fabricMode": bool,
            "portConnection": str,
            "portSecuritySetting": bool,
            "wwn": str,
            "portMode": str,
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
                    default_value = get_default_value(value_type)
                    new_dict[cased_key] = default_value
            new_items.append(new_dict)
        return new_items
