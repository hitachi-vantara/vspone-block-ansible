try:
    from ..provisioner.sdsb_license_provisioner import SDSBLicenseProvisioner
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
except ImportError:
    from provisioner.sdsb_license_provisioner import SDSBLicenseProvisioner
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit

logger = Log()


class SDSBLicenseReconciler:

    def __init__(self, connection_info):
        self.connection_info = connection_info
        self.provisioner = SDSBLicenseProvisioner(self.connection_info)

    @log_entry_exit
    def get_license_setting(self):
        return self.provisioner.get_license_setting()

    @log_entry_exit
    def get_license(self, license_id):
        return self.provisioner.get_license_by_id(license_id)

    @log_entry_exit
    def modify_license_setting(self, warning_threshold_setting):
        return self.provisioner.modify_license_setting(warning_threshold_setting)

    @log_entry_exit
    def get_license_facts(self, spec=None):
        if spec:
            self.validate_license_facts_spec(spec)
        return self.provisioner.get_licenses(spec)

    def validate_license_facts_spec(self, spec):
        valid_status_map = {
            "active": "Active",
            "warning": "Warning",
            "graceperiod": "GracePeriod",
            "invalid": "Invalid",
        }
        if spec.status:
            status_lower = spec.status.lower()
            if status_lower not in valid_status_map:
                raise ValueError(
                    f"Invalid status value: {spec.status}. Valid values are: {list(valid_status_map.values())}"
                )
            spec.status = valid_status_map[status_lower]

    # @log_entry_exit
    # def get_licenses(self, spec=None):
    #     return self.provisioner.get_licenses(spec)

    # @log_entry_exit
    # def get_license(self, license_id):
    #     return self.provisioner.get_license(license_id)

    @log_entry_exit
    def delete_license(self, license_id):
        return self.provisioner.delete_license(license_id)

    @log_entry_exit
    def create_license(self, key_code):
        return self.provisioner.create_license(key_code)
