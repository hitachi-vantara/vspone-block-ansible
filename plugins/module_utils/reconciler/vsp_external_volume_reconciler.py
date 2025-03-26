try:
    from ..common.ansible_common import (
        log_entry_exit,
    )
    from ..provisioner.vsp_external_volume_provisioner import (
        VSPExternalVolumeProvisioner,
    )
    from ..model.vsp_external_volume_models import (
        ExternalVolumeSpec,
        ExternalVolumeFactSpec,
    )
    from ..common.hv_constants import StateValue

    from ..gateway.vsp_storage_system_gateway import VSPStorageSystemDirectGateway

except ImportError:
    from gateway.vsp_storage_system_gateway import VSPStorageSystemDirectGateway
    from common.ansible_common import (
        log_entry_exit,
    )
    from plugins.module_utils.provisioner.vsp_external_volume_provisioner import (
        VSPExternalVolumeProvisioner,
    )
    from model.vsp_external_volume_models import (
        ExternalVolumeSpec,
        ExternalVolumeFactSpec,
    )
    from common.hv_constants import StateValue


class VSPExternalVolumeReconciler:

    def __init__(self, connection_info, serial=None):
        self.connection_info = connection_info
        if serial is None:
            serial = self.get_storage_serial_number()
        self.provisioner = VSPExternalVolumeProvisioner(self.connection_info, serial)
        self.serial = self.provisioner.check_ucp_system(serial)

    def get_storage_serial_number(self):
        storage_gw = VSPStorageSystemDirectGateway(self.connection_info)
        storage_system = storage_gw.get_current_storage_system_info()
        return storage_system.serialNumber

    @log_entry_exit
    def external_volume_reconcile(self, state: str, spec: ExternalVolumeSpec):
        #  reconcile based on the desired state in the specification
        state = state.lower()

        if state == StateValue.PRESENT:
            return self.provisioner.create_external_volume_by_spec(spec)
        else:
            return self.provisioner.delete_external_volume_by_spec(spec)

    @log_entry_exit
    def external_volume_facts(self, spec: ExternalVolumeFactSpec):
        rsp = self.provisioner.external_volume_facts(spec)
        if rsp is None:
            rsp = []
        return rsp
