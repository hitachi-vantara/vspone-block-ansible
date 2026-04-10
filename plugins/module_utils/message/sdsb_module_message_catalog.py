from enum import Enum


class SdsbMessageCatalog(Enum):

    # General messages
    MODULE_INIT_ERROR = "An error occurred during initialization: {}."

    # Message for hv_sds_block_compute_port module
    COMPUTE_PORT_OPERATION_SUCCESS = (
        "Successfully completed the compute port operation."
    )
    COMPUTE_PORT_PROTOCOL_CHANGED = "You must also carry out operations, including restarting the storage cluster, to apply the protocol setting change."

    # Message for hv_sds_block_remote_iscsi_port module
    REMOTE_ISCSI_PORT_REMOVE_SUCCESS = "Successfully removed the remote iSCSI port."
    REMOTE_ISCSI_PORT_REMOVE_FAILURE = "Failed to remove the remote iSCSI port."

    # Message for hv_sds_block_snmp_settings module
    SNMP_SETTINGS_UPDATE_SUCCESS = "Successfully updated the SNMP settings."

    # Message for hv_sds_block_spare_node module
    SPARE_NODE_UPDATE_SUCCESS = "Successfully updated spare node settings."

    # Message for hv_sds_block_storage_controller module
    STORAGE_CONTROLLER_UPDATE_SUCCESS = (
        "Successfully updated the settings for the storage controller."
    )

    # Message for hv_sds_block_storage_pool module
    STORAGE_POOL_MODIFICATION_SUCCESS = (
        "Successfully modified the storage pool settings."
    )
    STORAGE_POOL_EXPANSION_MESSAGE = (
        "The storage system will generate additional jobs for capacity and metadata allocation. "
        "Please wait for these tasks to finish and then verify the storage pool capacity."
    )
