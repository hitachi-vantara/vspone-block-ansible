try:
    from ..provisioner.vsp_session_provisioner import VSPSessionProvisioner
    from ..common.hv_constants import StateValue
    from ..common.hv_log import Log
    from ..common.ansible_common import (
        log_entry_exit,
    )
    from ..message.vsp_session_msgs import VSPSessionValidationMsg
except ImportError:
    from provisioner.sdsb_session_provisioner import VSPSessionProvisioner
    from common.hv_constants import StateValue
    from common.hv_log import Log
    from common.ansible_common import (
        log_entry_exit,
    )
    from message.vsp_session_msgs import VSPSessionValidationMsg

logger = Log()


class VSPSessionReconciler:

    def __init__(self, connection_info):
        self.connection_info = connection_info
        self.provisioner = VSPSessionProvisioner(self.connection_info)

    @log_entry_exit
    def get_session_facts(self, spec=None):
        if spec and spec.id:
            if spec.token is None:
                raise ValueError(
                    VSPSessionValidationMsg.TOKEN_MISSING_FOR_GET_BY_ID.value
                )
            return self.get_session_by_id(spec)
        ret_data = self.provisioner.get_sessions(spec)
        logger.writeDebug("RC:get_sesion_facts:ret_data = {}", ret_data)
        return ret_data

    @log_entry_exit
    def get_session_by_id(self, spec):
        id = spec.id
        token = spec.token
        try:
            return self.provisioner.get_session_by_id(id, token)
        except Exception as e:
            logger.writeException(e)
            spec.comment = str(e)
            return {}

    @log_entry_exit
    def delete_session(self, spec):
        if spec.id is None:
            raise ValueError(VSPSessionValidationMsg.ID_MISSING_FOR_DELETE.value)
        if spec.token is None:
            raise ValueError(VSPSessionValidationMsg.TOKEN_MISSING_FOR_DELETE.value)
        try:
            self.provisioner.delete_session(spec.id, spec.token, spec.force)
            self.connection_info.changed = True
            return True, None
        except Exception as e:
            logger.writeException(e)
            return False, str(e)

    @log_entry_exit
    def create_session(self, spec=None):
        if spec and spec.alive_time_in_seconds:
            if not (1 <= spec.alive_time_in_seconds <= 300):
                raise ValueError(VSPSessionValidationMsg.INVALID_ALIVE_TIME.value)
        if spec and spec.authentication_timeout:
            if not (1 <= spec.authentication_timeout <= 900):
                raise ValueError(
                    VSPSessionValidationMsg.INVALID_AUTHENTICATION_TIMEOUT.value
                )
        response = self.provisioner.create_session(spec)
        # logger.writeDebug("RC:create_session:response = {}", response)
        self.connection_info.changed = True
        return response

    @log_entry_exit
    def reconcile_session(self, state, spec):

        if state.lower() == StateValue.PRESENT:
            return self.create_session(spec)

        if state.lower() == StateValue.ABSENT:

            response, msg = self.delete_session(spec)
            if response:
                return f"Session with id {spec.id} is deleted successfully."
            else:
                self.connection_info.changed = False
                return f"Could not delete session, ensure session ID {spec.id} is valid. {msg}"
