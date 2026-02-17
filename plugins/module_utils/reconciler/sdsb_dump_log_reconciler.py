from ..provisioner.sdsb_dump_log_provisioner import SDSBDumpLogProvisioner
from ..common.ansible_common import log_entry_exit
from ..model.sdsb_dump_log_models import CreateDumpFileSpec, DumpLogStatusSpec
from ..common.hv_constants import StateValue


class SDSBDumpLogReconciler:

    def __init__(self, connection_info):
        self.provisioner = SDSBDumpLogProvisioner(connection_info)

    @log_entry_exit
    def dump_log_reconcile(self, spec: CreateDumpFileSpec, state: StateValue):
        if state == StateValue.PRESENT:
            return self.provisioner.create_dump_file(spec)
        elif state == StateValue.ABSENT:
            return self.provisioner.delete_dump_file(spec)
        else:
            return self.provisioner.download_dump_file(spec)

    @log_entry_exit
    def dump_log_status_facts_reconcile(self, spec: DumpLogStatusSpec):
        if spec.include_all_status:
            return self.provisioner.get_all_dump_log_status().data_to_snake_case_list()
        else:
            return self.provisioner.get_dump_log_status().camel_to_snake_dict()
