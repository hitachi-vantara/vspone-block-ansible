try:
    from ..provisioner.sdsb_capacity_mgmt_settings_provisioner import (
        SDSBCapacityManagementSettingsProvisioner,
    )
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
except ImportError:
    from provisioner.sdsb_capacity_mgmt_settings_provisioner import (
        SDSBCapacityManagementSettingsProvisioner,
    )
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit

logger = Log()


class SDSBCapacityManagementSettingsReconciler:

    def __init__(self, connection_info):
        self.connection_info = connection_info
        self.provisioner = SDSBCapacityManagementSettingsProvisioner(
            self.connection_info
        )

    @log_entry_exit
    def get_capacity_management_settings(self, spec=None):
        response = self.provisioner.get_capacity_management_settings(spec)
        return self.display_response(response)

    @log_entry_exit
    def display_response(self, response):
        return {
            "is_storage_cluster_capacity_balancing_enabled": response[
                "storage_cluster"
            ]["is_enabled"],
            "storage_controllers_capacity_balancing_settings": response[
                "storage_controllers"
            ],
        }
