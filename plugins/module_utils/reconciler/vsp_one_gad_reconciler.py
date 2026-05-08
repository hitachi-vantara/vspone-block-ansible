import time

from typing import Any

try:
    from ..common.ansible_common import log_entry_exit
    from ..common.hv_log import Log
    from ..provisioner.vsp_one_gad_provisioner import VspOneGadProvisioner
    from ..common.hv_constants import StateValue
except (ImportError, ValueError):
    from common.ansible_common import log_entry_exit
    from common.hv_log import Log
    from provisioner.vsp_one_gad_provisioner import VspOneGadProvisioner
    from common.hv_constants import StateValue

logger = Log()


class VspOneGadReconciler:
    def __init__(self, connection_info, secondary_connection_info=None):
        self.connectionInfo = connection_info
        # Store secondary connection for CTG operations
        self.secondaryConnectionInfo = secondary_connection_info
        self.provisioner = VspOneGadProvisioner(connection_info)

    @log_entry_exit
    def get_gad_pairs_facts(self, spec=None) -> Any:
        return self.provisioner.get_gad_pairs_facts(spec)

    @log_entry_exit
    def gad_pair_reconcile(self, state: str, spec: Any) -> Any:
        """
        Orchestrates GAD pair operations.
        Always uses the CTG Reconciler for creation.
        """
        state = state.lower()
        success = False

        if state == StateValue.ABSENT:
            success = self.provisioner.delete_gad_pairs(spec)
            if success:
                return f"GAD pairs {spec.ids} deleted successfully."

        elif state in [StateValue.SPLITTED]:
            success = self.provisioner.suspend_gad_pairs(spec)

        elif state in [StateValue.RE_SYNCED]:
            success = self.provisioner.resync_gad_pairs(spec)
        else:
            error_msg = f"Unsupported state: {state}."
            if hasattr(spec, "errors"):
                spec.errors.append(error_msg)
            return False

        # 2. Post-action stabilization (For Split/Sync)
        if success:
            sleep_time = 5
            logger.writeInfo(
                f"Action {state} successful. Waiting {sleep_time}s for stabilization..."
            )
            time.sleep(sleep_time)

            logger.writeInfo(f"Fetching updated facts for {spec.ids}")
            return self.provisioner.filter_gad_pairs_by_ids(spec.ids)

        return False
