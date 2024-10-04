try:
    from ..common.ansible_common import (
        log_entry_exit,

    )
    from ..common.hv_log import Log
    from ..common.hv_constants import *
    from ..provisioner.vsp_gad_pair_provisioner import GADPairProvisioner
    from ..model.vsp_gad_pairs_models import VspGadPairSpec
    from ..common.hv_constants import StateValue, ConnectionTypes

except ImportError:
    from common.ansible_common import (
        log_entry_exit,
    )
    from common.hv_log import Log
    from common.hv_constants import *
    from provisioner.vsp_gad_pair_provisioner import GADPairProvisioner
    from model.vsp_gad_pairs_models import VspGadPairSpec
    from common.hv_constants import StateValue, ConnectionTypes


class VSPGadPairReconciler:

    def __init__(self, connection_info, serial=None):
        self.connection_info = connection_info
        self.provisioner = GADPairProvisioner(self.connection_info)
        self.serial = self.provisioner.check_ucp_system(serial)

    @log_entry_exit
    def gad_pair_reconcile(self, state: str, spec: VspGadPairSpec):
        ## reconcile the storage pool based on the desired state in the specification
        pair = self.provisioner.get_gad_pair_by_pvol_id(spec.primary_volume_id)
        rec_methods = {
            StateValue.ABSENT: self.delete_gad_pair,
            StateValue.SPLIT: self.split_gad_pair,
            StateValue.RE_SYNC: self.resync_gad_pair,
        }
        if pair and rec_methods.get(state):
            response = rec_methods.get(state)(pair)
            return response.to_dict() if not isinstance(response, str) else response
        elif not pair and rec_methods.get(state):
            return "Gad pair not present"
        else:
            pair =  self.create_update_gad_pair(spec , pair)
            return pair.to_dict() if pair else None
   

    @log_entry_exit
    def create_update_gad_pair(self, spec, pair):
        if pair:return pair
        return self.provisioner.create_gad_pair(spec)

    @log_entry_exit
    def delete_gad_pair(self, pair):

        return self.provisioner.delete_gad_pair(pair)

    @log_entry_exit
    def split_gad_pair(self, pair):

        return self.provisioner.split_gad_pair(pair)

    @log_entry_exit
    def resync_gad_pair(self, pair):

        return self.provisioner.resync_gad_pair(pair)
    
    @log_entry_exit
    def gad_pair_facts(self, gad_pair_facts_spec):

        gad_pairs = self.provisioner.gad_pair_facts(gad_pair_facts_spec)
        return None if not gad_pairs else gad_pairs.to_dict()
