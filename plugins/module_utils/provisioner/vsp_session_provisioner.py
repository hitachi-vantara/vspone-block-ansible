try:
    from ..gateway.vsp_session_gateway import VSPSessionGateway
    from ..common.ansible_common import log_entry_exit

except ImportError:
    from gateway.vsp_session_gateway import VSPSessionGateway
    from common.ansible_common import log_entry_exit


class VSPSessionProvisioner:

    def __init__(self, connection_info):
        self.gateway = VSPSessionGateway(connection_info)

    @log_entry_exit
    def get_sessions(self, spec=None):
        response = self.gateway.get_sessions()
        if response:
            return response.data_to_snake_case_list()
        else:
            return None

    @log_entry_exit
    def get_session_by_id(self, id, token):
        response = self.gateway.get_session_by_id(id, token)
        if response:
            return response.camel_to_snake_dict()
        else:
            return None

    @log_entry_exit
    def delete_session(self, id, token, force=None):
        return self.gateway.delete_session(id, token, force)

    @log_entry_exit
    def create_session(self, spec=None):
        alive_time_in_seconds = None
        if spec and spec.alive_time_in_seconds:
            alive_time_in_seconds = spec.alive_time_in_seconds
        authentication_timeout = None
        if spec and spec.authentication_timeout:
            authentication_timeout = spec.authentication_timeout
        response = self.gateway.create_session(
            alive_time_in_seconds, authentication_timeout
        )
        if response:
            return response.camel_to_snake_dict()
        else:
            return None
