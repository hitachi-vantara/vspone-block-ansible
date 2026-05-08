from typing import Any

from ..common.ansible_common import (
    log_entry_exit,
)
from ..common.hv_log import Log
from ..provisioner.vsp_one_gad_ctg_provisioner import VspOneGadCtgProvisioner
from ..model.vsp_gad_pairs_models import VspGadCtgCreateSpec
from ..common.hv_constants import StateValue


logger = Log()


class VSPOneGadCtgReconciler:

    def __init__(self, connection_info, secondary_connection_info):

        self.logger = Log()
        self.connection_info = connection_info
        self.secondary_connection_info = secondary_connection_info
        self.provisioner = VspOneGadCtgProvisioner(
            connection_info, secondary_connection_info
        )

    @log_entry_exit
    def gad_ctg_facts(self, spec=None) -> Any:
        """
        Retrieve GAD consistency group facts for a given GAD consistency group ID.
        """
        response = self.provisioner.get_gad_ctgs(spec)
        if response is None:
            return []
        return response.camel_to_snake_dict()

    @log_entry_exit
    def reconcile(self, state, spec) -> Any:
        """
        Reconcile GAD pair state based on the desired state and specification.
        """
        if state == "suspended":
            return self.suspend_gad_pairs(spec)
        elif state == "resynced" or state == "swap_resynced":
            return self.resync_gad_pairs(spec, state)
        else:
            raise ValueError(f"Unsupported state: {state}")

    @log_entry_exit
    def suspend_gad_pairs(self, spec):
        """
        Suspend GAD pairs based on the specification.
        """
        if spec.consistency_group_ids is None or len(spec.consistency_group_ids) == 0:
            raise ValueError("Consistency group IDs must be provided for suspend operation.")
        if spec.continue_io_volume is None:
            spec.continue_io_volume = "SECONDARY"
        try:
            ids = self.provisioner.suspend_gad_pairs(spec)
            self.connection_info.changed = True
            response = self.provisioner.get_gad_pairs_by_ctg_id(ids)
            if response is None:
                return []
            return response.camel_to_snake_dict()
        except Exception as e:
            self.logger.writeException(e)
            spec.comments = str(e)
            return None

    @log_entry_exit
    def resync_gad_pairs(self, spec, state):
        """
        Resync GAD pair based on the specification and desired state.
        """
        if spec.consistency_group_ids is None or len(spec.consistency_group_ids) == 0:
            raise ValueError("Consistency group IDs must be provided for resync operation.")
        if spec.is_swap_resynced is None:
            spec.is_swap_resynced = state == "swap_resynced"
        if spec.io_preference_mode is None:
            spec.io_preference_mode = "KEEP_CURRENT_SETTING"
        if spec.copy_pace is None:
            spec.copy_pace = 3

        try:
            ids = self.provisioner.resync_gad_pairs(spec)
            self.connection_info.changed = True
            response = self.provisioner.get_gad_pairs_by_ctg_id(ids)
            if response is None:
                return []
            return response.camel_to_snake_dict()
        except Exception as e:
            self.logger.writeException(e)
            spec.comments = str(e)
            return None

    @log_entry_exit
    def vsp_one_gad_pair_reconcile(self, spec: VspGadCtgCreateSpec, state) -> Any:
        """
        Reconcile GAD pairs for a given GAD consistency group ID based on the provided specification.
        """
        if state.lower() == StateValue.PRESENT:
            self.provisioner.create_gad_using_ctg(spec)

        priamry_volumes = [gad_pair.primary_volume_id for gad_pair in spec.gad_pairs]
        gad_pairs_by_ctg = self.provisioner.filter_gad_pairs_by_primary_volume_ids(
            spec.consistency_group_id, priamry_volumes
        )
        return [gad_pair.camel_to_snake_dict() for gad_pair in gad_pairs_by_ctg]
