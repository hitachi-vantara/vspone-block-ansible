from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
import threading

try:
    from ..provisioner.vsp_iscsi_target_provisioner import VSPIscsiTargetProvisioner
    from ..common.ansible_common import (
        camel_to_snake_case,
        camel_array_to_snake_case,
        camel_dict_to_snake_case,
        generate_random_name_prefix_string,
        log_entry_exit,
    )
    from ..common.hv_log import Log
    from ..model.vsp_iscsi_target_models import (
        IscsiTargetPayLoad,
        VSPIscsiTargetModificationInfo,
        IscsiTargetSpec,
    )
    from ..common.hv_constants import VSPIscsiTargetConstant, StateValue
    from ..common.vsp_errors import VspPortNotFoundError
    from ..gateway.vsp_storage_system_gateway import VSPStorageSystemDirectGateway
    from ..message.vsp_iscsi_target_msgs import VSPIscsiTargetMessage
except ImportError:
    from provisioner.vsp_iscsi_target_provisioner import VSPIscsiTargetProvisioner
    from common.ansible_common import (
        camel_to_snake_case,
        camel_array_to_snake_case,
        camel_dict_to_snake_case,
        generate_random_name_prefix_string,
        log_entry_exit,
    )
    from common.hv_log import Log
    from model.vsp_iscsi_target_models import (
        IscsiTargetPayLoad,
        VSPIscsiTargetModificationInfo,
        IscsiTargetSpec,
    )
    from common.hv_constants import VSPIscsiTargetConstant, StateValue
    from common.vsp_errors import VspPortNotFoundError
    from gateway.vsp_storage_system_gateway import VSPStorageSystemDirectGateway
    from message.vsp_iscsi_target_msgs import VSPIscsiTargetMessage

logger = Log()


class VSPIscsiTargetReconciler:

    def __init__(self, connection_info, serial):
        self.connection_info = connection_info
        self.serial = serial
        if self.serial is None:
            self.serial = self.get_storage_serial_number()
        self.provisioner = VSPIscsiTargetProvisioner(self.connection_info)

    @log_entry_exit
    def get_iscsi_targets(self, spec):
        return self.provisioner.get_iscsi_targets(spec, self.serial)

    @log_entry_exit
    def get_storage_serial_number(self):
        storage_gw = VSPStorageSystemDirectGateway(self.connection_info)
        storage_system = storage_gw.get_current_storage_system_info()
        return storage_system.serialNumber

    @log_entry_exit
    def pre_check_sub_state(self, spec):
        sub_state = spec.state
        if sub_state not in (
            StateValue.PRESENT,
            StateValue.ABSENT,
            VSPIscsiTargetConstant.STATE_ADD_INITIATOR,
            VSPIscsiTargetConstant.STATE_REMOVE_INITIATOR,
            VSPIscsiTargetConstant.STATE_ATTACH_LDEV,
            VSPIscsiTargetConstant.STATE_DETACH_LDEV,
            VSPIscsiTargetConstant.STATE_ADD_CHAP_USER,
            VSPIscsiTargetConstant.STATE_REMOVE_CHAP_USER,
        ):
            raise ValueError(
                VSPIscsiTargetMessage.SPEC_STATE_INVALID.value.format(sub_state)
            )

        if (
            sub_state == VSPIscsiTargetConstant.STATE_ATTACH_LDEV
            or sub_state == VSPIscsiTargetConstant.STATE_DETACH_LDEV
        ):
            spec.chap_users = None
            spec.iqn_initiators = None
        elif (
            sub_state == VSPIscsiTargetConstant.STATE_ADD_INITIATOR
            or sub_state == VSPIscsiTargetConstant.STATE_REMOVE_INITIATOR
        ):
            spec.chap_users = None
            spec.ldevs = None
        elif (
            sub_state == VSPIscsiTargetConstant.STATE_ADD_CHAP_USER
            or sub_state == VSPIscsiTargetConstant.STATE_REMOVE_CHAP_USER
        ):
            spec.ldevs = None
            spec.iqn_initiators = None

    @log_entry_exit
    def pre_check_port(self, port):
        logger.writeDebug("port = {}", port)
        if not port:
            raise VspPortNotFoundError(
                VSPIscsiTargetMessage.PORT_NOT_FOUND.value.format(port)
            )
        if port:
            # before the subobjState change
            # make sure all the ports are defined in the storage
            # so we can add comments properly
            sports = self.provisioner.get_ports(self.serial).data
            logger.writeDebug("sports = {}", sports)
            found = [x for x in sports if x.portId == port]
            logger.writeDebug("found={}", found)
            if found is None or len(found) == 0:
                raise VspPortNotFoundError(
                    VSPIscsiTargetMessage.PORT_NOT_FOUND.value.format(port)
                )

    @log_entry_exit
    def handle_create_iscsi_target(self, spec, result):
        if not spec.port:
            raise ValueError(VSPIscsiTargetMessage.PORTS_PARAMETER_INVALID.value)

        spec.name = generate_random_name_prefix_string() if not spec.name else spec.name
        logger.writeDebug("spec.port={0}".format(spec.port))
        try:
            self.provisioner.create_one_iscsi_target(
                IscsiTargetPayLoad(
                    name=spec.name,
                    port=spec.port,
                    host_mode=spec.host_mode,
                    host_mode_options=spec.host_mode_options,
                    luns=spec.ldevs,
                    iqn_initiators=spec.iqn_initiators,
                    chap_users=spec.chap_users,
                    iscsi_id=spec.iscsi_id,
                    lun_paths=spec.lun_paths,
                ),
                self.serial,
            )
        except Exception as e:
            if VSPIscsiTargetMessage.CATCH_MSG_ISCSI_TARGET.value in str(e):
                spec.name = generate_random_name_prefix_string()
                return self.handle_create_iscsi_target(spec, result)
            else:
                raise e
        one_iscsi_info = self.provisioner.get_one_iscsi_target(
            spec.port, spec.name, self.serial
        ).data
        logger.writeDebug("060525 one_iscsi_info={}", one_iscsi_info)
        result["iscsiTarget"] = one_iscsi_info
        result["changed"] = True
        result["comment"] = VSPIscsiTargetMessage.ISCSI_TARGET_CREATED.value.format(
            spec.name, spec.port
        )
        return one_iscsi_info

    def handle_update_iscsi_target(self, spec, iscsi_target, result):
        sub_state = spec.state
        logger.writeDebug("sub_state={}", sub_state)

        logger.writeDebug("update iscsi_target={}", iscsi_target)
        logger.writeDebug("update HgName={}", iscsi_target.iscsiName)
        logger.writeDebug("update Port={}", iscsi_target.portId)

        port = iscsi_target.portId
        logger.writeDebug("processing port={}", port)

        logger.writeDebug("check host_mode and host_optlist for update")
        if spec.host_mode is not None or spec.host_mode_options is not None:
            self.handle_update_host_mode(
                spec.state, spec.host_mode, spec.host_mode_options, iscsi_target, result
            )

        logger.writeDebug("check iqn_initiators for update")
        if spec.iqn_initiators:  # If iqn_initiators is present, update iqn_initiators
            self.handle_update_iqn_initiators(
                spec.state, spec.iqn_initiators, iscsi_target, result
            )

        logger.writeDebug("check luns for update")
        if spec.ldevs:  # If ldevs is present, present or overwrite ldevs
            self.handle_update_luns(spec.state, spec.ldevs, iscsi_target, result)
        elif spec.port_ids and spec.lun_paths:
            self.handle_update_lun_paths(
                spec.state, iscsi_target, spec.lun_paths, result
            )

        logger.writeDebug("check chap users for update")
        if spec.chap_users:  # If chap_users is present, update chap_users
            self.handle_update_chap_users(
                spec.state, spec.chap_users, iscsi_target, result
            )

    def luns_to_add(self, new_lun: list, hg_lun: set):
        luns_to_add = []
        for lun in new_lun:
            if lun not in hg_lun:
                luns_to_add.append(lun)
        return luns_to_add

    def luns_to_delete(self, new_lun: list, hg_lun: set):
        luns_to_delete = []
        for lun in new_lun:
            if lun in hg_lun:
                luns_to_delete.append(lun)
        return luns_to_delete

    @log_entry_exit
    def handle_update_lun_paths(self, subobjState, hg, lun_paths, result):
        logger = Log()
        logger.writeDebug(f"hgLun={0}", hg)
        hgLun = set(path.logicalUnitId for path in hg.logicalUnits or [])
        newLun = set(path.ldev for path in lun_paths or [])
        logger.writeDebug("newLun={0}", newLun)
        addLun = self.luns_to_add(newLun, hgLun)
        # delLun = list(set(hgLun) - set(newLun))
        delLun = self.luns_to_delete(newLun, hgLun)
        logger.writeDebug("hgLun={0}", hgLun)
        logger.writeDebug("541 addLun={0}", addLun)
        logger.writeDebug("542 delLun={0}", delLun)

        add_lun_path = [path for path in lun_paths if path.ldev in addLun]

        if subobjState == StateValue.PRESENT and add_lun_path:
            if len(add_lun_path) > 0:
                try:
                    ret_val = self.provisioner.add_lun_paths_to_iscsi_target(
                        hg, add_lun_path
                    )
                    if ret_val:
                        comment = (
                            VSPIscsiTargetMessage.ADD_LUN_PATH_SUCCESS.value.format(
                                add_lun_path
                            )
                        )
                        result["comment"] = comment
                        result["changed"] = True
                except Exception as e:
                    logger.writeError(
                        VSPIscsiTargetMessage.ADD_LUN_PATH_FAILED.value.format(
                            [path.ldev for path in add_lun_path],
                            [path.lun for path in add_lun_path],
                            str(e),
                        )
                    )
                    # result.errors.append(
                    #     VSPIscsiTargetMessage.ADD_LUN_PATH_FAILED.value.format(
                    #         [path.ldev for path in add_lun_path],
                    #         [path.lun for path in add_lun_path],
                    #         str(e),
                    #     )
                    # )
                    raise ValueError(self.errors)

        if subobjState == StateValue.ABSENT:
            if delLun:
                logger.writeDebug("delete_luns_from_host_group delLun={0}", delLun)
                if len(delLun) > 0:
                    self.provisioner.delete_luns_from_iscsi_target(hg, list(delLun))
                    result["changed"] = True
                    result["comment"] = (
                        VSPIscsiTargetMessage.DELETE_LUN_PATH_SUCCESS.value.format(
                            delLun
                        )
                    )
            else:
                result["comment"] = (
                    VSPIscsiTargetMessage.LUN_IS_NOT_IN_ISCSI_TARGET.value.format(
                        delLun
                    )
                )

    @log_entry_exit
    def handle_update_host_mode(
        self, state, host_mode, host_mode_options, iscsi_target, result
    ):
        if host_mode is None:
            host_mode = iscsi_target.hostMode.hostMode
        # for host_mode, you can only update, no delete
        logger.writeDebug("update host_mode={}", host_mode)
        logger.writeDebug(
            "iscsi_target.hostMode.hostMode={}", iscsi_target.hostMode.hostMode
        )

        iscsi_target_hmo = [
            opt.raidOptionNumber for opt in iscsi_target.hostMode.hostModeOptions or []
        ]
        logger.writeDebug("iscsi_target_hmo={}", iscsi_target_hmo)
        logger.writeDebug("host_mode_options={}", host_mode_options)
        if host_mode_options is not None:
            old_list = set(iscsi_target_hmo)
            new_list = set(host_mode_options)
            new_list - old_list

            # if state == VSPIscsiTargetConstant.STATE_ADD_HOST_MODE or state == StateValue.PRESENT:
            #     # # add = new - old
            #     host_opt = iscsi_target_hmo + list(add_list)
            # elif state == VSPIscsiTargetConstant.STATE_REMOVE_HOST_MODE or state == StateValue.ABSENT:
            #     # del = old & new
            #     host_opt = list(set(iscsi_target_hmo) - set(host_mode_options))
            # else:
            #     logger.writeInfo("No changed")
            #     return
            host_opt = host_mode_options
        else:
            host_opt = iscsi_target_hmo
        logger.writeDebug("update host_opt={}", host_opt)

        if host_mode != iscsi_target.hostMode.hostMode or set(host_opt) != set(
            iscsi_target_hmo
        ):
            logger.writeDebug("call set_host_mode()")
            self.provisioner.set_host_mode(
                iscsi_target, host_mode, list(host_opt), self.serial
            )
            result["comment"] = (
                VSPIscsiTargetMessage.ISCSI_HOST_MODE_UPDATED.value.format(
                    host_mode, host_opt
                )
            )
            result["changed"] = True

    def handle_update_iqn_initiators(
        self, state, iqn_initiators_new, iscsi_target, result
    ):
        logger.writeDebug("iqn_initiators_new={0}", iqn_initiators_new)
        iqn_initiators = set(iqn.iqn for iqn in iqn_initiators_new)
        iscsi_target_iqn_initiators = set(
            iqnInitiator.iqn for iqnInitiator in iscsi_target.iqnInitiators or []
        )
        logger.writeDebug("iqn_initiators={0}", iqn_initiators)
        add_iqn_initiators = iqn_initiators - iscsi_target_iqn_initiators
        del_iqn_initiators = iscsi_target_iqn_initiators.intersection(iqn_initiators)
        logger.writeDebug(
            "iscsi_target_iqn_initiators={0}", iscsi_target_iqn_initiators
        )
        logger.writeDebug("add_iqn_initiators={0}", add_iqn_initiators)
        logger.writeDebug("del_iqn_initiators={0}", del_iqn_initiators)
        add_iqns_with_nick_names = [
            iqn for iqn in iqn_initiators_new if iqn.iqn in add_iqn_initiators
        ]

        if (
            state == VSPIscsiTargetConstant.STATE_ADD_INITIATOR
            or state == StateValue.PRESENT
        ) and add_iqn_initiators:
            if len(add_iqn_initiators) > 0:
                self.provisioner.add_iqn_initiators_to_iscsi_target(
                    iscsi_target, add_iqns_with_nick_names, self.serial
                )
                result["changed"] = True
                result["comment"] = VSPIscsiTargetMessage.ADD_IQN_SUCCESS.value.format(
                    add_iqn_initiators
                )

        if (
            state == VSPIscsiTargetConstant.STATE_REMOVE_INITIATOR
            or state == StateValue.ABSENT
        ):
            if del_iqn_initiators:
                logger.writeDebug(
                    "delete_iqn_initiators_from_iscsi_target del_iqn_initiators={0}",
                    del_iqn_initiators,
                )
                if len(del_iqn_initiators) > 0:
                    self.provisioner.delete_iqn_initiators_from_iscsi_target(
                        iscsi_target, list(del_iqn_initiators), self.serial
                    )
                    result["changed"] = True
                    result["comment"] = (
                        VSPIscsiTargetMessage.DELETE_IQN_SUCCESS.value.format(
                            del_iqn_initiators
                        )
                    )
            else:
                result["comment"] = (
                    VSPIscsiTargetMessage.IQN_IS_NOT_IN_ISCSI_TARGET.value
                )

        for iqn_initiator in iqn_initiators_new:
            match_iqn = next(
                (
                    iqn
                    for iqn in iscsi_target.iqnInitiators
                    if iqn.iqn == iqn_initiator.iqn
                ),
                None,
            )
            if (
                match_iqn
                and iqn_initiator.nick_name is not None
                and match_iqn.nick_name != iqn_initiator.nick_name
            ):
                self.provisioner.update_iqn_nick_name(iscsi_target, iqn_initiator)
                result["changed"] = True

    @log_entry_exit
    def handle_update_luns(self, state, luns, iscsi_target, result):
        luns = set(luns)
        iscsi_target_luns = set(
            logicalUnit.logicalUnitId for logicalUnit in iscsi_target.logicalUnits or []
        )
        logger.writeDebug("newLun={0}", luns)
        add_luns = luns - iscsi_target_luns
        del_luns = iscsi_target_luns.intersection(luns)
        logger.writeDebug("iscsi_target_lun={0}", iscsi_target_luns)
        logger.writeDebug("add_luns={0}", add_luns)
        logger.writeDebug("del_luns={0}", del_luns)

        if (
            state == VSPIscsiTargetConstant.STATE_ATTACH_LDEV
            or state == StateValue.PRESENT
        ) and add_luns:
            if len(add_luns) > 0:
                self.provisioner.add_luns_to_iscsi_target(
                    iscsi_target, list(add_luns), self.serial
                )
                result["changed"] = True
                result["comment"] = VSPIscsiTargetMessage.ADD_LUN_SUCCESS.value.format(
                    add_luns
                )

        if (
            state == VSPIscsiTargetConstant.STATE_DETACH_LDEV
            or state == StateValue.ABSENT
        ):
            if del_luns:
                logger.writeDebug(
                    "delete_luns_from_iscsi_target del_luns={0}", del_luns
                )
                if len(del_luns) > 0:
                    self.provisioner.delete_luns_from_iscsi_target(
                        iscsi_target, list(del_luns), self.serial
                    )
                    result["changed"] = True
                    result["comment"] = (
                        VSPIscsiTargetMessage.DELETE_LUN_SUCCESS.value.format(del_luns)
                    )
            else:
                result["comment"] = (
                    VSPIscsiTargetMessage.LUN_IS_NOT_IN_ISCSI_TARGET.value
                )

    @log_entry_exit
    def handle_update_chap_users(self, state, chap_users, iscsi_target, result):

        chap_user_names = set(chap_user.chap_user_name for chap_user in chap_users)
        iscsi_target_chap_users = set(
            chapUser for chapUser in iscsi_target.chapUsers or []
        )
        logger.writeDebug("chap_user_names={0}", chap_user_names)
        add_chap_users = []
        for chap_user in chap_users:
            if chap_user.chap_secret is not None:
                add_chap_users.append(chap_user)
            else:
                if chap_user.chap_user_name not in iscsi_target_chap_users:
                    add_chap_users.append(chap_user)
        del_chap_users = iscsi_target_chap_users.intersection(chap_user_names)
        logger.writeDebug("iscsi_target_chap_users={0}", iscsi_target_chap_users)
        logger.writeDebug("add_chap_users={0}", add_chap_users)
        logger.writeDebug("del_chap_users={0}", del_chap_users)

        if (
            state == VSPIscsiTargetConstant.STATE_ADD_CHAP_USER
            or state == StateValue.PRESENT
        ) and add_chap_users:
            if len(add_chap_users) > 0:
                self.provisioner.add_chap_users_to_iscsi_target(
                    iscsi_target, list(add_chap_users), self.serial
                )
                result["changed"] = True
                result["comment"] = (
                    VSPIscsiTargetMessage.ADD_CHAP_USER_SUCCESS.value.format(
                        # [chap_user for chap_user in add_chap_users]
                        list(add_chap_users)
                    )
                )

        if (
            state == VSPIscsiTargetConstant.STATE_REMOVE_CHAP_USER
            or state == StateValue.ABSENT
        ):
            if del_chap_users:
                logger.writeDebug(
                    "delete_chap_users_from_iscsi_target del_chap_users={0}",
                    del_chap_users,
                )
                if len(del_chap_users) > 0:
                    self.provisioner.delete_chap_users_from_iscsi_target(
                        iscsi_target, list(del_chap_users), self.serial
                    )
                    result["changed"] = True
                    result["comment"] = (
                        VSPIscsiTargetMessage.DELETE_CHAP_USER_SUCCESS.value.format(
                            # [chap_user for chap_user in del_chap_users]
                            list(del_chap_users)
                        )
                    )
            else:
                result["comment"] = (
                    VSPIscsiTargetMessage.CHAP_USER_IS_NOT_IN_ISCSI_TARGET.value
                )

    @log_entry_exit
    def handle_delete_iscsi_target(self, spec, iscsi_target, result):
        try:
            self.provisioner.delete_iscsi_target(
                iscsi_target, spec.should_delete_all_ldevs, self.serial
            )
            result["changed"] = True
            result["iscsiTarget"] = None
            comment = VSPIscsiTargetMessage.ISCSI_DELETE_SUCCESSFUL.value.format(
                iscsi_target.iscsiName, iscsi_target.portId
            )
            result["comment"] = comment
        except Exception as e:
            logger.writeException(e)
            result["errors"].append(str(e))

    @log_entry_exit
    def handle_release_host_reservation_status(self, spec, iscsi_target, result):
        try:
            if spec.lun is not None:
                self.provisioner.release_host_reservation_status(
                    spec.port, iscsi_target.iscsiId, spec.lun
                )
                result["changed"] = True
                comment = (
                    VSPIscsiTargetMessage.RELEASE_HOST_RESERVE.value
                    if spec.lun is None
                    else VSPIscsiTargetMessage.RELEASE_HOST_RESERVE_LU.value.format(
                        spec.lun
                    )
                )
                result["comment"] = comment
            if spec.port_ids and spec.lun_paths:
                for port_id in spec.port_ids:
                    for lun_path in spec.lun_paths:
                        self.provisioner.release_host_reservation_status(
                            port_id, iscsi_target.iscsiId, lun_path.lun
                        )
                result["changed"] = True
                comment = (
                    VSPIscsiTargetMessage.RELEASE_HOST_RESERVE.value
                    if spec.lun_paths is None
                    else VSPIscsiTargetMessage.RELEASE_HOST_RESERVE_LU.value.format(
                        [lun_path.lun for lun_path in spec.lun_paths]
                    )
                )
                result["comment"] = comment
        except Exception as e:
            logger.writeException(e)
            result["errors"].append(str(e))

    @log_entry_exit
    def iscsi_target_reconciler(self, state, spec: IscsiTargetSpec):
        result = {"changed": False}
        self.pre_check_sub_state(spec)
        self.pre_check_port(spec.port)
        iscsi_target = None
        if spec.iscsi_id:
            iscsi_target = self.provisioner.get_one_iscsi_target_using_id(
                spec.port, spec.iscsi_id
            ).data
        elif spec.name and not iscsi_target:
            iscsi_target = self.provisioner.get_one_iscsi_target(
                spec.port, spec.name, self.serial
            ).data
        else:
            iscsi_target = None

        if state == StateValue.PRESENT:
            result["iscsiTarget"] = iscsi_target
            if iscsi_target is None:
                # Handle create iscsi target
                iscsi_target = self.handle_create_iscsi_target(spec, result)
            else:
                # Handle update iscsi target
                self.handle_update_iscsi_target(spec, iscsi_target, result)
            target_id = iscsi_target.iscsiId if iscsi_target else spec.iscsi_id
            logger.writeDebug(f"060525 target_id = {target_id}")

            if spec.should_release_host_reserve:
                # self.provisioner.release_host_reservation_status(
                #     spec.port, target_id, spec.lun
                # )
                # result["changed"] = True
                # result["comment"] = (
                #     VSPIscsiTargetMessage.RELEASE_HOST_RESERVE.value
                #     if spec.lun is None
                #     else VSPIscsiTargetMessage.RELEASE_HOST_RESERVE_LU.value.format(
                #         spec.lun
                #     )
                # )
                self.handle_release_host_reservation_status(spec, iscsi_target, result)
            if result["changed"]:
                result["iscsiTarget"] = self.provisioner.get_one_iscsi_target_using_id(
                    spec.port, target_id
                ).data

        elif state == StateValue.ABSENT:
            if iscsi_target is None:
                logger.writeInfo("No iscsi target found, state is absent, no change")
                result["comment"] = (
                    VSPIscsiTargetMessage.ISCSI_TARGET_HAS_BEEN_DELETED.value.format(
                        spec.name, spec.port
                    )
                )
            else:
                if (
                    len(iscsi_target.logicalUnits) > 0
                    and not spec.should_delete_all_ldevs
                ):
                    result["comment"] = (
                        VSPIscsiTargetMessage.LDEVS_PRESENT.value.format(
                            iscsi_target.iscsiName, iscsi_target.portId
                        )
                    )
                else:
                    # Handle delete iscsi target
                    self.handle_delete_iscsi_target(spec, iscsi_target, result)

        return VSPIscsiTargetModificationInfo(**result)

    @log_entry_exit
    def validate_specified_port_ids(self, port_ids):

        logger.writeDebug("port_ids = {}", port_ids)

        if not port_ids or len(port_ids) == 0:
            raise VspPortNotFoundError(
                VSPIscsiTargetMessage.PORT_NOT_FOUND.value.format(port_ids)
            )
        if port_ids:
            # make sure all the ports are defined in the storage
            # so we can add comments properly
            sports = self.provisioner.get_ports(self.serial).data
            logger.writeDebug("sports = {}", sports)
            found = [x for x in sports if x.portId in port_ids]
            logger.writeDebug("found={}", found)
            if found is None or len(found) == 0:
                raise VspPortNotFoundError(
                    VSPIscsiTargetMessage.PORT_NOT_FOUND.value.format(port_ids)
                )
            if found and len(found) != len(port_ids):
                found_port_ids = [x.portId for x in found]
                not_found_port_ids = set(port_ids) - set(found_port_ids)
                raise VspPortNotFoundError(
                    VSPIscsiTargetMessage.PORT_NOT_FOUND.value.format(
                        not_found_port_ids
                    )
                )

            iscsi_ports = [
                x for x in found if x.portType == VSPIscsiTargetConstant.PORT_TYPE_ISCSI
            ]

            logger.writeDebug("iscsi_ports={}", iscsi_ports)
            if iscsi_ports is None or len(iscsi_ports) == 0:
                raise VspPortNotFoundError(
                    VSPIscsiTargetMessage.PORT_NOT_FOUND.value.format(port_ids)
                )
            if iscsi_ports and len(iscsi_ports) != len(port_ids):
                found_port_ids = [x.portId for x in found]
                not_found_port_ids = set(port_ids) - set(found_port_ids)
                raise VspPortNotFoundError(
                    VSPIscsiTargetMessage.NOT_ISCSI_PORTS.value.format(
                        not_found_port_ids
                    )
                )

    @log_entry_exit
    def get_iscsi_targets_by_id(self, port_ids, iscsi_id):
        iscsi_targets = []
        for port_id in port_ids:
            one_target = self.provisioner.get_one_iscsi_target_using_id(
                port_id, iscsi_id
            ).data
            if one_target:
                iscsi_targets.extend(one_target)
            else:
                raise ValueError(
                    VSPIscsiTargetMessage.ISCSI_TARGET_NOT_FOUND.value.format(
                        iscsi_id, port_id
                    )
                )
        logger.writeDebug("iscsi_targets={}", iscsi_targets)
        return iscsi_targets

    @log_entry_exit
    def get_isscsi_targets_by_name(self, port_ids, name):
        iscsi_targets = []
        sports = self.provisioner.get_ports(self.serial).data
        found = []
        for port_id in port_ids:
            found = [
                x
                for x in sports
                if x.portId == port_id
                and x.portType == VSPIscsiTargetConstant.PORT_TYPE_ISCSI
            ]

        logger.writeDebug("found={}", found)
        if found is None or len(found) == 0:
            raise VspPortNotFoundError(
                VSPIscsiTargetMessage.PORT_NOT_FOUND.value.format(port_ids)
            )
        if found and len(found) != len(port_ids):
            found_port_ids = [x.portId for x in found]
            not_found_port_ids = set(port_ids) - set(found_port_ids)
            raise VspPortNotFoundError(
                VSPIscsiTargetMessage.NOT_ISCSI_PORTS.value.format(not_found_port_ids)
            )
        for port_id in port_ids:
            one_target = self.provisioner.get_one_iscsi_target(
                port_id, name, self.serial
            ).data
            if one_target:
                iscsi_targets.extend(one_target)
        logger.writeDebug("iscsi_targets={}", iscsi_targets)
        return iscsi_targets

    @log_entry_exit
    def reconcile_iscsi_target_bulk(self, state, spec: IscsiTargetSpec):

        ports = spec.port_ids
        name = spec.name
        id = spec.id
        results = {"changed": False, "iscsi_targets": [], "comments": [], "errors": []}
        results_lock = threading.Lock()
        max_workers = min(len(ports), 10)  # Limit concurrent threads

        try:
            self.validate_specified_port_ids(ports)
        except Exception as e:
            logger.writeException(e)
            results["errors"].append(str(e))
            results["failed"] = True
            return results

        if state == StateValue.PRESENT:
            logger.writeDebug("RC:reconcile_iscsi_target_bulk for PRESENT state")
            executor = ThreadPoolExecutor(
                max_workers=max_workers, thread_name_prefix="PresentWorker"
            )
            try:
                futures = [
                    executor.submit(
                        self._process_present_port,
                        port,
                        name,
                        id,
                        spec,
                        results_lock,
                        results,
                    )
                    for port in ports
                ]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.writeDebug("Error processing iscsi target: {}", str(e))
            except KeyboardInterrupt:
                executor.shutdown(wait=False, cancel_futures=True)
                raise
            finally:
                executor.shutdown(wait=True)

        elif state == StateValue.ABSENT:
            logger.writeDebug("RC:reconcile_iscsi_target_bulk for ABSENT state")
            executor = ThreadPoolExecutor(
                max_workers=max_workers, thread_name_prefix="AbsentWorker"
            )
            try:
                futures = [
                    executor.submit(
                        self._process_absent_port,
                        port,
                        name,
                        id,
                        spec,
                        results_lock,
                        results,
                    )
                    for port in ports
                ]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.writeDebug("Error processing iscsi target: {}", str(e))
            except KeyboardInterrupt:
                executor.shutdown(wait=False, cancel_futures=True)
                raise
            finally:
                executor.shutdown(wait=True)

        elif state in (StateValue.ADDED, StateValue.REMOVED, StateValue.UPDATED):
            effective_state = StateValue.PRESENT
            if state == StateValue.REMOVED:
                effective_state = StateValue.ABSENT
            logger.writeDebug("RC:reconcile_iscsi_target_bulk for OTHER state")
            executor = ThreadPoolExecutor(
                max_workers=max_workers, thread_name_prefix="OtherWorker"
            )
            try:
                futures = [
                    executor.submit(
                        self._process_update_port,
                        port,
                        name,
                        id,
                        spec,
                        effective_state,
                        results_lock,
                        results,
                    )
                    for port in ports
                ]
                for future in as_completed(futures):
                    try:
                        future.result()
                    except Exception as e:
                        logger.writeDebug("Error processing iscsi target: {}", str(e))
            except KeyboardInterrupt:
                executor.shutdown(wait=False, cancel_futures=True)
                raise
            finally:
                executor.shutdown(wait=True)

        if results.get("errors"):
            results["failed"] = True

        return results

    @log_entry_exit
    def _process_present_port(self, port, name, id, spec, results_lock, results):
        """Process a single port for PRESENT state in a thread."""
        # Use a copy of spec for each thread to avoid race conditions
        local_spec = copy.deepcopy(spec)
        local_spec.port = port
        local_spec.name = name
        local_spec.iscsi_id = id
        local_spec.state = StateValue.PRESENT
        logger.writeDebug("Processing port {} for PRESENT state".format(port))
        logger.writeDebug(f"RC:_process_present_port:spec = {local_spec}")
        result = {"changed": False, "comments": [], "errors": [], "iscsi_target": None}
        try:
            iscsi_target = self.iscsi_target_reconciler(StateValue.PRESENT, local_spec)
            result["changed"] = iscsi_target.changed
            result["iscsi_target"] = iscsi_target.iscsiTarget
            result["comments"] = [iscsi_target.comment] if iscsi_target.comment else []
            logger.writeDebug(f"RC:_process_present_port:result = {result}")
        except Exception as e:
            logger.writeException(e)
            result["errors"].append(str(e))

        with results_lock:
            if result["comments"]:
                results["comments"].extend(result["comments"])
            if result["changed"]:
                results["changed"] = True
            if result["errors"]:
                results["errors"].extend(result["errors"])
            if result["iscsi_target"]:
                results["iscsi_targets"].append(
                    result["iscsi_target"].camel_to_snake_dict()
                )
            logger.writeDebug(f"RC:_process_present_port:results = {results}")

    @log_entry_exit
    def _process_absent_port(self, port, name, id, spec, results_lock, results):
        """Process a single port for ABSENT state in a thread."""
        local_spec = copy.deepcopy(spec)
        local_spec.port = port
        local_spec.name = name
        local_spec.iscsi_id = id
        local_spec.state = StateValue.ABSENT
        logger.writeDebug("Processing port {} for ABSENT state".format(port))
        logger.writeDebug(f"RC:_process_absent_port:spec = {local_spec}")
        result = {"changed": False, "comments": [], "errors": []}

        try:
            rsp = self.iscsi_target_reconciler(StateValue.ABSENT, local_spec)
            # comment = VSPIscsiTargetMessage.ISCSI_OPERATION_SUCCESSFUL.value.format(name, port)
            result["comments"] = [rsp.comment] if rsp.comment else []
            result["changed"] = rsp.changed
            logger.writeDebug(f"RC:_process_absent_port:result = {result}")
        except Exception as e:
            logger.writeException(e)
            result["errors"].append(str(e))

        with results_lock:
            if result["comments"]:
                results["comments"].extend(result["comments"])
            if result["changed"]:
                results["changed"] = True
            if result["errors"]:
                results["errors"].extend(result["errors"])

    @log_entry_exit
    def _process_update_port(self, port, name, id, spec, state, results_lock, results):
        """Process a single port for ADDED/REMOVED/UPDATED state in a thread."""

        local_spec = copy.deepcopy(spec)
        local_spec.port = port
        local_spec.name = name
        local_spec.iscsi_id = id
        local_spec.state = state
        logger.writeDebug("Processing port {} for {} state".format(port, state))
        result = {"changed": False, "comments": [], "errors": [], "iscsi_target": None}

        try:
            iscsi_target = self.iscsi_target_reconciler(StateValue.PRESENT, local_spec)
            result["changed"] = iscsi_target.changed
            result["iscsi_target"] = iscsi_target.iscsiTarget
            result["comments"] = [iscsi_target.comment] if iscsi_target.comment else []
            logger.writeDebug(f"RC:_process_update_port:result = {result}")
        except Exception as e:
            logger.writeException(e)
            result["errors"].append(str(e))

        with results_lock:
            if result["comments"]:
                results["comments"].extend(result["comments"])
            if result["changed"]:
                results["changed"] = True
            if result["errors"]:
                results["errors"].extend(result["errors"])
            if result["iscsi_target"]:
                results["iscsi_targets"].append(
                    result["iscsi_target"].camel_to_snake_dict()
                )
            logger.writeDebug(f"RC:_process_present_port:results = {results}")


class VSPIscsiTargetCommonPropertiesExtractor:
    def __init__(self):
        self.common_properties = {
            "portId": str,
            "hostMode": dict,
            "resourceGroupId": int,
            "iqn": str,
            "iqnInitiators": list,
            "logicalUnits": list,
            "authParam": dict,
            "storageId": str,
            "chapUsers": list,
            "iscsiName": str,
            "iscsiId": int,
        }

        self.modification_properties = {
            "changed": bool,
            "comment": str,
            "comments": list,
            "iscsiTarget": dict,
        }

    def extract_iscsi_target(self, new_dict, response):
        for key, value_type in self.common_properties.items():
            # Get the corresponding key from the response or its mapped key
            response_key = None
            if key in response:
                response_key = response.get(key)
            # Assign the value based on the response key and its data type
            cased_key = camel_to_snake_case(key)
            if response_key is not None:
                new_dict[cased_key] = value_type(response_key)

    def extract(self, responses):
        new_items = []
        for response in responses:
            new_dict = {}
            self.extract_iscsi_target(new_dict, response)
            new_items.append(new_dict)
        new_items = camel_array_to_snake_case(new_items)
        return new_items

    def extract_dict(self, response):
        new_dict = {}
        for key, value_type in self.modification_properties.items():
            # Get the corresponding key from the response or its mapped key
            response_key = None
            if key in response:
                response_key = response.get(key)
            # Assign the value based on the response key and its data type
            cased_key = camel_to_snake_case(key)
            if response_key is not None:
                if key == "iscsiTarget":
                    new_dict[cased_key] = {}
                    self.extract_iscsi_target(new_dict[cased_key], response_key)
                else:
                    new_dict[cased_key] = value_type(response_key)
        new_dict = camel_dict_to_snake_case(new_dict)
        return new_dict
