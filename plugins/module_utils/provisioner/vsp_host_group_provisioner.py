from concurrent.futures import ThreadPoolExecutor, as_completed

try:

    from ..common.hv_log import Log
    from ..common.ansible_common import convert_hex_to_dec
    from ..common.ansible_common import log_entry_exit
    from ..message.vsp_host_group_msgs import VSPHostGroupMessage
    from ..gateway.vsp_host_group_gateway import VSPHostGroupDirectGateway
    from ..common.hv_constants import VSPHostGroupConstant
    from ..common.ansible_common_constants import MAX_WORKER_THREADS

except ImportError:
    from common.hv_log import Log
    from common.ansible_common import convert_hex_to_dec
    from common.ansible_common import log_entry_exit
    from message.vsp_host_group_msgs import VSPHostGroupMessage
    from gateway.vsp_host_group_gateway import VSPHostGroupDirectGateway


class VSPHostGroupProvisioner:

    def __init__(self, connection_info):
        self.gateway = VSPHostGroupDirectGateway(connection_info)
        self.connection_info = connection_info
        self.serial = None
        self.all_hgs = None

    @log_entry_exit
    def get_host_groups(
        self,
        ports_input=None,
        name_input=None,
        lun_input=None,
        query=None,
        hg_number=None,
    ):
        if name_input is not None and hg_number is not None:
            raise Exception(
                "Both name and hg_number cannot be provided at the same time."
            )
        logger = Log()
        logger.writeDebug("PROV:get_host_groups:serial = {}", self.serial)
        if name_input == "":
            name_input = None

        if lun_input is not None and ":" in str(lun_input):
            lun_input = convert_hex_to_dec(lun_input)
            logger.writeDebug("Hex converted lun={0}".format(lun_input))
        if lun_input == "":
            lun_input = None

        port_set = None
        if ports_input:
            port_set = set(ports_input)
        logger.writeInfo("port_set={0}".format(port_set))
        is_get_wwns = False
        if query and "wwns" in query:
            is_get_wwns = True

        is_get_luns = False
        is_ldev_detail = False
        if query and "ldevs" in query:
            is_get_luns = False
            is_ldev_detail = True
        if lun_input is not None or (name_input is not None or hg_number is not None):
            is_get_luns = True
            is_ldev_detail = False
        host_groups = self.gateway.get_host_groups(
            ports_input, name_input, hg_number, is_get_wwns, is_get_luns, is_ldev_detail
        )
        if lun_input is not None:
            new_data = []
            for hg in host_groups.data:
                for lun in hg.lunPaths:
                    if lun_input == lun.lun:
                        hg.lunPaths = [lun]
                        new_data.append(hg)
                        break
            host_groups.data = new_data

        return host_groups

    @log_entry_exit
    def get_ports(self):
        return self.gateway.get_ports()

    @log_entry_exit
    def get_one_host_group(self, port_input, name):
        return self.gateway.get_one_host_group(port_input, name)

    @log_entry_exit
    def get_one_host_group_using_hg_port_id(self, port_id, hg_id):
        logger = Log()

        if not self.all_hgs:
            self.all_hgs = self.get_all_host_groups(self.serial)

        logger.writeDebug(f"self.all_hgs{self.all_hgs}")
        if self.all_hgs:
            for hg in self.all_hgs.data:
                if hg.portId == port_id and hg.hostGroupNumber == hg_id:
                    hg.port = hg.portId
                    return hg
        return None

    @log_entry_exit
    def get_all_host_groups(self, serial):
        return self.gateway.get_all_hgs()

    @log_entry_exit
    def create_host_group(
        self,
        port,
        name,
        wwns,
        host_mode,
        host_mode_options,
        luns=None,
        lun_paths=None,
        hg_number=None,
    ):
        logger = Log()
        try:
            errors, comments = self.gateway.create_host_group(
                port,
                name,
                wwns,
                host_mode,
                host_mode_options,
                luns,
                lun_paths,
                hg_number,
            )
            return errors, comments
        except Exception as e:
            err_msg = VSPHostGroupMessage.HG_CREATE_FAILED.value + str(e)
            logger.writeError(err_msg)
            raise Exception(err_msg)

    @log_entry_exit
    def delete_host_group(self, hg, is_delete_all_luns):
        hg = self.gateway.delete_host_group(hg, is_delete_all_luns)

    @log_entry_exit
    def add_wwns_to_host_group(self, hg, wwns):
        return self.gateway.add_wwns_to_host_group(hg, wwns)

    @log_entry_exit
    def delete_wwns_from_host_group(self, hg, wwns):
        return self.gateway.delete_wwns_from_host_group(hg, wwns)

    @log_entry_exit
    def add_luns_to_host_group(self, hg, luns):
        return self.gateway.add_luns_to_host_group(hg, luns)

    @log_entry_exit
    def add_lun_paths_to_host_group(self, hg, lun_paths):
        return self.gateway.add_lun_paths_to_host_group(hg, lun_paths)

    @log_entry_exit
    def delete_luns_from_host_group(self, hg, luns):
        return self.gateway.delete_luns_from_host_group(hg, luns)

    @log_entry_exit
    def set_host_mode(self, hg, host_mode, host_mode_options):
        self.gateway.set_host_mode(hg, host_mode, host_mode_options)

    @log_entry_exit
    def update_wwn_nickname(self, hg, wwns):
        return self.gateway.set_nickname_of_wwn(hg, wwns)

    @log_entry_exit
    def set_asymmetric_access_priority(self, port_id, hg_number, access_priority):
        return self.gateway.set_prirotiy_level_of_alua_path(
            port_id, hg_number, access_priority
        )

    @log_entry_exit
    def release_host_reserve(self, port_id, hg_number, lun=None):
        self.gateway.release_host_reservation_status(port_id, hg_number, lun)

    @log_entry_exit
    def get_host_mode_options(self):
        return self.gateway.get_host_mode_options()

    @log_entry_exit
    def handle_multi_hg_with_present_ldevs(
        self, hg_number, hg_name, ports, ldevs, sub_state
    ):
        logger = Log()

        hg_objects = []
        hg_objects_dict = {}
        logger.writeDebug("PROV:handle_multi_hg_with_present_ldevs:")
        logger.writeDebug(f"sub state: {sub_state}")

        def fetch_host_group(port):
            if hg_name is not None:
                hg = self.get_one_host_group(port, hg_name).data
            else:
                hg = self.get_one_host_group_using_hg_port_id(port, hg_number)
            if hg is None:
                raise Exception(VSPHostGroupMessage.PORTS_PARAMETER_INVALID.value)
            return hg

        executor = ThreadPoolExecutor(
            max_workers=MAX_WORKER_THREADS,
            thread_name_prefix="FetchHostGroups",
        )
        try:
            futures = {executor.submit(fetch_host_group, port): port for port in ports}
            for future in as_completed(futures):
                try:
                    hg = future.result()
                    hg_objects.append(hg)
                    hg_objects_dict.setdefault(hg.hostGroupNumber, []).append(hg.portId)
                except Exception as exc:
                    logger.writeError(
                        f"Port {futures[future]} generated an exception: {exc}"
                    )
                    raise exc
        except KeyboardInterrupt:
            executor.shutdown(wait=False, cancel_futures=True)
            raise
        finally:
            executor.shutdown(wait=True)

        all_comments, all_errors = [], []

        if sub_state == VSPHostGroupConstant.STATE_PRESENT_LDEV:

            def process_present(hg_num, port_ids):
                return self.gateway.add_ldev_and_ports_to_host_group(
                    hg_num, ldevs, port_ids
                )

            executor = ThreadPoolExecutor(
                max_workers=MAX_WORKER_THREADS,
                thread_name_prefix="ProcessPresent",
            )
            try:
                futures = {
                    executor.submit(process_present, hg_num, port_ids): hg_num
                    for hg_num, port_ids in hg_objects_dict.items()
                }
                for future in as_completed(futures):
                    try:
                        comments, errors = future.result()
                        all_comments.extend(comments or [])
                        all_errors.extend(errors or [])
                    except Exception as exc:
                        logger.writeError(
                            f"Host group {futures[future]} exception: {exc}"
                        )
                        all_errors.append(str(exc))
            except KeyboardInterrupt:
                executor.shutdown(wait=False, cancel_futures=True)
                raise
            finally:
                executor.shutdown(wait=True)

        elif sub_state == VSPHostGroupConstant.STATE_UNPRESENT_LDEV:

            def process_unpresent(hg):
                updated_hg = self.get_one_host_group(hg.portId, hg.hostGroupName).data
                return self.gateway.delete_luns_from_host_group(updated_hg, ldevs)

            executor = ThreadPoolExecutor(
                max_workers=MAX_WORKER_THREADS, thread_name_prefix="ProcessUnpresent"
            )
            try:
                futures = {
                    executor.submit(process_unpresent, hg): hg for hg in hg_objects
                }
                for future in as_completed(futures):
                    try:
                        com, err = future.result()
                        all_errors.extend(err or [])
                        all_comments.extend(com or [])
                    except Exception as exc:
                        logger.writeError(
                            f"Host group {futures[future]} exception: {exc}"
                        )
                        all_errors.append(str(exc))
            except KeyboardInterrupt:
                executor.shutdown(wait=False, cancel_futures=True)
                raise
            finally:
                executor.shutdown(wait=True)

        return all_comments, all_errors
