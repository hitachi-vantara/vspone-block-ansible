from __future__ import absolute_import, division, print_function

__metaclass__ = type

from abc import ABC, abstractmethod
import json
import time


from ansible.module_utils.urls import open_url, urllib_error, socket


try:
    from ..common.hv_api_constants import API
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..common.hv_exceptions import *
    from ..common.vsp_constants import Endpoints
except ImportError:
    # created a soft link from the current directory to avoid import error
    from common.hv_api_constants import API
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from common.hv_exceptions import *
    from common.vsp_constants import Endpoints


logger = Log()
moduleName = "Gateway Manager"
OPEN_URL_TIMEOUT = 600


class ConnectionManager(ABC):
    def __init__(self, address, username, password):
        self.address = address
        self.username = username
        self.password = password
        self.base_url = None

        if not self.base_url:
            self.base_url = self.form_base_url()

    @abstractmethod
    def form_base_url(self):
        pass

    def getAuthToken(self):
        pass

    def get_job(self):
        """get job method"""
        return

    @log_entry_exit
    def _load_response(self, response):
        """returns dict if json, native string otherwise"""
        try:
            text = response.read().decode("utf-8")
            logger.writeDebug(text)
            msg = {}
            raw_message = json.loads(text)
            if not len(raw_message):
                if raw_message.get("errorSource"):
                    msg[API.CAUSE] = raw_message[API.CAUSE]
                    msg[API.SOLUTION] = raw_message[API.SOLUTION]
                    return msg
            return raw_message
        except ValueError:
            return text

    @log_entry_exit
    def _make_request(self, method, end_point, data=None):

        url = self.base_url + "/" + end_point
        logger.writeDebug("url = {}", url)

        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if data is not None:
            data = json.dumps(data)
            x = url.endswith("chap-users")
            if not x:
                logger.writeDebug("data = {}", data)

        logger.writeDebug("method = {}", method)
        logger.writeDebug("headers = {}", headers)

        MAX_TIME_OUT = 300

        try:
            response = open_url(
                url=url,
                method=method,
                headers=headers,
                data=data,
                use_proxy=False,
                timeout=MAX_TIME_OUT,
                url_username=self.username,
                url_password=self.password,
                force_basic_auth=True,
                validate_certs=False,
            )
        except (urllib_error.HTTPError, socket.timeout) as err:
            error_resp = json.loads(err.read().decode())
            if error_resp.get("errorSource"):
                msg = {}
                msg[API.CODE] = err.code
                msg[API.CAUSE] = (
                    error_resp[API.CAUSE] if error_resp.get(API.CAUSE) else ""
                )
                msg[API.SOLUTION] = (
                    error_resp[API.SOLUTION] if error_resp.get(API.SOLUTION) else ""
                )
                msg[API.MESSAGE] = (
                    error_resp[API.MESSAGE] if error_resp.get(API.MESSAGE) else ""
                )
                raise Exception(msg)
            else:
                msg = {"code": err.code, "msg": err.msg}
                raise Exception(msg)
        except Exception as e:
            logger.writeDebug("Exception = {}", e)
            raise Exception(e)

        if response.status not in (200, 201, 202):
            error_msg = json.loads(response.read())
            logger.writeDebug("error_msg = {}", error_msg)
            raise Exception(error_msg, response.status)

        return self._load_response(response)

    @log_entry_exit
    def create(self, endpoint, data):
        return self._make_request(method="POST", end_point=endpoint, data=data)

    @log_entry_exit
    def post(self, endpoint, data):

        post_response = self._make_request(method="POST", end_point=endpoint, data=data)
        logger.writeDebug("post_response = {}", post_response)
        job_id = post_response[API.JOB_ID]
        response = None
        retryCount = 0
        while response is None and retryCount < 60:
            job_response = self.get_job(job_id)
            logger.writeDebug("post: job_response = {}", job_response)
            job_status = job_response[API.STATUS]
            job_state = job_response[API.STATE]
            response = None
            if job_status == API.COMPLETED:
                if job_state == API.SUCCEEDED:
                    # For POST call to add chap user to port, affected resource is empty
                    if len(job_response[API.AFFECTED_RESOURCES]) > 0:
                        response = job_response[API.AFFECTED_RESOURCES][0]
                    else:
                        response = job_response["self"]
                else:
                    raise Exception(self.job_exception_text(job_response))
            else:
                retryCount = retryCount + 1
                time.sleep(10)

        if response is None:
            raise Exception("Timeout Error! The taks was not completed in 10 minutes")

        resourceId = response.split("/")[-1]
        logger.writeDebug("response = {}", response)
        logger.writeDebug("resourceId = {}", resourceId)
        return resourceId

    @log_entry_exit
    def patch(self, endpoint, data):
        patch_response = self._make_request(
            method="PATCH", end_point=endpoint, data=data
        )
        job_id = patch_response[API.JOB_ID]
        response = None
        retryCount = 0
        while response is None and retryCount < 60:
            job_response = self.get_job(job_id)
            job_status = job_response[API.STATUS]
            job_state = job_response[API.STATE]
            logger.writeDebug("patch: job_response = {}", job_response)
            response = None
            if job_status == API.COMPLETED:
                if job_state == API.SUCCEEDED:
                    # For PATCH port-auth-settings, affected resource is empty
                    if len(job_response[API.AFFECTED_RESOURCES]) > 0:
                        response = job_response[API.AFFECTED_RESOURCES][0]
                    else:
                        response = job_response["self"]
                else:
                    raise Exception(self.job_exception_text(job_response))
            else:
                retryCount = retryCount + 1
                time.sleep(10)

        if response is None:
            raise Exception("Timeout Error! The taks was not completed in 10 minutes")

        resourceId = response.split("/")[-1]
        logger.writeDebug("response = {}", response)
        logger.writeDebug("resourceId = {}", resourceId)
        return resourceId

    @log_entry_exit
    def job_exception_text(self, job_response):

        keys = job_response[API.ERROR].keys()
        logger.writeDebug("job_response_error_keys= {}", keys)
        result_text = ""
        if API.MESSAGE_ID in keys:
            result_text += job_response[API.ERROR][API.MESSAGE_ID] + " "
        if API.MESSAGE in keys:
            result_text += job_response[API.ERROR][API.MESSAGE] + " "
        if API.CAUSE in keys:
            result_text += job_response[API.ERROR][API.CAUSE] + " "
        if API.SOLUTION in keys:
            result_text += job_response[API.ERROR][API.SOLUTION] + " "

        return result_text

    @log_entry_exit
    def read(self, endpoint):
        return self._make_request("GET", endpoint)

    @log_entry_exit
    def get(self, endpoint):
        return self._make_request("GET", endpoint)

    @log_entry_exit
    def update(self, endpoint, data):
        return self._make_request("PUT", endpoint, data)

    @log_entry_exit
    def delete(self, endpoint, data=None):
        delete_response = self._make_request(
            method="DELETE", end_point=endpoint, data=data
        )
        job_id = delete_response[API.JOB_ID]
        response = None
        retryCount = 0
        while response is None and retryCount < 60:
            job_response = self.get_job(job_id)
            job_status = job_response[API.STATUS]
            job_state = job_response[API.STATE]
            logger.writeDebug("job_response = {}", job_response)
            response = None
            if job_status == API.COMPLETED:
                if job_state == API.SUCCEEDED:
                    # For DELETE CHAP user from  port, affected resource is empty
                    if len(job_response[API.AFFECTED_RESOURCES]) > 0:
                        response = job_response[API.AFFECTED_RESOURCES][0]
                    else:
                        response = job_response["self"]
                else:
                    raise Exception(self.job_exception_text(job_response))
            else:
                retryCount = retryCount + 1
                time.sleep(10)

        if response is None:
            raise Exception("Timeout Error! The taks was not completed in 10 minutes")

        resourceId = response.split("/")[-1]
        logger.writeDebug("response = {}", response)
        logger.writeDebug("resourceId = {}", resourceId)
        return resourceId


class UAIGConnectionManager:
    def __init__(self, address, username=None, password=None, token=None):

        self.address = address
        self.username = username
        self.password = password
        self.token = token
        self.base_url = None
        self.logger = Log()

        if not self.base_url:
            self.base_url = self.form_base_url()

        if not token:
            self.token = self.get_auth_token()

    @log_entry_exit
    def form_base_url(self):
        return f"https://{self.address}/porcelain"

    @log_entry_exit
    def _make_login_request(self, method, url, data):
        # url = self.base_url + endpoint
        logger.writeDebug("UAIGConnectionManager._make_login_request")
        headers = {"Accept": "application/json", "Content-Type": "application/json"}

        USER_AGENT = "automation-module"

        if data is not None:
            body = json.dumps(data)
        try:
            response = open_url(
                url=url,
                method=method,
                headers=headers,
                data=body,
                use_proxy=False,
                url_username=None,
                url_password=None,
                force_basic_auth=True,
                validate_certs=False,
                timeout=OPEN_URL_TIMEOUT,
                http_agent=USER_AGENT,
            )
        except (urllib_error.URLError, socket.timeout) as err:
            raise Exception(err)
        except Exception as err:
            raise Exception(err)

        if response.status not in (200, 201):
            raise Exception(
                msg=f"Failed to make {method} request to {url}: {response.read()}"
            )

        return self._load_response(response)

    @log_entry_exit
    def _make_request(self, method, end_point, data=None, headers_input=None):

        logger.writeDebug("UAIGConnectionManager._make_request")

        url = self.base_url + "/" + end_point

        headers = self.get_auth_header()
        headers["accept"] = "application/json"
        headers["Content-Type"] = "application/json"
        if headers_input is not None:
            headers.update(headers_input)

        if data is not None:
            data = json.dumps(data)
        try:

            response = open_url(
                url=url,
                method=method,
                headers=headers,
                data=data,
                use_proxy=False,
                url_username=None,
                url_password=None,
                force_basic_auth=False,
                validate_certs=False,
                timeout=OPEN_URL_TIMEOUT,
            )
        except (urllib_error.HTTPError, socket.timeout) as err:
            error_resp = json.loads(err.read().decode())
            error_dtls = (
                error_resp.get("error").get("message")
                if error_resp.get("error")
                else error_resp.get("detail")
            )
            raise Exception(error_dtls)
        except Exception as err:
            raise Exception(err)

        if response.status not in (200, 201, 202):
            raise Exception(
                f"Failed to make {method} request to {url}: {response.read()}"
            )
        return self._load_response(response)

    @log_entry_exit
    def _load_response(self, response):
        """returns dict if json, native string otherwise"""
        try:
            text = response.read().decode("utf-8")
            logger.writeDebug(text)
            msg = {}
            raw_message = json.loads(text)
            if not len(raw_message):
                if raw_message.get("errorSource"):
                    msg[API.CAUSE] = raw_message[API.CAUSE]
                    msg[API.SOLUTION] = raw_message[API.SOLUTION]
                    return msg
            return raw_message
        except ValueError:
            return text

    @log_entry_exit
    def get_auth_token(self):
        # TODO : Implement cache ... how long this token is valid for?
        funcName = "UAIGConnectionManager:get_auth_token"
        # self.logger.writeEnterSDK(funcName)

        body = {"username": self.username, "password": self.password}

        end_point = "v2/auth/login"
        url = "{0}/{1}".format(self.base_url, end_point)

        try:
            response = self.login(url=url, data=body)
        except Exception as e:
            # can be due to wrong address or kong is not ready
            logger.writeDebug(e)
            raise Exception(
                "Failed to establish a connection, please check the Management System address or the credentials."
            )

        token = None
        if response[API.MESSAGE] == API.SUCCESS:
            data = response[API.DATA]
            token = data.get(API.TOKEN)
        else:
            self.logger.writeInfo("Unknown Exception response={}", response)
            raise Exception("UAIG login failed, please check the configuration.")

        self.token = token
        return token

    @log_entry_exit
    def get_auth_header(self):
        headers = {"Authorization": "Bearer {0}".format(self.token)}
        return headers

    @log_entry_exit
    def login(self, url, data):
        return self._make_login_request(method="POST", url=url, data=data)

    @log_entry_exit
    def get(self, end_point, headers=None):
        return self._make_request("GET", end_point, None, headers)

    @log_entry_exit
    def update(self, end_point, data=None):
        return self._make_request(method="PUT", end_point=end_point, data=data)

    @log_entry_exit
    def post(self, endpoint, data, headers_input=None):

        post_response = self._make_request(
            method="POST", end_point=endpoint, data=data, headers_input=headers_input
        )
        if post_response.get(API.DATA) is not None:
            task_id = post_response[API.DATA].get(API.TASK_ID)
            resource_id = post_response[API.DATA].get(API.RESOURCE_ID)
        else:
            task_id = post_response.get(API.TASK_ID)
            resource_id = post_response.get(API.RESOURCE_ID)

        response = None
        retryCount = 0
        while response is None and retryCount < 60:
            task_response = self.get_task(task_id)
            task_status = task_response[API.DATA].get(API.STATUS)
            logger.writeDebug("task_response = {}", task_response)
            response = None

            if task_status == API.SUCCESS:
                if resource_id is not None:
                    response = resource_id
                else:
                    response = task_response
            elif task_status == API.FAILED:
                task_name = task_response[API.DATA].get(API.NAME)
                task_events = task_response[API.DATA].get("events")
                if len(task_events):
                    descriptions = [
                        element.get("description") for element in task_events
                    ]
                # raise Exception(task_name + " " + task_status + " " + descriptions[0])
                raise Exception(f"{task_name} {task_status}, {descriptions[0]}")
            else:
                retryCount = retryCount + 1
                time.sleep(10)

        if response is None:
            raise Exception("Timeout Error! The tasks was not completed in 10 minutes")

        return response

    @log_entry_exit
    def patch(self, endpoint, data=None):
        print(f"Payload {data}")
        post_response = self._make_request(
            method="PATCH", end_point=endpoint, data=data
        )
        if post_response.get(API.DATA) is not None:
            task_id = post_response[API.DATA].get(API.TASK_ID)
            resource_id = post_response[API.DATA].get(
                API.RESOURCE_ID
            )  # there's no resource_id from porcelain's task info
        else:
            task_id = post_response.get(API.TASK_ID)
            resource_id = post_response.get(API.RESOURCE_ID)

        response = None
        retryCount = 0
        while response is None and retryCount < 60:
            task_response = self.get_task(task_id)
            task_status = task_response[API.DATA].get(API.STATUS)
            logger.writeDebug("task_response = {}", task_response)
            response = None
            if task_status == API.SUCCESS:
                if resource_id is not None:
                    response = resource_id
                else:
                    response = task_response
            elif task_status == API.FAILED:
                task_name = task_response[API.DATA].get(API.NAME)
                task_events = task_response[API.DATA].get("events")
                if len(task_events):
                    descriptions = [
                        element.get("description") for element in task_events
                    ]
                raise Exception(task_name + " " + task_status + " " + descriptions[0])
            else:
                retryCount = retryCount + 1
                time.sleep(10)

        if response is None:
            raise Exception("Timeout Error! The taks was not completed in 10 minutes")

        return response

    @log_entry_exit
    def delete(self, endpoint, data=None, headers_input=None):

        post_response = self._make_request(
            method="DELETE", end_point=endpoint, data=data, headers_input=headers_input
        )
        if post_response.get(API.DATA) is not None:
            task_id = post_response[API.DATA].get(API.TASK_ID)
            resource_id = post_response[API.DATA].get(
                API.RESOURCE_ID
            )  # there's no resource_id from porcelain's task info
        else:
            task_id = post_response.get(API.TASK_ID)
            resource_id = post_response.get(API.RESOURCE_ID)

        response = None
        retryCount = 0
        while response is None and retryCount < 60:
            task_response = self.get_task(task_id)
            task_status = task_response[API.DATA].get(API.STATUS)
            logger.writeDebug("task_response = {}", task_response)
            response = None
            if task_status == API.SUCCESS:
                if resource_id is not None:
                    response = resource_id
                else:
                    response = task_response
            elif task_status == API.FAILED:
                task_name = task_response[API.DATA].get(API.NAME)
                task_events = task_response[API.DATA].get("events")
                if len(task_events):
                    descriptions = [
                        element.get("description") for element in task_events
                    ]
                raise Exception(task_name + " " + task_status + " " + descriptions[0])
            else:
                retryCount = retryCount + 1
                time.sleep(10)

        if response is None:
            raise Exception("Timeout Error! The taks was not completed in 10 minutes")

        return response

    @log_entry_exit
    def get_task(self, task_id):
        end_point = "v2/tasks/{}".format(task_id)
        return self._make_request("GET", end_point)


class SDSBConnectionManager(ConnectionManager):

    @log_entry_exit
    def form_base_url(self):
        return f"https://{self.address}/ConfigurationManager/simple"

    @log_entry_exit
    def get_job(self, job_id):
        end_point = "v1/objects/jobs/" + job_id
        return self._make_request("GET", end_point)


class VSPConnectionManager(ConnectionManager):
    session = None

    @log_entry_exit
    def getAuthToken(self):
        # TODO : Implement cache ... how long this token is valid for?
        funcName = "VSPConnectionManager:getAuthToken"
        logger.writeDebug(funcName)
        # self.logger.writeEnterSDK(funcName)

        end_point = Endpoints.SESSIONS
        try:
            response = self._make_request(method="POST", end_point=end_point, data=None)

        except Exception as e:
            # can be due to wrong address or kong is not ready
            logger.writeDebug(e)
            raise Exception(
                "Failed to establish a connection, please check the Management System address or the credentials."
            )

        token = response.get(API.TOKEN)

        headers = {"Authorization": "Session {0}".format(token)}
        # self.logger.writeExitSDK(funcName)
        self.session = headers

    @log_entry_exit
    def form_base_url(self):
        return f"https://{self.address}/ConfigurationManager"

    @log_entry_exit
    def get_job(self, job_id):
        end_point = "v1/objects/jobs/{}".format(job_id)
        return self._make_request("GET", end_point)

    @log_entry_exit
    def pegasus_get(self, endpoint):
        self.getAuthToken()
        return self._make_pegasus_request("GET", endpoint)

    @log_entry_exit
    def pegasus_post(self, endpoint, data):
        self.getAuthToken()
        post_response = self._make_pegasus_request("POST", endpoint, data)

        """
        Sample job response
        [
                {
                    "statusResource": "/ConfigurationManager/simple/v1/objects/command-status/3"
                }
                ]
        """

        job_id = post_response[0].get("statusResource").split("/")[-1]

        response = None
        retryCount = 0
        while response is None and retryCount < 60:
            job_response = self.get_pegasus_job(job_id)
            job_status = job_response.get(API.PEGASUS_STATUS)
            job_progress = job_response.get(API.PEGASUS_PROGRESS)
            logger.writeDebug("patch: job_response = {}", job_response)
            response = None
            if job_progress == API.PEGASUS_COMPLETED:
                if job_status == API.PEGASUS_NORMAL:
                    # For PATCH port-auth-settings, affected resource is empty
                    response = job_response.get(API.AFFECTED_RESOURCES)[0]

                else:
                    raise Exception(job_response.get(API.ERROR_MESSAGE))
            else:
                retryCount = retryCount + 1
                time.sleep(10)

        if response is None:
            raise Exception("Timeout Error! The taks was not completed in 10 minutes")

        resourceId = response.split("/")[-1]
        logger.writeDebug("response = {}", response)
        logger.writeDebug("resourceId = {}", resourceId)
        return resourceId

    def get_pegasus_job(self, job_id):
        url = Endpoints.PEGASUS_JOB
        return self._make_pegasus_request("GET", url.format(job_id))

    @log_entry_exit
    def _make_pegasus_request(self, method, end_point, data=None, headers_input=None):

        logger.writeDebug("VSPConnectionManager._make_pegasus_request")

        url = self.base_url + "/" + end_point

        headers = self.session
        headers["Content-Type"] = "application/json"
        if headers_input is not None:
            headers.update(headers_input)

        TIME_OUT = 300
        if data is not None:
            data = json.dumps(data)
            logger.writeDebug("data = {}", data)
        try:

            response = open_url(
                url=url,
                method=method,
                headers=headers,
                data=data,
                use_proxy=False,
                url_username=None,
                url_password=None,
                force_basic_auth=False,
                validate_certs=False,
                timeout=TIME_OUT,
            )
        except (urllib_error.HTTPError, socket.timeout) as err:
            error_resp = json.loads(err.read().decode())
            error_dtls = (
                error_resp.get("message")
                if error_resp.get("message")
                else error_resp.get("errorMessage")
            )
            raise Exception(error_dtls)
        except Exception as err:
            raise Exception(err)

        if response.status not in (200, 201, 202):
            raise Exception(
                f"Failed to make {method} request to {url}: {response.read()}"
            )
        return self._load_response(response)
