try:
    from .gateway_manager import SDSBConnectionManager
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..common.sdsb_utils import convert_keys_to_snake_case, replace_nulls

except ImportError:
    from .gateway_manager import SDSBConnectionManager
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from common.sdsb_utils import convert_keys_to_snake_case, replace_nulls

GET_EVENT_LOGS = "v1/objects/event-logs"
GET_EVENT_LOGS_QUERY = "v1/objects/event-logs{}"

logger = Log()


class SDSBEventLogsDirectGateway:

    def __init__(self, connection_info):
        self.connection_manager = SDSBConnectionManager(
            connection_info.address, connection_info.username, connection_info.password
        )

    @log_entry_exit
    def get_query_parameters(
        self,
        spec,
    ):
        # logger.writeDebug(f"fault_domain_id={fault_domain_id}, name={name}, cluster_role={cluster_role}, protection_domain_id={protection_domain_id}")
        first = True
        query = ""
        if spec.start_time:
            query = query + f"?startTime={spec.start_time}"
            first = False
        if spec.end_time:
            if first:
                query = query + f"?endTime={spec.end_time}"
                first = False
            else:
                query = query + f"&endTime={spec.end_time}"
        if spec.severity:
            if first:
                query = query + f"?severity={spec.severity}"
                first = False
            else:
                query = query + f"&severity={spec.severity}"
        if spec.severity_ge:
            if first:
                query = query + f"?severitGey={spec.severity_ge}"
                first = False
            else:
                query = query + f"&severityGe={spec.severity_ge}"
        if spec.max_events:
            if first:
                query = query + f"?maxEvents={spec.max_events}"
                first = False
            else:
                query = query + f"&maxEvents={spec.max_events}"
        return query

    @log_entry_exit
    def get_event_logs(self, spec=None):

        end_point = GET_EVENT_LOGS

        if spec is not None:
            query = self.get_query_parameters(spec)
            end_point = GET_EVENT_LOGS_QUERY.format(query)
            logger.writeDebug("GW:get_event_logs:end_point={}", end_point)

        event_logs = self.connection_manager.get(end_point)
        logger.writeDebug("GW:get_event_logs:data={}", event_logs)

        converted = convert_keys_to_snake_case(event_logs)
        cleaned_data = replace_nulls(converted)
        return cleaned_data
