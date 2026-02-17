import json
import threading
import time
import atexit
import urllib.error as urllib_error
from ansible.module_utils.urls import socket
from ansible.module_utils.urls import open_url

try:
    from ..common.ansible_common import mask_token
    from ..common.hv_api_constants import API
    from ..common.hv_log import Log
    from ..common.vsp_constants import Endpoints

    # from .ansible_url import open_url
except ImportError:
    from common.ansible_common import mask_token
    from common.hv_api_constants import API
    from common.hv_log import Log
    from common.vsp_constants import Endpoints

    # from .ansible_url import open_url

logger = Log()

GET_SESSIONS = "v1/objects/sessions"
CREATE_SESSION = "v1/objects/sessions"
DELETE_SESSION = "v1/objects/sessions/{}"
GET_SESSION_BY_ID = "v1/objects/sessions/{}"


def mask_dict_tokens(data: dict) -> dict:
    """
    Mask all token values in a dictionary using mask_token (default n=12).

    Args:
        data (dict): Dictionary with values as tokens (UUID-like strings).

    Returns:
        dict: New dictionary with masked token values.
    """
    return {k: mask_token(v) for k, v in data.items()}


def mask_key_in_dict(data, visible_length=12, mask_char="X", key="token"):
    """
    Masks the value of `key` in the given dict so only the last `visible_length`
    characters are visible. Mutates the dict in place.

    - If the key is missing, None, or not a string, the dict is left unchanged.
    """
    if not isinstance(data, dict):
        return data

    result = data.copy()
    token = data.get(key)

    if not isinstance(token, str):
        return data

    if len(token) > visible_length:
        result[key] = (
            mask_char * (len(token) - visible_length) + token[-visible_length:]
        )

    return result


class SessionManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self.token_to_session_id_map = {}
        self.token_to_connection_info_map = {}
        self.current_sessions = {}
        self.retry_count = 0

        # Thread management
        self.active_threads = []
        self.stop_event = threading.Event()

        # only register once
        if not hasattr(self, "_cleanup_registered"):
            atexit.register(self.cleanup)
            self._cleanup_registered = True
        self._initialized = True

    def cleanup(self):
        # 4. Discard all sessions
        self.discard_sessions()
        logger.writeDebug("SessionManager - cleanup completed.")

    def get_current_session(self, connection_info):
        logger.writeDebug(
            "generate_token current_sessions = {}",
            mask_dict_tokens(self.current_sessions),
        )
        value = self.current_sessions.get(connection_info.address, None)
        if value is not None:
            return value
        else:
            token = self.generate_token(connection_info)
            self.current_sessions[connection_info.address] = token
            return token

    def renew_session(self, connection_info):
        unused = self.current_sessions.pop(connection_info.address, None)
        token = self.generate_token(connection_info)
        self.current_sessions[connection_info.address] = token
        return token

    def get_sessions(self, connection_info):
        end_point = GET_SESSIONS
        response = self._make_request(
            connection_info=connection_info,
            method="GET",
            end_point=end_point,
            data=None,
        )
        return response

    def get_session_by_id(self, connection_info, id, token):
        try:
            end_point = GET_SESSION_BY_ID.format(id)
            response = self._make_request(
                connection_info=connection_info,
                method="GET",
                end_point=end_point,
                token=token,
                data=None,
            )
            logger.writeDebug(
                "GW:get_session_by_id:response={}", mask_key_in_dict(response)
            )
            return response
        except Exception as ex:
            logger.writeDebug("GW:get_session_by_id:=Exception{}", ex)
            raise ex

    def create_session(
        self, connection_info, alive_time=None, authentication_timeout=None
    ):
        if alive_time is None:
            alive_time = 300
        payload = {"aliveTime": alive_time}
        if authentication_timeout is not None:
            payload["authenticationTimeout"] = authentication_timeout
        end_point = CREATE_SESSION
        response = self._make_request(
            connection_info=connection_info,
            method="POST",
            end_point=end_point,
            data=payload,
        )
        return response

    def generate_token(self, connection_info):
        end_point = Endpoints.SESSIONS
        try:
            response = self._make_request(
                connection_info=connection_info,
                method="POST",
                end_point=end_point,
                data=None,
            )
        except Exception as e:
            logger.writeException(e)
            err_msg = (
                "Failed to establish a connection, please check the Management System address or the credentials."
                + str(e)
            )
            raise Exception(err_msg)

        session_id = response.get(API.SESSION_ID)
        token = response.get(API.TOKEN)
        logger.writeDebug(
            "generate_token session id = {} token = {}", session_id, mask_token(token)
        )
        self.token_to_session_id_map[token] = session_id
        self.token_to_connection_info_map[token] = connection_info
        return token

    def _make_request(self, connection_info, method, end_point, token=None, data=None):

        url = f"https://{connection_info.address}/ConfigurationManager/" + end_point

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        username = None
        password = None
        if token:
            headers["Authorization"] = f"Session {token}"
        else:
            username = connection_info.username
            password = connection_info.password

        if data is not None:
            data = json.dumps(data)

        logger.writeDebug("url = {}", url)
        logger.writeDebug("method = {}", method)

        MAX_TIME_OUT = 300

        try:
            response = open_url(
                url=url,
                method=method,
                headers=headers,
                data=data,
                use_proxy=False,
                timeout=MAX_TIME_OUT,
                url_username=username,
                url_password=password,
                force_basic_auth=True if username else False,
                validate_certs=False,
            )
        except socket.timeout as t_err:
            logger.writeError(f"SessionManager._make_request - TimeoutError {t_err}")
            raise TimeoutError(t_err)
        except urllib_error.HTTPError as err:
            logger.writeError(f"SessionManager._make_request - HTTPError {err}")

            if err.code == 503:
                # 503 Service Unavailable
                # wait for 5 mins and try to re-authenticate, we will retry 5 times
                if self.retry_count < 5:
                    logger.writeDebug(
                        "wait for 5 mins and try to generate session token again."
                    )
                    time.sleep(300)
                    self.retry_count += 1
                    return self._make_request(connection_info, method, end_point, data)
                else:
                    if hasattr(err, "read"):
                        error_resp = json.loads(err.read().decode())
                        logger.writeDebug(
                            f"SessionManager.error_resp - error_resp {error_resp}"
                        )
                        error_dtls = (
                            error_resp.get("message")
                            if error_resp.get("message")
                            else error_resp.get("errorMessage")
                        )
                        if error_resp.get("cause"):
                            error_dtls = error_dtls + " " + error_resp.get("cause")

                        if error_resp.get("solution"):
                            error_dtls = error_dtls + " " + error_resp.get("solution")

                        raise Exception(error_dtls)
            raise Exception(err)
        except Exception as err:
            logger.writeException(err)
            raise err

        if response.status not in (200, 201, 202):
            try:
                error_msg = json.loads(response.read())
            except Exception:
                error_msg = response.read().decode()
            logger.writeError("error_msg = {}", error_msg)
            raise Exception(error_msg, response.status)

        return self._load_response(response)

    def _load_response(self, response):
        """
        Returns a dict if JSON, raw bytes if binary, or string if plain text.
        """
        try:
            # Attempt to decode as UTF-8 text
            content = response.read()
            try:
                text = content.decode("utf-8")
            except UnicodeDecodeError:
                # Binary data fallback
                logger.writeDebug(f"Binary response received: {len(content)} bytes")
                return content

            # Attempt to parse as JSON
            try:
                return json.loads(text)
            except json.JSONDecodeError:
                # Not JSON, return text
                return text

        except Exception as e:
            logger.writeDebug(f"Failed to read response: {e}")
            return None

    def delete_session(self, connection_info, session_id, token=None):
        try:
            end_point = DELETE_SESSION.format(session_id)
            method = "DELETE"
            self._make_request(connection_info, method, end_point, token, data=None)
        except Exception as e:
            logger.writeDebug(f"Issue in discarding session. session_id = {session_id}")

    def discard_sessions(self):
        logger.writeDebug("SessionManager - discard_sessions called.")
        for k, v in self.token_to_session_id_map.items():
            conn_info = self.token_to_connection_info_map.get(k)
            self.delete_session(conn_info, v, k)
            logger.writeDebug(
                f"Successfully discarded session. session_id = {v} token = {mask_token(k)}"
            )

    def delete_user_session(self, connection_info, session_id, token=None, force=None):
        try:
            end_point = DELETE_SESSION.format(session_id)
            method = "DELETE"
            payload = None
            if force is not None:
                payload = {"force": force}
            self._make_request(connection_info, method, end_point, token, data=payload)
        except Exception as e:
            logger.writeDebug(
                f"Issue in deleting user created session. session_id = {session_id}"
            )
            raise e
