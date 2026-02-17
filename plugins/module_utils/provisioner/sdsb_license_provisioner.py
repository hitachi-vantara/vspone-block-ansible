try:
    from ..gateway.sdsb_license_gateway import SDSBLicenseGateway
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
except ImportError:
    from gateway.sdsb_license_gateway import SDSBLicenseGateway
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit

logger = Log()


class SDSBLicenseProvisioner:

    def __init__(self, connection_info):
        self.connection_info = connection_info
        self.gateway = SDSBLicenseGateway(self.connection_info)

    @log_entry_exit
    def get_license_setting(self):
        return self.gateway.get_license_setting()

    @log_entry_exit
    def modify_license_setting(self, warning_threshold_setting):
        return self.gateway.modify_license_setting(warning_threshold_setting)

    @log_entry_exit
    def get_licenses(self, spec=None):
        if spec and spec.id:
            try:
                return self.gateway.get_license_by_id(spec.id)
            except Exception as e:
                logger.writeException(e)
                return None
        response = self.gateway.get_licenses(spec)
        return response

    @log_entry_exit
    def get_license_by_id(self, license_id):
        return self.gateway.get_license_by_id(license_id)

    @log_entry_exit
    def delete_license(self, license_id):
        return self.gateway.delete_license(license_id)

    @log_entry_exit
    def create_license(self, key_code):
        return self.gateway.create_license(key_code)
