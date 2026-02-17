try:
    from ..common.hv_api_constants import API
    from .gateway_manager import SDSBConnectionManager
    from ..common.hv_log import Log
    from ..common.ansible_common import log_entry_exit
    from ..model.sdsb_external_auth_server_models import (
        ExternalAuthServerSetting,
        ExternalAuthServerConnectionVerification,
    )
except ImportError:
    from common.hv_api_constants import API
    from .gateway_manager import SDSBConnectionManager
    from common.hv_log import Log
    from common.ansible_common import log_entry_exit
    from model.sdsb_external_auth_server_models import (
        ExternalAuthServerSetting,
        ExternalAuthServerConnectionVerification,
    )

GET_EXTERNAL_AUTH_SERVER_SETTINGS = "v1/objects/external-auth-server-setting"
VERIFY_EXTERNAL_AUTH_SERVER_SETTINGS = (
    "v1/objects/external-auth-server-setting/actions/verify-connectivity/invoke"
)
UPDATE_EXTERNAL_AUTH_SERVER_SETTINGS = "v1/objects/external-auth-server-setting"

logger = Log()


class SDSBExternalAuthServerGateway:

    def __init__(self, connection_info):
        self.connection_manager = SDSBConnectionManager(
            connection_info.address, connection_info.username, connection_info.password
        )

    @log_entry_exit
    def get_external_auth_server_settings(self):
        end_point = GET_EXTERNAL_AUTH_SERVER_SETTINGS
        external_auth_server_settings = self.connection_manager.get(end_point)
        logger.writeDebug(
            "GW:get_external_auth_server_settings:data={}",
            external_auth_server_settings,
        )

        return ExternalAuthServerSetting(**external_auth_server_settings)

    @log_entry_exit
    def verify_external_auth_server_settings(self):
        end_point = VERIFY_EXTERNAL_AUTH_SERVER_SETTINGS
        verification_response = self.connection_manager.post(end_point, data={})
        logger.writeDebug(
            "GW:verify_external_auth_server_settings:data={}", verification_response
        )

        return ExternalAuthServerConnectionVerification(**verification_response)

    @log_entry_exit
    def update_external_auth_server_settings(
        self, patch_external_auth_server_setting_param
    ):
        end_point = UPDATE_EXTERNAL_AUTH_SERVER_SETTINGS
        update_response = self.connection_manager.patch(
            end_point, data=patch_external_auth_server_setting_param
        )
        logger.writeDebug(
            "GW:update_external_auth_server_settings:data={}", update_response
        )

        return ExternalAuthServerSetting(**update_response)

    @log_entry_exit
    def download_external_auth_server_root_certificate(
        self, host_ip, file_name, target_server
    ):
        downloads_connection_manager = SDSBConnectionManager(
            host_ip, self.connection_manager.username, self.connection_manager.password
        )
        end_point = f"v1/objects/external-auth-server-root-certificates/{target_server}/download"

        resp = downloads_connection_manager.download_file(end_point)
        # Write to file
        with open(file_name, mode="wb") as file:
            file.write(resp)

        logger.writeDebug(
            "GW:download_external_auth_server_root_certificate:certificate saved to {}",
            file_name,
        )
        return

    @log_entry_exit
    def import_external_auth_server_root_certificate(
        self, host_ip, certificate_path, target_server
    ):
        imports_connection_manager = SDSBConnectionManager(
            host_ip, self.connection_manager.username, self.connection_manager.password
        )
        end_point = f"v1/objects/external-auth-server-root-certificates/{target_server}/actions/import/invoke"

        # Build multipart form data for the certificate file
        import os

        boundary = self.connection_manager.boundary
        body = bytearray()

        # Read certificate file
        with open(certificate_path, "rb") as cert_file:
            cert_content = cert_file.read()

        # Build multipart body
        filename = os.path.basename(certificate_path)
        body.extend(f"--{boundary}\r\n".encode("utf-8"))
        body.extend(
            f'Content-Disposition: form-data; name="rootCertificate"; filename="{filename}"\r\n'.encode(
                "utf-8"
            )
        )
        body.extend(b"Content-Type: application/octet-stream\r\n\r\n")
        body.extend(cert_content)
        body.extend(b"\r\n")
        body.extend(f"--{boundary}--\r\n".encode("utf-8"))

        # Headers
        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Expect": "",  # Suppress "Expect: 100-continue"
        }

        logger.writeDebug("GW:import_smtp_root_certificate:endpoint={}", end_point)

        try:
            # Make the POST request with multipart data
            resp = self.connection_manager._make_request_for_file(
                method="POST",
                end_point=end_point,
                data=bytes(body),
                headers_input=headers,
            )
            logger.writeDebug(f"resp: {resp}")
            job_id = resp[API.JOB_ID]
            return self.connection_manager._process_job(job_id)
        except Exception as err:
            logger.writeException(err)
            raise err
