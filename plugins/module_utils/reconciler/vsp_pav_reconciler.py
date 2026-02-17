from ..provisioner.vsp_pav_provisioner import VSPPavProvisioner
from ..model.vsp_pav_models import VSPPavLdevRequestSpec, VSPPavLdevFactsSpec
from ..common.hv_constants import StateValue


class VspPavReconciler:

    def __init__(self, connection_info):
        self.provisioner = VSPPavProvisioner(connection_info)

    def reconcile_pav_ldevs(self, spec: VSPPavLdevRequestSpec, state):
        if state == StateValue.ABSENT:
            return self.provisioner.unassign_pav_ldev(spec)
        elif state == StateValue.PRESENT:
            return self.provisioner.assign_pav_ldev(spec)

    def vsp_pav_facts_reconciler(self, spec: VSPPavLdevFactsSpec):
        if spec.cu_number is not None:
            pav_ldev = self.provisioner.get_pav_ldev_by_cu(spec.cu_number)
            return pav_ldev.data_to_snake_case_list() if pav_ldev else None
        if spec.base_ldev_id is not None:
            alias_ldevs = self.provisioner.get_aliases_from_base_ldev(spec.base_ldev_id)
            return [ldev.camel_to_snake_dict() for ldev in alias_ldevs]
        if spec.alias_ldev_id is not None:
            pav_ldev = self.provisioner.get_pav_ldevs_by_ids(spec.alias_ldev_id)
            return [pav_ldev.camel_to_snake_dict()] if pav_ldev else None
        return self.provisioner.get_all_pav_ldevs().data_to_snake_case_list()
