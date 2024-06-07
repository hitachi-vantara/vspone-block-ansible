class Http(object):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"
    BASE_URL = "/ConfigurationManager/"
    CONTENT_TYPE = "Content-Type"
    APPLICATION_JSON = "application/json"
    RESPONSE_JOB_STATUS = "Response-Job-Status"
    COMPLETED = "Completed"
    HEADERS_JSON = {CONTENT_TYPE: APPLICATION_JSON, RESPONSE_JOB_STATUS: COMPLETED}
    HTTP = "http://"
    HTTPS = "https://"
    DEFAULT_PORT = 443
    DEFAULT_SSL_PORT = 443
    OPEN_URL_TIMEOUT = 300
    USER_AGENT = "automation-module"


class LogMessages(object):
    ENTER_METHOD = "Enter method: {}"
    LEAVE_METHOD = "Leave method: {}"
    API_REQUEST_START = "API Request: {} {}"
    API_RESPONSE = "API Response: {}"


class StateValue:
    """
    Enum class for volume state
    """

    QUERY = "query"
    PRESENT = "present"
    ABSENT = "absent"
    SPLIT = "split"
    SYNC = "sync"
    RESTORE = "restore"
    UPDATE = "update"
    RE_SYNC = "resync"


class CommonConstants:
    #UCP_NAME = 'ucp-ansible-test'
    UCP_NAME = 'Storage_System'
    UCP_SERIAL = 'UCP-CI-202404'
    PARTNER_ID = 'apiadmin'
    SUBSCRIBER_ID = '12345'
    ONBOARDING = 'ONBOARDING'
    NORMAL = "NORMAL"


class ConnectionTypes:
    GATEWAY = "gateway"
    DIRECT = "direct"


class GatewayClassTypes:
    VSP_VOLUME = "vsp_volume"
    VSP_HOST_GROUP = "vsp_host_group"
    VSP_SNAPSHOT = "vsp_snapshot"
    VSP_SHADOW_IMAGE_PAIR = "vsp_shadow_image_pair"
    VSP_STORAGE_SYSTEM = "vsp_storage_system"
    VSP_ISCSI_TARGET = "vsp_iscsi_target"
    VSP_STORAGE_POOL = "vsp_storage_pool"
    VSP_PARITY_GROUP = "vsp_parity_group"

    SDSB_CHAP_USER = "sdsb_chap_user"
    SDSB_COMPUTE_NODE = "sdsb_compute_node"
    SDSB_VOLUME = "sdsb_volume"
    SDSB_STORAGE_SYSTEM = "sdsb_storage_system"
    SDSB_POOL = "sdsb_pool"
    SDSB_PORT_AUTH = "sdsb_port_auth"
    SDSB_PORT = "sdsb_port"

    UAIG_SUBSCRIBER = "uaig_subscriber"
    UAIG_PASSWORD = "uaig_password"


class VSPHostGroupConstant:
    PORT_TYPE_FIBRE = "FIBRE"
    PORT_TYPE_FCOE = "FCoE"
    PORT_TYPE_HNASS = "HNASS"
    PORT_TYPE_HNASU = "HNASU"
    STATE_PRESENT_LUN = "present_lun"
    STATE_UNPRESENT_LUN = "unpresent_lun"
    STATE_SET_HOST_MODE = "set_host_mode_and_hmo"
    STATE_ADD_WWN = "add_wwn"
    STATE_REMOVE_WWN = "remove_wwn"


class VSPIscsiTargetConstant:
    PORT_TYPE_ISCSI = "ISCSI"
    AUTH_MODE_CHAP = "CHAP"
    AUTH_MODE_NONE = "NONE"
    AUTH_MODE_BOTH = "BOTH"
    AUTH_DIRECTION_ONE_WAY = "S"
    AUTH_DIRECTION_MUTUAL = "D"
    WAY_OF_CHAP_USER = "INI"
    STATE_ADD_INITIATOR = "add_iscsi_initiator"
    STATE_REMOVE_INITIATOR = "remove_iscsi_initiator"
    STATE_ATTACH_LUN = "attach_lun"
    STATE_DETACH_LUN = "detach_lun"
    STATE_ADD_CHAP_USER = "add_chap_user"
    STATE_REMOVE_CHAP_USER = "remove_chap_user"

class GatewayConstant:
    ADMIN_USER_NAME = "admin"