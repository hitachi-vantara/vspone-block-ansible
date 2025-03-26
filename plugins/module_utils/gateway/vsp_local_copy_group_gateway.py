try:
    from .gateway_manager import VSPConnectionManager
    from ..model.vsp_local_copy_group_models import (
        LocalCopyGroupInfo,
        LocalCopyGroupInfoList,
        LocalSpecificCopyGroupInfo,
    )
    from ..common.ansible_common import dicts_to_dataclass_list
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
except ImportError:
    from .gateway_manager import VSPConnectionManager
    from model.vsp_local_copy_group_models import (
        LocalCopyGroupInfo,
        LocalCopyGroupInfoList,
        LocalSpecificCopyGroupInfo,
    )
    from common.ansible_common import dicts_to_dataclass_list
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit

GET_LOCAL_COPY_GROUPS = "v1/objects/local-clone-copygroups"
GET_ONE_COPY_GROUP = "v1/objects/local-clone-copygroups/{}"
GET_STORAGES_DIRECT = "v1/objects/storages"


logger = Log()


class VSPLocalCopyGroupDirectGateway:

    def __init__(self, connection_info):
        self.connection_manager = VSPConnectionManager(
            connection_info.address,
            connection_info.username,
            connection_info.password,
            connection_info.api_token,
        )
        self.connection_info = connection_info
        self.serial = None

    @log_entry_exit
    def set_storage_serial_number(self, serial: str):
        self.storage_serial_number = serial
        if self.storage_serial_number is None:
            self.storage_serial_number = self.get_storage_serial()

    @log_entry_exit
    def get_storage_serial(self):
        storage = self.connection_manager.get(GET_STORAGES_DIRECT)
        storage_info = storage["data"][0]
        storage_serial = storage_info.get("serialNumber")
        return storage_serial

    @log_entry_exit
    def get_local_copy_groups(self, spec):
        response = self.connection_manager.get(GET_LOCAL_COPY_GROUPS)
        logger.writeDebug(f"GW:get_local_copy_groups:response={response}")
        copy_gr_list = LocalCopyGroupInfoList(
            dicts_to_dataclass_list(response["data"], LocalCopyGroupInfo)
        )
        return copy_gr_list

    @log_entry_exit
    def get_copy_group_by_name(self, spec):
        response = self.get_local_copy_groups(spec)
        for x in response.data:
            if x.copyGroupName == spec.name:
                return x
        return None

    @log_entry_exit
    def get_one_copygroup_info_by_name(self, spec, fact_spec=False):
        response = self.get_local_copy_groups(spec)
        for x in response.data:
            if x.copyGroupName == spec.name:
                one_specific_copy_gr = self.get_one_copygroup_with_copy_pairs_by_id(
                    x.localCloneCopygroupId
                )
                logger.writeDebug(
                    f"GW:get_one_copygroup_info_by_name:one_specific_copy_gr={one_specific_copy_gr}"
                )

                return one_specific_copy_gr

        return None

    @log_entry_exit
    def get_one_copygroup_with_copy_pairs_by_id(self, local_copygroup_id: str):
        end_point = GET_ONE_COPY_GROUP.format(local_copygroup_id)
        logger.writeDebug(
            f"GW:get_one_copygroup_with_copy_pairs_by_id:end_point={end_point}"
        )
        if local_copygroup_id is None:
            return None
        response = self.connection_manager.get(end_point)
        logger.writeDebug(f"GW:get_local_copy_groups:response={response}")

        return LocalSpecificCopyGroupInfo(**response)
