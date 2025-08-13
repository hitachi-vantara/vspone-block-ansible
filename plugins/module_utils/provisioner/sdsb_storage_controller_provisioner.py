try:
    from ..gateway.gateway_factory import GatewayFactory
    from ..common.hv_constants import GatewayClassTypes
    from ..common.ansible_common import log_entry_exit

except ImportError:
    from gateway.gateway_factory import GatewayFactory
    from common.hv_constants import GatewayClassTypes
    from common.ansible_common import log_entry_exit


class SDSBStorageControllerProvisioner:

    def __init__(self, connection_info):

        self.gateway = GatewayFactory.get_gateway(
            connection_info, GatewayClassTypes.SDSB_STORAGE_CONTROLLER
        )

    @log_entry_exit
    def get_storage_controllers(self, spec=None):
        storage_controllers = self.gateway.get_storage_controllers(spec)
        controllers = None
        controllers = storage_controllers.get("data", [])
        if spec is not None and spec.primary_fault_domain_name:
            storage_controllers = [
                fd
                for fd in controllers
                if fd.get("primary_fault_domain_name") == spec.primary_fault_domain_name
            ]
        if spec is not None and spec.primary_fault_domain_id:
            storage_controllers = [
                fd
                for fd in controllers
                if fd.get("primary_fault_domain_id") == spec.primary_fault_domain_id
            ]
        return storage_controllers
