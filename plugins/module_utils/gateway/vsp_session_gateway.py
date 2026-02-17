try:
    from .vsp_session_manager import SessionManager
    from ..common.ansible_common import log_entry_exit
    from ..common.hv_log import Log
    from ..model.vsp_session_models import (
        SessionResponseList,
        CreateSessionResponse,
    )
except ImportError:
    from .vsp_session_manager import SessionManager
    from common.ansible_common import log_entry_exit
    from common.hv_log import Log
    from model.vsp_session_models import (
        SessionResponseList,
        CreateSessionResponse,
    )
logger = Log()


class VSPSessionGateway:

    def __init__(self, connection_info):
        self.connection_info = connection_info
        self.session_manager = SessionManager()

    @log_entry_exit
    def get_sessions(self):
        response = self.session_manager.get_sessions(self.connection_info)
        return SessionResponseList().dump_to_object(response)

    @log_entry_exit
    def get_session_by_id(self, id, token):
        try:
            response = self.session_manager.get_session_by_id(
                self.connection_info, id, token
            )
            # logger.writeDebug("GW:get_session_by_id:data={}", response)
            return CreateSessionResponse(**response)
        except Exception as ex:
            logger.writeDebug("GW:get_session_by_id:=Exception{}", ex)
            err_msg = f"Session with ID {id} not found. " + str(ex)
            raise ValueError(err_msg)

    @log_entry_exit
    def create_session(self, alive_time=None, authentication_timeout=None):
        response = self.session_manager.create_session(
            self.connection_info, alive_time, authentication_timeout
        )
        # logger.writeDebug("GW:create_session:data={}", response)
        return CreateSessionResponse(**response)

    @log_entry_exit
    def delete_session(self, id, token, force=None):
        response = self.session_manager.delete_user_session(
            self.connection_info, id, token, force
        )
        logger.writeDebug("GW:delete_session:data={}", response)
        return response
