try:
    from ..common.ansible_common import (
        log_entry_exit,
        snake_to_camel_case,
        get_response_key,
    )
    from ..common.hv_log import Log
    from ..common.hv_constants import *
    from ..provisioner.vsp_storage_pool_provisioner import VSPStoragePoolProvisioner
    from ..model.vsp_storage_pool_models import StoragePoolSpec, PoolFactSpec
    from ..common.hv_constants import StateValue, ConnectionTypes

except ImportError:
    from common.ansible_common import (
        log_entry_exit,
        snake_to_camel_case,
        get_response_key,
    )
    from common.hv_log import Log
    from common.hv_constants import *
    from provisioner.vsp_storage_pool_provisioner import VSPStoragePoolProvisioner
    from model.vsp_storage_pool_models import StoragePoolSpec, PoolFactSpec
    from common.hv_constants import StateValue, ConnectionTypes


class VSPStoragePoolReconciler:

    def __init__(self, connection_info, serial=None):
        self.connection_info = connection_info
        self.provisioner = VSPStoragePoolProvisioner(self.connection_info)
        self.serial = self.provisioner.check_ucp_system(serial)


    @log_entry_exit
    def storage_pool_reconcile(self, state: str, spec: StoragePoolSpec):
        ## reconcile the storage pool based on the desired state in the specification
        state = state.lower()
        if state == StateValue.ABSENT:
            return self.delete_storage_pool(spec)
        elif state == StateValue.PRESENT:
            return self.create_update_storage_pool(spec).to_dict()

    @log_entry_exit
    def create_update_storage_pool(self, spec):
        pool = self.provisioner.get_storage_pool_by_name_or_id(spec.name, spec.id)
        if pool is None:
            return self.provisioner.create_storage_pool(spec)
        else:
            return self.provisioner.update_storage_pool(spec, pool)
    @log_entry_exit
    def delete_storage_pool(self, spec):

        return self.provisioner.delete_storage_pool(spec)
    @log_entry_exit
    def storage_pool_facts(self, pool_fact_spec):

        pools = self.provisioner.get_storage_pool(pool_fact_spec)
        return None if not pools else pools.to_dict()
