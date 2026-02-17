from ..gateway.vsp_pav_gateway import VSPPavLdevGateway
from ..model.vsp_pav_models import VSPPavLdevRequestSpec
from ..common.ansible_common import log_entry_exit


class VSPPavProvisioner:

    def __init__(self, connection_info):
        self.gateway = VSPPavLdevGateway(connection_info)
        self.connect_info = connection_info

    @log_entry_exit
    def get_all_pav_ldevs(self):
        return self.gateway.get_all_pav_ldevs()

    @log_entry_exit
    def get_pav_ldev_by_cu(self, cu_number: int):
        return self.gateway.get_pav_ldev_by_cu(cu_number)

    def get_aliases_from_base_ldev(self, base_ldev_id: int):
        pav_ldevs = self.get_all_pav_ldevs()
        alias_ldevs = []
        for ldev in pav_ldevs.data:
            if ldev.cBaseVolumeId == base_ldev_id:
                alias_ldevs.append(ldev)
        return alias_ldevs

    def get_pav_ldevs_by_ids(self, ldev_id: int):
        pav_ldevs = self.get_all_pav_ldevs()
        for ldev in pav_ldevs.data:
            if ldev.ldevId == ldev_id:
                return ldev
        return None

    @log_entry_exit
    def unassign_pav_ldev(self, spec: VSPPavLdevRequestSpec):
        if spec.alias_ldev_ids is None or len(spec.alias_ldev_ids) == 0:
            raise ValueError("alias_ldev_ids must be provided for unassignment.")
        try:
            unsued = self.gateway.unassign_pav_ldev(spec.alias_ldev_ids)
            self.connect_info.changed = True
            spec.comment = "PAV LDEVs unassigned successfully."
        except Exception as e:
            if "The specified LDEV is not an alias volume." in str(e):
                # Ignore the error if the LDEV is already unassigned
                spec.comment = str(e)
            else:
                raise e
        return None

    @log_entry_exit
    def assign_pav_ldev(self, spec: VSPPavLdevRequestSpec):
        if spec.base_ldev_id is None:
            raise ValueError("base_ldev_id must be provided for assignment.")
        if spec.alias_ldev_ids is None or len(spec.alias_ldev_ids) == 0:
            raise ValueError("alias_ldev_ids must be provided for assignment.")
        try:
            unused = self.gateway.assign_pav_ldev(
                spec.alias_ldev_ids, spec.base_ldev_id
            )
            self.connect_info.changed = True
            spec.comment = "PAV LDEVs assigned successfully."

        except Exception as e:
            if "The specified LDEV is already in use as an alias volume." in str(e):
                # Ignore the error if the LDEV is already assigned
                spec.comment = str(e)
            else:
                raise e
        base_ldevs = self.get_aliases_from_base_ldev(spec.base_ldev_id)
        return (
            [ldevs.camel_to_snake_dict() for ldevs in base_ldevs]
            if base_ldevs
            else None
        )
