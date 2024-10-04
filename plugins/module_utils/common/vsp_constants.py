import logging
from ansible.module_utils.six.moves.urllib import parse as urlparse


PEGASUS_MODELS = ["B28", "B26"]

BASIC_STORAGE_DETAILS = None


def get_basic_storage_details():
    global BASIC_STORAGE_DETAILS
    return BASIC_STORAGE_DETAILS

def set_basic_storage_details(storage_details):
    global BASIC_STORAGE_DETAILS
    BASIC_STORAGE_DETAILS = storage_details
class Endpoints(object):

    #vsp storage

    GET_STORAGE_INFO = "v1/objects/storages/instance"
    PEGASUS_JOB = "simple/v1/objects/command-status/{}"
    SESSIONS = "v1/objects/sessions"
    DELETE_SESSION = "v1/objects/sessions/{}"
    
    # Volumes
    POST_LDEVS = "v1/objects/ldevs"
    LDEVS_ONE = "v1/objects/ldevs/{}"
    PEGA_LDEVS_ONE = "simple/v1/objects/volumes/{}"
    GET_LDEVS = "v1/objects/ldevs{}"
    PUT_LDEVS_CHANGE_STATUS = "v1/objects/ldevs/{}/actions/change-status/invoke"
    PUT_LDEVS_SHRED = "v1/objects/ldevs/{}/actions/shred/invoke"
    DELETE_LDEVS = "v1/objects/ldevs/{}"
    POST_EXPAND_LDEV = "v1/objects/ldevs/{}/actions/expand/invoke"
    POST_FORMAT_LDEV = "v1/objects/ldevs/{}/actions/format/invoke"
    UAIG_GET_VOLUMES = "v3/storage/{}/volumes/details{}"
    UAIG_DELETE_ONE_VOLUME = "v3/storage/{}/volumes/{}?isDelete=true"
    GET_FREE_LDEV_FROM_META = "v1/objects/ldevs?ldevOption=undefined&resourceGroupId=0&count=1"
    GET_LDEVS_BY_POOL_ID= "v1/objects/ldevs?poolId={}"

    # Port
    GET_PORTS = "v1/objects/ports"
    GET_PORTS_DETAILS = "v1/objects/ports?detailInfoType=portMode"
    GET_ONE_PORT = "v1/objects/ports/{}"
    GET_ONE_PORT_WITH_MODE = "v1/objects/ports/{}?detailInfoType=portMode"
    UPDATE_PORT = "v1/objects/ports/{}"
    UAIG_GET_PORTS_V2 = "v2/storage/devices/{}/ports{}"
    UAIG_GET_PORTS_V3 = "v3/storage/{}/ports{}"

    # HG
    POST_HOST_GROUPS = "v1/objects/host-groups"
    GET_WWNS = "v1/objects/host-wwns{}"
    POST_WWNS = "v1/objects/host-wwns"
    DELETE_WWNS = "v1/objects/host-wwns/{},{},{}"
    GET_HOST_GROUPS = "v1/objects/host-groups{}"
    GET_HOST_GROUP_ONE = "v1/objects/host-groups/{},{}"
    DELETE_HOST_GROUPS = "v1/objects/host-groups/{},{}"
    PATCH_HOST_GROUPS = "v1/objects/host-groups/{},{}"

    # ISCSI
    GET_HOST_ISCSISS = "v1/objects/host-iscsis{}"
    GET_ONE_HOST_ISCSIS = "v1/objects/host-iscsis/{},{},{}"
    POST_HOST_ISCSIS = "v1/objects/host-iscsis"
    PUT_HOST_ISCSIS = "v1/objects/host-iscsis/{},{},{}"
    DELETE_HOST_ISCSIS = "v1/objects/host-iscsis/{},{},{}"
    UAIG_GET_ISCSIS = "v3/storage/{}/iscsiTargets/details{}"
    UAIG_POST_ISCSIS = "v3/storage/{}/iscsiTargets"
    UAIG_DELETE_ISCSIS = "v3/storage/{}/iscsiTargets/{}?isDelete=true"
    UAIG_POST_IQNS = "v3/storage/{}/iscsiTargets/{}/iqns"
    UAIG_DELETE_IQNS = "v3/storage/{}/iscsiTargets/{}/iqns"
    UAIG_POST_HOST_MODE = "v2/storage/devices/{}/iscsiTargets/{}/hostMode"
    UAIG_POST_CHAP_USER = "v2/storage/devices/{}/iscsiTargets/{}/chapUser"
    UAIG_PATCH_CHAP_USER = "v2/storage/devices/{}/iscsiTargets/{}/chapUser"
    UAIG_DELETE_CHAP_USER = "v2/storage/devices/{}/iscsiTargets/{}/chapUsers/{}"

    # CHAP
    POST_CHAP_USERS = "v1/objects/chap-users"
    PATCH_CHAP_USERS = "v1/objects/chap-users/{}"
    PUT_CHAP_USERS_SINGLE = "v1/objects/chap-users/{},{},{},{}"
    DELETE_CHAP_USERS = "v1/objects/chap-users/{},{},{},{}"
    GET_CHAP_USERS = "v1/objects/chap-users{}"
    GET_CHAP_USER = "v1/objects/chap-users/{},{},{},{}"

    # LUNS
    POST_LUNS = "v1/objects/luns"
    GET_LUNS = "v1/objects/luns{}"
    DELETE_LUNS = "v1/objects/luns/{},{},{}"
    UAIG_POST_LUNS = "v3/storage/{}/iscsiTargets/{}/volumes"
    UAIG_DELETE_LUNS = "v3/storage/{}/iscsiTargets/{}/volumes"
    UAIG_DELETE_LUNS_FROM_HG = "v3/storage/{}/hostGroups/{}/volumes"

    # CG
    GET_LOCAL_CLONE_COPYGROUPS = "v1/objects/local-clone-copygroups"
    POST_LOCAL_CLONE_COPYPAIRS = "v1/objects/local-clone-copypairs"
    GET_LOCAL_CLONE_COPYGROUPS_ONE = "v1/objects/local-clone-copygroups/{}"

    # CP
    POST_LOCAL_CLONE_COPYPAIRS_SPLIT = (
        "v1/objects/local-clone-copypairs/{}/actions/split/invoke"
    )
    POST_LOCAL_CLONE_COPYPAIRS_RESYNC = (
        "v1/objects/local-clone-copypairs/{}/actions/resync/invoke"
    )

    # SI
    POST_SNAPSHOTS = "v1/objects/snapshots"
    GET_SNAPSHOT_GROUPS = "v1/objects/snapshot-groups"
    GET_SNAPSHOT_GROUPS_ONE = "v1/objects/snapshot-groups/{}"
    POST_SNAPSHOTS_SPLIT = "v1/objects/snapshots/{}/actions/split/invoke"
    POST_SNAPSHOTS_RESYNC = "v1/objects/snapshots/{}/actions/resync/invoke"
    POST_SNAPSHOTS_RESTORE = "v1/objects/snapshots/{}/actions/restore/invoke"
    GET_JOBS = "v1/objects/jobs/{}"
    PUT_ISCSI_PORTS_DISCOVER = "v1/objects/iscsi-ports/{}/actions/discover/invoke"
    PUT_ISCSI_PORTS_REGISTER = "v1/objects/iscsi-ports/{}/actions/register/invoke"
    PUT_ISCSI_PORTS_CHECK = "v1/objects/iscsi-ports/{}/actions/check/invoke"
    PUT_ISCSI_PORTS_REMOVE = "v1/objects/iscsi-ports/{}/actions/remove/invoke"
    GET_ISCSI_PORTS = "v1/objects/iscsi-ports/{}"
    GET_EXTERNAL_STORAGE_PORTS = "v1/objects/external-storage-ports{}"
    GET_EXTERNAL_STORAGE_LUNS = "v1/objects/external-storage-luns{}"
    GET_STORAGES_ONE = "v1/objects/storages/{}"
    GET_EXTERNAL_PATH_GROUPS_ONE = "simple/v1/objects/external-path-groups/{}"
    GET_EXTERNAL_PARITY_GROUPS_ONE = "simple/v1/objects/external-parity-groups/{}"
    GET_EXTERNAL_VOLUMES = "simple/v1/objects/external-volumes{}"
    POST_EXTERNAL_VOLUMES = "simple/v1/objects/external-volumes"
    POST_SESSIONS = "simple/v1/objects/sessions"
    DELETE_SESSIONS = "simple/v1/objects/sessions/{}"
    GET_COMMAND_STATUS = "simple/v1/objects/command-status/{}"
    DELETE_COMMAND_STATUS = "simple/v1/objects/command-status/{}"
    GET_HOST_ISCSI_PATHS = "v1/views/host-iscsi-paths?{}"
    GET_STORAGE_SYSTEMS = "v1/objects/storages"
    GET_STORAGE_SYSTEM = "v1/objects/storages/{}"
    GET_STORAGE_CAPACITY = "v1/objects/total-capacities/instance"
    GET_LICENSES = "v1/objects/licenses"
    GET_TOTAL_EFFICENCY = "v1/objects/storages/{}/total-efficiencies/instance"
    GET_JOURNAL_POOLS = "v1/objects/journals"
    GET_QUORUM_DISKS = "v1/objects/quorum-disks"
    GET_SYSLOG_SERVERS = "v1/objects/auditlog-syslog-servers/instance"
    UAIG_GET_ALL_SHADOW_IMAGE_PAIR = "v3/storage/devices/{deviceId}/shadowimages"
    UAIG_GET_SHADOW_IMAGE_PAIR_BY_ID = (
        "v2/storage/devices/{deviceId}/shadowimage/{pairId}"
    )
    # UAIG_CREATE_SHADOW_IMAGE_PAIR = 'v2/storage/devices/{deviceId}/shadowimage'
    UAIG_CREATE_SHADOW_IMAGE_PAIR = "v3/storage/devices/{deviceId}/shadowimage"
    UAIG_GET_SHADOW_IMAGE_PAIR_BY_PVOL = (
        "v2/storage/devices/{deviceId}/shadowimages/?primaryLunId={pvol}"
    )
    UAIG_SPLIT_SHADOW_IMAGE_PAIR = (
        "v2/storage/devices/{deviceId}/shadowimage/{pairId}/split"
    )
    UAIG_RESYNC_SHADOW_IMAGE_PAIR = (
        "v2/storage/devices/{deviceId}/shadowimage/{pairId}/resync"
    )
    UAIG_RESTORE_SHADOW_IMAGE_PAIR = (
        "v2/storage/devices/{deviceId}/shadowimage/{pairId}/restore"
    )
    # UAIG_DELETE_SHADOW_IMAGE_PAIR = 'v2/storage/devices/{deviceId}/shadowimage/{pairId}'
    UAIG_DELETE_SHADOW_IMAGE_PAIR = (
        "v3/storage/devices/{deviceId}/shadowimage/{pairId}?isDelete=true"
    )
    UAIG_GET_RESOURCE_MAPPING_INFO = (
        "v3/storage/{deviceId}/resource/{pairId}?type={type}"
    )
    DIRECT_GET_ALL_SHADOW_IMAGE_PAIR = "v1/objects/local-replications"
    DIRECT_GET_SHADOW_IMAGE_PAIR_BY_ID = "v1/objects/local-clone-copypairs/{pairId}"
    DIRECT_CREATE_SHADOW_IMAGE_PAIR = "v1/objects/local-clone-copypairs"
    DIRECT_SPLIT_SHADOW_IMAGE_PAIR = "v1/objects/local-clone-copypairs/{pairId}/actions/split/invoke"
    DIRECT_RESYNC_SHADOW_IMAGE_PAIR = "v1/objects/local-clone-copypairs/{pairId}/actions/resync/invoke"
    DIRECT_RESTORE_SHADOW_IMAGE_PAIR = "v1/objects/local-clone-copypairs/{pairId}/actions/restore/invoke"
    DIRECT_DELETE_SHADOW_IMAGE_PAIR = "v1/objects/local-clone-copypairs/{pairId}"
    DIRECT_GET_ALL_COPY_PAIR_GROUP = "v1/objects/local-clone-copygroups"
    DIRECT_GET_SI_BY_CPG = "v1/objects/local-clone-copypairs?localCloneCopyGroupId={}"
    
    # SnapShot
    ALL_SNAPSHOTS = "v1/objects/snapshot-replications"
    SNAPSHOTS = "v1/objects/snapshots"
    PEGASUS_SNAPSHOTS = "simple/v1/objects/snapshots"
    GET_ONE_SNAPSHOTS = "v1/objects/snapshots/{}"
    GET_SNAPSHOTS_QUERY = "v1/objects/snapshots?{}"
    GET_SNAPSHOT_GROUPS = "v1/objects/snapshot-groups"
    GET_SNAPSHOTS_BY_GROUP = "v1/objects/snapshot-groups/{}"
    GET_SNAPSHOT_GROUPS_ONE = "v1/objects/snapshot-groups/{}"
    POST_SNAPSHOTS_SPLIT = "v1/objects/snapshots/{}/actions/split/invoke"
    POST_SNAPSHOTS_SVOL_ADD = "v1/objects/snapshots/{}/actions/assign-volume/invoke"
    POST_SNAPSHOTS_SVOL_REMOVE = "v1/objects/snapshots/{}/actions/unassign-volume/invoke"
    POST_SNAPSHOTS_RESYNC = "v1/objects/snapshots/{}/actions/resync/invoke"
    POST_SNAPSHOTS_RESTORE = "v1/objects/snapshots/{}/actions/restore/invoke"

    SNAPSHOTS_BY_GROUP_ID = "v1/objects/snapshot-groups/{}"
    GET_SNAPSHOTS_BY_GROUP = "v1/objects/snapshot-groups"
    SPLIT_SNAPSHOT_BY_GRP = "v1/objects/snapshot-groups/{}/actions/split/invoke"
    RESYNC_SNAPSHOT_BY_GRP = "v1/objects/snapshot-groups/{}/actions/resync/invoke"
    RESTORE_SNAPSHOT_BY_GRP = "v1/objects/snapshot-groups/{}/actions/restore/invoke"
    # Pool
    GET_POOLS = "v1/objects/pools"
    GET_POOL = "v1/objects/pools/{}"


    # Parity group
    GET_PARITY_GROUPS = "v1/objects/parity-groups"
    GET_PARITY_GROUP = "v1/objects/parity-groups/{}"
    GET_EXTERNAL_PARITY_GROUPS = "v1/objects/external-parity-groups"
    GET_EXTERNAL_PARITY_GROUP = "v1/objects/external-parity-groups/{}"

    # Tag device resources
    UAIG_ADD_STORAGE_RESOURCE = "v3/storage/{}/resource"


class Http(object):
    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    DELETE = "DELETE"
    BASE_URL = "/ConfigurationManager/"
    CONTENT_TYPE = "Content-Type"
    APPLICATION_JSON = "application/json"
    RESPONSE_JOB_STATUS = "Response-Job-Status"
    COMPLETED = "Completed"
    HEADERS_JSON = {CONTENT_TYPE: APPLICATION_JSON, RESPONSE_JOB_STATUS: COMPLETED}
    HTTP = "http://"
    HTTPS = "https://"
    DEFAULT_PORT = 22015
    DEFAULT_SSL_PORT = 22016
    OPEN_URL_TIMEOUT = 300
    USER_AGENT = "automation-module"


class ModuleArgs(object):
    NULL = "None"
    SERVER = "management_address"
    SERVER_PORT = "management_port"
    USER = "user"
    PASSWORD = "password"
    CHECK_MODE = "check_mode"
    STORAGE_DEVICE_ID = "storage_device_id"
    POOL_ID = "pool_id"
    BLOCK_CAPACITY = "block_capacity"
    CAPACITY_MB = "capacity_mb"
    PORT_ID = "port_id"
    HOST_GROUP_NAME = "host_group_name"
    ISCSI_NAME = "iscsi_name"
    NICK_NAME = "nick_name"
    HOST_GROUP_NUMBER = "host_group_number"
    LDEV_ID = "ldev_id"
    DATA_REDUCTION_MODE = "data_reduction_mode"
    COPY_GROUP_NAME = "copy_group_name"
    PVOL_LDEV_ID = "pvol_ldev_id"
    SVOL_LDEV_ID = "svol_ldev_id"
    COPY_PACE = "copy_pace"
    CONSISTENCY_GROUP_ID = "consistency_group_id"
    SNAPSHOT_GROUP_NAME = "snapshot_group_name"
    SNAPSHOT_POOL_ID = "snapshot_pool_id"
    COPY_SPEED = "copy_speed"
    IS_CONSISTENCY_GROUP = "is_consistency_group"
    COPY_PAIR_NAME = "copy_pair_name"
    MU_NUMBER = "mu_number"
    GENERATIONS = "generations"
    EXTERNAL_PORT_ID = "external_port_id"
    EXTERNAL_LUN = "external_lun"
    EXTERNAL_PARITYGROUP_ID = "external_paritygroup_id"
    EXTERNAL_IP = "external_IP"
    EXTERNAL_PORT_NUMBER = "external_port_number"
    EXTERNAL_ISCSI_TARGET = "external_iscsi_target"
    EXTERNAL_PATHGROUP_ID = "external_pathgroup_id"
    ADVISOR_PORT = "advisor_port"
    CHAP_USER_NAME = "chap_user_name"
    WAY_OF_CHAP_USER = "way_of_chap_user"
    CHAP_PASSWORD = "chap_password"
    HOST_MODE = "host_mode"
    SHREDDING_PATTERN = "shredding_pattern"
    DELETE_LDEV = "delete_ldev"


class State(object):
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"

    @staticmethod
    def is_failed(status):
        return status in [State.FAILED, State.CANCELED]

    @staticmethod
    def is_finished(status):
        return status in [State.COMPLETED, State.FAILED, State.CANCELED]


class AutomationConstants(object):
    PORT_NUMBER_MIN = 0
    PORT_NUMBER_MAX = 49151
    NAME_PARAMS_MIN = 1
    NAME_PARAMS_MAX = 256
    MIN_SIZE_ZERO_ALLOWED = 0
    MIN_SIZE_ALLOWED = 1
    MAX_SIZE_ALLOWED = 999999999999
    MAX_TIME_ALLOWED = 999
    MIN_TIME_ALLOWED = 1
    POOL_ID_MIN = 0
    POOL_ID_MAX = 256
    LDEV_ID_MIN = 0
    LDEV_ID_MAX = 65535
    LDEV_MAX_NUMBER = 16384
    LDEV_MAX_MU_NUMBER = 1023
    ISCSI_NAME_LEN_MIN = 1
    ISCSI_NAME_LEN_MAX = 32
    IQN_LEN_MIN = 5
    IQN_LEN_MAX = 223
    CHAP_USER_NAME_LEN_MIN = 1
    CHAP_USER_NAME_LEN_MAX = 223
    CHAP_SECRET_LEN_MIN = 12
    CHAP_SECRET_LEN_MAX = 32
    HG_NAME_LEN_MIN = 1
    HG_NAME_LEN_MAX = 64
    CONSISTENCY_GROUP_ID_MIN = 0
    CONSISTENCY_GROUP_ID_MAX = 255
    POOL_SIZE_MIN = 16777216


class LogMessages(object):
    ENTER_METHOD = "Enter method: {}"
    LEAVE_METHOD = "Leave method: {}"
    API_REQUEST_START = "API Request: {} {}"
    API_RESPONSE = "API Response: {}"


class Log(object):
    SYSLOG_IDENTIFIER = "SYSLOG_IDENTIFIER"
    PRIORITY = "PRIORITY"
    # There is no applicable level in Python for following priorities
    # 0(Emergency), 1(Alert), 5(Notice)
    ARGS = {
        logging.DEBUG: {PRIORITY: 7},
        logging.INFO: {PRIORITY: 6},
        logging.WARNING: {PRIORITY: 4},
        logging.ERROR: {PRIORITY: 3},
        logging.CRITICAL: {PRIORITY: 2},
    }


class VolumePayloadConst:
    PARAMS = "parameters"
    POOL_ID = "poolId"
    BYTE_CAPACITY = "byteFormatCapacity"
    LDEV = "ldevId"
    ADR_SETTING = "dataReductionMode"
    PARITY_GROUP = "parityGroupId"
    PARALLEL_EXECUTION = "isParallelExecutionEnabled"
    LABEL = "label"
    ADDITIONAL_BLOCK_CAPACITY = "additionalBlockCapacity"
    IS_DATA_REDUCTION_SHARED_VOLUME_ENABLED = "isDataReductionSharedVolumeEnabled"
    IS_DATA_REDUCTION_SHARE_ENABLED = "isDataReductionShareEnabled"
    FORCE_FORMAT = "isDataReductionForceFormat"
    OPERATION_TYPE = "operationType"
    ENHANCED_EXPANSION = "enhancedExpansion"


    # URL PARAMS
    HEAD_LDEV_ID = "?headLdevId={}"
    COUNT = "&count={}"
    LDEV_OPTION = "&ldevOption={}"

    # volume emulation type
    NOT_DEFINED = "NOT DEFINED"
    
    IS_DATA_REDUCTION_SHARE_ENABLED="isDataReductionShareEnabled"
    IS_DATA_REDUCTION_DELETE_FORCE_EXECUTE = "isDataReductionDeleteForceExecute"


    DISABLED = "disabled"
    BLOCK = "BLK"

    # Volume operation type
    FMT= "FMT"
    QFMT = "QFMT"


class VSPSnapShotReq:
    snapshotGroupName = "snapshotGroupName"
    snapshotPoolId = "snapshotPoolId"
    pvolLdevId = "pvolLdevId"
    svolLdevId = "svolLdevId"
    isConsistencyGroup = "isConsistencyGroup"
    autoSplit = "autoSplit"
    isDataReductionForceCopy = "isDataReductionForceCopy"
    canCascade = "canCascade"
    parameters = "parameters"

class PairStatus:
    PSUS = "PSUS"
    SMPP = "SMPP"
    COPY = "COPY"
    PAIR = "PAIR"
    PFUL = "PFUL"
    PSUE = "PSUE"
    PFUS = "PFUS"
    RCPY =  "RCPY"
    PSUP = "PSUP"
    CPYP = "CPYP"
    OTHER = "OTHER"

class VSPPortSetting:
    LUN_SECURITY_SETTING = "lunSecuritySetting"
    PORT_MODE = "portMode"


class DefaultValues:
    DEFAULT_HG_NAME = "ansible_host_group"



ARRAY_FAMILY_LOOKUP = {
    "AMS": "ARRAY_FAMILY_DF",
    "HUS": "ARRAY_FAMILY_DF",
    "VSP": "ARRAY_FAMILY_R700",
    "HUS-VM": "ARRAY_FAMILY_HM700",
    "VSP G1000": "ARRAY_FAMILY_R800",
    "VSP G1500/F1500": "ARRAY_FAMILY_R800",
    "VSP G200": "ARRAY_FAMILY_HM800",
    "VSP G 400": "ARRAY_FAMILY_HM800",
    "VSP F 400": "ARRAY_FAMILY_HM800",
    "VSP N 400": "ARRAY_FAMILY_HM800",
    "VSP G 600": "ARRAY_FAMILY_HM800",
    "VSP F 600": "ARRAY_FAMILY_HM800",
    "VSP N 600": "ARRAY_FAMILY_HM800",
    "VSP G 800": "ARRAY_FAMILY_HM800",
    "VSP F 800": "ARRAY_FAMILY_HM800",
    "VSP N 800": "ARRAY_FAMILY_HM800",
    "VSP G130": "ARRAY_FAMILY_HM800",
    "VSP G150": "ARRAY_FAMILY_HM800",
    "VSP G/F350": "ARRAY_FAMILY_HM800",
    "VSP G/F370": "ARRAY_FAMILY_HM800",
    "VSP G/F700": "ARRAY_FAMILY_HM800",
    "VSP G/F900": "ARRAY_FAMILY_HM800",
    "VSP 5000": "ARRAY_FAMILY_R900",
    "VSP 5000H": "ARRAY_FAMILY_R900",
    "VSP 5500": "ARRAY_FAMILY_R900",
    "VSP 5500H": "ARRAY_FAMILY_R900",
    "VSP 5200": "ARRAY_FAMILY_R900",
    "VSP 5200H": "ARRAY_FAMILY_R900",
    "VSP 5600": "ARRAY_FAMILY_R900",
    "VSP 5600H": "ARRAY_FAMILY_R900",
    "VSP E590": "ARRAY_FAMILY_HM900",
    "VSP E790": "ARRAY_FAMILY_HM900",
    "VSP E990": "ARRAY_FAMILY_HM900",
    "VSP E1090": "ARRAY_FAMILY_HM900",
    "VSP E1090H": "ARRAY_FAMILY_HM900",
    "VSP One B23": "ARRAY_FAMILY_HM2000",
    "VSP One B24": "ARRAY_FAMILY_HM2000",
    "VSP One B26": "ARRAY_FAMILY_HM2000",
    "VSP One B28": "ARRAY_FAMILY_HM2000",
}


class UnSubscribeResourceTypes:
    HOST_GROUP = "HostGroup"
    VOLUME = "volume"
    PORT = "port"
    ISCSI_TARGET = "IscsiTarget"
    STORAGE_POOL = "StoragePool"
    CHAP_USER = "chapuser"
    SHADOW_IMAGE = "shadowimage"