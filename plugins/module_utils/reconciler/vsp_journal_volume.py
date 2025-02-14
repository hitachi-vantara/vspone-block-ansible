try:
    from ..common.ansible_common import (
        log_entry_exit,
    )
    from ..provisioner.vsp_journal_volume_provisioner import VSPJournalVolumeProvisioner
    from ..model.vsp_storage_pool_models import JournalVolumeSpec
    from ..common.hv_constants import StateValue
    from ..message.vsp_journal_volume_msgs import VSPSJournalVolumeValidateMsg

except ImportError:
    from common.ansible_common import (
        log_entry_exit,
    )
    from plugins.module_utils.provisioner.vsp_journal_volume_provisioner import (
        VSPJournalVolumeProvisioner,
    )
    from model.vsp_storage_pool_models import JournalVolumeSpec
    from common.hv_constants import StateValue


class VSPJournalVolumeReconciler:

    def __init__(self, connection_info, serial=None):
        self.connection_info = connection_info
        self.provisioner = VSPJournalVolumeProvisioner(self.connection_info)
        self.serial = self.provisioner.check_ucp_system(serial)

    @log_entry_exit
    def journal_volume_reconcile(self, state: str, spec: JournalVolumeSpec):
        #  reconcile the journal pool based on the desired state in the specification
        state = state.lower()

        if state == StateValue.PRESENT:
            return self.provisioner.create_journal_pool(spec)
        else:
            if spec.journal_id is None:
                raise ValueError(VSPSJournalVolumeValidateMsg.JP_ID.value)
            if state == StateValue.EXPAND_JOURNAL_VOLUME:
                return self.provisioner.expand_journal_pool(spec, spec.journal_id)
            elif state == StateValue.SHRINK_JOURNAL_VOLUME:
                return self.provisioner.shrink_journal_pool(spec, spec.journal_id)
            elif state == StateValue.UPDATE:
                return self.provisioner.update_journal_pool(spec, spec.journal_id)
            elif state == StateValue.ABSENT:
                return self.provisioner.delete_journal_pool(spec.journal_id)

    @log_entry_exit
    def journal_volume_facts(self, spec=None):
        return self.provisioner.journal_pool_facts(spec)
